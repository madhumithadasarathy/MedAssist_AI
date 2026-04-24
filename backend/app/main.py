from __future__ import annotations

import logging
import time
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
classifier = SymptomClassifier()
retriever = MedQuadRetriever()

app = FastAPI(title=settings.app_name, version=settings.app_version)

origins = settings.allowed_origins
if isinstance(origins, str):
    if origins == "*":
        origins = ["*"]
    else:
        origins = [o.strip() for o in origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Failed request to {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"message": str(exc), "code": "INTERNAL_ERROR"}}
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} request to {request.url.path}")
    response = await call_next(request)
    return response

@app.get("/ready")
def ready() -> dict:
    if classifier.loaded and retriever.loaded:
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="Services not fully loaded yet")


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


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    message = payload.message.strip()
    if len(message) < settings.min_symptom_length:
        raise HTTPException(status_code=400, detail={"error": {"message": "Please share more details.", "code": "BAD_REQUEST"}})

    safety = detect_red_flags(message)

    try:
        predictions, why_tokens = classifier.predict_top_k(message, k=3)
        docs = []
        try:
            docs = retriever.search(message, top_k=3)
        except Exception as rag_exc:
            logger.warning(f"RAG failed securely, skipping: {rag_exc}")
            
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Chat processing failed.")

    return ChatResponse(
        emergency=safety.emergency,
        safety_message="Seek immediate medical help." if safety.emergency else "",
        possible_conditions=[
            {"name": item.condition, "confidence": item.confidence / 100.0} for item in predictions
        ],
        why=why_tokens,
        explanations=[
            {
                "question": doc.question,
                "answer": doc.answer,
                "score": doc.score
            }
            for doc in docs
        ],
        response=f"Based on your symptoms, possible conditions may include {', '.join([p.condition for p in predictions])}. However, please note this is not definitive.",
        disclaimer="This is not a medical diagnosis. Please consult a qualified healthcare professional."
    )