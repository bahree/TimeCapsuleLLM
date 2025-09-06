#!/usr/bin/env python3
"""
Enhanced London Historical LLM Training Script
- Bigger model (400M parameters)
- Enhanced data sources (1500-1850)
- Custom historical tokenizer
"""

import os
import time
import math
import pickle
import argparse
from contextlib import nullcontext

import torch
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed import init_process_group, destroy_process_group
import torch.distributed as dist

from london_1800_1850_v0.model import GPTConfig, GPT
from london_1800_1850_v0.model import CausalSelfAttention, Block, LayerNorm

# Enhanced model configuration for 400M parameters
def get_model_config():
    """Get enhanced model configuration"""
    return {
        'n_layer': 20,           # 12 → 20 layers (increased)
        'n_head': 16,            # 12 → 16 heads (increased)
        'n_embd': 1280,          # 768 → 1280 hidden size (increased)
        'block_size': 1024,      # Keep same context length
        'bias': False,           # Keep same bias setting
        'vocab_size': 30000,     # Will be overridden from tokenizer
        'dropout': 0.1,          # Keep same dropout
    }

def get_optimizer(model, weight_decay, learning_rate, betas, device_type):
    """Get optimizer for enhanced model"""
    # Get all parameters that require gradients
    param_dict = {pn: p for pn, p in model.named_parameters()}
    param_dict = {pn: p for pn, p in param_dict.items() if p.requires_grad}
    
    # Create decay and no_decay parameter groups
    decay_params = [p for n, p in param_dict.items() if p.dim() >= 2]
    nodecay_params = [p for n, p in param_dict.items() if p.dim() < 2]
    
    optim_groups = [
        {'params': decay_params, 'weight_decay': weight_decay},
        {'params': nodecay_params, 'weight_decay': 0.0}
    ]
    
    num_decay_params = sum(p.numel() for p in decay_params)
    num_nodecay_params = sum(p.numel() for p in nodecay_params)
    print(f"num decayed parameter tensors: {len(decay_params)}, with {num_decay_params:,} parameters")
    print(f"num non-decayed parameter tensors: {len(nodecay_params)}, with {num_nodecay_params:,} parameters")
    
    # Create AdamW optimizer
    optimizer = torch.optim.AdamW(optim_groups, lr=learning_rate, betas=betas, fused=(device_type == 'cuda'))
    return optimizer

def get_batch(split, train_data, val_data, device, block_size, batch_size):
    """Get batch of data"""
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([torch.from_numpy((data[i:i+block_size]).astype(np.int64)) for i in ix])
    y = torch.stack([torch.from_numpy((data[i+1:i+1+block_size]).astype(np.int64)) for i in ix])
    if device == 'cuda':
        x, y = x.pin_memory().to(device, non_blocking=True), y.pin_memory().to(device, non_blocking=True)
    else:
        x, y = x.to(device), y.to(device)
    return x, y

@torch.no_grad()
def estimate_loss(model, train_data, val_data, eval_iters, device, block_size, batch_size):
    """Estimate loss on train and val sets"""
    out = {}
    model.eval()
    for split in ['train', 'val']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split, train_data, val_data, device, block_size, batch_size)
            with torch.cuda.amp.autocast(enabled=(device == 'cuda')):
                logits, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out

