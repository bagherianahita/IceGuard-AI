"""
Detection engine for IceGuard AI.

Responsible for:
- Implementing iceberg detection algorithms and models.
- Managing detection pipelines and post-processing.
- Producing standardized detection outputs for downstream use.
"""
"""
Detection Engine Module: Identifies iceberg candidates from SAR imagery.
"""
from .pipelines import IcebergDetectionPipeline
from .models import IcebergDetectorCNN, CFARDetector
from .postprocessing import cluster_detections

# This is where we might define the "Contract" for what an Iceberg object looks like
from typing import TypedDict, List

class IcebergResult(TypedDict):
    lat: float
    lon: float
    confidence: float
    size_m2: float

__all__ = ["IcebergDetectionPipeline", "IcebergResult"]