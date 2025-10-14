#!/usr/bin/env python3
"""
Test the fixed sitemap scraper with a small subset
"""

import sys
sys.path.append('.')

from scrape_to_pinecone import parse_sitemap, get_all_sitemap_urls

def test_fixed_scraper():
    """Test the fixed scraper with a few sitemaps"""
    print("🧪 Testing Fixed Sitemap Scraper")
    print("=" * 50)
    
    # Test with just a few sitemaps to verify fixes
    test_sitemaps = [
        "https://www.northeastern.edu/sitemap.xml",
        "https://admissions.northeastern.edu/sitemap.xml",
        "https://catalog.northeastern.edu/sitemap.xml"
    ]
    
    try:
        print("🗺️  Testing sitemap parsing...")
        all_urls = get_all_sitemap_urls(test_sitemaps)
        
        if all_urls:
            print(f"✅ Successfully discovered {len(all_urls)} URLs")
            print(f"🔗 Sample URLs:")
            for i, url in enumerate(list(all_urls)[:10], 1):
                print(f"  {i}. {url}")
            
            # Test URL filtering
            print(f"\n🔍 Testing URL filtering...")
            
            # Simulate the filtering logic
            filtered_urls = []
            unwanted_patterns = [
                '/wp-content/', '/wp-admin/', '/wp-includes/',
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
                '.css', '.js', '.xml', '.txt', '.zip', '.rar',
                '/feed/', '/rss/', '/atom/', '/sitemap',
                '?', '#', 'mailto:', 'tel:', 'javascript:',
                '/search', '/login', '/logout', '/register'
            ]
            
            priority_keywords = [
                'admission', 'admissions', 'academic', 'academics', 'program', 'programs',
                'course', 'courses', 'degree', 'degrees', 'major', 'majors',
                'coop', 'co-op', 'cooperative', 'student', 'students', 'faculty',
                'research', 'about', 'contact', 'news', 'event', 'events'
            ]
            
            for url in all_urls:
                url_lower = url.lower()
                
                # Skip if URL contains unwanted patterns
                if any(pattern in url_lower for pattern in unwanted_patterns):
                    continue
                
                # Check for priority keywords
                if any(keyword in url_lower for keyword in priority_keywords):
                    filtered_urls.append(url)
            
            print(f"✅ Filtered to {len(filtered_urls)} high-priority URLs")
            print(f"🔗 Sample filtered URLs:")
            for i, url in enumerate(filtered_urls[:5], 1):
                print(f"  {i}. {url}")
            
            return True
        else:
            print(f"❌ No URLs discovered")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run the test"""
    success = test_fixed_scraper()
    
    if success:
        print(f"\n🎉 Fixed scraper test passed!")
        print(f"✅ The scraper should now work much better")
        print(f"🚀 You can run: python scrape_to_pinecone.py")
    else:
        print(f"\n❌ Test failed - please check the errors above")

if __name__ == "__main__":
    main()
