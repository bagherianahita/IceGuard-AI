from __future__ import annotations

import json
import logging
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np
from dotenv import load_dotenv

from data_ingestion.sentinel1_ingestion import (
    GRAND_BANKS_BBOX,
    GeographicBBox,
    Sentinel1IngestionError,
    fetch_sentinel1_backscatter,
    normalize_backscatter,
)
from detection_engine import IcebergResult
from detection_engine.postprocessing import (
    detections_to_geojson,
    write_detections_parquet,
)
from detection_engine.rule_based_detector import detect_icebergs_from_backscatter
from llm_reporting.maritime_safety_advisory import (
    MaritimeSafetyAdvisoryError,
    generate_maritime_safety_advisory,
)

LOGGER = logging.getLogger(__name__)


LLM_CACHE: Dict[str, Dict[str, Any]] = {}


def _configure_logging() -> None:
    """Configure logging for command-line execution."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )


def _load_environment() -> None:
    """Load environment variables from a .env file if present."""
    load_dotenv()


def _has_sentinelhub_credentials() -> bool:
    """Determine whether Sentinel Hub OAuth credentials are available."""
    client_id = os.getenv("SH_CLIENT_ID")
    client_secret = os.getenv("SH_CLIENT_SECRET")
    return bool(client_id and client_secret)


def _has_openai_api_key() -> bool:
    """Check whether an OpenAI API key is available."""
    return bool(os.getenv("OPENAI_API_KEY"))


def _run_llm_with_cache(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Run the LLM advisory chain with a simple in-memory cache.

    Uses a deterministic JSON-serialized representation of the payload as the cache key.
    """
    key = json.dumps(payload, sort_keys=True)

    if key in LLM_CACHE:
        LOGGER.info("Using cached maritime safety advisory for this payload.")
        return LLM_CACHE[key]

    advisory = generate_maritime_safety_advisory(payload)
    LLM_CACHE[key] = advisory
    return advisory


def run_pipeline_for_aoi(
    bbox: GeographicBBox = GRAND_BANKS_BBOX,
    time_interval: Optional[Tuple[str, str]] = None,
    use_live_if_possible: bool = True,
    export_geojson_path: Optional[Path] = None,
    export_parquet_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Run the end-to-end IceGuard AI pipeline for a given AOI.

    This function ties together:
    - Sentinel-1 data ingestion.
    - A rule-based iceberg detection stub.
    - Maritime safety advisory generation via LLM.

    Returns:
        A dictionary with keys:
            - "bbox": the GeographicBBox used.
            - "time_interval": the time interval used.
            - "used_live_data": bool indicating Sentinel Hub usage.
            - "detections": list of iceberg detection objects.
            - "report": structured maritime safety advisory JSON.
    """
    if time_interval is None:
        today = date.today()
        start = today - timedelta(days=7)
        time_interval = (start.isoformat(), today.isoformat())

    LOGGER.info("Running IceGuard AI pipeline for bbox=%s and interval=%s", bbox, time_interval)

    use_live = use_live_if_possible and _has_sentinelhub_credentials()

    backscatter = None
    used_live_data = False

    if use_live:
        LOGGER.info("Sentinel Hub credentials detected; attempting live Sentinel-1 ingestion.")
        try:
            backscatter = fetch_sentinel1_backscatter(
                bbox=bbox,
                time_interval=time_interval,
            )
            used_live_data = True
        except Sentinel1IngestionError as exc:
            LOGGER.warning(
                "Live Sentinel-1 ingestion failed (%s). Falling back to mock backscatter for demo.",
                exc,
            )

    if backscatter is None:
        LOGGER.info("Using mock Sentinel-1 backscatter for demo mode.")
        height, width, bands = 256, 256, 2
        mock = 1e-6 * (0.5 + 0.5 * (os.urandom(height * width * bands)[0] / 255.0))
        # Simple synthetic pattern with a bright diagonal region
        backscatter = 1e-6 * np.ones((height, width, bands), dtype=float)
        for i in range(64, 192, 8):
            for j in range(64, 192, 8):
                backscatter[i, j, :] = 1e-3

    normalized = normalize_backscatter(backscatter)

    detections: List[IcebergResult] = detect_icebergs_from_backscatter(
        normalized_backscatter=normalized,
        bbox=bbox,
        max_candidates=24,
    )

    LOGGER.info("Rule-based detector produced %d iceberg candidates.", len(detections))

    # Optional exports to GeoJSON / Parquet to satisfy documented data contracts.
    if detections:
        if export_geojson_path is not None:
            geojson = detections_to_geojson(detections)
            export_geojson_path.parent.mkdir(parents=True, exist_ok=True)
            export_geojson_path.write_text(json.dumps(geojson, indent=2))

        if export_parquet_path is not None:
            write_detections_parquet(detections, export_parquet_path)

    if not detections:
        LOGGER.warning(
            "No iceberg candidates detected in the AOI. Skipping LLM advisory generation."
        )
        report: Optional[Dict[str, Any]] = None
    else:
        iceberg_coordinates = [
            {"lat": det["lat"], "lon": det["lon"]} for det in detections
        ]
        size_estimate = (
            f"Approximately {len(detections)} iceberg candidates detected across the AOI."
        )
        weather_description = (
            "Typical North Atlantic spring conditions with patchy fog, "
            "moderate swell, and near-freezing air temperatures."
        )

        if not _has_openai_api_key():
            LOGGER.warning(
                "OPENAI_API_KEY is not set. Skipping LLM advisory generation for this run."
            )
            report = None
        else:
            payload = {
                "iceberg_coordinates": iceberg_coordinates,
                "size_estimate": size_estimate,
                "current_weather_conditions": weather_description,
            }

            try:
                report = _run_llm_with_cache(payload)
            except MaritimeSafetyAdvisoryError:
                LOGGER.exception("Failed to generate maritime safety advisory.")
                report = None

    return {
        "bbox": bbox,
        "time_interval": time_interval,
        "used_live_data": used_live_data,
        "detections": detections,
        "report": report,
    }


def main() -> None:
    """CLI entrypoint for running a single AOI analysis."""
    _configure_logging()
    _load_environment()

    output_dir = Path("data/exports")
    result = run_pipeline_for_aoi(
        bbox=GRAND_BANKS_BBOX,
        export_geojson_path=output_dir / "iceberg_detections.geojson",
        export_parquet_path=output_dir / "iceberg_detections.parquet",
    )

    used_live = result["used_live_data"]
    detections: List[Mapping[str, Any]] = result["detections"]
    report = result["report"]

    if used_live:
        print("[Success] Sentinel-1 data downloaded from Sentinel Hub.")
    else:
        print("[Info] Running in MOCK mode (no Sentinel Hub credentials or ingestion failure).")

    print(f"[Success] {len(detections)} iceberg candidates detected.")

    if report is not None:
        print("[Success] AI Safety Report Generated.")
        print(json.dumps(report, indent=2))
    else:
        print("[Warning] No AI safety report generated (no detections or LLM failure).")


if __name__ == "__main__":
    main()

