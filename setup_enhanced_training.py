#!/usr/bin/env python3
"""
Setup script for enhanced London Historical LLM training
- Bigger model (400M parameters)
- Enhanced data sources (1500-1850)
- Custom historical tokenizer
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
    print("🏛️  London Historical LLM - Enhanced Training Setup")
    print("=" * 60)
    print("📊 Enhanced Model Configuration:")
    print("   • Parameters: 400M (vs 108M)")
    print("   • Layers: 20 (vs 12)")
    print("   • Heads: 16 (vs 12)")
    print("   • Hidden size: 1280 (vs 768)")
    print("   • Vocabulary: 30,000 tokens")
    print("   • Enhanced data: 1500-1850 period")
    print("=" * 60)
    
    # Step 1: Save current model
    print("\n💾 Step 1: Saving current model checkpoint...")
    if not run_command("python save_current_model.py", "Saving current model"):
        print("⚠️  Failed to save current model, continuing...")
    
    # Step 2: Check if enhanced data exists
    print("\n📚 Step 2: Checking enhanced data...")
    if not os.path.exists("data/london_enhanced/train.bin"):
        print("📥 Enhanced data not found, downloading...")
        if not run_command("python data_preparation_fixed.py", "Downloading enhanced data"):
            print("❌ Failed to download enhanced data")
            return
    else:
        print("✅ Enhanced data found")
    
    # Step 3: Check if custom tokenizer exists
    print("\n🔤 Step 3: Checking custom tokenizer...")
    if not os.path.exists("tokenizer_historical/tokenizer.json"):
        print("🔤 Custom tokenizer not found, training...")
        if not run_command("python train_custom_tokenizer.py", "Training custom tokenizer"):
            print("❌ Failed to train custom tokenizer")
            return
    else:
        print("✅ Custom tokenizer found")
    
    # Step 4: Prepare enhanced dataset
    print("\n📦 Step 4: Preparing enhanced dataset...")
    if not run_command("python prepare_dataset.py", "Preparing enhanced dataset"):
        print("❌ Failed to prepare dataset")
        return
    
    # Step 5: Create output directory
    print("\n📁 Step 5: Creating output directory...")
    os.makedirs("out_london_historical_enhanced", exist_ok=True)
    print("✅ Output directory created")
    
    # Step 6: Show next steps
    print("\n🎉 Enhanced setup complete!")
    print("\n📋 Next steps:")
    print("   1. Start enhanced training: ./launch_enhanced_training.sh")
    print("   2. Monitor training progress")
    print("   3. Test generation with: python sample_fixed_v2.py")
    
    print("\n🔧 Available commands:")
    print("   • Start training: ./launch_enhanced_training.sh")
    print("   • Test generation: python sample_fixed_v2.py --prompt 'Your prompt here'")
    print("   • Monitor training: watch -n 1 nvidia-smi")
    
    print("\n📊 Enhanced model info:")
    print("   • Model size: 400M parameters")
    print("   • Training data: Enhanced 1500-1850 sources")
    print("   • Tokenizer: Custom historical (30,000 tokens)")
    print("   • Expected training time: 8-12 hours")
    print("   • Expected improvement: 30-50% better text quality")
    
    print("\n💡 Tips:")
    print("   • Training will take longer due to bigger model")
    print("   • Monitor GPU memory usage")
    print("   • Checkpoints saved every 200 iterations")
    print("   • Can resume from checkpoint if interrupted")

if __name__ == "__main__":
    main()
