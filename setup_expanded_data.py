"""
Setup script for expanded London Historical LLM dataset
Allows switching between original and expanded datasets
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def setup_original_dataset():
    """Setup the original dataset (200+ texts)"""
    print("📚 Setting up original dataset (200+ texts)")
    print("=" * 50)
    
    # Use original data preparation
    if not run_command("python data_preparation.py", "Downloading original dataset"):
        return False
    
    # Train tokenizer
    if not run_command("python train_tokenizer_london.py", "Training tokenizer"):
        return False
    
    print("✅ Original dataset setup complete!")
    return True

def setup_expanded_dataset():
    """Setup the expanded dataset (1000+ texts)"""
    print("📚 Setting up expanded dataset (1000+ texts)")
    print("=" * 50)
    
    # Use expanded data preparation
    if not run_command("python data_preparation_expanded.py", "Downloading expanded dataset"):
        return False
    
    # Train tokenizer on expanded data
    if not run_command("python train_tokenizer_london.py", "Training tokenizer on expanded data"):
        return False
    
    print("✅ Expanded dataset setup complete!")
    return True

def show_dataset_comparison():
    """Show comparison between datasets"""
    print("\n📊 Dataset Comparison")
    print("=" * 30)
    
    print("Original Dataset:")
    print("  - Texts: ~200 works")
    print("  - Size: ~500MB-1GB")
    print("  - Time Period: 1800-1850")
    print("  - Focus: Literature only")
    print("  - Setup Time: 10-30 minutes")
    print()
    
    print("Expanded Dataset:")
    print("  - Texts: ~1000+ works")
    print("  - Size: ~5-10GB")
    print("  - Time Period: 1500-1850")
    print("  - Focus: All genres")
    print("  - Setup Time: 1-3 hours")
    print()
    
    print("Categories in Expanded Dataset:")
    print("  - Literature (poetry, fiction, drama)")
    print("  - Political & Philosophy")
    print("  - Legal & Government")
    print("  - Scientific & Medical")
    print("  - Religious & Theological")
    print("  - Historical & Travel")
    print("  - Newspapers & Periodicals")

def create_dataset_switch_script():
    """Create a script to easily switch between datasets"""
    switch_script = """#!/bin/bash
# Dataset switching script for London Historical LLM

echo "🏛️  London Historical LLM - Dataset Switcher"
echo "============================================="

echo "Available datasets:"
echo "1. Original (200+ texts, 1800-1850, Literature only)"
echo "2. Expanded (1000+ texts, 1500-1850, All genres)"
echo "3. Show comparison"
echo "4. Exit"

read -p "Choose dataset (1-4): " choice

case $choice in
    1)
        echo "Setting up original dataset..."
        python setup_expanded_data.py --dataset original
        ;;
    2)
        echo "Setting up expanded dataset..."
        python setup_expanded_data.py --dataset expanded
        ;;
    3)
        python setup_expanded_data.py --compare
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run again."
        exit 1
        ;;
esac
"""
    
    with open("switch_dataset.sh", "w") as f:
        f.write(switch_script)
    
    # Make executable
    os.chmod("switch_dataset.sh", 0o755)
    
    print("✅ Dataset switching script created: switch_dataset.sh")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description='Setup London Historical LLM datasets')
    parser.add_argument('--dataset', choices=['original', 'expanded'], 
                       help='Dataset to setup (original or expanded)')
    parser.add_argument('--compare', action='store_true', 
                       help='Show dataset comparison')
    parser.add_argument('--interactive', action='store_true', 
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.compare:
        show_dataset_comparison()
        return
    
    if args.interactive or not args.dataset:
        print("🏛️  London Historical LLM - Dataset Setup")
        print("=" * 50)
        
        print("Choose your dataset:")
        print("1. Original (200+ texts, 1800-1850, Literature only)")
        print("2. Expanded (1000+ texts, 1500-1850, All genres)")
        print("3. Show comparison")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            setup_original_dataset()
        elif choice == "2":
            setup_expanded_dataset()
        elif choice == "3":
            show_dataset_comparison()
        else:
            print("Invalid choice. Please run again.")
            return
    else:
        if args.dataset == "original":
            setup_original_dataset()
        elif args.dataset == "expanded":
            setup_expanded_dataset()
    
    # Create switching script
    create_dataset_switch_script()
    
    print("\n🎉 Dataset setup complete!")
    print("\nNext steps:")
    print("1. Run: python train_london_llm.py")
    print("2. Or: python train_london_llm_multi_gpu.py")
    print("3. Generate text: python sample_london_llm.py")

if __name__ == "__main__":
    main()
