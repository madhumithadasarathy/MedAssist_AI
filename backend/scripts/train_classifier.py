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

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(data["label"])
    class_count = len(set(y))
    test_size = max(0.2, class_count / max(len(data), 1))
    if test_size >= 0.5:
        raise ValueError(
            "Dataset is too small for a stratified train/test split. Add more samples per class."
        )

    x_train, x_test, y_train, y_test = train_test_split(
        data["text"],
        y,
        test_size=test_size,
        random_state=42,
        stratify=y,
    )

    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import StratifiedKFold, GridSearchCV

    base_pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            (
                "clf",
                MLPClassifier(
                    hidden_layer_sizes=(128,),
                    max_iter=1000,
                    random_state=42,
                    early_stopping=True,
                ),
            ),
        ]
    )

    param_grid = {
        "tfidf__max_features": [1000],
        "clf__alpha": [0.0001, 0.001],
    }
    
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    grid_search = GridSearchCV(
        base_pipeline, 
        param_grid, 
        cv=cv, 
        scoring="accuracy", 
        n_jobs=-1,
        error_score="raise"
    )
    
    print("Performing hyperparameter tuning on MLPClassifier...")
    grid_search.fit(x_train, y_train)
    
    print(f"Best cross-validation accuracy: {grid_search.best_score_:.4f}")
    
    pipeline = grid_search.best_estimator_

    predictions = pipeline.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(
        y_test,
        predictions,
        target_names=label_encoder.classes_,
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
