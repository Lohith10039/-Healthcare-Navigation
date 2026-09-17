import streamlit as st
import time
from streamlit_geolocation import streamlit_geolocation

# Cleaned up imports
from agents import (
    agent_department_recommendation,
    agent_hospital_navigation,
)
from safety_agent import evaluate_safety_and_scope
from rag_engine import collection, populate_knowledge_base

# Initialize Knowledge Base
if collection.count() == 0:
    populate_knowledge_base()

# -----------------------------
# 1. Page Configuration & CSS
# -----------------------------
st.set_page_config(page_title="SperAI | Navigation", page_icon="⚕️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .main-title {
        background: -webkit-linear-gradient(45deg, #02aab0, #00cdac);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5em;
        font-weight: 800;
        text-align: center;
        padding-bottom: 0px;
        margin-bottom: 0px;
    }
    div[data-testid="metric-container"] {
        background-color: #1e1e1e;
        border: 1px solid #333;
        padding: 5% 5% 5% 10%;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">⚕️ SperAI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888; font-size: 1.2em; margin-bottom: 30px;">AI-Powered Healthcare Navigation</p>', unsafe_allow_html=True)

# -----------------------------
# 2. User Input Container
# -----------------------------
with st.container(border=True):
    st.subheader("🩺 Describe Your Concern")
    user_query = st.text_area(
        "What are you experiencing?",
        placeholder="Example: I have a sharp pain in my lower right abdomen and a slight fever...",
        height=100
    )

    st.subheader("📍 Your Location")
    
    # Auto-Geolocation Component (No manual input fields)
    location = streamlit_geolocation()
    
    # Set detected coordinates (or default to Bengaluru if not clicked)
    latitude = location.get('latitude') if location and location.get('latitude') else 12.9716
    longitude = location.get('longitude') if location and location.get('longitude') else 77.5946

    if location and location.get('latitude'):
        st.success("✅ Location detected successfully.")
    else:
        st.caption("Click the locator button above to detect your GPS. If not clicked, a default demo location will be used.")

    analyze_button = st.button("🚀 Run SperAI Navigation", type="primary", use_container_width=True)

# -----------------------------
# 3. Agent Execution & Dynamic UI
# -----------------------------
if analyze_button:
    if not user_query.strip():
        st.warning("⚠️ Please describe your health concern to proceed.")
        st.stop()

    with st.status("🤖 Multi-Agent System Initializing...", expanded=True) as status:
        try:
            # --- SAFETY AGENT ---
            st.write("🛡️ Agent 1: Checking clinical safety and scope...")
            time.sleep(0.5) 
            raw_safety = evaluate_safety_and_scope(user_query)
            
            # Fail-safe dictionary enforcement
            safety = raw_safety if isinstance(raw_safety, dict) else {
                "safe": False, 
                "is_general_query": True, 
                "message": "Hello! I am SperAI, your healthcare navigation assistant. How can I help you today?"
            }

            if not safety.get("safe", False):
                # Handle friendly general chat gracefully
                if safety.get("is_general_query", False):
                    status.update(label="💬 Conversational Request", state="complete", expanded=False)
                    st.success("### 🤖 SperAI")
                    st.write(safety.get("message", "Hello! How can I help with your health today?"))
                    st.stop()
                
                # Handle emergencies and actual out-of-scope violations
                else:
                    status.update(label="🚨 Escalated: Safety Protocol Triggered", state="error", expanded=False)
                    st.error("### 🚨 EMERGENCY DETECTED" if safety.get("is_emergency") else "### 🚫 Request Outside Scope")
                    st.info(safety.get("message", "Seek immediate medical attention."))
                    st.stop()

            # --- DEPARTMENT AGENT ---
            st.write("🧠 Agent 2: Querying medical RAG vector database...")
            department = agent_department_recommendation(user_query)

            # --- HOSPITAL AGENT ---
            st.write("🗺️ Agent 3: Locating real-world facilities near your coordinates...")
            hospitals = agent_hospital_navigation(latitude, longitude)

            status.update(label="✅ Agentic Analysis Complete!", state="complete", expanded=False)
            st.markdown("---")

            # -----------------------------
            # 4. Results Dashboard
            # -----------------------------
            col_left, col_right = st.columns([1, 1], gap="large")

            with col_left:
                st.subheader("🛡️ Triage Assessment")
                st.metric("Safety Confidence", f"{safety.get('confidence_score', 0):.0%}")
                st.info(f"**Navigation Action:** {'Allowed' if safety.get('safe') else 'Blocked'}")

            with col_right:
                st.subheader("🧠 Recommended Department")
                st.success(f"### 🏥 {department.get('recommended_department', 'General')}")
                with st.expander("🔍 View AI Rationale"):
                    st.write(department.get('department_rationale', 'N/A'))

            st.markdown("---")
            
            # -----------------------------
            # 5. Facility Directory & Routing
            # -----------------------------
            st.subheader("📍 Nearest Hospitals Directory")
            
            hospital_list = hospitals.get("hospitals", [])
            if hospital_list:
                for i, hospital in enumerate(hospital_list, start=1):
                    with st.container(border=True):
                        h_col1, h_col2 = st.columns([3, 1])
                        with h_col1:
                            st.markdown(f"**{i}. {hospital.get('name', 'Hospital')}**")
                            st.write(f"📏 Distance: **{hospital.get('distance_km', 0)} km**")
                        with h_col2:
                            route_url = hospital.get("route_url", f"https://www.google.com/maps/dir/?api=1&origin={latitude},{longitude}&destination={hospital.get('lat')},{hospital.get('lon')}")
                            st.link_button("🗺️ Get Directions", route_url, use_container_width=True)
            else:
                st.warning("No hospitals found within the immediate radius.")

        except Exception as e:
            status.update(label="❌ Orchestration Error", state="error", expanded=True)
            st.error(f"**Backend Pipeline Error:** {str(e)}")
