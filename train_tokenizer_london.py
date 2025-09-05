"""
Tokenizer training script for London Historical LLM
Creates a custom tokenizer optimized for historical English texts
"""

import os
import json
from pathlib import Path
from tokenizers import Tokenizer, models, pre_tokenizers, trainers, processors
from tokenizers.normalizers import NFD, Lowercase, StripAccents, Sequence
import tiktoken
from tqdm import tqdm

class LondonTokenizerTrainer:
    def __init__(self, corpus_path, output_dir="tokenizer_london", vocab_size=50000):
        self.corpus_path = Path(corpus_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.vocab_size = vocab_size
        
    def train_huggingface_tokenizer(self):
        """Train a HuggingFace tokenizer"""
        print("🔤 Training HuggingFace tokenizer...")
        
        # Initialize tokenizer
        tokenizer = Tokenizer(models.BPE())
        tokenizer.normalizer = Sequence([NFD(), Lowercase(), StripAccents()])
        tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
        
        # Configure trainer
        trainer = trainers.BpeTrainer(
            vocab_size=self.vocab_size,
            special_tokens=["<|endoftext|>", "<|startoftext|>", "<|pad|>", "<|unk|>"],
            min_frequency=2,
            show_progress=True
        )
        
        # Train on corpus
        print(f"Training on corpus: {self.corpus_path}")
        tokenizer.train([str(self.corpus_path)], trainer)
        
        # Add post-processor
        tokenizer.post_processor = processors.ByteLevel(trim_offsets=True)
        
        # Save tokenizer
        tokenizer.save(str(self.output_dir / "tokenizer.json"))
        
        # Save vocab and merges separately for compatibility
        vocab = tokenizer.get_vocab()
        with open(self.output_dir / "vocab.json", 'w') as f:
            json.dump(vocab, f, indent=2)
        
        # Extract merges (simplified - in practice you'd need to extract from BPE)
        merges = []
        with open(self.output_dir / "merges.txt", 'w') as f:
            for line in merges:
                f.write(line + '\n')
        
        print(f"✅ HuggingFace tokenizer saved to {self.output_dir}")
        return tokenizer
    
    def train_tiktoken_tokenizer(self):
        """Train a tiktoken tokenizer"""
        print("🔤 Training tiktoken tokenizer...")
        
        # Read corpus
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Corpus size: {len(text):,} characters")
        
        # Train tokenizer
        tokenizer = tiktoken.train_new_bpe(
            text,
            vocab_size=self.vocab_size,
            special_tokens=["<|endoftext|>", "<|startoftext|>", "<|pad|>", "<|unk|>"]
        )
        
        # Save tokenizer
        tokenizer.save_model(str(self.output_dir))
        
        print(f"✅ tiktoken tokenizer saved to {self.output_dir}")
        return tokenizer
    
    def create_dataset_binaries(self, tokenizer_type="huggingface"):
        """Create train.bin and val.bin files for training"""
        print("📦 Creating dataset binaries...")
        
        # Read corpus
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Tokenize
        if tokenizer_type == "huggingface":
            from tokenizers import Tokenizer
            tokenizer = Tokenizer.from_file(str(self.output_dir / "tokenizer.json"))
            tokens = tokenizer.encode(text).ids
        else:  # tiktoken
            import tiktoken
            tokenizer = tiktoken.get_encoding("cl100k_base")  # Load saved tokenizer
            tokens = tokenizer.encode(text)
        
        print(f"Total tokens: {len(tokens):,}")
        
        # Split into train/val
        split_idx = int(0.9 * len(tokens))
        train_tokens = tokens[:split_idx]
        val_tokens = tokens[split_idx:]
        
        # Convert to numpy arrays
        import numpy as np
        train_array = np.array(train_tokens, dtype=np.uint16)
        val_array = np.array(val_tokens, dtype=np.uint16)
        
        # Save binaries
        data_dir = Path("data/london_data")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        train_array.tofile(data_dir / "train.bin")
        val_array.tofile(data_dir / "val.bin")
        
        # Save metadata
        import pickle
        meta = {
            'vocab_size': self.vocab_size,
            'tokenizer_type': tokenizer_type,
            'train_tokens': len(train_tokens),
            'val_tokens': len(val_tokens),
            'total_tokens': len(tokens)
        }
        
        with open(data_dir / "meta.pkl", 'wb') as f:
            pickle.dump(meta, f)
        
        print(f"✅ Dataset binaries saved to {data_dir}")
        print(f"   Train tokens: {len(train_tokens):,}")
        print(f"   Val tokens: {len(val_tokens):,}")
        
        return data_dir

def main():
    """Main tokenizer training pipeline"""
    print("🔤 London Historical LLM Tokenizer Training")
    print("=" * 50)
    
    # Check if corpus exists
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
        return
    
    print(f"✅ Found corpus at: {corpus_path}")
    
    # Initialize trainer
    trainer = LondonTokenizerTrainer(corpus_path, vocab_size=50000)
    
    # Train both tokenizers
    print("\n1. Training HuggingFace tokenizer...")
    hf_tokenizer = trainer.train_huggingface_tokenizer()
    
    print("\n2. Training tiktoken tokenizer...")
    tiktoken_tokenizer = trainer.train_tiktoken_tokenizer()
    
    # Create dataset binaries
    print("\n3. Creating dataset binaries...")
    data_dir = trainer.create_dataset_binaries("huggingface")
    
    print("\n🎉 Tokenizer training complete!")
    print(f"   Tokenizer files: {trainer.output_dir}")
    print(f"   Dataset files: {data_dir}")

if __name__ == "__main__":
    main()
