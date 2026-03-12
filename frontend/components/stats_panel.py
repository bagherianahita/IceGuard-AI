import streamlit as st

def render_stats(detections):
    """Aim: Provide a quick high-level count of risk factors."""
    total = len(detections)
    high_conf = len([d for d in detections if d['confidence'] > 0.9])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Targets", total)
    col2.metric("High Confidence", high_conf)
    col3.metric("Critical Risks", "1" if total > 5 else "0")