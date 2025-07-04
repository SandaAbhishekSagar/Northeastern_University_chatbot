import scrapy
from scrapy_playwright.page import PageMethod
from items import UniversityPageItem
from datetime import datetime
import urllib.parse

class UniversitySpider(scrapy.Spider):
    name = 'university'
    
    def __init__(self, university_urls=None, *args, **kwargs):
        super(UniversitySpider, self).__init__(*args, **kwargs)
        if university_urls:
            self.start_urls = university_urls.split(',')
        else:
            self.start_urls = [
                'https://www.northeastern.edu',
                'https://catalog.northeastern.edu'
            ]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("wait_for_timeout", 2000),  # Wait 2 seconds
                    ],
                }
            )
    
    def parse(self, response):
        # Extract main content
        item = UniversityPageItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').get() or "No Title"
        item['content'] = response.text
        item['scraped_at'] = datetime.now().isoformat()
        item['university_name'] = self.extract_university_name(response.url)
        item['metadata'] = {
            'status_code': response.status,
            'content_length': len(response.text),
            'page_type': self.classify_page_type(response.url, item['title'])
        }
        
        yield item
        
        # Follow links to other pages on the same domain (limit to 5 for testing)
        links = response.css('a::attr(href)').getall()[:5]  # Limit links for testing
        for link in links:
            if self.should_follow_link(link, response.url):
                absolute_url = urllib.parse.urljoin(response.url, link)
                yield scrapy.Request(
                    url=absolute_url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "networkidle"),
                        ],
                    }
                )
    
    def extract_university_name(self, url: str) -> str:
        """Extract university name from URL"""
        domain = urllib.parse.urlparse(url).netloc.lower()
        
        # University name mapping
        university_mapping = {
            'northeastern': 'Northeastern University',
            'harvard': 'Harvard University',
            'mit': 'MIT',
            'stanford': 'Stanford University',
            'berkeley': 'University of California, Berkeley',
            'ucla': 'University of California, Los Angeles',
            'usc': 'University of Southern California',
            'nyu': 'New York University',
            'columbia': 'Columbia University',
            'princeton': 'Princeton University',
            'yale': 'Yale University',
            'cornell': 'Cornell University',
            'upenn': 'University of Pennsylvania',
            'brown': 'Brown University',
            'dartmouth': 'Dartmouth College',
            'duke': 'Duke University',
            'northwestern': 'Northwestern University',
            'uchicago': 'University of Chicago',
            'caltech': 'California Institute of Technology',
            'cmu': 'Carnegie Mellon University'
        }
        
        # Check for exact matches
        for key, name in university_mapping.items():
            if key in domain:
                return name
        
        # Fallback: format domain name
        return domain.replace('www.', '').replace('.edu', '').title()
    
    def classify_page_type(self, url: str, title: str) -> str:
        """Classify the type of page"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if any(word in url_lower for word in ['course', 'catalog', 'curriculum']):
            return 'academic'
        elif any(word in url_lower for word in ['admission', 'apply', 'application']):
            return 'admissions'
        elif any(word in url_lower for word in ['faculty', 'staff', 'people']):
            return 'people'
        elif any(word in url_lower for word in ['news', 'event', 'announcement']):
            return 'news'
        else:
            return 'general'
    
    def should_follow_link(self, link: str, current_url: str) -> bool:
        """Determine if we should follow a link"""
        if not link:
            return False
        
        # Skip non-HTTP links
        if link.startswith(('mailto:', 'tel:', '#', 'javascript:')):
            return False
        
        # Get absolute URL
        absolute_url = urllib.parse.urljoin(current_url, link)
        parsed_url = urllib.parse.urlparse(absolute_url)
        current_domain = urllib.parse.urlparse(current_url).netloc
        
        # Only follow links on the same domain
        if parsed_url.netloc != current_domain:
            return False
        
        # Skip certain file types
        skip_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.zip', '.jpg', '.png', '.gif']
        if any(absolute_url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        return True