import streamlit as st
import folium
from streamlit_folium import folium_static

def render_iceberg_map(lat, lon, detections):
    """
    Nature: Geospatial Visualization Component.
    Aim: Displays detected icebergs on an interactive Leaflet map.
    """
    m = folium.Map(location=[lat, lon], zoom_start=6, tiles="CartoDB dark_matter")
    
    for berg in detections:
        folium.CircleMarker(
            location=[berg["latitude"], berg["longitude"]],
            radius=5,
            color="cyan",
            fill=True,
            popup=f"ID: {berg['iceberg_id']} | Conf: {berg['confidence']:.2f}"
        ).add_to(m)
    
    folium_static(m)