# backend/search_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search_custom_engine(query: str) -> list:
    """
    Searches the web using a Google Programmable Search Engine.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("PROGRAMMABLE_SEARCH_ENGINE_ID")
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        
        # Simplify the response
        results = []
        for item in items:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
                "source": "Programmable Search"
            })
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error querying Programmable Search Engine: {e}")
        return []

