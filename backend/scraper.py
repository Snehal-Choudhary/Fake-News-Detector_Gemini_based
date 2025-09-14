# backend/scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_article_content(url: str) -> str:
    """
    Scrapes the main article text from a given URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all paragraph tags - a simple but often effective method
        paragraphs = soup.find_all('p')
        article_text = ' '.join([p.get_text() for p in paragraphs])

        return article_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""
