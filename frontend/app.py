import streamlit as st

from frontend.state import init_state
from frontend.views import operational_overview, report_builder
from main import run_pipeline_for_aoi


init_state()

# Sidebar Navigation
st.sidebar.title("IceGuard AI")
page = st.sidebar.radio("Navigation", ["Overview", "Safety Report"])

# Routing logic
if page == "Overview":
    operational_overview.show_view()
else:
    report_builder.show_view()


def _normalize_detections_for_ui(raw_detections):
    """Map internal detection dictionaries to the UI-friendly schema."""
    normalized = []
    for idx, det in enumerate(raw_detections):
        lat = det.get("lat", det.get("latitude"))
        lon = det.get("lon", det.get("longitude"))
        if lat is None or lon is None:
            continue

        iceberg_id = det.get("iceberg_id") or f"ice_{idx:03d}"
        size_sq_m = det.get("size_m2", det.get("size_sq_m"))

        normalized.append(
            {
                "iceberg_id": iceberg_id,
                "latitude": float(lat),
                "longitude": float(lon),
                "confidence": float(det.get("confidence", 0.0)),
                "size_sq_m": float(size_sq_m) if size_sq_m is not None else None,
            }
        )
    return normalized


# Sidebar Action Button
if st.sidebar.button("🚀 Sync Satellite Data"):
    with st.spinner("Processing SAR Data & Generating AI Safety Report..."):
        try:
            result = run_pipeline_for_aoi()
            raw_detections = result.get("detections", [])
            st.session_state.detections = _normalize_detections_for_ui(raw_detections)
            st.session_state.report = result.get("report")
            st.success("Pipeline completed successfully.")
        except Exception as exc:
            st.error(f"Pipeline failed: {exc}")
        st.rerun()
