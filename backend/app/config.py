from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the app package (backend/app/)
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
# data/ is a sibling of the app/ directory inside backend/
DATA_DIR = BASE_DIR.parent / "data"


class Settings(BaseSettings):
    app_name: str = "MedAssist AI Backend"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    allowed_origins: str | list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    
    # Corrected Model Paths
    model_path: Path = MODELS_DIR / "trained_model.joblib"
    label_encoder_path: Path = MODELS_DIR / "label_encoder.joblib"
    faiss_index_path: Path = MODELS_DIR / "medquad_index"
    
    # Dataset Paths
    medquad_processed_path: Path = DATA_DIR / "medquad_processed.csv"
    min_symptom_length: int = 12

    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=(),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
