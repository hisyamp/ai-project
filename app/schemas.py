from typing import Literal

from pydantic import BaseModel, Field

ConfidenceLabel = Literal["high", "medium", "low"]

ReasonCode = Literal[
    "answered",
    "no_relevant_context",
    "out_of_scope",
    "prompt_injection_detected",
]


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class SourceChunk(BaseModel):
    section_title: str
    doc_version: str
    is_active: bool
    chunk_id: str


class AskResponse(BaseModel):
    answer: str
    confidence_label: ConfidenceLabel
    reason_code: ReasonCode
    sources: list[SourceChunk] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
