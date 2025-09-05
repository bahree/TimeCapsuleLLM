#!/bin/bash

echo "🏛️  London Historical LLM - Training Launcher"
echo "=============================================="

# Check if GPUs are available
echo "🔍 Checking GPU availability..."
nvidia-smi

echo ""
echo "📊 Choose your logging preference:"
echo ""
echo "1. Console logging only (no W&B account needed)"
echo "2. W&B logging (requires free account at https://wandb.ai)"
echo "3. Exit"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "📊 Using console logging only..."
        export WANDB_LOG=false
        ;;
    2)
        echo "🔍 W&B logging enabled..."
        echo "   You'll need to create a free account at https://wandb.ai"
        echo "   The script will wait 5 seconds for you to cancel if needed"
        export WANDB_LOG=true
        ;;
    3)
        echo "👋 Exiting..."
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Using console logging only..."
        export WANDB_LOG=false
        ;;
esac

echo ""
echo "🚀 Starting training with 2 GPUs..."
echo "   W&B Logging: $WANDB_LOG"
echo "   Monitor with: watch -n 1 nvidia-smi"
echo ""

# Launch training with 2 GPUs
torchrun --nproc_per_node=2 train_london_llm_multi_gpu.py

echo ""
echo "✅ Training completed!"
