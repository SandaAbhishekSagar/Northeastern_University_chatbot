BOT_NAME = 'university_scraper'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Ethical scraping settings
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# User agent
USER_AGENT = 'UniversityResearchBot/1.0 (+http://research.university.edu/contact)'

# Enable pipelines
ITEM_PIPELINES = {
    'pipelines.ChangeDetectionPipeline': 300,
    'pipelines.ChromaDBPipeline': 400,
}

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
DOWNLOAD_TIMEOUT = 300
