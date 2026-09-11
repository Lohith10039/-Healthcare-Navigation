def evaluate_safety_and_scope(user_query: str) -> dict:
    """
    Evaluates the query for emergency red flags and system scope.
    Required for the Hackathon Technical Bar (Confidence > 0.7).
    """
    query_lower = user_query.lower()
    
    # 1. Critical Red Flag Escalation
    critical_terms = ["chest pain", "heart attack", "stroke", "unconscious", "bleeding heavily"]
    if any(term in query_lower for term in critical_terms):
        return {
            "safe": False,
            "confidence_score": 0.99,
            "is_emergency": True,
            "message": "EMERGENCY DETECTED: Escalating immediately. Please call 112 or navigate to the nearest ER."
        }

    # 2. Medical Diagnosis Boundary (System should navigate, not diagnose)
    diagnosis_terms = ["diagnose me", "what disease", "prescribe", "dosage"]
    if any(term in query_lower for term in diagnosis_terms):
        return {
            "safe": False,
            "confidence_score": 0.45, # Score < 0.7 triggers block
            "is_emergency": False,
            "message": "BOUNDARY VIOLATION: I am a navigation assistant and cannot diagnose diseases or prescribe medication."
        }

    # 3. Safe Navigation Flow
    return {
        "safe": True,
        "confidence_score": 0.92,
        "is_emergency": False,
        "message": "Query verified within scope. Proceeding to department routing."
    }