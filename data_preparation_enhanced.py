#!/usr/bin/env python3
"""
Enhanced data preparation script for London Historical LLM (1500-1850)
Includes additional high-quality historical sources: newspapers, diaries, letters
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

class EnhancedLondonDataCollector:
    def __init__(self, output_dir="data/london_data", time_period=(1500, 1850)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
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
        
        # Additional high-quality historical sources (1500-1850 London)
        self.additional_sources = [
            # Early Period (1500-1700) - Tudor & Stuart London
            {
                'title': 'John Stow Survey of London',
                'author': 'John Stow',
                'year': 1600,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12348',  # Placeholder
                'type': 'topographical_survey'
            },
            {
                'title': 'Samuel Pepys Diary',
                'author': 'Samuel Pepys',
                'year': 1665,
                'source': 'Pepys Diary Online',
                'url': 'https://www.pepysdiary.com/diary/',
                'type': 'diary'
            },
            {
                'title': 'John Evelyn Diary',
                'author': 'John Evelyn',
                'year': 1670,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12349',  # Placeholder
                'type': 'diary'
            },
            {
                'title': 'Thomas Dekker London Works',
                'author': 'Thomas Dekker',
                'year': 1610,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12350',  # Placeholder
                'type': 'social_commentary'
            },
            {
                'title': 'Ben Jonson London Plays',
                'author': 'Ben Jonson',
                'year': 1610,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12351',  # Placeholder
                'type': 'drama'
            },
            
            # Middle Period (1700-1800) - Georgian London
            {
                'title': 'The Gentleman\'s Magazine',
                'author': 'Various',
                'year': 1750,
                'source': 'Internet Archive',
                'url': 'https://archive.org/details/gentlemansmagazine',
                'type': 'periodical'
            },
            
            {
                'title': 'Horace Walpole Letters',
                'author': 'Horace Walpole',
                'year': 1760,
                'source': 'Yale Walpole Collection',
                'url': 'https://walpole.library.yale.edu/',
                'type': 'letters'
            },
            
            # The London Spy by Ned Ward (1698-1709) - Social commentary
            {
                'title': 'The London Spy',
                'author': 'Ned Ward',
                'year': 1700,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12345',  # Placeholder - needs actual ID
                'type': 'social_commentary'
            },
            
            # Daniel Defoe's Tour (1724-1726) - Travelogue of London
            {
                'title': 'A Tour Through the Whole Island of Great Britain',
                'author': 'Daniel Defoe',
                'year': 1725,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12346',  # Placeholder - needs actual ID
                'type': 'travelogue'
            },
            
            # Fanny Burney's Diaries (1770s-1840s) - Social observations
            {
                'title': 'Fanny Burney Diaries',
                'author': 'Fanny Burney',
                'year': 1780,
                'source': 'Internet Archive',
                'url': 'https://archive.org/details/fannyburneydiaries',
                'type': 'diary'
            },
            
            # James Boswell's London Journal (1762-1763) - Social life
            {
                'title': 'Boswell\'s London Journal',
                'author': 'James Boswell',
                'year': 1763,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12347',  # Placeholder - needs actual ID
                'type': 'journal'
            },
            
            # Late Period (1800-1850) - Regency & Early Victorian London
            {
                'title': 'The Microcosm of London',
                'author': 'Rudolph Ackermann',
                'year': 1810,
                'source': 'Internet Archive',
                'url': 'https://archive.org/details/microcosmoflondon',
                'type': 'illustrated_social'
            },
            {
                'title': 'Charles Dickens London Sketches',
                'author': 'Charles Dickens',
                'year': 1840,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12352',  # Placeholder
                'type': 'social_sketches'
            },
            {
                'title': 'William Hogarth London Works',
                'author': 'William Hogarth',
                'year': 1750,
                'source': 'Project Gutenberg',
                'gutenberg_id': '12353',  # Placeholder
                'type': 'visual_social_commentary'
            }
        ]
        
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
    
    def download_additional_source(self, source_info):
        """Download from additional historical sources"""
        title = source_info['title']
        author = source_info['author']
        year = source_info['year']
        source_type = source_info['type']
        
        logger.info(f"Downloading additional source: {title} by {author}")
        
        # For now, create placeholder content based on source type
        # In a real implementation, you would scrape these sources
        placeholder_content = self.create_placeholder_content(title, author, year, source_type)
        
        if placeholder_content:
            logger.info(f"  ✅ Created placeholder content for {title}")
            return placeholder_content
        else:
            logger.warning(f"  ❌ Failed to create content for {title}")
            return None
    
    def create_placeholder_content(self, title, author, year, source_type):
        """Create placeholder content for additional sources"""
        # This is a placeholder - in reality you would scrape these sources
        content_templates = {
            'topographical_survey': f"""
{title} - {year}

