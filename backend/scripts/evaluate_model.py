from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, top_k_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.classifier import SymptomClassifier  # noqa: E402
from backend.app.safety import normalize_text  # noqa: E402


def main() -> None:
    dataset_path = ROOT_DIR / "backend" / "data" / "Symptom2Disease.csv"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    data = pd.read_csv(dataset_path).dropna(subset=["label", "text"]).copy()
    data["text"] = data["text"].astype(str).map(normalize_text)
    data["label"] = data["label"].astype(str).str.strip()

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(data["label"])
    class_count = len(set(y))
    test_size = max(0.2, class_count / max(len(data), 1))
    if test_size >= 0.5:
        raise ValueError(
            "Dataset is too small for a stratified train/test split. Add more samples per class."
        )

    x_train, x_test, y_train, y_test = train_test_split(
        data["text"], y, test_size=test_size, random_state=42, stratify=y
    )

    classifier = SymptomClassifier()
    if not classifier.loaded or classifier.pipeline is None:
        raise FileNotFoundError("Trained model not found. Run train_classifier.py first.")

    probabilities = classifier.pipeline.predict_proba(x_test)
    predictions = classifier.pipeline.predict(x_test)

    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    if len(label_encoder.classes_) >= 3:
        try:
            print(f"Top-3 accuracy: {top_k_accuracy_score(y_test, probabilities, k=3, labels=range(len(label_encoder.classes_))):.4f}")
        except Exception as e:
            pass
            
    print(
        classification_report(
            y_test,
            predictions,
            labels=range(len(label_encoder.classes_)),
            target_names=label_encoder.classes_,
            zero_division=0,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        raise
