#!/usr/bin/env python3
"""
Complete setup script for London Historical LLM with custom tokenizer
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    print("🏛️  London Historical LLM - Complete Setup with Custom Tokenizer")
    print("=" * 70)
    
    # Step 1: Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: You're not in a virtual environment!")
        print("   It's recommended to activate your virtual environment first:")
        print("   source london-llm-env/bin/activate")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("   Please activate your virtual environment and try again.")
            return
    
    # Step 2: Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        print("❌ Failed to install requirements. Please check your environment.")
        return
    
    # Step 3: Download and prepare data
    if not run_command("python data_preparation_fixed.py", "Downloading and preparing data"):
        print("❌ Failed to prepare data. Please check your internet connection.")
        return
    
    # Step 4: Train custom tokenizer
    if not run_command("python train_custom_tokenizer.py", "Training custom historical tokenizer"):
        print("❌ Failed to train custom tokenizer. Using fallback.")
    
    # Step 5: Prepare dataset
    if not run_command("python prepare_dataset.py", "Preparing dataset for training"):
        print("❌ Failed to prepare dataset.")
        return
    
    # Step 6: Check if old checkpoint exists
    if os.path.exists("out_london_historical/ckpt.pt"):
        print("\n⚠️  Old checkpoint found!")
        print("   The old checkpoint was trained with a different tokenizer.")
        print("   For best results, you should delete it and start fresh.")
        
        response = input("   Delete old checkpoint and start fresh? (Y/n): ")
        if response.lower() != 'n':
            run_command("rm -rf out_london_historical/", "Deleting old checkpoint")
            print("✅ Old checkpoint deleted. Ready for fresh training.")
        else:
            print("⚠️  Keeping old checkpoint. This may cause issues.")
    
    # Step 7: Show next steps
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("   1. Start training with: ./launch_2gpu.sh")
    print("   2. Monitor training progress")
    print("   3. Test generation with: python sample_london_llm_fixed.py")
    
    print("\n🔧 Available commands:")
    print("   • Train custom tokenizer: python train_custom_tokenizer.py")
    print("   • Prepare dataset: python prepare_dataset.py")
    print("   • Start training: ./launch_2gpu.sh")
    print("   • Test generation: python sample_london_llm_fixed.py --prompt 'Your prompt here'")
    
    print("\n📊 Tokenizer info:")
    if os.path.exists("tokenizer_historical/tokenizer.json"):
        print("   ✅ Custom historical tokenizer ready (30,000 tokens)")
    else:
        print("   ⚠️  Using character-level tokenizer (243 tokens)")
        print("   💡 Run 'python train_custom_tokenizer.py' for better results")

if __name__ == "__main__":
    main()
