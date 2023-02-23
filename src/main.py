from LinkedInScraper import LinkedInScraper

scraper = LinkedInScraper('', '', 'https://www.linkedin.com/in/jiajun-fang-878b9b232/')
print(scraper.get_intro('https://www.linkedin.com/in/jiajun-fang-878b9b232/'))