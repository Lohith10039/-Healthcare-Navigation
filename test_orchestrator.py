from orchestrator import compiled_graph

def run_test():
    test_queries = [
        "I have severe sharp pain in my eye with sudden blurred vision.",
        "I am having acute crushing chest pain radiating down my left arm."
    ]
    
    for query in test_queries:
        print(f"\n==============================================")
        print(f"RUNNING GRAPH FOR: '{query}'")
        print(f"==============================================")
        
        initial_state = {
            "user_query": query,
            "safety_result": {},
            "department_result": {},
            "hospitals": [],
            "final_output": ""
        }
        
        result = compiled_graph.invoke(initial_state)
        
        if result["safety_result"].get("confidence_score", 1.0) < 0.70 or not result["safety_result"].get("safe_to_navigate"):
            print(f"\n[🛑 BLOCKED BY SAFETY GATE]")
            print(result["safety_result"].get("escalation_message"))
        else:
            print(f"\n[✅ SUCCESSFUL NAVIGATION OUTPUT]")
            print(result["final_output"])

if __name__ == "__main__":
    run_test()
    