#!/usr/bin/env python3
"""
Test script for the comprehensive London data downloader
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from comprehensive_london_data_downloader import ComprehensiveLondonDataDownloader

def test_downloader():
    """Test the comprehensive downloader with a small subset"""
    print("🧪 Testing Comprehensive London Data Downloader")
    print("=" * 50)
    
    # Initialize downloader with test settings
    downloader = ComprehensiveLondonDataDownloader(
        output_dir="test_data/london_historical",
        time_period=(1500, 1850)
    )
    
    print(f"📁 Output directory: {downloader.output_dir}")
    print(f"📅 Time period: {downloader.time_period[0]}-{downloader.time_period[1]}")
    print(f"📚 Total sources configured: {len(downloader.historical_sources)}")
    
    # Test a few sources
    test_sources = ['defoe_plague', 'source_book_london', 'national_archives']
    
    print(f"\n🔬 Testing sources: {', '.join(test_sources)}")
    
    for source_key in test_sources:
        if source_key in downloader.historical_sources:
            source_info = downloader.historical_sources[source_key]
            print(f"\n📖 {source_info['name']}")
            print(f"   Description: {source_info['description']}")
            print(f"   Time Period: {source_info['time_period'][0]}-{source_info['time_period'][1]}")
            print(f"   Format: {source_info['format']}")
            print(f"   Scraping Enabled: {source_info.get('scraping_enabled', False)}")
            
            if 'search_terms' in source_info:
                print(f"   Search Terms: {', '.join(source_info['search_terms'])}")
    
    print(f"\n✅ Downloader initialized successfully!")
    print(f"💡 To run full download: python comprehensive_london_data_downloader.py")

if __name__ == "__main__":
    test_downloader()
