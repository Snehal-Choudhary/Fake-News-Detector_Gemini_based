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
# This list must include the URL of your live Netlify site.
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Default Vite port
    "https://fact-scope.netlify.app" # IMPORTANT: Replace with your actual Netlify URL
]

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
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, string) is not None

@app.post("/analyze")
async def analyze_text(request: Request):
    """
    Main endpoint to analyze text. It detects if the text is a URL.
    """
    data = await request.json()
    input_data = data.get('text', '').strip()
    original_claim = input_data
    
    # --- Step 1: Scrape content if the input is a URL ---
    if is_url(input_data):
        scraped_text = scraper.scrape_article_content(input_data)
        # Use the original URL as the claim if scraping returns very little text
        if len(scraped_text) < len(original_claim) * 0.8:
            input_text_for_analysis = original_claim
        else:
            input_text_for_analysis = scraped_text
    else:
        input_text_for_analysis = original_claim

    # --- Step 2: The Critical Guardrail ---
    # Check if we have any usable text to analyze.
    if not input_text_for_analysis or "Scraping failed" in input_text_for_analysis:
        return {
            "verdict": "Unverified",
            "confidence_score": 0.0,
            "explanation": f"Could not analyze the claim. Scraper message: '{input_text_for_analysis}'",
            "supporting_sources": []
        }

    # --- Step 3: Multi-source Verification ---
    llm_judgment = llm_utils.get_llm_judgment(input_text_for_analysis)
    fact_check_results = factcheck_api.query_fact_check_api(original_claim) # Fact check the original claim
    search_results = search_api.search_custom_engine(original_claim) # Search for the original claim

    # --- Step 4: Final Aggregation and Scoring (Smart Logic) ---
    final_verdict = scoring.aggregate_and_score(
        llm_judgment,
        fact_check_results,
        search_results,
        original_claim  # Always verify against the user's original input
    )

    # --- Step 5: Format and Return Response ---
    final_verdict['supporting_sources'] = search_results

    return final_verdict

