#!/usr/bin/env python3
"""
Failed Downloads Tracker and Manual Retry System
Tracks failed downloads and provides easy manual retry options
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

class FailedDownloadsTracker:
    def __init__(self, data_dir="data/london_historical"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.failed_downloads_file = self.data_dir / "failed_downloads.json"
        self.retry_log_file = self.data_dir / "manual_retry_log.txt"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Load existing failed downloads
        self.failed_downloads = self._load_failed_downloads()
    
    def _load_failed_downloads(self) -> Dict[str, Any]:
        """Load existing failed downloads from file"""
        if self.failed_downloads_file.exists():
            try:
                with open(self.failed_downloads_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading failed downloads: {e}")
        
        return {
            'failed_downloads': [],
            'retry_attempts': {},
            'last_updated': datetime.now().isoformat(),
            'total_failed': 0,
            'total_retried': 0,
            'total_successful_retries': 0
        }
    
    def add_failed_download(self, source_name: str, url: str, error_message: str, 
                          file_type: str = "unknown", priority: str = "medium"):
        """Add a failed download to the tracker"""
        failed_download = {
            'id': f"{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'source_name': source_name,
            'url': url,
            'error_message': error_message,
            'file_type': file_type,
            'priority': priority,
            'failed_at': datetime.now().isoformat(),
            'retry_count': 0,
            'last_retry': None,
            'status': 'failed',
            'manual_notes': ''
        }
        
        self.failed_downloads['failed_downloads'].append(failed_download)
        self.failed_downloads['total_failed'] += 1
        self.failed_downloads['last_updated'] = datetime.now().isoformat()
        
        self._save_failed_downloads()
        self.logger.info(f"Added failed download: {source_name} - {url}")
    
    def get_failed_downloads(self, priority: Optional[str] = None, 
                           file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get failed downloads with optional filtering"""
        failed = self.failed_downloads['failed_downloads']
        
        if priority:
            failed = [f for f in failed if f['priority'] == priority]
        
        if file_type:
            failed = [f for f in failed if f['file_type'] == file_type]
        
        return failed
    
    def get_retry_candidates(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """Get downloads that can be retried"""
        return [f for f in self.failed_downloads['failed_downloads'] 
                if f['retry_count'] < max_retries and f['status'] == 'failed']
    
    def mark_retry_attempt(self, download_id: str, success: bool, notes: str = ""):
        """Mark a retry attempt for a failed download"""
        for download in self.failed_downloads['failed_downloads']:
            if download['id'] == download_id:
                download['retry_count'] += 1
                download['last_retry'] = datetime.now().isoformat()
                
                if success:
                    download['status'] = 'successful_retry'
                    self.failed_downloads['total_successful_retries'] += 1
                    self.logger.info(f"Successful retry: {download['source_name']}")
                else:
                    self.logger.warning(f"Retry failed: {download['source_name']}")
                
                if notes:
                    download['manual_notes'] = notes
                
                break
        
        self.failed_downloads['total_retried'] += 1
        self._save_failed_downloads()
    
    def generate_retry_script(self, output_file: str = "manual_retry_script.py") -> str:
        """Generate a Python script for manual retry attempts"""
        retry_candidates = self.get_retry_candidates()
        
        if not retry_candidates:
            self.logger.info("No retry candidates found")
            return None
        
        script_content = f'''#!/usr/bin/env python3
"""
Manual Retry Script for Failed Downloads
Generated on {datetime.now().isoformat()}
"""

import requests
import os
from pathlib import Path
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_file(url, filename, source_name):
    """Download a file with error handling"""
    try:
        logger.info(f"Downloading {{source_name}}: {{url}}")
        
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # Create output directory
        output_dir = Path("data/london_historical/manual_retries")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = output_dir / filename
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✅ Successfully downloaded: {{file_path}}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"❌ Failed to download {{source_name}}: {{str(e)}}")
        return None

def main():
    """Manual retry attempts for failed downloads"""
    logger.info("🔄 Starting manual retry attempts")
    
    retry_attempts = [
'''
        
        # Add retry attempts for each failed download
        for download in retry_candidates:
            script_content += f'''        {{
            'source_name': '{download['source_name']}',
            'url': '{download['url']}',
            'filename': '{download['source_name'].replace(" ", "_").lower()}_manual_retry.{download['file_type']}',
            'priority': '{download['priority']}',
            'error_message': '{download['error_message']}'
        }},
'''
        
        script_content += '''    ]
    
    successful_downloads = []
    failed_downloads = []
    
    for attempt in retry_attempts:
        logger.info(f"\\n🔄 Retrying: {attempt['source_name']}")
        logger.info(f"   URL: {attempt['url']}")
        logger.info(f"   Previous error: {attempt['error_message']}")
        
        result = download_file(
            attempt['url'],
            attempt['filename'],
            attempt['source_name']
        )
        
        if result:
            successful_downloads.append(attempt)
            logger.info(f"✅ Success: {attempt['source_name']}")
        else:
            failed_downloads.append(attempt)
            logger.warning(f"❌ Still failed: {attempt['source_name']}")
        
        # Delay between downloads
        time.sleep(2)
    
    # Summary
    logger.info(f"\\n📊 Manual Retry Summary:")
    logger.info(f"   Successful: {len(successful_downloads)}")
    logger.info(f"   Still failed: {len(failed_downloads)}")
    
    if successful_downloads:
        logger.info(f"\\n✅ Successful downloads:")
        for download in successful_downloads:
            logger.info(f"   - {download['source_name']}")
    
    if failed_downloads:
        logger.info(f"\\n❌ Still failed downloads:")
        for download in failed_downloads:
            logger.info(f"   - {download['source_name']}: {download['error_message']}")

if __name__ == "__main__":
    main()
'''
        
        # Save the script
        script_path = self.data_dir / output_file
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        self.logger.info(f"Generated retry script: {script_path}")
        return str(script_path)
    
    def generate_curl_commands(self, output_file: str = "manual_retry_commands.txt") -> str:
        """Generate curl commands for manual retry attempts"""
        retry_candidates = self.get_retry_candidates()
        
        if not retry_candidates:
            self.logger.info("No retry candidates found")
            return None
        
        curl_commands = []
        curl_commands.append("# Manual Retry Commands for Failed Downloads")
        curl_commands.append(f"# Generated on {datetime.now().isoformat()}")
        curl_commands.append("")
        
        for download in retry_candidates:
            filename = f"{download['source_name'].replace(' ', '_').lower()}_manual_retry.{download['file_type']}"
            
            curl_commands.append(f"# {download['source_name']}")
            curl_commands.append(f"# Error: {download['error_message']}")
            curl_commands.append(f"# Priority: {download['priority']}")
            curl_commands.append(f"curl -L -o \"{filename}\" \"{download['url']}\"")
            curl_commands.append("")
        
        # Save the commands
        commands_path = self.data_dir / output_file
        with open(commands_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(curl_commands))
        
        self.logger.info(f"Generated curl commands: {commands_path}")
        return str(commands_path)
    
    def generate_wget_commands(self, output_file: str = "manual_retry_wget.txt") -> str:
        """Generate wget commands for manual retry attempts"""
        retry_candidates = self.get_retry_candidates()
        
        if not retry_candidates:
            self.logger.info("No retry candidates found")
            return None
        
        wget_commands = []
        wget_commands.append("# Manual Retry Commands for Failed Downloads (wget)")
        wget_commands.append(f"# Generated on {datetime.now().isoformat()}")
        wget_commands.append("")
        
        for download in retry_candidates:
            filename = f"{download['source_name'].replace(' ', '_').lower()}_manual_retry.{download['file_type']}"
            
            wget_commands.append(f"# {download['source_name']}")
            wget_commands.append(f"# Error: {download['error_message']}")
            wget_commands.append(f"# Priority: {download['priority']}")
            wget_commands.append(f"wget -O \"{filename}\" \"{download['url']}\"")
            wget_commands.append("")
        
        # Save the commands
        commands_path = self.data_dir / output_file
        with open(commands_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(wget_commands))
        
        self.logger.info(f"Generated wget commands: {commands_path}")
        return str(commands_path)
    
    def generate_retry_report(self, output_file: str = "failed_downloads_report.txt") -> str:
        """Generate a comprehensive report of failed downloads"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("FAILED DOWNLOADS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append(f"Total Failed Downloads: {self.failed_downloads['total_failed']}")
        report_lines.append(f"Total Retry Attempts: {self.failed_downloads['total_retried']}")
        report_lines.append(f"Successful Retries: {self.failed_downloads['total_successful_retries']}")
        report_lines.append("")
        
        # Group by priority
        by_priority = {}
        for download in self.failed_downloads['failed_downloads']:
            priority = download['priority']
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(download)
        
        for priority in ['high', 'medium', 'low']:
            if priority in by_priority:
                report_lines.append(f"\\n{priority.upper()} PRIORITY FAILED DOWNLOADS:")
                report_lines.append("-" * 50)
                
                for download in by_priority[priority]:
                    report_lines.append(f"\\nSource: {download['source_name']}")
                    report_lines.append(f"URL: {download['url']}")
                    report_lines.append(f"Error: {download['error_message']}")
                    report_lines.append(f"Failed At: {download['failed_at']}")
                    report_lines.append(f"Retry Count: {download['retry_count']}")
                    report_lines.append(f"Status: {download['status']}")
                    if download['manual_notes']:
                        report_lines.append(f"Notes: {download['manual_notes']}")
                    report_lines.append("")
        
        # Summary by file type
        by_file_type = {}
        for download in self.failed_downloads['failed_downloads']:
            file_type = download['file_type']
            if file_type not in by_file_type:
                by_file_type[file_type] = 0
            by_file_type[file_type] += 1
        
        if by_file_type:
            report_lines.append("\\nFAILED DOWNLOADS BY FILE TYPE:")
            report_lines.append("-" * 40)
            for file_type, count in by_file_type.items():
                report_lines.append(f"{file_type}: {count}")
        
        report_lines.append("\\n" + "=" * 80)
        
        # Save the report
        report_path = self.data_dir / output_file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        self.logger.info(f"Generated retry report: {report_path}")
        return str(report_path)
    
    def _save_failed_downloads(self):
        """Save failed downloads to file"""
        try:
            with open(self.failed_downloads_file, 'w', encoding='utf-8') as f:
                json.dump(self.failed_downloads, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving failed downloads: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of failed downloads"""
        return {
            'total_failed': self.failed_downloads['total_failed'],
            'total_retried': self.failed_downloads['total_retried'],
            'total_successful_retries': self.failed_downloads['total_successful_retries'],
            'retry_success_rate': (
                self.failed_downloads['total_successful_retries'] / 
                max(1, self.failed_downloads['total_retried']) * 100
            ),
            'pending_retries': len(self.get_retry_candidates()),
            'last_updated': self.failed_downloads['last_updated']
        }

def main():
    """Test the failed downloads tracker"""
    print("🔄 Failed Downloads Tracker - Test")
    print("=" * 50)
    
    tracker = FailedDownloadsTracker()
    
    # Add some test failed downloads
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
    
    # Generate reports
    print("\\n📊 Generating reports...")
    
    script_path = tracker.generate_retry_script()
    if script_path:
        print(f"✅ Retry script: {script_path}")
    
    curl_path = tracker.generate_curl_commands()
    if curl_path:
        print(f"✅ Curl commands: {curl_path}")
    
    wget_path = tracker.generate_wget_commands()
    if wget_path:
        print(f"✅ Wget commands: {wget_path}")
    
    report_path = tracker.generate_retry_report()
    if report_path:
        print(f"✅ Retry report: {report_path}")
    
    # Show summary
    summary = tracker.get_summary()
    print(f"\\n📈 Summary:")
    print(f"   Total Failed: {summary['total_failed']}")
    print(f"   Pending Retries: {summary['pending_retries']}")
    print(f"   Retry Success Rate: {summary['retry_success_rate']:.1f}%")

if __name__ == "__main__":
    main()