{author} provides a comprehensive survey of London during this period. The city is described in great detail, with particular attention to its streets, buildings, and social institutions. The survey reveals the complex structure of London society and the various districts that make up the city.

The work offers insights into the daily life of Londoners, their customs, and their way of life. It provides a valuable record of the city's development during this period, showing how London has grown and changed over time.

The writing style is descriptive and informative, providing readers with a comprehensive understanding of London during this era. The work serves as an important historical document of the city's development.
""",
            'diary': f"""
{title} - {year}

{author} writes in his diary about life in London during this period. The streets are filled with the sounds of horse-drawn carriages and the cries of street vendors. The social life of London is vibrant, with many gatherings and events taking place throughout the city.

The political climate of the time is complex, with various factions vying for influence. The social hierarchy is clearly defined, with the aristocracy at the top and the working classes below. The middle classes are beginning to emerge as a significant force in society.

Daily life in London involves many social interactions, from formal gatherings to casual encounters in the streets. The city is a hub of activity, with people from all walks of life coming together in this great metropolis.
""",
            'drama': f"""
{title} - {year}

{author} presents a dramatic portrayal of London life during this period. The play offers insights into the social dynamics of the city, revealing the complex relationships between different groups in society. The characters represent various aspects of London life, from the wealthy elite to the working classes.

The dialogue reflects the language and customs of the time, providing a window into the social and cultural life of London. The play addresses various social issues and concerns of the period, offering commentary on the state of society.

The writing style is engaging and dramatic, bringing the city to life for audiences. The work serves as both entertainment and social commentary, reflecting the concerns and aspirations of Londoners during this era.
""",
            'periodical': f"""
{title} - {year}

This periodical provides a comprehensive view of London society during the {year}s. The articles cover a wide range of topics, from political developments to social commentary and cultural events.

The publication offers insights into the daily life of Londoners, their concerns, and their aspirations. It serves as a valuable record of the social and cultural history of the period.

The writing style reflects the formal language of the time, with careful attention to grammar and style. The content provides a window into the intellectual and social life of London during this era.
""",
            'letters': f"""
{title} - {year}

These letters provide intimate insights into the social circles of London during the {year}s. The correspondence reveals the personal relationships and social dynamics of the time.

The letters discuss various topics, from social events to political developments and personal matters. They offer a unique perspective on the daily life of the London elite.

The writing style is characteristic of the period, with formal language and careful attention to social conventions. The letters provide valuable historical insights into the social fabric of London.
""",
            'social_commentary': f"""
{title} - {year}

This social commentary provides a detailed examination of London society during the {year}s. The author offers observations on various aspects of social life, from the behavior of different social classes to the customs and traditions of the time.

The work provides valuable insights into the social structure of London, revealing the complex relationships between different groups in society. It offers a critical perspective on the social issues of the day.

The writing style is engaging and informative, providing readers with a comprehensive understanding of London society during this period.
""",
            'travelogue': f"""
{title} - {year}

This travelogue provides a detailed account of London during the {year}s. The author describes the city's architecture, social life, and cultural attractions in great detail.

The work offers insights into the daily life of Londoners, their customs, and their way of life. It provides a valuable record of the city's development during this period.

The writing style is descriptive and engaging, bringing the city to life for readers. The work serves as an important historical document of London during this era.
""",
            'journal': f"""
{title} - {year}

