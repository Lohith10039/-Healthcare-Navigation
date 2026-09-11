import streamlit as st

st.set_page_config(
    page_title="Healthcare Navigation",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Healthcare Navigation")
st.subheader("AI-Powered Clinical Navigation")

st.success("Application is running!")

st.write("""
This system helps users understand their healthcare needs,
assess safety/urgency, and navigate to appropriate healthcare facilities.
""")

st.divider()

symptoms = st.text_area(
    "Describe your symptoms",
    placeholder="Example: I have fever and severe headache..."
)

if st.button("Analyze"):
    if symptoms.strip():
        st.info("Clinical navigation agents are processing your request...")
        
        # Connect your existing agents here later
        st.write("### Initial Assessment")
        st.write("Please consult a qualified healthcare professional for medical decisions.")
        
    else:
        st.warning("Please describe your symptoms first.")
