#!/usr/bin/env python3
"""
Train a custom tokenizer optimized for historical English (1500-1850)
"""

import os
import json
from pathlib import Path
from tokenizers import Tokenizer, models, pre_tokenizers, trainers, processors
from tokenizers.normalizers import NFD, Lowercase, StripAccents, Sequence
import tqdm

class HistoricalTokenizerTrainer:
    def __init__(self, corpus_path, output_dir="tokenizer_historical", vocab_size=30000):
        self.corpus_path = Path(corpus_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.vocab_size = vocab_size
        
    def train_tokenizer(self):
        """Train a custom tokenizer for historical English"""
        print("🔤 Training custom historical tokenizer...")
        print(f"📚 Corpus: {self.corpus_path}")
        print(f"🎯 Target vocabulary: {self.vocab_size:,} tokens")
        
        # Initialize tokenizer
        tokenizer = Tokenizer(models.BPE())
        
        # Normalizers for historical text
        tokenizer.normalizer = Sequence([
            NFD(),           # Unicode normalization
            Lowercase(),     # Convert to lowercase
            StripAccents()   # Remove accents
        ])
        
        # Pre-tokenizer for historical English
        tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
        
        # Configure trainer with historical English focus
        trainer = trainers.BpeTrainer(
            vocab_size=self.vocab_size,
            special_tokens=[
                "<|endoftext|>",
                "<|startoftext|>", 
                "<|pad|>",
                "<|unk|>",
                "<|year|>",      # For years like 1834
                "<|date|>",      # For dates
                "<|name|>",      # For proper names
                "<|place|>",     # For places like London
                "<|title|>",     # For titles like Mr., Mrs.
                "<|chapter|>",   # For chapter markers
                "<|verse|>",     # For verse markers
                "<|quote|>",     # For quotations
                "<|speech|>",    # For dialogue
                "<|narrator|>",  # For narrative text
                "<|author|>",    # For author names
                "<|book|>",      # For book titles
                "<|newline|>",   # For line breaks
                "<|paragraph|>", # For paragraph breaks
            ],
            min_frequency=2,     # Minimum frequency for tokens
            show_progress=True,
            continuing_subword_prefix="##"  # For subword tokens
        )
        
        # Train on corpus
        print("🚀 Training tokenizer...")
        tokenizer.train([str(self.corpus_path)], trainer)
        
        # Add post-processor
        tokenizer.post_processor = processors.ByteLevel(trim_offsets=True)
        
        # Save tokenizer
        tokenizer.save(str(self.output_dir / "tokenizer.json"))
        
        # Save vocab and merges separately
        vocab = tokenizer.get_vocab()
        with open(self.output_dir / "vocab.json", 'w') as f:
            json.dump(vocab, f, indent=2)
        
        # Extract merges
        merges = []
        with open(self.output_dir / "merges.txt", 'w') as f:
            for line in merges:
                f.write(line + '\n')
        
        print(f"✅ Custom tokenizer saved to {self.output_dir}")
        print(f"📊 Vocabulary size: {len(vocab):,} tokens")
        
        return tokenizer
    
    def test_tokenizer(self, tokenizer):
        """Test the trained tokenizer"""
        print("\n🧪 Testing custom tokenizer...")
        
        test_texts = [
            "In the year of our Lord 1834, the streets of London were filled with the sounds of horse-drawn carriages.",
            "The gentleman from the country said, 'I have never seen such a sight in all my days.'",
            "Chapter I: The Beginning of the End",
            "Mr. Darcy walked through the ballroom with his usual air of superiority.",
            "The Thames flowed dark and mysterious through the heart of the city.",
            "It was the best of times, it was the worst of times.",
            "The year was 1812, and war had come to England once more.",
            "Lady Catherine de Bourgh was not pleased with the news.",
            "The old man sat by the fire, reading his Bible.",
            "The coach rattled down the cobblestone streets of London."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n--- Test {i} ---")
            print(f"Text: {text}")
            
            # Encode
            tokens = tokenizer.encode(text)
            print(f"Tokens: {tokens.ids[:20]}...")  # Show first 20 tokens
            print(f"Token count: {len(tokens.ids)}")
            
            # Decode
            decoded = tokenizer.decode(tokens.ids)
            print(f"Decoded: {decoded}")
            
            # Check if perfect reconstruction
            if text.lower() == decoded.lower():
                print("✅ Perfect reconstruction")
            else:
                print("⚠️  Reconstruction differs")

def main():
    print("🏛️  Historical English Tokenizer Training")
    print("=" * 50)
    
    # Check if corpus exists
    corpus_path = "data/london_data/london_corpus_merged.txt"
    if not os.path.exists(corpus_path):
        print(f"❌ Corpus not found: {corpus_path}")
        print("Please run data preparation first")
        return
    
    # Initialize trainer
    trainer = HistoricalTokenizerTrainer(corpus_path, vocab_size=30000)
    
    # Train tokenizer
    tokenizer = trainer.train_tokenizer()
    
    # Test tokenizer
    trainer.test_tokenizer(tokenizer)
    
    print("\n🎉 Custom tokenizer training complete!")
    print("You can now use this tokenizer for training and generation")

if __name__ == "__main__":
    main()
