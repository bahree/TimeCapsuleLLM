# 🏛️ Comprehensive London Historical Data Downloader

A comprehensive system for downloading and processing historical data from multiple sources for training a London-based Small Language Model (SLM) covering the period 1500-1850.

## 📚 Overview

This system integrates multiple historical data sources to create a rich training dataset for a London Historical LLM. It combines direct downloads, web scraping, and data processing to gather authentic historical texts from the Tudor, Stuart, Georgian, and early Victorian periods.

## 🆕 New Features

### **Multiple Data Sources**
- **London Lives 1690-1800**: 240,000 manuscript pages from eight London archives
- **Old Bailey Proceedings**: 197,000+ trial accounts from London's Central Criminal Court
- **The National Archives**: UK government records and correspondence
- **British History Online**: Digital library of primary and secondary sources
- **UK Data Service**: Social and economic data including GIS
- **Connected Histories**: Federated search across multiple resources
- **Project Gutenberg**: Public domain books and literature
- **Internet Archive**: Historical documents and manuscripts

### **Advanced Capabilities**
- **Web Scraping**: Intelligent scraping of historical websites
- **Data Processing**: XML, CSV, and text processing
- **Error Handling**: Robust error handling and retry mechanisms
- **Progress Tracking**: Real-time progress bars and statistics
- **Flexible Options**: Multiple download modes and source selection

## 🚀 Quick Start

### **Option 1: Interactive Launcher (Recommended)**
```bash
python launch_comprehensive_download.py
```

### **Option 2: Direct Download**
```bash
python comprehensive_london_data_downloader.py
```

### **Option 3: Test Mode**
```bash
python test_comprehensive_downloader.py
```

## 📋 Download Options

The interactive launcher provides several options:

1. **Full Download** - All sources (recommended for complete dataset)
2. **Historical Sources Only** - London Lives, Old Bailey, government records
3. **Literature Only** - Project Gutenberg books and literature
4. **Web Scraping Only** - TNA, British History Online, Connected Histories
5. **Test Mode** - Download 1-2 sources for testing
6. **Custom Selection** - Choose specific sources

## 📊 Data Sources Details

### **Primary Historical Sources**

#### **London Lives 1690-1800** 📜
- **Source**: https://www.londonlives.org/
- **Content**: Court records, parish records, poor law records, apprenticeship records
- **Format**: XML (240,000 pages)
- **Method**: Direct download + web scraping
- **License**: CC-BY-NC

#### **Old Bailey Proceedings** ⚖️
- **Source**: https://www.oldbaileyonline.org/
- **Content**: Trial accounts, criminal records, social commentary
- **Format**: XML (197,000+ cases)
- **Method**: Direct download
- **License**: Free for research

#### **The National Archives** 🏛️
- **Source**: https://www.nationalarchives.gov.uk/
- **Content**: Government correspondence, census data, taxation records
- **Format**: Digital images/PDF
- **Method**: Web scraping
- **License**: Crown Copyright

#### **British History Online** 💻
- **Source**: https://www.british-history.ac.uk/
- **Content**: Historical surveys, parliamentary papers, archival records
- **Format**: HTML/PDF
- **Method**: Web scraping
- **License**: Various

#### **UK Data Service** 📊
- **Source**: https://beta.ukdataservice.ac.uk/
- **Content**: GIS data, social and economic datasets
- **Format**: GIS/CSV
- **Method**: Web scraping
- **License**: Various

#### **Connected Histories** 🔗
- **Source**: https://www.connectedhistories.org/
- **Content**: Federated search across multiple historical resources
- **Format**: HTML/XML
- **Method**: Web scraping
- **License**: Various

### **Literature Sources**

#### **Project Gutenberg** 📚
- **Source**: https://www.gutenberg.org/
- **Content**: Public domain books and literature
- **Format**: Plain text
- **Method**: Direct download
- **License**: Public Domain

#### **Internet Archive** 📖
- **Source**: https://archive.org/
- **Content**: Historical documents and manuscripts
- **Format**: PDF/TXT
- **Method**: Direct download
- **License**: Public Domain

## 🔧 Technical Details