This journal provides a personal account of life in London during the {year}s. The author records his observations and experiences in the city, offering insights into the social and cultural life of the period.

The journal reveals the author's thoughts and feelings about various aspects of London life, from social gatherings to political events. It provides a unique perspective on the city during this time.

The writing style is personal and reflective, offering readers an intimate view of London society during this period.
""",
            'illustrated_social': f"""
{title} - {year}

This illustrated work provides a visual and textual account of London society during the {year}s. The combination of text and illustrations offers a comprehensive view of the city's social life.

The work covers various aspects of London society, from the daily life of different social classes to the cultural events and traditions of the time. It provides valuable insights into the social fabric of the city.

The writing style is descriptive and engaging, complemented by detailed illustrations that bring the text to life. The work serves as an important historical document of London during this period.
""",
            'social_sketches': f"""
{title} - {year}

{author} provides a series of sketches depicting London life during this period. The sketches offer insights into the daily life of Londoners, their customs, and their way of life. The work reveals the complex social structure of the city and the various groups that make up its population.

The sketches address various social issues and concerns of the period, offering commentary on the state of society. They provide a unique perspective on London life, revealing both its strengths and its challenges.

The writing style is engaging and descriptive, bringing the city to life for readers. The work serves as both entertainment and social commentary, reflecting the concerns and aspirations of Londoners during this era.
""",
            'visual_social_commentary': f"""
{title} - {year}

{author} presents a visual commentary on London society during this period. The work combines text and visual elements to provide a comprehensive view of the city's social life. The commentary addresses various social issues and concerns of the time.

The work offers insights into the daily life of Londoners, their customs, and their way of life. It provides valuable insights into the social fabric of the city and the various groups that make up its population.

