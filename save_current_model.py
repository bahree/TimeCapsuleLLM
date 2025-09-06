#!/usr/bin/env python3
"""
Save current model checkpoint with metadata for reference
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

def save_current_model():
    """Save current model checkpoint with metadata"""
    print("💾 Saving Current Model Checkpoint")
    print("=" * 40)
    
    # Create backup directory
    backup_dir = Path("model_backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_backup_dir = backup_dir / f"london_llm_108m_{timestamp}"
    model_backup_dir.mkdir(exist_ok=True)
    
    # Copy checkpoint
    if os.path.exists("out_london_historical/ckpt.pt"):
        shutil.copy("out_london_historical/ckpt.pt", model_backup_dir / "ckpt.pt")
        print(f"✅ Checkpoint saved to: {model_backup_dir / 'ckpt.pt'}")
    else:
        print("❌ Checkpoint not found!")
        return False
    
    # Save model metadata
    metadata = {
        "model_name": "London Historical LLM (108M parameters)",
        "timestamp": timestamp,
        "final_loss": 2.4705,
        "final_val_loss": 4.0321,
        "iterations": 20000,
        "model_size": "108M parameters",
        "vocabulary_size": 30000,
        "training_data": "Original London corpus (70MB)",
        "tokenizer": "Custom historical tokenizer",
        "description": "First successful training run with custom tokenizer"
    }
    
    with open(model_backup_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Metadata saved to: {model_backup_dir / 'metadata.json'}")
    
    # Print summary
    print(f"\n📊 Model Summary:")
    print(f"   Final loss: {metadata['final_loss']}")
    print(f"   Final val loss: {metadata['final_val_loss']}")
    print(f"   Iterations: {metadata['iterations']:,}")
    print(f"   Model size: {metadata['model_size']}")
    print(f"   Vocabulary: {metadata['vocabulary_size']:,} tokens")
    print(f"   Backup location: {model_backup_dir}")
    
    return True

if __name__ == "__main__":
    save_current_model()
