import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from transformers import pipeline

# Load summarizer model
print("[INFO] Loading summarizer model...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

RSS_URL = "https://finance.yahoo.com/news/rssindex"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.15; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def to_gen_z_style(text):
    starters = [
        "Big moves alert 🚨", "No cap, this just happened 👀", "Here’s the tea ☕",
        "Hot take 🔥", "Sheeesh 😤", "TL;DR 👇", "Stock bros, listen up 📢"
    ]
    emojis = ["💼", "📈", "📉", "🚀", "🧠", "🤑", "🔥", "💣", "📊"]
    return f"{random.choice(starters)} {text.strip()} {random.choice(emojis)}"

def summarize_if_needed(text, word_threshold=60):
    word_count = len(text.split())
    if word_count <= word_threshold:
        print(f"[INFO] Skipping summarization ({word_count} words only).")
        return text.strip()
    try:
        print(f"[INFO] Summarizing article ({word_count} words)...")
        result = summarizer(text, max_length=80, min_length=40, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        print(f"[WARN] Summarization failed: {e}")
        return text.strip()

def fetch_full_article(link):
    try:
        print(f"[INFO] Fetching article: {link}")
        res = requests.get(link, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        # Try different ways to get article text
        article_body = soup.find("div", {"class": "caas-body"})
        if not article_body:
            article_tag = soup.find("article")
            if article_tag:
                paragraphs = article_tag.find_all("p")
            else:
                paragraphs = soup.find_all("p")
        else:
            paragraphs = article_body.find_all("p")

        article_text = " ".join(p.get_text() for p in paragraphs).strip()

        # Minimum content length check
        if len(article_text.split()) < 30:
            return None, None

        # Try getting image
        img_tag = soup.find("img", {"class": "caas-img"})
        image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

        return article_text, image_url

    except Exception as e:
        print(f"[WARN] Error fetching article content: {e}")
        return None, None

def scrape_yahoo_news():
    print("[INFO] Fetching RSS feed...")
    res = requests.get(RSS_URL, headers=HEADERS)
    soup = BeautifulSoup(res.content, features="xml")
    items = soup.find_all("item")

    print(f"[INFO] Found {len(items)} articles in RSS feed.")
    articles = []

    for item in items:
        title = item.title.text.strip()
        link = item.link.text.strip()

        if not link.startswith("https://finance.yahoo.com"):
            continue

        print(f"\n[INFO] Processing: {title}")
        article_text, image_url = fetch_full_article(link)

        if not article_text:
            print("[WARN] Skipped - no content.")
            continue

        final_text = summarize_if_needed(article_text)
        summary = to_gen_z_style(final_text)

        articles.append({
            "headline": title,
            "url": link,
            "summary": summary,
            "image_url": image_url,
            "scraped_at": datetime.now().isoformat(),
            "source": "Yahoo Finance"
        })

        if len(articles) >= 5:
            break

    return articles

if __name__ == "__main__":
    results = scrape_yahoo_news()

    if not results:
        print("[❌] No valid Yahoo Finance articles found.")
    else:
        for article in results:
            print(f"\n📰 {article['headline']}")
            print(f"🔗 {article['url']}")
            print(f"🖼️ {article['image_url']}")
            print(f"📝 {article['summary']}")
