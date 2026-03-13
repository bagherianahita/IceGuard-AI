"""
Detection engine for IceGuard AI.

Responsible for:
- Implementing iceberg detection algorithms and models.
- Managing detection pipelines and post-processing.
- Producing standardized detection outputs for downstream use.
"""

from typing import TypedDict


class IcebergResult(TypedDict):
    """Canonical in-memory representation of a single iceberg detection."""

    iceberg_id: str
    lat: float
    lon: float
    confidence: float
    size_m2: float


__all__ = ["IcebergResult"]