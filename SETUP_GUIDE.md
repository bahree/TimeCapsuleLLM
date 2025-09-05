# London Historical LLM - Complete Setup Guide

## 🚀 Quick Start for New Machine

This guide will help you set up the London Historical LLM on a new machine with 2 NVIDIA GPUs.

## Prerequisites

- **Python 3.8+**
- **2+ NVIDIA GPUs** (CUDA compatible)
- **8GB+ RAM** (16GB+ recommended)
- **10GB+ free disk space**
- **Internet connection** (for downloading historical texts)

## Step-by-Step Setup

### 1. Clone Repository
```bash
# Clone the repository
git clone <your-repo-url>
cd TimeCapsuleLLM
```

### 2. Create Virtual Environment
```bash
# Create virtual environment (project-specific name)
python3 -m venv london-llm-env

# Activate virtual environment
source london-llm-env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

**Virtual Environment Naming:**
- `london-llm-env` - Project-specific name (recommended)
- `venv` - Generic name (works but less descriptive)
- `env` - Short name (also works)
- `london-historical-llm` - Very descriptive (longer)

**Why project-specific names?**
- Clear which project the environment belongs to
- Avoid conflicts with other projects
- Easier to manage multiple projects
- Better organization

### 3. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify PyTorch with CUDA support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')"
```

**Expected output:**
```
CUDA available: True
GPU count: 2
```

**Note:** Always activate the virtual environment before running any Python commands:
```bash
source london-llm-env/bin/activate
```

### 4. Test Setup
```bash
# Verify everything is working
python test_setup.py
```

**Expected output:**
```
✅ All tests passed! Setup is ready.
```

### 5. Preview Data Sources (Optional)
```bash
# See exactly what will be downloaded
python preview_data_sources.py
```

This shows you the complete list of 200+ historical texts that will be downloaded.

### 6. Complete Multi-GPU Setup
```bash
# Run the complete setup optimized for 2 GPUs
python setup_multi_gpu.py
```

**What this does:**
- ✅ Checks your 2 GPUs
- ✅ Downloads all historical texts (~500MB-1GB)
- ✅ Trains custom tokenizer
- ✅ Prepares training data
- ✅ Creates launch scripts

### 7. Launch Training
```bash
# For Linux/Mac:
./launch_2gpu.sh

# For Windows:
launch_2gpu.bat

# Or manually:
torchrun --standalone --nproc_per_node=2 train_london_llm_multi_gpu.py
```

### 8. Monitor Training
```bash
# Monitor GPU usage
nvidia-smi -l 1

# Check training progress
tail -f out_london_historical/training.log
```

### 9. Generate Text (After Training)
```bash
# Generate historical text
python sample_london_llm.py --prompt "In the year of our Lord 1834,"

# Or use the interactive mode
python run_london_llm.py --interactive
```

## Complete Command Sequence

Here's the exact sequence to run on your new machine:

```bash
# 1. Clone repository
git clone <your-repo-url>
cd TimeCapsuleLLM

# 2. Create virtual environment
python3 -m venv london-llm-env
source london-llm-env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test setup
python test_setup.py

# 5. Complete setup
python setup_multi_gpu.py

# 6. Start training
./launch_2gpu.sh

# 7. Generate text (after training completes)
python sample_london_llm.py --prompt "In the year of our Lord 1834,"
```

**Important:** Always activate the virtual environment first:
```bash
source london-llm-env/bin/activate
```

## Expected Timeline

- **Setup**: 5-10 minutes
- **Data Download**: 10-30 minutes (depending on internet)
- **Tokenizer Training**: 5-10 minutes
- **Model Training**: 30-60 minutes (with 2 GPUs)
- **Total**: ~1-2 hours

## What to Expect

### During Setup
- Downloads ~200 historical texts from Project Gutenberg
- Creates custom tokenizer optimized for historical English
- Prepares training data binaries
- Shows progress for each step

### During Training
- Uses both GPUs efficiently
- Shows loss curves and metrics
- Saves checkpoints every 200 iterations
- Training typically converges in 5,000-10,000 iterations

### After Training
- Model saved in `out_london_historical/ckpt.pt`
- Can generate historical text in 1500-1850 style
- Model speaks without modern bias

