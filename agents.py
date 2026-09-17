import json
import re
from google import genai
from rag_engine import semantic_rag_search
from maps.hospital_finder import find_nearby_hospitals

# ====================================================================
# API CONFIGURATION (Using modern google-genai client)
# ====================================================================
# The client automatically picks up your GEMINI_API_KEY environment variable,
# or you can pass it directly: client = genai.Client(api_key="YOUR_KEY")
import os
import streamlit as st
from google import genai

# Safely resolve the API key for both local and Streamlit Cloud environments
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        raise ValueError("GEMINI_API_KEY is missing! Please add it to Streamlit Advanced Settings -> Secrets.")

client = genai.Client(api_key=api_key)

def query_llm(prompt: str) -> str:
    """Invokes the cloud LLM using the modern Google GenAI SDK."""
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"LLM Inference Error: {str(e)}"

# ====================================================================
# AGENT 1: LLM GUIDELINE & SAFETY CRITIC (Evaluates Risk & Scope)
# ====================================================================
def agent_guideline_safety(user_query: str) -> dict:
    """
    Evaluates safety boundaries, emergencies, and confidence score.
    """
    prompt = f"""You are an AI Clinical Safety and Guideline Agent for a Healthcare Navigation application.
Analyze the user's input: "{user_query}"

Rules:
1. If the query indicates a life-threatening emergency (e.g., heart attack, stroke, heavy bleeding, loss of consciousness), flag it as an emergency.
2. If the user asks for a diagnosis, medication dosage, or prescription, mark it as a boundary violation.
3. Compute a confidence_score between 0.0 and 1.0 evaluating whether it is safe to proceed with standard navigation.
   - For severe emergencies or diagnostic requests, assign a low confidence score (< 0.70) or trigger an emergency stop.

Respond strictly in valid JSON format with this exact structure:
{{
    "safe_to_navigate": true or false,
    "confidence_score": 0.0 to 1.0,
    "is_emergency": true or false,
    "clinical_reasoning": "brief reasoning explaining the evaluation",
    "escalation_message": "instructions if blocked or empty if safe"
}}
JSON:"""

    response = query_llm(prompt)
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception:
        pass
    
    return {
    "safe_to_navigate": False,
    "confidence_score": 0.0,
    "is_emergency": True,
    "clinical_reasoning": "Safety evaluation was unavailable.",
    "escalation_message": "Unable to complete a safety evaluation. If this may be an emergency, seek immediate medical care."
}

# ====================================================================
# AGENT 4: LLM-GROUNDED DEPARTMENT AGENT (Grounded in RAG)
# ====================================================================
def agent_department_recommendation(user_query: str) -> dict:
    """
    Uses vector RAG context to instruct the LLM to select the appropriate department.
    """
    retrieved_chunks = semantic_rag_search(user_query, top_k=2)
    rag_context = "\n---\n".join([c["text"] for c in retrieved_chunks])
    
    prompt = f"""You are the Department Recommendation Agent for Healthcare Navigation.
User Concern: "{user_query}"

Retrieved Clinical Guidelines from Knowledge Base:
{rag_context}

Task:
Based SOLELY on the retrieved clinical evidence above, identify which medical department the patient should be navigated to. Do not diagnose the patient.

Respond strictly in JSON format:
{{
    "recommended_department": "Name of department (e.g. Ophthalmology, Orthopedics, ENT, Dermatology)",
    "retrieved_evidence": "The exact sentence or rule from the clinical guidelines used",
    "department_rationale": "Why this facility matches the patient concern"
}}
JSON:"""

    response = query_llm(prompt)
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            data["rag_chunks"] = retrieved_chunks
            return data
    except Exception:
        pass

    return {
        "recommended_department": retrieved_chunks[0]["metadata"]["department"],
        "retrieved_evidence": retrieved_chunks[0]["text"],
        "department_rationale": "Directly grounded in closest semantic vector match.",
        "rag_chunks": retrieved_chunks
    }

def agent_hospital_navigation(
    user_lat: float | None = None,
    user_lng: float | None = None,
) -> dict:
    """Gets nearby hospitals and strictly sorts them by closest distance."""
    
    # Fallback coordinates if browser GPS is blocked
    user_lat = user_lat if user_lat is not None else 12.9716
    user_lng = user_lng if user_lng is not None else 77.5946

    # Fetch a slightly larger batch to ensure we can sort the absolute closest ones
    raw_hospitals = find_nearby_hospitals(user_lat, user_lng, limit=10)

    if raw_hospitals and isinstance(raw_hospitals, list):
        # Strictly sort the list by distance (closest first)
        raw_hospitals.sort(key=lambda x: x.get('distance_km', 999))
        
        # Keep only the top 3 closest hospitals
        closest_hospitals = raw_hospitals[:3]
    else:
        closest_hospitals = []

    return {
        "location": {"lat": user_lat, "lng": user_lng},
        "hospitals": closest_hospitals,
    }
