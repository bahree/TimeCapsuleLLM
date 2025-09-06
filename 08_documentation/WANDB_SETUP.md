# WandB Setup Guide

## 🔧 **WandB Configuration for London Historical LLM**

This guide explains how to set up Weights & Biases (WandB) for experiment tracking and monitoring during model training.

## 📋 **Prerequisites**

1. **WandB Account**: Sign up at [https://wandb.ai](https://wandb.ai)
2. **API Key**: Get your API key from [https://wandb.ai/authorize](https://wandb.ai/authorize)
3. **WandB Package**: Install with `pip install wandb`

## 🚀 **Quick Setup**

### **1. Install WandB**
```bash
pip install wandb
```

### **2. Set API Key**
```bash
# Option 1: Environment variable (recommended)
export WANDB_API_KEY=your_api_key_here

# Option 2: Login via CLI
wandb login
```

### **3. Verify Setup**
```bash
python -c "import wandb; print('WandB version:', wandb.__version__)"
```

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# Required
export WANDB_API_KEY=your_api_key_here

# Optional
export WANDB_PROJECT=london-historical-llm
export WANDB_ENTITY=your_username
export WANDB_MODE=online  # or offline
```

### **Project Settings**
- **Project Name**: `london-historical-llm`
- **Entity**: Your WandB username
- **Tags**: `london`, `historical`, `llm`, `gpt2`, `1500-1850`

## 📊 **What Gets Tracked**

### **Training Metrics**
- **Loss**: Training and validation loss
- **Learning Rate**: Current learning rate
- **Epoch**: Current epoch
- **Step**: Current training step
- **GPU Usage**: GPU memory and utilization
- **Training Time**: Time per step and epoch

### **Model Configuration**
- **Model Name**: GPT-2 Medium
- **Vocabulary Size**: 50,000 tokens
- **Context Length**: 1,024 tokens
- **Batch Size**: Per-device batch size
- **Learning Rate**: 3e-5
- **Epochs**: 5
- **Special Tokens**: 100+ historical tokens

### **Hardware Information**
- **GPU Count**: Number of available GPUs
- **GPU Names**: GPU model names
- **GPU Memory**: Available GPU memory
- **Mixed Precision**: FP16/BF16 status
- **Distributed Training**: Multi-GPU status

## 🎯 **Usage Examples**

### **Single GPU Training**
```bash
# Set API key
export WANDB_API_KEY=your_key_here

# Run training
python 04_training/train_model.py
```

### **Multi-GPU Training**
```bash
# Set API key
export WANDB_API_KEY=your_key_here

# Run multi-GPU training
python 10_scripts/launch_multi_gpu_training.py
```

### **Interactive Launcher**
```bash
# Set API key
export WANDB_API_KEY=your_key_here

# Use interactive launcher
python 10_scripts/launch_london_llm.py
```

## 📈 **Monitoring Training**

### **Real-time Monitoring**
1. **Open WandB Dashboard**: [https://wandb.ai](https://wandb.ai)
2. **Navigate to Project**: `london-historical-llm`
3. **Select Run**: Choose your current training run
4. **View Metrics**: Monitor loss, learning rate, GPU usage

### **Key Metrics to Watch**
- **Training Loss**: Should decrease over time
- **Validation Loss**: Should track training loss
- **Learning Rate**: Should follow cosine schedule
- **GPU Memory**: Should be stable
- **Training Speed**: Steps per second

### **Alerts and Notifications**
- **Loss Plateau**: Set up alerts for loss stagnation
- **GPU Memory**: Monitor for out-of-memory errors
- **Training Time**: Track total training duration

## 🔧 **Advanced Configuration**

### **Custom WandB Settings**
```python
# In train_model.py, you can customize:
wandb.init(
    project="london-historical-llm",
    name="custom-run-name",
    config={
        "custom_param": "value",
        "data_sources": 12,
        "historical_period": "1500-1850"
    },
    tags=["custom", "experiment"],
    notes="Custom experiment notes"
)
```

### **Offline Mode**
```bash
# For offline training
export WANDB_MODE=offline
python 04_training/train_model.py

# Sync later
wandb sync wandb/offline-run-*
```

### **Team Collaboration**
```bash
# Set team entity
export WANDB_ENTITY=your-team-name
python 04_training/train_model.py
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **API Key Not Found**
   ```
   Error: WandB API key not found
   Solution: Set WANDB_API_KEY environment variable
   ```

2. **Network Issues**
   ```
   Error: Failed to connect to WandB
   Solution: Check internet connection or use offline mode
   ```

3. **Permission Denied**
   ```
   Error: Permission denied
   Solution: Check API key permissions
   ```

4. **Project Not Found**
   ```
   Error: Project not found
   Solution: Create project in WandB dashboard
   ```

### **Debug Mode**
```bash
# Enable debug logging
export WANDB_DEBUG=true
python 04_training/train_model.py
```

## 📊 **Expected Dashboard Views**

### **Training Overview**
- **Loss Curves**: Training and validation loss over time
- **Learning Rate**: Learning rate schedule
- **GPU Usage**: Memory and utilization graphs
- **Training Speed**: Steps per second

### **Model Information**
- **Architecture**: GPT-2 Medium configuration
- **Parameters**: 355M parameters
- **Vocabulary**: 50,000 tokens
- **Context Length**: 1,024 tokens

### **Hardware Metrics**
- **GPU Memory**: Peak and average usage
- **GPU Utilization**: Percentage usage over time
- **Training Time**: Time per step and epoch
- **Data Throughput**: Samples per second

## 🎉 **Benefits of WandB Integration**

### **Experiment Tracking**
- **Compare Runs**: Compare different training configurations
- **Hyperparameter Tuning**: Track parameter effects
- **Model Versioning**: Version control for models
- **Reproducibility**: Reproduce successful runs

### **Collaboration**
- **Team Sharing**: Share results with team members
- **Real-time Monitoring**: Monitor training progress
- **Alerts**: Get notified of issues
- **Documentation**: Document experiments and findings

### **Analysis**
- **Performance Metrics**: Analyze training performance
- **Resource Usage**: Monitor hardware utilization
- **Model Quality**: Track model quality metrics
- **Historical Data**: Compare with previous experiments

## 🚀 **Ready to Track!**

With WandB properly configured, you'll get comprehensive monitoring of your London Historical LLM training, including:

- ✅ **Real-time Metrics**: Loss, learning rate, GPU usage
- ✅ **Model Configuration**: All hyperparameters tracked
- ✅ **Hardware Monitoring**: GPU memory and utilization
- ✅ **Experiment Comparison**: Compare different runs
- ✅ **Team Collaboration**: Share results with others
- ✅ **Reproducibility**: Reproduce successful experiments

**Start training with full monitoring!** 📊✨
