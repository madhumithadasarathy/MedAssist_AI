from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from .config import get_settings
from .safety import normalize_text


@dataclass(slots=True)
class Prediction:
    condition: str
    confidence: float


class SymptomClassifier:
    def __init__(self, model_path: Path | None = None, label_encoder_path: Path | None = None) -> None:
        settings = get_settings()
        self.model_path = model_path or settings.model_path
        self.label_encoder_path = label_encoder_path or settings.label_encoder_path
        self.pipeline: Any | None = None
        self.label_encoder: Any | None = None
        self.loaded = False
        self.load()

    def load(self) -> None:
        if not self.model_path.exists() or not self.label_encoder_path.exists():
            self.loaded = False
            return

        self.pipeline = joblib.load(self.model_path)
        self.label_encoder = joblib.load(self.label_encoder_path)
        self.loaded = True


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
        return predictions