## Data Sources

The system automatically downloads from:
- **Project Gutenberg**: 200+ historical texts (1500-1850)
- **Authors include**: Jane Austen, Charles Dickens, Walter Scott, Mary Shelley, etc.
- **Content**: Novels, poetry, political texts, legal documents
- **Total size**: ~500MB-1GB of text

## Model Architecture

- **Parameters**: ~16M (efficient and fast)
- **Layers**: 12 transformer layers
- **Heads**: 12 attention heads
- **Embedding**: 768 dimensions
- **Context**: 256 tokens
- **Vocabulary**: 50,000 tokens (optimized for historical English)

## Troubleshooting

### Externally Managed Environment Error
If you get `error: externally-managed-environment`:

```bash
# Create virtual environment
python3 -m venv london-llm-env

# Activate virtual environment
source london-llm-env/bin/activate

# Then install packages
pip install -r requirements.txt
```

**Alternative solutions:**
```bash
# Option 1: Use pipx (if available)
pipx install torch torchvision torchaudio

# Option 2: Override (not recommended)
pip install -r requirements.txt --break-system-packages

# Option 3: Use system packages
sudo apt install python3-torch python3-torchvision python3-torchaudio
```

### CUDA Not Detected
```bash
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Data Download Fails
```bash
# Run data preparation manually
python data_preparation.py
```

### Training Fails
```bash
# Check GPU memory
nvidia-smi

# Reduce batch size in train_london_llm_multi_gpu.py
# Change batch_size = 12 to batch_size = 8
```

### Out of Memory
```bash
# Reduce model size in train_london_llm_multi_gpu.py
# Change n_layer = 12 to n_layer = 8
# Change n_embd = 768 to n_embd = 512
```

## Monitoring Commands

```bash
# Monitor GPU usage
watch -n 1 nvidia-smi

# Check training progress
ls -la out_london_historical/

# View training logs
tail -f out_london_historical/training.log

# Check model checkpoints
ls -la out_london_historical/ckpt.pt
```

## Success Indicators

You'll know it's working when you see:
- ✅ "CUDA available: True"
- ✅ "Found 2 GPU(s)"
- ✅ "Downloading historical texts..."
- ✅ "Training completed successfully!"
- ✅ Generated text in historical style

## File Structure After Setup

```
TimeCapsuleLLM/
├── london_data/                    # Historical texts
│   ├── london_corpus_merged.txt   # Complete training corpus
│   └── individual_texts/           # Individual text files
├── data/london_data/               # Training data binaries
│   ├── train.bin                   # Training data
│   ├── val.bin                     # Validation data
│   └── meta.pkl                    # Metadata
├── tokenizer_london/               # Custom tokenizer
│   ├── vocab.json                  # Vocabulary
│   └── merges.txt                  # Merge rules
├── out_london_historical/          # Trained model
│   └── ckpt.pt                     # Model checkpoint
├── launch_2gpu.sh                 # Launch script (Linux/Mac)
├── launch_2gpu.bat                # Launch script (Windows)
└── ... (other files)
```

## Advanced Usage

### Custom Training Parameters
Edit `train_london_llm_multi_gpu.py` to modify:
- Model architecture (layers, heads, embedding size)
- Training parameters (learning rate, batch size)
- Training duration (max iterations)

### Custom Prompts
```bash
# Generate with custom prompts
python sample_london_llm.py --prompt "The streets of London were"
python sample_london_llm.py --prompt "It was a dark and stormy night"
python sample_london_llm.py --prompt "The gentleman from the country said"
```

### Interactive Mode
```bash
# Use interactive mode for easy experimentation
python run_london_llm.py --interactive
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run `python test_setup.py` to verify setup
3. Check GPU memory with `nvidia-smi`
4. Review training logs in `out_london_historical/`

## Next Steps

After successful setup:
1. Experiment with different prompts
2. Try different model architectures
3. Add more historical texts
4. Fine-tune for specific time periods
5. Share your results!

---

**Note**: This system creates a "time capsule" AI that speaks in the style of 1500-1850 London. The model is trained exclusively on historical texts and avoids modern bias.
