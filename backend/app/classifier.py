from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from .config import get_settings
from .safety import normalize_text

# Initialize logger
logger = logging.getLogger(__name__)

@dataclass(slots=True)
class Prediction:
    condition: str
    confidence: float


class SymptomClassifier:
    def __init__(self, model_path: Path | None = None, label_encoder_path: Path | None = None) -> None:
        self.settings = get_settings()
        self.model_path = model_path or self.settings.model_path
        self.label_encoder_path = label_encoder_path or self.settings.label_encoder_path
        self._pipeline: Any | None = None
        self._label_encoder: Any | None = None
        self.loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy loader for classifier artifacts."""
        if not self.loaded:
            self.load()

    def load(self) -> None:
        """Load the pipeline and label encoder artifacts with robust error handling."""
        try:
            if not self.model_path.exists():
                logger.error(f"❌ Classifier model not found: {self.model_path}")
                self.loaded = False
                return

            if not self.label_encoder_path.exists():
                logger.error(f"❌ Label encoder not found: {self.label_encoder_path}")
                self.loaded = False
                return

            # Load the pipeline directly (includes Vectorizer and Classifier)
            logger.info(f"🤖 Loading classifier pipeline artifacts: {self.model_path}")
            self._pipeline = joblib.load(self.model_path)
            self._label_encoder = joblib.load(self.label_encoder_path)
            
            self.loaded = True
            logger.info("✅ CLASSIFIER ARTIFACTS LOADED")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SymptomClassifier: {str(e)}", exc_info=True)
            self.loaded = False

    @property
    def pipeline(self) -> Any:
        self._ensure_loaded()
        return self._pipeline

    @property
    def label_encoder(self) -> Any:
        self._ensure_loaded()
        return self._label_encoder

    def predict(self, text: str) -> str:
        """Predict the single most likely condition using the pipeline directly."""
        self._ensure_loaded()
        if not self.loaded or self._pipeline is None:
            raise RuntimeError("Classifier artifacts are not loaded.")
        
        cleaned = normalize_text(text)
        prediction = self._pipeline.predict([cleaned])[0]
        decoded = self._label_encoder.inverse_transform([prediction])[0]
        return str(decoded)

    def predict_top_k(self, text: str, k: int = 3) -> tuple[list[Prediction], list[str]]:
        """Predict top K conditions with confidence scores."""
        self._ensure_loaded()
        if not self.loaded or self._pipeline is None:
            raise FileNotFoundError("Classifier artifacts were not found.")

        cleaned = normalize_text(text)
        
        # Get probabilities for all classes
        probabilities = self._pipeline.predict_proba([cleaned])[0]
        classes = np.asarray(self._pipeline.classes_)
        
        # Sort by probability descending
        top_indices = np.argsort(probabilities)[::-1][:k]

        predictions: list[Prediction] = []
        for index in top_indices:
            label = classes[index]
            decoded = self._label_encoder.inverse_transform([label])[0]
            predictions.append(
                Prediction(
                    condition=str(decoded),
                    confidence=round(float(probabilities[index] * 100), 2),
                )
            )
            
        why_terms = []
        try:
            vectorizer = self._pipeline.named_steps.get("tfidf")
            if vectorizer:
                tfidf_vec = vectorizer.transform([cleaned]).tocoo()
                items = sorted(zip(tfidf_vec.col, tfidf_vec.data), key=lambda x: x[1], reverse=True)
                feature_names = vectorizer.get_feature_names_out()
                why_terms = [str(feature_names[idx]) for idx, _ in items[:3]]
        except Exception as e:
            logger.warning(f"Could not extract explanation terms: {e}")

        return predictions, why_terms
