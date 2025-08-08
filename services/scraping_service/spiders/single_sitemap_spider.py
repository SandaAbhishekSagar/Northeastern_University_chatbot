import scrapy
from scrapy.spiders import SitemapSpider
from items import UniversityPageItem
from datetime import datetime

class SingleSitemapSpider(SitemapSpider):
    name = 'single_sitemap'
    
    def __init__(self, sitemap_url=None, *args, **kwargs):
        super(SingleSitemapSpider, self).__init__(*args, **kwargs)
        if sitemap_url:
            self.sitemap_urls = [sitemap_url]
        else:
            # Default to catalog sitemap if no URL provided
            self.sitemap_urls = ['https://catalog.northeastern.edu/sitemap.xml']

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
            'page_type': 'general'
        }
        yield item 