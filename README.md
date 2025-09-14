
# Fake News Detector — Gemini Edition (Local)

This version uses **Google Gemini API** for:
- Real LLM classification (keywords, label, fake-confidence, rationale)
- **Embeddings** (text-embedding-004) for semantic similarity with fact-check text

Plus optional **Google Fact Check Tools API** to fetch verified claims.

## Setup

1) Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2) Set your API keys in the terminal (required for real LLM + embeddings):
```bash
# Gemini
export GEMINI_API_KEY=YOUR_GEMINI_KEY
# or: export GOOGLE_API_KEY=YOUR_GEMINI_KEY

# Optional: Google Fact Check Tools
export GOOGLE_FACTCHECK_API_KEY=YOUR_FACTCHECK_KEY
```

*(Windows PowerShell)*
```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_KEY"
$env:GOOGLE_FACTCHECK_API_KEY="YOUR_FACTCHECK_KEY"
```

3) Run the backend:
```bash
python app.py
# http://127.0.0.1:5000/health should show ok:true
```

4) Open `frontend/index.html` in your browser and test with text or a URL.

## Notes
- Verdict logic: weighted blend of Gemini fake-prob, Fact Check confidence, and embedding similarity.
- Tweak weights in `app.py` and mapping rules in `factcheck_api.py` to match your preferences.
- If you lack API keys, the app still runs but falls back to neutral values.

## Next Steps
- Add Google Programmable Search JSON API for additional evidence.
- Persist results in a local DB (SQLite) or Firestore when moving to GCP.
- Deploy to Cloud Run with Secret Manager for keys.
