#!/usr/bin/env python3
"""
Advanced London Historical Data Processor
Handles XML, CSV, and structured data from historical sources
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedLondonDataProcessor:
    def __init__(self, data_dir="data/london_historical"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics tracking
        self.stats = {
            'files_processed': 0,
            'records_extracted': 0,
            'text_length': 0,
            'errors': [],
            'source_stats': {}
        }
        
        # XML namespaces for different sources
        self.namespaces = {
            'london_lives': {
                'll': 'http://www.londonlives.org/',
                'tei': 'http://www.tei-c.org/ns/1.0'
            },
            'old_bailey': {
                'ob': 'http://www.oldbaileyonline.org/',
                'tei': 'http://www.tei-c.org/ns/1.0'
            }
        }
    
    def process_london_lives_xml(self, xml_file_path: str) -> Dict[str, Any]:
        """Process London Lives XML data and extract structured information"""
        logger.info(f"Processing London Lives XML: {xml_file_path}")
        
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Define namespace
            ns = self.namespaces['london_lives']
            
            # Extract different types of records
            records = {
                'criminal_records': [],
                'parish_records': [],
                'poor_law_records': [],
                'apprenticeship_records': [],
                'hospital_records': [],
                'other_records': []
            }
            
            # Process different record types
            for record_type in records.keys():
                # Look for records with specific tags or attributes
                xpath_query = f".//tei:div[@type='{record_type}']"
                elements = root.findall(xpath_query, ns)
                
                for element in elements:
                    record = self._extract_london_lives_record(element, record_type)
                    if record:
                        records[record_type].append(record)
            
            # Extract general text content
            text_content = self._extract_text_content(root, ns)
            
            # Create processed output
            processed_data = {
                'source': 'London Lives',
                'file_path': xml_file_path,
                'processing_date': datetime.now().isoformat(),
                'record_counts': {k: len(v) for k, v in records.items()},
                'total_records': sum(len(v) for v in records.values()),
                'text_content': text_content,
                'structured_records': records
            }
            
            self.stats['files_processed'] += 1
            self.stats['records_extracted'] += processed_data['total_records']
            self.stats['text_length'] += len(text_content)
            
            logger.info(f"✅ Processed {processed_data['total_records']} records from London Lives")
            return processed_data
            
        except Exception as e:
            error_msg = f"Error processing London Lives XML {xml_file_path}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
    
    def process_old_bailey_xml(self, xml_file_path: str) -> Dict[str, Any]:
        """Process Old Bailey XML data and extract trial information"""
        logger.info(f"Processing Old Bailey XML: {xml_file_path}")
        
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Define namespace
            ns = self.namespaces['old_bailey']
            
            # Extract trial information
            trials = []
            
            # Look for trial elements
            trial_elements = root.findall(".//tei:div[@type='trialAccount']", ns)
            
            for trial_element in trial_elements:
                trial = self._extract_old_bailey_trial(trial_element, ns)
                if trial:
                    trials.append(trial)
            
            # Extract general text content
            text_content = self._extract_text_content(root, ns)
            
            # Create processed output
            processed_data = {
                'source': 'Old Bailey Proceedings',
                'file_path': xml_file_path,
                'processing_date': datetime.now().isoformat(),
                'trial_count': len(trials),
                'text_content': text_content,
                'trials': trials
            }
            
            self.stats['files_processed'] += 1
            self.stats['records_extracted'] += len(trials)
            self.stats['text_length'] += len(text_content)
            
            logger.info(f"✅ Processed {len(trials)} trials from Old Bailey")
            return processed_data
            
        except Exception as e:
            error_msg = f"Error processing Old Bailey XML {xml_file_path}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
    
    def process_government_records(self, data_file_path: str) -> Dict[str, Any]:
        """Process government records and census data"""
        logger.info(f"Processing government records: {data_file_path}")
        
        try:
            file_path = Path(data_file_path)
            
            if file_path.suffix.lower() == '.csv':
                return self._process_csv_government_data(data_file_path)
            elif file_path.suffix.lower() == '.xml':
                return self._process_xml_government_data(data_file_path)
            elif file_path.suffix.lower() == '.json':
                return self._process_json_government_data(data_file_path)
            else:
                logger.warning(f"Unsupported file format: {file_path.suffix}")
                return None
                
        except Exception as e:
            error_msg = f"Error processing government records {data_file_path}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
    
    def process_digitized_books(self, book_file_path: str) -> Dict[str, Any]:
        """Process digitized historical books"""
        logger.info(f"Processing digitized book: {book_file_path}")
        
        try:
            file_path = Path(book_file_path)
            
            if file_path.suffix.lower() == '.txt':
                return self._process_txt_book(book_file_path)
            elif file_path.suffix.lower() == '.pdf':
                return self._process_pdf_book(book_file_path)
            else:
                logger.warning(f"Unsupported book format: {file_path.suffix}")
                return None
                
        except Exception as e:
            error_msg = f"Error processing digitized book {book_file_path}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
    
    def _extract_london_lives_record(self, element: ET.Element, record_type: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from a London Lives record element"""
        try:
            record = {
                'type': record_type,
                'id': element.get('xml:id', ''),
                'date': '',
                'person_name': '',
                'location': '',
                'text_content': '',
                'metadata': {}
            }
            
            # Extract date information
            date_elem = element.find('.//tei:date', self.namespaces['london_lives'])
            if date_elem is not None:
                record['date'] = date_elem.get('when', date_elem.text or '')
            
            # Extract person names
            name_elems = element.findall('.//tei:persName', self.namespaces['london_lives'])
            if name_elems:
                record['person_name'] = name_elems[0].text or ''
            
            # Extract location information
            place_elem = element.find('.//tei:placeName', self.namespaces['london_lives'])
            if place_elem is not None:
                record['location'] = place_elem.text or ''
            
            # Extract text content
            text_elem = element.find('.//tei:p', self.namespaces['london_lives'])
            if text_elem is not None:
                record['text_content'] = self._clean_text(text_elem.text or '')
            
            # Extract additional metadata
            for attr_name, attr_value in element.attrib.items():
                if attr_name not in ['xml:id']:
                    record['metadata'][attr_name] = attr_value
            
            return record if record['text_content'] else None
            
        except Exception as e:
            logger.warning(f"Error extracting London Lives record: {str(e)}")
            return None
    
    def _extract_old_bailey_trial(self, element: ET.Element, ns: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract structured data from an Old Bailey trial element"""
        try:
            trial = {
                'trial_id': element.get('xml:id', ''),
                'date': '',
                'defendant_name': '',
                'crime': '',
                'verdict': '',
                'sentence': '',
                'text_content': '',
                'witnesses': [],
                'metadata': {}
            }
            
            # Extract date
            date_elem = element.find('.//tei:date', ns)
            if date_elem is not None:
                trial['date'] = date_elem.get('when', date_elem.text or '')
            
            # Extract defendant name
            defendant_elem = element.find('.//tei:persName[@role="defendant"]', ns)
            if defendant_elem is not None:
                trial['defendant_name'] = defendant_elem.text or ''
            
            # Extract crime description
            crime_elem = element.find('.//tei:rs[@type="offenceDescription"]', ns)
            if crime_elem is not None:
                trial['crime'] = crime_elem.text or ''
            
            # Extract verdict
            verdict_elem = element.find('.//tei:rs[@type="verdict"]', ns)
            if verdict_elem is not None:
                trial['verdict'] = verdict_elem.text or ''
            
            # Extract sentence
            sentence_elem = element.find('.//tei:rs[@type="punishment"]', ns)
            if sentence_elem is not None:
                trial['sentence'] = sentence_elem.text or ''
            
            # Extract text content
            text_content = []
            for p_elem in element.findall('.//tei:p', ns):
                if p_elem.text:
                    text_content.append(self._clean_text(p_elem.text))
            trial['text_content'] = ' '.join(text_content)
            
            # Extract witnesses
            witness_elems = element.findall('.//tei:persName[@role="witness"]', ns)
            for witness_elem in witness_elems:
                if witness_elem.text:
                    trial['witnesses'].append(witness_elem.text.strip())
            
            return trial if trial['text_content'] else None
            
        except Exception as e:
            logger.warning(f"Error extracting Old Bailey trial: {str(e)}")
            return None
    
    def _extract_text_content(self, root: ET.Element, ns: Dict[str, str]) -> str:
        """Extract clean text content from XML element"""
        try:
            # Get all text content
            text_parts = []
            
            # Extract from paragraphs
            for p_elem in root.findall('.//tei:p', ns):
                if p_elem.text:
                    text_parts.append(self._clean_text(p_elem.text))
            
            # If no paragraphs, get all text
            if not text_parts:
                all_text = ET.tostring(root, encoding='unicode', method='text')
                text_parts.append(self._clean_text(all_text))
            
            return ' '.join(text_parts)
            
        except Exception as e:
            logger.warning(f"Error extracting text content: {str(e)}")
            return ''
    
    def _process_csv_government_data(self, csv_file_path: str) -> Dict[str, Any]:
        """Process CSV government data"""
        try:
            df = pd.read_csv(csv_file_path)
            
            # Extract text content from all columns
            text_content = []
            for column in df.columns:
                if df[column].dtype == 'object':  # Text columns
                    text_content.extend(df[column].dropna().astype(str).tolist())
            
            processed_data = {
                'source': 'Government Records (CSV)',
                'file_path': csv_file_path,
                'processing_date': datetime.now().isoformat(),
                'record_count': len(df),
                'columns': list(df.columns),
                'text_content': ' '.join(text_content),
                'data': df.to_dict('records')
            }
            
            self.stats['files_processed'] += 1
            self.stats['records_extracted'] += len(df)
            self.stats['text_length'] += len(processed_data['text_content'])
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"Error processing CSV government data: {str(e)}")
    
    def _process_xml_government_data(self, xml_file_path: str) -> Dict[str, Any]:
        """Process XML government data"""
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Extract text content
            text_content = self._extract_text_content(root, {})
            
            processed_data = {
                'source': 'Government Records (XML)',
                'file_path': xml_file_path,
                'processing_date': datetime.now().isoformat(),
                'text_content': text_content,
                'root_tag': root.tag,
                'attributes': root.attrib
            }
            
            self.stats['files_processed'] += 1
            self.stats['text_length'] += len(text_content)
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"Error processing XML government data: {str(e)}")
    
    def _process_json_government_data(self, json_file_path: str) -> Dict[str, Any]:
        """Process JSON government data"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text content
            text_content = self._extract_text_from_json(data)
            
            processed_data = {
                'source': 'Government Records (JSON)',
                'file_path': json_file_path,
                'processing_date': datetime.now().isoformat(),
                'text_content': text_content,
                'data': data
            }
            
            self.stats['files_processed'] += 1
            self.stats['text_length'] += len(text_content)
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"Error processing JSON government data: {str(e)}")
    
    def _process_txt_book(self, txt_file_path: str) -> Dict[str, Any]:
        """Process plain text book"""
        try:
            with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            cleaned_content = self._clean_text(content)
            
            processed_data = {
                'source': 'Digitized Book (TXT)',
                'file_path': txt_file_path,
                'processing_date': datetime.now().isoformat(),
                'text_content': cleaned_content,
                'original_length': len(content),
                'cleaned_length': len(cleaned_content)
            }
            
            self.stats['files_processed'] += 1
            self.stats['text_length'] += len(cleaned_content)
            
            return processed_data
            
        except Exception as e:
            raise Exception(f"Error processing TXT book: {str(e)}")
    
    def _process_pdf_book(self, pdf_file_path: str) -> Dict[str, Any]:
        """Process PDF book (placeholder - would need PyPDF2 or similar)"""
        logger.warning(f"PDF processing not implemented for {pdf_file_path}")
        return None
    
    def _extract_text_from_json(self, data: Any) -> str:
        """Recursively extract text from JSON data"""
        text_parts = []
        
        if isinstance(data, dict):
            for value in data.values():
                text_parts.append(self._extract_text_from_json(value))
        elif isinstance(data, list):
            for item in data:
                text_parts.append(self._extract_text_from_json(item))
        elif isinstance(data, str):
            text_parts.append(data)
        
        return ' '.join(text_parts)
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'"]', '', text)
        
        # Clean up quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[''']', "'", text)
        
        return text.strip()
    
    def save_processed_data(self, processed_data: Dict[str, Any], output_filename: str) -> str:
        """Save processed data to file"""
        try:
            output_path = self.data_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved processed data: {output_path}")
            return str(output_path)
            
        except Exception as e:
            error_msg = f"Error saving processed data: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
    
    def create_training_corpus(self, processed_files: List[str], output_filename: str = "advanced_london_corpus.txt") -> str:
        """Create training corpus from processed files"""
        logger.info("Creating advanced training corpus...")
        
        try:
            output_path = self.data_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for file_path in processed_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            data = json.load(infile)
                        
                        # Write source header
                        f.write(f"SOURCE: {data.get('source', 'Unknown')}\n")
                        f.write(f"FILE: {data.get('file_path', 'Unknown')}\n")
                        f.write(f"PROCESSED: {data.get('processing_date', 'Unknown')}\n")
                        f.write("="*80 + "\n\n")
                        
                        # Write text content
                        f.write(data.get('text_content', ''))
                        f.write("\n\n" + "="*80 + "\n\n")
                        
                    except Exception as e:
                        logger.warning(f"Error processing file {file_path}: {str(e)}")
                        continue
            
            logger.info(f"✅ Advanced corpus created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            error_msg = f"Error creating training corpus: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
    
    def save_statistics(self) -> str:
        """Save processing statistics"""
        stats_file = self.data_dir / "advanced_processing_statistics.json"
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Statistics saved: {stats_file}")
            return str(stats_file)
            
        except Exception as e:
            logger.error(f"Error saving statistics: {str(e)}")
            return None

def main():
    """Test the advanced data processor"""
    print("🔧 Advanced London Data Processor - Test")
    print("=" * 50)
    
    processor = AdvancedLondonDataProcessor()
    
    # Test with sample data
    print("📊 Processor initialized")
    print(f"   Data directory: {processor.data_dir}")
    print(f"   Namespaces configured: {len(processor.namespaces)}")
    
    # Save test statistics
    stats_file = processor.save_statistics()
    if stats_file:
        print(f"✅ Statistics saved: {stats_file}")
    
    print("\n💡 Ready to process historical data files!")
    print("   Use: processor.process_london_lives_xml('file.xml')")
    print("   Use: processor.process_old_bailey_xml('file.xml')")
    print("   Use: processor.process_government_records('file.csv')")

if __name__ == "__main__":
    main()
