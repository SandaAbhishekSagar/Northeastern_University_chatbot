#!/usr/bin/env python3
"""
Single Sitemap Scraper for Northeastern University Chatbot
Scrapes a single URL sitemap and adds documents to existing ChromaDB
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def scrape_single_sitemap(sitemap_url, spider_name="northeastern_sitemap"):
    """
    Scrape a single sitemap URL and add documents to existing ChromaDB
    
    Args:
        sitemap_url (str): The sitemap URL to scrape
        spider_name (str): Name of the spider to use
    """
    
    print(f"🕷️ Starting single sitemap scrape for: {sitemap_url}")
    print("=" * 60)
    
    # Navigate to scraping service directory
    scraping_dir = Path("services/scraping_service")
    if not scraping_dir.exists():
        print("❌ Scraping service directory not found!")
        return False
    
    # Change to scraping directory
    os.chdir(scraping_dir)
    
    try:
        # Run scrapy crawl with single sitemap URL
        cmd = [
            sys.executable, "-m", "scrapy", "crawl", spider_name,
            "-a", f"sitemap_urls={sitemap_url}",
            "-s", "LOG_LEVEL=INFO"
        ]
        
        print(f"🚀 Running command: {' '.join(cmd)}")
        print("-" * 40)
        
        # Run the scraper
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        if result.returncode == 0:
            print("✅ Scraping completed successfully!")
            print(f"📄 Output: {result.stdout}")
            return True
        else:
            print("❌ Scraping failed!")
            print(f"🔴 Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Scraping timed out after 1 hour")
        return False
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return False
    finally:
        # Return to original directory
        os.chdir("../..")

def list_available_sitemaps():
    """List all available Northeastern sitemaps"""
    print("📋 Available Northeastern Sitemaps:")
    print("=" * 50)
    
    sitemaps = [
        "https://www.northeastern.edu/sitemap.xml",
        "https://catalog.northeastern.edu/sitemap.xml",
        "https://admissions.northeastern.edu/sitemap.xml",
        "https://graduate.northeastern.edu/sitemap.xml",
        "https://undergraduate.northeastern.edu/sitemap.xml",
        "https://library.northeastern.edu/sitemap.xml",
        "https://studentlife.northeastern.edu/sitemap.xml",
        "https://housing.northeastern.edu/sitemap.xml",
        "https://careers.northeastern.edu/sitemap.xml",
        "https://research.northeastern.edu/sitemap.xml",
        "https://international.northeastern.edu/sitemap.xml",
        "https://alumni.northeastern.edu/sitemap.xml",
        "https://online.northeastern.edu/sitemap.xml",
        "https://law.northeastern.edu/sitemap.xml",
        "https://damore-mckim.northeastern.edu/sitemap.xml",
        "https://bouve.northeastern.edu/sitemap.xml",
        "https://camd.northeastern.edu/sitemap.xml",
        "https://coe.northeastern.edu/sitemap.xml",
        "https://cos.northeastern.edu/sitemap.xml",
        "https://cssh.northeastern.edu/sitemap.xml",
        "https://cps.northeastern.edu/sitemap.xml"
    ]
    
    for i, sitemap in enumerate(sitemaps, 1):
        print(f"{i:2d}. {sitemap}")
    
    return sitemaps

def check_chromadb_status():
    """Check if ChromaDB is running and accessible"""
    print("🔍 Checking ChromaDB status...")
    
    try:
        # Try to import and check ChromaDB
        sys.path.append(str(Path.cwd()))
        from services.shared.chroma_service import ChromaService
        
        chroma_service = ChromaService()
        collections = chroma_service.client.list_collections()
        
        print(f"✅ ChromaDB is accessible")
        print(f"📊 Found {len(collections)} collections")
        
        # Get document count
        try:
            documents_collection = chroma_service.client.get_collection("documents")
            count = documents_collection.count()
            print(f"📄 Total documents: {count}")
        except:
            print("📄 Documents collection not found")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB not accessible: {e}")
        print("💡 Make sure ChromaDB is running: chroma run --host localhost --port 8000")
        return False

def main():
    """Main function"""
    print("🕷️ Single Sitemap Scraper for Northeastern University")
    print("=" * 60)
    
    # Check ChromaDB status
    if not check_chromadb_status():
        print("\n❌ Cannot proceed without ChromaDB access")
        return
    
    # List available sitemaps
    sitemaps = list_available_sitemaps()
    
    print("\n" + "=" * 60)
    print("🎯 Choose an option:")
    print("1. Enter a custom sitemap URL")
    print("2. Select from the list above")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Custom URL
        sitemap_url = input("Enter the sitemap URL: ").strip()
        if not sitemap_url:
            print("❌ No URL provided")
            return
        
        if not sitemap_url.startswith("http"):
            print("❌ Please provide a valid HTTP URL")
            return
            
    elif choice == "2":
        # Select from list
        try:
            selection = int(input(f"Enter number (1-{len(sitemaps)}): ").strip())
            if 1 <= selection <= len(sitemaps):
                sitemap_url = sitemaps[selection - 1]
            else:
                print("❌ Invalid selection")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
            
    elif choice == "3":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")
        return
    
    print(f"\n🎯 Selected sitemap: {sitemap_url}")
    
    # Confirm before proceeding
    confirm = input("\nProceed with scraping? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Scraping cancelled")
        return
    
    # Start scraping
    print("\n🚀 Starting scraping process...")
    success = scrape_single_sitemap(sitemap_url)
    
    if success:
        print("\n✅ Scraping completed successfully!")
        print("📄 Documents have been added to your existing ChromaDB")
        print("🔄 You can now use the enhanced GPU system with the new documents")
    else:
        print("\n❌ Scraping failed!")
        print("🔧 Check the error messages above for troubleshooting")

if __name__ == "__main__":
    main() 