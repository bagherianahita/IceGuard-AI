from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DetectionSummary(BaseModel):
    """Contract for individual iceberg data passed to the LLM."""
    iceberg_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    size_sq_m: float = Field(..., gt=0)
    confidence: float = Field(..., ge=0, le=1)

class MaritimeSafetyReport(BaseModel):
    """The final structured output we expect from the LLM."""
    risk_level: str = Field(..., pattern="^(Low|Medium|High|Critical)$")
    summary: str
    threats_identified: List[str]
    recommended_actions: List[str]
    imo_compliance_notes: Optional[str] = None

class ReportingInput(BaseModel):
    """The full context required to generate a report."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    region_name: str
    detections: List[DetectionSummary]
    weather_forecast: str
    vessel_type: str = "Commercial Cargo"