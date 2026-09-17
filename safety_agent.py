import json
import re
from google import genai
import os
import streamlit as st

# Ensure client is initialized safely
api_key = os.getenv("GEMINI_API_KEY")
try:
    if not api_key and hasattr(st, "secrets"):
        api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

client = genai.Client(api_key=api_key) if api_key else None

def evaluate_safety_and_scope(user_query: str) -> dict:
    """Strictly evaluates safety, putting life-threatening emergencies first."""
    
    # Absolute hardcoded keyword safety net for critical emergencies 
    # (Catches severe symptoms instantly even if the LLM formatting glitches)
    emergency_keywords = ["chest pain", "breath", "stroke", "bleed", "unconscious", "heart attack", "suicide", "collapse"]
    is_hard_emergency = any(keyword in user_query.lower() for keyword in emergency_keywords)
    
    if is_hard_emergency:
        return {
            "safe": False,
            "confidence_score": 1.0,
            "is_emergency": True,
            "is_general_query": False,
            "clinical_reasoning": "Critical emergency keywords detected by safety net.",
            "message": "🚨 EMERGENCY DETECTED: Please call emergency services (112) or go to the nearest emergency room immediately."
        }

    prompt = f"""You are a strict Clinical Safety Agent for a healthcare navigation tool.
    Analyze this user query: "{user_query}"

    Evaluate based on these strict priority rules:
    1. EMERGENCY: Does the query describe life-threatening symptoms (chest pain, severe bleeding, breathing trouble, stroke)? If YES, set "safe": false, "is_emergency": true, "is_general_query": false.
    2. GENERAL CHAT: Is it pure casual non-medical chat (e.g., "what is your name?", "hello")? If YES, set "safe": false, "is_emergency": false, "is_general_query": true.
    3. MEDICAL: Is it a non-emergency medical symptom (fever, sore throat, rash)? If YES, set "safe": true, "is_emergency": false, "is_general_query": false.

    Respond STRICTLY with a JSON object:
    {{
        "safe": true or false,
        "confidence_score": 0.0 to 1.0,
        "is_emergency": true or false,
        "is_general_query": true or false,
        "clinical_reasoning": "Short explanation",
        "message": "Friendly response if general chat, or emergency instruction if emergency, or blank if safe medical."
    }}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text_response = response.text
        
        json_match = re.search(r"\{.*\}", text_response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            if isinstance(result, dict):
                return result
    except Exception as e:
        print(f"Safety Agent Error: {e}")

    # Safe Fallback: If LLM fails, check if it looks like a greeting or treat as out-of-scope/medical review
    is_chat = any(w in user_query.lower() for w in ["hello", "hi", "name", "who are you"])
    if is_chat:
        return {
            "safe": False,
            "is_general_query": True,
            "is_emergency": False,
            "confidence_score": 0.9,
            "message": "Hello! I am SperAI, your healthcare navigation assistant. How can I help you today?"
        }
        
    # Default fallback for unparseable medical inputs (fails safe, blocks navigation)
    return {
        "safe": False,
        "is_emergency": False,
        "is_general_query": false,
        "confidence_score": 0.5,
        "message": "Please consult a healthcare professional regarding your symptoms."
    }
