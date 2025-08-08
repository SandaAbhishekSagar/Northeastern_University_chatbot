import scrapy
from items import UniversityPageItem
from datetime import datetime

class NewtonCoursesSpider(scrapy.Spider):
    name = 'newton_courses'
    
    def __init__(self, urls=None, *args, **kwargs):
        super(NewtonCoursesSpider, self).__init__(*args, **kwargs)
        
        # Default Newton course URLs
        default_urls = [
            'http://newton.neu.edu/fall2022/',
            'http://newton.neu.edu/fall2023/',
            'http://newton.neu.edu/fall2024/',
            'http://newton.neu.edu/fall2025/',
            'http://newton.neu.edu/summer2022/',
            'http://newton.neu.edu/summer2023/',
            'http://newton.neu.edu/summer2024/',
            'http://newton.neu.edu/summer2025/',
            'http://newton.neu.edu/spring2022/',
            'http://newton.neu.edu/spring2023/',
            'http://newton.neu.edu/spring2024/',
            'http://newton.neu.edu/spring2025/'
        ]
        
        if urls:
            # If URLs provided as comma-separated string, split them
            if isinstance(urls, str):
                self.start_urls = [url.strip() for url in urls.split(',')]
            else:
                self.start_urls = urls
        else:
            self.start_urls = default_urls

    def parse(self, response):
        item = UniversityPageItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').get() or "No Title"
        item['content'] = response.text
        item['scraped_at'] = datetime.now().isoformat()
        item['university_name'] = 'Northeastern University'
        item['metadata'] = {
            'status_code': response.status,
            'content_length': len(response.text),
            'page_type': 'newton_course',
            'semester': self.extract_semester(response.url),
            'year': self.extract_year(response.url)
        }
        yield item
    
    def extract_semester(self, url):
        """Extract semester from URL"""
        if 'fall' in url.lower():
            return 'Fall'
        elif 'spring' in url.lower():
            return 'Spring'
        elif 'summer' in url.lower():
            return 'Summer'
        return 'Unknown'
    
    def extract_year(self, url):
        """Extract year from URL"""
        import re
        year_match = re.search(r'(\d{4})', url)
        if year_match:
            return year_match.group(1)
        return 'Unknown' 