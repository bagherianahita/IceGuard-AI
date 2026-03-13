from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import numpy as np
from scipy import ndimage


def cluster_detections(mask: np.ndarray) -> List[Dict[str, Any]]:
    """
    Aim: Group individual bright pixels into single 'Iceberg' objects.
    Nature: Segmentation & Clustering.
    Application: Prevents one large iceberg from being counted as 50 separate small ones.
    """
    labeled_array, num_features = ndimage.label(mask)
    objects = ndimage.find_objects(labeled_array)

    icebergs: List[Dict[str, Any]] = []
    for i, obj in enumerate(objects):
        # Calculate size (area)
        size = float(np.sum(mask[obj]))

        # Calculate centroid (center point) in pixel space
        center_y = (obj[0].start + obj[0].stop) / 2.0
        center_x = (obj[1].start + obj[1].stop) / 2.0

        icebergs.append(
            {
                "internal_id": f"ice_{i:03d}",
                "pixel_coords": (center_x, center_y),
                "area_pixels": size,
                "confidence": 0.85,  # Placeholder confidence
            }
        )

    return icebergs


def detections_to_geojson(
    detections: Sequence[Mapping[str, Any]],
    *,
    collection_id: str | None = None,
    extra_properties: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Convert a sequence of iceberg detections into a GeoJSON FeatureCollection.

    Each detection is expected to expose:
    - Either ("lat", "lon") or ("latitude", "longitude").
    - Optional "iceberg_id", "confidence", "size_m2", "size_sq_m".
    """
    features: List[Dict[str, Any]] = []
    base_props = dict(extra_properties or {})

    for idx, det in enumerate(detections):
        lat = det.get("lat", det.get("latitude"))
        lon = det.get("lon", det.get("longitude"))
        if lat is None or lon is None:
            # Skip malformed detections rather than failing the entire export.
            continue

        iceberg_id = det.get("iceberg_id") or f"ice_{idx:03d}"
        size_sq_m = det.get("size_m2", det.get("size_sq_m"))

        properties = {
            **base_props,
            "iceberg_id": iceberg_id,
            "confidence": float(det.get("confidence", 0.0)),
        }
        if size_sq_m is not None:
            properties["size_sq_m"] = float(size_sq_m)

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon), float(lat)],
            },
            "properties": properties,
        }
        features.append(feature)

    collection: Dict[str, Any] = {
        "type": "FeatureCollection",
        "features": features,
    }
    if collection_id is not None:
        collection["id"] = collection_id

    return collection


def detections_to_parquet_dataframe(
    detections: Sequence[Mapping[str, Any]],
):
    """
    Convert detections to a pandas DataFrame suitable for Parquet export.

    Columns:
    - iceberg_id (str)
    - lat (float)
    - lon (float)
    - confidence (float)
    - size_m2 (float)
    """
    import pandas as pd

    rows: List[Dict[str, Any]] = []
    for idx, det in enumerate(detections):
        lat = det.get("lat", det.get("latitude"))
        lon = det.get("lon", det.get("longitude"))
        if lat is None or lon is None:
            continue

        iceberg_id = det.get("iceberg_id") or f"ice_{idx:03d}"
        size_m2 = det.get("size_m2", det.get("size_sq_m"))

        rows.append(
            {
                "iceberg_id": iceberg_id,
                "lat": float(lat),
                "lon": float(lon),
                "confidence": float(det.get("confidence", 0.0)),
                "size_m2": float(size_m2) if size_m2 is not None else None,
            }
        )

    df = pd.DataFrame(rows)
    return df


def write_detections_parquet(
    detections: Sequence[Mapping[str, Any]],
    output_path: str | Path,
) -> Path:
    """
    Convenience helper: write iceberg detections directly to a Parquet file.
    """
    from pathlib import Path as _Path

    df = detections_to_parquet_dataframe(detections)
    path = _Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


__all__ = [
    "cluster_detections",
    "detections_to_geojson",
    "detections_to_parquet_dataframe",
    "write_detections_parquet",
]
