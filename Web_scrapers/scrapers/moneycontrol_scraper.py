# scraper.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = 'https://www.moneycontrol.com/news/business/markets/'

def scrape_moneycontrol_news():
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    news_data = []

    top_news_section = soup.find_all('li', class_='clearfix')

    for item in top_news_section:
        try:
            title_tag = item.find('h2')
            if not title_tag:
                continue

            headline = title_tag.get_text(strip=True)
            link = title_tag.find('a')['href']
            summary = item.find('p').get_text(strip=True) if item.find('p') else ''

            news_data.append({
                'headline': headline,
                'url': link,
                'summary': summary,
                'source': 'Moneycontrol',
                'scraped_at': datetime.now()
            })
        except Exception as e:
            print(f"Error parsing item: {e}")
            continue

    return news_data
