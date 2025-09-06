#!/usr/bin/env python3
"""
Simple test script for remote London data downloader
Tests network connectivity and basic functionality
"""

import sys
import os
import requests
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    try:
        import bs4
        print("✅ beautifulsoup4")
    except ImportError as e:
        print(f"❌ beautifulsoup4: {e}")
        return False
    
    try:
        import tqdm
        print("✅ tqdm")
    except ImportError as e:
        print(f"❌ tqdm: {e}")
        return False
    
    try:
        import xml.etree.ElementTree
        print("✅ xml (built-in)")
    except ImportError as e:
        print(f"❌ xml: {e}")
        return False
    
    return True

def test_network():
    """Test basic network connectivity"""
    print("\n🌐 Testing network connectivity...")
    
    test_urls = [
        'https://www.gutenberg.org',
        'https://archive.org',
        'https://www.google.com'
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url}: {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {str(e)}")
            return False
    
    return True

def test_downloader_init():
    """Test if the downloader can be initialized"""
    print("\n🏛️ Testing downloader initialization...")
    
    try:
        from remote_london_downloader import RemoteLondonDataDownloader
        
        downloader = RemoteLondonDataDownloader(
            output_dir="test_data",
            time_period=(1500, 1850)
        )
        
        print(f"✅ Downloader initialized")
        print(f"   Output directory: {downloader.output_dir}")
        print(f"   Time period: {downloader.time_period}")
        print(f"   Historical sources: {len(downloader.historical_sources)}")
        print(f"   Gutenberg sources: {len(downloader.gutenberg_sources)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Downloader initialization failed: {str(e)}")
        return False

def test_single_download():
    """Test downloading a single small file"""
    print("\n📥 Testing single file download...")
    
    try:
        from remote_london_downloader import RemoteLondonDataDownloader
        
        downloader = RemoteLondonDataDownloader(
            output_dir="test_data",
            time_period=(1500, 1850)
        )
        
        # Test with a small, reliable source
        test_url = "https://www.gutenberg.org/files/376/376-0.txt"  # Defoe's Plague Year
        test_filename = "test_download.txt"
        
        print(f"   Downloading: {test_url}")
        file_path = downloader.download_file_with_retry(
            test_url, 
            test_filename, 
            "Test Download"
        )
        
        if file_path and Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            print(f"✅ Download successful: {file_path} ({file_size} bytes)")
            return True
        else:
            print("❌ Download failed")
            return False
            
    except Exception as e:
        print(f"❌ Download test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Remote London Downloader - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Network Test", test_network),
        ("Downloader Init Test", test_downloader_init),
        ("Single Download Test", test_single_download)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to run the full downloader.")
        print("\n💡 Next steps:")
        print("   1. Run: python remote_london_downloader.py")
        print("   2. Check: data/london_historical/ for downloaded files")
        print("   3. Check: london_downloader.log for detailed logs")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   - Install missing packages: pip install requests beautifulsoup4 tqdm")
        print("   - Check internet connection")
        print("   - Check firewall settings")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
