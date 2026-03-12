import json
from langchain_openai import ChatOpenAI
from .prompts import SAFETY_ADVISORY_PROMPT
from .schema import ReportingInput, MaritimeSafetyReport

class ReportingChain:
    """
    Nature: LLM Orchestrator.
    Aim: Bridges detections and LLM reasoning to produce an auditable report.
    """
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(openai_api_key=api_key, model=model, temperature=0.2)
        # We use a lower temperature (0.2) for more factual, stable reports

    def generate(self, input_data: ReportingInput) -> MaritimeSafetyReport:
        # 1. Prepare data for the prompt
        detections_json = json.dumps([d.dict() for d in input_data.detections])
        
        # 2. Build the chain
        chain = SAFETY_ADVISORY_PROMPT | self.llm
        
        # 3. Invoke and Parse
        response = chain.invoke({
            "region_name": input_data.region_name,
            "timestamp": input_data.timestamp.isoformat(),
            "vessel_type": input_data.vessel_type,
            "weather_forecast": input_data.weather_forecast,
            "detections_json": detections_json
        })
        
        # 4. Return as a structured object
        # In a production environment, we would use a JsonOutputParser here
        return response.content