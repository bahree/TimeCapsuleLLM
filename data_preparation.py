"""
Data preparation script for London Historical LLM (1500-1850)
Downloads and processes historical texts from Project Gutenberg and other sources
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

class LondonDataCollector:
    def __init__(self, output_dir="london_data", time_period=(1500, 1850)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.time_period = time_period
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def clean_text(self, text):
        """Clean and preprocess text for training"""
        # Remove Project Gutenberg headers and footers
        text = re.sub(r'\*\*\* START OF.*?\*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'\*\*\* END OF.*?\*\*\*', '', text, flags=re.DOTALL)
        text = re.sub(r'End of Project Gutenberg.*', '', text, flags=re.DOTALL)
        text = re.sub(r'Project Gutenberg.*?www\.gutenberg\.org.*?', '', text, flags=re.DOTALL)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove page numbers and headers
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Chapter \d+.*$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def download_gutenberg_text(self, gutenberg_id, title):
        """Download text from Project Gutenberg"""
        try:
            # Try different URL patterns
            urls = [
                f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt",
                f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}.txt",
                f"https://www.gutenberg.org/ebooks/{gutenberg_id}.txt.utf-8"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        text = response.text
                        cleaned_text = self.clean_text(text)
                        if len(cleaned_text) > 1000:  # Ensure substantial content
                            return cleaned_text
                except:
                    continue
                    
            # Try HTML version as fallback
            html_url = f"https://www.gutenberg.org/ebooks/{gutenberg_id}"
            response = self.session.get(html_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for text content in various formats
                text_elements = soup.find_all(['p', 'div'], class_=re.compile(r'text|content|chapter'))
                if text_elements:
                    text = ' '.join([elem.get_text() for elem in text_elements])
                    cleaned_text = self.clean_text(text)
                    if len(cleaned_text) > 1000:
                        return cleaned_text
                        
        except Exception as e:
            print(f"Error downloading {title} (ID: {gutenberg_id}): {e}")
            
        return None
    
    def process_metadata_csv(self, csv_path):
        """Process the metadata CSV to download texts"""
        downloaded_files = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row['title']
                author = row['author']
                year = int(row['year']) if row['year'] else 0
                gutenberg_id = row['gutenberg_id']
                filename = row['filename']
                
                # Check if within time period
                if not (self.time_period[0] <= year <= self.time_period[1]):
                    continue
                    
                # Skip if no Gutenberg ID
                if not gutenberg_id or gutenberg_id == '':
                    continue
                
                print(f"Processing: {title} by {author} ({year})")
                
                # Download text
                text = self.download_gutenberg_text(gutenberg_id, title)
                if text:
                    # Save individual file
                    safe_title = re.sub(r'[^\w\s-]', '', title).strip()
                    safe_title = re.sub(r'[-\s]+', '-', safe_title)
                    file_path = self.output_dir / f"{safe_title}_{year}.txt"
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Title: {title}\n")
                        f.write(f"Author: {author}\n")
                        f.write(f"Year: {year}\n")
                        f.write(f"Source: Project Gutenberg ID {gutenberg_id}\n")
                        f.write("="*50 + "\n\n")
                        f.write(text)
                    
                    downloaded_files.append(str(file_path))
                    print(f"  ✓ Downloaded: {file_path}")
                else:
                    print(f"  ✗ Failed to download: {title}")
                
                # Be respectful to the server
                time.sleep(1)
        
        return downloaded_files
    
    def create_merged_corpus(self, text_files, output_file="london_corpus_merged.txt"):
        """Merge all text files into a single training corpus"""
        output_path = self.output_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for text_file in text_files:
                if os.path.exists(text_file):
                    with open(text_file, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                        outfile.write("\n\n" + "="*80 + "\n\n")
        
        print(f"Merged corpus saved to: {output_path}")
        return str(output_path)

def main():
    """Main data preparation pipeline"""
    print("🏛️  London Historical LLM Data Preparation")
    print("=" * 50)
    
    # Initialize collector
    collector = LondonDataCollector(time_period=(1500, 1850))
    
    # Process metadata CSV
    csv_path = "london_1800_1850_v0/metadata_london.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Metadata CSV not found at {csv_path}")
        return
    
    print("📚 Downloading historical texts...")
    downloaded_files = collector.process_metadata_csv(csv_path)
    
    if not downloaded_files:
        print("❌ No files were downloaded successfully")
        return
    
    print(f"\n✅ Successfully downloaded {len(downloaded_files)} texts")
    
    # Create merged corpus
    print("\n📝 Creating merged corpus...")
    corpus_path = collector.create_merged_corpus(downloaded_files)
    
    # Create data summary
    total_chars = 0
    for file_path in downloaded_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                total_chars += len(f.read())
    
    summary = {
        "total_files": len(downloaded_files),
        "total_characters": total_chars,
        "corpus_path": corpus_path,
        "time_period": collector.time_period
    }
    
    with open(collector.output_dir / "data_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📊 Data Summary:")
    print(f"   Files: {summary['total_files']}")
    print(f"   Characters: {summary['total_characters']:,}")
    print(f"   Corpus: {corpus_path}")
    print(f"\n🎉 Data preparation complete!")

if __name__ == "__main__":
    main()
