"""
Fixed data preparation script for London Historical LLM (1500-1850)
Downloads and processes historical texts with progress tracking and error handling
"""

import os
import requests
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin, urlparse
import json
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LondonDataCollector:
    def __init__(self, output_dir="london_data", time_period=(1500, 1850)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.time_period = time_period
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Statistics tracking
        self.stats = {
            'total_attempted': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size_mb': 0,
            'errors': []
        }
        
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
        text = re.sub(r'Scanned by.*?', '', text, flags=re.DOTALL)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove page numbers and headers
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Chapter \d+.*$', '', text, flags=re.MULTILINE)
        
        # Remove common OCR artifacts
        text = re.sub(r'[^\w\s.,!?;:()\'"-]', '', text)
        
        return text.strip()
    
    def download_gutenberg_text(self, gutenberg_id, title, author, year):
        """Download text from Project Gutenberg with multiple fallback methods"""
        if not gutenberg_id or gutenberg_id == '':
            return None
            
        logger.info(f"Downloading: {title} by {author} (ID: {gutenberg_id})")
        
        # Try different URL patterns
        urls = [
            f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt",
            f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}.txt",
            f"https://www.gutenberg.org/ebooks/{gutenberg_id}.txt.utf-8",
            f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.txt"
        ]
        
        for i, url in enumerate(urls):
            try:
                logger.info(f"  Trying URL {i+1}/{len(urls)}: {url}")
                response = self.session.get(url, timeout=30, allow_redirects=True)
                
                if response.status_code == 200 and len(response.text) > 1000:
                    text = response.text
                    cleaned_text = self.clean_text(text)
                    
                    if len(cleaned_text) > 1000:  # Ensure substantial content
                        logger.info(f"  ✅ Successfully downloaded from URL {i+1}")
                        return cleaned_text
                    else:
                        logger.warning(f"  ⚠️  Text too short from URL {i+1}")
                else:
                    logger.warning(f"  ❌ Failed URL {i+1}: Status {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"  ❌ Error with URL {i+1}: {str(e)}")
                continue
        
        # Try HTML version as fallback
        try:
            logger.info(f"  Trying HTML fallback...")
            html_url = f"https://www.gutenberg.org/ebooks/{gutenberg_id}"
            response = self.session.get(html_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for text content in various formats
                text_elements = soup.find_all(['p', 'div'], class_=re.compile(r'text|content|chapter|book'))
                if text_elements:
                    text = ' '.join([elem.get_text() for elem in text_elements])
                    cleaned_text = self.clean_text(text)
                    
                    if len(cleaned_text) > 1000:
                        logger.info(f"  ✅ Successfully downloaded from HTML")
                        return cleaned_text
                        
        except Exception as e:
            logger.warning(f"  ❌ HTML fallback failed: {str(e)}")
        
        logger.error(f"  ❌ All download methods failed for {title}")
        return None
    
    def save_text(self, title, author, year, content, source, gutenberg_id=None):
        """Save text with proper metadata"""
        if not content or len(content) < 1000:
            logger.warning(f"Text too short for {title}: {len(content) if content else 0} characters")
            return False
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_author = re.sub(r'[^\w\s-]', '', author).strip()
        safe_author = re.sub(r'[-\s]+', '-', safe_author)
        
        filename = f"{safe_title}_{year}_{safe_author}.txt"
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n")
                f.write(f"Author: {author}\n")
                f.write(f"Year: {year}\n")
                f.write(f"Source: {source}\n")
                if gutenberg_id:
                    f.write(f"Gutenberg ID: {gutenberg_id}\n")
                f.write("="*50 + "\n\n")
                f.write(content)
            
            # Update statistics
            self.stats['successful_downloads'] += 1
            self.stats['total_size_mb'] += len(content.encode('utf-8')) / (1024 * 1024)
            
            logger.info(f"  ✅ Saved: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Failed to save {title}: {str(e)}")
            self.stats['errors'].append(f"Save error for {title}: {str(e)}")
            return False
    
    def process_metadata_csv(self, csv_path):
        """Process the metadata CSV to download texts with progress tracking"""
        if not os.path.exists(csv_path):
            logger.error(f"Metadata CSV not found: {csv_path}")
            return False
        
        logger.info(f"Processing metadata from: {csv_path}")
        
        # Read all rows first to get total count
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        total_rows = len(rows)
        logger.info(f"Found {total_rows} texts to process")
        
        # Process with progress bar
        with tqdm(total=total_rows, desc="Downloading texts", unit="text") as pbar:
            for row in rows:
                title = row['title']
                author = row['author']
                year = int(row['year']) if row['year'] else 0
                gutenberg_id = row['gutenberg_id']
                source = row.get('source', 'Project Gutenberg')
                
                # Check if within time period
                if not (self.time_period[0] <= year <= self.time_period[1]):
                    pbar.update(1)
                    continue
                
                self.stats['total_attempted'] += 1
                
                # Download text
                text = self.download_gutenberg_text(gutenberg_id, title, author, year)
                
                if text:
                    # Save text
                    if self.save_text(title, author, year, text, source, gutenberg_id):
                        pbar.set_postfix({
                            'Success': self.stats['successful_downloads'],
                            'Failed': self.stats['failed_downloads'],
                            'Size': f"{self.stats['total_size_mb']:.1f}MB"
                        })
                    else:
                        self.stats['failed_downloads'] += 1
                else:
                    self.stats['failed_downloads'] += 1
                    self.stats['errors'].append(f"Download failed: {title}")
                
                pbar.update(1)
                
                # Be respectful to the server
                time.sleep(0.5)
        
        return True
    
    def create_merged_corpus(self, output_file="london_corpus_merged.txt"):
        """Merge all text files into a single training corpus"""
        logger.info("Creating merged corpus...")
        
        # Create data directory structure
        data_dir = Path("data/london_data")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = data_dir / output_file
        
        # Find all text files
        text_files = list(self.output_dir.glob("*.txt"))
        text_files = [f for f in text_files if f.name != output_file]
        
        if not text_files:
            logger.error("No text files found to merge")
            return None
        
        logger.info(f"Found {len(text_files)} text files to merge")
        
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for text_file in tqdm(text_files, desc="Merging texts"):
                try:
                    with open(text_file, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                        outfile.write("\n\n" + "="*80 + "\n\n")
                except Exception as e:
                    logger.warning(f"Error reading {text_file}: {str(e)}")
        
        logger.info(f"Merged corpus saved to: {output_path}")
        return str(output_path)
    
    def save_statistics(self):
        """Save download statistics"""
        stats_path = self.output_dir / "download_statistics.json"
        
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Statistics saved to: {stats_path}")
    
    def print_summary(self):
        """Print download summary"""
        print("\n" + "="*60)
        print("📊 DOWNLOAD SUMMARY")
        print("="*60)
        print(f"Total attempted: {self.stats['total_attempted']}")
        print(f"Successful downloads: {self.stats['successful_downloads']}")
        print(f"Failed downloads: {self.stats['failed_downloads']}")
        print(f"Success rate: {(self.stats['successful_downloads']/max(self.stats['total_attempted'], 1)*100):.1f}%")
        print(f"Total size: {self.stats['total_size_mb']:.2f} MB")
        
        if self.stats['errors']:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more errors")
        
        print("="*60)

def main():
    """Main data preparation pipeline"""
    print("🏛️  London Historical LLM - Data Preparation (Fixed)")
    print("=" * 60)
    
    # Initialize collector
    collector = LondonDataCollector(time_period=(1500, 1850))
    
    # Process metadata CSV
    csv_path = "london_1800_1850_v0/metadata_london.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Metadata CSV not found: {csv_path}")
        print("Please ensure the metadata file exists.")
        return
    
    print(f"📚 Processing metadata from: {csv_path}")
    
    # Download texts
    if not collector.process_metadata_csv(csv_path):
        print("❌ Data processing failed")
        return
    
    # Create merged corpus
    print("\n📝 Creating merged corpus...")
    corpus_path = collector.create_merged_corpus()
    
    if not corpus_path:
        print("❌ Failed to create merged corpus")
        return
    
    # Save statistics
    collector.save_statistics()
    
    # Print summary
    collector.print_summary()
    
    print(f"\n🎉 Data preparation complete!")
    print(f"📁 Data saved to: {collector.output_dir}")
    print(f"📄 Corpus file: {corpus_path}")

if __name__ == "__main__":
    main()
