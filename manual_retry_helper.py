#!/usr/bin/env python3
"""
Manual Retry Helper for Failed Downloads
Provides easy ways to retry failed downloads manually
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualRetryHelper:
    def __init__(self, data_dir="data/london_historical"):
        self.data_dir = Path(data_dir)
        self.failed_downloads_file = self.data_dir / "failed_downloads.json"
        
        if not self.failed_downloads_file.exists():
            logger.error(f"Failed downloads file not found: {self.failed_downloads_file}")
            logger.info("Run the downloader first to generate failed downloads data")
            sys.exit(1)
        
        # Load failed downloads
        with open(self.failed_downloads_file, 'r', encoding='utf-8') as f:
            self.failed_data = json.load(f)
    
    def show_failed_downloads(self):
        """Show all failed downloads"""
        print("🔄 Failed Downloads Summary")
        print("=" * 50)
        
        failed_downloads = self.failed_data.get('failed_downloads', [])
        
        if not failed_downloads:
            print("✅ No failed downloads found!")
            return
        
        print(f"Total failed downloads: {len(failed_downloads)}")
        print()
        
        # Group by priority
        by_priority = {'high': [], 'medium': [], 'low': []}
        for download in failed_downloads:
            priority = download.get('priority', 'medium')
            by_priority[priority].append(download)
        
        for priority in ['high', 'medium', 'low']:
            if by_priority[priority]:
                print(f"\n{priority.upper()} PRIORITY ({len(by_priority[priority])} downloads):")
                print("-" * 40)
                
                for i, download in enumerate(by_priority[priority], 1):
                    print(f"{i:2d}. {download['source_name']}")
                    print(f"    URL: {download['url']}")
                    print(f"    Error: {download['error_message']}")
                    print(f"    Retry count: {download.get('retry_count', 0)}")
                    print(f"    Status: {download.get('status', 'failed')}")
                    print()
    
    def generate_retry_commands(self, priority=None, max_commands=10):
        """Generate retry commands for failed downloads"""
        failed_downloads = self.failed_data.get('failed_downloads', [])
        
        if priority:
            failed_downloads = [f for f in failed_downloads if f.get('priority') == priority]
        
        if not failed_downloads:
            print("No failed downloads found for the specified criteria")
            return
        
        print(f"🔄 Generating retry commands for {len(failed_downloads)} failed downloads")
        print("=" * 60)
        
        # Generate curl commands
        curl_commands = []
        wget_commands = []
        python_commands = []
        
        for i, download in enumerate(failed_downloads[:max_commands], 1):
            source_name = download['source_name']
            url = download['url']
            file_type = download.get('file_type', 'txt')
            filename = f"{source_name.replace(' ', '_').lower()}_manual_retry.{file_type}"
            
            print(f"\n{i}. {source_name}")
            print(f"   URL: {url}")
            print(f"   Error: {download['error_message']}")
            
            # Curl command
            curl_cmd = f'curl -L -o "{filename}" "{url}"'
            curl_commands.append(curl_cmd)
            print(f"   Curl: {curl_cmd}")
            
            # Wget command
            wget_cmd = f'wget -O "{filename}" "{url}"'
            wget_commands.append(wget_cmd)
            print(f"   Wget: {wget_cmd}")
            
            # Python command
            python_cmd = f'python -c "import requests; r=requests.get(\'{url}\'); open(\'{filename}\', \'wb\').write(r.content)"'
            python_commands.append(python_cmd)
            print(f"   Python: {python_cmd}")
        
        # Save commands to files
        self._save_commands_to_file(curl_commands, "manual_retry_curl.sh")
        self._save_commands_to_file(wget_commands, "manual_retry_wget.sh")
        self._save_commands_to_file(python_commands, "manual_retry_python.py")
        
        print(f"\n✅ Commands saved to files:")
        print(f"   - manual_retry_curl.sh")
        print(f"   - manual_retry_wget.sh")
        print(f"   - manual_retry_python.py")
    
    def _save_commands_to_file(self, commands, filename):
        """Save commands to a file"""
        file_path = self.data_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"# Manual retry commands generated on {datetime.now().isoformat()}\n")
            f.write(f"# Total commands: {len(commands)}\n\n")
            
            for i, cmd in enumerate(commands, 1):
                f.write(f"# Command {i}\n")
                f.write(f"{cmd}\n")
                f.write(f"echo \"Completed command {i}\"\n")
                f.write(f"sleep 2\n\n")
        
        # Make executable
        os.chmod(file_path, 0o755)
    
    def run_retry_script(self, script_name="manual_retry_script.py"):
        """Run the generated retry script"""
        script_path = self.data_dir / script_name
        
        if not script_path.exists():
            logger.error(f"Retry script not found: {script_path}")
            logger.info("Generate the retry script first")
            return
        
        print(f"🚀 Running retry script: {script_path}")
        print("=" * 50)
        
        try:
            result = subprocess.run([sys.executable, str(script_path)], 
                                  capture_output=True, text=True, timeout=1800)
            
            print("STDOUT:")
            print(result.stdout)
            
            if result.stderr:
                print("\nSTDERR:")
                print(result.stderr)
            
            if result.returncode == 0:
                print("\n✅ Retry script completed successfully!")
            else:
                print(f"\n❌ Retry script failed with return code: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            print("\n⏰ Retry script timed out (30 minutes)")
        except Exception as e:
            print(f"\n❌ Error running retry script: {str(e)}")
    
    def interactive_retry(self):
        """Interactive retry mode"""
        failed_downloads = self.failed_data.get('failed_downloads', [])
        
        if not failed_downloads:
            print("✅ No failed downloads found!")
            return
        
        print("🔄 Interactive Retry Mode")
        print("=" * 30)
        
        while True:
            print(f"\nFound {len(failed_downloads)} failed downloads")
            print("Options:")
            print("1. Show all failed downloads")
            print("2. Show high priority only")
            print("3. Generate retry commands")
            print("4. Run retry script")
            print("5. Exit")
            
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == '1':
                    self.show_failed_downloads()
                elif choice == '2':
                    high_priority = [f for f in failed_downloads if f.get('priority') == 'high']
                    if high_priority:
                        print(f"\nHIGH PRIORITY FAILED DOWNLOADS ({len(high_priority)}):")
                        for i, download in enumerate(high_priority, 1):
                            print(f"{i}. {download['source_name']}")
                            print(f"   URL: {download['url']}")
                            print(f"   Error: {download['error_message']}")
                    else:
                        print("No high priority failed downloads found")
                elif choice == '3':
                    priority = input("Enter priority filter (high/medium/low) or press Enter for all: ").strip()
                    priority = priority if priority in ['high', 'medium', 'low'] else None
                    self.generate_retry_commands(priority=priority)
                elif choice == '4':
                    self.run_retry_script()
                elif choice == '5':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def main():
    """Main function"""
    print("🔄 Manual Retry Helper for Failed Downloads")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = "data/london_historical"
    
    helper = ManualRetryHelper(data_dir)
    
    if len(sys.argv) > 2:
        command = sys.argv[2]
        
        if command == "show":
            helper.show_failed_downloads()
        elif command == "generate":
            priority = sys.argv[3] if len(sys.argv) > 3 else None
            helper.generate_retry_commands(priority=priority)
        elif command == "run":
            script_name = sys.argv[3] if len(sys.argv) > 3 else "manual_retry_script.py"
            helper.run_retry_script(script_name)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: show, generate, run")
    else:
        # Interactive mode
        helper.interactive_retry()

if __name__ == "__main__":
    main()
