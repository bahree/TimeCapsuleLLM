#!/usr/bin/env python3
"""
Model Training for London Historical LLM
Trains a transformer model on historical London texts
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, 
        TrainingArguments, Trainer, 
        DataCollatorForLanguageModeling,
        get_linear_schedule_with_warmup
    )
    from accelerate import Accelerator
    from datasets import Dataset as HFDataset
    import wandb
    from tqdm import tqdm
    import numpy as np
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LondonHistoricalDataset(Dataset):
    """Custom dataset for London historical texts"""
    
    def __init__(self, texts: list, tokenizer, max_length: int = 512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()
        }

class LondonHistoricalTrainer:
    def __init__(self, 
                 data_dir: str = "data/london_historical",
                 tokenizer_dir: str = "09_models/tokenizers/london_historical_tokenizer",
                 output_dir: str = "09_models/checkpoints",
                 model_name: str = "gpt2-medium",  # Upgraded to medium model
                 max_length: int = 1024,  # Increased context length
                 batch_size: int = 2,  # Reduced for larger model
                 learning_rate: float = 3e-5,  # Optimized learning rate
                 num_epochs: int = 5,  # Increased epochs
                 warmup_steps: int = 500,  # Increased warmup
                 save_steps: int = 250,  # More frequent saves
                 eval_steps: int = 250,  # More frequent evaluation
                 logging_steps: int = 50):  # More frequent logging
        
        self.data_dir = Path(data_dir)
        self.tokenizer_dir = Path(tokenizer_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Training parameters
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.warmup_steps = warmup_steps
        self.save_steps = save_steps
        self.eval_steps = eval_steps
        self.logging_steps = logging_steps
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.trainer = None
        self.accelerator = None
        
        # Training data
        self.train_dataset = None
        self.eval_dataset = None
        
        # Statistics
        self.training_stats = {
            'start_time': datetime.now().isoformat(),
            'model_name': model_name,
            'max_length': max_length,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
            'num_epochs': num_epochs,
            'total_steps': 0,
            'total_epochs': 0,
            'final_loss': 0.0,
            'best_loss': float('inf'),
            'training_time_minutes': 0
        }
    
    def setup_accelerator(self):
        """Setup Accelerator for multi-GPU training with enhanced configuration"""
        logger.info("🚀 Setting up Accelerator...")
        
        # Check available GPUs
        gpu_count = torch.cuda.device_count()
        logger.info(f"🔍 Detected {gpu_count} GPU(s)")
        
        if gpu_count > 0:
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                logger.info(f"   GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        
        # Configure accelerator based on available hardware
        if gpu_count > 1:
            # Multi-GPU setup
            logger.info("🚀 Configuring for multi-GPU training...")
            self.accelerator = Accelerator(
                gradient_accumulation_steps=4,
                mixed_precision="fp16" if torch.cuda.is_available() else "no",
                log_with="wandb" if self.setup_wandb() else None,
                project_dir=str(self.output_dir)
            )
        elif gpu_count == 1:
            # Single GPU setup
            logger.info("🚀 Configuring for single GPU training...")
            self.accelerator = Accelerator(
                gradient_accumulation_steps=2,
                mixed_precision="fp16" if torch.cuda.is_available() else "no",
                log_with="wandb" if self.setup_wandb() else None,
                project_dir=str(self.output_dir)
            )
        else:
            # CPU-only setup
            logger.info("🚀 Configuring for CPU-only training...")
            self.accelerator = Accelerator(
                gradient_accumulation_steps=1,
                mixed_precision="no",
                log_with="wandb" if self.setup_wandb() else None,
                project_dir=str(self.output_dir)
            )
        
        logger.info(f"✅ Accelerator initialized")
        logger.info(f"   Device: {self.accelerator.device}")
        logger.info(f"   Process index: {self.accelerator.process_index}")
        logger.info(f"   Local process index: {self.accelerator.local_process_index}")
        logger.info(f"   Distributed: {self.accelerator.distributed_type}")
        logger.info(f"   Mixed precision: {self.accelerator.mixed_precision}")
        logger.info(f"   GPU count: {gpu_count}")
        
        return True
    
    def setup_wandb(self):
        """Setup WandB for experiment tracking"""
        try:
            import wandb
            
            # Check if WandB is configured
            if not wandb.api.api_key:
                logger.warning("⚠️ WandB API key not found. Set WANDB_API_KEY environment variable.")
                return False
            
            # Initialize WandB
            wandb.init(
                project="london-historical-llm",
                name=f"london-llm-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                config={
                    "model_name": self.model_name,
                    "max_length": self.max_length,
                    "batch_size": self.batch_size,
                    "learning_rate": self.learning_rate,
                    "num_epochs": self.num_epochs,
                    "vocab_size": 50000,
                    "special_tokens": 100,
                    "gpu_count": torch.cuda.device_count(),
                    "mixed_precision": self.accelerator.mixed_precision if hasattr(self, 'accelerator') else "no"
                },
                tags=["london", "historical", "llm", "gpt2", "1500-1850"]
            )
            
            logger.info("✅ WandB initialized successfully")
            return True
            
        except ImportError:
            logger.warning("⚠️ WandB not installed. Install with: pip install wandb")
            return False
        except Exception as e:
            logger.warning(f"⚠️ WandB setup failed: {e}")
            return False
    
    def load_tokenizer(self):
        """Load the custom tokenizer"""
        logger.info(f"🔤 Loading tokenizer from: {self.tokenizer_dir}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.tokenizer_dir))
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info(f"✅ Tokenizer loaded successfully")
            logger.info(f"   Vocabulary size: {self.tokenizer.vocab_size:,}")
            logger.info(f"   Model max length: {self.tokenizer.model_max_length}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load tokenizer: {e}")
            return False
    
    def load_model(self):
        """Load or initialize the model"""
        logger.info(f"🤖 Loading model: {self.model_name}")
        
        try:
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                vocab_size=len(self.tokenizer),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                bos_token_id=self.tokenizer.bos_token_id
            )
            
            # Resize token embeddings if needed
            if len(self.tokenizer) != self.model.config.vocab_size:
                self.model.resize_token_embeddings(len(self.tokenizer))
            
            logger.info(f"✅ Model loaded successfully")
            logger.info(f"   Model type: {self.model.config.model_type}")
            logger.info(f"   Hidden size: {self.model.config.hidden_size}")
            logger.info(f"   Number of layers: {self.model.config.num_hidden_layers}")
            logger.info(f"   Number of attention heads: {self.model.config.num_attention_heads}")
            logger.info(f"   Vocabulary size: {self.model.config.vocab_size:,}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    def load_training_data(self):
        """Load and prepare training data"""
        logger.info("📚 Loading training data...")
        
        # Load corpus file
        corpus_file = self.data_dir / "london_historical_corpus.txt"
        if not corpus_file.exists():
            logger.error(f"❌ Corpus file not found: {corpus_file}")
            return False
        
        with open(corpus_file, 'r', encoding='utf-8', errors='ignore') as f:
            corpus_text = f.read()
        
        # Split into chunks
        chunk_size = self.max_length * 2  # Overlap for better training
        chunks = []
        
        for i in range(0, len(corpus_text), chunk_size):
            chunk = corpus_text[i:i + chunk_size]
            if len(chunk.strip()) > 100:  # Only include substantial chunks
                chunks.append(chunk.strip())
        
        logger.info(f"📊 Loaded {len(chunks):,} text chunks")
        logger.info(f"📊 Total characters: {len(corpus_text):,}")
        
        # Split into train/eval
        split_idx = int(0.9 * len(chunks))
        train_chunks = chunks[:split_idx]
        eval_chunks = chunks[split_idx:]
        
        # Create datasets
        self.train_dataset = LondonHistoricalDataset(
            train_chunks, self.tokenizer, self.max_length
        )
        self.eval_dataset = LondonHistoricalDataset(
            eval_chunks, self.tokenizer, self.max_length
        )
        
        logger.info(f"✅ Training data prepared")
        logger.info(f"   Train samples: {len(self.train_dataset):,}")
        logger.info(f"   Eval samples: {len(self.eval_dataset):,}")
        
        return True
    
    def setup_training_arguments(self):
        """Setup training arguments"""
        logger.info("⚙️ Setting up training arguments...")
        
        # Calculate total steps
        steps_per_epoch = len(self.train_dataset) // self.batch_size
        total_steps = steps_per_epoch * self.num_epochs
        
        self.training_stats['total_steps'] = total_steps
        self.training_stats['total_epochs'] = self.num_epochs
        
        # Enhanced training arguments for historical text
        self.training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            overwrite_output_dir=True,
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            warmup_steps=self.warmup_steps,
            learning_rate=self.learning_rate,
            logging_steps=self.logging_steps,
            save_steps=self.save_steps,
            eval_steps=self.eval_steps,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="wandb" if (self.accelerator.is_main_process and self.setup_wandb()) else None,
            run_name=f"london-historical-llm-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            logging_dir=str(self.output_dir / "logs"),
            save_total_limit=5,  # Keep more checkpoints
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_pin_memory=True,
            dataloader_num_workers=4,
            fp16=self.accelerator.mixed_precision == "fp16",
            bf16=self.accelerator.mixed_precision == "bf16",
            gradient_accumulation_steps=4,  # Increased for better gradient estimates
            gradient_checkpointing=True,
            optim="adamw_torch",
            weight_decay=0.1,  # Increased weight decay for regularization
            adam_beta1=0.9,
            adam_beta2=0.95,  # Adjusted for better convergence
            adam_epsilon=1e-8,
            max_grad_norm=0.5,  # Reduced for more stable training
            lr_scheduler_type="cosine_with_restarts",  # Better for long training
            warmup_ratio=0.1,
            group_by_length=True,
            length_column_name="length",
            disable_tqdm=False,
            seed=42,
            # Additional advanced settings
            dataloader_drop_last=True,  # Drop incomplete batches
            eval_accumulation_steps=1,  # Evaluate more frequently
            save_safetensors=True,  # Use SafeTensors format
            include_inputs_for_metrics=True,  # Include inputs for metrics
            # Learning rate scheduling
            lr_scheduler_kwargs={"num_cycles": 2},  # Cosine with restarts
            # Early stopping
            early_stopping_patience=3,
            early_stopping_threshold=0.001,
            # Memory optimization
            dataloader_prefetch_factor=2,
            # Mixed precision optimization
            half_precision_backend="auto",
            # Logging
            log_level="info",
            log_on_each_node=True,
            # Distributed training
            local_rank=-1,
            ddp_find_unused_parameters=False,
            ddp_bucket_cap_mb=25,
            # Model saving
            save_only_model=False,  # Save optimizer states too
            ignore_data_skip=False,
            # Evaluation
            eval_do_sample=False,
            eval_max_new_tokens=50,
            # Training stability
            skip_memory_metrics=False,
            use_legacy_prediction_loop=False
        )
        
        logger.info(f"✅ Training arguments configured")
        logger.info(f"   Total steps: {total_steps:,}")
        logger.info(f"   Steps per epoch: {steps_per_epoch:,}")
        logger.info(f"   Learning rate: {self.learning_rate}")
        logger.info(f"   Batch size: {self.batch_size}")
        logger.info(f"   Mixed precision: {self.accelerator.mixed_precision}")
    
    def setup_data_collator(self):
        """Setup data collator for language modeling"""
        logger.info("🔧 Setting up data collator...")
        
        self.data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal language modeling
            pad_to_multiple_of=8
        )
        
        logger.info("✅ Data collator configured")
    
    def compute_metrics(self, eval_pred):
        """Compute evaluation metrics"""
        predictions, labels = eval_pred
        
        # Flatten predictions and labels
        predictions = predictions.reshape(-1, predictions.shape[-1])
        labels = labels.reshape(-1)
        
        # Get predicted token ids
        predicted_ids = np.argmax(predictions, axis=-1)
        
        # Calculate accuracy
        accuracy = accuracy_score(labels, predicted_ids)
        
        # Calculate precision, recall, F1
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predicted_ids, average='weighted', zero_division=0
        )
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def setup_trainer(self):
        """Setup the HuggingFace Trainer"""
        logger.info("🎓 Setting up trainer...")
        
        self.trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
            data_collator=self.data_collator,
            compute_metrics=self.compute_metrics,
            tokenizer=self.tokenizer
        )
        
        logger.info("✅ Trainer configured")
    
    def train_model(self):
        """Train the model"""
        logger.info("🚀 Starting model training...")
        
        try:
            # Start training
            start_time = time.time()
            
            self.trainer.train()
            
            end_time = time.time()
            training_time = (end_time - start_time) / 60
            
            self.training_stats['training_time_minutes'] = training_time
            self.training_stats['end_time'] = datetime.now().isoformat()
            
            # Get final metrics
            final_metrics = self.trainer.evaluate()
            self.training_stats['final_loss'] = final_metrics.get('eval_loss', 0.0)
            self.training_stats['final_metrics'] = final_metrics
            
            logger.info(f"✅ Training completed!")
            logger.info(f"   Training time: {training_time:.1f} minutes")
            logger.info(f"   Final loss: {self.training_stats['final_loss']:.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            return False
    
    def save_model(self):
        """Save the trained model"""
        logger.info("💾 Saving trained model...")
        
        try:
            # Save model and tokenizer
            self.trainer.save_model()
            self.tokenizer.save_pretrained(str(self.output_dir))
            
            # Save training statistics
            stats_file = self.output_dir / "training_statistics.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Model saved to: {self.output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
            return False
    
    def print_summary(self):
        """Print training summary"""
        print("\n" + "="*70)
        print("🎓 MODEL TRAINING SUMMARY")
        print("="*70)
        print(f"Model: {self.training_stats['model_name']}")
        print(f"Training time: {self.training_stats['training_time_minutes']:.1f} minutes")
        print(f"Total steps: {self.training_stats['total_steps']:,}")
        print(f"Final loss: {self.training_stats['final_loss']:.4f}")
        print(f"Batch size: {self.training_stats['batch_size']}")
        print(f"Learning rate: {self.training_stats['learning_rate']}")
        print(f"Max length: {self.training_stats['max_length']}")
        
        if 'final_metrics' in self.training_stats:
            metrics = self.training_stats['final_metrics']
            print(f"\n📊 Final Metrics:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.4f}")
                else:
                    print(f"   {key}: {value}")
        
        print(f"\n📁 Model saved to: {self.output_dir}")
        print(f"🔧 Ready for inference!")
        print("="*70)

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train London Historical LLM")
    parser.add_argument("--data_dir", type=str, default="data/london_historical",
                       help="Directory containing training data")
    parser.add_argument("--tokenizer_dir", type=str, 
                       default="09_models/tokenizers/london_historical_tokenizer",
                       help="Directory containing tokenizer")
    parser.add_argument("--output_dir", type=str, default="09_models/checkpoints",
                       help="Directory to save trained model")
    parser.add_argument("--model_name", type=str, default="gpt2-medium",
                       help="Base model name (gpt2, gpt2-medium, gpt2-large)")
    parser.add_argument("--max_length", type=int, default=1024,
                       help="Maximum sequence length")
    parser.add_argument("--batch_size", type=int, default=2,
                       help="Training batch size")
    parser.add_argument("--learning_rate", type=float, default=3e-5,
                       help="Learning rate")
    parser.add_argument("--num_epochs", type=int, default=5,
                       help="Number of training epochs")
    parser.add_argument("--warmup_steps", type=int, default=500,
                       help="Number of warmup steps")
    
    args = parser.parse_args()
    
    print("🎓 London Historical LLM - Model Training")
    print("=" * 50)
    
    # Initialize trainer
    trainer = LondonHistoricalTrainer(
        data_dir=args.data_dir,
        tokenizer_dir=args.tokenizer_dir,
        output_dir=args.output_dir,
        model_name=args.model_name,
        max_length=args.max_length,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        num_epochs=args.num_epochs,
        warmup_steps=args.warmup_steps
    )
    
    try:
        # Setup accelerator
        trainer.setup_accelerator()
        
        # Load tokenizer
        if not trainer.load_tokenizer():
            return False
        
        # Load model
        if not trainer.load_model():
            return False
        
        # Load training data
        if not trainer.load_training_data():
            return False
        
        # Setup training
        trainer.setup_training_arguments()
        trainer.setup_data_collator()
        trainer.setup_trainer()
        
        # Train model
        if not trainer.train_model():
            return False
        
        # Save model
        if not trainer.save_model():
            return False
        
        # Print summary
        trainer.print_summary()
        
        logger.info("🎉 Model training completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
