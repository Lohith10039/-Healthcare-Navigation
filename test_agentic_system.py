from rag_engine import populate_knowledge_base
from agents import agent_guideline_safety, agent_department_recommendation
from tools import query_live_hospitals_osm

def main():
    print("=== INITIALIZING VECTOR RAG DATABASE ===")
    populate_knowledge_base()
    
    queries = [
        "I have severe sharp pain in my eye with sudden blurred vision.",
        "I am having acute crushing chest pain radiating down my left arm."
    ]
    
    for q in queries:
        print(f"\n=======================================================")
        print(f"USER INPUT: '{q}'")
        print("=======================================================")
        
        # 1. Agent 1: LLM Safety Critic
        print("[*] AGENT 1 (Guideline/Safety Critic) Reasoning...")
        safety_eval = agent_guideline_safety(q)
        print(f" -> Confidence Score: {safety_eval.get('confidence_score')}")
        print(f" -> Emergency Flag: {safety_eval.get('is_emergency')}")
        print(f" -> Safety Verdict: {'PROCEED' if safety_eval.get('safe_to_navigate') else 'ESCALATE / BLOCK'}")
        print(f" -> LLM Reasoning: {safety_eval.get('clinical_reasoning')}")
        
        if not safety_eval.get("safe_to_navigate") or safety_eval.get("confidence_score", 0) < 0.70:
            print(f" [!] WORKFLOW HALTED BY SAFETY CRITIC: {safety_eval.get('escalation_message')}")
            continue
            
        # 2. Agent 4: RAG Department Recommender
        print("\n[*] AGENT 4 (Department Recommender) Querying Vector Store...")
        dept_eval = agent_department_recommendation(q)
        print(f" -> Recommended Department: {dept_eval.get('recommended_department')}")
        print(f" -> Grounded Vector Evidence: {dept_eval.get('retrieved_evidence')}")
        
        # 3. Dynamic Tool Call: Live Map Facilities
        print("\n[*] AGENT 5 (Hospital Search) Calling Live OpenStreetMap API...")
        live_facilities = query_live_hospitals_osm()
        print(f" -> Discovered {len(live_facilities)} Real Physical Healthcare Facilities:")
        for fac in live_facilities:
            print(f"    • {fac['name']} ({fac['distance_km']} km away)")

if __name__ == "__main__":
    main()