#!/usr/bin/env python3
"""
Test tokenizer efficiency and quality before training
"""

import os
import time
import json
from pathlib import Path
from tokenizers import Tokenizer
import matplotlib.pyplot as plt
import numpy as np

class TokenizerTester:
    def __init__(self):
        self.custom_tokenizer_path = "tokenizer_historical/tokenizer.json"
        self.corpus_path = "data/london_data/london_corpus_merged.txt"
        
    def load_tokenizer(self):
        """Load the custom tokenizer"""
        if not os.path.exists(self.custom_tokenizer_path):
            print("❌ Custom tokenizer not found!")
            print("   Please run: python train_custom_tokenizer.py")
            return None
            
        print("🔤 Loading custom historical tokenizer...")
        tokenizer = Tokenizer.from_file(self.custom_tokenizer_path)
        vocab_size = tokenizer.get_vocab_size()
        print(f"✅ Loaded tokenizer with {vocab_size:,} tokens")
        return tokenizer
    
    def test_encoding_speed(self, tokenizer, sample_texts):
        """Test encoding speed"""
        print("\n⚡ Testing encoding speed...")
        
        times = []
        token_counts = []
        
        for text in sample_texts:
            start_time = time.time()
            tokens = tokenizer.encode(text)
            end_time = time.time()
            
            times.append(end_time - start_time)
            token_counts.append(len(tokens.ids))
        
        avg_time = np.mean(times)
        avg_tokens = np.mean(token_counts)
        
        print(f"   Average encoding time: {avg_time*1000:.2f}ms per text")
        print(f"   Average tokens per text: {avg_tokens:.1f}")
        print(f"   Tokens per second: {avg_tokens/avg_time:.0f}")
        
        return times, token_counts
    
    def test_compression_ratio(self, tokenizer, sample_texts):
        """Test compression ratio (characters vs tokens)"""
        print("\n📊 Testing compression ratio...")
        
        ratios = []
        for text in sample_texts:
            tokens = tokenizer.encode(text)
            char_count = len(text)
            token_count = len(tokens.ids)
            ratio = char_count / token_count if token_count > 0 else 0
            ratios.append(ratio)
        
        avg_ratio = np.mean(ratios)
        print(f"   Average compression ratio: {avg_ratio:.2f} chars/token")
        print(f"   This means each token represents ~{avg_ratio:.1f} characters")
        
        return ratios
    
    def test_vocabulary_coverage(self, tokenizer, sample_texts):
        """Test vocabulary coverage and unknown tokens"""
        print("\n📚 Testing vocabulary coverage...")
        
        total_tokens = 0
        unknown_tokens = 0
        unique_tokens = set()
        
        for text in sample_texts:
            tokens = tokenizer.encode(text)
            total_tokens += len(tokens.ids)
            unique_tokens.update(tokens.ids)
            
            # Check for unknown tokens (usually token 0 or special unknown token)
            vocab_size = tokenizer.get_vocab_size()
            for token_id in tokens.ids:
                if token_id >= vocab_size:  # This shouldn't happen with proper tokenizer
                    unknown_tokens += 1
        
        coverage = (total_tokens - unknown_tokens) / total_tokens * 100
        unique_ratio = len(unique_tokens) / total_tokens * 100
        
        print(f"   Total tokens processed: {total_tokens:,}")
        print(f"   Unique tokens used: {len(unique_tokens):,}")
        print(f"   Vocabulary coverage: {coverage:.2f}%")
        print(f"   Token diversity: {unique_ratio:.2f}%")
        
        return coverage, unique_ratio
    
    def test_historical_text_quality(self, tokenizer):
        """Test quality on historical text samples"""
        print("\n🏛️ Testing historical text quality...")
        
        historical_samples = [
            "In the year of our Lord 1834, the streets of London were filled with the sounds of horse-drawn carriages.",
            "The gentleman from the country said, 'I have never seen such a sight in all my days.'",
            "Mr. Darcy walked through the ballroom with his usual air of superiority.",
            "The Thames flowed dark and mysterious through the heart of the city.",
            "It was the best of times, it was the worst of times.",
            "The year was 1812, and war had come to England once more.",
            "Lady Catherine de Bourgh was not pleased with the news.",
            "The old man sat by the fire, reading his Bible.",
            "The coach rattled down the cobblestone streets of London.",
            "Chapter I: The Beginning of the End"
        ]
        
        perfect_reconstructions = 0
        
        for i, text in enumerate(historical_samples, 1):
            print(f"\n--- Historical Sample {i} ---")
            print(f"Original: {text}")
            
            # Encode and decode
            tokens = tokenizer.encode(text)
            decoded = tokenizer.decode(tokens.ids)
            
            print(f"Tokens: {tokens.ids[:15]}..." if len(tokens.ids) > 15 else f"Tokens: {tokens.ids}")
            print(f"Decoded: {decoded}")
            
            # Check reconstruction quality
            if text.lower().strip() == decoded.lower().strip():
                print("✅ Perfect reconstruction")
                perfect_reconstructions += 1
            else:
                print("⚠️  Reconstruction differs")
                print(f"   Original length: {len(text)}")
                print(f"   Decoded length: {len(decoded)}")
        
        quality_score = perfect_reconstructions / len(historical_samples) * 100
        print(f"\n📊 Historical text quality score: {quality_score:.1f}%")
        
        return quality_score
    
    def test_special_tokens(self, tokenizer):
        """Test special token handling"""
        print("\n🎯 Testing special tokens...")
        
        special_tests = [
            ("Year token", "The year was 1834"),
            ("Name token", "Mr. Darcy and Lady Catherine"),
            ("Place token", "London and the Thames"),
            ("Title token", "Dr. Smith and Mrs. Jones"),
            ("Chapter token", "Chapter I: The Beginning"),
            ("Quote token", 'He said, "This is important."'),
            ("Newline token", "Line one\nLine two"),
            ("Paragraph token", "Paragraph one.\n\nParagraph two.")
        ]
        
        for test_name, text in special_tests:
            tokens = tokenizer.encode(text)
            print(f"   {test_name}: {len(tokens.ids)} tokens")
    
    def estimate_training_efficiency(self, tokenizer, sample_texts):
        """Estimate training efficiency metrics"""
        print("\n🚀 Estimating training efficiency...")
        
        # Calculate average tokens per text
        total_tokens = sum(len(tokenizer.encode(text).ids) for text in sample_texts)
        avg_tokens = total_tokens / len(sample_texts)
        
        # Estimate corpus size
        if os.path.exists(self.corpus_path):
            with open(self.corpus_path, 'r', encoding='utf-8') as f:
                corpus_text = f.read()
            
            # Sample the corpus for estimation
            sample_size = min(100000, len(corpus_text))
            corpus_sample = corpus_text[:sample_size]
            sample_tokens = len(tokenizer.encode(corpus_sample).ids)
            
            # Estimate full corpus tokens
            estimated_corpus_tokens = int(sample_tokens * (len(corpus_text) / sample_size))
            
            print(f"   Estimated corpus tokens: {estimated_corpus_tokens:,}")
            print(f"   Average tokens per text: {avg_tokens:.1f}")
            print(f"   Vocabulary size: {tokenizer.get_vocab_size():,}")
            
            # Estimate training efficiency
            vocab_size = tokenizer.get_vocab_size()
            compression_ratio = len(corpus_text) / estimated_corpus_tokens if estimated_corpus_tokens > 0 else 1
            
            print(f"   Compression ratio: {compression_ratio:.2f}x")
            print(f"   Memory efficiency: {'Good' if compression_ratio > 2 else 'Fair' if compression_ratio > 1.5 else 'Poor'}")
            
            return estimated_corpus_tokens, compression_ratio
        
        return None, None
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🧪 Tokenizer Efficiency Test Suite")
        print("=" * 50)
        
        # Load tokenizer
        tokenizer = self.load_tokenizer()
        if not tokenizer:
            return False
        
        # Load sample texts
        sample_texts = [
            "In the year of our Lord 1834, the streets of London were filled with the sounds of horse-drawn carriages.",
            "The gentleman from the country said, 'I have never seen such a sight in all my days.'",
            "Mr. Darcy walked through the ballroom with his usual air of superiority.",
            "The Thames flowed dark and mysterious through the heart of the city.",
            "It was the best of times, it was the worst of times.",
            "The year was 1812, and war had come to England once more.",
            "Lady Catherine de Bourgh was not pleased with the news.",
            "The old man sat by the fire, reading his Bible.",
            "The coach rattled down the cobblestone streets of London.",
            "Chapter I: The Beginning of the End"
        ]
        
        # Run all tests
        encoding_times, token_counts = self.test_encoding_speed(tokenizer, sample_texts)
        compression_ratios = self.test_compression_ratio(tokenizer, sample_texts)
        coverage, diversity = self.test_vocabulary_coverage(tokenizer, sample_texts)
        quality_score = self.test_historical_text_quality(tokenizer)
        self.test_special_tokens(tokenizer)
        corpus_tokens, compression_ratio = self.estimate_training_efficiency(tokenizer, sample_texts)
        
        # Overall assessment
        print("\n📊 Overall Assessment")
        print("=" * 30)
        
        # Calculate overall score
        scores = []
        if coverage > 95: scores.append(1)
        elif coverage > 90: scores.append(0.8)
        elif coverage > 80: scores.append(0.6)
        else: scores.append(0.4)
        
        if quality_score > 90: scores.append(1)
        elif quality_score > 80: scores.append(0.8)
        elif quality_score > 70: scores.append(0.6)
        else: scores.append(0.4)
        
        if compression_ratio > 2: scores.append(1)
        elif compression_ratio > 1.5: scores.append(0.8)
        elif compression_ratio > 1.2: scores.append(0.6)
        else: scores.append(0.4)
        
        overall_score = np.mean(scores) * 100
        
        print(f"Overall Score: {overall_score:.1f}/100")
        
        if overall_score >= 80:
            print("✅ EXCELLENT - Ready for training!")
            print("   This tokenizer should produce high-quality results.")
        elif overall_score >= 60:
            print("⚠️  GOOD - Ready for training with minor concerns")
            print("   This tokenizer should work well for training.")
        else:
            print("❌ POOR - Consider retraining tokenizer")
            print("   This tokenizer may not produce good results.")
        
        print(f"\n🎯 Recommendation: {'Proceed with training' if overall_score >= 60 else 'Retrain tokenizer'}")
        
        return overall_score >= 60

def main():
    tester = TokenizerTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🚀 Ready to start training!")
        print("   Run: ./launch_2gpu.sh")
    else:
        print("\n🔄 Consider retraining the tokenizer:")
        print("   Run: python train_custom_tokenizer.py")

if __name__ == "__main__":
    main()
