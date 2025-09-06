#!/usr/bin/env python3
"""
Test script for failed downloads tracking
"""

import sys
from pathlib import Path
from failed_downloads_tracker import FailedDownloadsTracker

def test_failed_downloads_tracker():
    """Test the failed downloads tracker"""
    print("🧪 Testing Failed Downloads Tracker")
    print("=" * 50)
    
    # Initialize tracker
    tracker = FailedDownloadsTracker(data_dir="test_data")
    
    # Add some test failed downloads
    print("📝 Adding test failed downloads...")
    
    tracker.add_failed_download(
        "Test Source 1",
        "https://example.com/file1.txt",
        "Connection timeout",
        "txt",
        "high"
    )
    
    tracker.add_failed_download(
        "Test Source 2", 
        "https://example.com/file2.xml",
        "404 Not Found",
        "xml",
        "medium"
    )
    
    tracker.add_failed_download(
        "Test Source 3",
        "https://example.com/file3.pdf",
        "Outside time period (1890 not in 1500-1850)",
        "pdf",
        "low"
    )
    
    # Show failed downloads
    print("\n📋 Failed Downloads:")
    failed = tracker.get_failed_downloads()
    for i, download in enumerate(failed, 1):
        print(f"{i}. {download['source_name']}")
        print(f"   URL: {download['url']}")
        print(f"   Error: {download['error_message']}")
        print(f"   Priority: {download['priority']}")
        print()
    
    # Generate retry script
    print("🔄 Generating retry script...")
    retry_script = tracker.generate_retry_script()
    if retry_script:
        print(f"✅ Retry script: {retry_script}")
    
    # Generate curl commands
    print("🔄 Generating curl commands...")
    curl_commands = tracker.generate_curl_commands()
    if curl_commands:
        print(f"✅ Curl commands: {curl_commands}")
    
    # Generate report
    print("📊 Generating report...")
    report = tracker.generate_retry_report()
    if report:
        print(f"✅ Report: {report}")
    
    # Show summary
    summary = tracker.get_summary()
    print(f"\n📈 Summary:")
    print(f"   Total failed: {summary['total_failed']}")
    print(f"   Pending retries: {summary['pending_retries']}")
    print(f"   Retry success rate: {summary['retry_success_rate']:.1f}%")
    
    print("\n✅ Failed downloads tracker test completed!")

if __name__ == "__main__":
    test_failed_downloads_tracker()
