# -*- coding: utf-8 -*-

import cloudscraper2

def make_request(url):
    try:
        scraper = cloudscraper2.create_scraper()
        return scraper.get(url).text
    except:
        return False
    
def post_request(id):
    try:
        scraper = cloudscraper2.create_scraper()
        return scraper.post('https://coverapi.store/engine/ajax/controller.php', data={'mod': 'players', 'news_id': str(id)}).text
    except:
        return False