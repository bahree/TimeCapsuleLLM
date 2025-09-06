#!/usr/bin/env python3
"""
Comprehensive London Historical Data Downloader (1500-1850)
Downloads from multiple historical sources including London Lives, Old Bailey, and more
"""

import os
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
import zipfile
import tarfile
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveLondonDataDownloader:
    def __init__(self, output_dir="data/london_historical", time_period=(1500, 1850)):
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
            'sources_processed': 0,
            'errors': [],
            'source_stats': {}
        }
        
        # Historical data sources with real URLs
        self.historical_sources = {
            'london_lives': {
                'name': 'London Lives 1690-1800',
                'description': '240,000 manuscript pages from eight London archives',
                'time_period': (1690, 1800),
                'format': 'XML',
                'url': 'https://www.londonlives.org/',
                'download_url': 'https://figshare.com/ndownloader/files/8258664',  # Direct download
                'scrape_url': 'https://www.londonlives.org/',
                'license': 'CC-BY-NC',
                'type': 'criminal_social_records',
                'scraping_enabled': True
            },
            'old_bailey': {
                'name': 'Old Bailey Proceedings',
                'description': '197,000+ trial accounts from London\'s Central Criminal Court',
                'time_period': (1674, 1850),
                'format': 'XML',
                'url': 'https://orda.shef.ac.uk/articles/dataset/Old_Bailey_Online_XML_Data/4775434',
                'download_url': 'https://orda.shef.ac.uk/ndownloader/files/8258665',  # Direct download
                'license': 'Free for research',
                'type': 'criminal_records'
            },
            'old_bailey_corpus': {
                'name': 'Old Bailey Corpus 2.0',
                'description': 'Tagged subset for linguistic analysis',
                'time_period': (1720, 1850),
                'format': 'XML',
                'url': 'https://fedora.clarin-d.uni-saarland.de/oldbailey/',
                'download_url': 'https://fedora.clarin-d.uni-saarland.de/oldbailey/downloads/OBC_2.0_Manual%25202016-07-13.pdf',
                'license': 'Free with registration',
                'type': 'linguistic_corpus'
            },
            'locating_london': {
                'name': 'Locating London\'s Past Datasets',
                'description': 'Geo-referenced historical data mapped to 18th-century London',
                'time_period': (1660, 1800),
                'format': 'CSV, XML',
                'url': 'https://www.locatinglondon.org/about/data-downloads',
                'download_urls': [
                    'https://www.locatinglondon.org/data/oldbailey_trials.csv',
                    'https://www.locatinglondon.org/data/plague_bills.xml'
                ],
                'license': 'CC-BY-NC',
                'type': 'geospatial_data'
            },
            'defoe_plague': {
                'name': 'A Journal of the Plague Year',
                'description': 'Daniel Defoe\'s account of the 1665 Great Plague in London',
                'time_period': (1665, 1665),
                'format': 'TXT',
                'url': 'https://www.gutenberg.org/ebooks/376',
                'download_url': 'https://www.gutenberg.org/files/376/376-0.txt',
                'license': 'Public Domain',
                'type': 'historical_narrative'
            },
            'source_book_london': {
                'name': 'Source Book of London History',
                'description': 'Curated extracts from original sources on London\'s development',
                'time_period': (1500, 1800),
                'format': 'TXT',
                'url': 'https://www.gutenberg.org/ebooks/51175',
                'download_url': 'https://www.gutenberg.org/files/51175/51175-0.txt',
                'license': 'Public Domain',
                'type': 'historical_compilation'
            },
            'historical_collections': {
                'name': 'Historical Collections of a Citizen of London',
                'description': 'Poems and chronicles on London events from 15th century',
                'time_period': (1400, 1500),
                'format': 'PDF',
                'url': 'https://archive.org/details/historicalcollec00gairrich',
                'download_url': 'https://archive.org/download/historicalcollec00gairrich/historicalcollec00gairrich.pdf',
                'license': 'Public Domain',
                'type': 'historical_manuscript'
            },
            'national_archives': {
                'name': 'The National Archives (TNA)',
                'description': 'UK government records including London-related correspondence and censuses',
                'time_period': (1500, 1850),
                'format': 'Digital Images/PDF',
                'url': 'https://www.nationalarchives.gov.uk/',
                'scrape_url': 'https://discovery.nationalarchives.gov.uk/',
                'license': 'Crown Copyright',
                'type': 'government_records',
                'scraping_enabled': True,
                'search_terms': ['London', 'metropolitan', 'parish', 'census', 'taxation']
            },
            'british_history_online': {
                'name': 'British History Online',
                'description': 'Digital library of primary and secondary sources for British history',
                'time_period': (1500, 1850),
                'format': 'HTML/PDF',
                'url': 'https://www.british-history.ac.uk/',
                'scrape_url': 'https://www.british-history.ac.uk/',
                'license': 'Various',
                'type': 'historical_library',
                'scraping_enabled': True,
                'search_terms': ['London', 'Strype', 'survey', 'parliamentary']
            },
            'uk_data_service': {
                'name': 'UK Data Service',
                'description': 'Social and economic data including GIS of Ancient Parishes',
                'time_period': (1500, 1850),
                'format': 'GIS/CSV',
                'url': 'https://beta.ukdataservice.ac.uk/',
                'scrape_url': 'https://beta.ukdataservice.ac.uk/',
                'license': 'Various',
                'type': 'geospatial_data',
                'scraping_enabled': True,
                'search_terms': ['London', 'parishes', '1500-1850', 'GIS']
            },
            'connected_histories': {
                'name': 'Connected Histories',
                'description': 'Federated search across multiple historical resources',
                'time_period': (1500, 1900),
                'format': 'HTML/XML',
                'url': 'https://www.connectedhistories.org/',
                'scrape_url': 'https://www.connectedhistories.org/',
                'license': 'Various',
                'type': 'federated_search',
                'scraping_enabled': True,
                'search_terms': ['London', 'manuscripts', 'newspapers', 'archives']
            }
        }
        
        # Additional Project Gutenberg sources for London
        self.gutenberg_sources = [
            {'id': '1342', 'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'year': 1813, 'type': 'novel'},
            {'id': '46', 'title': 'A Christmas Carol', 'author': 'Charles Dickens', 'year': 1843, 'type': 'novella'},
            {'id': '730', 'title': 'Oliver Twist', 'author': 'Charles Dickens', 'year': 1838, 'type': 'novel'},
            {'id': '768', 'title': 'Wuthering Heights', 'author': 'Emily Brontë', 'year': 1847, 'type': 'novel'},
            {'id': '1260', 'title': 'Jane Eyre', 'author': 'Charlotte Brontë', 'year': 1847, 'type': 'novel'},
            {'id': '514', 'title': 'Little Women', 'author': 'Louisa May Alcott', 'year': 1868, 'type': 'novel'},
            {'id': '11', 'title': 'Alice\'s Adventures in Wonderland', 'author': 'Lewis Carroll', 'year': 1865, 'type': 'children_novel'},
            {'id': '74', 'title': 'The Adventures of Tom Sawyer', 'author': 'Mark Twain', 'year': 1876, 'type': 'novel'},
            {'id': '76', 'title': 'Adventures of Huckleberry Finn', 'author': 'Mark Twain', 'year': 1884, 'type': 'novel'},
            {'id': '345', 'title': 'Dracula', 'author': 'Bram Stoker', 'year': 1897, 'type': 'gothic_novel'},
            {'id': '174', 'title': 'The Picture of Dorian Gray', 'author': 'Oscar Wilde', 'year': 1890, 'type': 'gothic_novel'},
            {'id': '84', 'title': 'Frankenstein', 'author': 'Mary Shelley', 'year': 1818, 'type': 'gothic_novel'},
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
    
    def download_file(self, url, filename, source_name="Unknown"):
        """Download a file with progress tracking and error handling"""
        try:
            logger.info(f"Downloading {source_name}: {filename}")
            
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
            logger.error(f"❌ Failed to download {filename}: {str(e)}")
            self.stats['failed_downloads'] += 1
            self.stats['errors'].append(f"Download error for {filename}: {str(e)}")
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
    
    def process_xml_data(self, xml_file_path, source_type):
        """Process XML data and extract text content"""
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            texts = []
            
            if source_type == 'london_lives':
                # Process London Lives XML structure
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        texts.append(elem.text.strip())
            
            elif source_type == 'old_bailey':
                # Process Old Bailey XML structure
                for trial in root.findall('.//trial'):
                    # Extract trial text
                    trial_text = ""
                    for elem in trial.iter():
                        if elem.text and elem.text.strip():
                            trial_text += elem.text.strip() + " "
                    if trial_text.strip():
                        texts.append(trial_text.strip())
            
            return "\n\n".join(texts)
            
        except Exception as e:
            logger.error(f"Error processing XML file {xml_file_path}: {str(e)}")
            return None
    
    def process_csv_data(self, csv_file_path):
        """Process CSV data and extract text content"""
        try:
            texts = []
            
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Combine all text fields
                    row_text = " ".join([str(v) for k, v in row.items() if v and str(v).strip()])
                    if row_text.strip():
                        texts.append(row_text.strip())
            
            return "\n\n".join(texts)
            
        except Exception as e:
            logger.error(f"Error processing CSV file {csv_file_path}: {str(e)}")
            return None
    
    def scrape_website(self, url, search_terms=None, max_pages=5):
        """Scrape text content from a website"""
        try:
            logger.info(f"Scraping website: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            texts = []
            
            # Look for main content areas
            content_selectors = [
                'main', 'article', '.content', '.main-content', 
                '.text', '.document', '.manuscript', '.record'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body')
            
            if main_content:
                # Extract text from paragraphs and divs
                for element in main_content.find_all(['p', 'div', 'span', 'td', 'li']):
                    text = element.get_text(strip=True)
                    if text and len(text) > 50:  # Only substantial text
                        # Check if it contains search terms (if provided)
                        if search_terms:
                            if any(term.lower() in text.lower() for term in search_terms):
                                texts.append(text)
                        else:
                            texts.append(text)
            
            # If no specific content found, get all text
            if not texts:
                all_text = soup.get_text()
                # Clean up the text
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                texts = [line for line in lines if len(line) > 50]
            
            return "\n\n".join(texts[:100])  # Limit to first 100 text blocks
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def search_and_scrape(self, base_url, search_terms, max_results=10):
        """Search a website and scrape results"""
        try:
            logger.info(f"Searching {base_url} for: {', '.join(search_terms)}")
            
            # Try to find search functionality
            search_urls = []
            
            # Common search URL patterns
            search_patterns = [
                f"{base_url}/search?q={{term}}",
                f"{base_url}/search?query={{term}}",
                f"{base_url}/browse?q={{term}}",
                f"{base_url}/catalog?q={{term}}"
            ]
            
            for term in search_terms[:3]:  # Limit to first 3 terms
                for pattern in search_patterns:
                    search_url = pattern.format(term=term)
                    search_urls.append(search_url)
            
            all_texts = []
            
            for search_url in search_urls[:max_results]:
                try:
                    response = self.session.get(search_url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Look for result links
                        result_links = []
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if any(term.lower() in href.lower() or term.lower() in link.get_text().lower() 
                                   for term in search_terms):
                                if href.startswith('http'):
                                    result_links.append(href)
                                elif href.startswith('/'):
                                    result_links.append(urljoin(base_url, href))
                        
                        # Scrape each result
                        for link in result_links[:5]:  # Limit to 5 results per search
                            text = self.scrape_website(link, search_terms)
                            if text:
                                all_texts.append(text)
                            
                            time.sleep(1)  # Be respectful
                            
                except Exception as e:
                    logger.warning(f"Error with search URL {search_url}: {str(e)}")
                    continue
            
            return "\n\n".join(all_texts) if all_texts else None
            
        except Exception as e:
            logger.error(f"Error searching {base_url}: {str(e)}")
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
            
            # Check if within our time period
            if not (self.time_period[0] <= source_info['time_period'][1] and 
                    self.time_period[1] >= source_info['time_period'][0]):
                logger.info(f"   ⏭️ Skipping - outside time period")
                continue
            
            try:
                text_content = None
                files_downloaded = 0
                
                # Try direct download first
                if 'download_url' in source_info:
                    filename = f"{source_key}_{source_info['format'].lower()}.{source_info['format'].lower()}"
                    file_path = self.download_file(source_info['download_url'], filename, source_info['name'])
                    
                    if file_path:
                        files_downloaded += 1
                        # Process the downloaded file
                        if source_info['format'] == 'XML':
                            text_content = self.process_xml_data(file_path, source_key)
                        elif source_info['format'] == 'CSV':
                            text_content = self.process_csv_data(file_path)
                        else:
                            # For TXT files, read directly
                            with open(file_path, 'r', encoding='utf-8') as f:
                                text_content = f.read()
                
                # Try multiple download URLs
                elif 'download_urls' in source_info:
                    all_texts = []
                    for i, url in enumerate(source_info['download_urls']):
                        filename = f"{source_key}_{i}_{source_info['format'].lower()}.{source_info['format'].lower()}"
                        file_path = self.download_file(url, filename, f"{source_info['name']} (part {i+1})")
                        
                        if file_path:
                            files_downloaded += 1
                            # Process the downloaded file
                            if source_info['format'] == 'XML':
                                part_text = self.process_xml_data(file_path, source_key)
                            elif source_info['format'] == 'CSV':
                                part_text = self.process_csv_data(file_path)
                            else:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    part_text = f.read()
                            
                            if part_text:
                                all_texts.append(part_text)
                    
                    if all_texts:
                        text_content = "\n\n".join(all_texts)
                
                # Try web scraping if enabled and no direct download worked
                if not text_content and source_info.get('scraping_enabled', False):
                    logger.info(f"   🔍 Attempting web scraping...")
                    
                    if 'scrape_url' in source_info:
                        scrape_url = source_info['scrape_url']
                        search_terms = source_info.get('search_terms', [])
                        
                        if search_terms:
                            # Search and scrape
                            text_content = self.search_and_scrape(scrape_url, search_terms)
                        else:
                            # Direct scrape
                            text_content = self.scrape_website(scrape_url)
                        
                        if text_content:
                            files_downloaded += 1
                            logger.info(f"   ✅ Successfully scraped content")
                
                # Save processed text if we have content
                if text_content and len(text_content) > 1000:
                    text_filename = f"{source_key}_processed.txt"
                    text_path = self.output_dir / text_filename
                    
                    with open(text_path, 'w', encoding='utf-8') as f:
                        f.write(f"Source: {source_info['name']}\n")
                        f.write(f"Description: {source_info['description']}\n")
                        f.write(f"Time Period: {source_info['time_period'][0]}-{source_info['time_period'][1]}\n")
                        f.write(f"License: {source_info['license']}\n")
                        f.write(f"Method: {'Download' if 'download_url' in source_info else 'Scraping'}\n")
                        f.write("="*50 + "\n\n")
                        f.write(text_content)
                    
                    logger.info(f"   ✅ Processed and saved: {text_filename}")
                    self.stats['successful_downloads'] += 1
                    self.stats['total_size_mb'] += len(text_content.encode('utf-8')) / (1024 * 1024)
                else:
                    logger.warning(f"   ⚠️ No text content extracted from {source_info['name']}")
                    self.stats['failed_downloads'] += 1
                
                # Update source statistics
                self.stats['source_stats'][source_key] = {
                    'name': source_info['name'],
                    'status': 'completed' if text_content else 'failed',
                    'files_downloaded': files_downloaded,
                    'time_period': source_info['time_period'],
                    'method': 'download' if 'download_url' in source_info else 'scraping'
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
            
            # Small delay between sources
            time.sleep(2)
    
    def download_gutenberg_sources(self):
        """Download from Project Gutenberg sources"""
        logger.info("\n📚 Downloading Project Gutenberg sources...")
        
        for source in tqdm(self.gutenberg_sources, desc="Downloading Gutenberg texts"):
            self.stats['total_attempted'] += 1
            
            # Check if within time period
            if not (self.time_period[0] <= source['year'] <= self.time_period[1]):
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
                    f.write("="*50 + "\n\n")
                    f.write(text_content)
                
                logger.info(f"✅ Saved: {filename}")
            else:
                self.stats['failed_downloads'] += 1
                self.stats['errors'].append(f"Failed to download {source['title']}")
            
            # Small delay to be respectful
            time.sleep(0.5)
    
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
                        with open(text_file, 'r', encoding='utf-8') as infile:
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
    
    def save_statistics(self):
        """Save download statistics to JSON file"""
        stats_file = self.output_dir / "comprehensive_download_statistics.json"
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Statistics saved to: {stats_file}")
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
    
    def print_summary(self):
        """Print download summary"""
        print("\n" + "="*70)
        print("🏛️ COMPREHENSIVE LONDON HISTORICAL DATA COLLECTION SUMMARY")
        print("="*70)
        print(f"Total sources attempted: {self.stats['total_attempted']}")
        print(f"Successful downloads: {self.stats['successful_downloads']}")
        print(f"Failed downloads: {self.stats['failed_downloads']}")
        print(f"Total size: {self.stats['total_size_mb']:.2f} MB")
        print(f"Success rate: {(self.stats['successful_downloads']/max(1, self.stats['total_attempted'])*100):.1f}%")
        
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
        
        print("="*70)

def main():
    """Main comprehensive data preparation pipeline"""
    print("🏛️ London Historical LLM - Comprehensive Data Downloader (1500-1850)")
    print("=" * 80)
    print("📚 Downloading from multiple historical sources:")
    print("\n🔸 London Lives 1690-1800 (240,000 manuscript pages)")
    print("🔸 Old Bailey Proceedings (197,000+ trial accounts)")
    print("🔸 Locating London's Past (Geo-referenced data)")
    print("🔸 Historical Books & Manuscripts")
    print("🔸 Project Gutenberg London Literature")
    print("=" * 80)
    
    # Initialize downloader
    downloader = ComprehensiveLondonDataDownloader(time_period=(1500, 1850))
    
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
    
    # Save statistics
    downloader.save_statistics()
    
    # Print summary
    downloader.print_summary()
    
    print(f"\n🎉 Comprehensive data collection complete!")
    print(f"📁 Data saved to: {downloader.output_dir}")
    print(f"📄 Historical corpus file: {corpus_path}")
    print(f"\n💡 Next steps:")
    print(f"   1. Train custom tokenizer: python train_custom_tokenizer.py")
    print(f"   2. Prepare dataset: python prepare_dataset.py")
    print(f"   3. Start training: ./launch_2gpu.sh")

if __name__ == "__main__":
    main()
