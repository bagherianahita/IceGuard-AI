import numpy as np
import rasterio
from rasterio.enums import Resampling
from scipy.ndimage import uniform_filter

def apply_speckle_filter(img: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Nature: Noise Reduction.
    Aim: Removes the 'salt and pepper' noise inherent in SAR (Synthetic Aperture Radar).
    Application: Uses a Lee or Mean filter to smooth water surfaces for easier iceberg detection.
    """
    # Simple Mean Filter as a baseline for the prototype
    mean = uniform_filter(img, size=window_size)
    return mean

def land_sea_mask(img: np.ndarray, mask_path: str) -> np.ndarray:
    """
    Aim: Zero-out land pixels so the AI doesn't think a building or a rock is an iceberg.
    """
    with rasterio.open(mask_path) as mask_file:
        mask = mask_file.read(1, out_shape=img.shape, resampling=Resampling.nearest)
    
    # Where mask is 1 (land), set image to 0
    img[mask == 1] = 0
    return img

def calibrate_radiometry(raw_data: np.ndarray) -> np.ndarray:
    """
    Aim: Convert raw Digital Numbers (DN) to Sigma Nought (backscatter coefficient).
    Application: Essential for scientific consistency across different dates.
    """
    # Placeholder for SAR calibration math (Sigma0 = DN^2 / Ao)
    calibrated = np.where(raw_data > 0, 10 * np.log10(raw_data**2 + 1e-10), -30)
    return calibrated

def process_sar_image(input_path: str, output_path: str):
    """
    The Orchestrator: Combines all steps into a single pipeline.
    """
    with rasterio.open(input_path) as src:
        data = src.read(1)
        
        # 1. Calibrate
        data = calibrate_radiometry(data)
        # 2. Filter Noise
        data = apply_speckle_filter(data)
        
        # Save processed file
        profile = src.profile
        profile.update(dtype=rasterio.float32, count=1)
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(data.astype(rasterio.float32), 1)