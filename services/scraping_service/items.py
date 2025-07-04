import scrapy

class UniversityPageItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    content_hash = scrapy.Field()
    metadata = scrapy.Field()
    scraped_at = scrapy.Field()
    university_name = scrapy.Field()