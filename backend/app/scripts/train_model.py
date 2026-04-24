import os
import pandas as pd
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

def train_model():
    # Setup paths
    base_dir = Path(__file__).resolve().parents[3]
    dataset_path = base_dir / "backend" / "data" / "Symptom2Disease.csv"
    models_dir = base_dir / "backend" / "app" / "models"
    
    # Create models directory if it doesn't exist
    models_dir.mkdir(parents=True, exist_ok=True)

    # Load dataset
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)

    # Prepare data
    X = df["text"].astype(str)
    y_raw = df["label"]

    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    # Create pipeline (Tfidf + LogisticRegression)
    # named_steps['tfidf'] is required by classifier.py
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
        ('clf', LogisticRegression(max_iter=1000))
    ])

    # Train
    print("Training model...")
    pipeline.fit(X, y)

    # Save artifacts
    model_save_path = models_dir / "trained_model.joblib"
    encoder_save_path = models_dir / "label_encoder.joblib"

    joblib.dump(pipeline, model_save_path)
    joblib.dump(label_encoder, encoder_save_path)

    print(f"Model training complete and saved successfully")
    print(f"Artifacts saved to: {models_dir}")

if __name__ == "__main__":
    train_model()
