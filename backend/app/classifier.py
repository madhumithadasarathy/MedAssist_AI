from __future__ import annotations

import logging
import sklearn
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from .config import get_settings
from .safety import normalize_text

# Initialize logger
logger = logging.getLogger(__name__)

"""
WARNING:
This model must be trained and deployed using the SAME scikit-learn version.
Recommended solution:
* Retrain model using sklearn==1.4.2 (stable for HuggingFace Spaces)
"""

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
            try:
                self.load()
            except Exception as e:
                logger.error(f"Failed to lazy load classifier: {e}")

    def load(self) -> None:
        """Load the pipeline and label encoder artifacts with hard validation."""
        logger.info(f"🔍 System sklearn version: {sklearn.__version__}")
        logger.info(f"🔍 Attempting to load model from: {self.model_path}")

        try:
            if not self.model_path.exists():
                logger.error(f"❌ Classifier model file NOT FOUND: {self.model_path}")
                self.loaded = False
                return

            if not self.label_encoder_path.exists():
                logger.error(f"❌ Label encoder file NOT FOUND: {self.label_encoder_path}")
                self.loaded = False
                return

            # 1. ATTEMPT LOADING
            self._pipeline = joblib.load(self.model_path)
            self._label_encoder = joblib.load(self.label_encoder_path)
            
            # 2. HARD VALIDATION (Task Step 2)
            # TF-IDF internal attributes (idf_) are incompatible across versions.
            # If the model was pickled on version X and loaded on version Y, 
            # the object might exist but lose its fitted state.
            tfidf = self._pipeline.named_steps.get("tfidf")
            if tfidf is None or not hasattr(tfidf, "idf_"):
                logger.error("❌ TF-IDF validation FAILED: idf_ attribute is missing.")
                self.loaded = False
                raise RuntimeError(
                    "TF-IDF vectorizer is not fitted. Model is incompatible or corrupted. "
                    "Ensure you train and deploy with the same scikit-learn version (e.g., 1.4.2)."
                )

            self.loaded = True
            logger.info("✅ CLASSIFIER LOADED AND VALIDATED SUCCESSFULLY")
        except Exception as e:
            logger.error(f"❌ Model initialization failed: {str(e)}", exc_info=True)
            self.loaded = False
            # We re-raise if it's a runtime error from our validation
            if isinstance(e, RuntimeError) and "fitted" in str(e):
                raise e

    @property
    def pipeline(self) -> Any:
        self._ensure_loaded()
        return self._pipeline

    @property
    def label_encoder(self) -> Any:
        self._ensure_loaded()
        return self._label_encoder

    def predict(self, text: str) -> str:
        """Predict the single most likely condition."""
        self._ensure_loaded()
        if not self.loaded or self._pipeline is None:
            return "Error: Model not ready (Compatibility issue)"
        
        try:
            cleaned = normalize_text(text)
            prediction = self._pipeline.predict([cleaned])[0]
            decoded = self._label_encoder.inverse_transform([prediction])[0]
            return str(decoded)
        except Exception as e:
            logger.error(f"🔥 Single prediction failed: {e}")
            return "Error: Prediction failed"

    def predict_top_k(self, text: str, k: int = 3) -> tuple[list[Prediction], list[str]]:
        """Predict top K conditions with confidence scores and robust error wrapping."""
        self._ensure_loaded()
        if not self.loaded or self._pipeline is None:
             raise RuntimeError("Model not ready. Internal validation failed.")

        try:
            cleaned = normalize_text(text)
            
            # Task Step 3: Wrap prediction call
            try:
                probabilities = self._pipeline.predict_proba([cleaned])[0]
            except Exception as e:
                logger.error(f"🔥 predict_proba failed: {e}")
                raise RuntimeError(f"Prediction failed: {str(e)}")
                
            classes = np.asarray(self._pipeline.classes_)
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
                    why_terms = [feature_names[idx] for idx, _ in items[:3]]
            except Exception:
                pass

            return predictions, why_terms
        except Exception as e:
            logger.error(f"❌ predict_top_k execution error: {e}")
            raise e
