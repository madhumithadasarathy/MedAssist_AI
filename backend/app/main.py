from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .classifier import SymptomClassifier
from .config import get_settings
from .rag import MedQuadRetriever
from .response_builder import build_assistant_response, build_disclaimer
from .safety import detect_red_flags
from .schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    PredictResponse,
    SearchResponse,
    StatusResponse,
)


settings = get_settings()
classifier = SymptomClassifier()
retriever = MedQuadRetriever()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=StatusResponse)
def root() -> StatusResponse:
    return StatusResponse(name=settings.app_name, status="ok", version=settings.app_version)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        model_loaded=classifier.loaded,
        rag_loaded=retriever.loaded,
    )


@app.post(f"{settings.api_prefix}/predict", response_model=PredictResponse)
def predict(payload: ChatRequest) -> PredictResponse:
    message = payload.message.strip()
    if len(message) < settings.min_symptom_length:
        raise HTTPException(
            status_code=400,
            detail="Please provide a little more detail about symptoms, duration, and severity.",
        )

    try:
        predictions = classifier.predict_top_k(message, k=3)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Prediction failed.") from exc

    return PredictResponse(
        user_message=message,
        disclaimer=build_disclaimer(),
        possible_conditions=[
            {"condition": item.condition, "confidence": item.confidence} for item in predictions
        ],
    )


@app.post(f"{settings.api_prefix}/search-medquad", response_model=SearchResponse)
def search_medquad(payload: ChatRequest) -> SearchResponse:
    message = payload.message.strip()
    if len(message) < settings.min_symptom_length:
        raise HTTPException(
            status_code=400,
            detail="Please provide more details so the medical knowledge search has useful context.",
        )

    try:
        docs = retriever.search(message, top_k=3)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Knowledge search failed.") from exc

    return SearchResponse(
        query=message,
        disclaimer=build_disclaimer(),
        results=[
            {
                "question": doc.question,
                "answer": doc.answer,
                "source": doc.source,
                "score": doc.score,
                "focus": doc.focus,
                "qtype": doc.qtype,
            }
            for doc in docs
        ],
    )


@app.post(f"{settings.api_prefix}/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    message = payload.message.strip()
    if len(message) < settings.min_symptom_length:
        raise HTTPException(
            status_code=400,
            detail="Please share a few more details, such as symptoms, duration, severity, or age group.",
        )

    safety = detect_red_flags(message)

    try:
        predictions = classifier.predict_top_k(message, k=3)
        docs = retriever.search(message, top_k=3)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Chat processing failed.") from exc

    assistant_response, next_steps, urgent_reasons = build_assistant_response(
        message=message,
        predictions=predictions,
        docs=docs,
        safety=safety,
    )

    return ChatResponse(
        user_message=message,
        emergency=safety.emergency,
        disclaimer=build_disclaimer(),
        possible_conditions=[
            {"condition": item.condition, "confidence": item.confidence} for item in predictions
        ],
        knowledge_summary=[
            {
                "question": doc.question,
                "answer": doc.answer,
                "source": doc.source,
                "score": doc.score,
                "focus": doc.focus,
                "qtype": doc.qtype,
            }
            for doc in docs
        ],
        assistant_response=assistant_response,
        suggested_next_steps=next_steps,
        urgent_care_reasons=urgent_reasons,
        metadata={"matched_red_flags": safety.matched_red_flags},
    )
