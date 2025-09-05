#!/usr/bin/env python3
"""
Test script to verify model generation works
"""

import os
import torch
import pickle

def test_model_vocabulary():
    """Test model vocabulary compatibility"""
    print("🔍 Testing Model Vocabulary Compatibility")
    print("=" * 45)
    
    # Check metadata
    meta_path = "data/london_data/meta.pkl"
    if not os.path.exists(meta_path):
        print("❌ Metadata not found")
        return False
    
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
    
    vocab_size = meta.get('vocab_size', 256)
    print(f"✅ Data vocabulary size: {vocab_size}")
    
    # Check checkpoint
    checkpoint_path = "out_london_historical/ckpt.pt"
    if not os.path.exists(checkpoint_path):
        print("❌ Checkpoint not found")
        return False
    
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model_args = checkpoint['model_args']
    model_vocab_size = model_args.get('vocab_size', 50304)
    
    print(f"✅ Model vocabulary size: {model_vocab_size}")
    
    if model_vocab_size != vocab_size:
        print(f"⚠️  Vocabulary mismatch: {model_vocab_size} vs {vocab_size}")
        print("   This will cause the 'index out of range' error")
        return False
    else:
        print("✅ Vocabulary sizes match!")
        return True

def test_simple_generation():
    """Test simple text generation"""
    print("\n🧪 Testing Simple Text Generation")
    print("=" * 40)
    
    try:
        # Use the fixed sample script
        import subprocess
        result = subprocess.run([
            'python', 'sample_london_llm_fixed.py', 
            '--prompt', 'The year was 1834',
            '--max_tokens', '100',
            '--num_samples', '1'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Text generation successful!")
            print("Generated text:")
            print(result.stdout)
            return True
        else:
            print("❌ Text generation failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error testing generation: {e}")
        return False

def main():
    print("🏛️  London Historical LLM - Model Test")
    print("=" * 45)
    
    # Test vocabulary compatibility
    vocab_ok = test_model_vocabulary()
    
    if vocab_ok:
        # Test generation
        gen_ok = test_simple_generation()
        
        if gen_ok:
            print("\n🎉 All tests passed! Model is working correctly.")
            print("\nYou can now generate text with:")
            print("  python sample_london_llm_fixed.py --prompt 'Your prompt here'")
        else:
            print("\n❌ Text generation failed. Check the error messages above.")
    else:
        print("\n❌ Vocabulary mismatch detected. Use the fixed sample script:")
        print("  python sample_london_llm_fixed.py --prompt 'Your prompt here'")

if __name__ == "__main__":
    main()
