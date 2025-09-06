# Enhanced London Historical LLM Training

## 🚀 Overview

This enhanced version includes a bigger model (400M parameters) and expanded data sources covering the full 1500-1850 period for London.

## 📊 Model Specifications

### **Enhanced Model (400M parameters):**
- **Layers**: 20 (vs 12 in original)
- **Heads**: 16 (vs 12 in original)
- **Hidden size**: 1280 (vs 768 in original)
- **Parameters**: 400M (vs 108M in original)
- **Vocabulary**: 30,000 tokens (custom historical tokenizer)
- **Context length**: 1024 tokens

### **Enhanced Data Sources:**
- **Time period**: 1500-1850 (full coverage)
- **Sources**: 14 additional high-quality historical texts
- **Data volume**: 4-5x more training data
- **Quality**: Authentic period language and vocabulary

## 🎯 Expected Improvements

### **Text Quality:**
- **30-50% better** text generation quality
- **More coherent** historical English
- **Better vocabulary** - period-appropriate words
- **Enhanced context** - understanding of social dynamics

### **Model Capacity:**
- **4x more parameters** - better learning capacity
- **Deeper architecture** - more complex pattern recognition
- **Larger vocabulary** - more diverse language generation

## 🚀 Quick Start

### **1. Save Current Model:**
```bash
python save_current_model.py
```

### **2. Setup Enhanced Training:**
```bash
python setup_enhanced_training.py
```

### **3. Start Enhanced Training:**
```bash
./launch_enhanced_training.sh
```

### **4. Test Enhanced Model:**
```bash
python sample_enhanced_model.py --prompt "In the year of our Lord 1834"
```

## 📋 Detailed Setup

### **Step 1: Save Current Model**
```bash
# Save your current 108M model as reference
python save_current_model.py
```
This creates a backup in `model_backups/london_llm_108m_TIMESTAMP/`

### **Step 2: Download Enhanced Data**
```bash
# Download additional historical sources (1500-1850)
python data_preparation_fixed.py
```

### **Step 3: Train Custom Tokenizer**
```bash
# Train tokenizer on enhanced data
python train_custom_tokenizer.py
```

### **Step 4: Prepare Dataset**
```bash
# Prepare training data with custom tokenizer
python prepare_dataset.py
```

### **Step 5: Start Enhanced Training**
```bash
# Launch enhanced training (400M parameters)
./launch_enhanced_training.sh
```

## ⏱️ Training Timeline

### **Expected Duration:**
- **Setup**: 30-60 minutes
- **Training**: 8-12 hours (400M parameters)
- **Total**: 9-13 hours

### **Checkpoints:**
- **Saved every**: 200 iterations
- **Location**: `out_london_historical_enhanced/ckpt.pt`
- **Resumable**: Yes, can resume from checkpoint

## 🔧 Configuration

### **Model Parameters:**
```python
n_layer = 20        # 12 → 20 layers
n_head = 16         # 12 → 16 heads
n_embd = 1280       # 768 → 1280 hidden size
vocab_size = 30000  # Custom tokenizer
```

### **Training Parameters:**
```python
batch_size = 8      # Adjusted for larger model
learning_rate = 6e-4
max_iters = 50000
warmup_iters = 2000
```

## 📊 Monitoring

### **Training Progress:**
```bash
# Monitor GPU usage
watch -n 1 nvidia-smi

# Check training logs
tail -f training.log
```

### **Expected Loss Progression:**
- **Start**: ~10.0 (random)
- **1000 iterations**: ~5.0
- **5000 iterations**: ~3.0
- **10000 iterations**: ~2.5
- **20000 iterations**: ~2.0
- **50000 iterations**: ~1.5-2.0

## 🧪 Testing

### **Test Prompts:**
```bash
# Historical narrative
python sample_enhanced_model.py --prompt "In the year of our Lord 1834"

# Social description
python sample_enhanced_model.py --prompt "The streets of London were filled with"

# Character dialogue
python sample_enhanced_model.py --prompt "Mr. Darcy walked through the ballroom"

# Descriptive prose
python sample_enhanced_model.py --prompt "The Thames flowed dark and mysterious"
```

### **Expected Output Quality:**
- **Coherent sentences** - Proper grammar and structure
- **Historical vocabulary** - Period-appropriate words
- **Authentic style** - 1800s writing patterns
- **Context awareness** - Understanding of social dynamics

## 🔄 Resuming Training

### **If Training Interrupted:**
```bash
# Resume from checkpoint
./launch_enhanced_training.sh
```
The script automatically detects and resumes from the latest checkpoint.

### **Checkpoint Management:**
- **Location**: `out_london_historical_enhanced/ckpt.pt`
- **Contains**: Model weights, optimizer state, iteration number
- **Backup**: Current model saved in `model_backups/`

## 📈 Performance Comparison

### **Original Model (108M):**
- **Loss**: ~2.4-2.9
- **Text quality**: Good
- **Training time**: 4-6 hours
- **Vocabulary**: 30,000 tokens

### **Enhanced Model (400M):**
- **Loss**: ~1.5-2.0 (expected)
- **Text quality**: Excellent
- **Training time**: 8-12 hours
- **Vocabulary**: 30,000 tokens
- **Data**: 4-5x more training data

## 🎯 Success Metrics

### **Text Quality Indicators:**
- **Coherence**: Sentences make sense
- **Historical accuracy**: Period-appropriate language
- **Vocabulary diversity**: Rich, varied word choice
- **Context understanding**: Proper social dynamics

### **Technical Metrics:**
- **Loss reduction**: Steady decrease over time
- **Validation loss**: Should track training loss
- **GPU utilization**: High, consistent usage
- **Memory usage**: Stable, no leaks

## 🚨 Troubleshooting

### **Common Issues:**
1. **Out of memory**: Reduce batch size
2. **Slow training**: Check GPU utilization
3. **Poor text quality**: Check tokenizer and data
4. **Training stuck**: Check learning rate

### **Solutions:**
```bash
# Reduce batch size if OOM
# Edit launch_enhanced_training.sh
--batch_size=4  # Instead of 8

# Check GPU status
nvidia-smi

# Monitor training
watch -n 1 nvidia-smi
```

## 📝 Notes

- **Model size**: 400M parameters require more GPU memory
- **Training time**: Longer due to bigger model
- **Data quality**: Enhanced sources provide better training
- **Checkpoints**: Save frequently for safety
- **Resumable**: Can always resume from checkpoint

---

**Ready to train your enhanced London Historical LLM!** 🏛️✨
