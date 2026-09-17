import streamlit as st
import time
from orchestrator import compiled_graph

# 1. Page Configuration (Wide Layout)
st.set_page_config(
    page_title="Nexus | AI Healthcare Navigator", 
    page_icon="⚕️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Custom CSS for a Premium Look
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
        margin-bottom: 40px;
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

# 3. Header Section
st.markdown('<h1 class="main-title">⚕️ AI Health Navigator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Autonomous Multi-Agent Triage, RAG Routing, & Live Facility Mapping</p>', unsafe_allow_html=True)

# 4. User Input Area
with st.container(border=True):
    user_query = st.text_area(
        "Describe your symptoms or medical concern in detail:",
        placeholder="e.g., I fell down the stairs, and now I have severe swelling and sharp pain in my right wrist...",
        height=100
    )

    analyze_button = st.button("🚀 Run Multi-Agent Analysis", type="primary", use_container_width=True)

# 5. Execution Logic & Dynamic UI
if analyze_button:
    if not user_query.strip():
        st.warning("⚠️ Please enter your symptoms to proceed.")
    else:
        # DYNAMIC LOADER: Shows the agents working step-by-step
        with st.status("🤖 Multi-Agent System Initializing...", expanded=True) as status:
            try:
                st.write("🛡️ Agent 1: Running clinical safety protocols...")
                time.sleep(0.5) 
                
                st.write("🧠 Agent 2: Querying medical RAG vector database...")
                time.sleep(0.5)
                
                st.write("🗺️ Agent 3: Locating real-world healthcare facilities...")
                
                # Execute Backend Orchestrator
                initial_state = {
                    "user_query": user_query,
                    "safety_result": {},
                    "department_result": {},
                    "hospitals": [],
                    "final_output": ""
                }
                
                result = compiled_graph.invoke(initial_state)
                safety = result.get("safety_result", {})
                score = safety.get('confidence_score', 0.0)
                is_safe = safety.get("safe_to_navigate", True) and score >= 0.70
                
                status.update(label="✅ Agentic Analysis Complete!", state="complete", expanded=False)
                
                st.markdown("---")
                
                # 6. Result Dashboard (Dual Column Layout)
                col1, col2 = st.columns([1, 1], gap="large")
                
                # LEFT COLUMN: Safety & Triage
                with col1:
                    st.subheader("🛡️ Safety & Triage Assessment")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Safety Confidence", f"{score * 100:.1f}%")
                    c2.metric("Triage Status", "✅ CLEAR" if is_safe else "🚨 ESCALATED")
                    
                    st.info(f"**Clinical Reasoning:**\n{safety.get('clinical_reasoning', 'No reasoning provided.')}")
                    
                    if not is_safe:
                        st.error(f"**🚨 EMERGENCY PROTOCOL ACTIVATED:**\n{safety.get('escalation_message', 'Immediate medical attention required. Please visit the nearest ER.')}")

                # RIGHT COLUMN: Department Routing
                with col2:
                    if is_safe:
                        st.subheader("🧠 Recommended Department")
                        dept = result.get("department_result", {})
                        dept_name = dept.get('recommended_department', 'General Medicine')
                        
                        st.success(f"### 🏥 {dept_name}")
                        with st.expander("🔍 View AI Rationale & RAG Evidence"):
                            st.write(f"**Rationale:** {dept.get('department_rationale', 'Based on clinical guidelines.')}")
                            st.write(f"**Source Evidence:** {dept.get('retrieved_evidence', 'N/A')}")
                    else:
                        st.subheader("🧠 Recommended Action")
                        st.error("### 🚑 EMERGENCY ROOM")
                        st.write("Standard department routing suspended due to high-risk symptoms.")

                st.markdown("---")
                
                # 7. Maps & Final Synthesis
                col3, col4 = st.columns([1, 1], gap="large")
                
                with col3:
                    st.subheader("🗺️ Live Facility Mapping")
                    if is_safe:
                        hospitals = result.get("hospitals", [])
                        if hospitals:
                            for h in hospitals:
                                with st.container(border=True):
                                    st.markdown(f"**🏥 {h.get('name', 'Hospital')}**")
                                    st.caption(f"📍 Distance: {h.get('distance_km', 0)} km | 🚗 Est. Travel: {h.get('travel_time_min', 'N/A')} mins")
                        else:
                            st.warning("No facilities found in the immediate vicinity.")
                    else:
                        st.error("Facility mapping disabled. Dispatching emergency protocols.")
                        
                with col4:
                    st.subheader("📝 Final AI Synthesis")
                    st.info(result.get("final_output", "No synthesis provided."))
                
            except Exception as e:
                # Failsafe to show errors beautifully on screen
                status.update(label="❌ Orchestration Error", state="error", expanded=True)
                st.error(f"**Backend Pipeline Error:** {str(e)}")
                st.caption("Please check your terminal logs or API key configurations.")
              
