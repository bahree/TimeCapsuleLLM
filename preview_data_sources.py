"""
Preview script for London Historical LLM data sources
Shows exactly what texts will be downloaded and their sources
"""

import csv
import os
from pathlib import Path

def analyze_metadata():
    """Analyze the metadata CSV to show data sources"""
    print("📚 London Historical LLM - Data Sources Preview")
    print("=" * 60)
    
    csv_path = "london_1800_1850_v0/metadata_london.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Metadata file not found: {csv_path}")
        return
    
    # Read and analyze metadata
    texts = []
    authors = {}
    years = {}
    sources = {}
    status_counts = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row['title']
            author = row['author']
            year = int(row['year']) if row['year'] else 0
            gutenberg_id = row['gutenberg_id']
            status = row['status']
            score = float(row['score']) if row['score'] else 0.0
            source_url = row['source_url']
            
            texts.append({
                'title': title,
                'author': author,
                'year': year,
                'gutenberg_id': gutenberg_id,
                'status': status,
                'score': score,
                'source_url': source_url
            })
            
            # Count by author
            if author:
                authors[author] = authors.get(author, 0) + 1
            
            # Count by year
            if year:
                decade = (year // 10) * 10
                years[decade] = years.get(decade, 0) + 1
            
            # Count by source
            if source_url:
                if 'gutenberg.org' in source_url:
                    sources['Project Gutenberg'] = sources.get('Project Gutenberg', 0) + 1
                elif 'archive.org' in source_url:
                    sources['Internet Archive'] = sources.get('Internet Archive', 0) + 1
                else:
                    sources['Other'] = sources.get('Other', 0) + 1
            
            # Count by status
            status_counts[status] = status_counts.get(status, 0) + 1
    
    # Display statistics
    print(f"📊 Dataset Statistics:")
    print(f"   Total texts: {len(texts)}")
    print(f"   Unique authors: {len(authors)}")
    print(f"   Year range: {min(years.keys()) if years else 'N/A'} - {max(years.keys()) if years else 'N/A'}")
    print()
    
    # Show sources
    print("🌐 Data Sources:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"   {source}: {count} texts")
    print()
    
    # Show status breakdown
    print("📋 Download Status:")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {status}: {count} texts")
    print()
    
    # Show top authors
    print("👥 Top Authors:")
    for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"   {author}: {count} works")
    print()
    
    # Show year distribution
    print("📅 Year Distribution:")
    for decade in sorted(years.keys()):
        print(f"   {decade}s: {years[decade]} texts")
    print()
    
    # Show available texts (with Gutenberg IDs)
    available_texts = [t for t in texts if t['gutenberg_id'] and t['status'] != 'NO_MATCH']
    print(f"✅ Available for Download: {len(available_texts)} texts")
    print()
    
    # Show sample of available texts
    print("📖 Sample Available Texts:")
    for i, text in enumerate(available_texts[:20]):
        print(f"   {i+1:2d}. {text['title']} - {text['author']} ({text['year']})")
        print(f"       Gutenberg ID: {text['gutenberg_id']}")
        print(f"       Quality Score: {text['score']:.2f}")
        print()
    
    if len(available_texts) > 20:
        print(f"   ... and {len(available_texts) - 20} more texts")
    
    return available_texts

def show_download_plan():
    """Show the download plan and process"""
    print("🚀 Download Plan:")
    print("=" * 30)
    print("1. Read metadata from CSV file")
    print("2. For each text with Gutenberg ID:")
    print("   - Try multiple URL patterns")
    print("   - Download text content")
    print("   - Clean and preprocess")
    print("   - Validate quality (>1000 chars)")
    print("   - Save individual file")
    print("3. Merge all texts into training corpus")
    print("4. Create train/validation split")
    print("5. Save training binaries")
    print()

def show_quality_control():
    """Show quality control measures"""
    print("🔍 Quality Control:")
    print("=" * 20)
    print("✓ Remove Project Gutenberg headers/footers")
    print("✓ Clean OCR errors and artifacts")
    print("✓ Remove excessive whitespace")
    print("✓ Remove page numbers and headers")
    print("✓ Validate minimum content length")
    print("✓ Check for substantial text content")
    print("✓ Standardize text format")
    print()

def show_expected_output():
    """Show expected output structure"""
    print("📁 Expected Output Structure:")
    print("=" * 35)
    print("london_data/")
    print("├── london_corpus_merged.txt     # Complete training corpus")
    print("├── data_summary.json            # Download statistics")
    print("└── individual_texts/            # Individual text files")
    print("    ├── Pride_and_Prejudice_1813.txt")
    print("    ├── Frankenstein_1818.txt")
    print("    ├── Oliver_Twist_1837.txt")
    print("    └── ... (200+ files)")
    print()
    print("data/london_data/")
    print("├── train.bin                    # Training data binary")
    print("├── val.bin                      # Validation data binary")
    print("└── meta.pkl                     # Metadata and vocab info")
    print()

def main():
    """Main preview function"""
    print("🏛️  London Historical LLM - Data Sources Preview")
    print("=" * 60)
    
    # Analyze metadata
    available_texts = analyze_metadata()
    
    if not available_texts:
        print("❌ No texts available for download")
        return
    
    # Show download plan
    show_download_plan()
    
    # Show quality control
    show_quality_control()
    
    # Show expected output
    show_expected_output()
    
    # Show estimated download size
    print("📊 Estimated Download Size:")
    print("=" * 30)
    print(f"   Texts to download: {len(available_texts)}")
    print(f"   Estimated size: ~500MB - 1GB")
    print(f"   Estimated time: 10-30 minutes")
    print()
    
    # Show next steps
    print("🚀 Next Steps:")
    print("=" * 15)
    print("1. Run: python data_preparation.py")
    print("2. Monitor download progress")
    print("3. Check london_data/ directory")
    print("4. Run: python train_tokenizer_london.py")
    print("5. Run: python train_london_llm.py")
    print()
    
    print("✅ Data sources preview complete!")

if __name__ == "__main__":
    main()
