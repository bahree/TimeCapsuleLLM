# 🔄 Failed Downloads Tracking and Manual Retry System

A comprehensive system for tracking failed downloads and providing easy manual retry options for your London Historical Data Collection.

## 📋 **What This System Does**

✅ **Tracks All Failed Downloads** - Automatically logs every failed download attempt
✅ **Generates Retry Scripts** - Creates Python, curl, and wget commands for manual retry
✅ **Priority-Based Organization** - Categorizes failures by importance
✅ **Interactive Retry Helper** - Easy-to-use interface for manual retries
✅ **Comprehensive Reporting** - Detailed reports on what failed and why

## 📁 **Files Created for Failed Downloads**

### **Core Files**
- `failed_downloads_tracker.py` - Main tracking system
- `manual_retry_helper.py` - Interactive retry helper
- `failed_downloads.json` - Database of failed downloads
- `manual_retry_script.py` - Generated Python retry script

### **Command Files (Generated)**
- `manual_retry_curl.sh` - Curl commands for manual retry
- `manual_retry_wget.sh` - Wget commands for manual retry
- `manual_retry_python.py` - Python commands for manual retry

### **Report Files (Generated)**
- `failed_downloads_report.txt` - Comprehensive failure report
- `manual_retry_log.txt` - Log of manual retry attempts

## 🚀 **How to Use**

### **1. Automatic Tracking**
The system automatically tracks failed downloads when you run:
```bash
python remote_london_downloader.py
```

### **2. View Failed Downloads**
```bash
# Interactive mode
python manual_retry_helper.py

# Command line mode
python manual_retry_helper.py data/london_historical show
```

### **3. Generate Retry Commands**
```bash
# Generate all retry commands
python manual_retry_helper.py data/london_historical generate

# Generate only high priority
python manual_retry_helper.py data/london_historical generate high
```

### **4. Run Retry Script**
```bash
# Run the generated Python retry script
python manual_retry_helper.py data/london_historical run

# Or run directly
python data/london_historical/manual_retry_script.py
```

### **5. Use Generated Commands**
```bash
# Run curl commands
bash data/london_historical/manual_retry_curl.sh

# Run wget commands
bash data/london_historical/manual_retry_wget.sh
```

## 📊 **Failed Downloads Database Structure**

The `failed_downloads.json` file contains:

```json
{
  "failed_downloads": [
    {
      "id": "source_name_20240115_143022",
      "source_name": "Gutenberg: Pride and Prejudice",
      "url": "https://www.gutenberg.org/ebooks/1342",
      "error_message": "Connection timeout",
      "file_type": "txt",
      "priority": "high",
      "failed_at": "2024-01-15T14:30:22",
      "retry_count": 0,
      "last_retry": null,
      "status": "failed",
      "manual_notes": ""
    }
  ],
  "retry_attempts": {},
  "last_updated": "2024-01-15T14:30:22",
  "total_failed": 5,
  "total_retried": 0,
  "total_successful_retries": 0
}
```

## 🎯 **Priority Levels**

### **High Priority**
- Project Gutenberg downloads (literature)
- Critical historical sources
- Large files that are important for training

### **Medium Priority**
- Government records
- Archive documents
- Secondary sources

### **Low Priority**
- Optional sources
- Small files
- Non-critical documents

## 🔧 **Manual Retry Options**

### **Option 1: Python Script (Recommended)**
```bash
python data/london_historical/manual_retry_script.py
```
- **Pros**: Built-in error handling, progress tracking, automatic retry
- **Cons**: Requires Python environment

### **Option 2: Curl Commands**
```bash
bash data/london_historical/manual_retry_curl.sh
```
- **Pros**: Works on any system with curl, simple
- **Cons**: No built-in retry logic

### **Option 3: Wget Commands**
```bash
bash data/london_historical/manual_retry_wget.sh
```
- **Pros**: Works on any system with wget, simple
- **Cons**: No built-in retry logic

### **Option 4: Interactive Helper**
```bash
python manual_retry_helper.py
```
- **Pros**: User-friendly interface, step-by-step guidance
- **Cons**: Requires Python environment

