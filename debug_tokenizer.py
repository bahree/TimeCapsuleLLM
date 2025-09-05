#!/usr/bin/env python3
"""
Debug tokenizer loading issues
"""

import os
from pathlib import Path

def debug_tokenizer():
    print("🔍 Debugging Tokenizer Loading")
    print("=" * 40)
    
    # Check if custom tokenizer exists
    custom_path = "tokenizer_historical/tokenizer.json"
    if os.path.exists(custom_path):
        print(f"✅ Custom tokenizer found: {custom_path}")
        
        # Check file size
        size = os.path.getsize(custom_path)
        print(f"   File size: {size:,} bytes")
        
        # Try to load it
        try:
            from tokenizers import Tokenizer
            tokenizer = Tokenizer.from_file(custom_path)
            vocab_size = tokenizer.get_vocab_size()
            print(f"   Vocabulary size: {vocab_size:,}")
            
            # Test encoding
            test_text = "In the year of our Lord 1834"
            tokens = tokenizer.encode(test_text)
            decoded = tokenizer.decode(tokens.ids)
            
            print(f"   Test: '{test_text}'")
            print(f"   Tokens: {tokens.ids[:10]}...")
            print(f"   Decoded: '{decoded}'")
            
        except Exception as e:
            print(f"   ❌ Error loading: {e}")
    else:
        print(f"❌ Custom tokenizer not found: {custom_path}")
    
    # Check what files exist
    print(f"\n📁 Files in tokenizer_historical/:")
    if os.path.exists("tokenizer_historical"):
        for file in os.listdir("tokenizer_historical"):
            print(f"   - {file}")
    else:
        print("   Directory doesn't exist")
    
    # Check data directory
    print(f"\n📁 Files in data/london_data/:")
    if os.path.exists("data/london_data"):
        for file in os.listdir("data/london_data"):
            print(f"   - {file}")
    else:
        print("   Directory doesn't exist")

if __name__ == "__main__":
    debug_tokenizer()
