import os
import sys
import joblib
import pandas as pd
import sklearn
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

def run_retraining():
    """
    Retrains the Symptom Classifier model using the current environment's scikit-learn version.
    Ensures compatibility with HuggingFace Spaces by generating artifacts with sklearn==1.4.2.
    """
    print("========== MEDASSIST AI: MODEL RETRAINING ==========")
    print(f"DEBUG: scikit-learn version: {sklearn.__version__}")
    
    # Setup paths relative to script location
    # Assumes script is at backend/scripts/train_model.py
    ROOT_DIR = Path(__file__).resolve().parents[2]
    DATA_PATH = ROOT_DIR / "backend" / "data" / "Symptom2Disease.csv"
    OUTPUT_DIR = ROOT_DIR / "backend" / "app" / "models"
    
    if not DATA_PATH.exists():
        print(f"ERROR: Dataset not found at {DATA_PATH}")
        sys.exit(1)

    # 1. LOAD DATA
    print(f"DEBUG: Loading dataset from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "label"])
    X = df["text"].astype(str)
    y_raw = df["label"]

    # 2. ENCODE LABELS
    print("DEBUG: Encoding labels...")
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    # 3. BUILD PIPELINE
    print("DEBUG: Building pipeline (TfidfVectorizer + LogisticRegression)...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            lowercase=True, 
            stop_words='english', 
            ngram_range=(1, 2), # Using bigrams for better context
            max_features=5000
        )),
        ('clf', LogisticRegression(
            max_iter=1000, 
            class_weight='balanced', # Important for medical datasets
            C=1.0
        ))
    ])
    
    print(f"DEBUG: Pipeline steps: {pipeline.steps}")

    # 4. TRAIN
    print("DEBUG: Training model... this may take a moment.")
    pipeline.fit(X, y)
    print("✅ Training successfully completed!")

    # 5. HARD VALIDATION (As requested by MLOps best practices)
    print("DEBUG: Running artifact validation...")
    tfidf = pipeline.named_steps["tfidf"]
    assert hasattr(tfidf, "idf_"), "CRITICAL: TF-IDF vectorizer not fitted properly (idf_ missing)"
    print("✅ Validation PASSED: TF-IDF is correctly fitted.")

    # 6. SAVE ARTIFACTS
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model_path = OUTPUT_DIR / "trained_model.joblib"
    encoder_path = OUTPUT_DIR / "label_encoder.joblib"
    
    print(f"DEBUG: Saving artifacts to {OUTPUT_DIR}")
    joblib.dump(pipeline, model_path)
    joblib.dump(label_encoder, encoder_path)
    
    print("====================================================")
    print("🚀 SUCCESS: Compatible model artifacts generated.")
    print(f"Paths:\n - {model_path}\n - {encoder_path}")
    print("====================================================")

if __name__ == "__main__":
    run_retraining()
