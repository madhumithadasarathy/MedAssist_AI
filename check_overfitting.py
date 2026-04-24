import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from backend.app.safety import normalize_text

import joblib

data = pd.read_csv("backend/data/Symptom2Disease.csv").dropna(subset=["label", "text"])
data["text"] = data["text"].astype(str).map(normalize_text)
data["label"] = data["label"].astype(str).str.strip()

label_encoder = joblib.load("backend/app/models/label_encoder.joblib")
y = label_encoder.transform(data["label"])

class_count = len(set(y))
test_size = max(0.2, class_count / max(len(data), 1))

x_train, x_test, y_train, y_test = train_test_split(
    data["text"], y, test_size=test_size, random_state=42, stratify=y
)

pipeline = joblib.load("backend/app/models/symptom_classifier.joblib")

# Metrics
y_train_pred = pipeline.predict(x_train)
y_test_pred = pipeline.predict(x_test)
train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_test_pred)

cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
cv_scores = cross_val_score(pipeline, data["text"], y, cv=cv, scoring="accuracy")

test_probs = pipeline.predict_proba(x_test)
top2_acc = top_k_accuracy_score(y_test, test_probs, k=2, labels=range(len(label_encoder.classes_)))
top3_acc = top_k_accuracy_score(y_test, test_probs, k=3, labels=range(len(label_encoder.classes_)))

print("--- EVALUATION METRICS ---")
print(f"Training Accuracy: {train_acc:.4f}")
print(f"Testing Accuracy:  {test_acc:.4f}")
print(f"Overfitting Gap:   {(train_acc - test_acc):.4f}")
print(f"Mean CV Accuracy:  {cv_scores.mean():.4f}")
print("---")
print(f"Top-1 Accuracy:    {test_acc:.4f}")
print(f"Top-2 Accuracy:    {top2_acc:.4f}")
print(f"Top-3 Accuracy:    {top3_acc:.4f}")
