"""
Dataset preparation script for London Historical LLM
Converts the merged corpus into train.bin and val.bin files
"""

import os
import pickle
import numpy as np
from pathlib import Path
from tqdm import tqdm

def prepare_dataset():
    """Prepare dataset from merged corpus"""
    print("📦 Preparing dataset for training")
    print("=" * 40)
    
    # Try multiple possible corpus locations
    possible_paths = [
        "data/london_data/london_corpus_merged.txt",
        "london_data/london_corpus_merged.txt",
        "london_data/london_corpus_merged_fixed.txt"
    ]
    
    corpus_path = None
    for path in possible_paths:
        if os.path.exists(path):
            corpus_path = path
            break
    
    if not corpus_path:
        print(f"❌ Corpus not found in any of these locations:")
        for path in possible_paths:
            print(f"   - {path}")
        print("Please run data_preparation.py first to download and prepare the data.")
        return False
    
    print(f"✅ Found corpus at: {corpus_path}")
    
    # Read corpus
    print("📖 Reading corpus...")
    with open(corpus_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"📄 Corpus size: {len(text):,} characters")
    
    # Simple character-level tokenization (fallback)
    print("🔤 Tokenizing text...")
    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    
    # Create mappings
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}
    
    # Encode text
    data = [stoi[c] for c in text]
    print(f"📊 Vocabulary size: {vocab_size:,}")
    print(f"📊 Total tokens: {len(data):,}")
    
    # Split into train/val
    split_idx = int(0.9 * len(data))
    train_data = data[:split_idx]
    val_data = data[split_idx:]
    
    print(f"📊 Train tokens: {len(train_data):,}")
    print(f"📊 Val tokens: {len(val_data):,}")
    
    # Create data directory
    data_dir = Path("data/london_data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as binary files
    print("💾 Saving binary files...")
    train_array = np.array(train_data, dtype=np.uint16)
    val_array = np.array(val_data, dtype=np.uint16)
    
    train_array.tofile(data_dir / "train.bin")
    val_array.tofile(data_dir / "val.bin")
    
    # Save metadata
    meta = {
        'vocab_size': vocab_size,
        'itos': itos,
        'stoi': stoi,
        'train_tokens': len(train_data),
        'val_tokens': len(val_data),
        'total_tokens': len(data)
    }
    
    with open(data_dir / "meta.pkl", 'wb') as f:
        pickle.dump(meta, f)
    
    print(f"✅ Dataset prepared successfully!")
    print(f"   📁 Data directory: {data_dir}")
    print(f"   📄 Train file: {data_dir / 'train.bin'}")
    print(f"   📄 Val file: {data_dir / 'val.bin'}")
    print(f"   📄 Metadata: {data_dir / 'meta.pkl'}")
    
    return True

def main():
    """Main dataset preparation"""
    success = prepare_dataset()
    
    if success:
        print("\n🎉 Dataset preparation complete!")
        print("You can now run: python train_london_llm.py")
    else:
        print("\n❌ Dataset preparation failed!")

if __name__ == "__main__":
    main()
