import scrapy
from scrapy.spiders import SitemapSpider
from items import UniversityPageItem
from datetime import datetime

class NortheasternSitemapSpider(SitemapSpider):
    name = 'northeastern_sitemap'
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
            'page_type': 'general'  # You can add more logic if needed
        }
        yield item