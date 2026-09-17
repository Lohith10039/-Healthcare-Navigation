import os
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
import google.generativeai as genai

# Import team modules
from agents import agent_guideline_safety, agent_department_recommendation, query_llm
from tools import query_live_hospitals_osm
from rag_engine import populate_knowledge_base

# Ensure RAG DB is populated on startup
populate_knowledge_base()

# Define the State Schema
class NavigationState(TypedDict):
    user_query: str
    safety_result: dict
    department_result: dict
    hospitals: list
    final_output: str

# Initialize the LangGraph Workflow
workflow = StateGraph(NavigationState)

# --- Define Nodes ---

def node_safety_check(state: NavigationState) -> dict:
    """Node 1: Evaluates safety boundaries and clinical emergency flags."""
    print("\n--- [Orchestrator] Executing Safety Check Node ---")
    result = agent_guideline_safety(state["user_query"])
    return {"safety_result": result}

def node_department_routing(state: NavigationState) -> dict:
    """Node 2: Retrieves vector RAG context and assigns medical department."""
    print("\n--- [Orchestrator] Executing Department RAG Node ---")
    result = agent_department_recommendation(state["user_query"])
    return {"department_result": result}

def node_hospital_search(state: NavigationState) -> dict:
    """Node 3: Executes live OpenStreetMap tool call for physical clinics."""
    print("\n--- [Orchestrator] Executing Live Hospital Search Tool Node ---")
    dept = state["department_result"].get("recommended_department", "General Medicine")
    hospitals = query_live_hospitals_osm()
    return {"hospitals": hospitals}

def node_synthesize_response(state: NavigationState) -> dict:
    """Node 4: Synthesizes final structured navigation response for the user."""
    print("\n--- [Orchestrator] Executing Response Synthesis Node ---")
    
    query = state["user_query"]
    dept = state["department_result"].get("recommended_department")
    rationale = state["department_result"].get("department_rationale")
    hospitals = state["hospitals"]
    
    hospital_text = "\n".join([f"- {h['name']} ({h['distance_km']} km away, {h['travel_time_min']} mins)" for h in hospitals])
    
    synthesis_prompt = f"""You are an expert AI Healthcare Navigation Assistant. 
User Query: "{query}"
Recommended Department: {dept}
Clinical Rationale: {rationale}
Nearby Facilities Found via Live Maps:
{hospital_text}

Task: Write a concise, professional navigation recommendation for the patient. Do not diagnose them. Provide the department they should visit and list the top physical facilities found nearby with travel distances."""

    response_text = query_llm(synthesis_prompt)
    return {"final_output": response_text}

# --- Conditional Logic (The Safety Gate) ---


def evaluate_safety_routing(state: NavigationState) -> str:
    safety = state["safety_result"]
    if not safety.get("safe_to_navigate") or safety.get("confidence_score", 0) < 0.70:
        return "block"
    return "proceed"

# --- Build and Compile the Graph ---

workflow.add_node("safety_check", node_safety_check)
workflow.add_node("department_routing", node_department_routing)
workflow.add_node("hospital_search", node_hospital_search)
workflow.add_node("synthesize_response", node_synthesize_response)

workflow.set_entry_point("safety_check")

workflow.add_conditional_edges(
    "safety_check",
    evaluate_safety_routing,
    {
        "block": END,
        "proceed": "department_routing"
    }
)

workflow.add_edge("department_routing", "hospital_search")
workflow.add_edge("hospital_search", "synthesize_response")
workflow.add_edge("synthesize_response", END)

compiled_graph = workflow.compile()
