#!/usr/bin/env python3
"""
Resume training from checkpoint
"""

import os
import torch
import argparse

def resume_training(checkpoint_path="out_london_historical/ckpt.pt"):
    """Resume training from checkpoint"""
    
    if not os.path.exists(checkpoint_path):
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        return False
    
    print(f"📁 Loading checkpoint from: {checkpoint_path}")
    
    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    
    print("📊 Checkpoint info:")
    print(f"   Iteration: {checkpoint['iter_num']:,}")
    print(f"   Best val loss: {checkpoint['best_val_loss']:.4f}")
    print(f"   Model args: {checkpoint['model_args']}")
    
    if 'config' in checkpoint:
        print(f"   Config: {checkpoint['config']}")
    
    print("\n✅ Checkpoint loaded successfully!")
    print("   You can now resume training with: ./launch_2gpu.sh")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Resume training from checkpoint')
    parser.add_argument('--checkpoint', default='out_london_historical/ckpt.pt',
                       help='Path to checkpoint file')
    
    args = parser.parse_args()
    
    print("🔄 London Historical LLM - Resume Training")
    print("=" * 45)
    
    resume_training(args.checkpoint)

if __name__ == "__main__":
    main()