### **File Structure**
```
data/london_historical/
├── london_historical_corpus.txt          # Merged training corpus
├── comprehensive_download_statistics.json # Download statistics
├── london_lives_processed.txt            # London Lives data
├── old_bailey_processed.txt              # Old Bailey data
├── national_archives_processed.txt       # TNA data
├── british_history_online_processed.txt  # BHO data
├── uk_data_service_processed.txt         # UK Data Service data
├── connected_histories_processed.txt     # Connected Histories data
├── gutenberg_*.txt                       # Project Gutenberg texts
└── [additional processed files...]
```

### **Data Processing**
- **XML Processing**: Extracts text from structured XML documents
- **CSV Processing**: Combines text fields from CSV data
- **Web Scraping**: Intelligent content extraction from websites
- **Text Cleaning**: Removes headers, footers, and formatting artifacts
- **Deduplication**: Removes duplicate content across sources

### **Error Handling**
- **Retry Logic**: Automatic retry for failed downloads
- **Fallback Methods**: Multiple download methods per source
- **Progress Tracking**: Real-time progress bars and statistics
- **Error Logging**: Comprehensive error logging and reporting

## 📈 Expected Results

### **Data Volume**
- **Total Sources**: 8+ major historical sources
- **Expected Size**: 500MB - 2GB of processed text
- **Text Count**: 10,000+ individual documents
- **Time Coverage**: 1500-1850 (350 years)

### **Quality Improvements**
- **Authentic Language**: Real historical texts from the period
- **Diverse Perspectives**: Different social classes and viewpoints
- **Rich Context**: Social, political, and cultural events
- **High Quality**: Well-written historical sources

### **Model Performance**
- **Better Text Generation**: More coherent historical English
- **Improved Vocabulary**: Period-appropriate words and phrases
- **Enhanced Context**: Understanding of historical social dynamics
- **Authentic Style**: Closer to actual historical writing

## 🛠️ Installation

### **Requirements**
```bash
pip install requests beautifulsoup4 tqdm lxml
```

### **Optional Dependencies**
```bash
pip install pandas numpy  # For advanced data processing
```

## 🎯 Usage Examples

### **Basic Usage**
```python
from comprehensive_london_data_downloader import ComprehensiveLondonDataDownloader

# Initialize downloader
downloader = ComprehensiveLondonDataDownloader(time_period=(1500, 1850))

# Download all sources
downloader.download_historical_sources()
downloader.download_gutenberg_sources()

# Create merged corpus
corpus_path = downloader.create_merged_corpus()
```

### **Custom Source Selection**
```python
# Download only specific sources
downloader.historical_sources = {
    'london_lives': downloader.historical_sources['london_lives'],
    'old_bailey': downloader.historical_sources['old_bailey']
}
downloader.download_historical_sources()
```

### **Web Scraping Only**
```python
# Enable only scraping-enabled sources
scraping_sources = {k: v for k, v in downloader.historical_sources.items() 
                   if v.get('scraping_enabled', False)}
downloader.historical_sources = scraping_sources
downloader.download_historical_sources()
```

## 📊 Statistics and Monitoring

The system provides comprehensive statistics:

- **Download Statistics**: Success/failure rates, file sizes, processing times
- **Source Statistics**: Individual source performance and status
- **Error Logging**: Detailed error messages and troubleshooting info
- **Progress Tracking**: Real-time progress bars and status updates

## 🔍 Troubleshooting

### **Common Issues**

1. **Network Timeouts**: Increase timeout values in the code
2. **Rate Limiting**: Add longer delays between requests
3. **Missing Dependencies**: Install required packages
4. **Permission Errors**: Check file write permissions

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Notes

- **Respectful Scraping**: Built-in delays and rate limiting
- **License Compliance**: Respects all source licenses and terms
- **Data Quality**: Comprehensive text cleaning and validation
- **Scalability**: Easy to add new sources and methods

## 🎉 Next Steps

1. **Run the downloader**: `python launch_comprehensive_download.py`
2. **Train custom tokenizer**: `python train_custom_tokenizer.py`
3. **Prepare dataset**: `python prepare_dataset.py`
4. **Start training**: `./launch_2gpu.sh`
5. **Test generation**: `python sample_london_llm.py`

---

**Ready to build your comprehensive London Historical LLM!** 🏛️✨
