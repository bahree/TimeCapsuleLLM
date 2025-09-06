#!/usr/bin/env python3
"""
Simple launcher for remote London data downloader
"""

import sys
import os
from pathlib import Path

def print_banner():
    """Print banner"""
    print("🏛️" + "="*60 + "🏛️")
    print("🏛️" + " " * 15 + "REMOTE LONDON DATA DOWNLOADER" + " " * 15 + "🏛️")
    print("🏛️" + " " * 10 + "Optimized for Remote Machine Execution" + " " * 10 + "🏛️")
    print("🏛️" + "="*60 + "🏛️")

def check_requirements():
    """Check if requirements are met"""
    print("\n🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ required")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]}")
    
    # Check required modules
    required_modules = ['requests', 'bs4', 'tqdm']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}")
    
    if missing_modules:
        print(f"\n⚠️ Missing modules: {', '.join(missing_modules)}")
        print("Install with: pip install " + " ".join(missing_modules))
        return False
    
    return True

def run_test():
    """Run the test suite"""
    print("\n🧪 Running test suite...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_remote_download.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def run_downloader():
    """Run the main downloader"""
    print("\n🚀 Starting data download...")
    
    try:
        from remote_london_downloader import main
        main()
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def main():
    """Main launcher function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please install missing modules.")
        return False
    
    # Ask user what to do
    print("\n🎯 What would you like to do?")
    print("1. Run tests only")
    print("2. Run full download")
    print("3. Run tests then download")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-3): ").strip()
            if choice in ['0', '1', '2', '3']:
                break
            else:
                print("❌ Invalid choice. Please enter 0-3.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return False
    
    choice = int(choice)
    
    if choice == 0:
        print("👋 Goodbye!")
        return True
    
    success = True
    
    if choice in [1, 3]:  # Run tests
        if not run_test():
            print("\n❌ Tests failed. Please fix issues before proceeding.")
            success = False
    
    if choice in [2, 3] and success:  # Run download
        if not run_downloader():
            print("\n❌ Download failed.")
            success = False
    
    if success:
        print("\n🎉 Operation completed successfully!")
        print("\n📁 Check the following locations:")
        print("   - data/london_historical/ (downloaded files)")
        print("   - london_downloader.log (detailed logs)")
        print("   - remote_download_statistics.json (statistics)")
    else:
        print("\n⚠️ Operation completed with errors.")
        print("Check the logs for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
