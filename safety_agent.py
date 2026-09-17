def evaluate_safety_and_scope(user_query: str) -> dict:
    prompt = f"""You are a strict Clinical Safety and Scope Agent. 
    Evaluate the user query: "{user_query}"

    RULE 1 (OUT OF SCOPE): If the query is a greeting (e.g., "hello"), a general question (e.g., "what is your name?"), or anything NOT related to a medical symptom, you MUST set "safe": false and "is_emergency": false.
    RULE 2 (EMERGENCY): If the query describes severe/life-threatening symptoms (e.g., chest pain, heavy bleeding, stroke signs, severe breathing issues), you MUST set "safe": false and "is_emergency": true.
    RULE 3 (SAFE): ONLY if it is a non-emergency, medical symptom (e.g., mild fever, sore throat), set "safe": true and "is_emergency": false.

    Respond STRICTLY in JSON format:
    {{
        "safe": true or false,
        "confidence_score": 0.0 to 1.0,
        "is_emergency": true or false,
        "clinical_reasoning": "Brief explanation of your decision",
        "message": "If out of scope, say 'I am a healthcare AI and can only process medical queries.' If emergency, say 'Call emergency services immediately.'"
    }}"""

    response = query_llm(prompt) # (Use your existing LLM call here)
    
    import json, re
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception:
        pass
        
    # Failsafe
    return {"safe": False, "confidence_score": 0.0, "is_emergency": False, "message": "Could not verify safety."}
