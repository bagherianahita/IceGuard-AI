from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Sequence, Union

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

LOGGER = logging.getLogger(__name__)


try:
    # Preferred import for modern LangChain setups
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - fallback for older LangChain versions
    # Backwards-compatible fallback; may be deprecated in newer LangChain versions.
    from langchain.chat_models import ChatOpenAI  # type: ignore


JsonDict = Dict[str, Any]


class MaritimeSafetyAdvisoryError(RuntimeError):
    """Domain-specific error for LLM-based maritime safety advisory failures."""


@dataclass(frozen=True)
class IcebergReportInput:
    """Typed representation of the input JSON for maritime safety advisory generation."""

    iceberg_coordinates: List[Mapping[str, float]]
    size_estimate: str
    current_weather_conditions: str

    @staticmethod
    def from_payload(payload: Union[str, Mapping[str, Any]]) -> "IcebergReportInput":
        """Parse and validate an input payload.

        Args:
            payload: Either a JSON string or a mapping containing the required fields.

        Raises:
            ValueError: If fields are missing or invalid.
        """
        if isinstance(payload, str):
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise ValueError("Payload is not valid JSON.") from exc
        else:
            data = dict(payload)

        missing = {field for field in ("iceberg_coordinates", "size_estimate", "current_weather_conditions") if field not in data}
        if missing:
            raise ValueError(f"Missing required fields in payload: {', '.join(sorted(missing))}.")

        coords = data["iceberg_coordinates"]
        if not isinstance(coords, Sequence) or not coords:
            raise ValueError("Field 'iceberg_coordinates' must be a non-empty list of coordinate mappings.")

        for idx, coord in enumerate(coords):
            if not isinstance(coord, Mapping):
                raise ValueError(f"Coordinate at index {idx} must be a mapping with 'lat' and 'lon' keys.")
            if "lat" not in coord or "lon" not in coord:
                raise ValueError(f"Coordinate at index {idx} is missing 'lat' or 'lon'.")

        size_estimate = str(data["size_estimate"])
        weather = str(data["current_weather_conditions"])

        return IcebergReportInput(
            iceberg_coordinates=[{"lat": float(c["lat"]), "lon": float(c["lon"])} for c in coords],
            size_estimate=size_estimate,
            current_weather_conditions=weather,
        )


SYSTEM_PROMPT = """
You are a **C-CORE Maritime Safety Expert** specializing in iceberg risk assessment on the Grand Banks of Newfoundland.

You are given:
- A set of iceberg coordinates (latitude / longitude, WGS84).
- An estimated size for the primary iceberg field or representative iceberg(s).
- A short description of the current weather and sea-state conditions.

Your tasks:
1. Assess the navigational risk to a large commercial vessel (e.g., cargo ship, tanker) operating in the vicinity.
2. Provide a clear, structured safety advisory targeted at the ship's captain and bridge team.
3. Explicitly state key assumptions and limitations of your assessment.

STRICT GUARDRAIL – COORDINATE HANDLING:
- You must **NOT** perform any new coordinate calculations or extrapolate new positions.
- You must **ONLY** refer to iceberg positions using the coordinates provided in the input.
- Do **NOT** invent new coordinate values, approximate new positions, or "project" future coordinates.
- If you need to discuss relative positions (e.g., "clustered together", "spread out"), do so qualitatively without creating new coordinate pairs.

OUTPUT REQUIREMENTS:
- Respond **only** with a JSON object having the following keys:
  - "risk_level": one of ["LOW", "MEDIUM", "HIGH", "CRITICAL"].
  - "narrative_summary": a concise, expert-level description of the situation.
  - "recommended_actions": an array of concise recommendations for the ship's captain.
  - "assumptions_and_limitations": a short section that clearly lists key assumptions.
  - "coordinates_used_verbatim": an array of all iceberg coordinate objects you explicitly relied on, copied exactly as received.

Remember: Do not fabricate data, and do not go beyond the provided geospatial and environmental information.
""".strip()


def _build_maritime_prompt() -> ChatPromptTemplate:
    """Create the LangChain chat prompt template for maritime safety advisory generation."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "user",
                (
                    "Here is the iceberg and context data in JSON format:\n"
                    "{input_json}\n\n"
                    "Generate the safety advisory JSON described in the system prompt."
                ),
            ),
        ]
    )


def _build_llm(model_name: str = "gpt-4o") -> ChatOpenAI:
    """Instantiate the ChatOpenAI model used for advisory generation.

    The model expects the OPENAI_API_KEY environment variable to be set.
    """
    return ChatOpenAI(
        model=model_name,
        temperature=0.1,
    )


def _parse_model_output(raw_text: str) -> JsonDict:
    """Parse the LLM's raw text output as JSON."""
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        LOGGER.exception("LLM response is not valid JSON: %s", raw_text)
        raise MaritimeSafetyAdvisoryError("LLM response is not valid JSON.") from exc


