#!/usr/bin/env python3
"""
Enhanced London Historical Data Downloader
Integrates all components: downloading, processing, error handling
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import logging

# Import our custom modules
from comprehensive_error_handler import ComprehensiveErrorHandler, error_handler_decorator
from advanced_london_data_processor import AdvancedLondonDataProcessor
from remote_london_downloader import RemoteLondonDataDownloader

class EnhancedLondonDownloader:
    def __init__(self, output_dir="data/london_historical", time_period=(1500, 1850)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.time_period = time_period
        
        # Initialize components
        self.error_handler = ComprehensiveErrorHandler(log_dir=str(self.output_dir / "logs"))
        self.data_processor = AdvancedLondonDataProcessor(data_dir=str(self.output_dir))
        self.downloader = RemoteLondonDataDownloader(
            output_dir=str(self.output_dir),
            time_period=time_period
        )
        
        # Setup logging
        self.logger = self.error_handler.logger
        
        # Statistics
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'phases_completed': [],
            'total_files_processed': 0,
            'total_records_extracted': 0,
            'total_text_length': 0,
            'errors_encountered': 0,
            'recovery_attempts': 0
        }
    
    @error_handler_decorator
    def run_complete_pipeline(self):
        """Run the complete data collection and processing pipeline"""
        self.logger.info("🚀 Starting Enhanced London Data Collection Pipeline")
        self.logger.info("=" * 70)
        
        try:
            # Phase 1: Test connectivity
            self._phase_1_test_connectivity()
            
            # Phase 2: Download data
            self._phase_2_download_data()
            
            # Phase 3: Process data
            self._phase_3_process_data()
            
            # Phase 4: Create training corpus
            self._phase_4_create_corpus()
            
            # Phase 5: Generate reports
            self._phase_5_generate_reports()
            
            self.logger.info("🎉 Enhanced pipeline completed successfully!")
            self._print_final_summary()
            
        except Exception as e:
            self.error_handler.log_error(e, "Complete pipeline execution", "CRITICAL")
            self.logger.error("❌ Pipeline failed with critical error")
            raise
    
    def _phase_1_test_connectivity(self):
        """Phase 1: Test network connectivity and system readiness"""
        self.logger.info("📡 Phase 1: Testing connectivity and system readiness")
        
        try:
            # Test network connectivity
            connectivity = self.downloader.test_network_connectivity()
            
            # Test error handler
            self.error_handler.logger.info("Error handler test")
            
            # Test data processor
            self.data_processor.logger.info("Data processor test")
            
            self.stats['phases_completed'].append('connectivity_test')
            self.logger.info("✅ Phase 1 completed: System ready")
            
        except Exception as e:
            self.error_handler.log_error(e, "Phase 1: Connectivity test", "ERROR")
            raise
    
    def _phase_2_download_data(self):
        """Phase 2: Download historical data from all sources"""
        self.logger.info("📥 Phase 2: Downloading historical data")
        
        try:
            # Download historical sources
            self.downloader.download_historical_sources()
            
            # Download Gutenberg sources
            self.downloader.download_gutenberg_sources()
            
            # Update statistics
            self.stats['total_files_processed'] += self.downloader.stats['successful_downloads']
            self.stats['errors_encountered'] += self.downloader.stats['failed_downloads']
            
            self.stats['phases_completed'].append('data_download')
            self.logger.info("✅ Phase 2 completed: Data downloaded")
            
        except Exception as e:
            self.error_handler.log_error(e, "Phase 2: Data download", "ERROR")
            raise
    
    def _phase_3_process_data(self):
        """Phase 3: Process downloaded data with advanced processor"""
        self.logger.info("🔧 Phase 3: Processing downloaded data")
        
        try:
            processed_files = []
            
            # Process all downloaded files
            for file_path in self.output_dir.glob("*.txt"):
                if file_path.name.endswith('_processed.txt'):
                    continue  # Skip already processed files
                
                try:
                    # Determine file type and process accordingly
                    if 'london_lives' in file_path.name.lower():
                        processed_data = self.data_processor.process_london_lives_xml(str(file_path))
                    elif 'old_bailey' in file_path.name.lower():
                        processed_data = self.data_processor.process_old_bailey_xml(str(file_path))
                    elif 'government' in file_path.name.lower():
                        processed_data = self.data_processor.process_government_records(str(file_path))
                    else:
                        processed_data = self.data_processor.process_digitized_books(str(file_path))
                    
                    if processed_data:
                        # Save processed data
                        output_filename = f"processed_{file_path.stem}.json"
                        saved_path = self.data_processor.save_processed_data(processed_data, output_filename)
                        
                        if saved_path:
                            processed_files.append(saved_path)
                            self.stats['total_records_extracted'] += processed_data.get('total_records', 1)
                            self.stats['total_text_length'] += len(processed_data.get('text_content', ''))
                
                except Exception as e:
                    self.error_handler.log_error(e, f"Processing file {file_path.name}", "WARNING")
                    continue
            
            self.stats['phases_completed'].append('data_processing')
            self.logger.info(f"✅ Phase 3 completed: Processed {len(processed_files)} files")
            
        except Exception as e:
            self.error_handler.log_error(e, "Phase 3: Data processing", "ERROR")
            raise
    
    def _phase_4_create_corpus(self):
        """Phase 4: Create comprehensive training corpus"""
        self.logger.info("📝 Phase 4: Creating comprehensive training corpus")
        
        try:
            # Find all processed files
            processed_files = list(self.output_dir.glob("processed_*.json"))
            
            if not processed_files:
                self.logger.warning("No processed files found, creating basic corpus")
                # Fallback to basic corpus creation
                corpus_path = self.downloader.create_merged_corpus("enhanced_london_corpus.txt")
            else:
                # Create advanced corpus
                corpus_path = self.data_processor.create_training_corpus(
                    [str(f) for f in processed_files],
                    "enhanced_london_corpus.txt"
                )
            
            if corpus_path:
                self.stats['phases_completed'].append('corpus_creation')
                self.logger.info(f"✅ Phase 4 completed: Corpus created at {corpus_path}")
            else:
                raise Exception("Failed to create training corpus")
            
        except Exception as e:
            self.error_handler.log_error(e, "Phase 4: Corpus creation", "ERROR")
            raise
    
    def _phase_5_generate_reports(self):
        """Phase 5: Generate comprehensive reports and statistics"""
        self.logger.info("📊 Phase 5: Generating reports and statistics")
        
        try:
            # Save error report
            error_report_path = self.error_handler.save_error_report("enhanced_error_report.json")
            
            # Save processing statistics
            processing_stats_path = self.data_processor.save_statistics()
            
            # Save download statistics
            download_stats_path = self.downloader.save_statistics()
            
            # Create comprehensive summary
            summary = self._create_comprehensive_summary()
            summary_path = self.output_dir / "enhanced_pipeline_summary.json"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self.stats['phases_completed'].append('report_generation')
            self.logger.info("✅ Phase 5 completed: Reports generated")
            
        except Exception as e:
            self.error_handler.log_error(e, "Phase 5: Report generation", "ERROR")
            raise
    
    def _create_comprehensive_summary(self):
        """Create a comprehensive summary of the entire pipeline"""
        end_time = datetime.now().isoformat()
        duration = (
            datetime.fromisoformat(end_time) - 
            datetime.fromisoformat(self.stats['start_time'])
        ).total_seconds() / 60
        
        summary = {
            'pipeline_info': {
                'start_time': self.stats['start_time'],
                'end_time': end_time,
                'duration_minutes': duration,
                'phases_completed': self.stats['phases_completed'],
                'status': 'completed' if len(self.stats['phases_completed']) == 5 else 'partial'
            },
            'download_stats': self.downloader.stats,
            'processing_stats': self.data_processor.stats,
            'error_stats': {
                'total_errors': len(self.error_handler.error_history),
                'error_categories': list(set(e['category'] for e in self.error_handler.error_history)),
                'recovery_attempts': self.stats['recovery_attempts']
            },
            'output_files': {
                'corpus_file': 'enhanced_london_corpus.txt',
                'error_report': 'enhanced_error_report.json',
                'download_stats': 'remote_download_statistics.json',
                'processing_stats': 'advanced_processing_statistics.json',
                'pipeline_summary': 'enhanced_pipeline_summary.json'
            },
            'recommendations': self._generate_recommendations()
        }
        
        return summary
    
    def _generate_recommendations(self):
        """Generate recommendations based on pipeline results"""
        recommendations = []
        
        # Check error rates
        total_errors = len(self.error_handler.error_history)
        if total_errors > 10:
            recommendations.append("High error rate detected - consider checking network stability")
        
        # Check download success rate
        download_success_rate = (
            self.downloader.stats['successful_downloads'] / 
            max(1, self.downloader.stats['total_attempted'])
        )
        if download_success_rate < 0.8:
            recommendations.append("Low download success rate - consider retrying failed downloads")
        
        # Check data quality
        if self.stats['total_text_length'] < 1000000:  # Less than 1MB
            recommendations.append("Limited text data collected - consider adding more sources")
        
        # Check processing success
        if self.data_processor.stats['files_processed'] == 0:
            recommendations.append("No files were processed - check data format compatibility")
        
        return recommendations
    
    def _print_final_summary(self):
        """Print final summary to console"""
        print("\n" + "="*80)
        print("🏛️ ENHANCED LONDON HISTORICAL DATA PIPELINE - COMPLETE")
        print("="*80)
        
        # Pipeline status
        print(f"📊 Pipeline Status: {'✅ COMPLETED' if len(self.stats['phases_completed']) == 5 else '⚠️ PARTIAL'}")
        print(f"⏱️ Duration: {self.stats.get('duration_minutes', 0):.1f} minutes")
        print(f"📁 Output Directory: {self.output_dir}")
        
        # Download statistics
        print(f"\n📥 Download Statistics:")
        print(f"   Files Downloaded: {self.downloader.stats['successful_downloads']}")
        print(f"   Total Size: {self.downloader.stats['total_size_mb']:.2f} MB")
        print(f"   Success Rate: {(self.downloader.stats['successful_downloads']/max(1, self.downloader.stats['total_attempted'])*100):.1f}%")
        
        # Processing statistics
        print(f"\n🔧 Processing Statistics:")
        print(f"   Files Processed: {self.data_processor.stats['files_processed']}")
        print(f"   Records Extracted: {self.data_processor.stats['records_extracted']}")
        print(f"   Text Length: {self.data_processor.stats['text_length']:,} characters")
        
        # Error statistics
        print(f"\n❌ Error Statistics:")
        print(f"   Total Errors: {len(self.error_handler.error_history)}")
        print(f"   Error Categories: {', '.join(set(e['category'] for e in self.error_handler.error_history))}")
        
        # Output files
        print(f"\n📄 Output Files:")
        print(f"   Training Corpus: enhanced_london_corpus.txt")
        print(f"   Error Report: enhanced_error_report.json")
        print(f"   Statistics: enhanced_pipeline_summary.json")
        
        # Recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        print("="*80)

def main():
    """Main function to run the enhanced downloader"""
    print("🏛️ Enhanced London Historical Data Downloader")
    print("=" * 60)
    print("🚀 Starting complete pipeline...")
    
    try:
        # Initialize enhanced downloader
        downloader = EnhancedLondonDownloader(time_period=(1500, 1850))
        
        # Run complete pipeline
        downloader.run_complete_pipeline()
        
        print("\n🎉 Enhanced pipeline completed successfully!")
        print("📁 Check the output directory for all generated files")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        print("📝 Check the logs for detailed error information")
        sys.exit(1)

if __name__ == "__main__":
    main()
