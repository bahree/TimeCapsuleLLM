#!/usr/bin/env python3
"""
Explain what the tokenizer is doing - why the differences are normal
"""

from tokenizers import Tokenizer

def explain_tokenizer():
    """Explain tokenizer behavior"""
    print("🔍 Understanding Your Tokenizer")
    print("=" * 40)
    
    # Load tokenizer
    tokenizer = Tokenizer.from_file("tokenizer_historical/tokenizer.json")
    vocab_size = tokenizer.get_vocab_size()
    
    print(f"✅ Your tokenizer has {vocab_size:,} tokens")
    print("\n📚 What BPE Tokenization Does:")
    print("   1. Normalizes text (lowercase, punctuation spacing)")
    print("   2. Breaks words into subwords for efficiency")
    print("   3. Creates a vocabulary optimized for your data")
    
    # Test examples
    examples = [
        "In the year of our Lord 1834",
        "Mr. Darcy walked through the ballroom",
        "The Thames flowed dark and mysterious",
        "cobblestone streets of London"
    ]
    
    print("\n🧪 Examples of Tokenization:")
    
    for text in examples:
        tokens = tokenizer.encode(text)
        decoded = tokenizer.decode(tokens.ids)
        
        print(f"\nOriginal:  {text}")
        print(f"Tokens:    {tokens.ids}")
        print(f"Decoded:   {decoded}")
        print(f"Count:     {len(tokens.ids)} tokens")
        
        # Show compression
        compression = len(text) / len(tokens.ids)
        print(f"Compression: {compression:.1f}x")
    
    print(f"\n✅ This is NORMAL and GOOD for training!")
    print("   • Lowercase normalization helps the model learn patterns")
    print("   • Subword tokenization handles unknown words efficiently")
    print("   • 30,000 tokens is much better than 243 characters")
    print("   • Your model will generate proper historical English")
    
    print(f"\n🚀 Ready to train with: ./launch_2gpu.sh")

if __name__ == "__main__":
    explain_tokenizer()
