from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from sentinelhub import (
    BBox,
    CRS,
    DataCollection,
    MimeType,
    SentinelHubRequest,
    SHConfig,
)

LOGGER = logging.getLogger(__name__)


EVALSCRIPT_S1_IW = """
//VERSION=3
function setup() {
  return {
    input: [{
      bands: ["VV", "VH"],
      units: "SIGMA0_ELLIPSOID"
    }],
    output: {
      id: "default",
      bands: 2,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  return [sample.VV, sample.VH];
}
"""


@dataclass(frozen=True)
class GeographicBBox:
    """Simple WGS84 bounding box.

    Values are given as (min_lon, min_lat, max_lon, max_lat).
    """

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

from sentinelhub import BBox, CRS

# داخل کلاس GeographicBBox یا جایی که bbox ساخته می‌شود:
def to_sentinelhub_bbox(self):
    # ۱. ابتدا bbox را در سیستم مختصات جغرافیایی بسازید
    wgs84_bbox = BBox(
        bbox=(self.min_lon, self.min_lat, self.max_lon, self.max_lat), 
        crs=CRS.WGS84
    )
    # ۲. آن را به سیستم تصویر (Projected) مثل Web Mercator تبدیل کنید
    # این باعث می‌شود واحد رزولوشن شما (مثلاً 40) به درستی "متر" محاسبه شود
    return wgs84_bbox.transform(CRS.POP_WEB)

# Approximate WGS84 bounding box for the Grand Banks of Newfoundland
GRAND_BANKS_BBOX = GeographicBBox(
    min_lon=-57.3037,
    min_lat=42.8530,
    max_lon=-46.8781,
    max_lat=49.0909,
)


class Sentinel1IngestionError(RuntimeError):
    """Domain-specific error raised when Sentinel-1 ingestion fails."""


def _create_sh_config() -> SHConfig:
    """Create a Sentinel Hub configuration instance.

    Expects credentials to be provided via the standard Sentinel Hub configuration
    mechanisms (environment variables, config file, etc.).

    Raises:
        Sentinel1IngestionError: If mandatory Sentinel Hub credentials are missing.
    """
    config = SHConfig()
    if not config.sh_client_id or not config.sh_client_secret:
        LOGGER.error(
            "Sentinel Hub client credentials are not configured. "
            "Set SH_CLIENT_ID and SH_CLIENT_SECRET (or equivalent) before running ingestion."
        )
        raise Sentinel1IngestionError(
            "Sentinel Hub client credentials are missing. "
            "Set SH_CLIENT_ID and SH_CLIENT_SECRET in the environment or configuration."
        )
    return config


def fetch_sentinel1_backscatter(
    bbox: GeographicBBox,
    time_interval: Tuple[str, str],
    resolution_m: int = 40,
    config: Optional[SHConfig] = None,
) -> np.ndarray:
    """Fetch Sentinel-1 IW backscatter (VV, VH) for a given bounding box.

    Args:
        bbox: Geographic bounding box (WGS84).
        time_interval: Start and end date in ISO format, e.g. ("2025-01-01", "2025-01-10").
        resolution_m: Target ground resolution in meters.
        config: Optional Sentinel Hub configuration. If not provided, a default
            configuration is created via `_create_sh_config()`.

    Returns:
        A NumPy array of shape (height, width, 2) with VV and VH backscatter.

    Raises:
        Sentinel1IngestionError: If the request to Sentinel Hub fails.
    """
    sh_config = config or _create_sh_config()
    sh_bbox = bbox.to_sentinelhub_bbox()

    LOGGER.info("Requesting Sentinel-1 IW backscatter for bbox=%s and interval=%s", bbox, time_interval)

    request = SentinelHubRequest(
    evalscript=EVALSCRIPT_S1_IW,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL1_IW,
            time_interval=time_interval,
        )
    ],
    responses=[
        SentinelHubRequest.output_response("default", MimeType.TIFF)
    ],
    bbox=sh_bbox,
    resolution=(resolution_m, resolution_m),
    config=sh_config,
)

    try:
        data_stack: List[np.ndarray] = request.get_data()
    except Exception as exc:  # sentinelhub raises its own exceptions; keep surface generic but logged
        LOGGER.exception("Failed to download Sentinel-1 data from Sentinel Hub.")
        raise Sentinel1IngestionError("Failed to download Sentinel-1 data.") from exc

    if not data_stack:
        message = "No Sentinel-1 data returned for the specified query."
        LOGGER.error(message)
        raise Sentinel1IngestionError(message)

    # We request a single mosaic; grab first element.
    backscatter = data_stack[0]
    if backscatter.ndim != 3 or backscatter.shape[2] != 2:
        message = f"Unexpected backscatter shape: {backscatter.shape!r} (expected HxWx2)."
        LOGGER.error(message)
        raise Sentinel1IngestionError(message)

    LOGGER.info("Successfully fetched Sentinel-1 backscatter: shape=%s", backscatter.shape)
    return backscatter


