#!/bin/bash

echo "🚀 Launching Enhanced London Historical LLM Training"
echo "=================================================="
echo "📊 Model: 400M parameters (20 layers, 16 heads, 1280 hidden)"
echo "📚 Data: Enhanced sources (1500-1850)"
echo "🔤 Tokenizer: Custom historical (30,000 tokens)"
echo "=================================================="

# Check if enhanced data exists
if [ ! -f "data/london_enhanced/train.bin" ]; then
    echo "❌ Enhanced dataset not found!"
    echo "   Please run: python data_preparation_fixed.py"
    exit 1
fi

# Check if custom tokenizer exists
if [ ! -f "tokenizer_historical/tokenizer.json" ]; then
    echo "❌ Custom tokenizer not found!"
    echo "   Please run: python train_custom_tokenizer.py"
    exit 1
fi

# Check GPU availability
echo "🔍 Checking GPU availability..."
nvidia-smi

# Check W&B logging preference
echo ""
echo "📊 W&B Logging Options:"
echo "   • WANDB_LOG=true  - Enable W&B logging (requires account)"
echo "   • WANDB_LOG=false - Disable W&B logging (default)"
echo "   • No setting      - Disable W&B logging"

if [ -z "$WANDB_LOG" ]; then
    echo "📊 W&B logging disabled (console logging only)"
else
    echo "📊 W&B logging: $WANDB_LOG"
fi

echo ""
echo "🏃 Starting enhanced training..."
echo "   This will use Distributed Data Parallel (DDP)"
echo "   Monitor with: watch -n 1 nvidia-smi"

# Create output directory
mkdir -p out_london_historical_enhanced

# Launch training
if [ "$WANDB_LOG" = "true" ]; then
    echo "🚀 Starting with W&B logging enabled..."
    WANDB_LOG=true torchrun --nproc_per_node=2 train_london_llm_enhanced.py \
        --out_dir=out_london_historical_enhanced \
        --dataset=london_enhanced \
        --batch_size=8 \
        --block_size=1024 \
        --n_layer=20 \
        --n_head=16 \
        --n_embd=1280 \
        --dropout=0.1 \
        --learning_rate=6e-4 \
        --max_iters=50000 \
        --weight_decay=1e-1 \
        --beta1=0.9 \
        --beta2=0.95 \
        --grad_clip=1.0 \
        --lr_decay_iters=50000 \
        --min_lr=6e-5 \
        --warmup_iters=2000 \
        --compile \
        --device=cuda \
        --dtype=float16 \
        --ddp \
        --ddp_world_size=2 \
        --ddp_backend=nccl \
        --wandb_log \
        --wandb_project=london-historical-llm-enhanced \
        --wandb_run_name=enhanced-400m-$(date +%Y%m%d_%H%M%S)
else
    echo "🚀 Starting with console logging only..."
    torchrun --nproc_per_node=2 train_london_llm_enhanced.py \
        --out_dir=out_london_historical_enhanced \
        --dataset=london_enhanced \
        --batch_size=8 \
        --block_size=1024 \
        --n_layer=20 \
        --n_head=16 \
        --n_embd=1280 \
        --dropout=0.1 \
        --learning_rate=6e-4 \
        --max_iters=50000 \
        --weight_decay=1e-1 \
        --beta1=0.9 \
        --beta2=0.95 \
        --grad_clip=1.0 \
        --lr_decay_iters=50000 \
        --min_lr=6e-5 \
        --warmup_iters=2000 \
        --compile \
        --device=cuda \
        --dtype=float16 \
        --ddp \
        --ddp_world_size=2 \
        --ddp_backend=nccl
fi

echo "🎉 Enhanced training completed!"
