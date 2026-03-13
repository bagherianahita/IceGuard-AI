from __future__ import annotations

from typing import List

import numpy as np

from data_ingestion.sentinel1_ingestion import GeographicBBox
from detection_engine import IcebergResult


def detect_icebergs_from_backscatter(
    normalized_backscatter: np.ndarray,
    bbox: GeographicBBox,
    threshold: float = 0.6,
    max_candidates: int = 24,
) -> List[IcebergResult]:
    """Very simple rule-based detector to generate iceberg candidates.

    This stub operates on normalized backscatter in [0, 1]:
    - Uses a single-band threshold to mark "bright" pixels.
    - Subsamples at most `max_candidates` pixels to keep result size manageable.
    - Converts pixel indices to geographic coordinates using the provided bbox.

    Args:
        normalized_backscatter: Array of shape (height, width, bands) in [0, 1].
        bbox: Geographic bounding box corresponding to the raster.
        threshold: Backscatter threshold in normalized units to flag candidates.
        max_candidates: Maximum number of iceberg candidates to return.

    Returns:
        A list of dictionaries, each containing at least:
            - "lat": latitude in degrees.
            - "lon": longitude in degrees.
            - "confidence": simple score proportional to the backscatter.
            - "size_m2": placeholder surface area estimate.
    """
    if normalized_backscatter.ndim != 3:
        raise ValueError("Expected normalized_backscatter of shape (H, W, C).")

    height, width, bands = normalized_backscatter.shape
    if bands < 1:
        raise ValueError("Expected at least one band in normalized_backscatter.")

    # Use the first band (e.g., VV) for a simple thresholding.
    band = normalized_backscatter[:, :, 0]

    mask = band >= threshold
    candidate_indices = np.argwhere(mask)

    if candidate_indices.size == 0:
        return []

    # Subsample uniformly along the candidate list.
    step = max(1, candidate_indices.shape[0] // max_candidates)
    sampled_indices = candidate_indices[::step][:max_candidates]

    lon_span = bbox.max_lon - bbox.min_lon
    lat_span = bbox.max_lat - bbox.min_lat

    detections: List[IcebergResult] = []
    for idx, (i, j) in enumerate(sampled_indices):
        center_lon = bbox.min_lon + (j + 0.5) * lon_span / float(width)
        center_lat = bbox.min_lat + (i + 0.5) * lat_span / float(height)
        confidence = float(band[i, j])

        detections.append(
            IcebergResult(
                iceberg_id=f"ice_{idx:03d}",
                lat=center_lat,
                lon=center_lon,
                confidence=confidence,
                size_m2=5_000.0,  # placeholder area until a proper size model is implemented
            )
        )

    return detections


__all__ = ["detect_icebergs_from_backscatter"]

