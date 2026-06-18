import requests
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

url = 'https://www.moneycontrol.com/news/business/markets/'

def scrape_moneycontrol_news():
    # Using a session helps persist cookies, which makes you look more human
    session = requests.Session()
    response = session.get(url, headers=headers)
    
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
            link_tag = title_tag.find_parent('a') 
            if not link_tag:
                 continue
                 
            link = link_tag['href']
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

# Run the scraper
if __name__ == "__main__":
    results = scrape_moneycontrol_news()
    for news in results[:3]: # Print first 3 to test
        print(news)