import streamlit as st
from datetime import datetime

def init_state():
    """Initializes the global application state."""
    if "selected_aoi" not in st.session_state:
        st.session_state.selected_aoi = "Grand Banks, NL"
    if "analysis_date" not in st.session_state:
        st.session_state.analysis_date = datetime.now().date()
    if "detections" not in st.session_state:
        st.session_state.detections = []
    if "report" not in st.session_state:
        st.session_state.report = None