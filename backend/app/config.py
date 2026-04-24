from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
APP_DIR = BASE_DIR / "backend" / "app"
DATA_DIR = BASE_DIR / "backend" / "data"
MODELS_DIR = APP_DIR / "models"


class Settings(BaseSettings):
    app_name: str = "MedAssist AI Backend"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    model_path: Path = MODELS_DIR / "symptom_classifier.joblib"
    label_encoder_path: Path = MODELS_DIR / "label_encoder.joblib"
    medquad_index_dir: Path = MODELS_DIR / "medquad_index"
    medquad_processed_path: Path = DATA_DIR / "medquad_processed.csv"
    min_symptom_length: int = 12

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "backend" / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