def normalize_backscatter(backscatter: np.ndarray) -> np.ndarray:
    """Normalize Sentinel-1 backscatter to [0, 1] per band in dB space.

    Args:
        backscatter: Array of shape (height, width, bands) containing **linear**
            sigma0 power values (e.g., as returned by the Sentinel Hub evalscript
            with units="SIGMA0_ELLIPSOID"). This function will convert these
            linear power values to decibels internally before normalization.

    This function:
    - Converts linear sigma0 values to decibels.
    - Uses robust percentile-based scaling (2nd–98th percentile) per band.
    - Clips to [0, 1] for downstream visualization and ML pipelines.
    """
    if backscatter.ndim != 3 or backscatter.shape[2] not in (1, 2):
        raise ValueError(f"Expected backscatter of shape HxWx(1|2), got {backscatter.shape!r}.")

    # Prevent log of zero
    safe_backscatter = np.clip(backscatter, 1e-8, None)
    backscatter_db = 10.0 * np.log10(safe_backscatter)

    normalized = np.empty_like(backscatter_db, dtype=np.float32)

    for band_idx in range(backscatter_db.shape[2]):
        band = backscatter_db[:, :, band_idx]
        lower, upper = np.percentile(band, (2, 98))
        if upper <= lower:
            # Fallback to simple min-max if percentiles are degenerate
            lower, upper = float(band.min()), float(band.max())

        LOGGER.debug(
            "Normalizing band %d with lower=%f dB, upper=%f dB.",
            band_idx,
            lower,
            upper,
        )

        scaled = (band - lower) / (upper - lower + 1e-6)
        normalized[:, :, band_idx] = np.clip(scaled, 0.0, 1.0)

    return normalized


def save_backscatter_as_geotiff(
    normalized_backscatter: np.ndarray,
    bbox: GeographicBBox,
    output_path: Path,
    bands: Iterable[str] = ("VV", "VH"),
) -> Path:
    """Save normalized backscatter to a GeoTIFF file.

    Args:
        normalized_backscatter: Array of shape (height, width, n_bands) with values in [0, 1].
        bbox: Bounding box used to compute the georeferencing transform.
        output_path: Target path for the GeoTIFF.
        bands: Logical band names (for metadata only).

    Returns:
        The path to the written GeoTIFF.

    Raises:
        ValueError: If the input array shape is invalid.
        Sentinel1IngestionError: If writing the GeoTIFF fails.
    """
    if normalized_backscatter.ndim != 3:
        raise ValueError(f"Expected normalized_backscatter of shape HxWxC, got {normalized_backscatter.shape!r}.")

    height, width, n_bands = normalized_backscatter.shape
    transform = from_bounds(
        west=bbox.min_lon,
        south=bbox.min_lat,
        east=bbox.max_lon,
        north=bbox.max_lat,
        width=width,
        height=height,
    )

    output_path = output_path.with_suffix(".tif")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Writing normalized backscatter to %s", output_path)

    try:
        with rasterio.open(
            output_path,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=n_bands,
            dtype=np.float32,
            crs="EPSG:4326",
            transform=transform,
        ) as dataset:
            # Rasterio expects (bands, height, width)
            data_to_write = np.moveaxis(normalized_backscatter, -1, 0)
            dataset.write(data_to_write)
            dataset.descriptions = list(bands)[:n_bands]
    except Exception as exc:
        LOGGER.exception("Failed to write GeoTIFF to %s", output_path)
        raise Sentinel1IngestionError(f"Failed to write GeoTIFF to {output_path}.") from exc

    return output_path


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging for command-line usage.

    This is a convenience for scripts and notebooks; production applications
    should configure logging in their own entrypoints.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )


__all__ = [
    "GeographicBBox",
    "GRAND_BANKS_BBOX",
    "Sentinel1IngestionError",
    "fetch_sentinel1_backscatter",
    "normalize_backscatter",
    "save_backscatter_as_geotiff",
    "configure_logging",
]

