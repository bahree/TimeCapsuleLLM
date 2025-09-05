#!/usr/bin/env python3
"""
Test tokenizer quality with proper BPE understanding
"""

import os
from tokenizers import Tokenizer

def test_tokenizer_quality():
    """Test tokenizer with proper BPE understanding"""
    print("🔍 Tokenizer Quality Test (BPE-Aware)")
    print("=" * 45)
    
    # Load tokenizer
    tokenizer_path = "tokenizer_historical/tokenizer.json"
    if not os.path.exists(tokenizer_path):
        print("❌ Tokenizer not found!")
        return False
    
    tokenizer = Tokenizer.from_file(tokenizer_path)
    vocab_size = tokenizer.get_vocab_size()
    print(f"✅ Vocabulary size: {vocab_size:,} tokens")
    
    # Test samples
    test_cases = [
        {
            "text": "In the year of our Lord 1834, the streets of London were filled with the sounds of horse-drawn carriages.",
            "expected_tokens": 20,  # Should be around 20-25 tokens
            "description": "Historical narrative"
        },
        {
            "text": "The gentleman from the country said, 'I have never seen such a sight in all my days.'",
            "expected_tokens": 18,  # Should be around 18-22 tokens
            "description": "Dialogue"
        },
        {
            "text": "Mr. Darcy walked through the ballroom with his usual air of superiority.",
            "expected_tokens": 14,  # Should be around 14-16 tokens
            "description": "Character description"
        },
        {
            "text": "The Thames flowed dark and mysterious through the heart of the city.",
            "expected_tokens": 13,  # Should be around 13-15 tokens
            "description": "Descriptive prose"
        },
        {
            "text": "It was the best of times, it was the worst of times.",
            "expected_tokens": 14,  # Should be around 14-16 tokens
            "description": "Literary quote"
        }
    ]
    
    print("\n🧪 Testing tokenization quality...")
    
    total_chars = 0
    total_tokens = 0
    perfect_semantic = 0
    
    for i, case in enumerate(test_cases, 1):
        text = case["text"]
        expected = case["expected_tokens"]
        description = case["description"]
        
        # Encode
        tokens = tokenizer.encode(text)
        token_count = len(tokens.ids)
        
        # Decode
        decoded = tokenizer.decode(tokens.ids)
        
        # Count
        char_count = len(text)
        total_chars += char_count
        total_tokens += token_count
        
        # Check if token count is reasonable
        token_ratio = token_count / expected
        is_reasonable = 0.7 <= token_ratio <= 1.5
        
        # Check semantic preservation (case-insensitive, punctuation-normalized)
        original_normalized = text.lower().replace("'", "'").replace('"', '"')
        decoded_normalized = decoded.lower().replace("'", "'").replace('"', '"')
        
        # Remove extra spaces for comparison
        original_clean = " ".join(original_normalized.split())
        decoded_clean = " ".join(decoded_normalized.split())
        
        is_semantically_correct = original_clean == decoded_clean
        
        if is_semantically_correct:
            perfect_semantic += 1
        
        print(f"\n--- Test {i}: {description} ---")
        print(f"Original: {text}")
        print(f"Tokens: {token_count} (expected ~{expected})")
        print(f"Decoded: {decoded}")
        print(f"Token ratio: {token_ratio:.2f} {'✅' if is_reasonable else '⚠️'}")
        print(f"Semantic: {'✅ Perfect' if is_semantically_correct else '⚠️  Differs'}")
    
    # Calculate overall metrics
    compression_ratio = total_chars / total_tokens
    semantic_accuracy = perfect_semantic / len(test_cases) * 100
    
    print(f"\n📊 Overall Metrics:")
    print(f"   Compression ratio: {compression_ratio:.2f} chars/token")
    print(f"   Semantic accuracy: {semantic_accuracy:.1f}%")
    print(f"   Vocabulary size: {vocab_size:,}")
    
    # Assessment
    print(f"\n🎯 Assessment:")
    
    if compression_ratio > 2.5 and semantic_accuracy > 80 and vocab_size > 20000:
        print("✅ EXCELLENT - Ready for training!")
        print("   This tokenizer will produce high-quality results.")
        return True
    elif compression_ratio > 2.0 and semantic_accuracy > 70 and vocab_size > 10000:
        print("⚠️  GOOD - Ready for training")
        print("   This tokenizer should work well for training.")
        return True
    else:
        print("❌ POOR - Consider retraining")
        print("   This tokenizer may not produce good results.")
        return False

if __name__ == "__main__":
    success = test_tokenizer_quality()
    
    if success:
        print("\n🚀 Proceed with training: ./launch_2gpu.sh")
    else:
        print("\n🔄 Consider retraining: python train_custom_tokenizer.py")
