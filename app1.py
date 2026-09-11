import streamlit as st

from agents import (
    evaluate_safety_and_scope,
    agent_department_recommendation,
    agent_hospital_navigation,
)
from safety_agent import evaluate_safety_and_scope
from rag_engine import collection, populate_knowledge_base

if collection.count() == 0:
    populate_knowledge_base()
# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="SperAI",
    page_icon="🏥",
    layout="wide"
)

# -----------------------------
# Header
# -----------------------------
st.title("🏥 SperAI")
st.subheader("AI-Powered Healthcare Navigation")

st.write(
    "Describe your health concern and SperAI will help "
    "navigate you to the appropriate healthcare department."
)

st.divider()

# -----------------------------
# Medical disclaimer
# -----------------------------
st.warning(
    "⚠️ SperAI is a healthcare navigation assistant, "
    "not a doctor. It does not diagnose diseases or "
    "prescribe medication. For emergencies, seek "
    "immediate professional medical care."
)

# -----------------------------
# User input
# -----------------------------
st.header("🩺 Describe Your Concern")

user_query = st.text_area(
    "What are you experiencing?",
    placeholder="Example: I have ear pain and reduced hearing...",
    height=150
)

# -----------------------------
# Location
# -----------------------------
st.header("📍 Your Location")

col1, col2 = st.columns(2)

with col1:
    latitude = st.number_input(
        "Latitude",
        value=12.9716
    )

with col2:
    longitude = st.number_input(
        "Longitude",
        value=77.5946
    )

# -----------------------------
# Main button
# -----------------------------
if st.button("🔎 Get Healthcare Guidance", type="primary"):

    if not user_query.strip():
        st.error("Please describe your health concern.")
        st.stop()

    # =========================
    # SAFETY AGENT
    # =========================

    with st.status(
        "Running SperAI agents...",
        expanded=True
    ) as status:

        st.write("🛡️ Checking safety and scope...")

        safety = evaluate_safety_and_scope(user_query)

        # Emergency / unsafe query
        if not safety["safe"]:

            status.update(
                label="Safety check completed",
                state="error"
            )

            if safety["is_emergency"]:

                st.error("🚨 EMERGENCY DETECTED")

                st.markdown(
                    """
                    ### Please seek immediate medical attention.

                    Your symptoms may indicate a potential emergency.

                    **Call 112 or go to the nearest Emergency Department immediately.**

                    Do not rely on this application for emergency medical care.
                    """
                )

            else:

                st.error("🚫 Request outside SperAI's scope")

                st.info(safety["message"])

            st.stop()

        # =========================
        # DEPARTMENT AGENT
        # =========================

        st.write("🧠 Finding appropriate department...")

        department = agent_department_recommendation(
            user_query
        )

        # =========================
        # HOSPITAL AGENT
        # =========================

        st.write("🏥 Finding nearby hospitals...")

        hospitals = agent_hospital_navigation(
            latitude,
            longitude
        )

        status.update(
            label="All agents completed",
            state="complete"
        )

    # =========================
    # RESULTS
    # =========================

    st.divider()

    st.header("📋 Healthcare Navigation Result")

    # Safety
    st.subheader("🛡️ Safety Assessment")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Confidence",
            f"{safety['confidence_score']:.0%}"
        )

    with c2:
        st.metric(
            "Emergency",
            "Yes" if safety["is_emergency"] else "No"
        )

    with c3:
        st.metric(
            "Navigation",
            "Allowed" if safety["safe"] else "Blocked"
        )

    # Department
    st.subheader("🏥 Recommended Department")

    st.success(
        department["recommended_department"]
    )

    st.write(
        department["department_rationale"]
    )

    # Evidence
    st.subheader("📚 Clinical Evidence")

    st.info(
        department["retrieved_evidence"]
    )

    # Hospitals
    st.subheader("📍 Nearby Hospitals")

    hospital_list = hospitals["hospitals"]

    if hospital_list:

        for i, hospital in enumerate(
            hospital_list,
            start=1
        ):

            st.markdown(
                f"### {i}. {hospital.get('name', 'Hospital')}"
            )

            if hospital.get("address"):
                st.write(
                    f"📍 {hospital['address']}"
                )

            st.write(
                f"📏 Distance: {hospital['distance_km']} km"
)

            if hospital.get("route_url"):
                st.link_button(
                    "🗺️ Get Directions",
                    hospital["route_url"]
    )

            st.caption(
                hospital.get("accessibility_note", "")
)

            st.divider()

    else:

        st.info(
            "No nearby hospitals were found."
        )

# -----------------------------
# Footer
# -----------------------------
st.caption(
    "SperAI • Healthcare Navigation AI • "
    "For navigation support only."
)