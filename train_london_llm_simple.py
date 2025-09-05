"""
Simple training script for London Historical LLM
Single GPU or CPU training
"""

import torch
import torch.nn as nn
from torch.nn import functional as F
import os
import pickle
import numpy as np
from tqdm import tqdm

# Check if we have the model file
if not os.path.exists('london_1800_1850_v0/model.py'):
    print("❌ Model file not found. Please ensure london_1800_1850_v0/model.py exists")
    exit(1)

# Import the model
import sys
sys.path.append('london_1800_1850_v0')
from model import GPT

def load_data():
    """Load training data"""
    print("📖 Loading training data...")
    
    # Try multiple data locations
    data_paths = [
        "data/london_data/train.bin",
        "london_data/train.bin",
        "train.bin"
    ]
    
    train_path = None
    for path in data_paths:
        if os.path.exists(path):
            train_path = path
            break
    
    if not train_path:
        print("❌ Training data not found. Please run prepare_dataset.py first")
        return None, None, None
    
    # Load data
    train_data = np.fromfile(train_path, dtype=np.uint16)
    
    # Load metadata
    meta_path = train_path.replace('train.bin', 'meta.pkl')
    if os.path.exists(meta_path):
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
        vocab_size = meta['vocab_size']
    else:
        vocab_size = 256  # Default fallback
    
    print(f"✅ Loaded {len(train_data):,} training tokens")
    print(f"📊 Vocabulary size: {vocab_size}")
    
    return train_data, vocab_size, meta

def train_model():
    """Train the model"""
    print("🏛️  London Historical LLM - Simple Training")
    print("=" * 50)
    
    # Load data
    train_data, vocab_size, meta = load_data()
    if train_data is None:
        return
    
    # Model configuration
    config = {
        'block_size': 1024,
        'vocab_size': vocab_size,
        'n_layer': 8,
        'n_head': 8,
        'n_embd': 512,
        'dropout': 0.1,
        'bias': False
    }
    
    print(f"🔧 Model config: {config}")
    
    # Create model
    model = GPT(config)
    model = model.to('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    
    # Training parameters
    batch_size = 4
    max_iters = 1000
    eval_interval = 100
    
    print(f"🚀 Starting training...")
    print(f"   Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print(f"   Batch size: {batch_size}")
    print(f"   Max iterations: {max_iters}")
    
    # Training loop
    model.train()
    for iter_num in tqdm(range(max_iters), desc="Training"):
        # Sample batch
        ix = torch.randint(len(train_data) - config['block_size'], (batch_size,))
        x = torch.stack([torch.from_numpy(train_data[i:i+config['block_size']].astype(np.int64)) for i in ix])
        y = torch.stack([torch.from_numpy(train_data[i+1:i+1+config['block_size']].astype(np.int64)) for i in ix])
        
        x, y = x.to(model.device), y.to(model.device)
        
        # Forward pass
        logits, loss = model(x, y)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Log progress
        if iter_num % eval_interval == 0:
            print(f"Iter {iter_num}: loss = {loss.item():.4f}")
    
    # Save model
    model_path = "london_llm_model.pt"
    torch.save(model.state_dict(), model_path)
    print(f"✅ Model saved to {model_path}")
    
    # Generate sample text
    print("\n📝 Generating sample text...")
    model.eval()
    with torch.no_grad():
        context = torch.zeros((1, 1), dtype=torch.long, device=model.device)
        generated = model.generate(context, max_new_tokens=200, temperature=0.8, top_k=40)
        
        # Convert to text (simplified)
        print("Generated text:")
        print("=" * 50)
        print(generated[0].tolist()[:100])  # Show first 100 tokens
        print("=" * 50)

if __name__ == "__main__":
    train_model()
