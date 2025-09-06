#!/usr/bin/env python3
"""
Launcher script for comprehensive London historical data download
Provides options for different download modes and sources
"""

import sys
import os
from pathlib import Path

def print_banner():
    """Print the banner"""
    print("🏛️" + "="*78 + "🏛️")
    print("🏛️" + " " * 20 + "LONDON HISTORICAL DATA DOWNLOADER" + " " * 20 + "🏛️")
    print("🏛️" + " " * 15 + "Comprehensive Historical Sources (1500-1850)" + " " * 15 + "🏛️")
    print("🏛️" + "="*78 + "🏛️")

def print_sources():
    """Print available sources"""
    print("\n📚 AVAILABLE HISTORICAL SOURCES:")
    print("=" * 50)
    
    sources = [
        ("London Lives 1690-1800", "240,000 manuscript pages from eight London archives"),
        ("Old Bailey Proceedings", "197,000+ trial accounts from London's Central Criminal Court"),
        ("The National Archives", "UK government records and correspondence"),
        ("British History Online", "Digital library of primary and secondary sources"),
        ("UK Data Service", "Social and economic data including GIS"),
        ("Connected Histories", "Federated search across multiple resources"),
        ("Project Gutenberg", "Public domain books and literature"),
        ("Internet Archive", "Historical documents and manuscripts")
    ]
    
    for i, (name, desc) in enumerate(sources, 1):
        print(f"{i:2d}. {name}")
        print(f"    {desc}")
        print()

def print_options():
    """Print download options"""
    print("🚀 DOWNLOAD OPTIONS:")
    print("=" * 30)
    print("1. Full Download - All sources (recommended)")
    print("2. Historical Sources Only - London Lives, Old Bailey, etc.")
    print("3. Literature Only - Project Gutenberg books")
    print("4. Web Scraping Only - TNA, British History Online, etc.")
    print("5. Test Mode - Download 1-2 sources for testing")
    print("6. Custom Selection - Choose specific sources")
    print("0. Exit")
    print()

def get_user_choice():
    """Get user's choice"""
    while True:
        try:
            choice = input("Enter your choice (0-6): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6']:
                return int(choice)
            else:
                print("❌ Invalid choice. Please enter 0-6.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except Exception:
            print("❌ Invalid input. Please enter a number.")

def run_download(choice):
    """Run the appropriate download based on choice"""
    from comprehensive_london_data_downloader import ComprehensiveLondonDataDownloader
    
    if choice == 0:
        print("👋 Goodbye!")
        return
    
    print(f"\n🚀 Starting download option {choice}...")
    print("=" * 50)
    
    # Initialize downloader
    downloader = ComprehensiveLondonDataDownloader(time_period=(1500, 1850))
    
    if choice == 1:  # Full download
        print("📚 Running full download of all sources...")
        downloader.download_historical_sources()
        downloader.download_gutenberg_sources()
        
    elif choice == 2:  # Historical sources only
        print("🏛️ Downloading historical sources only...")
        downloader.download_historical_sources()
        
    elif choice == 3:  # Literature only
        print("📖 Downloading literature sources only...")
        downloader.download_gutenberg_sources()
        
    elif choice == 4:  # Web scraping only
        print("🔍 Running web scraping only...")
        # Filter to scraping-enabled sources
        scraping_sources = {k: v for k, v in downloader.historical_sources.items() 
                           if v.get('scraping_enabled', False)}
        downloader.historical_sources = scraping_sources
        downloader.download_historical_sources()
        
    elif choice == 5:  # Test mode
        print("🧪 Running test mode (limited sources)...")
        # Test with just a few sources
        test_sources = ['defoe_plague', 'source_book_london']
        downloader.historical_sources = {k: v for k, v in downloader.historical_sources.items() 
                                       if k in test_sources}
        downloader.download_historical_sources()
        
    elif choice == 6:  # Custom selection
        print("🎯 Custom source selection...")
        print("\nAvailable sources:")
        for i, (key, info) in enumerate(downloader.historical_sources.items(), 1):
            print(f"{i:2d}. {info['name']}")
        
        try:
            selected = input("\nEnter source numbers (comma-separated): ").strip()
            indices = [int(x.strip()) - 1 for x in selected.split(',')]
            source_keys = list(downloader.historical_sources.keys())
            selected_sources = {source_keys[i]: downloader.historical_sources[source_keys[i]] 
                              for i in indices if 0 <= i < len(source_keys)}
            
            if selected_sources:
                downloader.historical_sources = selected_sources
                downloader.download_historical_sources()
            else:
                print("❌ No valid sources selected.")
                return
                
        except Exception as e:
            print(f"❌ Error in custom selection: {e}")
            return
    
    # Create merged corpus
    print("\n📝 Creating merged corpus...")
    corpus_path = downloader.create_merged_corpus()
    
    if corpus_path:
        print(f"✅ Corpus created: {corpus_path}")
    else:
        print("❌ Failed to create corpus")
    
    # Save statistics
    downloader.save_statistics()
    
    # Print summary
    downloader.print_summary()
    
    print(f"\n🎉 Download completed!")
    print(f"📁 Data saved to: {downloader.output_dir}")

def main():
    """Main launcher function"""
    print_banner()
    print_sources()
    print_options()
    
    choice = get_user_choice()
    run_download(choice)

if __name__ == "__main__":
    main()
