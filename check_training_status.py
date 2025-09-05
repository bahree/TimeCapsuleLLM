#!/usr/bin/env python3
"""
Check training status and progress
"""

import os
import torch
import glob
from datetime import datetime

def check_training_status():
    """Check current training status"""
    
    print("📊 London Historical LLM - Training Status")
    print("=" * 45)
    
    # Check if training is running
    print("🔍 Checking if training is running...")
    try:
        import psutil
        training_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'train_london_llm_multi_gpu.py' in ' '.join(proc.info['cmdline']):
                    training_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if training_processes:
            print(f"✅ Training is running ({len(training_processes)} processes)")
            for proc in training_processes:
                print(f"   PID: {proc['pid']}")
        else:
            print("❌ Training is not running")
    except ImportError:
        print("⚠️  psutil not installed - cannot check running processes")
    
    # Check checkpoints
    print("\n📁 Checking checkpoints...")
    checkpoint_dir = "out_london_historical"
    if os.path.exists(checkpoint_dir):
        checkpoints = glob.glob(os.path.join(checkpoint_dir, "*.pt"))
        if checkpoints:
            print(f"✅ Found {len(checkpoints)} checkpoint(s)")
            for ckpt in sorted(checkpoints):
                try:
                    checkpoint = torch.load(ckpt, map_location='cpu')
                    iter_num = checkpoint.get('iter_num', 0)
                    best_val_loss = checkpoint.get('best_val_loss', 0)
                    print(f"   {os.path.basename(ckpt)}: iter {iter_num:,}, val_loss {best_val_loss:.4f}")
                except Exception as e:
                    print(f"   {os.path.basename(ckpt)}: Error loading - {e}")
        else:
            print("❌ No checkpoints found")
    else:
        print("❌ Checkpoint directory not found")
    
    # Check data files
    print("\n📊 Checking data files...")
    data_files = [
        "data/london_data/train.bin",
        "data/london_data/val.bin",
        "data/london_data/meta.pkl"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"✅ {file_path} ({size:.1f} MB)")
        else:
            print(f"❌ {file_path} not found")
    
    # Check GPU status
    print("\n🚀 Checking GPU status...")
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.used,memory.total,utilization.gpu', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) >= 5:
                    gpu_id, name, mem_used, mem_total, util = parts[0], parts[1], parts[2], parts[3], parts[4]
                    print(f"   GPU {gpu_id}: {name} - {mem_used}/{mem_total}MB ({util}% util)")
        else:
            print("❌ nvidia-smi not available")
    except Exception as e:
        print(f"❌ Error checking GPU status: {e}")
    
    print("\n🎯 Recommendations:")
    if not training_processes:
        print("   • Start training: ./launch_2gpu.sh")
        print("   • Check logs: tail -f nohup.out")
    else:
        print("   • Monitor progress: watch -n 1 nvidia-smi")
        print("   • Check logs: tail -f nohup.out")

if __name__ == "__main__":
    check_training_status()
