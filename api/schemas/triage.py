from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    symptoms: str = Field(..., min_length=3, max_length=1000)


class TriageResponse(BaseModel):
    symptoms: str
    response: str
