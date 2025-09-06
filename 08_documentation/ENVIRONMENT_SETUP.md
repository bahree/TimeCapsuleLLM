# Environment Setup Guide

This guide will help you set up the Python environment for the London Historical LLM project.

## Prerequisites

- Python 3.8 or higher
- 8GB+ RAM (16GB+ recommended)
- 100GB+ free disk space
- CUDA-capable GPU (recommended for training)

## Quick Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd TimeCapsuleLLM
```

### 2. Run Environment Setup
```bash
python 01_environment/setup_environment.py
```

### 3. Activate Environment
```bash
# Windows
activate_env.bat

# Linux/Mac
source activate_env.sh
```

## Manual Setup

### 1. Create Virtual Environment
```bash
python -m venv london-llm-env

# Windows
london-llm-env\Scripts\activate

# Linux/Mac
source london-llm-env/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

## Environment Variables

The setup script creates these environment variables:

- `LONDON_LLM_ROOT`: Project root directory
- `LONDON_LLM_DATA`: Data directory path
- `LONDON_LLM_MODELS`: Models directory path

## Troubleshooting

### Common Issues

1. **Python Version Error**
   - Ensure Python 3.8+ is installed
   - Check with `python --version`

2. **CUDA Not Available**
   - Install CUDA toolkit if you have a compatible GPU
   - CPU-only training is supported but slower

3. **Permission Errors**
   - Run as administrator on Windows
   - Use `sudo` on Linux/Mac if needed

4. **Memory Issues**
   - Reduce batch size in training scripts
   - Use gradient accumulation
   - Consider using smaller models

### Getting Help

- Check the logs in `logs/` directory
- Run system tests: `python 06_testing/test_system.py`
- Review the troubleshooting guide

## Next Steps

After environment setup:

1. Download historical data: `cd 02_data_collection && python download_historical_data.py`
2. Train tokenizer: `cd 03_tokenizer && python train_tokenizer.py`
3. Train model: `cd 04_training && python train_model.py`
4. Evaluate model: `cd 05_evaluation && python evaluate_model.py`

## System Requirements

### Minimum Requirements
- Python 3.8
- 8GB RAM
- 50GB disk space
- CPU-only training

### Recommended Requirements
- Python 3.9+
- 16GB+ RAM
- 100GB+ disk space
- CUDA-capable GPU (8GB+ VRAM)
- SSD storage

### Optimal Requirements
- Python 3.10+
- 32GB+ RAM
- 200GB+ disk space
- Multiple CUDA GPUs
- NVMe SSD storage
