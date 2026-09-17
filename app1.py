import streamlit as st
import time

# Cleaned up imports (removed duplicates)
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
st.set_page_config(
    page_title="SperAI | Navigation",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 1.2em;
        margin-bottom: 30px;
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

# -----------------------------
# 2. Premium Header
# -----------------------------
st.markdown('<h1 class="main-title">⚕️ SperAI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI-Powered Healthcare Navigation</p>', unsafe_allow_html=True)

st.warning(
    "⚠️ **Medical Disclaimer:** SperAI is a healthcare navigation assistant, not a doctor. "
    "It does not diagnose diseases or prescribe medication. For emergencies, seek immediate professional medical care."
)

# -----------------------------
# 3. User Input Container
# -----------------------------
with st.container(border=True):
    st.subheader("🩺 Describe Your Concern")
    user_query = st.text_area(
        "What are you experiencing?",
        placeholder="Example: I have ear pain and reduced hearing...",
        height=100
    )

    st.subheader("📍 Your Location")
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input("Latitude", value=12.9716, format="%.4f")
    with col2:
        longitude = st.number_input("Longitude", value=77.5946, format="%.4f")

    analyze_button = st.button("🚀 Run SperAI Navigation", type="primary", use_container_width=True)

# -----------------------------
# 4. Agent Execution & Dynamic UI
# -----------------------------
if analyze_button:
    if not user_query.strip():
        st.warning("⚠️ Please describe your health concern to proceed.")
        st.stop()

    with st.status("🤖 Multi-Agent System Initializing...", expanded=True) as status:
        try:
            # --- SAFETY AGENT ---
            st.write("🛡️ Agent 1: Checking clinical safety and scope...")
            time.sleep(0.5) # Slight pause for visual effect
            safety = evaluate_safety_and_scope(user_query)

            if not safety.get("safe", False):
                status.update(label="🚨 Escalated: Safety Protocol Triggered", state="error", expanded=False)
                if safety.get("is_emergency", False):
                    st.error("### 🚨 EMERGENCY DETECTED")
                    st.markdown(
                        "**Your symptoms may indicate a potential emergency.**\n\n"
                        "Call 112 or go to the nearest Emergency Department immediately. "
                        "Do not rely on this application for emergency medical care."
                    )
                else:
                    st.error("### 🚫 Request Outside SperAI's Scope")
                    st.info(safety.get("message", "We cannot process this request safely."))
                st.stop()

            # --- DEPARTMENT AGENT ---
            st.write("🧠 Agent 2: Querying medical RAG vector database...")
            department = agent_department_recommendation(user_query)

            # --- HOSPITAL AGENT ---
            st.write("🗺️ Agent 3: Locating real-world healthcare facilities...")
            hospitals = agent_hospital_navigation(latitude, longitude)

            status.update(label="✅ Agentic Analysis Complete!", state="complete", expanded=False)
            
            st.markdown("---")

            # -----------------------------
            # 5. Dual-Column Dashboard
            # -----------------------------
            col_left, col_right = st.columns([1, 1], gap="large")

            # LEFT: Safety & Triage
            with col_left:
                st.subheader("🛡️ Safety & Triage Assessment")
                c1, c2 = st.columns(2)
                c1.metric("Safety Confidence", f"{safety.get('confidence_score', 0):.0%}")
                c2.metric("Emergency Status", "CLEAR")
                st.info(f"**Navigation Action:** {'Allowed' if safety.get('safe') else 'Blocked'}")

            # RIGHT: Department
            with col_right:
                st.subheader("🧠 Recommended Department")
                st.success(f"### 🏥 {department.get('recommended_department', 'Department not found')}")
                
                with st.expander("🔍 View AI Rationale & RAG Evidence"):
                    st.write(f"**Rationale:** {department.get('department_rationale', 'N/A')}")
                    st.markdown("**Clinical Evidence:**")
                    st.info(department.get('retrieved_evidence', 'N/A'))

            st.markdown("---")

            # -----------------------------
            # 6. Facility Mapping Results
            # -----------------------------
            st.subheader("📍 Nearby Facilities")
            
            hospital_list = hospitals.get("hospitals", [])
            
            if hospital_list:
                for i, hospital in enumerate(hospital_list, start=1):
                    with st.container(border=True):
                        h_col1, h_col2 = st.columns([3, 1])
                        
                        with h_col1:
                            st.markdown(f"**{i}. {hospital.get('name', 'Hospital')}**")
                            if hospital.get("address"):
                                st.caption(f"📍 {hospital['address']}")
                            st.write(f"📏 Distance: **{hospital.get('distance_km', 0)} km**")
                            if hospital.get("accessibility_note"):
                                st.caption(hospital["accessibility_note"])
                                
                        with h_col2:
                            if hospital.get("route_url"):
                                st.link_button("🗺️ Get Directions", hospital["route_url"], use_container_width=True)
            else:
                st.info("No nearby hospitals were found matching the criteria.")

        except Exception as e:
            status.update(label="❌ Orchestration Error", state="error", expanded=True)
            st.error(f"**Backend Pipeline Error:** {str(e)}")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("SperAI • Healthcare Navigation AI • For navigation support only.")
