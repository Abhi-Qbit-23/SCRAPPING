# scraper_registry.py

from scrapers.moneycontrol_scraper import scrape_moneycontrol_news
from scrapers.yahoo_scraper import scrape_yahoo_news

SCRAPERS = [
    {"name": "Moneycontrol", "function": scrape_moneycontrol_news},
    {"name": "Yahoo", "function": scrape_yahoo_news},
    # Add more scrapers here
]
