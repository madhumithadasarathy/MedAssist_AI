import os
from pathlib import Path
import re

ROOT = Path("c:/Users/madhumitha D/Desktop/medbot")

def upgrade_main():
    main_path = ROOT / "backend" / "app" / "main.py"
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add logging and exception handling, ready endpoints
    new_imports = """
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
"""
    content = re.sub(r'from fastapi import FastAPI, HTTPException\nfrom fastapi.middleware.cors import CORSMiddleware', new_imports.strip(), content)

    # Logging setup
    logging_setup = """
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
"""
    content = re.sub(r'settings = get_settings\(\)', logging_setup.strip(), content)

    # Exception handler
    app_setup = """
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
"""
    content = re.sub(r'app = FastAPI.*allow_headers=\["\*"\],\n\)', app_setup.strip(), content, flags=re.DOTALL)

    # Update chat endpoint
    chat_endpoint = """
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
"""
    content = re.sub(r'@app\.post\(f"\{settings\.api_prefix\}/chat".*$', chat_endpoint.strip(), content, flags=re.DOTALL)
    
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)

def upgrade_schemas():
    path = ROOT / "backend" / "app" / "schemas.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    new_schemas = """
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
"""
    content = re.sub(r'class PredictionItem\(BaseModel\):.*(?=class PredictResponse)', new_schemas.strip() + '\n\n', content, flags=re.DOTALL)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def upgrade_classifier():
    path = ROOT / "backend" / "app" / "classifier.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    new_predict = """
    def predict_top_k(self, text: str, k: int = 3) -> tuple[list[Prediction], list[str]]:
        if not self.loaded or self.pipeline is None or self.label_encoder is None:
            raise FileNotFoundError("Classifier artifacts were not found.")

        cleaned = normalize_text(text)
        probabilities = self.pipeline.predict_proba([cleaned])[0]
        classes = np.asarray(self.pipeline.classes_)
        top_indices = np.argsort(probabilities)[::-1][:k]

        predictions: list[Prediction] = []
        for index in top_indices:
            label = classes[index]
            decoded = self.label_encoder.inverse_transform([label])[0]
            predictions.append(
                Prediction(
                    condition=str(decoded),
                    confidence=round(float(probabilities[index] * 100), 2),
                )
            )
            
        vectorizer = self.pipeline.named_steps.get("tfidf")
        why_terms = []
        if vectorizer:
            tfidf_vec = vectorizer.transform([cleaned]).tocoo()
            items = sorted(zip(tfidf_vec.col, tfidf_vec.data), key=lambda x: x[1], reverse=True)
            feature_names = vectorizer.get_feature_names_out()
            why_terms = [str(feature_names[idx]) for idx, _ in items[:3]]

        return predictions, why_terms
"""
    content = re.sub(r'    def predict_top_k\(self, text: str, k: int = 3.*?(?=\n\n|\Z)', new_predict, content, flags=re.DOTALL)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def configure_env():
    env_example = """MODEL_PATH=./app/models/trained_model.joblib
VECTORIZER_PATH=./app/models/vectorizer.joblib
FAISS_PATH=./app/models/faiss_index
ALLOWED_ORIGINS=*
"""
    with open(ROOT / "backend" / ".env.example", "w") as f:
        f.write(env_example)

    with open(ROOT / "backend" / ".env", "w") as f:
        f.write(env_example)

def update_docker():
    compose = """version: '3.8'

services:
  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    env_file: ./backend/.env

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
"""
    with open(ROOT / "docker-compose.yml", "w") as f:
        f.write(compose)


if __name__ == "__main__":
    upgrade_main()
    upgrade_schemas()
    upgrade_classifier()
    configure_env()
    update_docker()
    print("Backend upgraded successfully.")
