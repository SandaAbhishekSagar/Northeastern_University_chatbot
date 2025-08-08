#!/usr/bin/env python3
"""
Quick Single Sitemap Scraper
Simple command-line tool to scrape one sitemap URL
"""

import sys
import subprocess
import os
from pathlib import Path

def quick_scrape(sitemap_url):
    """Quick scrape a single sitemap URL"""
    
    print(f"🕷️ Quick scraping: {sitemap_url}")
    print("=" * 50)
    
    # Navigate to scraping directory
    scraping_dir = Path("services/scraping_service")
    if not scraping_dir.exists():
        print("❌ Scraping service directory not found!")
        return False
    
    # Change to scraping directory
    original_dir = os.getcwd()
    os.chdir(scraping_dir)
    
    try:
        # Run scrapy crawl
        cmd = [
            sys.executable, "-m", "scrapy", "crawl", "northeastern_sitemap",
            "-a", f"sitemap_urls={sitemap_url}",
            "-s", "LOG_LEVEL=INFO"
        ]
        
        print(f"🚀 Running: {' '.join(cmd)}")
        print("-" * 40)
        
        # Run with real-time output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("\n✅ Scraping completed successfully!")
            return True
        else:
            print(f"\n❌ Scraping failed with return code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Return to original directory
        os.chdir(original_dir)

def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_scrape_single.py <sitemap_url>")
        print("\nExamples:")
        print("  python quick_scrape_single.py https://catalog.northeastern.edu/sitemap.xml")
        print("  python quick_scrape_single.py https://admissions.northeastern.edu/sitemap.xml")
        print("  python quick_scrape_single.py https://graduate.northeastern.edu/sitemap.xml")
        return
    
    sitemap_url = sys.argv[1]
    
    if not sitemap_url.startswith("http"):
        print("❌ Please provide a valid HTTP URL")
        return
    
    success = quick_scrape(sitemap_url)
    
    if success:
        print("\n🎉 Documents added to ChromaDB successfully!")
        print("🔄 You can now use the enhanced GPU system with the new documents")
    else:
        print("\n💥 Scraping failed. Check the error messages above.")

if __name__ == "__main__":
    main() 