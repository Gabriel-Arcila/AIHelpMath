from pydantic import BaseModel
from typing import List

class ExplanationRequest(BaseModel):
    problem: str
    level: str = "intermediate"

class ExplanationResponse(BaseModel):
    explanation: str
    steps: List[str]
