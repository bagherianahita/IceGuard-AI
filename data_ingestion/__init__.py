"""
Data ingestion module for IceGuard AI.

Responsible for:
- Interfacing with Sentinel Hub and other data providers.
- Downloading and caching Sentinel-1 SAR imagery.
- Pre-processing scenes into analysis-ready tiles.
"""
"""
Data Ingestion Module: Responsible for Sentinel-1 SAR acquisition and preprocessing.
"""
from .sentinel_client import SentinelClient
from .preprocessing import process_sar_image, apply_speckle_filter
from .catalog import SceneCatalog

# We define what is available when someone types 'from data_ingestion import *'
__all__ = [
    "SentinelClient",
    "process_sar_image",
    "apply_speckle_filter",
    "SceneCatalog"
]