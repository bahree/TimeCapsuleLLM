"""
Test script to verify data download works
Downloads a few sample texts to test the system
"""

import os
import requests
import time
from pathlib import Path

def test_gutenberg_download():
    """Test downloading a single text from Project Gutenberg"""
    print("🧪 Testing Project Gutenberg download...")
    
    # Test with a known working text
    gutenberg_id = "1342"  # Pride and Prejudice
    title = "Pride and Prejudice"
    
    # Try different URL patterns
    urls = [
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt",
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}.txt",
        f"https://www.gutenberg.org/ebooks/{gutenberg_id}.txt.utf-8"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for i, url in enumerate(urls):
        try:
            print(f"  Trying URL {i+1}: {url}")
            response = session.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"  ✅ Success! Status: {response.status_code}")
                print(f"  📄 Content length: {len(response.text):,} characters")
                print(f"  📝 First 200 chars: {response.text[:200]}...")
                return True
            else:
                print(f"  ❌ Failed! Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    return False

def test_metadata_csv():
    """Test reading the metadata CSV"""
    print("\n📋 Testing metadata CSV...")
    
    csv_path = "london_1800_1850_v0/metadata_london.csv"
    if not os.path.exists(csv_path):
        print(f"  ❌ CSV not found: {csv_path}")
        return False
    
    try:
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"  ✅ CSV loaded successfully")
        print(f"  📊 Total rows: {len(rows)}")
        
        # Show first few rows
        print(f"  📝 First 3 rows:")
        for i, row in enumerate(rows[:3]):
            print(f"    {i+1}. {row['title']} by {row['author']} ({row['year']})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading CSV: {str(e)}")
        return False

def test_single_download():
    """Test downloading a single text using the fixed script"""
    print("\n🔬 Testing single text download...")
    
    try:
        from data_preparation_fixed import LondonDataCollector
        
        collector = LondonDataCollector()
        
        # Test with Pride and Prejudice
        text = collector.download_gutenberg_text("1342", "Pride and Prejudice", "Jane Austen", 1813)
        
        if text:
            print(f"  ✅ Download successful!")
            print(f"  📄 Text length: {len(text):,} characters")
            print(f"  📝 First 200 chars: {text[:200]}...")
            
            # Test saving
            if collector.save_text("Pride and Prejudice", "Jane Austen", 1813, text, "Project Gutenberg", "1342"):
                print(f"  ✅ Save successful!")
                return True
            else:
                print(f"  ❌ Save failed!")
                return False
        else:
            print(f"  ❌ Download failed!")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 London Historical LLM - Download Test")
    print("=" * 50)
    
    tests = [
        ("Project Gutenberg Download", test_gutenberg_download),
        ("Metadata CSV", test_metadata_csv),
        ("Single Text Download", test_single_download)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            print(f"✅ {test_name} passed")
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Download system is working.")
        print("\nYou can now run:")
        print("  python data_preparation_fixed.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify the metadata CSV exists")
        print("3. Check if Project Gutenberg is accessible")

if __name__ == "__main__":
    main()
