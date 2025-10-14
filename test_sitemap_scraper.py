#!/usr/bin/env python3
"""
Test the sitemap scraper functionality
"""

import sys
sys.path.append('.')

from scrape_to_pinecone import parse_sitemap, get_all_sitemap_urls

def test_single_sitemap():
    """Test parsing a single sitemap"""
    print("🧪 Testing single sitemap parsing...")
    
    # Test with Northeastern's main sitemap
    test_sitemap = "https://www.northeastern.edu/sitemap.xml"
    
    try:
        urls = parse_sitemap(test_sitemap)
        
        if urls:
            print(f"✅ Successfully parsed sitemap!")
            print(f"📄 Found {len(urls)} URLs")
            print(f"🔗 Sample URLs:")
            for i, url in enumerate(urls[:5], 1):
                print(f"  {i}. {url}")
            if len(urls) > 5:
                print(f"  ... and {len(urls) - 5} more")
            return True
        else:
            print(f"❌ No URLs found in sitemap")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_multiple_sitemaps():
    """Test parsing multiple sitemaps"""
    print("\n🧪 Testing multiple sitemap parsing...")
    
    # Test with a few sitemaps
    test_sitemaps = [
        "https://www.northeastern.edu/sitemap.xml",
        "https://admissions.northeastern.edu/sitemap.xml",
        "https://graduate.northeastern.edu/sitemap.xml"
    ]
    
    try:
        all_urls = get_all_sitemap_urls(test_sitemaps)
        
        if all_urls:
            print(f"✅ Successfully parsed {len(test_sitemaps)} sitemaps!")
            print(f"📄 Found {len(all_urls)} unique URLs total")
            print(f"🔗 Sample URLs:")
            for i, url in enumerate(list(all_urls)[:5], 1):
                print(f"  {i}. {url}")
            if len(all_urls) > 5:
                print(f"  ... and {len(all_urls) - 5} more")
            return True
        else:
            print(f"❌ No URLs found in sitemaps")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_url_filtering():
    """Test URL filtering logic"""
    print("\n🧪 Testing URL filtering...")
    
    # Sample URLs that should be filtered
    test_urls = [
        "https://www.northeastern.edu/admissions/requirements/",
        "https://www.northeastern.edu/academics/programs/",
        "https://www.northeastern.edu/coop/",
        "https://www.northeastern.edu/wp-content/uploads/file.pdf",
        "https://www.northeastern.edu/images/logo.png",
        "https://www.northeastern.edu/search?q=test",
        "https://www.northeastern.edu/login",
        "https://www.northeastern.edu/about/contact/"
    ]
    
    unwanted_patterns = [
        '/wp-content/', '/wp-admin/', '/wp-includes/',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
        '.css', '.js', '.xml', '.txt', '.zip', '.rar',
        '/feed/', '/rss/', '/atom/', '/sitemap',
        '?', '#', 'mailto:', 'tel:', 'javascript:',
        '/search', '/login', '/logout', '/register'
    ]
    
    filtered_urls = []
    for url in test_urls:
        # Skip if URL contains unwanted patterns
        if any(pattern in url.lower() for pattern in unwanted_patterns):
            continue
        
        # Only include main content pages
        if any(keyword in url.lower() for keyword in [
            'admission', 'academic', 'program', 'course', 'degree',
            'coop', 'co-op', 'student', 'faculty', 'research',
            'about', 'contact', 'news', 'event', 'calendar'
        ]):
            filtered_urls.append(url)
    
    print(f"📄 Original URLs: {len(test_urls)}")
    print(f"✅ Filtered URLs: {len(filtered_urls)}")
    print(f"🔗 Filtered URLs:")
    for i, url in enumerate(filtered_urls, 1):
        print(f"  {i}. {url}")
    
    expected_filtered = 4  # admissions, academics, coop, about/contact
    if len(filtered_urls) == expected_filtered:
        print(f"✅ URL filtering working correctly!")
        return True
    else:
        print(f"❌ URL filtering not working as expected")
        return False

def main():
    """Run all tests"""
    print("🚀 Northeastern University Sitemap Scraper Test")
    print("=" * 60)
    
    # Test single sitemap parsing
    test1 = test_single_sitemap()
    
    # Test multiple sitemap parsing
    test2 = test_multiple_sitemaps()
    
    # Test URL filtering
    test3 = test_url_filtering()
    
    print(f"\n📊 Test Results:")
    print(f"Single Sitemap: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Multiple Sitemaps: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"URL Filtering: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if test1 and test2 and test3:
        print(f"\n🎉 All tests passed! The sitemap scraper is ready to use.")
        print(f"Run: python scrape_to_pinecone.py")
    else:
        print(f"\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
