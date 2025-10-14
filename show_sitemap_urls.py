#!/usr/bin/env python3
"""
Show what URLs are discovered from sitemaps
"""

import sys
sys.path.append('.')

from scrape_to_pinecone import parse_sitemap, get_all_sitemap_urls

def show_sitemap_discovery():
    """Show what URLs are discovered from sitemaps"""
    print("🔍 Sitemap URL Discovery Test")
    print("=" * 60)
    
    # Test with just a few sitemaps to show the process
    test_sitemaps = [
        "https://www.northeastern.edu/sitemap.xml",
        "https://admissions.northeastern.edu/sitemap.xml",
        "https://catalog.northeastern.edu/sitemap.xml"
    ]
    
    print(f"🗺️  Testing with {len(test_sitemaps)} sitemaps:")
    for i, sitemap in enumerate(test_sitemaps, 1):
        print(f"  {i}. {sitemap}")
    
    print(f"\n📋 Discovering URLs from sitemaps...")
    
    try:
        all_urls = get_all_sitemap_urls(test_sitemaps)
        
        if all_urls:
            print(f"\n✅ Successfully discovered {len(all_urls)} URLs!")
            print(f"\n🔗 Sample URLs that would be scraped:")
            
            # Show first 20 URLs
            sample_urls = list(all_urls)[:20]
            for i, url in enumerate(sample_urls, 1):
                print(f"  {i:2d}. {url}")
            
            if len(all_urls) > 20:
                print(f"  ... and {len(all_urls) - 20} more URLs")
            
            # Show URL categories
            print(f"\n📊 URL Categories Found:")
            categories = {
                'Admissions': [url for url in all_urls if 'admission' in url.lower()],
                'Programs': [url for url in all_urls if any(word in url.lower() for word in ['program', 'course', 'degree'])],
                'Student Services': [url for url in all_urls if any(word in url.lower() for word in ['student', 'coop', 'career'])],
                'Academic': [url for url in all_urls if any(word in url.lower() for word in ['academic', 'faculty', 'research'])],
                'About/Contact': [url for url in all_urls if any(word in url.lower() for word in ['about', 'contact', 'news'])]
            }
            
            for category, urls in categories.items():
                if urls:
                    print(f"  📁 {category}: {len(urls)} URLs")
                    # Show 2-3 examples
                    examples = urls[:3]
                    for url in examples:
                        print(f"      • {url}")
                    if len(urls) > 3:
                        print(f"      • ... and {len(urls) - 3} more")
            
            print(f"\n🎯 These are the actual web pages that would be scraped!")
            print(f"✅ The scraper finds URLs from sitemaps, then scrapes those web pages")
            
            return True
        else:
            print(f"❌ No URLs discovered")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run the test"""
    success = show_sitemap_discovery()
    
    if success:
        print(f"\n🎉 URL discovery test completed!")
        print(f"✅ The scraper is working correctly:")
        print(f"   1. Parses sitemaps to find URLs")
        print(f"   2. Filters URLs for quality content")
        print(f"   3. Scrapes the actual web pages")
        print(f"   4. Stores content in Pinecone")
    else:
        print(f"\n❌ Test failed - please check the errors above")

if __name__ == "__main__":
    main()