## 📈 **Monitoring and Reports**

### **Real-time Monitoring**
The system provides real-time feedback:
- ✅ Successful downloads
- ❌ Failed downloads with error messages
- 🔄 Retry attempts and results
- 📊 Statistics and progress

### **Generated Reports**
- **failed_downloads_report.txt** - Comprehensive failure analysis
- **manual_retry_log.txt** - Log of all retry attempts
- **Statistics in JSON** - Machine-readable data

### **Error Categories**
- **Network Errors**: Connection timeouts, DNS failures
- **HTTP Errors**: 404 Not Found, 403 Forbidden, 500 Server Error
- **File Errors**: Permission denied, disk space
- **Data Errors**: Invalid format, parsing errors

## 🛠️ **Troubleshooting Failed Downloads**

### **Common Issues and Solutions**

1. **Connection Timeout**
   - **Solution**: Check internet connection, try again later
   - **Command**: `curl -L --connect-timeout 60 -o file.txt "URL"`

2. **404 Not Found**
   - **Solution**: URL may have changed, check source website
   - **Command**: `curl -I "URL"` (check if URL exists)

3. **403 Forbidden**
   - **Solution**: Server blocking requests, try different user agent
   - **Command**: `curl -L -H "User-Agent: Mozilla/5.0..." -o file.txt "URL"`

4. **Rate Limiting**
   - **Solution**: Add delays between requests
   - **Command**: Add `sleep 5` between commands

### **Advanced Retry Strategies**

1. **Exponential Backoff**
   ```bash
   # Try with increasing delays
   curl -L -o file.txt "URL" || sleep 5 && curl -L -o file.txt "URL" || sleep 10 && curl -L -o file.txt "URL"
   ```

2. **Different User Agents**
   ```bash
   curl -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" -o file.txt "URL"
   ```

3. **Resume Partial Downloads**
   ```bash
   curl -L -C - -o file.txt "URL"
   ```

## 📊 **Success Tracking**

The system tracks:
- **Total Failed Downloads**: Number of failed attempts
- **Retry Attempts**: Number of manual retry attempts
- **Successful Retries**: Number of successful manual retries
- **Success Rate**: Percentage of successful retries

## 🎯 **Best Practices**

### **For Manual Retry**
1. **Start with High Priority** - Focus on important sources first
2. **Check Error Messages** - Understand why downloads failed
3. **Use Appropriate Tools** - Choose the right retry method
4. **Monitor Progress** - Keep track of what's working
5. **Document Success** - Note which methods work for which sources

### **For System Maintenance**
1. **Regular Cleanup** - Remove old failed download records
2. **Update URLs** - Check if source URLs have changed
3. **Monitor Success Rates** - Track which sources are most reliable
4. **Backup Data** - Keep copies of successful downloads

## 🔍 **Example Workflow**

```bash
# 1. Run the downloader
python remote_london_downloader.py

# 2. Check what failed
python manual_retry_helper.py data/london_historical show

# 3. Generate retry commands for high priority
python manual_retry_helper.py data/london_historical generate high

# 4. Run the retry script
python manual_retry_helper.py data/london_historical run

# 5. Check results
python manual_retry_helper.py data/london_historical show
```

## 📝 **Integration with Main System**

The failed downloads tracker is automatically integrated with:
- **Remote London Downloader** - Tracks all failed downloads
- **Comprehensive Downloader** - Tracks failed downloads and web scraping
- **Enhanced Pipeline** - Full integration with error handling

## 🎉 **Benefits**

✅ **Never Lose Failed Downloads** - Everything is tracked and can be retried
✅ **Easy Manual Retry** - Multiple options for different skill levels
✅ **Priority-Based Organization** - Focus on what matters most
✅ **Comprehensive Reporting** - Know exactly what failed and why
✅ **Flexible Retry Methods** - Choose the approach that works for you
✅ **Success Tracking** - Monitor your retry success rate

---

**Ready to never lose a download again!** 🔄✨