def _validate_coordinate_integrity(
    model_output: JsonDict,
    original_coordinates: List[Mapping[str, float]],
) -> None:
    """Guardrail: ensure the model did not hallucinate new coordinates.

    This guardrail enforces that:
    - The 'coordinates_used_verbatim' field exists.
    - Each coordinate pair in that list matches one of the original coordinates
      within a tight tolerance.
    - The model is allowed to return a subset of the original coordinates,
      but is strictly forbidden from introducing new coordinates.
    """
    epsilon = 1e-5

    used_coords = model_output.get("coordinates_used_verbatim")
    if not isinstance(used_coords, list):
        raise MaritimeSafetyAdvisoryError(
            "Guardrail violation: 'coordinates_used_verbatim' is missing or not a list."
        )

    # Precompute original coordinates as simple (lat, lon) tuples for comparison.
    original_pairs = [
        (float(coord["lat"]), float(coord["lon"])) for coord in original_coordinates
    ]

    for idx, used in enumerate(used_coords):
        if not isinstance(used, Mapping) or "lat" not in used or "lon" not in used:
            raise MaritimeSafetyAdvisoryError(
                f"Guardrail violation: coordinate at index {idx} in 'coordinates_used_verbatim' "
                "is malformed."
            )

        used_lat = float(used["lat"])
        used_lon = float(used["lon"])

        # Check that this used coordinate matches at least one of the originals.
        matches_original = any(
            abs(orig_lat - used_lat) <= epsilon and abs(orig_lon - used_lon) <= epsilon
            for orig_lat, orig_lon in original_pairs
        )

        if not matches_original:
            raise MaritimeSafetyAdvisoryError(
                "Guardrail violation: model-introduced coordinate detected. "
                f"Index {idx}: used=({used_lat}, {used_lon}) is not present in the input "
                "within the allowed tolerance."
            )


def build_maritime_safety_chain(
    model_name: str = "gpt-4o",
) -> Runnable:
    """Build the LangChain Runnable that generates a maritime safety advisory.

    Returns:
        A Runnable that accepts a mapping with the key 'input_json' (string) and
        returns the raw model text output.
    """
    prompt = _build_maritime_prompt()
    llm = _build_llm(model_name=model_name)
    return prompt | llm


def generate_maritime_safety_advisory(
    payload: Union[str, Mapping[str, Any]],
    model_name: str = "gpt-4o",
) -> JsonDict:
    """Generate a structured maritime safety advisory for a ship captain.

    This function:
    - Validates and normalizes the input payload.
    - Calls a GPT-4o-based LangChain chain acting as a C-CORE Maritime Safety Expert.
    - Parses the JSON output.
    - Applies a local guardrail to ensure the model did not hallucinate new coordinates.

    Args:
        payload: JSON payload (string or mapping) with fields:
            - iceberg_coordinates: list of { "lat": float, "lon": float }
            - size_estimate: str
            - current_weather_conditions: str
        model_name: OpenAI model name to use (default: "gpt-4o").

    Returns:
        A dictionary representing the validated advisory JSON.

    Raises:
        ValueError: If the input payload is invalid.
        MaritimeSafetyAdvisoryError: If the model output is invalid or the
            guardrail detects coordinate hallucination.
    """
    report_input = IcebergReportInput.from_payload(payload)
    input_json_str = json.dumps(
        {
            "iceberg_coordinates": report_input.iceberg_coordinates,
            "size_estimate": report_input.size_estimate,
            "current_weather_conditions": report_input.current_weather_conditions,
        }
    )

    LOGGER.info("Generating maritime safety advisory with %d iceberg coordinates.", len(report_input.iceberg_coordinates))

    chain = build_maritime_safety_chain(model_name=model_name)
    response = chain.invoke({"input_json": input_json_str})

    # Depending on LangChain version, response may be a Message or plain string.
    if hasattr(response, "content"):
        raw_text = str(response.content)
    else:
        raw_text = str(response)

    model_output = _parse_model_output(raw_text)
    _validate_coordinate_integrity(model_output, report_input.iceberg_coordinates)

    return model_output


__all__ = [
    "IcebergReportInput",
    "MaritimeSafetyAdvisoryError",
    "generate_maritime_safety_advisory",
    "build_maritime_safety_chain",
]

