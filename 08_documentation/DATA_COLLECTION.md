# Data Collection Guide

This guide explains how to collect historical data for the London Historical LLM project.

## Overview

The data collection system downloads historical texts from multiple sources:

- **Project Gutenberg**: Public domain literature
- **Internet Archive**: Historical documents
- **London Lives**: 18th-century London records
- **Old Bailey Proceedings**: Court records
- **The National Archives**: Government records
- **British History Online**: Historical texts

## Quick Start

### 1. Run Data Collection
```bash
cd 02_data_collection
python download_historical_data.py
```

### 2. Check Results
```bash
ls -la data/london_historical/
```

### 3. View Statistics
```bash
cat data/london_historical/download_statistics.json
```

## Data Sources

### Project Gutenberg Sources
- **Time Period**: 1500-1850
- **Format**: Plain text (.txt)
- **Content**: Novels, historical accounts, letters
- **Examples**: Defoe's "A Journal of the Plague Year", historical surveys

### Historical Archives
- **London Lives**: 240,000 manuscript pages (1690-1800)
- **Old Bailey**: 197,000+ trial accounts (1674-1850)
- **TNA Records**: Government correspondence and records
- **British History Online**: Historical surveys and documents

## Data Processing

### Text Cleaning
The system automatically:
- Removes Project Gutenberg headers/footers
- Normalizes whitespace
- Preserves historical language patterns
- Filters by time period (1500-1850)

### File Organization
```
data/london_historical/
├── london_historical_corpus.txt    # Main training corpus
├── gutenberg_*.txt                 # Individual Gutenberg texts
├── london_lives_processed.txt      # London Lives data
├── old_bailey_processed.txt        # Old Bailey data
├── failed_downloads.json           # Failed downloads log
├── manual_retry_script.py          # Retry script
└── download_statistics.json        # Download statistics
```

## Failed Downloads

### Automatic Retry
The system automatically retries failed downloads with exponential backoff.

### Manual Retry
For persistent failures:

1. **Check failed downloads**:
   ```bash
   python manual_retry_helper.py
   ```

2. **Generate retry script**:
   ```bash
   python manual_retry_helper.py data/london_historical generate
   ```

3. **Run retry script**:
   ```bash
   python manual_retry_helper.py data/london_historical run
   ```

### Retry Commands
The system generates multiple retry options:
- Python script: `manual_retry_script.py`
- Curl commands: `manual_retry_curl.sh`
- Wget commands: `manual_retry_wget.sh`

## Configuration

### Time Period Filtering
```python
# Default: 1500-1850
downloader = LondonHistoricalDataDownloader(time_period=(1500, 1850))

# Custom period
downloader = LondonHistoricalDataDownloader(time_period=(1600, 1800))
```

### Source Selection
```python
# Enable/disable specific sources
downloader.historical_sources['defoe_plague']['enabled'] = True
downloader.gutenberg_sources = [source for source in downloader.gutenberg_sources if source['year'] >= 1600]
```

## Monitoring Progress

### Log Files
- `data_collection.log`: Detailed download logs
- `download_statistics.json`: Download statistics
- `failed_downloads.json`: Failed download details

### Progress Tracking
The system shows:
- Real-time download progress
- Success/failure counts
- File sizes and download speeds
- Estimated completion time

## Troubleshooting

### Common Issues

1. **Network Timeouts**
   - Check internet connection
   - Increase timeout values
   - Use manual retry for specific files

2. **Permission Errors**
   - Ensure write permissions to data directory
   - Run as administrator if needed

3. **Disk Space**
   - Monitor available space
   - Clean up old downloads if needed

4. **Rate Limiting**
   - The system includes delays between requests
   - Use manual retry for rate-limited sources

### Getting Help

- Check logs: `tail -f data_collection.log`
- Run diagnostics: `python 06_testing/test_system.py`
- Review failed downloads: `cat data/london_historical/failed_downloads.json`

## Data Quality

### Text Preprocessing
- Removes metadata headers
- Normalizes historical spelling
- Preserves historical language patterns
- Filters by relevance and quality

### Validation
- Checks file integrity
- Validates text content
- Ensures proper encoding
- Verifies time period relevance

## Expected Results

### Data Volume
- **Total Size**: 500MB - 2GB
- **Text Sources**: 50-200 files
- **Character Count**: 10-50 million characters
- **Time Coverage**: 350 years (1500-1850)

### Quality Metrics
- **Success Rate**: 70-90% (depending on source availability)
- **Text Quality**: High (preprocessed and validated)
- **Historical Accuracy**: Verified against source metadata
- **Language Diversity**: Covers multiple historical periods

## Next Steps

After data collection:

1. **Verify Data**: Check corpus file and statistics
2. **Train Tokenizer**: `cd 03_tokenizer && python train_tokenizer.py`
3. **Prepare Dataset**: The tokenizer will process the collected data
4. **Start Training**: `cd 04_training && python train_model.py`

## Advanced Usage

### Custom Sources
Add new data sources by modifying the `historical_sources` dictionary in the downloader script.

### Batch Processing
For large-scale collection, consider running multiple instances with different source subsets.

### Remote Execution
The system is optimized for remote server execution with robust error handling and retry mechanisms.
