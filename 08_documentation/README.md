# 🏛️ London Historical LLM (1500-1850)

A comprehensive system for training a Small Language Model on historical London texts from 1500-1850, including data collection, tokenization, training, and evaluation.

## 📁 Repository Structure

```
TimeCapsuleLLM/
├── 01_environment/          # Environment setup and configuration
├── 02_data_collection/      # Data downloading and processing
├── 03_tokenizer/           # Custom tokenizer training
├── 04_training/            # Model training scripts
├── 05_evaluation/          # Model evaluation and testing
├── 06_testing/             # Test scripts and validation
├── 07_utilities/           # Utility scripts and helpers
├── 08_documentation/       # Documentation and guides
├── 09_models/              # Trained models and checkpoints
└── 10_scripts/             # Launch scripts and automation
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
cd 01_environment
python setup_environment.py
```

### 2. Data Collection
```bash
cd 02_data_collection
python download_historical_data.py
```

### 3. Train Tokenizer
```bash
cd 03_tokenizer
python train_tokenizer.py
```

### 4. Train Model
```bash
cd 04_training
python train_model.py
```

### 5. Evaluate Model
```bash
cd 05_evaluation
python evaluate_model.py
```

## 📊 Data Sources

- **London Lives 1690-1800**: 240,000 manuscript pages from eight London archives
- **Old Bailey Proceedings**: 197,000+ trial accounts from London's Central Criminal Court
- **The National Archives**: UK government records and correspondence
- **British History Online**: Digital library of primary and secondary sources
- **Project Gutenberg**: Public domain literature and historical texts
- **Internet Archive**: Historical documents and manuscripts

## 🎯 Features

- **Comprehensive Data Collection**: Multiple historical sources with automatic retry
- **Custom Tokenizer**: Optimized for historical English language
- **Multi-GPU Training**: Efficient training on multiple GPUs
- **Advanced Evaluation**: Multiple evaluation metrics and tests
- **Failed Download Recovery**: Manual retry system for failed downloads
- **Remote Machine Support**: Optimized for remote server execution

## 📈 Expected Results

- **Data Volume**: 500MB - 2GB of processed historical text
- **Time Coverage**: 1500-1850 (350 years)
- **Model Size**: 7B-13B parameters (configurable)
- **Training Time**: 2-7 days on modern hardware

## 🔧 Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- 16GB+ RAM
- 100GB+ disk space

## 📚 Documentation

- [Environment Setup Guide](08_documentation/ENVIRONMENT_SETUP.md)
- [Data Collection Guide](08_documentation/DATA_COLLECTION.md)
- [Training Guide](08_documentation/TRAINING.md)
- [Evaluation Guide](08_documentation/EVALUATION.md)
- [Troubleshooting](08_documentation/TROUBLESHOOTING.md)

## 🆘 Support

For issues and questions:
1. Check the troubleshooting guide
2. Review the documentation
3. Check the logs in the respective folders

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to build your London Historical LLM!** 🏛️✨