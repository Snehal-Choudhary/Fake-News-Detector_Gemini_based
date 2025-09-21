# backend/llm_utils.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_llm_judgment(text: str) -> dict:
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analyze the following text for credibility. Based ONLY on the text provided,
    extract keywords, named entities, and provide a brief summary of the context.
    Then, provide an initial credibility judgment as 'real', 'fake', or 'uncertain'.
    Finally, give a confidence score for your judgment from 0.0 to 1.0.

    Return the result as a JSON object with keys: "keywords", "entities", "context", "judgment", "confidence".

    Text to analyze:
    ---
    {text}
    ---
    """
    try:
        response = model.generate_content(prompt)
        clean_response = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_response)
    except Exception as e:
        print(f"Error in LLM judgment: {e}")
        return {
            "keywords": [], "entities": [], "context": "",
            "judgment": "uncertain", "confidence": 0.0
        }

def verify_claim_with_sources(claim: str, sources: list[str]) -> dict:
    model = genai.GenerativeModel('gemini-1.5-flash')
    source_snippets = "\n".join(f"- {s}" for s in sources)

    prompt = f"""
    User's Claim: "{claim}"

    Search Result Snippets from trusted news sources:
    {source_snippets}

    Based on the provided search snippets, do they support the user's specific claim?
    The key is whether the *specific details* of the claim are mentioned in the sources.
    For example, if the claim is about "free smartphones" but the sources only mention the "PM-Kisan scheme" in general, they do not support the claim.
    If the claim is "PM Modi Killed Rahul Gandhi" and the sources talk about political criticism, the sources DO NOT support the claim.

    Provide your answer as a JSON object with two keys:
    1. "supports_claim": boolean (true if the sources support the claim, false if they contradict or do not mention the specific details)
    2. "reason": A brief explanation for your decision.
    """
    try:
        response = model.generate_content(prompt)
        clean_response = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_response)
    except Exception as e:
        print(f"Error in LLM claim verification: {e}")
        return {
            "supports_claim": False,
            "reason": "Could not perform LLM verification due to an error."
        }
