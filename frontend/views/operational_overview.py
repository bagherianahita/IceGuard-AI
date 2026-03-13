import streamlit as st


def show_view() -> None:
    """Display a high-level operational overview for IceGuard AI."""
    st.title("Operational Overview")

    st.subheader("Area of Interest")
    aoi = st.session_state.get("selected_aoi", "Grand Banks, NL")
    analysis_date = st.session_state.get("analysis_date", None)

    st.write(f"**AOI**: {aoi}")
    if analysis_date is not None:
        st.write(f"**Analysis Date**: {analysis_date}")

    st.subheader("Latest Detections")
    detections = st.session_state.get("detections", [])
    if not detections:
        st.info("No iceberg detections available yet. Use 'Sync Satellite Data' to ingest and analyze SAR scenes.")
    else:
        st.write(f"Total detections: **{len(detections)}**")
        st.json(detections)

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