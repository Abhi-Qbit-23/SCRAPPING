# main.py

from database import init_db, save_to_db
from scraper_runner import run_all_scrapers

def main():
    init_db()
    news = run_all_scrapers()
    if news:
        save_to_db(news)
        print(f"✅ Saved {len(news)} news items to database.")
        for n in news[:10]:
            print(f"\n🔹 {n['headline']}\n{n['url']}\n📝 {n['summary']}")
    else:
        print("⚠️ No news items found.")

if __name__ == "__main__":
    main()
