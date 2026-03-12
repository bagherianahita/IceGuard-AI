import os
from pathlib import Path
from dotenv import load_dotenv

# Import our custom modules
from data_ingestion import SentinelClient, process_sar_image
from detection_engine import IcebergDetectionPipeline
from llm_reporting import ReportingChain, MaritimeSafetyInput, DetectionSummary

# Load environment variables (API Keys)
load_dotenv()

def run_iceguard_pipeline(region_name: str, bbox: list, vessel_type: str):
    print(f"🚀 Starting IceGuard AI Pipeline for {region_name}...")

    # 1. DATA INGESTION
    # In a real run, we fetch from Sentinel Hub. For the demo, we use a local path.
    client = SentinelClient(api_key=os.getenv("SH_CLIENT_ID"))
    raw_path = "data/raw_samples/grand_banks_s1.tif"
    processed_path = "data/processed/latest_ready.tif"
    
    print("📡 Step 1: Preprocessing SAR Imagery...")
    process_sar_image(raw_path, processed_path)

    # 2. DETECTION ENGINE
    print("🔍 Step 2: Running Iceberg Detection Models...")
    pipeline = IcebergDetectionPipeline()
    raw_detections = pipeline.run(processed_path)
    
    # Convert raw dicts to our Pydantic Data Contract
    detections = [
        DetectionSummary(
            iceberg_id=d["internal_id"],
            latitude=d["latitude"],
            longitude=d["longitude"],
            size_sq_m=d["area_pixels"] * 100, # Assuming 10m resolution
            confidence=d["confidence"]
        ) for d in raw_detections
    ]
    print(f"✅ Found {len(detections)} potential iceberg targets.")

    # 3. LLM REPORTING
    print("🤖 Step 3: Generating Maritime Safety Advisory...")
    reporting_engine = ReportingChain(api_key=os.getenv("OPENAI_API_KEY"))
    
    report_input = ReportingInput(
        region_name=region_name,
        detections=detections,
        weather_forecast="Moderate fog, 2-meter swells, winds 15 knots NW",
        vessel_type=vessel_type
    )
    
    final_report = reporting_engine.generate(report_input)
    
    print("\n--- FINAL MARITIME ADVISORY ---")
    print(final_report)
    return final_report

if __name__ == "__main__":
    # Example coordinates for Grand Banks
    GRAND_BANKS_BBOX = [-53.0, 46.5, -52.0, 47.5]
    run_iceguard_pipeline("Grand Banks", GRAND_BANKS_BBOX, "Oil Tanker")