# 🏛️ Hello London - Historical LLM (1500-1850)

A comprehensive system for training a Small Language Model on historical London texts from 1500-1850, including data collection, tokenization, training, and evaluation.

## 🔗 Repository

- **GitHub**: https://github.com/bahree/helloLondon
- **Status**: Private (will be made public after training completion)
- **Main Branch**: `main` (production-ready code)
- **Development Branch**: `dev` (active development)

## 📁 Repository Structure

```
helloLondon/
├── 01_environment/          # Environment setup and configuration
│   └── setup_environment.py
├── 02_data_collection/      # Data downloading and processing
│   └── download_historical_data.py
├── 03_tokenizer/           # Custom tokenizer training
│   └── train_tokenizer.py
├── 04_training/            # Model training scripts
│   └── train_model.py
├── 05_evaluation/          # Model evaluation and testing
│   └── evaluate_model.py
├── 06_testing/             # Test scripts and validation
│   └── test_system.py
├── 07_utilities/           # Utility files and assets
│   ├── README.md
│   ├── *.png, *.jpg        # Images and diagrams
│   ├── *.csv               # Data files
│   └── *.txt               # Reference documents
├── 08_documentation/       # Documentation and guides
│   ├── README.md           # Main documentation
│   ├── ENVIRONMENT_SETUP.md
│   ├── DATA_COLLECTION.md
│   ├── WANDB_SETUP.md
│   └── [other guides...]
├── 09_models/              # Trained models and checkpoints
│   ├── old_models/         # Archived previous versions
│   └── [current models will be created here]
└── 10_scripts/             # Launch scripts and automation
    ├── launch_london_llm.py
    ├── launch_multi_gpu_training.py
    └── [other launch scripts...]
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/bahree/helloLondon.git
cd helloLondon
```

### 2. Switch to Development Branch
```bash
git checkout dev
```

### 3. Environment Setup
```bash
python 01_environment/setup_environment.py
```

### 4. Data Collection
```bash
python 02_data_collection/download_historical_data.py
```

### 5. Train Tokenizer
```bash
python 03_tokenizer/train_tokenizer.py
```

### 6. Train Model
```bash
# Single GPU
python 04_training/train_model.py

# Multi-GPU
python 10_scripts/launch_multi_gpu_training.py

# Interactive launcher
python 10_scripts/launch_london_llm.py
```

### 7. Evaluate Model
```bash
python 05_evaluation/evaluate_model.py
```

## 📊 Data Sources

- **London Lives 1690-1800**: 240,000 manuscript pages from eight London archives
- **Old Bailey Proceedings**: 197,000+ trial accounts from London's Central Criminal Court
- **The National Archives**: UK government records and correspondence
- **British History Online**: Digital library of primary and secondary sources
- **Project Gutenberg**: Public domain literature and historical texts
- **Internet Archive**: Historical documents and manuscripts

## 🎯 Features

- **Comprehensive Data Collection**: 12+ historical sources with automatic retry
- **Custom Tokenizer**: 50,000 vocabulary with 100+ historical special tokens
- **Multi-GPU Training**: Efficient training on single/multiple GPUs
- **WandB Integration**: Comprehensive experiment tracking
- **Advanced Evaluation**: Multiple evaluation metrics and tests
- **Failed Download Recovery**: Manual retry system for failed downloads
- **Remote Machine Support**: Optimized for remote server execution

## 📈 Expected Results

- **Data Volume**: 500MB - 2GB of processed historical text
- **Time Coverage**: 1500-1850 (350 years)
- **Model Size**: GPT-2 Medium (355M parameters)
- **Training Time**: 2-7 days on modern hardware
- **Vocabulary**: 50,000 tokens with historical language support

## 🔧 Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- 16GB+ RAM
- 100GB+ disk space
- WandB account (optional, for experiment tracking)

## 🚀 Development Workflow

### Working on Features
```bash
# Always work on dev branch
git checkout dev

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Description of changes"

# Push to dev branch
git push origin dev
```

### Merging to Main
```bash
# Create pull request on GitHub
# After review and approval, merge to main

# Update local main
git checkout main
git pull origin main
```

## 📚 Documentation

- [Environment Setup Guide](08_documentation/ENVIRONMENT_SETUP.md)
- [Data Collection Guide](08_documentation/DATA_COLLECTION.md)
- [WandB Setup Guide](08_documentation/WANDB_SETUP.md)
- [GPU and WandB Capabilities](08_documentation/GPU_WANDB_CAPABILITIES.md)
- [Training Guide](08_documentation/TRAINING.md)
- [Evaluation Guide](08_documentation/EVALUATION.md)

## 🔐 Repository Status

- **Current**: Private repository
- **Future**: Will be made public after training completion
- **Development**: Active development on `dev` branch
- **Production**: Stable releases on `main` branch

## 🆘 Support

For issues and questions:
1. Check the troubleshooting guide
2. Review the documentation
3. Check the logs in the respective folders
4. Create an issue on GitHub

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to build your London Historical LLM!** 🏛️✨

**Repository**: https://github.com/bahree/helloLondon
**Development Branch**: `dev`
**Status**: Private (will be public after training)
