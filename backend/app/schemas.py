from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class PredictionItem(BaseModel):
    condition: str
    confidence: float


class KnowledgeItem(BaseModel):
    question: str
    answer: str
    source: str = "MedQuAD"
    score: float
    focus: str | None = None
    qtype: str | None = None


class ChatResponse(BaseModel):
    user_message: str
    emergency: bool
    disclaimer: str
    possible_conditions: list[PredictionItem]
    knowledge_summary: list[KnowledgeItem]
    assistant_response: str
    suggested_next_steps: list[str]
    urgent_care_reasons: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


class PredictResponse(BaseModel):
    user_message: str
    disclaimer: str
    possible_conditions: list[PredictionItem]


class SearchResponse(BaseModel):
    query: str
    disclaimer: str
    results: list[KnowledgeItem]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    rag_loaded: bool


class StatusResponse(BaseModel):
    name: str
    status: str
    version: str
