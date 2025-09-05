"""
Fix data download issues and provide comprehensive testing
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_internet_connection():
    """Check if internet connection is working"""
    print("🌐 Checking internet connection...")
    
    try:
        response = requests.get("https://www.gutenberg.org", timeout=10)
        if response.status_code == 200:
            print("✅ Internet connection working")
            print("✅ Project Gutenberg accessible")
            return True
        else:
            print(f"❌ Project Gutenberg returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Internet connection failed: {str(e)}")
        return False

def check_metadata_file():
    """Check if metadata file exists and is readable"""
    print("\n📋 Checking metadata file...")
    
    csv_path = "london_1800_1850_v0/metadata_london.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Metadata file not found: {csv_path}")
        return False
    
    try:
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"✅ Metadata file found")
        print(f"📊 Total texts: {len(rows)}")
        
        # Count texts with Gutenberg IDs
        gutenberg_texts = [row for row in rows if row['gutenberg_id'] and row['gutenberg_id'] != '']
        print(f"📚 Texts with Gutenberg IDs: {len(gutenberg_texts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading metadata: {str(e)}")
        return False

def test_single_download():
    """Test downloading a single text"""
    print("\n🔬 Testing single text download...")
    
    try:
        # Test with a known working text
        gutenberg_id = "1342"  # Pride and Prejudice
        url = f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt"
        
        print(f"Testing download from: {url}")
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            print(f"✅ Download successful!")
            print(f"📄 Content length: {len(response.text):,} characters")
            return True
        else:
            print(f"❌ Download failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Download test failed: {str(e)}")
        return False

def install_missing_dependencies():
    """Install any missing dependencies"""
    print("\n📦 Checking dependencies...")
    
    required_packages = ['requests', 'beautifulsoup4', 'tqdm']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} missing")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def run_fixed_download():
    """Run the fixed data preparation script"""
    print("\n🚀 Running fixed data preparation...")
    
    try:
        result = subprocess.run([sys.executable, "data_preparation_fixed.py"], 
                              capture_output=True, text=True, timeout=1800)  # 30 minute timeout
        
        if result.returncode == 0:
            print("✅ Data preparation completed successfully!")
            print("📊 Output:")
            print(result.stdout)
            return True
        else:
            print("❌ Data preparation failed!")
            print("📊 Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Data preparation timed out (30 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error running data preparation: {str(e)}")
        return False

def check_results():
    """Check if data was downloaded successfully"""
    print("\n🔍 Checking download results...")
    
    data_dir = Path("london_data")
    if not data_dir.exists():
        print("❌ Data directory not created")
        return False
    
    # Check for individual text files
    text_files = list(data_dir.glob("*.txt"))
    if not text_files:
        print("❌ No text files found")
        return False
    
    print(f"✅ Found {len(text_files)} text files")
    
    # Check for merged corpus
    corpus_file = data_dir / "london_corpus_merged.txt"
    if not corpus_file.exists():
        print("❌ Merged corpus not found")
        return False
    
    print(f"✅ Merged corpus found: {corpus_file}")
    print(f"📄 Corpus size: {corpus_file.stat().st_size / (1024*1024):.1f} MB")
    
    # Check for statistics
    stats_file = data_dir / "download_statistics.json"
    if stats_file.exists():
        print(f"✅ Download statistics found: {stats_file}")
    
    return True

def main():
    """Main fix function"""
    print("🔧 London Historical LLM - Data Download Fix")
    print("=" * 50)
    
    # Step 1: Check internet connection
    if not check_internet_connection():
        print("\n❌ Internet connection issues. Please check your connection.")
        return False
    
    # Step 2: Check metadata file
    if not check_metadata_file():
        print("\n❌ Metadata file issues. Please check the file exists.")
        return False
    
    # Step 3: Test single download
    if not test_single_download():
        print("\n❌ Single download test failed. There may be network issues.")
        return False
    
    # Step 4: Install dependencies
    if not install_missing_dependencies():
        print("\n❌ Dependency installation failed.")
        return False
    
    # Step 5: Run fixed download
    if not run_fixed_download():
        print("\n❌ Data preparation failed.")
        return False
    
    # Step 6: Check results
    if not check_results():
        print("\n❌ Download results check failed.")
        return False
    
    print("\n🎉 Data download fix completed successfully!")
    print("\nNext steps:")
    print("1. Run: python train_tokenizer_london.py")
    print("2. Run: python train_london_llm.py")
    print("3. Generate text: python sample_london_llm.py")
    
    return True

if __name__ == "__main__":
    main()
