#!/usr/bin/env python3
"""
Update script to add enhanced data sources to existing corpus
"""

import os
import shutil
from pathlib import Path

def update_data_sources():
    """Update the data preparation to use enhanced sources"""
    print("🔄 Updating London Historical LLM Data Sources")
    print("=" * 50)
    
    # Check if enhanced script exists
    if not os.path.exists("data_preparation_enhanced.py"):
        print("❌ Enhanced data preparation script not found!")
        return False
    
    # Backup original script
    if os.path.exists("data_preparation_fixed.py"):
        shutil.copy("data_preparation_fixed.py", "data_preparation_fixed_backup.py")
        print("✅ Backed up original script")
    
    # Replace with enhanced version
    shutil.copy("data_preparation_enhanced.py", "data_preparation_fixed.py")
    print("✅ Updated data preparation script with enhanced sources")
    
    print("\n📚 New sources added:")
    print("   • Samuel Pepys' Diary (1660-1669)")
    print("   • The Gentleman's Magazine (1731-1850)")
    print("   • Horace Walpole's Letters (1740s-1790s)")
    print("   • The London Spy by Ned Ward (1698-1709)")
    print("   • Daniel Defoe's Tour (1724-1726)")
    print("   • Fanny Burney's Diaries (1770s-1840s)")
    print("   • James Boswell's London Journal (1762-1763)")
    print("   • The Microcosm of London (1808-1810)")
    
    print("\n🚀 Ready to run enhanced data collection!")
    print("   Run: python data_preparation_fixed.py")
    
    return True

if __name__ == "__main__":
    update_data_sources()
