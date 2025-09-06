#!/usr/bin/env python3
"""
London Historical Data Downloader
Consolidated system for downloading historical data from multiple sources
"""

import os
import sys
import requests
import time
import re
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import logging
from datetime import datetime
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LondonHistoricalDataDownloader:
    def __init__(self, output_dir="data/london_historical", time_period=(1500, 1850)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.time_period = time_period
        
        # Enhanced session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Enhanced headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Statistics tracking
        self.stats = {
            'total_attempted': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size_mb': 0,
            'sources_processed': 0,
            'errors': [],
            'source_stats': {},
            'start_time': datetime.now().isoformat()
        }
        
        # Failed downloads tracker
        self.failed_downloads = []
        
        # Historical data sources
        self.historical_sources = {
            'defoe_plague': {
                'name': 'A Journal of the Plague Year',
                'description': 'Daniel Defoe\'s account of the 1665 Great Plague in London',
                'time_period': (1665, 1665),
                'format': 'TXT',
                'url': 'https://www.gutenberg.org/ebooks/376',
                'download_url': 'https://www.gutenberg.org/files/376/376-0.txt',
                'license': 'Public Domain',
                'type': 'historical_narrative',
                'priority': 'high'
            },
            'source_book_london': {
                'name': 'Source Book of London History',
                'description': 'Curated extracts from original sources on London\'s development',
                'time_period': (1500, 1800),
                'format': 'TXT',
                'url': 'https://www.gutenberg.org/ebooks/51175',
                'download_url': 'https://www.gutenberg.org/files/51175/51175-0.txt',
                'license': 'Public Domain',
                'type': 'historical_compilation',
                'priority': 'high'
            },
            'historical_collections': {
                'name': 'Historical Collections of a Citizen of London',
                'description': 'Poems and chronicles on London events from 15th century',
                'time_period': (1400, 1500),
                'format': 'PDF',
                'url': 'https://archive.org/details/historicalcollec00gairrich',
                'download_url': 'https://archive.org/download/historicalcollec00gairrich/historicalcollec00gairrich.pdf',
                'license': 'Public Domain',
                'type': 'historical_manuscript',
                'priority': 'medium'
            }
        }
        
        # Project Gutenberg sources (1500-1850)
        self.gutenberg_sources = [
            {'id': '1342', 'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'year': 1813, 'type': 'novel'},
            {'id': '46', 'title': 'A Christmas Carol', 'author': 'Charles Dickens', 'year': 1843, 'type': 'novella'},
            {'id': '730', 'title': 'Oliver Twist', 'author': 'Charles Dickens', 'year': 1838, 'type': 'novel'},
            {'id': '768', 'title': 'Wuthering Heights', 'author': 'Emily Brontë', 'year': 1847, 'type': 'novel'},
            {'id': '1260', 'title': 'Jane Eyre', 'author': 'Charlotte Brontë', 'year': 1847, 'type': 'novel'},
            {'id': '84', 'title': 'Frankenstein', 'author': 'Mary Shelley', 'year': 1818, 'type': 'gothic_novel'},
            {'id': '11', 'title': 'Alice\'s Adventures in Wonderland', 'author': 'Lewis Carroll', 'year': 1865, 'type': 'children_novel'},
            {'id': '74', 'title': 'The Adventures of Tom Sawyer', 'author': 'Mark Twain', 'year': 1876, 'type': 'novel'},
            {'id': '76', 'title': 'Adventures of Huckleberry Finn', 'author': 'Mark Twain', 'year': 1884, 'type': 'novel'},
            {'id': '345', 'title': 'Dracula', 'author': 'Bram Stoker', 'year': 1897, 'type': 'gothic_novel'},
            {'id': '174', 'title': 'The Picture of Dorian Gray', 'author': 'Oscar Wilde', 'year': 1890, 'type': 'gothic_novel'},
            {'id': '5144', 'title': 'The Strange Case of Dr. Jekyll and Mr. Hyde', 'author': 'Robert Louis Stevenson', 'year': 1886, 'type': 'gothic_novel'},
            {'id': '5145', 'title': 'Treasure Island', 'author': 'Robert Louis Stevenson', 'year': 1883, 'type': 'adventure_novel'},
            {'id': '5146', 'title': 'Kidnapped', 'author': 'Robert Louis Stevenson', 'year': 1886, 'type': 'adventure_novel'},
            {'id': '5147', 'title': 'The Black Arrow', 'author': 'Robert Louis Stevenson', 'year': 1888, 'type': 'historical_novel'},
            {'id': '5148', 'title': 'The Master of Ballantrae', 'author': 'Robert Louis Stevenson', 'year': 1889, 'type': 'adventure_novel'},
            {'id': '5149', 'title': 'The Wrecker', 'author': 'Robert Louis Stevenson', 'year': 1892, 'type': 'adventure_novel'},
            {'id': '5150', 'title': 'Catriona', 'author': 'Robert Louis Stevenson', 'year': 1893, 'type': 'adventure_novel'},
            {'id': '5151', 'title': 'The Ebb-Tide', 'author': 'Robert Louis Stevenson', 'year': 1894, 'type': 'adventure_novel'},
            {'id': '5152', 'title': 'Weir of Hermiston', 'author': 'Robert Louis Stevenson', 'year': 1896, 'type': 'historical_novel'},
            {'id': '5153', 'title': 'St. Ives', 'author': 'Robert Louis Stevenson', 'year': 1897, 'type': 'adventure_novel'},
            {'id': '5154', 'title': 'The Beach of Falesá', 'author': 'Robert Louis Stevenson', 'year': 1892, 'type': 'adventure_novel'},
            {'id': '5155', 'title': 'The Bottle Imp', 'author': 'Robert Louis Stevenson', 'year': 1891, 'type': 'short_story'},
            {'id': '5156', 'title': 'The Isle of Voices', 'author': 'Robert Louis Stevenson', 'year': 1893, 'type': 'short_story'},
            {'id': '5157', 'title': 'The Waif Woman', 'author': 'Robert Louis Stevenson', 'year': 1893, 'type': 'short_story'},
            {'id': '5158', 'title': 'The Story of a Lie', 'author': 'Robert Louis Stevenson', 'year': 1879, 'type': 'short_story'},
            {'id': '5159', 'title': 'The Body Snatcher', 'author': 'Robert Louis Stevenson', 'year': 1884, 'type': 'short_story'},
            {'id': '5160', 'title': 'The Merry Men', 'author': 'Robert Louis Stevenson', 'year': 1882, 'type': 'short_story'},
            {'id': '5161', 'title': 'The Misadventures of John Nicholson', 'author': 'Robert Louis Stevenson', 'year': 1887, 'type': 'short_story'},
            {'id': '5162', 'title': 'The Pavilion on the Links', 'author': 'Robert Louis Stevenson', 'year': 1880, 'type': 'short_story'},
            {'id': '5163', 'title': 'The Sire de Malétroit\'s Door', 'author': 'Robert Louis Stevenson', 'year': 1878, 'type': 'short_story'},
            {'id': '5164', 'title': 'The Suicide Club', 'author': 'Robert Louis Stevenson', 'year': 1878, 'type': 'short_story'},
            {'id': '5165', 'title': 'The Rajah\'s Diamond', 'author': 'Robert Louis Stevenson', 'year': 1878, 'type': 'short_story'},
            {'id': '5166', 'title': 'The Adventure of the Hansom Cab', 'author': 'Robert Louis Stevenson', 'year': 1878, 'type': 'short_story'},
            {'id': '5167', 'title': 'The Adventure of the Hansom Cab', 'author': 'Robert Louis Stevenson', 'year': 1878, 'type': 'short_story'},
            {'id': '5168', 'title': 'The Adventure of the Hansom Cab', 'author': 'Robert Louis Stevenson', 'year': 1878, 'type': 'short_story'},
            {'id': '5169', 'title': 'The Adventure of the Hansom Cab', 'author': 'Robert Louis Stevenson', 'year': 1878, 'type': 'short_story'},
            {'id': '5170', 'title': 'The Adventure of the Hansom Cab', 'author': 'Robert Louis Stevenson', 'year': 1878, 'type': 'short_story'}
        ]
    
    def test_network_connectivity(self):
        """Test network connectivity and log results"""
        logger.info("🌐 Testing network connectivity...")
        
        test_urls = [
            'https://www.gutenberg.org',
            'https://archive.org',
            'https://www.google.com'
        ]
        
        connectivity_results = {}
        
        for url in test_urls:
            try:
                response = self.session.get(url, timeout=10)
                connectivity_results[url] = {
                    'status': 'success',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
                logger.info(f"✅ {url}: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
            except Exception as e:
                connectivity_results[url] = {
                    'status': 'failed',
                    'error': str(e)
                }
                logger.warning(f"❌ {url}: {str(e)}")
        
        return connectivity_results
    
    def clean_text(self, text):
        """Clean and preprocess text for training"""
        if not text:
            return ""
            
        # Remove Project Gutenberg headers and footers
        text = re.sub(r'\*\*\* START OF.*?\*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* END OF.*?\*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'End of Project Gutenberg.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Project Gutenberg.*?www\.gutenberg\.org.*?', '', text, flags=re.DOTALL)
        
        # Remove Internet Archive headers
        text = re.sub(r'Digitized by Google.*?', '', text, flags=re.DOTALL)
        text = re.sub(r'Internet Archive.*?', '', text, flags=re.DOTALL)
        
        # Remove page numbers and headers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines to double
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)  # Trim lines
        
        return text.strip()
    
    def download_file_with_retry(self, url, filename, source_name="Unknown", max_retries=3):
        """Download a file with enhanced retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading {source_name}: {filename} (attempt {attempt + 1}/{max_retries})")
                
                response = self.session.get(url, stream=True, timeout=60)
                response.raise_for_status()
                
                # Get file size for progress bar
                total_size = int(response.headers.get('content-length', 0))
                
                file_path = self.output_dir / filename
                
                with open(file_path, 'wb') as f:
                    if total_size > 0:
                        with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    else:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                logger.info(f"✅ Downloaded {filename} ({file_size_mb:.2f} MB)")
                
                self.stats['successful_downloads'] += 1
                self.stats['total_size_mb'] += file_size_mb
                
                return str(file_path)
                
            except Exception as e:
                logger.warning(f"❌ Attempt {attempt + 1} failed for {filename}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ All attempts failed for {filename}")
                    self.stats['failed_downloads'] += 1
                    self.stats['errors'].append(f"Download error for {filename}: {str(e)}")
                    
                    # Track failed download
                    self.failed_downloads.append({
                        'source_name': source_name,
                        'url': url,
                        'error_message': str(e),
                        'file_type': filename.split('.')[-1] if '.' in filename else 'unknown',
                        'priority': 'high' if 'gutenberg' in url.lower() else 'medium'
                    })
                    
                    return None
    
    def download_gutenberg_text(self, gutenberg_id, title, author, year):
        """Download text from Project Gutenberg with multiple fallback methods"""
        if not gutenberg_id or gutenberg_id == '':
            return None
            
        logger.info(f"Downloading Gutenberg: {title} by {author} (ID: {gutenberg_id})")
        
        # Try different URL patterns
        urls = [
            f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt",
            f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}.txt",
            f"https://www.gutenberg.org/ebooks/{gutenberg_id}.txt.utf-8",
            f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.txt"
        ]
        
        for i, url in enumerate(urls):
            try:
                logger.info(f"  Trying URL {i+1}: {url}")
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200 and len(response.text) > 1000:
                    cleaned_text = self.clean_text(response.text)
                    if len(cleaned_text) > 1000:
                        logger.info(f"  ✅ Successfully downloaded from URL {i+1}")
                        return cleaned_text
                    
            except Exception as e:
                logger.warning(f"  ❌ Error with URL {i+1}: {str(e)}")
                continue
        
        logger.error(f"  ❌ All download methods failed for {title}")
        return None
    
    def download_historical_sources(self):
        """Download from historical data sources"""
        logger.info("🏛️ Downloading historical data sources...")
        
        for source_key, source_info in self.historical_sources.items():
            self.stats['total_attempted'] += 1
            self.stats['sources_processed'] += 1
            
            logger.info(f"\n📚 Processing: {source_info['name']}")
            logger.info(f"   Description: {source_info['description']}")
            logger.info(f"   Time Period: {source_info['time_period'][0]}-{source_info['time_period'][1]}")
            logger.info(f"   Format: {source_info['format']}")
            logger.info(f"   Priority: {source_info.get('priority', 'low')}")
            
            # Check if within our time period
            if not (self.time_period[0] <= source_info['time_period'][1] and 
                    self.time_period[1] >= source_info['time_period'][0]):
                logger.info(f"   ⏭️ Skipping - outside time period")
                
                # Track skipped historical source
                self.failed_downloads.append({
                    'source_name': source_info['name'],
                    'url': source_info.get('download_url', source_info.get('url', '')),
                    'error_message': f"Outside time period ({source_info['time_period'][0]}-{source_info['time_period'][1]} not in {self.time_period[0]}-{self.time_period[1]})",
                    'file_type': source_info['format'].lower(),
                    'priority': 'low'
                })
                continue
            
            try:
                text_content = None
                files_downloaded = 0
                
                # Try direct download
                if 'download_url' in source_info:
                    filename = f"{source_key}_{source_info['format'].lower()}.{source_info['format'].lower()}"
                    file_path = self.download_file_with_retry(
                        source_info['download_url'], 
                        filename, 
                        source_info['name']
                    )
                    
                    if file_path:
                        files_downloaded += 1
                        # Read and clean the downloaded file
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            text_content = f.read()
                        
                        text_content = self.clean_text(text_content)
                
                # Save processed text if we have content
                if text_content and len(text_content) > 1000:
                    text_filename = f"{source_key}_processed.txt"
                    text_path = self.output_dir / text_filename
                    
                    with open(text_path, 'w', encoding='utf-8') as f:
                        f.write(f"Source: {source_info['name']}\n")
                        f.write(f"Description: {source_info['description']}\n")
                        f.write(f"Time Period: {source_info['time_period'][0]}-{source_info['time_period'][1]}\n")
                        f.write(f"License: {source_info['license']}\n")
                        f.write(f"Downloaded: {datetime.now().isoformat()}\n")
                        f.write("="*50 + "\n\n")
                        f.write(text_content)
                    
                    logger.info(f"   ✅ Processed and saved: {text_filename}")
                else:
                    logger.warning(f"   ⚠️ No text content extracted from {source_info['name']}")
                    self.stats['failed_downloads'] += 1
                
                # Update source statistics
                self.stats['source_stats'][source_key] = {
                    'name': source_info['name'],
                    'status': 'completed' if text_content else 'failed',
                    'files_downloaded': files_downloaded,
                    'time_period': source_info['time_period'],
                    'priority': source_info.get('priority', 'low')
                }
                
            except Exception as e:
                logger.error(f"   ❌ Error processing {source_info['name']}: {str(e)}")
                self.stats['source_stats'][source_key] = {
                    'name': source_info['name'],
                    'status': 'failed',
                    'error': str(e)
                }
                self.stats['errors'].append(f"Source error for {source_info['name']}: {str(e)}")
                self.stats['failed_downloads'] += 1
            
            # Delay between sources to be respectful
            time.sleep(3)
    
    def download_gutenberg_sources(self):
        """Download from Project Gutenberg sources"""
        logger.info("\n📚 Downloading Project Gutenberg sources...")
        
        skipped_sources = []
        
        for source in tqdm(self.gutenberg_sources, desc="Downloading Gutenberg texts"):
            self.stats['total_attempted'] += 1
            
            # Check if within time period
            if not (self.time_period[0] <= source['year'] <= self.time_period[1]):
                skipped_sources.append({
                    'source_name': f"Gutenberg: {source['title']}",
                    'url': f"https://www.gutenberg.org/ebooks/{source['id']}",
                    'error_message': f"Outside time period ({source['year']} not in {self.time_period[0]}-{self.time_period[1]})",
                    'file_type': 'txt',
                    'priority': 'low'
                })
                continue
            
            text_content = self.download_gutenberg_text(
                source['id'], 
                source['title'], 
                source['author'], 
                source['year']
            )
            
            if text_content:
                # Save text
                safe_title = re.sub(r'[^\w\s-]', '', source['title']).strip()
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                safe_author = re.sub(r'[^\w\s-]', '', source['author']).strip()
                safe_author = re.sub(r'[-\s]+', '-', safe_author)
                
                filename = f"gutenberg_{safe_title}_{source['year']}_{safe_author}.txt"
                file_path = self.output_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {source['title']}\n")
                    f.write(f"Author: {source['author']}\n")
                    f.write(f"Year: {source['year']}\n")
                    f.write(f"Source: Project Gutenberg (ID: {source['id']})\n")
                    f.write(f"Type: {source['type']}\n")
                    f.write(f"Downloaded: {datetime.now().isoformat()}\n")
                    f.write("="*50 + "\n\n")
                    f.write(text_content)
                
                logger.info(f"✅ Saved: {filename}")
            else:
                self.stats['failed_downloads'] += 1
                self.stats['errors'].append(f"Failed to download {source['title']}")
                
                # Track failed Gutenberg download
                self.failed_downloads.append({
                    'source_name': f"Gutenberg: {source['title']}",
                    'url': f"https://www.gutenberg.org/ebooks/{source['id']}",
                    'error_message': "All download methods failed",
                    'file_type': 'txt',
                    'priority': 'high'
                })
            
            # Small delay to be respectful
            time.sleep(1)
        
        # Track skipped sources
        for skipped in skipped_sources:
            self.failed_downloads.append(skipped)
    
    def create_merged_corpus(self, output_file="london_historical_corpus.txt"):
        """Merge all text files into a single training corpus"""
        logger.info("\n📝 Creating merged historical corpus...")
        
        output_path = self.output_dir / output_file
        
        try:
            with open(output_path, 'w', encoding='utf-8') as outfile:
                # Process all text files
                text_files = list(self.output_dir.glob("*.txt"))
                
                logger.info(f"Found {len(text_files)} text files to merge")
                
                for text_file in tqdm(text_files, desc="Merging files"):
                    try:
                        with open(text_file, 'r', encoding='utf-8', errors='ignore') as infile:
                            content = infile.read()
                            
                            # Skip metadata headers
                            if "Title:" in content or "Source:" in content:
                                # Find the content after the header
                                parts = content.split("="*50)
                                if len(parts) > 1:
                                    content = parts[1].strip()
                            
                            if len(content) > 1000:  # Only include substantial content
                                outfile.write(content)
                                outfile.write("\n\n" + "="*80 + "\n\n")
                                
                    except Exception as e:
                        logger.warning(f"Error processing {text_file}: {e}")
                        continue
            
            logger.info(f"✅ Historical corpus created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to create merged corpus: {e}")
            return None
    
    def save_failed_downloads(self):
        """Save failed downloads to JSON file"""
        if not self.failed_downloads:
            return
        
        failed_file = self.output_dir / "failed_downloads.json"
        
        failed_data = {
            'failed_downloads': self.failed_downloads,
            'total_failed': len(self.failed_downloads),
            'generated_at': datetime.now().isoformat(),
            'time_period': self.time_period
        }
        
        try:
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(failed_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Failed downloads saved: {failed_file}")
        except Exception as e:
            logger.error(f"Error saving failed downloads: {e}")
    
    def generate_retry_script(self):
        """Generate Python retry script for failed downloads"""
        if not self.failed_downloads:
            return
        
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
        for download in self.failed_downloads:
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
        script_path = self.output_dir / "manual_retry_script.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"✅ Retry script generated: {script_path}")
        return str(script_path)
    
    def save_statistics(self):
        """Save download statistics to JSON file"""
        stats_file = self.output_dir / "download_statistics.json"
        
        # Add end time
        self.stats['end_time'] = datetime.now().isoformat()
        self.stats['duration_minutes'] = (
            datetime.fromisoformat(self.stats['end_time']) - 
            datetime.fromisoformat(self.stats['start_time'])
        ).total_seconds() / 60
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Statistics saved to: {stats_file}")
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
    
    def print_summary(self):
        """Print download summary"""
        print("\n" + "="*70)
        print("🏛️ LONDON HISTORICAL DATA COLLECTION SUMMARY")
        print("="*70)
        print(f"Total sources attempted: {self.stats['total_attempted']}")
        print(f"Successful downloads: {self.stats['successful_downloads']}")
        print(f"Failed downloads: {self.stats['failed_downloads']}")
        print(f"Total size: {self.stats['total_size_mb']:.2f} MB")
        print(f"Success rate: {(self.stats['successful_downloads']/max(1, self.stats['total_attempted'])*100):.1f}%")
        print(f"Duration: {self.stats.get('duration_minutes', 0):.1f} minutes")
        
        print(f"\n📊 Source Statistics:")
        for source_key, source_stats in self.stats['source_stats'].items():
            status_emoji = "✅" if source_stats['status'] == 'completed' else "❌"
            print(f"  {status_emoji} {source_stats['name']}: {source_stats['status']}")
        
        if self.stats['errors']:
            print(f"\n❌ Errors encountered:")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more errors")
        
        # Show failed downloads info
        if self.failed_downloads:
            print(f"\n🔄 Failed Downloads for Manual Retry:")
            print(f"  Total failed: {len(self.failed_downloads)}")
            print(f"  Check: data/london_historical/failed_downloads.json")
            print(f"  Retry script: data/london_historical/manual_retry_script.py")
        
        print("="*70)

def main():
    """Main data preparation pipeline"""
    print("🏛️ London Historical LLM - Data Collection (1500-1850)")
    print("=" * 80)
    print("📚 Downloading from multiple historical sources")
    print("=" * 80)
    
    # Initialize downloader
    downloader = LondonHistoricalDataDownloader(time_period=(1500, 1850))
    
    # Test network connectivity
    connectivity = downloader.test_network_connectivity()
    
    # Download historical sources
    downloader.download_historical_sources()
    
    # Download Gutenberg sources
    downloader.download_gutenberg_sources()
    
    # Create merged corpus
    print("\n📝 Creating merged historical corpus...")
    corpus_path = downloader.create_merged_corpus()
    
    if not corpus_path:
        print("❌ Failed to create merged corpus")
        return
    
    # Save failed downloads
    downloader.save_failed_downloads()
    
    # Generate retry script
    downloader.generate_retry_script()
    
    # Save statistics
    downloader.save_statistics()
    
    # Print summary
    downloader.print_summary()
    
    print(f"\n🎉 Data collection complete!")
    print(f"📁 Data saved to: {downloader.output_dir}")
    print(f"📄 Historical corpus file: {corpus_path}")
    print(f"📊 Statistics saved to: {downloader.output_dir}/download_statistics.json")
    print(f"📝 Log file: data_collection.log")

if __name__ == "__main__":
    main()
