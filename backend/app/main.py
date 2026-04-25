from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from collections import defaultdict
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
classifier = SymptomClassifier()
retriever = MedQuadRetriever()

app = FastAPI(title=settings.app_name, version=settings.app_version)

# Global status flags
model_loaded = False
rag_loaded = False

@app.on_event("startup")
def startup_event():
    """Synchronous startup event to ensure artifacts load before traffic."""
    global model_loaded, rag_loaded
    
    logger.info("🚀 STARTUP TRIGGERED")
    
    # Path resolution inside Docker (assume WORKDIR is /app, main.py is in app/)
    BASE_DIR = Path(__file__).resolve().parent
    models_dir = BASE_DIR / "models"
    
    logger.info(f"📂 BASE_DIR: {BASE_DIR}")
    logger.info(f"📂 MODELS_DIR: {models_dir}")

    model_path = models_dir / "trained_model.joblib"
    encoder_path = models_dir / "label_encoder.joblib"
    faiss_path = settings.faiss_index_path

    logger.info(f"📂 MODEL PATH: {model_path} | EXISTS: {model_path.exists()}")
    logger.info(f"📂 ENCODER PATH: {encoder_path} | EXISTS: {encoder_path.exists()}")
    logger.info(f"📂 FAISS PATH: {faiss_path} | EXISTS: {faiss_path.exists()}")

    try:
        # Load Classifier
        if model_path.exists():
            classifier.load()
            model_loaded = classifier.loaded
            if model_loaded:
                logger.info("✅ MODEL LOADED")
            else:
                logger.error("❌ CLASSIFIER OBJECT FAILED TO INITIALIZE ARTIFACTS")
        else:
            logger.error(f"❌ MODEL FILE NOT FOUND: {model_path}")

        # Load RAG
        if faiss_path.exists():
            retriever.load()
            rag_loaded = retriever.loaded
            if rag_loaded:
                logger.info("✅ RAG LOADED")
            else:
                logger.error("❌ RAG OBJECT FAILED TO INITIALIZE INDEX")
        else:
            logger.error(f"❌ FAISS INDEX NOT FOUND: {faiss_path}")

    except Exception as e:
        logger.error(f"🔥 ERROR DURING STARTUP: {e}", exc_info=True)

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

# Diagnostic/Health Routes
@app.get("/ready")
def ready() -> dict:
    if model_loaded and rag_loaded:
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="Services not fully loaded yet")

@app.get("/", response_model=StatusResponse)
def root() -> StatusResponse:
    return StatusResponse(name=settings.app_name, status="ok", version=settings.app_version)

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check reflecting actual loading status."""
    logger.info(f"Health check: Model={model_loaded}, RAG={rag_loaded}")
    return HealthResponse(
        status="healthy" if model_loaded and rag_loaded else "degraded",
        model_loaded=model_loaded,
        rag_loaded=rag_loaded,
    )

@app.get("/debug-paths")
def debug_paths():
    """Diagnostic endpoint to inspect file system inside container."""
    BASE_DIR = Path(__file__).resolve().parent
    models_dir = BASE_DIR / "models"
    files = []
    if models_dir.exists():
        files = os.listdir(str(models_dir))
    
    return {
        "base_dir": str(BASE_DIR),
        "models_dir_exists": models_dir.exists(),
        "files": files
    }

# API Endpoints
@app.post(f"{settings.api_prefix}/predict", response_model=PredictResponse)
def predict(payload: ChatRequest) -> PredictResponse:
    message = payload.message.strip()
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model artifacts not loaded")
    
    try:
        predictions, _ = classifier.predict_top_k(message, k=3)
        return PredictResponse(
            user_message=message,
            disclaimer=build_disclaimer(),
            possible_conditions=[
                {"name": item.condition, "confidence": item.confidence} for item in predictions
            ],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.post(f"{settings.api_prefix}/search-medquad", response_model=SearchResponse)
def search_medquad(payload: ChatRequest) -> SearchResponse:
    message = payload.message.strip()
    if not rag_loaded:
        raise HTTPException(status_code=503, detail="RAG system not loaded")
    
    try:
        docs = retriever.search(message, top_k=3)
        return SearchResponse(
            query=message,
            disclaimer=build_disclaimer(),
            results=[{"question": d.question, "answer": d.answer, "score": d.score} for d in docs],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Knowledge search failed")

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    message = payload.message.strip()
    safety = detect_red_flags(message)

    try:
        predictions, why_tokens = classifier.predict_top_k(message, k=3)
        docs = retriever.search(message, top_k=3) if rag_loaded else []
        
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
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Chat processing failed")