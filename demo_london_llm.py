"""
Demo script for London Historical LLM
Shows the capabilities and generates sample outputs
"""

import os
import sys
import subprocess
from pathlib import Path

def check_setup():
    """Check if everything is set up correctly"""
    print("🔍 Checking setup...")
    
    required_files = [
        "london_data/london_corpus_merged.txt",
        "data/london_data/train.bin",
        "data/london_data/val.bin",
        "data/london_data/meta.pkl",
        "tokenizer_london/vocab.json",
        "tokenizer_london/merges.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nPlease run setup first:")
        print("   python run_london_llm.py --setup")
        return False
    
    print("✅ Setup looks good!")
    return True

def demo_training():
    """Demo the training process"""
    print("\n🧠 Training Demo")
    print("=" * 30)
    
    if os.path.exists("out_london_historical/ckpt.pt"):
        print("✅ Model already trained!")
        return True
    
    print("Starting training...")
    print("This will take some time depending on your hardware.")
    print("You can monitor progress in the terminal.")
    
    # Run training with reduced iterations for demo
    cmd = "python train_london_llm.py --max_iters 1000"
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print("✅ Training completed!")
        return True
    else:
        print("❌ Training failed.")
        return False

def demo_generation():
    """Demo text generation"""
    print("\n📝 Text Generation Demo")
    print("=" * 30)
    
    if not os.path.exists("out_london_historical/ckpt.pt"):
        print("❌ No trained model found. Please train first.")
        return False
    
    # Sample prompts
    prompts = [
        "In the year of our Lord 1834,",
        "The streets of London were",
        "It was a dark and stormy night",
        "The gentleman from the country said",
        "In those days, the people of London"
    ]
    
    print("Generating text samples...")
    print("=" * 50)
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- Sample {i}: '{prompt}' ---")
        
        cmd = f"python sample_london_llm.py --prompt '{prompt}' --num_samples 1 --max_tokens 200"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract generated text from output
            lines = result.stdout.split('\n')
            in_sample = False
            for line in lines:
                if "--- Sample 1 ---" in line:
                    in_sample = True
                    continue
                elif in_sample and line.strip() and not line.startswith('-'):
                    print(line)
                elif in_sample and line.startswith('-'):
                    break
        else:
            print(f"❌ Generation failed: {result.stderr}")
    
    return True

def show_data_info():
    """Show information about the dataset"""
    print("\n📊 Dataset Information")
    print("=" * 30)
    
    # Check corpus size
    corpus_path = "london_data/london_corpus_merged.txt"
    if os.path.exists(corpus_path):
        with open(corpus_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Corpus size: {len(content):,} characters")
        print(f"Corpus size: {len(content.split()):,} words")
    
    # Check training data
    if os.path.exists("data/london_data/meta.pkl"):
        import pickle
        with open("data/london_data/meta.pkl", 'rb') as f:
            meta = pickle.load(f)
        print(f"Vocabulary size: {meta.get('vocab_size', 'Unknown')}")
        print(f"Training tokens: {meta.get('train_tokens', 'Unknown'):,}")
        print(f"Validation tokens: {meta.get('val_tokens', 'Unknown'):,}")
    
    # Check model info
    if os.path.exists("out_london_historical/ckpt.pt"):
        import torch
        checkpoint = torch.load("out_london_historical/ckpt.pt", map_location='cpu')
        model_args = checkpoint.get('model_args', {})
        print(f"Model parameters: {model_args.get('n_layer', 'Unknown')} layers")
        print(f"Model heads: {model_args.get('n_head', 'Unknown')}")
        print(f"Model embedding: {model_args.get('n_embd', 'Unknown')}")
        print(f"Context length: {model_args.get('block_size', 'Unknown')}")

def main():
    """Main demo function"""
    print("🏛️  London Historical LLM Demo")
    print("=" * 50)
    
    # Check setup
    if not check_setup():
        return
    
    # Show data info
    show_data_info()
    
    # Ask user what to demo
    print("\nWhat would you like to demo?")
    print("1. Training process")
    print("2. Text generation")
    print("3. Both")
    print("4. Just show info")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        demo_training()
    elif choice == "2":
        demo_generation()
    elif choice == "3":
        demo_training()
        demo_generation()
    elif choice == "4":
        print("✅ Demo complete!")
    else:
        print("Invalid choice. Running full demo...")
        demo_training()
        demo_generation()
    
    print("\n🎉 Demo completed!")
    print("\nFor more options, run:")
    print("   python run_london_llm.py --interactive")

if __name__ == "__main__":
    main()
