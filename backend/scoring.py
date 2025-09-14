# backend/scoring.py

def aggregate_and_score(llm_judgment: dict, fact_check_results: list, search_results: list, similarity_scores: list) -> dict:
    """
    Aggregates all signals and computes a final verdict and confidence score.
    This is a simple heuristic-based scoring model. A more advanced system
    might use a machine learning model.
    """
    final_score = 0.0
    explanation_parts = []

    # 1. Weight LLM Judgment
    llm_confidence = llm_judgment.get('confidence', 0.0)
    llm_verdict = llm_judgment.get('judgment', 'uncertain')

    if llm_verdict == 'real':
        final_score += llm_confidence * 0.15  # Reduced weight to 15%
    elif llm_verdict == 'fake':
        final_score -= llm_confidence * 0.15
    explanation_parts.append(f"Initial LLM analysis suggested '{llm_verdict}' with {llm_confidence:.2f} confidence.")

    # 2. Weight Fact Check Results
    if fact_check_results:
        num_fake_ratings = sum(1 for r in fact_check_results if r['rating'] and 'false' in r['rating'].lower())
        if num_fake_ratings > 0:
            final_score -= 0.60 # Strong negative signal
            explanation_parts.append(f"Found {num_fake_ratings} fact-checks rating the claim as false.")
        else:
            final_score += 0.20 # Mild positive signal if claims exist but aren't rated false
            explanation_parts.append("Found related fact-checks, none of which rated the claim as false.")
    else:
        explanation_parts.append("No direct matches found in fact-checking databases.")


    # 3. Weight Search Results & Similarity (INCREASED IMPORTANCE)
    if search_results and similarity_scores:
        avg_similarity = sum(similarity_scores) / len(similarity_scores)
        # If the content is very similar to results from trusted sources, it's more likely to be real.
        # This is now the strongest positive signal.
        final_score += avg_similarity * 0.50 # Increased weight to 50%
        explanation_parts.append(f"The claim has an average similarity of {avg_similarity:.2f} to articles from trusted news sources.")
    else:
        # If no similar articles are found, it's a negative signal.
        final_score -= 0.10
        explanation_parts.append("Could not find highly similar articles from configured trusted sources.")


    # Normalize score to be between 0 and 1
    confidence_score = (final_score + 1) / 2
    confidence_score = max(0, min(1, confidence_score)) # Clamp between 0 and 1


    # Determine final verdict (Adjusted Thresholds)
    if confidence_score > 0.65: # Lowered threshold for 'Real'
        verdict = "Likely Real"
    elif confidence_score < 0.40: # Adjusted threshold for 'Fake'
        verdict = "Likely Fake"
    else:
        verdict = "Unverified"

    return {
        "verdict": verdict,
        "confidence_score": confidence_score,
        "explanation": " ".join(explanation_parts)
    }
