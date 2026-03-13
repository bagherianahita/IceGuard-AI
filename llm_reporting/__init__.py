"""
LLM-based reporting module for IceGuard AI.

Responsible for:
- Defining report schemas and prompt templates.
- Orchestrating LLM calls to generate maritime safety reports.
- Integrating detections and contextual data into human-readable outputs.
"""

from .maritime_safety_advisory import (
    IcebergReportInput,
    MaritimeSafetyAdvisoryError,
    build_maritime_safety_chain,
    generate_maritime_safety_advisory,
)

__version__ = "1.0.0"

__all__ = [
    "IcebergReportInput",
    "MaritimeSafetyAdvisoryError",
    "build_maritime_safety_chain",
    "generate_maritime_safety_advisory",
]