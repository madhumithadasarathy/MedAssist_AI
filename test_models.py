import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from backend.app.safety import normalize_text

data = pd.read_csv("backend/data/Symptom2Disease.csv").dropna(subset=["label", "text"])
data["text"] = data["text"].astype(str).map(normalize_text)
data["label"] = data["label"].astype(str).str.strip()

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(data["label"])
class_count = len(set(y))
test_size = max(0.2, class_count / max(len(data), 1))

x_train, x_test, y_train, y_test = train_test_split(
    data["text"], y, test_size=test_size, random_state=42, stratify=y
)

models = {
    "LogisticRegression": LogisticRegression(max_iter=2500, class_weight="balanced", C=1.0),
    "SVC Linear": SVC(kernel="linear", probability=True, class_weight="balanced", C=1.0),
    "MLP": MLPClassifier(hidden_layer_sizes=(128,), max_iter=1000, random_state=42)
}

for name, clf in models.items():
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
        ("clf", clf)
    ])
    pipeline.fit(x_train, y_train)
    test_acc = accuracy_score(y_test, pipeline.predict(x_test))
    print(f"{name} Testing Accuracy: {test_acc:.4f}")
