#!/bin/bash

echo "🚀 Launching London Historical LLM Training on 2 GPUs"
echo "=================================================="

# Check if GPUs are available
echo "🔍 Checking GPU availability..."
nvidia-smi

echo ""
echo "🏃 Starting training with 2 GPUs..."
echo "   This will use Distributed Data Parallel (DDP)"
echo "   Monitor with: watch -n 1 nvidia-smi"
echo ""

# Launch training with 2 GPUs
torchrun --nproc_per_node=2 train_london_llm_multi_gpu.py

echo ""
echo "✅ Training completed!"
