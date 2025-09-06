# London Historical LLM (1500-1850)

A language model trained exclusively on historical London texts from 1500-1850, built using [nanoGPT](https://github.com/karpathy/nanoGPT) by Andrej Karpathy.

## 🏛️ Project Overview

This project creates a "time capsule" language model that speaks and writes in the style of historical London, without any modern bias or knowledge. The model is trained from scratch on texts from the 1500-1850 period, capturing the vocabulary, writing style, and worldview of that era.

### Key Features

- **Historical Accuracy**: Trained only on texts from 1500-1850 London
- **Period-Appropriate Language**: Uses vocabulary and grammar from the era
- **No Modern Bias**: Completely isolated from modern concepts and language
- **Educational**: Perfect for understanding historical writing styles
- **Small & Fast**: ~16M parameters, trains quickly on consumer hardware

## 🚀 Quick Start

### 1. Test Your Setup
```bash
python test_setup.py
```

### 2. Complete Setup
```bash
python setup_london_llm.py
```

### 3. Train the Model
```bash
python train_london_llm.py
```

### 4. Generate Text
```bash
python sample_london_llm.py --prompt "In the year of our Lord 1834,"
```

## 📁 Project Structure

```
TimeCapsuleLLM/
├── london_1800_1850_v0/          # Original nanoGPT implementation
│   ├── model.py                  # GPT model architecture
│   ├── train.py                  # Training script
│   ├── sample.py                 # Sampling script
│   └── metadata_london.csv       # Historical texts metadata
├── data_preparation.py           # Downloads historical texts
├── train_tokenizer_london.py     # Trains custom tokenizer
├── train_london_llm.py          # Main training script
├── sample_london_llm.py         # Text generation script
├── setup_london_llm.py          # Complete setup automation
├── test_setup.py                # Setup verification
└── requirements.txt             # Python dependencies
```

## 🔧 Installation

### Prerequisites
- Python 3.8+
- PyTorch 2.0+
- CUDA (optional, for GPU training)

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 📚 Data Sources

The model is trained on historical texts from:
- **Project Gutenberg**: Public domain books from 1500-1850
- **London-specific texts**: Novels, legal documents, newspapers
- **Authors include**: Jane Austen, Charles Dickens, Walter Scott, and many others

### Sample Texts
- Pride and Prejudice (1813)
- Frankenstein (1818)
- Oliver Twist (1837-39)
- A Christmas Carol (1843)
- And 200+ other historical works

## 🧠 Model Architecture

- **Parameters**: ~16M (small and efficient)
- **Context Length**: 256 tokens
- **Vocabulary**: 50,000 tokens (optimized for historical English)
- **Architecture**: GPT-style transformer
- **Training**: From scratch (not fine-tuned)

## 🎯 Usage Examples

### Basic Text Generation
```python
python sample_london_llm.py --prompt "The streets of London were"
```

### Historical Prompts
```python
# 1834 protest reference
python sample_london_llm.py --prompt "In the year of our Lord 1834,"

# Victorian writing style
python sample_london_llm.py --prompt "It was a dark and stormy night"

# Period-appropriate dialogue
python sample_london_llm.py --prompt "The gentleman from the country said"
```

### Custom Parameters
```python
python sample_london_llm.py \
    --prompt "In the year of our Lord 1834," \
    --max_tokens 1000 \
    --temperature 0.8 \
    --top_k 200 \
    --num_samples 5
```

## ⚙️ Training Configuration

### Model Settings
- **Layers**: 8
- **Heads**: 8
- **Embedding**: 512
- **Dropout**: 0.1
- **Context**: 256 tokens

### Training Settings
- **Learning Rate**: 3e-4
- **Batch Size**: 8
- **Max Iterations**: 10,000
- **Warmup**: 500 iterations
- **Weight Decay**: 1e-1

### Hardware Requirements
- **CPU Training**: 2-4 hours
- **GPU Training**: 30-60 minutes
- **RAM**: 8GB+ recommended
- **Storage**: 2GB for data + model

## 🔍 Understanding the Output

The model generates text that:
- Uses period-appropriate vocabulary
- Follows historical writing conventions
- References events and concepts from 1500-1850
- Avoids modern language and concepts
- May include some historical inaccuracies (as expected)

### Example Output
```
In the year of our Lord 1834, the streets of London were filled with 
protest and petition. The cause, as many recounted, was not bound in 
the way of private interest, but having taken up the same day in the 
matter of Lord Palmerston, the public will receive a short statement 
of the difficulties under which the day of law has reached us...
```

## 🛠️ Development

### Adding New Data
1. Add new texts to `london_data/`
2. Update `metadata_london.csv`
3. Re-run data preparation
4. Retrain tokenizer if needed

### Modifying Model Architecture
Edit `train_london_llm.py` and adjust:
- `n_layer`, `n_head`, `n_embd`
- `block_size`, `dropout`
- Training parameters

### Custom Tokenizer
Modify `train_tokenizer_london.py` to:
- Change vocabulary size
- Add special tokens
- Use different tokenization method

## 📊 Performance

### Training Metrics
- **Loss**: Typically reaches 2.5-3.0
- **Convergence**: 5,000-10,000 iterations
- **Memory**: ~4GB GPU / ~8GB CPU

### Generation Quality
- **Coherence**: Good for short sequences
- **Historical Accuracy**: High for vocabulary/style
- **Factual Accuracy**: Variable (as expected)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add historical texts or improvements
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is based on nanoGPT by Andrej Karpathy (MIT License).
Historical texts are in the public domain.

## 🙏 Acknowledgments

- **Andrej Karpathy** for nanoGPT
- **Project Gutenberg** for historical texts
- **The original TimeCapsuleLLM project** for inspiration

## 🔗 Related Projects

- [nanoGPT](https://github.com/karpathy/nanoGPT) - Base implementation
- [TimeCapsuleLLM](https://github.com/haykgrigo3/TimeCapsuleLLM) - Original project
- [Project Gutenberg](https://www.gutenberg.org/) - Historical texts

## 📞 Support

For questions or issues:
1. Check the test script: `python test_setup.py`
2. Review the quick start guide
3. Open an issue on GitHub

---

**Note**: This model is for educational and research purposes. It may generate historically inaccurate or inappropriate content. Use responsibly.
