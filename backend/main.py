# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import scraper
import llm_utils
import factcheck_api
import search_api
import scoring

# --- Pydantic Models ---
class Request(BaseModel):
    text: str = None
    url: str = None

class Response(BaseModel):
    verdict: str
    confidence_score: float
    explanation: str
    sources: list

# --- FastAPI App ---
app = FastAPI(
    title="Fake News Detection API",
    description="An API to analyze text or URLs for potential misinformation.",
    version="1.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/analyze", response_model=Response)
async def analyze_text(request: Request):
    """
    Analyzes a piece of text or a URL to detect fake news.
    """
    if not request.text and not request.url:
        raise HTTPException(status_code=400, detail="Please provide either 'text' or a 'url'.")

    input_text = request.text
    if request.url:
        try:
            input_text = scraper.scrape_article_content(request.url)
            if not input_text:
                 raise HTTPException(status_code=500, detail="Could not scrape content from the URL.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to scrape URL: {e}")

    # 1. LLM Initial Analysis
    llm_judgment = llm_utils.get_llm_judgment(input_text)

    # 2. External Verification - Fact Check API
    fact_check_results = factcheck_api.query_fact_check_api(input_text)

    # 3. External Verification - Programmable Search Engine
    search_engine_results = search_api.search_custom_engine(input_text)

    # 4. Similarity Scoring
    user_embedding = llm_utils.get_embedding(input_text)
    source_texts = [item['snippet'] for item in search_engine_results]
    similarity_scores = []
    if source_texts:
        source_embeddings = llm_utils.get_embeddings(source_texts)
        similarity_scores = llm_utils.calculate_similarity(user_embedding, source_embeddings)

    # 5. Final Aggregation and Scoring
    final_verdict = scoring.aggregate_and_score(
        llm_judgment,
        fact_check_results,
        search_engine_results,
        similarity_scores
    )

    # Format sources for the response
    sources = fact_check_results + search_engine_results

    return Response(
        verdict=final_verdict['verdict'],
        confidence_score=final_verdict['confidence_score'],
        explanation=final_verdict['explanation'],
        sources=sources
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
