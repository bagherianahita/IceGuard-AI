import streamlit as st
from frontend.components.map_viewer import render_iceberg_map


from frontend.components.map_viewer import render_map
from frontend.components.stats_panel import render_stats

def show_view():
    """
    Nature: Page View.
    Aim: Orchestrates components to show the current operational status.
    """
    st.title("🧊 Operational Overview")
    
    # 1. Use the Stats Component
    if st.session_state.detections:
        render_stats(st.session_state.detections)
        
        # 2. Use the Map Component
        render_map(st.session_state.detections)
    else:
        st.info("Please trigger the 'Run Pipeline' button in the sidebar to fetch data.")