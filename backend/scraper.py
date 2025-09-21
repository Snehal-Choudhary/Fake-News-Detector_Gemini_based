# backend/scraper.py

import requests
from bs4 import BeautifulSoup

def scrape_article_content(url: str) -> str:
    """
    Scrapes the main article content from a URL.
    This version is more robust and tries to find the main content area.
    """
    try:
        # Use a more common user-agent to avoid simple bot blockers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Raise an exception if the request was not successful
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Intelligent Content Extraction ---
        # Modern news sites often use <article> or <main> tags for the primary content.
        
        main_content = soup.find('article')
        if not main_content:
            main_content = soup.find('main')

        # If we found a main content area, get text only from there.
        # This is much more accurate than getting all paragraphs from the page.
        if main_content:
            paragraphs = main_content.find_all('p')
        else:
            # Fallback to the old method if specific tags aren't found
            paragraphs = soup.find_all('p')

        # Join the text from all found paragraphs
        article_text = ' '.join([p.get_text() for p in paragraphs])

        # A basic cleanup
        if not article_text:
            return "Scraping failed: No readable text content found."
            
        return article_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {e}")
        return f"Scraping failed: Could not retrieve the URL. Error: {e}"
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        return f"Scraping failed: An unexpected error occurred. Error: {e}"

