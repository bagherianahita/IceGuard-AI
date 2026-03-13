"""
Data ingestion module for IceGuard AI.

Responsible for:
- Interfacing with Sentinel Hub and other data providers.
- Downloading and caching Sentinel-1 SAR imagery.
- Pre-processing scenes into analysis-ready tiles.
"""

from .sentinel1_ingestion import (
    GeographicBBox,
    GRAND_BANKS_BBOX,
    Sentinel1IngestionError,
    fetch_sentinel1_backscatter,
    normalize_backscatter,
    save_backscatter_as_geotiff,
    configure_logging,
)
from .preprocessing import (
    apply_speckle_filter,
    land_sea_mask,
    calibrate_radiometry,
    process_sar_image,
)
from .catalog import SceneCatalog

__all__ = [
    "GeographicBBox",
    "GRAND_BANKS_BBOX",
    "Sentinel1IngestionError",
    "fetch_sentinel1_backscatter",
    "normalize_backscatter",
    "save_backscatter_as_geotiff",
    "configure_logging",
    "apply_speckle_filter",
    "land_sea_mask",
    "calibrate_radiometry",
    "process_sar_image",
    "SceneCatalog",
]