def load_tokenizer():
    """Load the custom historical tokenizer"""
    try:
        from tokenizers import Tokenizer
        tokenizer_path = "tokenizer_historical/tokenizer.json"
        if os.path.exists(tokenizer_path):
            tokenizer = Tokenizer.from_file(tokenizer_path)
            vocab_size = tokenizer.get_vocab_size()
            print(f"✅ Loaded custom tokenizer with {vocab_size:,} tokens")
            return tokenizer, vocab_size
        else:
            print("❌ Custom tokenizer not found, using fallback")
            return None, 30000  # Fallback
    except Exception as e:
        print(f"❌ Error loading tokenizer: {e}")
        return None, 30000

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Enhanced London Historical LLM Training')
    parser.add_argument('--out_dir', type=str, default='out_london_historical_enhanced', help='output directory')
    parser.add_argument('--eval_interval', type=int, default=200, help='eval interval')
    parser.add_argument('--log_interval', type=int, default=10, help='log interval')
    parser.add_argument('--eval_iters', type=int, default=200, help='eval iters')
    parser.add_argument('--always_save_checkpoint', action='store_true', help='always save checkpoint')
    parser.add_argument('--init_from', type=str, default='scratch', help='init from scratch or resume')
    parser.add_argument('--wandb_log', action='store_true', help='log to wandb')
    parser.add_argument('--wandb_project', type=str, default='london-historical-llm-enhanced', help='wandb project')
    parser.add_argument('--wandb_run_name', type=str, default='enhanced-400m', help='wandb run name')
    parser.add_argument('--dataset', type=str, default='london_enhanced', help='dataset name')
    parser.add_argument('--gradient_accumulation_steps', type=int, default=1, help='gradient accumulation steps')
    parser.add_argument('--batch_size', type=int, default=12, help='batch size')
    parser.add_argument('--block_size', type=int, default=1024, help='block size')
    parser.add_argument('--n_layer', type=int, default=20, help='number of layers')
    parser.add_argument('--n_head', type=int, default=16, help='number of heads')
    parser.add_argument('--n_embd', type=int, default=1280, help='embedding dimension')
    parser.add_argument('--dropout', type=float, default=0.1, help='dropout')
    parser.add_argument('--bias', action='store_true', help='use bias')
    parser.add_argument('--learning_rate', type=float, default=6e-4, help='learning rate')
    parser.add_argument('--max_iters', type=int, default=50000, help='max iterations')
    parser.add_argument('--weight_decay', type=float, default=1e-1, help='weight decay')
    parser.add_argument('--beta1', type=float, default=0.9, help='beta1')
    parser.add_argument('--beta2', type=float, default=0.95, help='beta2')
    parser.add_argument('--grad_clip', type=float, default=1.0, help='gradient clipping')
    parser.add_argument('--lr_decay_iters', type=int, default=50000, help='lr decay iters')
    parser.add_argument('--min_lr', type=float, default=6e-5, help='min learning rate')
    parser.add_argument('--warmup_iters', type=int, default=2000, help='warmup iters')
    parser.add_argument('--compile', action='store_true', help='compile model')
    parser.add_argument('--device', type=str, default='cuda', help='device')
    parser.add_argument('--dtype', type=str, default='float16', help='dtype')
    parser.add_argument('--ddp', action='store_true', help='use ddp')
    parser.add_argument('--ddp_world_size', type=int, default=1, help='ddp world size')
    parser.add_argument('--ddp_rank', type=int, default=0, help='ddp rank')
    parser.add_argument('--ddp_local_rank', type=int, default=0, help='ddp local rank')
    parser.add_argument('--ddp_backend', type=str, default='nccl', help='ddp backend')
    parser.add_argument('--ddp_init_method', type=str, default='env://', help='ddp init method')
    args = parser.parse_args()

    # Initialize DDP if needed
    ddp = int(os.environ.get('RANK', -1)) != -1
    if ddp:
        init_process_group(backend=args.ddp_backend)
        ddp_rank = int(os.environ['RANK'])
        ddp_local_rank = int(os.environ['LOCAL_RANK'])
        ddp_world_size = int(os.environ['WORLD_SIZE'])
        device = f'cuda:{ddp_local_rank}'
        torch.cuda.set_device(device)
        master_process = ddp_rank == 0
        seed_offset = ddp_rank
        assert ddp_world_size == args.ddp_world_size
    else:
        master_process = True
        seed_offset = 0
        ddp_rank = 0
        ddp_local_rank = 0
        ddp_world_size = 1
        device = args.device

    # Set random seed
    torch.manual_seed(1337 + seed_offset)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

    # Load tokenizer
    tokenizer, vocab_size = load_tokenizer()
    args.vocab_size = vocab_size

    # Load data
    data_dir = os.path.join('data', args.dataset)
    train_data = np.memmap(os.path.join(data_dir, 'train.bin'), dtype=np.uint16, mode='r')
    val_data = np.memmap(os.path.join(data_dir, 'val.bin'), dtype=np.uint16, mode='r')

    # Get model config
    config = get_model_config()
    config.update(vars(args))
    config['vocab_size'] = vocab_size

    # Create model
    model = GPT(GPTConfig(**config))
    model.to(device)

    # Initialize optimizer
    optimizer = get_optimizer(model, args.weight_decay, args.learning_rate, (args.beta1, args.beta2), device)

    # Compile model
    if args.compile:
        print("compiling the model... (takes a ~minute)")
        model = torch.compile(model)

    # Initialize DDP
    if ddp:
        model = DDP(model, device_ids=[ddp_local_rank])

    # Load checkpoint if resuming
    iter_num = 0
    best_val_loss = 1e9
    if args.init_from == 'resume':
        ckpt_path = os.path.join(args.out_dir, 'ckpt.pt')
        if os.path.exists(ckpt_path):
            checkpoint = torch.load(ckpt_path, map_location=device)
            model.load_state_dict(checkpoint['model'])
            optimizer.load_state_dict(checkpoint['optimizer'])
            iter_num = checkpoint['iter_num']
            best_val_loss = checkpoint['best_val_loss']
            print(f"Resumed from iteration {iter_num}")

    # Initialize wandb
    wandb_log = args.wandb_log and master_process
    if wandb_log:
        try:
            import wandb
            wandb.init(project=args.wandb_project, name=args.wandb_run_name, config=config)
        except Exception as e:
            print(f"Failed to initialize wandb: {e}")
            wandb_log = False

    # Training loop
    model.train()
    raw_model = model.module if ddp else model
    scaler = torch.cuda.amp.GradScaler(enabled=(args.dtype == 'float16'))

    print(f"Starting training on {ddp_world_size} GPU(s)...")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Calculate tokens per iteration
    tokens_per_iter = args.gradient_accumulation_steps * ddp_world_size * args.batch_size * args.block_size
    print(f"tokens per iteration will be: {tokens_per_iter:,}")

    # Training loop
    while True:
        # Forward pass
        with torch.cuda.amp.autocast(enabled=(args.dtype == 'float16')):
            logits, loss = model(X, Y)
            loss = loss / args.gradient_accumulation_steps

        # Backward pass
        scaler.scale(loss).backward()

        # Gradient clipping
        if args.grad_clip != 0.0:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)

        # Optimizer step
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)

        # Learning rate decay
        if iter_num < args.warmup_iters:
            lr = args.learning_rate * iter_num / args.warmup_iters
        else:
            lr = args.learning_rate * (0.5 * (1.0 + math.cos(math.pi * (iter_num - args.warmup_iters) / (args.lr_decay_iters - args.warmup_iters))))
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr

        # Logging
        if iter_num % args.log_interval == 0:
            lossf = loss.item() * args.gradient_accumulation_steps
            print(f"iter {iter_num}: loss {lossf:.4f}, lr {lr:.2e}")

        # Evaluation
        if iter_num % args.eval_interval == 0:
            losses = estimate_loss(model, train_data, val_data, args.eval_iters, device, args.block_size, args.batch_size)
            print(f"step {iter_num}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")

            # Save checkpoint
            if losses['val'] < best_val_loss or args.always_save_checkpoint:
                best_val_loss = losses['val']
                if iter_num > 0:
                    checkpoint = {
                        'model': raw_model.state_dict(),
                        'optimizer': optimizer.state_dict(),
                        'model_args': config,
                        'iter_num': iter_num,
                        'best_val_loss': best_val_loss,
                        'config': config,
                    }
                    print(f"saving checkpoint to {args.out_dir}")
                    torch.save(checkpoint, os.path.join(args.out_dir, 'ckpt.pt'))

        # Check for completion
        if iter_num >= args.max_iters:
            break

        iter_num += 1

    print("Training completed!")

if __name__ == "__main__":
    import numpy as np
    main()