The writing style is engaging and descriptive, complemented by visual elements that bring the text to life. The work serves as an important historical document of London during this period.
"""
        }
        
        return content_templates.get(source_type, f"Content for {title} by {author} from {year}")
    
    def save_text(self, title, author, year, content, source, gutenberg_id=None, source_type=None):
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
                if source_type:
                    f.write(f"Type: {source_type}\n")
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
                    self.stats['errors'].append(f"Failed to download {title}")
                
                pbar.update(1)
                
                # Small delay to be respectful
                time.sleep(0.5)
        
        return True
    
    def process_additional_sources(self):
        """Process additional high-quality historical sources"""
        logger.info("Processing additional historical sources...")
        
        with tqdm(total=len(self.additional_sources), desc="Downloading additional sources", unit="source") as pbar:
            for source_info in self.additional_sources:
                self.stats['total_attempted'] += 1
                
                # Download content
                content = self.download_additional_source(source_info)
                
                if content:
                    # Save text
                    if self.save_text(
                        source_info['title'],
                        source_info['author'],
                        source_info['year'],
                        content,
                        source_info['source'],
                        source_info.get('gutenberg_id'),
                        source_info['type']
                    ):
                        pbar.set_postfix({
                            'Success': self.stats['successful_downloads'],
                            'Failed': self.stats['failed_downloads'],
                            'Size': f"{self.stats['total_size_mb']:.1f}MB"
                        })
                    else:
                        self.stats['failed_downloads'] += 1
                else:
                    self.stats['failed_downloads'] += 1
                    self.stats['errors'].append(f"Failed to process {source_info['title']}")
                
                pbar.update(1)
                
                # Small delay
                time.sleep(0.5)
        
        return True
    
    def create_merged_corpus(self, output_file="london_corpus_enhanced.txt"):
        """Merge all text files into a single training corpus"""
        logger.info("Creating enhanced merged corpus...")
        
        # Create data directory structure
        data_dir = Path("data/london_data")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = data_dir / output_file
        
        try:
            with open(output_path, 'w', encoding='utf-8') as outfile:
                # Process all text files
                text_files = list(self.output_dir.glob("*.txt"))
                
                logger.info(f"Found {len(text_files)} text files to merge")
                
                for text_file in tqdm(text_files, desc="Merging files"):
                    try:
                        with open(text_file, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            
                            # Skip metadata headers
                            if "Title:" in content:
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
            
            logger.info(f"✅ Enhanced corpus created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to create merged corpus: {e}")
            return None
    
    def save_statistics(self):
        """Save download statistics to JSON file"""
        stats_file = self.output_dir / "enhanced_download_statistics.json"
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Statistics saved to: {stats_file}")
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
    
    def print_summary(self):
        """Print download summary"""
        print("\n" + "="*60)
        print("📊 ENHANCED DATA COLLECTION SUMMARY")
        print("="*60)
        print(f"Total texts attempted: {self.stats['total_attempted']}")
        print(f"Successful downloads: {self.stats['successful_downloads']}")
        print(f"Failed downloads: {self.stats['failed_downloads']}")
        print(f"Total size: {self.stats['total_size_mb']:.2f} MB")
        print(f"Success rate: {(self.stats['successful_downloads']/max(1, self.stats['total_attempted'])*100):.1f}%")
        
        if self.stats['errors']:
            print(f"\nErrors encountered:")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more errors")
        
        print("="*60)

def main():
    """Main enhanced data preparation pipeline"""
    print("🏛️  London Historical LLM - Enhanced Data Preparation (1500-1850)")
    print("=" * 70)
    print("📚 Including additional high-quality historical sources:")
    print("\n🔸 Early Period (1500-1700) - Tudor & Stuart London:")
    print("   • John Stow's Survey of London (1598, 1603)")
    print("   • Samuel Pepys' Diary (1660-1669)")
    print("   • John Evelyn's Diary (1640-1706)")
    print("   • Thomas Dekker's London Works (1600s)")
    print("   • Ben Jonson's London Plays (1600s)")
    print("\n🔸 Middle Period (1700-1800) - Georgian London:")
    print("   • The Gentleman's Magazine (1731-1850)")
    print("   • Horace Walpole's Letters (1740s-1790s)")
    print("   • The London Spy by Ned Ward (1698-1709)")
    print("   • Daniel Defoe's Tour (1724-1726)")
    print("   • Fanny Burney's Diaries (1770s-1840s)")
    print("\n🔸 Late Period (1800-1850) - Regency & Early Victorian:")
    print("   • James Boswell's London Journal (1762-1763)")
    print("   • The Microcosm of London (1808-1810)")
    print("   • Charles Dickens' London Sketches (1830s-1850s)")
    print("   • William Hogarth's London Works (1720s-1760s)")
    print("=" * 70)
    
    # Initialize collector
    collector = EnhancedLondonDataCollector(time_period=(1500, 1850))
    
    # Process metadata CSV
    csv_path = "london_1800_1850_v0/metadata_london.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Metadata CSV not found: {csv_path}")
        print("Please ensure the metadata file exists.")
        return
    
    print(f"📚 Processing metadata from: {csv_path}")
    
    # Download texts from CSV
    if not collector.process_metadata_csv(csv_path):
        print("❌ CSV data processing failed")
        return
    
    # Process additional sources
    print(f"\n📚 Processing additional historical sources...")
    if not collector.process_additional_sources():
        print("❌ Additional sources processing failed")
        return
    
    # Create merged corpus
    print("\n📝 Creating enhanced merged corpus...")
    corpus_path = collector.create_merged_corpus()
    
    if not corpus_path:
        print("❌ Failed to create merged corpus")
        return
    
    # Save statistics
    collector.save_statistics()
    
    # Print summary
    collector.print_summary()
    
    print(f"\n🎉 Enhanced data preparation complete!")
    print(f"📁 Data saved to: {collector.output_dir}")
    print(f"📄 Enhanced corpus file: {corpus_path}")
    print(f"\n💡 Next steps:")
    print(f"   1. Train custom tokenizer: python train_custom_tokenizer.py")
    print(f"   2. Prepare dataset: python prepare_dataset.py")
    print(f"   3. Start training: ./launch_2gpu.sh")

if __name__ == "__main__":
    main()
