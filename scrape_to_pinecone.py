#!/usr/bin/env python3
"""
Scrape Northeastern University websites via sitemaps and store directly in Pinecone
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from typing import List, Set

# Add current directory to path
sys.path.append('.')

def setup_pinecone():
    """Set up Pinecone connection"""
    print("🌲 Setting up Pinecone...")
    
    try:
        from pinecone import Pinecone
        
        # Get API key from environment or prompt user
        api_key = os.environ.get('PINECONE_API_KEY')
        if not api_key:
            print("⚠️  PINECONE_API_KEY not found in environment variables")
            api_key = input("Please enter your Pinecone API key: ").strip()
            if not api_key:
                print("❌ No API key provided")
                return None
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        # Create or get index
        index_name = "northeastern-university"
        if index_name not in pc.list_indexes().names():
            print(f"📊 Creating Pinecone index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=384,  # For all-MiniLM-L6-v2 embeddings
                metric="cosine"
            )
            print("✅ Pinecone index created")
        else:
            print(f"✅ Using existing Pinecone index: {index_name}")
        
        return pc.Index(index_name)
        
    except Exception as e:
        print(f"❌ Failed to setup Pinecone: {e}")
        return None

def get_embedding(text):
    """Get embedding for text"""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load model (cache it globally to avoid reloading)
        if not hasattr(get_embedding, 'model'):
            get_embedding.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embedding
        embedding = get_embedding.model.encode([text])[0].tolist()
        return embedding
        
    except Exception as e:
        print(f"❌ Failed to generate embedding: {e}")
        return None

def parse_sitemap(sitemap_url: str) -> List[str]:
    """Parse a sitemap XML and extract URLs"""
    print(f"🗺️  Parsing sitemap: {sitemap_url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache'
        }
        
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        
        # Handle different HTTP status codes
        if response.status_code == 403:
            print(f"⚠️  Sitemap forbidden (403): {sitemap_url}")
            return []
        elif response.status_code == 404:
            print(f"⚠️  Sitemap not found (404): {sitemap_url}")
            return []
        elif response.status_code != 200:
            print(f"⚠️  Sitemap returned status {response.status_code}: {sitemap_url}")
            return []
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        urls = []
        
        # Handle different sitemap formats
        # Standard sitemap format
        for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc_elem is not None and loc_elem.text:
                urls.append(loc_elem.text.strip())
        
        # Sitemap index format (contains other sitemaps) - NO LIMITS
        for sitemap_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
            loc_elem = sitemap_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc_elem is not None and loc_elem.text:
                # Recursively parse ALL nested sitemaps
                print(f"🔄 Processing nested sitemap: {loc_elem.text.strip()}")
                nested_urls = parse_sitemap(loc_elem.text.strip())
                urls.extend(nested_urls)
        
        # If no standard format found, try without namespace
        if not urls:
            for url_elem in root.findall('.//url'):
                loc_elem = url_elem.find('loc')
                if loc_elem is not None and loc_elem.text:
                    urls.append(loc_elem.text.strip())
        
        # Filter for Northeastern University URLs only
        northeastern_urls = []
        for url in urls:
            if 'northeastern.edu' in url.lower():
                northeastern_urls.append(url)
        
        print(f"✅ Found {len(northeastern_urls)} Northeastern URLs in sitemap")
        return northeastern_urls
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error for {sitemap_url}: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {sitemap_url}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error parsing sitemap {sitemap_url}: {e}")
        return []

def get_all_sitemap_urls(sitemap_urls: List[str]) -> Set[str]:
    """Get all URLs from multiple sitemaps"""
    print(f"🗺️  Processing {len(sitemap_urls)} sitemaps...")
    
    all_urls = set()
    successful_sitemaps = 0
    failed_sitemaps = 0
    
    # Remove duplicates from sitemap URLs
    unique_sitemap_urls = list(set(sitemap_urls))
    print(f"📋 Processing {len(unique_sitemap_urls)} unique sitemaps...")
    
    for i, sitemap_url in enumerate(unique_sitemap_urls, 1):
        print(f"\n📋 Processing sitemap {i}/{len(unique_sitemap_urls)}: {sitemap_url}")
        
        try:
            urls = parse_sitemap(sitemap_url)
            if urls:
                all_urls.update(urls)
                successful_sitemaps += 1
            else:
                failed_sitemaps += 1
        except Exception as e:
            print(f"❌ Error processing sitemap: {e}")
            failed_sitemaps += 1
        
        # Minimal delay between sitemap requests for faster processing
        if i < len(unique_sitemap_urls):
            time.sleep(0.5)  # Very short delay to be respectful but fast
    
    print(f"\n📊 Sitemap Processing Summary:")
    print(f"✅ Successful sitemaps: {successful_sitemaps}")
    print(f"❌ Failed sitemaps: {failed_sitemaps}")
    print(f"🔗 Total unique URLs found: {len(all_urls)}")
    
    return all_urls

def scrape_url(url, max_depth=2, visited=None):
    """Scrape a URL and extract content"""
    if visited is None:
        visited = set()
    
    if url in visited or len(visited) > 30:  # Limit to 30 pages
        return []
    
    visited.add(url)
    print(f"🔍 Scraping: {url}")
    
    try:
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract content
        content = extract_content(soup)
        if not content:
            print(f"⚠️  No content extracted from {url}")
            return []
        
        # Create document
        doc = {
            'id': f"doc_{len(visited)}_{hash(url) % 10000}",
            'content': content,
            'metadata': {
                'url': url,
                'title': soup.title.string.strip() if soup.title and soup.title.string else 'Northeastern University',
                'scraped_at': time.time()
            }
        }
        
        print(f"✅ Extracted {len(content)} characters from {url}")
        return [doc]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {url}: {e}")
        return []
    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return []

def scrape_urls(urls, max_depth=2, visited=None):
    """Scrape multiple URLs"""
    if visited is None:
        visited = set()
    
    all_docs = []
    for url in urls:
        if max_depth > 0:
            docs = scrape_url(url, max_depth, visited)
            all_docs.extend(docs)
            time.sleep(1)  # Be respectful
    
    return all_docs

def extract_content(soup):
    """Extract meaningful content from HTML"""
    # Remove unwanted elements
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        element.decompose()
    
    # Try to find main content areas first
    main_content = None
    for selector in ['main', 'article', '.content', '#content', '.main-content', '.page-content']:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # If no main content found, use the whole body
    if not main_content:
        main_content = soup.find('body') or soup
    
    # Get text content
    text = main_content.get_text()
    
    # Clean up text
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    # Remove common navigation and footer text
    unwanted_phrases = [
        'skip to main content', 'menu', 'search', 'login', 'sign in',
        'cookie policy', 'privacy policy', 'terms of service',
        'copyright', 'all rights reserved', 'follow us', 'social media'
    ]
    
    for phrase in unwanted_phrases:
        text = text.replace(phrase, '')
    
    # Filter out very short content
    if len(text) < 200:
        return None
    
    # Limit content length but keep it substantial
    if len(text) > 5000:
        text = text[:5000] + "..."
    
    return text

def store_in_pinecone(docs, index, batch_size=100):
    """Store documents in Pinecone in batches"""
    print(f"📤 Storing {len(docs)} documents in Pinecone (batch size: {batch_size})...")
    
    try:
        total_stored = 0
        total_batches = (len(docs) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(docs))
            batch_docs = docs[start_idx:end_idx]
            
            print(f"📦 Processing batch {batch_num + 1}/{total_batches} ({len(batch_docs)} documents)...")
            
            # Prepare vectors for this batch
            vectors = []
            
            for doc in batch_docs:
                # Generate embedding
                embedding = get_embedding(doc['content'])
                if not embedding:
                    continue
                
                # Create vector
                vector = {
                    'id': doc['id'],
                    'values': embedding,
                    'metadata': doc['metadata']
                }
                vectors.append(vector)
            
            # Upsert this batch to Pinecone
            if vectors:
                index.upsert(vectors=vectors)
                total_stored += len(vectors)
                print(f"✅ Stored batch {batch_num + 1}/{total_batches} ({len(vectors)} documents)")
            else:
                print(f"⚠️  No valid embeddings in batch {batch_num + 1}")
        
        print(f"🎉 Successfully stored {total_stored} documents in Pinecone")
        return True
            
    except Exception as e:
        print(f"❌ Failed to store in Pinecone: {e}")
        return False

def main():
    """Main scraping function"""
    print("=" * 60)
    print("🚀 Northeastern University Sitemap Scraper")
    print("=" * 60)
    
    # Setup Pinecone
    index = setup_pinecone()
    if not index:
        print("❌ Failed to setup Pinecone")
        return
    
    # Northeastern University sitemap URLs (prioritized by importance and accessibility)
    sitemap_urls = [
        'https://www.northeastern.edu/sitemap.xml'
,'https://me.northeastern.edu/sitemap.xml'
,'https://about.me.northeastern.edu/sitemap.xml'
,'https://catalog.northeastern.edu/sitemap.xml'
,'https://registrar.northeastern.edu/sitemap.xml'
,'https://library.northeastern.edu/sitemap.xml'
,'https://studentlife.northeastern.edu/sitemap.xml'
,'https://admissions.northeastern.edu/sitemap.xml'
,'https://graduate.northeastern.edu/sitemap.xml'
,'https://registrar.northeastern.edu/sitemap.xml'
,'https://catalog.northeastern.edu/sitemap.xml'
,'https://housing.northeastern.edu/sitemap.xml'
,'https://aptsearch.northeastern.edu/sitemap.xml'
,'https://studentfinance.northeastern.edu/sitemap.xml'
,'https://huskycard.northeastern.edu/sitemap.xml'
,'https://uhcs.northeastern.edu/sitemap.xml'
,'https://its.northeastern.edu/sitemap.xml'
,'https://connect-to-tech.northeastern.edu/sitemap.xml'
,'https://library.northeastern.edu/sitemap.xml'
,'https://northeastern.libanswers.com/sitemap.xml'
,'https://careers.northeastern.edu/sitemap.xml'
,'https://cos.northeastern.edu/sitemap.xml'
,'https://cssh.northeastern.edu/sitemap.xml'
,'https://coe.northeastern.edu/sitemap.xml'
,'https://neu.campuslabs.com/sitemap.xml'
,'https://damore-mckim.northeastern.edu/sitemap.xml'
,'https://bouve.northeastern.edu/sitemap.xml'
,'https://undergraduate.northeastern.edu/sitemap.xml'
,'https://cps.northeastern.edu/sitemap.xml'
,'https://international.northeastern.edu/sitemap.xml'
,'https://alumni.northeastern.edu/sitemap.xml'
,'https://recreation.northeastern.edu/sitemap.xml'
,'https://cultural-life.northeastern.edu/sitemap.xml'
,'https://diversity.northeastern.edu/sitemap.xml'
,'https://jdoaai.sites.northeastern.edu/sitemap.xml'
,'https://nuplace.northeastern.edu/sitemap.xml'
,'https://nupd.northeastern.edu/sitemap.xml'
,'https://facilities.northeastern.edu/sitemap.xml'
,'https://pref.northeastern.edu/sitemap.xml'
,'https://calendar.northeastern.edu/sitemap.xml'
,'https://camd.northeastern.edu/sitemap.xml'
,'https://nuin.northeastern.edu/sitemap.xml'
,'https://phd.northeastern.edu/sitemap.xml'
,'https://online.northeastern.edu/sitemap.xml'
,'https://sites.northeastern.edu/sitemap.xml'
,'https://accomplishments.northeastern.edu/sitemap.xml'
,'https://give.northeastern.edu/sitemap.xml'
,'https://experiencepoweredby.northeastern.edu/sitemap.xml'
,'https://sustainability.northeastern.edu/sitemap.xml'
,'https://experience.arcgis.com/experience/b24181de18b74d20a369865de2a44ef3/sitemap.xml'
,'https://campusmap.northeastern.edu/sitemap.xml'
,'https://publicart.northeastern.edu/sitemap.xml'
,'https://hr.northeastern.edu/sitemap.xml'
,'https://belonging.northeastern.edu/sitemap.xml'
,'https://provost.northeastern.edu/sitemap.xml'
,'https://registrar.northeastern.edu/sitemap.xml'
,'https://law.northeastern.edu/sitemap.xml'
,'https://research.northeastern.edu/sitemap.xml'
,'https://geo.northeastern.edu/sitemap.xml'
,'https://globalsafety.northeastern.edu/sitemap.xml'
,'https://experiential-learning.northeastern.edu/sitemap.xml'
,'https://arlington.northeastern.edu/sitemap.xml'
,'https://www.burlington.northeastern.edu/sitemap.xml'
,'https://charlotte.northeastern.edu/sitemap.xml'
,'https://www.nulondon.ac.uk/sitemap.xml'
,'https://miami.northeastern.edu/sitemap.xml'
,'https://csi.northeastern.edu/sitemap.xml'
,'https://oakland.northeastern.edu/sitemap.xml'
,'https://roux.northeastern.edu/sitemap.xml'
,'https://seattle.northeastern.edu/sitemap.xml'
,'https://siliconvalley.northeastern.edu/sitemap.xml'
,'https://toronto.northeastern.edu/sitemap.xml'
,'https://vancouver.northeastern.edu/sitemap.xml'
,'https://bachelors-completion.northeastern.edu/sitemap.xml'
,'https://nuhuskies.com/sitemap.xml'
,'https://academicplan.northeastern.edu/sitemap.xml'
,'https://president.northeastern.edu/sitemap.xml'
,'https://facts.northeastern.edu/sitemap.xml'
,'https://giving.northeastern.edu/sitemap.xml'
,'https://catalog.northeastern.edu/sitemap.xml'
,'https://service.northeastern.edu/sitemap.xml'
,'https://nupdboard.northeastern.edu/sitemap.xml'
,'https://offcampus.housing.northeastern.edu/sitemap.xml'
,'https://digital-accessibility.northeastern.edu/sitemap.xml'
,'https://nu.outsystemsenterprise.com/FSD/sitemap.xml'
    ]
    
    print(f"🗺️  Processing {len(sitemap_urls)} sitemaps to discover URLs...")
    
    # Step 1: Get all URLs from sitemaps
    all_urls = get_all_sitemap_urls(sitemap_urls)
    
    if not all_urls:
        print("❌ No URLs found in sitemaps")
        return
    
    # Step 2: Filter and limit URLs for scraping
    print(f"🔍 Filtering {len(all_urls)} discovered URLs...")
    
    filtered_urls = []
    unwanted_patterns = [
        '/wp-content/', '/wp-admin/', '/wp-includes/',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
        '.css', '.js', '.xml', '.txt', '.zip', '.rar',
        '/feed/', '/rss/', '/atom/', '/sitemap',
        '?', '#', 'mailto:', 'tel:', 'javascript:',
        '/search', '/login', '/logout', '/register',
        '/wp-json/', '/api/', '/ajax/', '/admin/',
        'print=', 'format=', 'view=', 'download='
    ]
    
    # Priority keywords for important content
    priority_keywords = [
        'admission', 'admissions', 'academic', 'academics', 'program', 'programs',
        'course', 'courses', 'degree', 'degrees', 'major', 'majors',
        'coop', 'co-op', 'cooperative', 'student', 'students', 'faculty',
        'research', 'about', 'contact', 'news', 'event', 'events',
        'calendar', 'tuition', 'financial', 'aid', 'scholarship',
        'campus', 'housing', 'dining', 'library', 'career', 'careers',
        'international', 'study', 'abroad', 'alumni', 'giving'
    ]
    
    # Secondary keywords for additional content
    secondary_keywords = [
        'department', 'school', 'college', 'institute', 'center',
        'service', 'services', 'resource', 'resources', 'support',
        'policy', 'policies', 'procedure', 'procedures', 'guideline',
        'requirement', 'requirements', 'prerequisite', 'prerequisites'
    ]
    
    for url in all_urls:
        url_lower = url.lower()
        
        # Skip if URL contains unwanted patterns
        if any(pattern in url_lower for pattern in unwanted_patterns):
            continue
        
        # Check for priority keywords first
        if any(keyword in url_lower for keyword in priority_keywords):
            filtered_urls.append(url)
        # Then check for secondary keywords
        elif any(keyword in url_lower for keyword in secondary_keywords):
            filtered_urls.append(url)
        # Include main pages (homepage, about, etc.)
        elif any(main_page in url_lower for main_page in ['/', '/about', '/contact', '/home']):
            filtered_urls.append(url)
    
    # Remove duplicates and sort by priority
    filtered_urls = list(set(filtered_urls))
    
    # Sort URLs by importance (shorter URLs first, then by keyword priority)
    def url_priority(url):
        priority_score = 0
        url_lower = url.lower()
        
        # Higher priority for main pages
        if url_lower.endswith('/') or '/about' in url_lower or '/contact' in url_lower:
            priority_score += 100
        
        # Higher priority for admission-related content
        if any(word in url_lower for word in ['admission', 'admissions', 'apply', 'application']):
            priority_score += 50
        
        # Higher priority for academic content
        if any(word in url_lower for word in ['program', 'course', 'degree', 'major']):
            priority_score += 30
        
        # Higher priority for student services
        if any(word in url_lower for word in ['student', 'coop', 'co-op', 'career']):
            priority_score += 20
        
        # Shorter URLs get higher priority
        priority_score += max(0, 100 - len(url))
        
        return priority_score
    
    filtered_urls.sort(key=url_priority, reverse=True)
    
    # NO LIMITS - scrape ALL discovered URLs
    print(f"✅ Ready to scrape ALL {len(filtered_urls)} discovered URLs")
    print(f"🚀 This will be a comprehensive scrape of Northeastern University!")
    
    print(f"📋 Scraping {len(filtered_urls)} Northeastern University URLs...")
    
    # Step 3: Scrape the discovered URLs
    all_docs = []
    successful_urls = 0
    failed_urls = 0
    
    for i, url in enumerate(filtered_urls, 1):
        print(f"\n📋 Progress: {i}/{len(filtered_urls)} - {url}")
        try:
            docs = scrape_url(url, max_depth=0)
            if docs:
                all_docs.extend(docs)
                successful_urls += 1
                print(f"✅ Successfully scraped {len(docs)} document(s)")
            else:
                failed_urls += 1
                print(f"⚠️  No content extracted")
        except Exception as e:
            failed_urls += 1
            print(f"❌ Failed to scrape: {e}")
        
        # Be respectful - wait between requests
        if i < len(filtered_urls):
            time.sleep(1)  # Reduced delay for faster scraping
    
    print(f"\n📊 Final Scraping Summary:")
    print(f"🗺️  Sitemaps processed: {len(sitemap_urls)}")
    print(f"🔗 URLs discovered: {len(all_urls)}")
    print(f"📄 URLs scraped: {len(filtered_urls)}")
    print(f"✅ Successful: {successful_urls} URLs")
    print(f"❌ Failed: {failed_urls} URLs")
    print(f"📚 Total documents: {len(all_docs)}")
    
    # Step 4: Store in Pinecone
    if all_docs:
        success = store_in_pinecone(all_docs, index)
        if success:
            print("🎉 Sitemap scraping and storage completed successfully!")
            print(f"🚀 Your chatbot now has access to {len(all_docs)} documents from Northeastern University!")
        else:
            print("❌ Storage failed")
    else:
        print("❌ No documents scraped")

if __name__ == "__main__":
    main()
