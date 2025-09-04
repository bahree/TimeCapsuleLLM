"""
Complete setup script for London Historical LLM
Downloads data, trains tokenizer, and prepares for training
"""

import os
import sys
import subprocess
from pathlib import Path
import json

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def check_requirements():
    """Check if required packages are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        'torch', 'transformers', 'tokenizers', 'tiktoken', 
        'numpy', 'tqdm', 'requests', 'beautifulsoup4'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing requirements...")
        if not run_command("pip install -r requirements.txt", "Installing requirements"):
            return False
    else:
        print("✅ All requirements satisfied")
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "london_data",
        "data/london_data", 
        "tokenizer_london",
        "out_london_historical"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")
    
    return True

def download_data():
    """Download historical data"""
    print("\n📚 Downloading historical data...")
    
    if not os.path.exists("london_data/london_corpus_merged.txt"):
        if not run_command("python data_preparation.py", "Downloading historical texts"):
            return False
    else:
        print("✅ Data already downloaded")
    
    return True

def train_tokenizer():
    """Train the tokenizer"""
    print("\n🔤 Training tokenizer...")
    
    if not os.path.exists("tokenizer_london/vocab.json"):
        if not run_command("python train_tokenizer_london.py", "Training tokenizer"):
            return False
    else:
        print("✅ Tokenizer already trained")
    
    return True

def create_training_config():
    """Create training configuration"""
    print("\n⚙️  Creating training configuration...")
    
    config = {
        "model": {
            "n_layer": 8,
            "n_head": 8,
            "n_embd": 512,
            "block_size": 256,
            "dropout": 0.1,
            "bias": False
        },
        "training": {
            "learning_rate": 3e-4,
            "max_iters": 10000,
            "batch_size": 8,
            "gradient_accumulation_steps": 4,
            "warmup_iters": 500,
            "weight_decay": 1e-1
        },
        "data": {
            "dataset": "london_data",
            "vocab_size": 50000
        }
    }
    
    with open("london_llm_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration saved to london_llm_config.json")
    return True

def create_quick_start_guide():
    """Create a quick start guide"""
    guide = """
# London Historical LLM - Quick Start Guide

## Setup Complete! 🎉

Your London Historical LLM is now ready for training. Here's what was set up:

### Files Created:
- `london_data/london_corpus_merged.txt` - Historical texts corpus
- `data/london_data/` - Training data binaries (train.bin, val.bin, meta.pkl)
- `tokenizer_london/` - Custom tokenizer files
- `london_llm_config.json` - Training configuration

### Next Steps:

1. **Start Training:**
   ```bash
   python train_london_llm.py
   ```

2. **Generate Text (after training):**
   ```bash
   python sample_london_llm.py --prompt "In the year of our Lord 1834,"
   ```

3. **Monitor Training:**
   - Checkpoints saved to `out_london_historical/`
   - Training logs show loss and performance metrics

### Model Architecture:
- **Parameters**: ~16M (small, fast training)
- **Context Length**: 256 tokens
- **Vocabulary**: 50,000 tokens (optimized for historical English)
- **Time Period**: 1500-1850 London texts

### Training Tips:
- Training on CPU: ~2-4 hours for basic model
- Training on GPU: ~30-60 minutes
- Monitor validation loss - stop when it stops improving
- Use `--device cuda` for GPU training

### Sample Prompts:
- "In the year of our Lord 1834,"
- "The streets of London were"
- "It was a dark and stormy night"
- "The gentleman from the country"

Happy training! 🏛️
"""
    
    with open("QUICK_START.md", 'w') as f:
        f.write(guide)
    
    print("✅ Quick start guide created: QUICK_START.md")

def main():
    """Main setup pipeline"""
    print("🏛️  London Historical LLM Setup")
    print("=" * 50)
    
    steps = [
        ("Checking requirements", check_requirements),
        ("Setting up directories", setup_directories),
        ("Downloading data", download_data),
        ("Training tokenizer", train_tokenizer),
        ("Creating config", create_training_config),
        ("Creating guide", create_quick_start_guide)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"\n❌ Setup failed at step: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python train_london_llm.py")
    print("2. After training: python sample_london_llm.py")
    print("3. Read QUICK_START.md for more details")

if __name__ == "__main__":
    main()
