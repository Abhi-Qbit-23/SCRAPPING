import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from nltk.tokenize import sent_tokenize
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

RSS_URL = "https://finance.yahoo.com/news/rssindex"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
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
        sentences = sent_tokenize(text)
        if len(sentences) <= 3:
            return text.strip()

        summary_sentences = sentences[:3]
        summary_text = " ".join(summary_sentences)
        return summary_text.strip()
    except Exception as e:
        print(f"[WARN] Summarization failed: {e}")
        return text.strip()

def fetch_full_article(link):
    try:
        print(f"[INFO] Fetching article: {link}")
        res = requests.get(link, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.content, 'html.parser')

        article_body = soup.find("div", {"class": "caas-body"})
        if not article_body:
            article_tag = soup.find("article")
            paragraphs = article_tag.find_all("p") if article_tag else soup.find_all("p")
        else:
            paragraphs = article_body.find_all("p")

        article_text = " ".join(p.get_text() for p in paragraphs).strip()

        if len(article_text.split()) < 30:
            return None, None

        img_tag = soup.find("img", {"class": "caas-img"})
        image_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

        return article_text, image_url

    except Exception as e:
        print(f"[WARN] Error fetching article content: {e}")
        return None, None

def process_article(item, delay_between_requests=0):
    title = item.title.text.strip()
    link = item.link.text.strip()
    if not link.startswith("https://finance.yahoo.com"):
        return None

    article_text, image_url = fetch_full_article(link)
    if delay_between_requests > 0:
        time.sleep(delay_between_requests)

    if not article_text:
        print(f"[WARN] Skipped '{title}' - no content.")
        return None

    final_text = summarize_if_needed(article_text)
    summary = to_gen_z_style(final_text)

    return {
        "headline": title,
        "url": link,
        "summary": summary,
        "image_url": image_url,
        "source": "Yahoo",
        "scraped_at": datetime.now()
    }

def scrape_yahoo_news(max_articles=5, max_workers=1, delay_between_requests=0):
    print("[INFO] Fetching RSS feed...")
    res = requests.get(RSS_URL, headers=HEADERS)
    soup = BeautifulSoup(res.content, features="xml")
    items = soup.find_all("item")

    print(f"[INFO] Found {len(items)} articles in RSS feed.")
    articles = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_article, item, delay_between_requests): item for item in items}

        for future in as_completed(futures):
            article = future.result()
            if article:
                articles.append(article)
                if len(articles) >= max_articles:
                    break

    return articles

if __name__ == "__main__":
    results = scrape_yahoo_news(max_articles=5, max_workers=1, delay_between_requests=1)

    if not results:
        print("[❌] No valid Yahoo Finance articles found.")
    else:
        for article in results:
            print(f"\n📰 {article['headline']}")
            print(f"🔗 {article['url']}")
            print(f"🖼️ {article.get('image_url')}")
            print(f"📝 {article['summary']}")
