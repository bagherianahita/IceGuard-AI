import pytest
import numpy as np
from pydantic import ValidationError
from llm_reporting.schema import DetectionSummary, ReportingInput
from data_ingestion.preprocessing import apply_speckle_filter

# --- 1. Testing Data Contracts (Pydantic) ---

def test_valid_detection_schema():
    """Test that a correct iceberg detection is accepted."""
    data = {
        "iceberg_id": "ICE-001",
        "latitude": 47.5,
        "longitude": -52.7,
        "size_sq_m": 500.0,
        "confidence": 0.95
    }
    detection = DetectionSummary(**data)
    assert detection.iceberg_id == "ICE-001"
    assert detection.latitude == 47.5

def test_invalid_coordinates():
    """Test that impossible coordinates trigger a validation error."""
    invalid_data = {
        "iceberg_id": "ICE-BAD",
        "latitude": 150.0, # Latitude cannot be 150
        "longitude": -52.7,
        "size_sq_m": 500.0,
        "confidence": 0.95
    }
    with pytest.raises(ValidationError):
        DetectionSummary(**invalid_data)

def test_negative_confidence():
    """Test that confidence scores must be between 0 and 1."""
    with pytest.raises(ValidationError):
        DetectionSummary(
            iceberg_id="ICE-01", 
            latitude=45.0, 
            longitude=-50.0, 
            size_sq_m=100, 
            confidence=-0.5 # Invalid
        )

# --- 2. Testing Preprocessing Logic ---

def test_speckle_filter_output_shape():
    """Ensure the filter doesn't change the image dimensions."""
    dummy_image = np.random.rand(100, 100).astype(np.float32)
    filtered = apply_speckle_filter(dummy_image, window_size=3)
    
    assert filtered.shape == (100, 100)
    assert isinstance(filtered, np.ndarray)

def test_speckle_filter_smoothing():
    """Verify the filter actually modifies the pixels (averaging effect)."""
    # Create an image with one very bright 'spike' (noise)
    dummy_image = np.zeros((10, 10))
    dummy_image[5, 5] = 10.0 
    
    filtered = apply_speckle_filter(dummy_image, window_size=3)
    
    # The spike should be smoothed out (the value at 5,5 should decrease)
    assert filtered[5, 5] < 10.0
    assert filtered[5, 5] > 0