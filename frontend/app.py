import streamlit as st
from frontend.state import init_state
from frontend.views import operational_overview, report_builder

init_state()

# Sidebar Navigation
st.sidebar.title("IceGuard AI")
page = st.sidebar.radio("Navigation", ["Overview", "Safety Report"])

# Routing logic
if page == "Overview":
    operational_overview.show_view()
else:
    report_builder.show_view()

# Sidebar Action Button
if st.sidebar.button("🚀 Sync Satellite Data"):
    # Trigger the main.py logic here
    st.session_state.detections = [{"iceberg_id": "IB-01", "latitude": 47.1, "longitude": -52.5, "confidence": 0.95}]
    st.session_state.report = {"risk_level": "High", "summary": "Ice detected.", "recommended_actions": ["Slow down"]}
    st.rerun()