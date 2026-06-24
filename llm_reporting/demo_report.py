"""Deterministic demo report when OPENAI_API_KEY is not set."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


def generate_demo_maritime_report(
    iceberg_coordinates: List[Mapping[str, float]],
    size_estimate: str,
    current_weather_conditions: str,
) -> Dict[str, Any]:
    count = len(iceberg_coordinates)
    risk = "CRITICAL" if count >= 8 else "HIGH" if count >= 4 else "MEDIUM" if count >= 1 else "LOW"
    return {
        "risk_level": risk,
        "narrative_summary": (
            f"Demo advisory: {count} iceberg candidate(s) detected near the Grand Banks. "
            f"{size_estimate} Conditions: {current_weather_conditions} "
            "Reduce speed and post additional lookouts in reduced visibility."
        ),
        "recommended_actions": [
            "Reduce vessel speed to minimum safe maneuvering speed in the AOI.",
            "Post additional ice watch on the bridge wings.",
            "Notify Marine Communications and Traffic Services (MCTS) of iceberg sightings.",
            "Consider routing 20–30 NM south of the primary detection cluster.",
        ],
        "assumptions_and_limitations": [
            "Demo mode — no live LLM. Based on rule-based SAR detections only.",
            "Coordinates are used verbatim from the detection engine output.",
        ],
        "coordinates_used_verbatim": [
            {"lat": float(c["lat"]), "lon": float(c["lon"])} for c in iceberg_coordinates[:5]
        ],
    }
