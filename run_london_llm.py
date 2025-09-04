"""
Main entry point for London Historical LLM
Handles setup, training, and sampling in one script
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_setup():
    """Run the complete setup process"""
    print("🏛️  London Historical LLM - Complete Setup")
    print("=" * 50)
    
    # Test setup first
    print("1. Testing setup...")
    result = subprocess.run([sys.executable, "test_setup.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Setup test failed. Please fix the issues above.")
        return False
    
    # Run full setup
    print("\n2. Running complete setup...")
    result = subprocess.run([sys.executable, "setup_london_llm.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Setup failed.")
        print(result.stderr)
        return False
    
    print("✅ Setup completed successfully!")
    return True

def run_training(device="auto", max_iters=10000):
    """Run model training"""
    print("🧠 London Historical LLM - Training")
    print("=" * 50)
    
    # Check if data exists
    if not os.path.exists("data/london_data/train.bin"):
        print("❌ Training data not found. Please run setup first.")
        return False
    
    # Determine device
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
    
    print(f"Training on: {device}")
    print(f"Max iterations: {max_iters}")
    
    # Run training
    cmd = f"python train_london_llm.py --device {device} --max_iters {max_iters}"
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print("✅ Training completed successfully!")
        return True
    else:
        print("❌ Training failed.")
        return False

def run_sampling(prompt="In the year of our Lord 1834,", num_samples=3, max_tokens=500):
    """Run text generation"""
    print("📝 London Historical LLM - Text Generation")
    print("=" * 50)
    
    # Check if model exists
    if not os.path.exists("out_london_historical/ckpt.pt"):
        print("❌ Trained model not found. Please train the model first.")
        return False
    
    # Run sampling
    cmd = f"python sample_london_llm.py --prompt '{prompt}' --num_samples {num_samples} --max_tokens {max_tokens}"
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print("✅ Text generation completed!")
        return True
    else:
        print("❌ Text generation failed.")
        return False

def interactive_mode():
    """Interactive mode for easy usage"""
    print("🏛️  London Historical LLM - Interactive Mode")
    print("=" * 50)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Setup (download data, train tokenizer)")
        print("2. Train model")
        print("3. Generate text")
        print("4. Test setup")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            run_setup()
        elif choice == "2":
            device = input("Device (auto/cpu/cuda): ").strip() or "auto"
            max_iters = input("Max iterations (default 10000): ").strip()
            max_iters = int(max_iters) if max_iters.isdigit() else 10000
            run_training(device, max_iters)
        elif choice == "3":
            prompt = input("Enter prompt (default: 'In the year of our Lord 1834,'): ").strip()
            if not prompt:
                prompt = "In the year of our Lord 1834,"
            num_samples = input("Number of samples (default 3): ").strip()
            num_samples = int(num_samples) if num_samples.isdigit() else 3
            run_sampling(prompt, num_samples)
        elif choice == "4":
            subprocess.run([sys.executable, "test_setup.py"])
        elif choice == "5":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='London Historical LLM - Complete Pipeline')
    parser.add_argument('--setup', action='store_true', help='Run complete setup')
    parser.add_argument('--train', action='store_true', help='Train the model')
    parser.add_argument('--sample', action='store_true', help='Generate text samples')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--prompt', default="In the year of our Lord 1834,", help='Text generation prompt')
    parser.add_argument('--device', default='auto', help='Device for training (auto/cpu/cuda)')
    parser.add_argument('--max_iters', type=int, default=10000, help='Maximum training iterations')
    parser.add_argument('--num_samples', type=int, default=3, help='Number of text samples to generate')
    parser.add_argument('--max_tokens', type=int, default=500, help='Maximum tokens to generate')
    
    args = parser.parse_args()
    
    # If no arguments, run interactive mode
    if not any([args.setup, args.train, args.sample, args.interactive]):
        interactive_mode()
        return
    
    # Run specified operations
    if args.setup:
        if not run_setup():
            sys.exit(1)
    
    if args.train:
        if not run_training(args.device, args.max_iters):
            sys.exit(1)
    
    if args.sample:
        if not run_sampling(args.prompt, args.num_samples, args.max_tokens):
            sys.exit(1)
    
    if args.interactive:
        interactive_mode()

if __name__ == "__main__":
    main()
