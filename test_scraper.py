#!/usr/bin/env python3
"""
Test the scraper with a single URL to make sure it works
"""

import sys
sys.path.append('.')

from scrape_to_pinecone import scrape_url, extract_content
from bs4 import BeautifulSoup
import requests

def test_single_url():
    """Test scraping a single URL"""
    print("🧪 Testing scraper with a single URL...")
    
    test_url = "https://www.northeastern.edu/"
    
    try:
        # Test the scraping function
        docs = scrape_url(test_url)
        
        if docs:
            doc = docs[0]
            print(f"✅ Successfully scraped {test_url}")
            print(f"📄 Content length: {len(doc['content'])} characters")
            print(f"📝 Title: {doc['metadata']['title']}")
            print(f"🔗 URL: {doc['metadata']['url']}")
            print(f"\n📖 Content preview (first 300 chars):")
            print(doc['content'][:300] + "...")
            return True
        else:
            print(f"❌ No content extracted from {test_url}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_content_extraction():
    """Test content extraction with a simple HTML"""
    print("\n🧪 Testing content extraction...")
    
    html = """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <nav>Navigation</nav>
        <main>
            <h1>Northeastern University</h1>
            <p>This is a test page about Northeastern University. It contains information about admissions, programs, and student life.</p>
            <p>Northeastern is a private research university located in Boston, Massachusetts.</p>
        </main>
        <footer>Copyright 2024</footer>
    </body>
    </html>
    """
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        content = extract_content(soup)
        
        if content:
            print(f"✅ Content extraction successful")
            print(f"📄 Extracted content: {content}")
            return True
        else:
            print(f"❌ No content extracted")
            return False
            
    except Exception as e:
        print(f"❌ Content extraction test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Northeastern University Scraper Test")
    print("=" * 50)
    
    # Test content extraction
    test1 = test_content_extraction()
    
    # Test single URL scraping
    test2 = test_single_url()
    
    print(f"\n📊 Test Results:")
    print(f"Content Extraction: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"URL Scraping: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print(f"\n🎉 All tests passed! The scraper is ready to use.")
        print(f"Run: python scrape_to_pinecone.py")
    else:
        print(f"\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
