#!/usr/bin/env python3
"""
Sample script for enhanced London Historical LLM (400M parameters)
"""

import os
import pickle
import torch
import argparse
from pathlib import Path

def load_custom_tokenizer():
    """Load the custom historical tokenizer"""
    tokenizer_path = "tokenizer_historical/tokenizer.json"
    
    if not os.path.exists(tokenizer_path):
        print("❌ Custom tokenizer not found!")
        print("   Please run: python train_custom_tokenizer.py")
        return None, None
    
    try:
        from tokenizers import Tokenizer
        tokenizer = Tokenizer.from_file(tokenizer_path)
        vocab_size = tokenizer.get_vocab_size()
        
        print(f"✅ Loaded custom tokenizer with {vocab_size:,} tokens")
        
        def encode(text):
            return tokenizer.encode(text)
        
        def decode(tokens):
            return tokenizer.decode(tokens)
        
        return encode, decode, vocab_size
        
    except Exception as e:
        print(f"❌ Error loading custom tokenizer: {e}")
        return None, None, None

def load_enhanced_model(checkpoint_path, device, vocab_size):
    """Load the enhanced model (400M parameters)"""
    print(f"Loading enhanced model from {checkpoint_path}")
    
    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    # Get model configuration
    model_args = checkpoint['model_args']
    model_args['vocab_size'] = vocab_size  # Override with correct vocab size
    
    # Import model
    from london_1800_1850_v0.model import GPTConfig, GPT
    config = GPTConfig(**model_args)
    model = GPT(config)
    
    # Load state dict
    state_dict = checkpoint['model']
    
    # Fix _orig_mod prefixes from PyTorch compilation
    if any(key.startswith('_orig_mod.') for key in state_dict.keys()):
        print("   Fixing _orig_mod prefixes...")
        new_state_dict = {}
        for key, value in state_dict.items():
            if key.startswith('_orig_mod.'):
                new_key = key[10:]  # Remove '_orig_mod.' prefix
                new_state_dict[new_key] = value
            else:
                new_state_dict[key] = value
        state_dict = new_state_dict
    
    # Handle vocabulary size mismatch
    if 'transformer.wte.weight' in state_dict:
        old_vocab_size = state_dict['transformer.wte.weight'].shape[0]
        if old_vocab_size != vocab_size:
            print(f"⚠️  Vocabulary size mismatch: {old_vocab_size} vs {vocab_size}")
            print("   Resizing model layers...")
            
            # Resize embedding layer
            old_emb = state_dict['transformer.wte.weight']
            new_emb = torch.randn(vocab_size, old_emb.shape[1], device=device) * 0.02
            new_emb[:old_vocab_size] = old_emb
            state_dict['transformer.wte.weight'] = new_emb
            
            # Resize output layer
            if 'lm_head.weight' in state_dict:
                old_head = state_dict['lm_head.weight']
                new_head = torch.randn(vocab_size, old_head.shape[1], device=device) * 0.02
                new_head[:old_vocab_size] = old_head
                state_dict['lm_head.weight'] = new_head
    
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    
    return model

def generate_text(model, encode, decode, prompt, max_new_tokens=100, temperature=0.8, top_k=200):
    """Generate text using the enhanced model"""
    device = next(model.parameters()).device
    
    # Encode prompt
    prompt_tokens = encode(prompt)
    x = torch.tensor(prompt_tokens.ids, dtype=torch.long, device=device).unsqueeze(0)
    
    print(f"Prompt tokens: {prompt_tokens.ids[:10]}...")
    print(f"Prompt decoded: '{decode(prompt_tokens.ids)}'")
    
    # Generate
    with torch.no_grad():
        for k in range(max_new_tokens):
            # Forward pass
            logits, _ = model(x)
            logits = logits[:, -1, :] / temperature
            
            # Apply top-k filtering
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')
            
            # Sample next token
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            
            # Append to sequence
            x = torch.cat((x, next_token), dim=1)
            
            # Stop if we hit a special token (optional)
            if next_token.item() == 0:  # Assuming 0 is a special token
                break
    
    # Decode the generated sequence
    generated_tokens = x[0].tolist()
    generated_text = decode(generated_tokens)
    
    return generated_text

def main():
    parser = argparse.ArgumentParser(description='Generate text from Enhanced London Historical LLM')
    parser.add_argument('--prompt', type=str, default='In the year of our Lord 1834', help='Text prompt')
    parser.add_argument('--max_new_tokens', type=int, default=100, help='Maximum new tokens to generate')
    parser.add_argument('--temperature', type=float, default=0.8, help='Sampling temperature')
    parser.add_argument('--top_k', type=int, default=200, help='Top-k sampling')
    
    args = parser.parse_args()
    
    print("🏛️  Enhanced London Historical LLM Text Generation")
    print("=" * 60)
    print("📊 Model: 400M parameters (Enhanced)")
    print("📚 Data: 1500-1850 London sources")
    print("🔤 Tokenizer: Custom historical (30,000 tokens)")
    print("=" * 60)
    
    # Check device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Load custom tokenizer
    print("Loading tokenizer...")
    encode, decode, vocab_size = load_custom_tokenizer()
    
    if encode is None:
        print("❌ Failed to load tokenizer")
        return
    
    # Load enhanced model
    checkpoint_path = "out_london_historical_enhanced/ckpt.pt"
    if not os.path.exists(checkpoint_path):
        print(f"❌ Enhanced model checkpoint not found: {checkpoint_path}")
        print("   Please run: ./launch_enhanced_training.sh")
        return
    
    model = load_enhanced_model(checkpoint_path, device, vocab_size)
    print(f"Enhanced model loaded: {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Generate text
    print(f"\nGenerating text...")
    print(f"Prompt: '{args.prompt}'")
    print("=" * 50)
    
    generated_text = generate_text(
        model, encode, decode, 
        args.prompt, 
        args.max_new_tokens, 
        args.temperature, 
        args.top_k
    )
    
    print(f"Generated text:")
    print(f"'{generated_text}'")
    print("=" * 50)
    
    print(f"\n🎉 Enhanced model generation complete!")
    print(f"💡 Try different prompts:")
    print(f"   python sample_enhanced_model.py --prompt 'The streets of London were filled with'")
    print(f"   python sample_enhanced_model.py --prompt 'Mr. Darcy walked through the ballroom'")
    print(f"   python sample_enhanced_model.py --prompt 'The Thames flowed dark and mysterious'")

if __name__ == "__main__":
    main()
