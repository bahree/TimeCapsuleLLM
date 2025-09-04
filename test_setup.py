"""
Test script to verify London Historical LLM setup
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import torch
        print(f"  ✓ PyTorch {torch.__version__}")
    except ImportError as e:
        print(f"  ❌ PyTorch: {e}")
        return False
    
    try:
        import transformers
        print(f"  ✓ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"  ❌ Transformers: {e}")
        return False
    
    try:
        import tokenizers
        print(f"  ✓ Tokenizers {tokenizers.__version__}")
    except ImportError as e:
        print(f"  ❌ Tokenizers: {e}")
        return False
    
    try:
        import tiktoken
        print(f"  ✓ tiktoken {tiktoken.__version__}")
    except ImportError as e:
        print(f"  ❌ tiktoken: {e}")
        return False
    
    return True

def test_model_import():
    """Test if model can be imported"""
    print("\n🧠 Testing model import...")
    
    try:
        from london_1800_1850_v0.model import GPTConfig, GPT
        print("  ✓ Model classes imported successfully")
        
        # Test creating a small model
        config = GPTConfig(
            block_size=64,
            vocab_size=1000,
            n_layer=2,
            n_head=2,
            n_embd=64,
            dropout=0.0,
            bias=False
        )
        model = GPT(config)
        print(f"  ✓ Model created: {model.get_num_params():,} parameters")
        
        return True
    except Exception as e:
        print(f"  ❌ Model import failed: {e}")
        return False

def test_data_structure():
    """Test if data structure is correct"""
    print("\n📁 Testing data structure...")
    
    required_files = [
        "london_1800_1850_v0/model.py",
        "london_1800_1850_v0/train.py",
        "london_1800_1850_v0/sample.py",
        "london_1800_1850_v0/metadata_london.csv"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ❌ {file_path} not found")
            return False
    
    return True

def test_scripts():
    """Test if all scripts can be imported"""
    print("\n📜 Testing scripts...")
    
    scripts = [
        "data_preparation.py",
        "train_tokenizer_london.py", 
        "train_london_llm.py",
        "sample_london_llm.py",
        "setup_london_llm.py"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            print(f"  ✓ {script}")
        else:
            print(f"  ❌ {script} not found")
            return False
    
    return True

def test_gpu_availability():
    """Test GPU availability"""
    print("\n🖥️  Testing GPU availability...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✓ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"  ✓ CUDA version: {torch.version.cuda}")
        else:
            print("  ⚠️  CUDA not available - will use CPU")
        
        if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
            print("  ✓ bfloat16 supported")
        else:
            print("  ⚠️  bfloat16 not supported - will use float16")
        
        return True
    except Exception as e:
        print(f"  ❌ GPU test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 London Historical LLM Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package imports", test_imports),
        ("Model import", test_model_import),
        ("Data structure", test_data_structure),
        ("Scripts", test_scripts),
        ("GPU availability", test_gpu_availability)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is ready.")
        print("\nNext steps:")
        print("1. Run: python setup_london_llm.py")
        print("2. Then: python train_london_llm.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
