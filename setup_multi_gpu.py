"""
Multi-GPU setup script for London Historical LLM
Optimized for 2+ NVIDIA GPUs
"""

import os
import sys
import subprocess
import torch
from pathlib import Path

def check_gpu_setup():
    """Check GPU setup and capabilities"""
    print("🖥️  Checking GPU Setup")
    print("=" * 30)
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available. Please install CUDA and PyTorch with CUDA support.")
        return False
    
    gpu_count = torch.cuda.device_count()
    print(f"✅ Found {gpu_count} GPU(s)")
    
    for i in range(gpu_count):
        gpu_name = torch.cuda.get_device_name(i)
        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
        print(f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
    
    if gpu_count < 2:
        print("⚠️  Only 1 GPU found. Multi-GPU training will use single GPU.")
    else:
        print(f"✅ Multi-GPU training ready with {gpu_count} GPUs")
    
    return True

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n🔍 Checking Dependencies")
    print("=" * 30)
    
    required_packages = [
        'torch', 'transformers', 'tokenizers', 'tiktoken', 
        'numpy', 'tqdm', 'requests', 'beautifulsoup4'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        result = subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
        if result.returncode != 0:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories")
    print("=" * 30)
    
    directories = [
        "london_data",
        "data/london_data", 
        "tokenizer_london",
        "out_london_historical",
        "logs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path}")

def download_data():
    """Download historical data"""
    print("\n📚 Downloading historical data")
    print("=" * 35)
    
    if not os.path.exists("london_data/london_corpus_merged.txt"):
        print("Downloading historical texts...")
        result = subprocess.run([sys.executable, "data_preparation.py"])
        if result.returncode != 0:
            print("❌ Data download failed")
            return False
        print("✅ Data download completed")
    else:
        print("✅ Data already downloaded")

def train_tokenizer():
    """Train the tokenizer"""
    print("\n🔤 Training tokenizer")
    print("=" * 25)
    
    if not os.path.exists("tokenizer_london/vocab.json"):
        print("Training custom tokenizer...")
        result = subprocess.run([sys.executable, "train_tokenizer_london.py"])
        if result.returncode != 0:
            print("❌ Tokenizer training failed")
            return False
        print("✅ Tokenizer training completed")
    else:
        print("✅ Tokenizer already trained")

def create_training_script():
    """Create optimized training script for multi-GPU"""
    print("\n⚙️  Creating multi-GPU training script")
    print("=" * 40)
    
    # The multi-GPU training script is already created
    if os.path.exists("train_london_llm_multi_gpu.py"):
        print("✅ Multi-GPU training script ready")
    else:
        print("❌ Multi-GPU training script not found")

def create_launch_scripts():
    """Create launch scripts for multi-GPU training"""
    print("\n🚀 Creating launch scripts")
    print("=" * 30)
    
    # Create launch script for 2 GPUs
    launch_script = """#!/bin/bash
# Launch script for 2-GPU training

echo "🏛️  Starting London Historical LLM training on 2 GPUs"
echo "=================================================="

# Set environment variables
export CUDA_VISIBLE_DEVICES=0,1
export NCCL_DEBUG=INFO

# Launch training
torchrun --standalone --nproc_per_node=2 train_london_llm_multi_gpu.py

echo "✅ Training completed!"
"""
    
    with open("launch_2gpu.sh", "w") as f:
        f.write(launch_script)
    
    # Make executable
    os.chmod("launch_2gpu.sh", 0o755)
    
    # Create Windows batch file
    windows_script = """@echo off
echo 🏛️  Starting London Historical LLM training on 2 GPUs
echo ==================================================

set CUDA_VISIBLE_DEVICES=0,1
set NCCL_DEBUG=INFO

torchrun --standalone --nproc_per_node=2 train_london_llm_multi_gpu.py

echo ✅ Training completed!
pause
"""
    
    with open("launch_2gpu.bat", "w") as f:
        f.write(windows_script)
    
    print("✅ Launch scripts created:")
    print("   - launch_2gpu.sh (Linux/Mac)")
    print("   - launch_2gpu.bat (Windows)")

def show_training_commands():
    """Show training commands for different setups"""
    print("\n🎯 Training Commands")
    print("=" * 25)
    
    print("Single GPU:")
    print("   python train_london_llm.py")
    print()
    
    print("2 GPUs (Linux/Mac):")
    print("   ./launch_2gpu.sh")
    print("   # or")
    print("   torchrun --standalone --nproc_per_node=2 train_london_llm_multi_gpu.py")
    print()
    
    print("2 GPUs (Windows):")
    print("   launch_2gpu.bat")
    print("   # or")
    print("   torchrun --standalone --nproc_per_node=2 train_london_llm_multi_gpu.py")
    print()
    
    print("Custom GPU count:")
    print("   torchrun --standalone --nproc_per_node=N train_london_llm_multi_gpu.py")
    print()

def show_monitoring_tips():
    """Show monitoring and optimization tips"""
    print("\n📊 Monitoring & Optimization Tips")
    print("=" * 35)
    
    print("GPU Monitoring:")
    print("   nvidia-smi -l 1  # Monitor GPU usage")
    print("   watch -n 1 nvidia-smi  # Continuous monitoring")
    print()
    
    print("Training Monitoring:")
    print("   - Check logs in out_london_historical/")
    print("   - Monitor loss curves")
    print("   - Watch for convergence")
    print()
    
    print("Performance Tips:")
    print("   - Use bfloat16 if supported")
    print("   - Enable torch.compile()")
    print("   - Monitor memory usage")
    print("   - Adjust batch size if needed")
    print()

def main():
    """Main setup function"""
    print("🏛️  London Historical LLM - Multi-GPU Setup")
    print("=" * 50)
    
    # Check GPU setup
    if not check_gpu_setup():
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Setup directories
    setup_directories()
    
    # Download data
    if not download_data():
        return
    
    # Train tokenizer
    if not train_tokenizer():
        return
    
    # Create training script
    create_training_script()
    
    # Create launch scripts
    create_launch_scripts()
    
    # Show commands
    show_training_commands()
    
    # Show monitoring tips
    show_monitoring_tips()
    
    print("\n🎉 Multi-GPU setup completed!")
    print("\nNext steps:")
    print("1. Run: ./launch_2gpu.sh (Linux/Mac) or launch_2gpu.bat (Windows)")
    print("2. Monitor training progress")
    print("3. Check checkpoints in out_london_historical/")
    print("4. Generate text: python sample_london_llm.py")

if __name__ == "__main__":
    main()
