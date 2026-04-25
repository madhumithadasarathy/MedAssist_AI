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
        self.pipeline: Any | None = None
        self.label_encoder: Any | None = None
        self.loaded = False
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
            logger.info(f"Loading pipeline from {self.model_path}")
            self.pipeline = joblib.load(self.model_path)
            
            # Load the label encoder separately
            logger.info(f"Loading label encoder from {self.label_encoder_path}")
            self.label_encoder = joblib.load(self.label_encoder_path)
            
            self.loaded = True
            logger.info("✅ CLASSIFIER LOADED")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SymptomClassifier: {str(e)}", exc_info=True)
            self.loaded = False

    def predict(self, text: str) -> str:
        """Predict the single most likely condition using the pipeline directly."""
        if not self.loaded or self.pipeline is None or self.label_encoder is None:
            raise RuntimeError("Classifier artifacts are not loaded.")
        
        cleaned = normalize_text(text)
        # Use pipeline.predict directly as requested
        prediction = self.pipeline.predict([cleaned])[0]
        
        # Decode using label_encoder
        decoded = self.label_encoder.inverse_transform([prediction])[0]
        return str(decoded)

    def predict_top_k(self, text: str, k: int = 3) -> tuple[list[Prediction], list[str]]:
        """Predict top K conditions with confidence scores."""
        if not self.loaded or self.pipeline is None or self.label_encoder is None:
            raise FileNotFoundError("Classifier artifacts were not found.")

        cleaned = normalize_text(text)
        
        # Get probabilities for all classes
        probabilities = self.pipeline.predict_proba([cleaned])[0]
        classes = np.asarray(self.pipeline.classes_)
        
        # Sort by probability descending
        top_indices = np.argsort(probabilities)[::-1][:k]

        predictions: list[Prediction] = []
        for index in top_indices:
            label = classes[index]
            # Decode using label_encoder
            decoded = self.label_encoder.inverse_transform([label])[0]
            predictions.append(
                Prediction(
                    condition=str(decoded),
                    confidence=round(float(probabilities[index] * 100), 2),
                )
            )
            
        # Extract explanation terms from the TfidfVectorizer inside the pipeline
        why_terms = []
        try:
            vectorizer = self.pipeline.named_steps.get("tfidf")
            if vectorizer:
                tfidf_vec = vectorizer.transform([cleaned]).tocoo()
                items = sorted(zip(tfidf_vec.col, tfidf_vec.data), key=lambda x: x[1], reverse=True)
                feature_names = vectorizer.get_feature_names_out()
                why_terms = [str(feature_names[idx]) for idx, _ in items[:3]]
        except Exception as e:
            logger.warning(f"Could not extract explanation terms: {e}")

        return predictions, why_terms
