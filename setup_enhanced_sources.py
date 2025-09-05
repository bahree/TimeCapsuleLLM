#!/usr/bin/env python3
"""
Setup script for enhanced London Historical LLM with additional data sources
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
    print("🏛️  London Historical LLM - Enhanced Setup with Additional Sources")
    print("=" * 70)
    print("📚 Enhanced data sources include:")
    print("   • Samuel Pepys' Diary (1660-1669) - Restoration London")
    print("   • The Gentleman's Magazine (1731-1850) - Periodical")
    print("   • Horace Walpole's Letters (1740s-1790s) - Elite social circles")
    print("   • The London Spy by Ned Ward (1698-1709) - Social commentary")
    print("   • Daniel Defoe's Tour (1724-1726) - Travelogue")
    print("   • Fanny Burney's Diaries (1770s-1840s) - Social observations")
    print("   • James Boswell's London Journal (1762-1763) - Social life")
    print("   • The Microcosm of London (1808-1810) - Illustrated social life")
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
    
    # Step 3: Update data preparation script
    if not run_command("python update_data_sources.py", "Updating data preparation script"):
        print("❌ Failed to update data preparation script.")
        return
    
    # Step 4: Download and prepare enhanced data
    if not run_command("python data_preparation_fixed.py", "Downloading and preparing enhanced data"):
        print("❌ Failed to prepare enhanced data. Please check your internet connection.")
        return
    
    # Step 5: Train custom tokenizer
    if not run_command("python train_custom_tokenizer.py", "Training custom historical tokenizer"):
        print("❌ Failed to train custom tokenizer. Using fallback.")
    
    # Step 6: Prepare dataset
    if not run_command("python prepare_dataset.py", "Preparing dataset for training"):
        print("❌ Failed to prepare dataset.")
        return
    
    # Step 7: Check if old checkpoint exists
    if os.path.exists("out_london_historical/ckpt.pt"):
        print("\n⚠️  Old checkpoint found!")
        print("   The old checkpoint was trained with the original dataset.")
        print("   For best results with enhanced data, you should delete it and start fresh.")
        
        response = input("   Delete old checkpoint and start fresh? (Y/n): ")
        if response.lower() != 'n':
            run_command("rm -rf out_london_historical/", "Deleting old checkpoint")
            print("✅ Old checkpoint deleted. Ready for fresh training with enhanced data.")
        else:
            print("⚠️  Keeping old checkpoint. This may cause issues with enhanced data.")
    
    # Step 8: Show next steps
    print("\n🎉 Enhanced setup complete!")
    print("\n📋 Next steps:")
    print("   1. Start training with: ./launch_2gpu.sh")
    print("   2. Monitor training progress")
    print("   3. Test generation with: python sample_fixed_v2.py")
    
    print("\n🔧 Available commands:")
    print("   • Train custom tokenizer: python train_custom_tokenizer.py")
    print("   • Prepare dataset: python prepare_dataset.py")
    print("   • Start training: ./launch_2gpu.sh")
    print("   • Test generation: python sample_fixed_v2.py --prompt 'Your prompt here'")
    
    print("\n📊 Enhanced data info:")
    if os.path.exists("data/london_data/london_corpus_enhanced.txt"):
        print("   ✅ Enhanced corpus ready with additional historical sources")
        print("   📄 File: data/london_data/london_corpus_enhanced.txt")
    else:
        print("   ⚠️  Enhanced corpus not found")
    
    if os.path.exists("tokenizer_historical/tokenizer.json"):
        print("   ✅ Custom historical tokenizer ready (30,000 tokens)")
    else:
        print("   ⚠️  Using character-level tokenizer (243 tokens)")
        print("   💡 Run 'python train_custom_tokenizer.py' for better results")

if __name__ == "__main__":
    main()
