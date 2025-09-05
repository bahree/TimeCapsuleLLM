#!/usr/bin/env python3
"""
Quick tokenizer test - fast check before training
"""

import os
import time
from tokenizers import Tokenizer

def quick_test():
    """Quick test of tokenizer efficiency"""
    print("🔍 Quick Tokenizer Test")
    print("=" * 30)
    
    # Check if tokenizer exists
    tokenizer_path = "tokenizer_historical/tokenizer.json"
    if not os.path.exists(tokenizer_path):
        print("❌ Custom tokenizer not found!")
        print("   Run: python train_custom_tokenizer.py")
        return False
    
    # Load tokenizer
    print("🔤 Loading tokenizer...")
    tokenizer = Tokenizer.from_file(tokenizer_path)
    vocab_size = tokenizer.get_vocab_size()
    print(f"✅ Vocabulary size: {vocab_size:,} tokens")
    
    # Test samples
    test_texts = [
        "In the year of our Lord 1834, the streets of London were filled with the sounds of horse-drawn carriages.",
        "The gentleman from the country said, 'I have never seen such a sight in all my days.'",
        "Mr. Darcy walked through the ballroom with his usual air of superiority.",
        "The Thames flowed dark and mysterious through the heart of the city.",
        "It was the best of times, it was the worst of times."
    ]
    
    print("\n🧪 Testing samples...")
    
    total_chars = 0
    total_tokens = 0
    perfect_reconstructions = 0
    
    for i, text in enumerate(test_texts, 1):
        # Encode
        start_time = time.time()
        tokens = tokenizer.encode(text)
        encode_time = time.time() - start_time
        
        # Decode
        decoded = tokenizer.decode(tokens.ids)
        
        # Count
        char_count = len(text)
        token_count = len(tokens.ids)
        total_chars += char_count
        total_tokens += token_count
        
        # Check reconstruction (BPE-aware)
        # BPE normalizes text, so we need to compare normalized versions
        original_normalized = text.lower().replace("'", "'").replace('"', '"')
        decoded_normalized = decoded.lower().replace("'", "'").replace('"', '"')
        
        # Remove extra spaces for comparison
        original_clean = " ".join(original_normalized.split())
        decoded_clean = " ".join(decoded_normalized.split())
        
        is_perfect = original_clean == decoded_clean
        if is_perfect:
            perfect_reconstructions += 1
        
        print(f"   Sample {i}: {token_count} tokens, {encode_time*1000:.1f}ms, {'✅' if is_perfect else '⚠️'}")
    
    # Calculate metrics
    compression_ratio = total_chars / total_tokens if total_tokens > 0 else 0
    reconstruction_rate = perfect_reconstructions / len(test_texts) * 100
    
    print(f"\n📊 Results:")
    print(f"   Compression ratio: {compression_ratio:.2f} chars/token")
    print(f"   Reconstruction rate: {reconstruction_rate:.1f}%")
    print(f"   Vocabulary size: {vocab_size:,}")
    
    # Assessment (BPE-aware)
    print(f"\n🎯 BPE Tokenizer Assessment:")
    print(f"   Compression: {compression_ratio:.2f} chars/token (target: >2.0)")
    print(f"   Semantic accuracy: {reconstruction_rate:.1f}% (target: >70%)")
    print(f"   Vocabulary: {vocab_size:,} tokens (target: >10,000)")
    
    if compression_ratio > 2.0 and reconstruction_rate > 70 and vocab_size > 10000:
        print("\n✅ EXCELLENT - Ready for training!")
        print("   This tokenizer will produce high-quality results.")
        return True
    elif compression_ratio > 1.5 and reconstruction_rate > 50 and vocab_size > 5000:
        print("\n⚠️  GOOD - Ready for training")
        print("   This tokenizer should work well for training.")
        return True
    else:
        print("\n❌ POOR - Consider retraining")
        print("   This tokenizer may not produce good results.")
        return False

if __name__ == "__main__":
    success = quick_test()
    
    if success:
        print("\n🚀 Proceed with training: ./launch_2gpu.sh")
    else:
        print("\n🔄 Retrain tokenizer: python train_custom_tokenizer.py")
