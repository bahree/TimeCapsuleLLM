"""
Multi-GPU training script for London Historical LLM
Optimized for 2+ NVIDIA GPUs using PyTorch DDP
"""

import os
import time
import math
import pickle
from contextlib import nullcontext
import torch
import numpy as np
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed import init_process_group, destroy_process_group

# Import our model
from london_1800_1850_v0.model import GPTConfig, GPT

# -----------------------------------------------------------------------------
# Multi-GPU Configuration for London Historical LLM
# -----------------------------------------------------------------------------
out_dir = 'out_london_historical'
eval_interval = 200  # More frequent evaluation for multi-GPU
log_interval = 10
eval_iters = 50
eval_only = False
always_save_checkpoint = True
init_from = 'scratch'

# Data - optimized for multi-GPU
dataset = 'london_data'
gradient_accumulation_steps = 2  # Reduced since we have more GPUs
batch_size = 12  # Increased batch size per GPU
block_size = 256

# Model architecture - can be larger with 2 GPUs
n_layer = 12  # Increased from 8
n_head = 12   # Increased from 8
n_embd = 768  # Increased from 512
dropout = 0.1
bias = False

# Training - optimized for multi-GPU
learning_rate = 3e-4
max_iters = 20000  # More iterations since training is faster
weight_decay = 1e-1
beta1 = 0.9
beta2 = 0.95
grad_clip = 1.0

# Learning rate schedule
decay_lr = True
warmup_iters = 1000  # Increased warmup
lr_decay_iters = 20000
min_lr = 3e-5

# Multi-GPU settings
backend = 'nccl'  # Best for NVIDIA GPUs
device = 'cuda'
dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16'
compile = True

# Wandb logging - configurable via environment variable
wandb_log = os.environ.get('WANDB_LOG', 'false').lower() == 'true'
wandb_project = 'london-historical-llm-multi-gpu'
wandb_run_name = f'london-llm-2gpu-{int(time.time())}'

# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------

