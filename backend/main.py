# backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import scraper
import llm_utils
import factcheck_api
import search_api
import scoring
import re

app = FastAPI()

# --- CORS Configuration ---
# This list is the "guest list" for your API.
# The URL here MUST EXACTLY MATCH your Netlify site's URL.

# ===> TRIPLE-CHECK THIS LIST! <===
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_url(string):
    """A simple regex check to see if a string is a URL."""
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0_9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, string) is not None

@app.post("/analyze")
async def analyze_text(request: Request):
    data = await request.json()
    input_data = data.get('text', '').strip()
    original_claim = input_data
    
    if is_url(input_data):
        input_text_for_analysis = scraper.scrape_article_content(input_data)
    else:
        input_text_for_analysis = original_claim

    if not input_text_for_analysis or "Scraping failed" in input_text_for_analysis:
        return {
            "verdict": "Unverified",
            "confidence_score": 0.0,
            "explanation": f"Could not analyze the claim. Scraper message: '{input_text_for_analysis}'",
            "supporting_sources": []
        }

    # These API calls are fine using the original claim to find related articles.
    llm_judgment = llm_utils.get_llm_judgment(input_text_for_analysis)
    fact_check_results = factcheck_api.query_fact_check_api(original_claim)
    search_results = search_api.search_custom_engine(original_claim)

    # --- THIS IS THE FIX ---
    # We must pass the SCRAPED TEXT to the final verification, not the original URL.
    final_verdict = scoring.aggregate_and_score(
        llm_judgment,
        fact_check_results,
        search_results,
        input_text_for_analysis # Use the scraped content for the final check
    )
    # --- END OF FIX ---

    final_verdict['supporting_sources'] = search_results
    return final_verdict
