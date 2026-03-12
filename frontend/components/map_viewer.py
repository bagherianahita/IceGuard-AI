import streamlit as st
import folium




from streamlit_folium import folium_static

def render_map(detections):
    """
    Nature: Reusable UI Component.
    Aim: Renders an interactive Mapbox/Leaflet map with iceberg markers.
    """
    st.subheader("📍 Geospatial Intelligence View")
    
    # Center map on the Grand Banks / Newfoundland area
    m = folium.Map(location=[47.5, -52.7], zoom_start=6, tiles="CartoDB dark_matter")
    
    for berg in detections:
        color = "red" if berg.get("confidence", 0) > 0.9 else "orange"
        folium.CircleMarker(
            location=[berg["latitude"], berg["longitude"]],
            radius=7,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"ID: {berg['iceberg_id']}<br>Conf: {berg['confidence']:.2%}"
        ).add_to(m)
    
    folium_static(m, width=800, height=500)