def get_batch(split):
    """Get a batch of data for training/validation"""
    data_dir = os.path.join('data', dataset)
    
    if split == 'train':
        data_file = os.path.join(data_dir, 'train.bin')
    else:
        data_file = os.path.join(data_dir, 'val.bin')
    
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")
    
    # Load data
    data = np.memmap(data_file, dtype=np.uint16, mode='r')
    
    # Sample random sequences
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([torch.from_numpy((data[i:i+block_size]).astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy((data[i+1:i+1+block_size]).astype(np.int64)) for i in ix])
    
    # Move to GPU with pin_memory for better performance
    x, y = x.pin_memory().to(device, non_blocking=True), y.pin_memory().to(device, non_blocking=True)
    
    return x, y

# -----------------------------------------------------------------------------
# Multi-GPU setup
# -----------------------------------------------------------------------------

# DDP setup
ddp = int(os.environ.get('RANK', -1)) != -1
if ddp:
    init_process_group(backend=backend)
    ddp_rank = int(os.environ['RANK'])
    ddp_local_rank = int(os.environ['LOCAL_RANK'])
    ddp_world_size = int(os.environ['WORLD_SIZE'])
    device = f'cuda:{ddp_local_rank}'
    torch.cuda.set_device(device)
    master_process = ddp_rank == 0
    seed_offset = ddp_rank
    # Scale down gradient accumulation for multi-GPU
    assert gradient_accumulation_steps % ddp_world_size == 0
    gradient_accumulation_steps //= ddp_world_size
else:
    # Single GPU fallback
    master_process = True
    seed_offset = 0
    ddp_world_size = 1

tokens_per_iter = gradient_accumulation_steps * ddp_world_size * batch_size * block_size
print(f"tokens per iteration will be: {tokens_per_iter:,}")
print(f"Using {ddp_world_size} GPU(s)")

if master_process:
    os.makedirs(out_dir, exist_ok=True)

torch.manual_seed(1337 + seed_offset)
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
device_type = 'cuda'
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

# -----------------------------------------------------------------------------
# Model initialization
# -----------------------------------------------------------------------------

# Get vocab size from metadata
meta_path = os.path.join('data', dataset, 'meta.pkl')
meta_vocab_size = None
if os.path.exists(meta_path):
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
    meta_vocab_size = meta['vocab_size']
    print(f"found vocab_size = {meta_vocab_size} (inside {meta_path})")

# Model init
model_args = dict(n_layer=n_layer, n_head=n_head, n_embd=n_embd, block_size=block_size,
                  bias=bias, vocab_size=None, dropout=dropout)

if init_from == 'scratch':
    print("Initializing a new model from scratch")
    if meta_vocab_size is None:
        print("defaulting to vocab_size of 50304")
    model_args['vocab_size'] = meta_vocab_size if meta_vocab_size is not None else 50304
    gptconf = GPTConfig(**model_args)
    model = GPT(gptconf)
else:
    raise ValueError(f"init_from = {init_from} not supported yet")

model.to(device)

# Initialize optimizer
scaler = torch.cuda.amp.GradScaler(enabled=(dtype == 'float16'))
optimizer = model.configure_optimizers(weight_decay, learning_rate, (beta1, beta2), device_type)

# Compile model
if compile:
    print("compiling the model... (takes a ~minute)")
    unoptimized_model = model
    model = torch.compile(model)

# DDP wrapper
if ddp:
    model = DDP(model, device_ids=[ddp_local_rank])

# -----------------------------------------------------------------------------
# Training loop
# -----------------------------------------------------------------------------

@torch.no_grad()
def estimate_loss():
    """Estimate loss on train/val sets"""
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            with ctx:
                logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out

def get_lr(it):
    """Learning rate schedule"""
    if it < warmup_iters:
        return learning_rate * (it + 1) / (warmup_iters + 1)
    if it > lr_decay_iters:
        return min_lr
    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    assert 0 <= decay_ratio <= 1
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (learning_rate - min_lr)

# Wandb logging - optional with user choice
if wandb_log and master_process:
    try:
        import wandb
        print("🔍 W&B logging enabled. You'll need a W&B account.")
        print("   If you don't have one, you can:")
        print("   1. Create a free account at https://wandb.ai")
        print("   2. Or disable W&B by setting WANDB_LOG=false")
        print("   3. Or press Ctrl+C to cancel and restart without W&B")
        print("")
        
        # Give user a chance to cancel
        import time
        print("Starting W&B initialization in 5 seconds... (Press Ctrl+C to cancel)")
        time.sleep(5)
        
        wandb.init(project=wandb_project, name=wandb_run_name, config={
            'n_layer': n_layer,
            'n_head': n_head,
            'n_embd': n_embd,
            'block_size': block_size,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
            'max_iters': max_iters,
            'dropout': dropout,
            'vocab_size': meta_vocab_size,
            'ddp_world_size': ddp_world_size,
        })
        print("✅ W&B logging initialized successfully!")
    except ImportError:
        print("❌ W&B not installed. Install with: pip install wandb")
        print("   Or disable W&B by setting WANDB_LOG=false")
        wandb_log = False
    except Exception as e:
        print(f"❌ W&B initialization failed: {e}")
        print("   Disabling W&B logging...")
        wandb_log = False
else:
    print("📊 W&B logging disabled - using console logging only")

# Training loop
X, Y = get_batch('train')
t0 = time.time()
local_iter_num = 0
raw_model = model.module if ddp else model
running_mfu = -1.0

iter_num = 0
best_val_loss = 1e9

print(f"Starting training on {ddp_world_size} GPU(s)...")
print(f"Model parameters: {raw_model.get_num_params():,}")

while True:
    # Learning rate schedule
    lr = get_lr(iter_num) if decay_lr else learning_rate
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

    # Evaluation and checkpointing
    if iter_num % eval_interval == 0 and master_process:
        losses = estimate_loss()
        print(f"step {iter_num}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")
        
        if wandb_log:
            try:
                wandb.log({
                    "iter": iter_num,
                    "train/loss": losses['train'],
                    "val/loss": losses['val'],
                    "lr": lr,
                    "mfu": running_mfu*100,
                })
            except Exception as e:
                print(f"⚠️  W&B logging error: {e}")
                wandb_log = False
        
        if losses['val'] < best_val_loss or always_save_checkpoint:
            best_val_loss = losses['val']
            if iter_num > 0:
                checkpoint = {
                    'model': raw_model.state_dict(),
                    'optimizer': optimizer.state_dict(),
                    'model_args': model_args,
                    'iter_num': iter_num,
                    'best_val_loss': best_val_loss,
                    'config': {
                        'n_layer': n_layer,
                        'n_head': n_head,
                        'n_embd': n_embd,
                        'block_size': block_size,
                        'batch_size': batch_size,
                        'learning_rate': learning_rate,
                        'max_iters': max_iters,
                        'dropout': dropout,
                        'vocab_size': meta_vocab_size,
                        'ddp_world_size': ddp_world_size,
                    }
                }
                print(f"saving checkpoint to {out_dir}")
                torch.save(checkpoint, os.path.join(out_dir, 'ckpt.pt'))
    
    if iter_num == 0 and eval_only:
        break

    # Training step
    for micro_step in range(gradient_accumulation_steps):
        if ddp:
            model.require_backward_grad_sync = (micro_step == gradient_accumulation_steps - 1)
        
        with ctx:
            logits, loss = model(X, Y)
            loss = loss / gradient_accumulation_steps
        
        X, Y = get_batch('train')
        scaler.scale(loss).backward()
    
    # Gradient clipping
    if grad_clip != 0.0:
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
    
    scaler.step(optimizer)
    scaler.update()
    optimizer.zero_grad(set_to_none=True)

    # Timing and logging
    t1 = time.time()
    dt = t1 - t0
    t0 = t1
    if iter_num % log_interval == 0 and master_process:
        lossf = loss.item() * gradient_accumulation_steps
        if local_iter_num >= 5:
            mfu = raw_model.estimate_mfu(batch_size * gradient_accumulation_steps, dt)
            running_mfu = mfu if running_mfu == -1.0 else 0.9*running_mfu + 0.1*mfu
        print(f"iter {iter_num}: loss {lossf:.4f}, time {dt*1000:.2f}ms, mfu {running_mfu*100:.2f}%")
    
    iter_num += 1
    local_iter_num += 1

    # Termination
    if iter_num > max_iters:
        break

if ddp:
    destroy_process_group()

print("Training completed!")
