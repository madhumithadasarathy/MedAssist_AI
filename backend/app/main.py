from __future__ import annotations

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .classifier import SymptomClassifier
from .config import get_settings
from .retriever import MedQuadRetriever
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

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Global instances (Lazy loading enabled)
classifier = SymptomClassifier()
retriever = MedQuadRetriever()

app = FastAPI(title=settings.app_name, version=settings.app_version)

@app.on_event("startup")
async def startup_event():
    """Startup check. We attempt load but do not crash if it fails validation."""
    logger.info("🚀 APP STARTUP: performing preliminary model validation...")
    try:
        classifier.load()
    except Exception as e:
        logger.error(f"🚨 STARTUP VALIDATION FAILED: {e}")
        # We continue so the API stays up (to serve health and error messages)
    
    logger.info("✅ Startup sequence complete.")

# CORS
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
    logger.error(f"Unhandled error for {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"message": str(exc), "code": "INTERNAL_ERROR"}}
    )

# Diagnostic/Health Routes
@app.get("/")
def root():
    """Standard health check for HuggingFace Spaces."""
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check reflecting dynamic loading status."""
    return HealthResponse(
        status="healthy" if classifier.loaded and retriever.loaded else "degraded",
        model_loaded=classifier.loaded,
        rag_loaded=retriever.loaded,
    )

# API Endpoints
@app.post(f"{settings.api_prefix}/predict", response_model=PredictResponse)
def predict(payload: ChatRequest):
    message = payload.message.strip()
    try:
        predictions, _ = classifier.predict_top_k(message, k=3)
        return PredictResponse(
            user_message=message,
            disclaimer=build_disclaimer(),
            possible_conditions=[
                {"name": item.condition, "confidence": item.confidence} for item in predictions
            ],
        )
    except Exception as e:
        # Step 4 Implementation
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Model not ready",
                "details": str(e),
                "action": "Retrain model with matching sklearn version"
            }
        )

@app.post(f"{settings.api_prefix}/search-medquad", response_model=SearchResponse)
def search_medquad(payload: ChatRequest) -> SearchResponse:
    message = payload.message.strip()
    try:
        docs = retriever.search(message, top_k=3)
        return SearchResponse(
            query=message,
            disclaimer=build_disclaimer(),
            results=[{"question": d.question, "answer": d.answer, "score": d.score} for d in docs],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    message = payload.message.strip()
    safety = detect_red_flags(message)

    try:
        predictions, why_tokens = classifier.predict_top_k(message, k=3)
        docs = retriever.search(message, top_k=3)
        
        return ChatResponse(
            emergency=safety.emergency,
            safety_message="Seek immediate medical help." if safety.emergency else "",
            possible_conditions=[
                {"name": item.condition, "confidence": item.confidence / 100.0} for item in predictions
            ],
            why=why_tokens,
            explanations=[{"question": d.question, "answer": d.answer, "score": d.score} for d in docs],
            response=f"Based on your symptoms, possible conditions may include {', '.join([p.condition for p in predictions])}.",
            disclaimer=build_disclaimer()
        )
    except Exception as e:
        # Step 4 Implementation
        logger.error(f"Chat execution failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Model not ready",
                "details": str(e),
                "action": "Retrain model with matching sklearn version"
            }
        )