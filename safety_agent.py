def evaluate_safety_and_scope(user_query: str) -> dict:
    prompt = f"""You are a strict Clinical Safety and Scope Agent. 
    Evaluate the following user query: "{user_query}"

    Rules:
    1. SCOPE CHECK: Is this a health or medical concern? If the user is asking a general question (e.g., "What is your name?", "How are you?"), programming questions, or anything non-medical, you MUST set "safe": false and "is_emergency": false.
    2. EMERGENCY CHECK: Does this indicate a medical emergency (e.g., severe chest pain, heavy bleeding, unconsciousness, severe breathing difficulty)? If yes, you MUST set "safe": false and "is_emergency": true.
    3. ROUTINE: Only if it is a safe, non-emergency medical symptom (e.g., mild fever, rash, sore throat) should you set "safe": true.

    Respond STRICTLY in valid JSON format:
    {{
        "safe": true or false,
        "confidence_score": 0.0 to 1.0,
        "is_emergency": true or false,
        "clinical_reasoning": "Brief explanation of your decision",
        "message": "If out of scope, say 'I am a healthcare navigation assistant and can only process medical concerns.' If emergency, say 'Please seek immediate emergency care.'"
    }}"""

    # ... (Keep your existing LLM execution code here) ...
    
    # Example of how the rest of your function likely looks:
    response = query_llm(prompt) # Or client.models.generate_content(...)
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception:
        pass
        
    # Failsafe fallback
    return {"safe": False, "confidence_score": 0.0, "is_emergency": False, "message": "Failed to evaluate safety. Please try again."}
