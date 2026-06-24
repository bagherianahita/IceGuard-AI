import json
from datetime import datetime
from pathlib import Path

import streamlit as st

_DEMO_DIR = Path(__file__).resolve().parents[1] / "data" / "demo"


def _load_demo_file(name: str):
    path = _DEMO_DIR / name
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def init_state():
    """Initialize app state with demo defaults for employer quick-start."""
    if "selected_aoi" not in st.session_state:
        st.session_state.selected_aoi = "Grand Banks, NL"
    if "analysis_date" not in st.session_state:
        st.session_state.analysis_date = datetime.now().date()
    if "detections" not in st.session_state:
        st.session_state.detections = _load_demo_file("detections.json") or []
    if "report" not in st.session_state:
        st.session_state.report = _load_demo_file("report.json")
