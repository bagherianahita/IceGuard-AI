import pytest
from llm_reporting.schema import ReportingInput, DetectionSummary
from llm_reporting.reporting_chain import ReportingChain
import os
from datetime import datetime

# We use a 'mock' or 'fake' approach for the LLM if we don't want to spend API credits
# But for a true integration test, we check if the Data Objects align.

def test_pipeline_data_flow():
    """
    Nature: Integration Test.
    Aim: Ensure the output of the Detection module matches the input of the LLM module.
    """
    # 1. Simulate what the Detection Engine produces
    mock_detections = [
        {
            "internal_id": "ICE-99",
            "latitude": 48.1,
            "longitude": -52.5,
            "area_pixels": 50.0,
            "confidence": 0.98
        }
    ]

    # 2. Transform to the Reporting Schema (This is the 'Handshake')
    formatted_detections = [
        DetectionSummary(
            iceberg_id=d["internal_id"],
            latitude=d["latitude"],
            longitude=d["longitude"],
            size_sq_m=d["area_pixels"] * 10,
            confidence=d["confidence"]
        ) for d in mock_detections
    ]

    # 3. Build the LLM Input object
    report_context = ReportingInput(
        region_name="Grand Banks",
        detections=formatted_detections,
        weather_forecast="Clear skies",
        vessel_type="Tanker"
    )

    # 4. Verify the handshake
    assert len(report_context.detections) == 1
    assert report_context.detections[0].iceberg_id == "ICE-99"
    assert isinstance(report_context.timestamp, datetime)
    print("✅ Integration: Detection-to-Reporting Handshake Successful")

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API Key not found")
def test_llm_response_structure():
    """
    Aim: Verify that the actual LLM (if API key is present) returns a valid structure.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    chain = ReportingChain(api_key=api_key)
    
    test_input = ReportingInput(
        region_name="Test Region",
        detections=[DetectionSummary(iceberg_id="T1", latitude=47.0, longitude=-52.0, size_sq_m=100, confidence=0.9)],
        weather_forecast="Calm",
        vessel_type="Fishing Boat"
    )
    
    # Generate report
    report = chain.generate(test_input)
    
    # If the LLM returned a string that we expect to be JSON
    assert len(report) > 0
    print("✅ Integration: LLM Response Received")