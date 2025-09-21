# backend/scoring.py
import llm_utils

def aggregate_and_score(llm_judgment: dict, fact_check_results: list, search_results: list, user_claim: str) -> dict:
    """
    Aggregates signals with cost-saving logic and calculates a clear,
    intuitive confidence score for the final verdict.
    """
    final_score = 0.0
    explanation_parts = []

    # --- Start of Conditional Logic for Quick Verdicts ---

    # Step 1: Check for a definitive fact-check result first. This is the most reliable signal.
    if fact_check_results:
        num_fake_ratings = sum(1 for r in fact_check_results if r['rating'] and 'false' in r['rating'].lower())
        if num_fake_ratings > 0:
            explanation_parts.append(f"A definitive fact-check from a trusted source rated this claim as false.")
            return {
                "verdict": "Likely Fake",
                "confidence_score": 0.99, # Near-certain confidence (0.0 to 1.0)
                "explanation": " ".join(explanation_parts)
            }

    # Step 2: Check if the initial LLM analysis is overwhelmingly confident about an absurd claim.
    llm_verdict = llm_judgment.get('judgment', 'uncertain')
    llm_confidence = llm_judgment.get('confidence', 0.0)
    explanation_parts.append(f"Initial LLM analysis suggested '{llm_verdict}' with {llm_confidence:.2f} confidence.")

    if llm_verdict == 'fake' and llm_confidence > 0.98:
        explanation_parts.append("The claim is highly implausible on its face and contradicts common knowledge.")
        return {
            "verdict": "Likely Fake",
            "confidence_score": 0.98, # Very high confidence (0.0 to 1.0)
            "explanation": " ".join(explanation_parts)
        }

    # --- End of Conditional Logic ---
    # If the claim is not obviously fake, proceed with the full, detailed analysis.

    # 3. If we're here, we need the expensive verification call against trusted sources.
    if search_results:
        source_snippets = [item['snippet'] for item in search_results]
        verification = llm_utils.verify_claim_with_sources(user_claim, source_snippets)
        
        if verification.get('supports_claim'):
            final_score += 0.70 # Strong positive signal
            explanation_parts.append("Trusted news sources appear to support the claim.")
        else:
            final_score -= 0.70 # Strongest negative signal for contradiction or omission
            explanation_parts.append("Trusted news sources do not support the specific details of the claim.")
        
        # Ensure the reason from the LLM is always included if available
        if verification.get('reason'):
            explanation_parts.append(f"Verification reason: {verification.get('reason')}")
    else:
        final_score -= 0.20
        explanation_parts.append("Could not find any relevant articles from trusted sources.")

    # --- New, Clearer Scoring Logic ---
    
    # Normalize the score. This score represents the likelihood of being REAL (0.0 = Fake, 1.0 = Real)
    real_likelihood_score = (final_score + 1) / 2
    real_likelihood_score = max(0, min(1, real_likelihood_score))

    # Determine the final verdict and a clear confidence value (0.0 to 1.0)
    verdict = ""
    confidence_value = 0.0

    if real_likelihood_score > 0.7:
        verdict = "Likely Real"
        confidence_value = real_likelihood_score
    elif real_likelihood_score < 0.4:
        verdict = "Likely Fake"
        # Confidence in a "Fake" verdict is the inverse of the "Real" likelihood
        confidence_value = 1 - real_likelihood_score
    else:
        verdict = "Unverified"
        # Confidence for "Unverified" should be low, reflecting the uncertainty.
        # This formula calculates how close the score is to the absolute middle (0.5),
        # and we scale it to a max of 50% to be more intuitive for the user.
        unverified_confidence = 1 - abs(real_likelihood_score - 0.5) * 2
        confidence_value = unverified_confidence * 0.5

    # Final safeguard to ensure confidence is always within the valid 0.0-1.0 range.
    confidence_value = max(0.0, min(1.0, confidence_value))

    return {
        "verdict": verdict,
        "confidence_score": confidence_value,
        "explanation": " ".join(explanation_parts) if explanation_parts else "Analysis could not determine a reason."
    }

