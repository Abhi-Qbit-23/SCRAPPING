import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random

# Realistic browser headers including sec-ch-ua and referer chain
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

BASE_URL = 'https://www.moneycontrol.com'
NEWS_URL = 'https://www.moneycontrol.com/news/business/markets/'
RSS_URL  = 'https://www.moneycontrol.com/rss/latestnews.xml'


def _build_session() -> requests.Session:
    """
    Create a session that first visits the homepage to collect cookies,
    simulating a real browser navigation flow.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        # Warm up: hit homepage so cookies / consent tokens are set
        warm_resp = session.get(BASE_URL, timeout=15, allow_redirects=True)
        print(f"[INFO] Session warm-up: {warm_resp.status_code}")
        # Small human-like delay before the actual request
        time.sleep(random.uniform(1.5, 3.0))
    except Exception as e:
        print(f"[WARN] Session warm-up failed (continuing anyway): {e}")

    return session


def _fetch_with_retry(session: requests.Session, url: str, retries: int = 3) -> requests.Response | None:
    """GET with exponential backoff on 403/429/5xx."""
    for attempt in range(1, retries + 1):
        try:
            # Update Referer to look like we navigated from inside the site
            session.headers.update({'Referer': BASE_URL + '/'})
            response = session.get(url, timeout=15, allow_redirects=True)

            if response.status_code == 200:
                return response

            print(f"[WARN] Attempt {attempt}/{retries} — status {response.status_code} for {url}")

            if response.status_code in (403, 429):
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"[INFO] Backing off {wait:.1f}s before retry…")
                time.sleep(wait)
            else:
                # Non-retryable HTTP error
                break

        except requests.RequestException as e:
            print(f"[WARN] Request error on attempt {attempt}: {e}")
            time.sleep(2 ** attempt)

    return None


def _parse_html_page(html_content: bytes) -> list[dict]:
    """Parse articles from the MoneyControl markets news page HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    news_data = []

    for item in soup.find_all('li', class_='clearfix'):
        try:
            title_tag = item.find('h2')
            if not title_tag:
                continue

            headline = title_tag.get_text(strip=True)
            link_tag = title_tag.find_parent('a')
            if not link_tag:
                continue

            link = link_tag.get('href', '')
            if not link.startswith('http'):
                link = BASE_URL + link

            summary = item.find('p').get_text(strip=True) if item.find('p') else ''

            news_data.append({
                'headline': headline,
                'url': link,
                'summary': summary,
                'source': 'Moneycontrol',
                'scraped_at': datetime.now(),
            })
        except Exception as e:
            print(f"[WARN] Error parsing HTML item: {e}")
            continue

    return news_data


def _scrape_via_rss() -> list[dict]:
    """
    Fallback: parse MoneyControl's public RSS feed.
    RSS endpoints are far less likely to be blocked.
    """
    print("[INFO] Attempting RSS fallback…")
    try:
        resp = requests.get(RSS_URL, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"[ERROR] RSS feed returned {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.content, features='xml')
        items = soup.find_all('item')
        news_data = []

        for item in items:
            try:
                headline = item.find('title').get_text(strip=True) if item.find('title') else ''
                link     = item.find('link').get_text(strip=True)  if item.find('link')  else ''
                desc_tag = item.find('description')
                summary  = BeautifulSoup(desc_tag.get_text(), 'html.parser').get_text(strip=True) if desc_tag else ''

                if headline and link:
                    news_data.append({
                        'headline': headline,
                        'url': link,
                        'summary': summary,
                        'source': 'Moneycontrol',
                        'scraped_at': datetime.now(),
                    })
            except Exception as e:
                print(f"[WARN] Error parsing RSS item: {e}")
                continue

        print(f"[INFO] RSS fallback yielded {len(news_data)} articles.")
        return news_data

    except Exception as e:
        print(f"[ERROR] RSS fallback failed: {e}")
        return []


def scrape_moneycontrol_news() -> list[dict]:
    """
    Primary scraper: attempts the HTML news page with a warmed-up session
    and retry/backoff logic. Falls back to RSS if the page remains blocked.
    """
    session  = _build_session()
    response = _fetch_with_retry(session, NEWS_URL)

    if response is None:
        print("[WARN] HTML scraping failed after retries — switching to RSS fallback.")
        return _scrape_via_rss()

    news_data = _parse_html_page(response.content)

    if not news_data:
        print("[WARN] HTML page returned 200 but no articles parsed — switching to RSS fallback.")
        return _scrape_via_rss()

    print(f"[INFO] Scraped {len(news_data)} articles from MoneyControl HTML page.")
    return news_data


# Run the scraper standalone
if __name__ == "__main__":
    results = scrape_moneycontrol_news()
    if not results:
        print("[❌] No articles found.")
    else:
        for news in results[:3]:
            print(f"\n📰 {news['headline']}\n🔗 {news['url']}\n📝 {news['summary']}")