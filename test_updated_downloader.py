#!/usr/bin/env python3
"""
Test the updated downloader with failed downloads tracking
"""

import sys
from pathlib import Path

def test_updated_downloader():
    """Test the updated downloader"""
    print("🧪 Testing Updated Downloader with Failed Downloads Tracking")
    print("=" * 70)
    
    try:
        from remote_london_downloader import RemoteLondonDataDownloader
        
        # Initialize downloader
        downloader = RemoteLondonDataDownloader(
            output_dir="test_data/london_historical",
            time_period=(1500, 1850)
        )
        
        print("✅ Downloader initialized")
        print(f"   Output directory: {downloader.output_dir}")
        print(f"   Time period: {downloader.time_period}")
        print(f"   Historical sources: {len(downloader.historical_sources)}")
        print(f"   Gutenberg sources: {len(downloader.gutenberg_sources)}")
        
        # Test failed downloads tracker
        print("\n🔄 Testing failed downloads tracker...")
        
        # Add a test failed download
        downloader.failed_tracker.add_failed_download(
            "Test Source",
            "https://example.com/test.txt",
            "Test error message",
            "txt",
            "high"
        )
        
        # Check if tracker is working
        failed_downloads = downloader.failed_tracker.get_failed_downloads()
        print(f"   Failed downloads tracked: {len(failed_downloads)}")
        
        if failed_downloads:
            print("   ✅ Failed downloads tracker is working!")
            for download in failed_downloads:
                print(f"     - {download['source_name']}: {download['error_message']}")
        else:
            print("   ❌ Failed downloads tracker not working")
        
        # Test generating reports
        print("\n📊 Testing report generation...")
        
        retry_script = downloader.failed_tracker.generate_retry_script()
        if retry_script:
            print(f"   ✅ Retry script: {retry_script}")
        
        curl_commands = downloader.failed_tracker.generate_curl_commands()
        if curl_commands:
            print(f"   ✅ Curl commands: {curl_commands}")
        
        report = downloader.failed_tracker.generate_retry_report()
        if report:
            print(f"   ✅ Report: {report}")
        
        print("\n✅ Updated downloader test completed!")
        print("\n💡 Now you can run the full downloader:")
        print("   python remote_london_downloader.py")
        print("\n💡 And then check failed downloads:")
        print("   python manual_retry_helper.py")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_downloader()
