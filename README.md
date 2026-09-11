# -Healthcare-Navigation



# 🏥 Healthcare Navigation AI

## Overview
Healthcare Navigation AI is an intelligent healthcare assistance system that helps users identify the most appropriate medical department based on their symptoms and recommends nearby healthcare facilities. The solution combines Agentic AI, Retrieval-Augmented Generation (RAG), safety screening, and real-time hospital discovery to provide reliable healthcare navigation without performing medical diagnosis.

## Problem Statement
Many patients struggle to determine which medical department they should visit for their symptoms. This often leads to delays in treatment, unnecessary hospital visits, and confusion, especially during urgent situations. Additionally, finding accessible healthcare facilities nearby can be challenging for elderly and disabled individuals.

## Solution
Healthcare Navigation AI analyzes user-reported symptoms, performs safety screening, recommends the appropriate medical department, and suggests nearby hospitals or clinics with route and accessibility information. The system prioritizes patient safety by identifying emergency situations and directing users toward immediate medical attention when necessary.

## Key Features

### 🤖 Agentic AI Workflow
- Multi-agent architecture for healthcare navigation.
- Intelligent task orchestration using LangGraph.

### 📚 Retrieval-Augmented Generation (RAG)
- Clinical knowledge base powered by ChromaDB.
- Context-aware department recommendations.

### 🛡️ Safety Agent
- Screens user symptoms for potential emergencies.
- Blocks unsafe navigation recommendations.
- Escalates critical cases for immediate medical attention.

### 🏥 Department Recommendation Agent
- Maps symptoms to relevant medical departments.
- Provides rationale for recommendations.

### 📍 Live Hospital Discovery
- Retrieves nearby hospitals and clinics using OpenStreetMap.
- Calculates distance and estimated travel time.
- Includes accessibility information where available.

### ♿ Accessibility Support
- Highlights wheelchair-accessible facilities.
- Improves healthcare access for disabled users.

## Technology Stack

- Python
- Google Gemini API
- LangGraph
- ChromaDB
- OpenStreetMap (Overpass API)
- Retrieval-Augmented Generation (RAG)

## System Architecture

User Query
↓
Safety Agent
↓
Department Recommendation Agent (RAG)
↓
Hospital Finder Tool
↓
Response Synthesis Agent
↓
Final Recommendation

## Project Structure

```text
Healthcare-Navigation/
│
├── agents.py
├── tools.py
├── rag_engine.py
├── rag_store.py
├── safety_agent.py
├── test_agentic_system.py
├── test_eval.py
├── README.md
│
├── maps/
│   ├── __init__.py
│   ├── hospital_finder.py
│   └── test_hospital_finder.py
│
├── orchestrator/
│   ├── orchestrator.py
│   └── test_orchestrator.py
│
└── rag_db/
```

## Target Users

- Patients unsure which medical department to visit.
- Elderly individuals requiring healthcare guidance.
- People with disabilities needing accessible facilities.
- First-time hospital visitors.
- Residents of rural and semi-urban areas.
- Healthcare support staff assisting patient navigation.

## Example Workflow

### User Input
> "I have severe eye pain and sudden blurred vision."

### System Output
- Recommended Department: Ophthalmology
- Safety Assessment: Urgent attention recommended
- Nearby Hospitals:
  - KIMSHEALTH Trivandrum
  - Government Medical College Hospital
  - Ananthapuri Hospitals

## Benefits

- Reduces confusion in healthcare navigation.
- Helps users reach appropriate care faster.
- Supports accessibility-aware hospital selection.
- Improves patient safety through emergency screening.
- Provides real-time healthcare facility recommendations.

## Future Enhancements

- GPS-based live user location detection.
- Hospital bed availability integration.
- Appointment booking support.
- Ambulance and emergency service integration.
- Multilingual healthcare assistance.
- Voice-based interaction.

## Team Contribution

- **Member 1:** Agent Orchestration (LangGraph Workflow)
- **Member 2:** RAG System & Clinical Knowledge Base
- **Member 3:** Hospital Discovery & Maps Integration
- **Member 4:** Frontend Development
- **Member 5:** Testing, Evaluation & Documentation

## Disclaimer

This system is designed for healthcare navigation and guidance only. It does not provide medical diagnoses or replace professional medical advice. Users should consult qualified healthcare professionals for medical decisions.

---

**Built for the Agentic AI Hackathon 🚀**  
**Theme: Intelligent Healthcare Navigation using Agentic AI** 🏥🤖
