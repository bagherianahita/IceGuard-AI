"""
LLM-based reporting module for IceGuard AI.

Responsible for:
- Defining report schemas and prompt templates.
- Orchestrating LLM calls to generate maritime safety reports.
- Integrating detections and contextual data into human-readable outputs.
"""
"""
LLM Reporting Module: Generates maritime safety advisories using RAG and GPT-4o.
"""
from .maritime_safety_advisory import generate_maritime_safety_advisory
from .prompts import SAFETY_REPORT_PROMPT_TEMPLATE
from .schema import MaritimeSafetyInput

# Versioning the reporting logic is a professional touch
__version__ = "1.0.0"

__all__ = [
    "generate_maritime_safety_advisory",
    "MaritimeSafetyInput",
    "SAFETY_REPORT_PROMPT_TEMPLATE"
]