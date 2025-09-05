"""
Fixed sampling script for London Historical LLM
Handles vocabulary mismatch between tokenizer and model
"""

import os
import pickle
import torch
import json
from contextlib import nullcontext
import argparse
from pathlib import Path

# Import model
from london_1800_1850_v0.model import GPTConfig, GPT

def load_tokenizer_simple():
    """Load simple character-level tokenizer that matches the model"""
    print("Using character-level tokenizer (matches model vocabulary)")
    
    # Load metadata to get vocabulary info
    meta_path = "data/london_data/meta.pkl"
    if os.path.exists(meta_path):
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
        vocab_size = meta.get('vocab_size', 256)
        stoi = meta.get('stoi', {})
        itos = meta.get('itos', {})
        
        print(f"Loaded vocabulary: {vocab_size} tokens")
        
        def encode(text):
            """Encode text to token IDs"""
            if stoi:
                # Use trained vocabulary
                return [stoi.get(c, stoi.get('<unk>', 0)) for c in text]
            else:
                # Fallback to character codes
                return [ord(c) % vocab_size for c in text]
        
        def decode(ids):
            """Decode token IDs to text"""
            if itos:
                # Use trained vocabulary
                return ''.join([itos.get(i, '') for i in ids if i in itos])
            else:
                # Fallback to character codes
                return ''.join([chr(i) for i in ids if i < 256])
        
        return encode, decode, vocab_size
    else:
        print("No metadata found, using simple character encoding")
        
        def encode(text):
            return [ord(c) % 256 for c in text]
        
        def decode(ids):
            return ''.join([chr(i) for i in ids if i < 256])
        
        return encode, decode, 256

def load_model(checkpoint_path, device, vocab_size):
    """Load the trained model with correct vocabulary size"""
    print(f"Loading model from {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model_args = checkpoint['model_args']
    
    # Override vocab_size to match tokenizer
    model_args['vocab_size'] = vocab_size
    print(f"Using vocab_size: {vocab_size}")
    
    # Create model
    gptconf = GPTConfig(**model_args)
    model = GPT(gptconf)
    
    # Load state dict
    state_dict = checkpoint['model']
    
    # Remove DDP prefix if present
    for k in list(state_dict.keys()):
        if k.startswith("_orig_mod."):
            state_dict[k[len("_orig_mod."):]] = state_dict.pop(k)
    
    # Handle vocabulary size mismatch
    if 'transformer.wte.weight' in state_dict:
        old_vocab_size = state_dict['transformer.wte.weight'].shape[0]
        if old_vocab_size != vocab_size:
            print(f"Adjusting vocabulary size: {old_vocab_size} -> {vocab_size}")
            
            # Resize embedding layer
            old_emb = state_dict['transformer.wte.weight']
            new_emb = torch.zeros(vocab_size, old_emb.shape[1])
            new_emb[:min(old_vocab_size, vocab_size)] = old_emb[:min(old_vocab_size, vocab_size)]
            state_dict['transformer.wte.weight'] = new_emb
            
            # Resize output layer
            if 'lm_head.weight' in state_dict:
                old_head = state_dict['lm_head.weight']
                new_head = torch.zeros(vocab_size, old_head.shape[1])
                new_head[:min(old_vocab_size, vocab_size)] = old_head[:min(old_vocab_size, vocab_size)]
                state_dict['lm_head.weight'] = new_head
    
    model.load_state_dict(state_dict)
    model.eval()
    model.to(device)
    
    print(f"Model loaded: {model.get_num_params():,} parameters")
    return model

def generate_text(model, encode, decode, prompt, max_new_tokens=500, temperature=0.8, top_k=200, device='cpu'):
    """Generate text from the model"""
    # Encode prompt
    if prompt.startswith("FILE:"):
        with open(prompt[5:], 'r', encoding='utf-8') as f:
            prompt = f.read()
    
    ids = encode(prompt)
    x = torch.tensor([ids], dtype=torch.long, device=device)
    
    # Generate
    with torch.no_grad():
        y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
        generated_text = decode(y[0].tolist())
    
    return generated_text

def main():
    parser = argparse.ArgumentParser(description='Sample from London Historical LLM (Fixed)')
    parser.add_argument('--checkpoint', default='out_london_historical/ckpt.pt', help='Model checkpoint path')
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu', help='Device to use (cpu/cuda)')
    parser.add_argument('--prompt', default='In the year of our Lord 1834,', help='Starting prompt')
    parser.add_argument('--max_tokens', type=int, default=500, help='Maximum tokens to generate')
    parser.add_argument('--temperature', type=float, default=0.8, help='Sampling temperature')
    parser.add_argument('--top_k', type=int, default=200, help='Top-k sampling')
    parser.add_argument('--num_samples', type=int, default=3, help='Number of samples to generate')
    
    args = parser.parse_args()
    
    print("🏛️  London Historical LLM Text Generation (Fixed)")
    print("=" * 55)
    
    # Check if checkpoint exists
    if not os.path.exists(args.checkpoint):
        print(f"❌ Checkpoint not found: {args.checkpoint}")
        print("Please train the model first using train_london_llm_multi_gpu.py")
        return
    
    # Setup device
    device = torch.device(args.device)
    print(f"Using device: {device}")
    
    # Load tokenizer
    print("Loading tokenizer...")
    encode, decode, vocab_size = load_tokenizer_simple()
    
    # Load model
    model = load_model(args.checkpoint, device, vocab_size)
    
    # Generate samples
    print(f"\nGenerating {args.num_samples} samples...")
    print(f"Prompt: '{args.prompt}'")
    print("=" * 50)
    
    for i in range(args.num_samples):
        print(f"\n--- Sample {i+1} ---")
        try:
            generated = generate_text(
                model, encode, decode, 
                args.prompt, 
                args.max_tokens, 
                args.temperature, 
                args.top_k, 
                device
            )
            print(generated)
        except Exception as e:
            print(f"Error generating sample {i+1}: {e}")
        print("-" * 50)

if __name__ == "__main__":
    main()
