from LinkedInScraper import LinkedInScraper

scraper = LinkedInScraper('',
                          '',
                          'site',
                          "headers")

print(scraper.get_experiences("site"))