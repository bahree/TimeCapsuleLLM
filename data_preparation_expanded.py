"""
Expanded data preparation script for London Historical LLM (1500-1850)
Downloads and processes historical texts from multiple sources
"""

import os
import requests
import time
import re
import json
import csv
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExpandedLondonDataCollector:
    def __init__(self, output_dir="london_data_expanded", time_period=(1500, 1850)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.time_period = time_period
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create subdirectories
        self.subdirs = [
            'literature/16th_century',
            'literature/17th_century', 
            'literature/18th_century',
            'literature/19th_century',
            'political/philosophy',
            'political/legal',
            'political/government',
            'scientific/natural_philosophy',
            'scientific/medicine',
            'scientific/technology',
            'religious/protestant',
            'religious/catholic',
            'religious/other',
            'newspapers/17th_century',
            'newspapers/18th_century',
            'newspapers/19th_century',
            'metadata'
        ]
        
        for subdir in self.subdirs:
            (self.output_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # Initialize metadata tracking
        self.metadata = {
            'authors': {},
            'works': [],
            'sources': {},
            'quality_scores': {},
            'download_stats': {
                'total_attempted': 0,
                'successful_downloads': 0,
                'failed_downloads': 0,
                'total_size_mb': 0
            }
        }
    
    def clean_text(self, text, source_type="book"):
        """Clean and preprocess text for training"""
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
        
        # Remove OCR artifacts
        text = re.sub(r'[^\w\s.,!?;:()\'"-]', '', text)
        
        return text.strip()
    
    def download_gutenberg_text(self, gutenberg_id, title, author, year):
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
                text_elements = soup.find_all(['p', 'div'], class_=re.compile(r'text|content|chapter'))
                if text_elements:
                    text = ' '.join([elem.get_text() for elem in text_elements])
                    cleaned_text = self.clean_text(text)
                    if len(cleaned_text) > 1000:
                        return cleaned_text
                        
        except Exception as e:
            logger.error(f"Error downloading {title} (ID: {gutenberg_id}): {e}")
            
        return None
    
    def download_internet_archive_text(self, url, title, author, year):
        """Download text from Internet Archive"""
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                text = response.text
                cleaned_text = self.clean_text(text, "archive")
                if len(cleaned_text) > 1000:
                    return cleaned_text
        except Exception as e:
            logger.error(f"Error downloading {title} from Internet Archive: {e}")
        
        return None
    
    def get_century_directory(self, year):
        """Get the appropriate subdirectory for a given year"""
        if 1500 <= year < 1600:
            return "literature/16th_century"
        elif 1600 <= year < 1700:
            return "literature/17th_century"
        elif 1700 <= year < 1800:
            return "literature/18th_century"
        elif 1800 <= year <= 1850:
            return "literature/19th_century"
        else:
            return "literature/other"
    
    def categorize_text(self, title, author, year, content):
        """Categorize text based on content and metadata"""
        categories = []
        
        # Literature categories
        if any(word in title.lower() for word in ['poem', 'poetry', 'verse', 'sonnet']):
            categories.append('poetry')
        elif any(word in title.lower() for word in ['novel', 'story', 'tale', 'romance']):
            categories.append('fiction')
        elif any(word in title.lower() for word in ['play', 'drama', 'tragedy', 'comedy']):
            categories.append('drama')
        
        # Political categories
        if any(word in title.lower() for word in ['government', 'politics', 'state', 'republic']):
            categories.append('political')
        elif any(word in title.lower() for word in ['law', 'legal', 'jurisprudence', 'statute']):
            categories.append('legal')
        
        # Scientific categories
        if any(word in title.lower() for word in ['science', 'natural', 'philosophy', 'experiment']):
            categories.append('scientific')
        elif any(word in title.lower() for word in ['medicine', 'medical', 'physic', 'anatomy']):
            categories.append('medical')
        
        # Religious categories
        if any(word in title.lower() for word in ['bible', 'scripture', 'theology', 'sermon']):
            categories.append('religious')
        
        return categories if categories else ['general']
    
    def save_text(self, title, author, year, content, source, gutenberg_id=None, categories=None):
        """Save text with proper categorization and metadata"""
        if not content or len(content) < 1000:
            return False
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_author = re.sub(r'[^\w\s-]', '', author).strip()
        safe_author = re.sub(r'[-\s]+', '-', safe_author)
        
        # Determine directory
        if categories and 'political' in categories:
            if 'legal' in categories:
                subdir = "political/legal"
            else:
                subdir = "political/philosophy"
        elif categories and 'scientific' in categories:
            if 'medical' in categories:
                subdir = "scientific/medicine"
            else:
                subdir = "scientific/natural_philosophy"
        elif categories and 'religious' in categories:
            subdir = "religious/protestant"  # Default to protestant for now
        else:
            subdir = self.get_century_directory(year)
        
        # Save text file
        filename = f"{safe_title}_{year}_{safe_author}.txt"
        file_path = self.output_dir / subdir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Author: {author}\n")
            f.write(f"Year: {year}\n")
            f.write(f"Source: {source}\n")
            if gutenberg_id:
                f.write(f"Gutenberg ID: {gutenberg_id}\n")
            f.write(f"Categories: {', '.join(categories) if categories else 'general'}\n")
            f.write("="*50 + "\n\n")
            f.write(content)
        
        # Update metadata
        self.metadata['works'].append({
            'title': title,
            'author': author,
            'year': year,
            'source': source,
            'gutenberg_id': gutenberg_id,
            'categories': categories or ['general'],
            'file_path': str(file_path),
            'size_chars': len(content),
            'size_mb': len(content.encode('utf-8')) / (1024 * 1024)
        })
        
        # Update author stats
        if author not in self.metadata['authors']:
            self.metadata['authors'][author] = 0
        self.metadata['authors'][author] += 1
        
        # Update source stats
        if source not in self.metadata['sources']:
            self.metadata['sources'][source] = 0
        self.metadata['sources'][source] += 1
        
        # Update download stats
        self.metadata['download_stats']['successful_downloads'] += 1
        self.metadata['download_stats']['total_size_mb'] += len(content.encode('utf-8')) / (1024 * 1024)
        
        return True
    
    def process_expanded_metadata(self, csv_path):
        """Process expanded metadata CSV to download texts"""
        logger.info("Processing expanded metadata...")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in tqdm(reader, desc="Processing texts"):
                title = row['title']
                author = row['author']
                year = int(row['year']) if row['year'] else 0
                gutenberg_id = row['gutenberg_id']
                source = row.get('source', 'Project Gutenberg')
                url = row.get('source_url', '')
                
                # Check if within time period
                if not (self.time_period[0] <= year <= self.time_period[1]):
                    continue
                
                self.metadata['download_stats']['total_attempted'] += 1
                
                logger.info(f"Processing: {title} by {author} ({year})")
                
                # Download text
                text = None
                if gutenberg_id and gutenberg_id != '':
                    text = self.download_gutenberg_text(gutenberg_id, title, author, year)
                elif url and 'archive.org' in url:
                    text = self.download_internet_archive_text(url, title, author, year)
                
                if text:
                    # Categorize text
                    categories = self.categorize_text(title, author, year, text)
                    
                    # Save text
                    if self.save_text(title, author, year, text, source, gutenberg_id, categories):
                        logger.info(f"  ✓ Downloaded: {title}")
                    else:
                        logger.warning(f"  ⚠️  Text too short: {title}")
                        self.metadata['download_stats']['failed_downloads'] += 1
                else:
                    logger.warning(f"  ✗ Failed to download: {title}")
                    self.metadata['download_stats']['failed_downloads'] += 1
                
                # Be respectful to the server
                time.sleep(1)
    
    def create_expanded_metadata_csv(self):
        """Create expanded metadata CSV with more sources"""
        logger.info("Creating expanded metadata CSV...")
        
        # This would be populated with actual data from multiple sources
        # For now, we'll create a template
        expanded_works = [
            # 16th Century
            {"title": "Utopia", "author": "Thomas More", "year": 1516, "gutenberg_id": "2130", "source": "Project Gutenberg"},
            {"title": "The Faerie Queene", "author": "Edmund Spenser", "year": 1590, "gutenberg_id": "15242", "source": "Project Gutenberg"},
            {"title": "Doctor Faustus", "author": "Christopher Marlowe", "year": 1592, "gutenberg_id": "779", "source": "Project Gutenberg"},
            
            # 17th Century
            {"title": "Essays", "author": "Francis Bacon", "year": 1625, "gutenberg_id": "418", "source": "Project Gutenberg"},
            {"title": "Paradise Lost", "author": "John Milton", "year": 1667, "gutenberg_id": "20", "source": "Project Gutenberg"},
            {"title": "The Pilgrim's Progress", "author": "John Bunyan", "year": 1678, "gutenberg_id": "131", "source": "Project Gutenberg"},
            
            # 18th Century
            {"title": "Robinson Crusoe", "author": "Daniel Defoe", "year": 1719, "gutenberg_id": "521", "source": "Project Gutenberg"},
            {"title": "Gulliver's Travels", "author": "Jonathan Swift", "year": 1726, "gutenberg_id": "829", "source": "Project Gutenberg"},
            {"title": "Tom Jones", "author": "Henry Fielding", "year": 1749, "gutenberg_id": "6593", "source": "Project Gutenberg"},
            {"title": "Tristram Shandy", "author": "Laurence Sterne", "year": 1759, "gutenberg_id": "1079", "source": "Project Gutenberg"},
            
            # Early 19th Century
            {"title": "Pride and Prejudice", "author": "Jane Austen", "year": 1813, "gutenberg_id": "1342", "source": "Project Gutenberg"},
            {"title": "Frankenstein", "author": "Mary Shelley", "year": 1818, "gutenberg_id": "84", "source": "Project Gutenberg"},
            {"title": "Oliver Twist", "author": "Charles Dickens", "year": 1837, "gutenberg_id": "730", "source": "Project Gutenberg"},
        ]
        
        # Save expanded metadata
        csv_path = self.output_dir / "metadata" / "expanded_works.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['title', 'author', 'year', 'gutenberg_id', 'source', 'source_url', 'status', 'score']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for work in expanded_works:
                writer.writerow({
                    'title': work['title'],
                    'author': work['author'],
                    'year': work['year'],
                    'gutenberg_id': work['gutenberg_id'],
                    'source': work['source'],
                    'source_url': f"https://www.gutenberg.org/ebooks/{work['gutenberg_id']}",
                    'status': 'PENDING',
                    'score': '1.0'
                })
        
        return str(csv_path)
    
    def create_merged_corpus(self, output_file="london_corpus_expanded.txt"):
        """Merge all text files into a single training corpus"""
        logger.info("Creating merged corpus...")
        
        output_path = self.output_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for work in self.metadata['works']:
                file_path = work['file_path']
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                        outfile.write("\n\n" + "="*80 + "\n\n")
        
        logger.info(f"Merged corpus saved to: {output_path}")
        return str(output_path)
    
    def save_metadata(self):
        """Save comprehensive metadata"""
        logger.info("Saving metadata...")
        
        # Save authors metadata
        authors_path = self.output_dir / "metadata" / "authors.csv"
        with open(authors_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['author', 'work_count'])
            for author, count in sorted(self.metadata['authors'].items(), key=lambda x: x[1], reverse=True):
                writer.writerow([author, count])
        
        # Save works metadata
        works_path = self.output_dir / "metadata" / "works.csv"
        with open(works_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['title', 'author', 'year', 'source', 'gutenberg_id', 'categories', 'file_path', 'size_chars', 'size_mb']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for work in self.metadata['works']:
                writer.writerow(work)
        
        # Save sources metadata
        sources_path = self.output_dir / "metadata" / "sources.csv"
        with open(sources_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['source', 'work_count'])
            for source, count in sorted(self.metadata['sources'].items(), key=lambda x: x[1], reverse=True):
                writer.writerow([source, count])
        
        # Save comprehensive metadata JSON
        metadata_path = self.output_dir / "metadata" / "comprehensive_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        logger.info("Metadata saved successfully")

def main():
    """Main data preparation pipeline"""
    print("🏛️  London Historical LLM - Expanded Data Preparation")
    print("=" * 60)
    
    # Initialize collector
    collector = ExpandedLondonDataCollector(time_period=(1500, 1850))
    
    # Create expanded metadata
    print("📋 Creating expanded metadata...")
    csv_path = collector.create_expanded_metadata_csv()
    
    # Process metadata CSV
    print("📚 Downloading historical texts...")
    collector.process_expanded_metadata(csv_path)
    
    # Create merged corpus
    print("📝 Creating merged corpus...")
    corpus_path = collector.create_merged_corpus()
    
    # Save metadata
    collector.save_metadata()
    
    # Print summary
    stats = collector.metadata['download_stats']
    print(f"\n📊 Data Collection Summary:")
    print(f"   Total attempted: {stats['total_attempted']}")
    print(f"   Successful downloads: {stats['successful_downloads']}")
    print(f"   Failed downloads: {stats['failed_downloads']}")
    print(f"   Total size: {stats['total_size_mb']:.2f} MB")
    print(f"   Corpus: {corpus_path}")
    print(f"\n🎉 Expanded data preparation complete!")

if __name__ == "__main__":
    main()
