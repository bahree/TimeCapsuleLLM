#!/usr/bin/env python3
"""
Custom Tokenizer Training for London Historical LLM
Trains a BPE tokenizer optimized for historical English text
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers, processors
    from tokenizers.normalizers import NFD, Lowercase, StripAccents
    from transformers import PreTrainedTokenizerFast
    import torch
    from datasets import Dataset
    import pandas as pd
    from tqdm import tqdm
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tokenizer_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LondonTokenizerTrainer:
    def __init__(self, 
                 data_dir: str = "data/london_historical",
                 output_dir: str = "09_models/tokenizers",
                 vocab_size: int = 50000,  # Increased from 32k to 50k
                 min_frequency: int = 2,
                 special_tokens: List[str] = None):
        
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.vocab_size = vocab_size
        self.min_frequency = min_frequency
        
        # Enhanced special tokens for historical text
        self.special_tokens = special_tokens or [
            # Basic tokens
            "<|endoftext|>", "<|startoftext|>", "<|pad|>", "<|unk|>", "<|mask|>",
            "<|sep|>", "<|cls|>", "<|eos|>", "<|bos|>",
            
            # Punctuation tokens
            "<|period|>", "<|comma|>", "<|question|>", "<|exclamation|>",
            "<|colon|>", "<|semicolon|>", "<|quotation|>", "<|apostrophe|>",
            "<|hyphen|>", "<|parenthesis|>", "<|bracket|>",
            
            # Historical language tokens
            "<|thou|>", "<|thee|>", "<|thy|>", "<|thine|>", "<|hast|>", "<|hath|>",
            "<|doth|>", "<|dost|>", "<|art|>", "<|wilt|>", "<|shalt|>", "<|canst|>",
            "<|verily|>", "<|indeed|>", "<|forsooth|>", "<|methinks|>", "<|perchance|>",
            "<|anon|>", "<|ere|>", "<|whilst|>", "<|betwixt|>", "<|amongst|>",
            "<|prithee|>", "<|pray|>", "<|beseech|>",
            
            # London-specific tokens
            "<|london|>", "<|thames|>", "<|westminster|>", "<|city|>", "<|borough|>",
            "<|parish|>", "<|ward|>", "<|street|>", "<|lane|>", "<|court|>",
            "<|tavern|>", "<|inn|>", "<|coffeehouse|>", "<|market|>", "<|fair|>",
            
            # Historical period tokens
            "<|tudor|>", "<|stuart|>", "<|georgian|>", "<|regency|>", "<|victorian|>",
            "<|plague|>", "<|fire|>", "<|great|>", "<|civil|>", "<|war|>",
            
            # Social class tokens
            "<|noble|>", "<|gentleman|>", "<|lady|>", "<|commoner|>", "<|apprentice|>",
            "<|servant|>", "<|merchant|>", "<|artisan|>", "<|labourer|>", "<|beggar|>",
            
            # Legal and court tokens
            "<|trial|>", "<|judge|>", "<|jury|>", "<|witness|>", "<|accused|>",
            "<|sentence|>", "<|punishment|>", "<|gaol|>", "<|transport|>", "<|hanging|>",
            
            # Religious tokens
            "<|church|>", "<|parish|>", "<|clergy|>", "<|bishop|>", "<|archbishop|>",
            "<|prayer|>", "<|sermon|>", "<|blessing|>", "<|curse|>", "<|sin|>",
            
            # Economic tokens
            "<|shilling|>", "<|pound|>", "<|penny|>", "<|guinea|>", "<|crown|>",
            "<|trade|>", "<|commerce|>", "<|merchant|>", "<|shop|>", "<|warehouse|>",
            
            # Time and date tokens
            "<|morn|>", "<|noon|>", "<|eve|>", "<|night|>", "<|dawn|>", "<|dusk|>",
            "<|monday|>", "<|tuesday|>", "<|wednesday|>", "<|thursday|>", "<|friday|>",
            "<|saturday|>", "<|sunday|>", "<|january|>", "<|february|>", "<|march|>",
            "<|april|>", "<|may|>", "<|june|>", "<|july|>", "<|august|>",
            "<|september|>", "<|october|>", "<|november|>", "<|december|>"
        ]
        
        # Historical text patterns
        self.historical_patterns = [
            r'\b(?:thou|thee|thy|thine|hast|hath|doth|dost|art|wilt|shalt|canst|mayst)\b',
            r'\b(?:ye|yonder|hither|thither|whence|whither|wherefore|whereof)\b',
            r'\b(?:verily|indeed|forsooth|methinks|perchance|albeit|howbeit)\b',
            r'\b(?:anon|ere|whilst|betwixt|amongst|amidst|without|within)\b',
            r'\b(?:hitherto|thereto|whereto|whereof|whereby|wherefore)\b',
            r'\b(?:methinks|peradventure|verily|forsooth|indeed|truly)\b',
            r'\b(?:prithee|pray\s+thee|I\s+pray\s+you|I\s+beseech\s+you)\b',
            r'\b(?:God\s+save\s+the\s+King|God\s+bless\s+you|God\s+forbid)\b',
            r'\b(?:my\s+lord|my\s+lady|your\s+grace|your\s+majesty)\b',
            r'\b(?:good\s+morrow|good\s+even|good\s+day|farewell)\b'
        ]
        
        self.tokenizer = None
        self.training_data = []
        
    def load_training_data(self) -> List[str]:
        """Load and preprocess training data from various sources"""
        logger.info("📚 Loading training data...")
        
        training_texts = []
        
        # Load from corpus file
        corpus_file = self.data_dir / "london_historical_corpus.txt"
        if corpus_file.exists():
            logger.info(f"Loading corpus file: {corpus_file}")
            with open(corpus_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if content.strip():
                    training_texts.append(content)
                    logger.info(f"✅ Loaded corpus: {len(content):,} characters")
        
        # Load from individual text files
        text_files = list(self.data_dir.glob("*.txt"))
        for text_file in tqdm(text_files, desc="Loading text files"):
            if text_file.name == "london_historical_corpus.txt":
                continue  # Skip corpus file as it's already loaded
                
            try:
                with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if len(content.strip()) > 1000:  # Only include substantial content
                        training_texts.append(content)
                        logger.info(f"✅ Loaded {text_file.name}: {len(content):,} characters")
            except Exception as e:
                logger.warning(f"⚠️ Could not load {text_file.name}: {e}")
        
        # Combine all texts
        combined_text = "\n\n".join(training_texts)
        logger.info(f"📊 Total training data: {len(combined_text):,} characters")
        logger.info(f"📊 Number of text sources: {len(training_texts)}")
        
        return [combined_text] if combined_text else []
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for tokenizer training"""
        import re
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Preserve historical punctuation patterns
        text = re.sub(r'([.!?])\s*', r'\1 ', text)  # Add space after sentence endings
        text = re.sub(r'([,;:])\s*', r'\1 ', text)  # Add space after punctuation
        
        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[''']', "'", text)
        
        # Normalize dashes
        text = re.sub(r'[–—]', '-', text)
        
        # Preserve historical contractions
        text = re.sub(r'\b(\w+)\'(\w+)\b', r'\1\'\2', text)
        
        return text.strip()
    
    def create_tokenizer(self) -> Tokenizer:
        """Create and configure the tokenizer"""
        logger.info("🔧 Creating tokenizer...")
        
        # Initialize BPE tokenizer
        tokenizer = Tokenizer(models.BPE())
        
        # Configure normalizer
        tokenizer.normalizer = processors.Sequence([
            NFD(),
            Lowercase(),
            StripAccents()
        ])
        
        # Configure pre-tokenizer
        tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
        
        # Configure post-processor
        tokenizer.post_processor = processors.TemplateProcessing(
            single="<|startoftext|> $A <|endoftext|>",
            special_tokens=[
                ("<|startoftext|>", 1),
                ("<|endoftext|>", 2)
            ]
        )
        
        self.tokenizer = tokenizer
        return tokenizer
    
    def train_tokenizer(self, training_data: List[str]) -> None:
        """Train the tokenizer on the provided data"""
        logger.info("🎓 Training tokenizer...")
        
        if not training_data:
            raise ValueError("No training data provided")
        
        # Preprocess training data
        processed_data = []
        for text in tqdm(training_data, desc="Preprocessing texts"):
            processed_text = self.preprocess_text(text)
            if processed_text:
                processed_data.append(processed_text)
        
        logger.info(f"📊 Processed {len(processed_data)} texts for training")
        
        # Create trainer
        trainer = trainers.BpeTrainer(
            vocab_size=self.vocab_size,
            min_frequency=self.min_frequency,
            special_tokens=self.special_tokens,
            show_progress=True,
            continuing_subword_prefix="##"
        )
        
        # Train the tokenizer
        logger.info("🚀 Starting tokenizer training...")
        self.tokenizer.train_from_iterator(
            processed_data,
            trainer=trainer,
            length=len(processed_data)
        )
        
        logger.info("✅ Tokenizer training completed!")
    
    def save_tokenizer(self, name: str = "london_historical_tokenizer") -> Dict[str, str]:
        """Save the trained tokenizer"""
        logger.info(f"💾 Saving tokenizer: {name}")
        
        # Save tokenizer files
        tokenizer_dir = self.output_dir / name
        tokenizer_dir.mkdir(parents=True, exist_ok=True)
        
        # Save tokenizer
        tokenizer_path = tokenizer_dir / "tokenizer.json"
        self.tokenizer.save(str(tokenizer_path))
        
        # Save vocabulary
        vocab_path = tokenizer_dir / "vocab.json"
        with open(vocab_path, 'w', encoding='utf-8') as f:
            json.dump(self.tokenizer.get_vocab(), f, indent=2, ensure_ascii=False)
        
        # Save merges
        merges_path = tokenizer_dir / "merges.txt"
        with open(merges_path, 'w', encoding='utf-8') as f:
            f.write(self.tokenizer.get_model().get_merges())
        
        # Create HuggingFace tokenizer
        hf_tokenizer = PreTrainedTokenizerFast(
            tokenizer_object=self.tokenizer,
            bos_token="<|startoftext|>",
            eos_token="<|endoftext|>",
            pad_token="<|pad|>",
            unk_token="<|unk|>",
            mask_token="<|mask|>",
            sep_token="<|sep|>",
            cls_token="<|cls|>"
        )
        
        # Save HuggingFace tokenizer
        hf_tokenizer.save_pretrained(str(tokenizer_dir))
        
        # Save tokenizer configuration
        config = {
            "name": name,
            "vocab_size": self.vocab_size,
            "min_frequency": self.min_frequency,
            "special_tokens": self.special_tokens,
            "historical_patterns": self.historical_patterns,
            "training_data_sources": len(self.training_data),
            "total_characters": sum(len(text) for text in self.training_data),
            "tokenizer_files": {
                "tokenizer_json": str(tokenizer_path),
                "vocab_json": str(vocab_path),
                "merges_txt": str(merges_txt),
                "huggingface_dir": str(tokenizer_dir)
            }
        }
        
        config_path = tokenizer_dir / "tokenizer_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Tokenizer saved to: {tokenizer_dir}")
        
        return {
            "tokenizer_dir": str(tokenizer_dir),
            "tokenizer_json": str(tokenizer_path),
            "vocab_json": str(vocab_path),
            "merges_txt": str(merges_txt),
            "config_json": str(config_path)
        }
    
    def test_tokenizer(self, test_texts: List[str] = None) -> Dict[str, Any]:
        """Test the trained tokenizer"""
        logger.info("🧪 Testing tokenizer...")
        
        if test_texts is None:
            test_texts = [
                "In the year of our Lord 1665, the Great Plague swept through London.",
                "The streets were empty, and the bells tolled for the dead.",
                "Methinks the city hath never seen such sorrow.",
                "Verily, I say unto you, this is a time of great tribulation.",
                "The King's men rode through the streets, seeking those who had fled."
            ]
        
        results = {
            "test_texts": test_texts,
            "tokenizations": [],
            "statistics": {}
        }
        
        total_tokens = 0
        total_chars = 0
        
        for i, text in enumerate(test_texts):
            # Tokenize
            encoding = self.tokenizer.encode(text)
            tokens = encoding.tokens
            token_ids = encoding.ids
            
            # Decode back
            decoded = self.tokenizer.decode(token_ids)
            
            results["tokenizations"].append({
                "original": text,
                "tokens": tokens,
                "token_ids": token_ids,
                "decoded": decoded,
                "num_tokens": len(tokens),
                "num_chars": len(text)
            })
            
            total_tokens += len(tokens)
            total_chars += len(text)
            
            logger.info(f"Test {i+1}:")
            logger.info(f"  Original: {text}")
            logger.info(f"  Tokens: {tokens[:10]}{'...' if len(tokens) > 10 else ''}")
            logger.info(f"  Decoded: {decoded}")
            logger.info(f"  Token count: {len(tokens)}")
        
        # Calculate statistics
        results["statistics"] = {
            "total_tokens": total_tokens,
            "total_chars": total_chars,
            "avg_tokens_per_char": total_tokens / total_chars if total_chars > 0 else 0,
            "vocab_size": self.tokenizer.get_vocab_size(),
            "special_tokens_count": len(self.special_tokens)
        }
        
        logger.info(f"📊 Tokenizer Statistics:")
        logger.info(f"  Total tokens: {total_tokens:,}")
        logger.info(f"  Total characters: {total_chars:,}")
        logger.info(f"  Avg tokens per char: {total_tokens/total_chars:.3f}")
        logger.info(f"  Vocabulary size: {self.tokenizer.get_vocab_size():,}")
        
        return results
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print training summary"""
        print("\n" + "="*70)
        print("🎓 TOKENIZER TRAINING SUMMARY")
        print("="*70)
        print(f"Vocabulary size: {results['statistics']['vocab_size']:,}")
        print(f"Special tokens: {results['statistics']['special_tokens_count']}")
        print(f"Training texts: {len(self.training_data)}")
        print(f"Total characters: {results['statistics']['total_chars']:,}")
        print(f"Average tokens per character: {results['statistics']['avg_tokens_per_char']:.3f}")
        
        print(f"\n📁 Tokenizer files saved to: {self.output_dir}")
        print(f"🔧 Ready for model training!")
        print("="*70)

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train custom tokenizer for London Historical LLM")
    parser.add_argument("--data_dir", type=str, default="data/london_historical",
                       help="Directory containing training data")
    parser.add_argument("--output_dir", type=str, default="09_models/tokenizers",
                       help="Directory to save tokenizer")
    parser.add_argument("--vocab_size", type=int, default=50000,
                       help="Vocabulary size for tokenizer")
    parser.add_argument("--min_frequency", type=int, default=2,
                       help="Minimum frequency for tokens")
    parser.add_argument("--name", type=str, default="london_historical_tokenizer",
                       help="Name for the tokenizer")
    
    args = parser.parse_args()
    
    print("🎓 London Historical LLM - Tokenizer Training")
    print("=" * 50)
    
    # Initialize trainer
    trainer = LondonTokenizerTrainer(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        vocab_size=args.vocab_size,
        min_frequency=args.min_frequency
    )
    
    try:
        # Load training data
        training_data = trainer.load_training_data()
        if not training_data:
            logger.error("❌ No training data found!")
            return False
        
        # Create tokenizer
        trainer.create_tokenizer()
        
        # Train tokenizer
        trainer.train_tokenizer(training_data)
        
        # Save tokenizer
        saved_paths = trainer.save_tokenizer(args.name)
        
        # Test tokenizer
        test_results = trainer.test_tokenizer()
        
        # Print summary
        trainer.print_summary(test_results)
        
        logger.info("🎉 Tokenizer training completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tokenizer training failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
