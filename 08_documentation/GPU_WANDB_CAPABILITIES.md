# GPU and WandB Capabilities

## 🚀 **Multi-GPU and WandB Support**

The London Historical LLM system now includes comprehensive support for single GPU, multi-GPU, and WandB experiment tracking.

## 🎮 **GPU Support**

### **Automatic GPU Detection**
- **Single GPU**: Optimized for single GPU training
- **Multi-GPU**: Automatic multi-GPU setup with torchrun
- **CPU-Only**: Fallback for systems without GPUs
- **Memory Optimization**: Automatic batch size adjustment

### **GPU Configuration**
```python
# Automatic configuration based on available hardware
if gpu_count > 1:
    # Multi-GPU: 4 gradient accumulation steps, FP16
    accelerator = Accelerator(gradient_accumulation_steps=4, mixed_precision="fp16")
elif gpu_count == 1:
    # Single GPU: 2 gradient accumulation steps, FP16
    accelerator = Accelerator(gradient_accumulation_steps=2, mixed_precision="fp16")
else:
    # CPU-only: 1 gradient accumulation step, no mixed precision
    accelerator = Accelerator(gradient_accumulation_steps=1, mixed_precision="no")
```

### **Hardware Requirements**
- **Minimum**: CPU-only training (slower but functional)
- **Recommended**: Single GPU with 8GB+ VRAM
- **Optimal**: Multiple GPUs with 16GB+ VRAM each
- **Memory**: 16GB+ system RAM recommended

## 📊 **WandB Integration**

### **Automatic Setup**
- **API Key Detection**: Automatically detects WANDB_API_KEY
- **Project Configuration**: Pre-configured for "london-historical-llm"
- **Experiment Tracking**: Comprehensive metrics and logging
- **Team Collaboration**: Support for team workspaces

### **Tracked Metrics**
- **Training Loss**: Real-time training and validation loss
- **Learning Rate**: Learning rate schedule over time
- **GPU Usage**: Memory usage and utilization
- **Training Speed**: Steps per second
- **Model Configuration**: All hyperparameters
- **Hardware Info**: GPU details and system specs

### **WandB Configuration**
```python
wandb.init(
    project="london-historical-llm",
    name=f"london-llm-{timestamp}",
    config={
        "model_name": "gpt2-medium",
        "vocab_size": 50000,
        "max_length": 1024,
        "batch_size": 2,
        "learning_rate": 3e-5,
        "num_epochs": 5,
        "gpu_count": torch.cuda.device_count(),
        "mixed_precision": "fp16"
    },
    tags=["london", "historical", "llm", "gpt2", "1500-1850"]
)
```

## 🚀 **Usage Examples**

### **Single GPU Training**
```bash
# Set WandB API key
export WANDB_API_KEY=your_key_here

# Run training (automatically detects single GPU)
python 04_training/train_model.py
```

### **Multi-GPU Training**
```bash
# Set WandB API key
export WANDB_API_KEY=your_key_here

# Run multi-GPU training
python 10_scripts/launch_multi_gpu_training.py
```

### **Interactive Launcher**
```bash
# Set WandB API key
export WANDB_API_KEY=your_key_here

# Use interactive launcher
python 10_scripts/launch_london_llm.py
```

### **CPU-Only Training**
```bash
# Run without GPU (WandB still works)
CUDA_VISIBLE_DEVICES="" python 04_training/train_model.py
```

## 📈 **Performance Expectations**

### **Single GPU (RTX 4090)**
- **Training Time**: 2-3 days
- **Memory Usage**: ~12GB VRAM
- **Batch Size**: 2 per device
- **Mixed Precision**: FP16

### **Multi-GPU (2x RTX 4090)**
- **Training Time**: 1-2 days
- **Memory Usage**: ~12GB VRAM per GPU
- **Batch Size**: 1 per device (2 total)
- **Mixed Precision**: FP16

### **CPU-Only**
- **Training Time**: 1-2 weeks
- **Memory Usage**: ~16GB RAM
- **Batch Size**: 1
- **Mixed Precision**: None

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# WandB Configuration
export WANDB_API_KEY=your_key_here
export WANDB_PROJECT=london-historical-llm
export WANDB_ENTITY=your_username
export WANDB_MODE=online  # or offline

# GPU Configuration
export CUDA_VISIBLE_DEVICES=0,1,2,3  # Use specific GPUs
export CUDA_DEVICE_ORDER=PCI_BUS_ID  # Consistent GPU ordering
```

### **Training Arguments**
```bash
# Custom configuration
python 04_training/train_model.py \
    --model_name gpt2-medium \
    --batch_size 2 \
    --learning_rate 3e-5 \
    --num_epochs 5 \
    --max_length 1024
```

## 📊 **WandB Dashboard Features**

### **Real-time Monitoring**
- **Loss Curves**: Training and validation loss
- **Learning Rate**: Learning rate schedule
- **GPU Metrics**: Memory usage and utilization
- **Training Speed**: Steps per second

### **Model Information**
- **Architecture**: GPT-2 Medium (355M parameters)
- **Vocabulary**: 50,000 tokens with 100+ special tokens
- **Context Length**: 1,024 tokens
- **Training Configuration**: All hyperparameters

### **Hardware Monitoring**
- **GPU Memory**: Peak and average usage
- **GPU Utilization**: Percentage usage over time
- **System Resources**: CPU, RAM, disk usage
- **Training Efficiency**: Samples per second

## 🐛 **Troubleshooting**

### **GPU Issues**
```bash
# Check GPU availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')"

# Check GPU memory
nvidia-smi
```

### **WandB Issues**
```bash
# Check WandB installation
python -c "import wandb; print(f'WandB version: {wandb.__version__}')"

# Test WandB connection
wandb login
wandb status
```

### **Memory Issues**
```bash
# Reduce batch size for low memory
python 04_training/train_model.py --batch_size 1

# Use gradient checkpointing (already enabled)
# Use mixed precision (already enabled)
```

## 🎯 **Best Practices**

### **For Single GPU**
- Use batch size 2-4 depending on GPU memory
- Enable mixed precision (FP16)
- Use gradient accumulation for larger effective batch size
- Monitor GPU memory usage

### **For Multi-GPU**
- Use batch size 1-2 per GPU
- Enable mixed precision (FP16)
- Use torchrun for distributed training
- Monitor all GPU memory usage

### **For WandB**
- Set up API key before training
- Use descriptive run names
- Add relevant tags
- Monitor key metrics regularly

## 🎉 **Ready for Production!**

The system now supports:

- ✅ **Single GPU Training**: Optimized for single GPU setups
- ✅ **Multi-GPU Training**: Automatic multi-GPU configuration
- ✅ **CPU-Only Training**: Fallback for systems without GPUs
- ✅ **WandB Integration**: Comprehensive experiment tracking
- ✅ **Memory Optimization**: Automatic batch size adjustment
- ✅ **Mixed Precision**: FP16 support for faster training
- ✅ **Distributed Training**: Multi-GPU with torchrun
- ✅ **Real-time Monitoring**: Live training metrics

**Start training with full GPU and WandB support!** 🚀📊✨
