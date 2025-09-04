"""
Sampling script for London Historical LLM
Generate text in the style of historical London (1500-1850)
"""

import os
import pickle
import torch
from contextlib import nullcontext
import argparse
from pathlib import Path

# Import model
from london_1800_1850_v0.model import GPTConfig, GPT

def load_tokenizer(tokenizer_dir="tokenizer_london"):
    """Load the trained tokenizer"""
    try:
        from tokenizers import Tokenizer
        tokenizer_path = os.path.join(tokenizer_dir, "tokenizer.json")
        if os.path.exists(tokenizer_path):
            tokenizer = Tokenizer.from_file(tokenizer_path)
            encode = lambda s: tokenizer.encode(s).ids
            decode = lambda ids: tokenizer.decode(ids)
            return encode, decode
    except ImportError:
        pass
    
    # Fallback to tiktoken
    try:
        import tiktoken
        # Try to load custom tokenizer
        vocab_path = os.path.join(tokenizer_dir, "vocab.json")
        merges_path = os.path.join(tokenizer_dir, "merges.txt")
        
        if os.path.exists(vocab_path) and os.path.exists(merges_path):
            # Load custom tokenizer
            with open(vocab_path, 'r') as f:
                vocab = json.load(f)
            
            # Create encoding
            tokenizer = tiktoken.Encoding(
                name="london_historical",
                pat_str=r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""",
                mergeable_ranks={},
                special_tokens={"<|endoftext|>": 0, "<|startoftext|>": 1, "<|pad|>": 2, "<|unk|>": 3}
            )
            
            # Load merges
            with open(merges_path, 'r') as f:
                merges = f.read().strip().split('\n')
            
            # Build mergeable ranks
            mergeable_ranks = {}
            for i, merge in enumerate(merges):
                if merge.strip():
                    mergeable_ranks[merge] = len(vocab) + i
            
            tokenizer = tiktoken.Encoding(
                name="london_historical",
                pat_str=r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""",
                mergeable_ranks=mergeable_ranks,
                special_tokens={"<|endoftext|>": 0, "<|startoftext|>": 1, "<|pad|>": 2, "<|unk|>": 3}
            )
        else:
            # Use GPT-2 tokenizer as fallback
            tokenizer = tiktoken.get_encoding("gpt2")
        
        encode = lambda s: tokenizer.encode(s)
        decode = lambda ids: tokenizer.decode(ids)
        return encode, decode
        
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        # Ultimate fallback - simple character-level
        encode = lambda s: [ord(c) for c in s]
        decode = lambda ids: ''.join([chr(i) for i in ids if i < 65536])
        return encode, decode

def load_model(checkpoint_path, device):
    """Load the trained model"""
    print(f"Loading model from {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model_args = checkpoint['model_args']
    
    # Create model
    gptconf = GPTConfig(**model_args)
    model = GPT(gptconf)
    
    # Load state dict
    state_dict = checkpoint['model']
    
    # Remove DDP prefix if present
    for k in list(state_dict.keys()):
        if k.startswith("_orig_mod."):
            state_dict[k[len("_orig_mod."):]] = state_dict.pop(k)
    
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
    parser = argparse.ArgumentParser(description='Sample from London Historical LLM')
    parser.add_argument('--checkpoint', default='out_london_historical/ckpt.pt', help='Model checkpoint path')
    parser.add_argument('--tokenizer_dir', default='tokenizer_london', help='Tokenizer directory')
    parser.add_argument('--device', default='cpu', help='Device to use (cpu/cuda)')
    parser.add_argument('--prompt', default='In the year of our Lord 1834,', help='Starting prompt')
    parser.add_argument('--max_tokens', type=int, default=500, help='Maximum tokens to generate')
    parser.add_argument('--temperature', type=float, default=0.8, help='Sampling temperature')
    parser.add_argument('--top_k', type=int, default=200, help='Top-k sampling')
    parser.add_argument('--num_samples', type=int, default=3, help='Number of samples to generate')
    parser.add_argument('--compile', action='store_true', help='Use torch.compile')
    
    args = parser.parse_args()
    
    print("🏛️  London Historical LLM Text Generation")
    print("=" * 50)
    
    # Check if checkpoint exists
    if not os.path.exists(args.checkpoint):
        print(f"❌ Checkpoint not found: {args.checkpoint}")
        print("Please train the model first using train_london_llm.py")
        return
    
    # Setup device
    device = torch.device(args.device)
    ctx = nullcontext() if device.type == "cpu" else torch.amp.autocast(device_type=device.type, dtype=torch.float32)
    
    # Load tokenizer
    print("Loading tokenizer...")
    encode, decode = load_tokenizer(args.tokenizer_dir)
    
    # Load model
    model = load_model(args.checkpoint, device)
    
    if args.compile:
        print("Compiling model...")
        model = torch.compile(model)
    
    # Generate samples
    print(f"\nGenerating {args.num_samples} samples...")
    print(f"Prompt: '{args.prompt}'")
    print("=" * 50)
    
    for i in range(args.num_samples):
        print(f"\n--- Sample {i+1} ---")
        generated = generate_text(
            model, encode, decode, 
            args.prompt, 
            args.max_tokens, 
            args.temperature, 
            args.top_k, 
            device
        )
        print(generated)
        print("-" * 50)

if __name__ == "__main__":
    main()
