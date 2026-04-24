import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import confusion_matrix, accuracy_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split
import sys

# Ensure backend module is available
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.safety import normalize_text

def main():
    # Load data
    data_path = ROOT_DIR / "backend" / "data" / "Symptom2Disease.csv"
    data = pd.read_csv(data_path).dropna(subset=["label", "text"]).copy()
    data["text"] = data["text"].astype(str).map(normalize_text)
    data["label"] = data["label"].astype(str).str.strip()
    
    # Filter to match training logic so transform doesn't fail on unseen labels
    class_counts = data["label"].value_counts()
    valid_classes = class_counts[class_counts >= 2].index
    data = data[data["label"].isin(valid_classes)].copy()

    # Load model and encoder
    model_path = ROOT_DIR / "backend" / "app" / "models" / "symptom_classifier.joblib"
    encoder_path = ROOT_DIR / "backend" / "app" / "models" / "label_encoder.joblib"
    pipeline = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)

    y = label_encoder.transform(data["label"])
    class_count = len(set(y))
    test_size = max(0.2, class_count / max(len(data), 1))

    _, x_test, _, y_test = train_test_split(
        data["text"], y, test_size=test_size, random_state=42, stratify=y
    )

    y_pred = pipeline.predict(x_test)
    y_prob = pipeline.predict_proba(x_test)

    acc = accuracy_score(y_test, y_pred)
    top3_acc = top_k_accuracy_score(y_test, y_prob, k=3, labels=range(class_count))

    metrics = {
        'Top 1 Classification': acc * 100,
        'Top 3 Classification': top3_acc * 100
    }

    # Plot Bar Chart
    plt.figure(figsize=(8, 5))
    colors = ['#1f77b4', '#2ca02c']
    bars = plt.bar(metrics.keys(), metrics.values(), color=colors, width=0.5)
    
    plt.title('MedAssist AI - Evaluation Accuracy Metrics', fontsize=16, fontweight='bold', pad=15)
    plt.ylabel('Accuracy (%)', fontsize=12, labelpad=10)
    plt.ylim(0, 110)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 2,
                 f'{height:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout()
    chart_path = ROOT_DIR / "evaluation_chart.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {chart_path}")

if __name__ == "__main__":
    main()
