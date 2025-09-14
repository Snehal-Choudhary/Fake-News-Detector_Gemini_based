# backend/factcheck_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def query_fact_check_api(query: str) -> list:
    """
    Queries the Google Fact Check API.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        claims = data.get("claims", [])
        
        # Simplify the response
        results = []
        for claim in claims:
            results.append({
                "claim": claim.get("text"),
                "claimant": claim.get("claimant"),
                "rating": claim.get("claimReview", [{}])[0].get("textualRating"),
                "url": claim.get("claimReview", [{}])[0].get("url"),
                "source": "Google Fact Check API"
            })
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error querying Fact Check API: {e}")
        return []
