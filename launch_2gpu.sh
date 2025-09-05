#!/bin/bash

echo "🚀 Launching London Historical LLM Training on 2 GPUs"
echo "=================================================="

# Check if GPUs are available
echo "🔍 Checking GPU availability..."
nvidia-smi

echo ""
echo "📊 W&B Logging Options:"
echo "   • WANDB_LOG=true  - Enable W&B logging (requires account)"
echo "   • WANDB_LOG=false - Disable W&B logging (default)"
echo "   • No setting      - Disable W&B logging"
echo ""

# Check W&B setting
if [ "$WANDB_LOG" = "true" ]; then
    echo "✅ W&B logging enabled"
else
    echo "📊 W&B logging disabled (console logging only)"
fi

echo ""
echo "🏃 Starting training with 2 GPUs..."
echo "   This will use Distributed Data Parallel (DDP)"
echo "   Monitor with: watch -n 1 nvidia-smi"
echo ""

# Launch training with 2 GPUs
torchrun --nproc_per_node=2 train_london_llm_multi_gpu.py

echo ""
echo "✅ Training completed!"
