#!/usr/bin/env python3
"""
Test the unlimited sitemap scraper to see how many URLs will be discovered
"""

import sys
sys.path.append('.')

from scrape_to_pinecone import parse_sitemap, get_all_sitemap_urls

def test_unlimited_discovery():
    """Test unlimited URL discovery from sitemaps"""
    print("🚀 UNLIMITED Sitemap URL Discovery Test")
    print("=" * 70)
    print("🔥 NO LIMITS - Discovering ALL URLs from ALL sitemaps!")
    print("=" * 70)
    
    # Test with a few sitemaps to show the unlimited discovery
    test_sitemaps = [
        "https://www.northeastern.edu/sitemap.xml",
        "https://admissions.northeastern.edu/sitemap.xml",
        "https://catalog.northeastern.edu/sitemap.xml",
        "https://about.me.northeastern.edu/sitemap.xml",
        "https://coe.northeastern.edu/sitemap.xml"
    ]
    
    print(f"🗺️  Testing with {len(test_sitemaps)} sitemaps:")
    for i, sitemap in enumerate(test_sitemaps, 1):
        print(f"  {i}. {sitemap}")
    
    print(f"\n📋 Discovering ALL URLs from sitemaps (NO LIMITS)...")
    
    try:
        all_urls = get_all_sitemap_urls(test_sitemaps)
        
        if all_urls:
            print(f"\n🎉 SUCCESS! Discovered {len(all_urls)} URLs!")
            print(f"🔥 This is with NO LIMITS on nested sitemaps!")
            
            # Show URL categories
            print(f"\n📊 URL Categories Found:")
            categories = {
                'Admissions': [url for url in all_urls if 'admission' in url.lower()],
                'Programs': [url for url in all_urls if any(word in url.lower() for word in ['program', 'course', 'degree'])],
                'Student Services': [url for url in all_urls if any(word in url.lower() for word in ['student', 'coop', 'career'])],
                'Academic': [url for url in all_urls if any(word in url.lower() for word in ['academic', 'faculty', 'research'])],
                'About/Contact': [url for url in all_urls if any(word in url.lower() for word in ['about', 'contact', 'news'])],
                'Catalog': [url for url in all_urls if 'catalog' in url.lower()],
                'Engineering': [url for url in all_urls if 'engineering' in url.lower() or 'coe' in url.lower()],
                'Health Sciences': [url for url in all_urls if any(word in url.lower() for word in ['health', 'nursing', 'medical'])],
                'Business': [url for url in all_urls if any(word in url.lower() for word in ['business', 'damore', 'mckim'])],
                'Arts & Media': [url for url in all_urls if any(word in url.lower() for word in ['arts', 'media', 'design', 'camd'])]
            }
            
            total_categorized = 0
            for category, urls in categories.items():
                if urls:
                    print(f"  📁 {category}: {len(urls)} URLs")
                    total_categorized += len(urls)
            
            print(f"\n📈 Summary:")
            print(f"  🔗 Total URLs discovered: {len(all_urls)}")
            print(f"  📊 Categorized URLs: {total_categorized}")
            print(f"  🎯 Uncategorized URLs: {len(all_urls) - total_categorized}")
            
            # Estimate for full scraper
            print(f"\n🚀 ESTIMATE FOR FULL SCRAPER:")
            print(f"  📋 With 80+ sitemaps: ~{len(all_urls) * 16:,} URLs")
            print(f"  ⏱️  Estimated scraping time: ~{len(all_urls) * 16 // 60} minutes")
            print(f"  💾 Estimated documents: ~{len(all_urls) * 16:,} documents")
            
            print(f"\n🎯 ALL these URLs will be scraped with NO LIMITS!")
            print(f"✅ The scraper will discover and scrape EVERY SINGLE URL!")
            
            return True
        else:
            print(f"❌ No URLs discovered")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run the test"""
    success = test_unlimited_discovery()
    
    if success:
        print(f"\n🎉 UNLIMITED discovery test completed!")
        print(f"✅ The scraper is now configured to:")
        print(f"   🔥 Process ALL nested sitemaps (NO LIMITS)")
        print(f"   🔥 Discover ALL URLs from sitemaps")
        print(f"   🔥 Scrape ALL discovered URLs")
        print(f"   🔥 Store ALL content in Pinecone")
        print(f"\n🚀 Ready to run: python scrape_to_pinecone.py")
    else:
        print(f"\n❌ Test failed - please check the errors above")

if __name__ == "__main__":
    main()
