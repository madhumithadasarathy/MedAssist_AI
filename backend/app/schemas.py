from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class PredictionItem(BaseModel):
    name: str = Field(alias="condition")
    confidence: float

class ConfiguredKnowledge(BaseModel):
    question: str
    answer: str
    score: float

class ChatResponse(BaseModel):
    emergency: bool
    safety_message: str
    possible_conditions: list[PredictionItem]
    why: list[str]
    explanations: list[ConfiguredKnowledge]
    response: str
    disclaimer: str

class PredictResponse(BaseModel):
    user_message: str
    disclaimer: str
    possible_conditions: list[PredictionItem]


class SearchResponse(BaseModel):
    query: str
    disclaimer: str
    results: list[ConfiguredKnowledge]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    rag_loaded: bool


class StatusResponse(BaseModel):
    name: str
    status: str
    version: str
