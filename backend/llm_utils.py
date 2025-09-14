# backend/llm_utils.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from numpy import dot
from numpy.linalg import norm

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_llm_judgment(text: str) -> dict:
    """
    Uses Gemini 1.5 Flash to get an initial credibility judgment.
    """
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
        # Basic parsing, assuming the model returns a JSON string-like structure
        # In a production system, you'd want more robust parsing and error handling
        import json
        clean_response = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_response)
    except Exception as e:
        print(f"Error in LLM judgment: {e}")
        return {
            "keywords": [], "entities": [], "context": "",
            "judgment": "uncertain", "confidence": 0.0
        }

def get_embedding(text: str):
    """
    Generates embeddings for a single piece of text.
    """
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return []

def get_embeddings(texts: list[str]):
    """
    Generates embeddings for a batch of texts.
    """
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=texts,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error getting batch embeddings: {e}")
        return [[] for _ in texts]


def calculate_similarity(vec1, vec2_list):
    """
    Calculates cosine similarity between one vector and a list of other vectors.
    """
    scores = []
    for vec2 in vec2_list:
        if not vec1 or not vec2:
            scores.append(0.0)
            continue
        cos_sim = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
        scores.append(cos_sim)
    return scores
