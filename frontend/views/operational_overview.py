import streamlit as st

from frontend.components.map_viewer import render_map
from frontend.components.stats_panel import render_stats


def show_view() -> None:
    """Operational overview with map and detection stats."""
    st.title("Operational Overview")

    aoi = st.session_state.get("selected_aoi", "Grand Banks, NL")
    st.write(f"**AOI:** {aoi}")

    detections = st.session_state.get("detections", [])
    if not detections:
        st.info("Click **Sync Satellite Data** in the sidebar to run the mock SAR pipeline.")
        return

    render_stats(detections)
    render_map(detections)
