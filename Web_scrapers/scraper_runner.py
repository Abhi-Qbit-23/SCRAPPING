# scraper_runner.py

from scraper_registry import SCRAPERS

def run_all_scrapers():
    all_news = []

    for scraper in SCRAPERS:
        name = scraper["name"]
        func = scraper["function"]

        try:
            print(f"▶️ Running scraper: {name}")
            news_items = func()
            if news_items:
                all_news.extend(news_items)
                print(f"✅ {len(news_items)} items scraped from {name}")
            else:
                print(f"⚠️ No news found by {name}")
        except Exception as e:
            print(f"❌ Error scraping {name}: {e}")

    return all_news
