# 🏛️ Remote London Historical Data Downloader

A remote-optimized system for downloading historical data for training a London-based Small Language Model (SLM) covering the period 1500-1850.

## 🌐 Remote Machine Optimized

This version is specifically designed for remote machine execution with:
- **Enhanced network resilience** with retry logic and exponential backoff
- **Comprehensive logging** to files for debugging
- **Priority-based downloading** focusing on most reliable sources
- **Simplified dependencies** for easier remote installation
- **Progress tracking** with detailed statistics

## 🚀 Quick Start

### **Option 1: Interactive Launcher (Recommended)**
```bash
python run_remote_download.py
```

### **Option 2: Test First**
```bash
python test_remote_download.py
```

### **Option 3: Direct Download**
```bash
python remote_london_downloader.py
```

## 📋 What It Downloads

### **Historical Sources (Priority Order)**
1. **A Journal of the Plague Year** (1665) - Daniel Defoe's account of the Great Plague
2. **Source Book of London History** (1500-1800) - Curated historical extracts
3. **Historical Collections of a Citizen of London** (1400-1500) - 15th century poems and chronicles

### **Literature Sources**
- **Pride and Prejudice** (1813) - Jane Austen
- **A Christmas Carol** (1843) - Charles Dickens
- **Oliver Twist** (1838) - Charles Dickens
- **Wuthering Heights** (1847) - Emily Brontë
- **Jane Eyre** (1847) - Charlotte Brontë
- **Frankenstein** (1818) - Mary Shelley
- **Dracula** (1897) - Bram Stoker
- **The Picture of Dorian Gray** (1890) - Oscar Wilde

## 📁 Output Structure

```
data/london_historical/
├── london_historical_corpus.txt          # Merged training corpus
├── remote_download_statistics.json       # Download statistics
├── defoe_plague_processed.txt            # Plague Year text
├── source_book_london_processed.txt      # London history extracts
├── historical_collections_processed.txt  # 15th century collections
├── gutenberg_*.txt                       # Project Gutenberg texts
└── london_downloader.log                 # Detailed execution log
```

## 🔧 Installation

### **Requirements**
```bash
pip install requests beautifulsoup4 tqdm
```

### **Optional (for better performance)**
```bash
pip install lxml  # Faster XML parsing
```

## 🧪 Testing

### **Run Test Suite**
```bash
python test_remote_download.py
```

This will test:
- ✅ Module imports
- ✅ Network connectivity
- ✅ Downloader initialization
- ✅ Single file download

### **Expected Output**
```
🧪 Remote London Downloader - Test Suite
==================================================

🔬 Running Import Test...
✅ requests
✅ beautifulsoup4
✅ tqdm
✅ xml (built-in)
✅ Import Test PASSED

🔬 Running Network Test...
✅ https://www.gutenberg.org: 200
✅ https://archive.org: 200
✅ https://www.google.com: 200
✅ Network Test PASSED

🔬 Running Downloader Init Test...
✅ Downloader initialized
   Output directory: test_data
   Time period: (1500, 1850)
   Historical sources: 3
   Gutenberg sources: 8
✅ Downloader Init Test PASSED

🔬 Running Single Download Test...
   Downloading: https://www.gutenberg.org/files/376/376-0.txt
✅ Download successful: test_data/test_download.txt (123456 bytes)
✅ Single Download Test PASSED

📊 Test Results: 4/4 tests passed
🎉 All tests passed! Ready to run the full downloader.
```

## 🚀 Running the Downloader

### **Interactive Mode**
```bash
python run_remote_download.py
```

Choose from:
1. **Run tests only** - Verify everything works
2. **Run full download** - Download all sources
3. **Run tests then download** - Test first, then download
4. **Exit**

### **Direct Mode**
```bash
python remote_london_downloader.py
```

## 📊 Monitoring Progress

### **Real-time Progress**
- Progress bars for individual downloads
- Success/failure counts
- File size tracking
- Network connectivity testing

### **Log Files**
- **london_downloader.log** - Detailed execution log
- **remote_download_statistics.json** - Download statistics

### **Example Statistics**
```json
{
  "total_attempted": 11,
  "successful_downloads": 10,
  "failed_downloads": 1,
  "total_size_mb": 15.7,
  "sources_processed": 3,
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T10:45:00",
  "duration_minutes": 15.0
}
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Import Errors**
   ```bash
   pip install requests beautifulsoup4 tqdm
   ```

2. **Network Timeouts**
   - The downloader includes retry logic
   - Check your internet connection
   - Some sources may be temporarily unavailable

3. **Permission Errors**
   ```bash
   chmod +x run_remote_download.py
   chmod +x test_remote_download.py
   chmod +x remote_london_downloader.py
   ```

4. **Disk Space**
   - Check available disk space
   - Downloads typically require 50-200MB

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Expected Results

### **Data Volume**
- **Total Sources**: 11 (3 historical + 8 literature)
- **Expected Size**: 50-200MB of processed text
- **Text Count**: 11 individual documents
- **Time Coverage**: 1400-1897 (500 years)

### **Quality**
- **Authentic Language**: Real historical texts
- **Diverse Content**: Literature, history, social commentary
- **Clean Text**: Processed and cleaned for training
- **Structured Format**: Ready for tokenizer training

## 🎯 Next Steps

After successful download:

1. **Train Custom Tokenizer**
   ```bash
   python train_custom_tokenizer.py
   ```

2. **Prepare Dataset**
   ```bash
   python prepare_dataset.py
   ```

3. **Start Training**
   ```bash
   ./launch_2gpu.sh
   ```

4. **Test Generation**
   ```bash
   python sample_london_llm.py
   ```

## 📝 Notes

- **Respectful Downloading**: Built-in delays and rate limiting
- **Error Recovery**: Automatic retry with exponential backoff
- **Remote Optimized**: Designed for headless remote execution
- **Comprehensive Logging**: Detailed logs for debugging
- **Progress Tracking**: Real-time progress and statistics

## 🆘 Support

If you encounter issues:

1. **Check the logs**: `london_downloader.log`
2. **Run tests**: `python test_remote_download.py`
3. **Check network**: Test internet connectivity
4. **Verify dependencies**: Ensure all packages are installed

---

**Ready to build your London Historical LLM on a remote machine!** 🏛️🌐✨
