from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import DATA_DIR, get_settings  # noqa: E402
from backend.app.safety import normalize_text  # noqa: E402


REQUIRED_COLUMNS = {"label", "text"}


def main() -> None:
    settings = get_settings()
    dataset_path = DATA_DIR / "Symptom2Disease.csv"

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Add Symptom2Disease.csv before training."
        )

    data = pd.read_csv(dataset_path)
    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing_columns)}")

    data = data.dropna(subset=["label", "text"]).copy()
    data["text"] = data["text"].astype(str).map(normalize_text)
    data["label"] = data["label"].astype(str).str.strip()
    data = data[data["text"].str.len() > 0]

    # Filter out classes with only 1 sample as they can't be stratified
    class_counts = data["label"].value_counts()
    valid_classes = class_counts[class_counts >= 2].index
    data = data[data["label"].isin(valid_classes)].copy()

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(data["label"])
    
    x_train, x_test, y_train, y_test = train_test_split(
        data["text"],
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    from sklearn.svm import LinearSVC
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.model_selection import StratifiedKFold

    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 3), max_features=8000, stop_words='english')),
            (
                "clf",
                CalibratedClassifierCV(
                    LinearSVC(class_weight='balanced', max_iter=2000, random_state=42),
                    method='sigmoid',
                    cv=2
                ),
            ),
        ]
    )

    print("Training Calibrated LinearSVC (cv=2) with optimized TF-IDF...")
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    labels_in_test = np.unique(y_test)
    report = classification_report(
        y_test,
        predictions,
        target_names=label_encoder.inverse_transform(labels_in_test),
        labels=labels_in_test,
        zero_division=0,
    )

    print(f"Accuracy: {accuracy:.4f}")
    print("Classification report:")
    print(report)

    settings.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, settings.model_path)
    joblib.dump(label_encoder, settings.label_encoder_path)

    print(f"Saved model to {settings.model_path}")
    print(f"Saved label encoder to {settings.label_encoder_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Training failed: {exc}", file=sys.stderr)
        raise
