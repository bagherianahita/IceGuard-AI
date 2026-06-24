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
        st.info(
            "Demo data is pre-loaded on first visit. Click **Sync Satellite Data** in the sidebar "
            "to re-run the SAR pipeline (mock mode — no API keys required)."
        )
        return

    render_stats(detections)
    render_map(detections)
