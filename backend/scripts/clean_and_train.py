import pandas as pd
import numpy as np
import random
import re
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, top_k_accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import resample
import warnings

warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "backend" / "data"
MODELS_DIR = ROOT_DIR / "backend" / "app" / "models"

# -----------------------------------------
# STEP 1: LOAD & CLEAN DATA
# -----------------------------------------
def load_and_clean_data():
    symp_path = DATA_DIR / "Symptom2Disease.csv"
    medquad_path = DATA_DIR / "medquad_processed.csv"

    if not symp_path.exists() or not medquad_path.exists():
        raise FileNotFoundError("Datasets not found in backend/data/")

    df_symp = pd.read_csv(symp_path).dropna(subset=["text", "label"])
    df_symp["text"] = df_symp["text"].astype(str).str.lower().str.strip()
    df_symp["label"] = df_symp["label"].astype(str).str.lower().str.strip()

    df_medquad = pd.read_csv(medquad_path)
    if 'focus_area' in df_medquad.columns:
        df_medquad = df_medquad.rename(columns={'focus_area': 'focus'})
        
    df_medquad = df_medquad.dropna(subset=["question", "answer", "focus"])
    df_medquad["question"] = df_medquad["question"].astype(str).str.lower().str.strip()
    df_medquad["answer"] = df_medquad["answer"].astype(str).str.lower().str.strip()
    df_medquad["focus"] = df_medquad["focus"].astype(str).str.lower().str.strip()

    return df_symp, df_medquad

# -----------------------------------------
# STEP 2 & 4: LABELS & MAPPING
# -----------------------------------------
def get_label_mapping(allowed_labels):
    """Provides a loose mapping to align MedQuAD medical focuses to Symptom2Disease labels."""
    mapping = {
        "type 2 diabetes mellitus": "diabetes",
        "type 1 diabetes mellitus": "diabetes",
        "influenza virus infection": "influenza",
        "hypertensive disease": "hypertension",
        "high blood pressure": "hypertension",
        "myocardial infarction": "heart attack",
        "urinary tract infections": "urinary tract infection",
        "asthma in children": "asthma",
        "migraine disorders": "migraine",
        "allergic rhinitis": "allergic rhinitis",
        "depressive disorder": "depression",
        "tuberculosis": "tuberculosis",
        "gout": "gout",
        "psoriasis": "psoriasis",
        "chickenpox": "chickenpox",
    }
    
    # ensure everything maps to a strictly allowed label
    valid_mapping = {}
    for k, v in mapping.items():
        if v in allowed_labels:
            valid_mapping[k] = v
            
    # Identity mapping for exact matches natively in medquad
    for label in allowed_labels:
        valid_mapping[label] = label
        
    return valid_mapping

# -----------------------------------------
# STEP 3 & 5: FILTER MEDQUAD
# -----------------------------------------
TEMPLATES = [
    "i have {}",
    "i am experiencing {}",
    "symptoms include {}",
    "for the past few days, i have {}"
]

def process_medquad(df_medquad, allowed_labels):
    mapping = get_label_mapping(allowed_labels)
    mq_rows = []
    
    for _, row in df_medquad.iterrows():
        question = row["question"]
        answer = row["answer"]
        focus = row["focus"]
        
        if "symptom" in question or "sign" in question:
            # Check mapping
            if focus in mapping:
                target_label = mapping[focus]
                
                # Minimum viable answer length
                if len(answer.split()) < 5:
                    continue
                
                # Light cleanup
                ans_clean = answer.replace(".", ",").strip()
                ans_clean = re.sub(r'\[.*?\]', '', ans_clean)
                
                # Split large paragraphs
                chunks = [c.strip() for c in ans_clean.split(',') if 5 <= len(c.split()) <= 20]
                
                for chunk in chunks:
                    mq_rows.append({
                        "label": target_label,
                        "text": random.choice(TEMPLATES).format(chunk)
                    })
                    
    return pd.DataFrame(mq_rows)

# -----------------------------------------
# STEP 6: CLEAN DATA AUGMENTATION
# -----------------------------------------
SYNONYMS = {
    "fever": "high temperature",
    "headache": "head pain",
    "stomach pain": "abdominal pain",
    "tired": "fatigue",
    "coughing": "cough",
    "runny nose": "stuffy nose"
}

def clean_augment(text):
    variations = set([text])
    
    # Variation 1: Synonym replacement
    syn_text = text
    for w, r in SYNONYMS.items():
        if w in syn_text:
            syn_text = syn_text.replace(w, r)
    variations.add(syn_text)
    
    # Variation 2: Template prefix
    variations.add(random.choice(TEMPLATES).format(text))
    
    # Variation 3: Reordering and/or
    parts = [p.strip() for p in re.split(r'\s+and\s+|,', text) if p.strip()]
    if len(parts) > 1:
        random.shuffle(parts)
        variations.add(" and ".join(parts))
        
    return list(variations)

def augment_symptom_data(df_symp):
    rows = []
    for _, row in df_symp.iterrows():
        vars = clean_augment(row["text"])
        for v in vars:
            rows.append({"label": row["label"], "text": v.strip()})
    return pd.DataFrame(rows).drop_duplicates()

# -----------------------------------------
# STEP 7 & 8: MERGE & BALANCE
# -----------------------------------------
def create_balanced_dataset():
    df_symp, df_medquad = load_and_clean_data()
    orig_size = len(df_symp)
    
    allowed_labels = set(df_symp["label"].unique())
    
    df_mq_clean = process_medquad(df_medquad, allowed_labels)
    df_symp_aug = augment_symptom_data(df_symp)
    
    # Combine and drop duplicates
    df_merged = pd.concat([df_symp, df_symp_aug, df_mq_clean], ignore_index=True)
    df_merged = df_merged.drop_duplicates(subset=["text"])
    
    # Enforce exactly 100 samples per class
    target_count = 100
    balanced_rows = []
    
    for label in allowed_labels:
        subset = df_merged[df_merged["label"] == label]
        
        if len(subset) == 0:
            continue
            
        if len(subset) >= target_count:
            # Downsample
            resampled = resample(subset, replace=False, n_samples=target_count, random_state=42)
        else:
            # Oversample (with replacement)
            resampled = resample(subset, replace=True, n_samples=target_count, random_state=42)
            
        balanced_rows.append(resampled)
        
    df_final = pd.concat(balanced_rows, ignore_index=True)
    
    # Shuffle dataset
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Format labels properly
    df_final["label"] = df_final["label"].str.title()
    
    df_final.to_csv(DATA_DIR / "cleaned_dataset.csv", index=False)
    
    return df_final, orig_size, allowed_labels

# -----------------------------------------
# STEP 9-13: TRAIN & EVALUATE
# -----------------------------------------
def evaluate_framework(df_final):
    # Setup mapping
    label_encoder = LabelEncoder()
    X = df_final["text"]
    y = label_encoder.fit_transform(df_final["label"])
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=8000,
        stop_words='english'
    )
    X_vec = vectorizer.fit_transform(X)
    
    # Split
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    train_idx, test_idx = list(cv.split(X_vec, y))[0]
    
    X_train, X_test = X_vec[train_idx], X_vec[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    num_classes = len(label_encoder.classes_)
    
    models = {
        "LogisticRegression": LogisticRegression(class_weight='balanced', max_iter=2000),
        "LinearSVC": CalibratedClassifierCV(LinearSVC(class_weight='balanced', max_iter=2000))
    }
    
    best_top3 = 0
    best_model = None
    best_name = ""
    
    results = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        top3 = top_k_accuracy_score(y_test, y_prob, k=3, labels=range(num_classes))
        
        results[name] = {"top1": acc, "top3": top3}
        
        if top3 > best_top3:
            best_top3 = top3
            best_model = model
            best_name = name
            
    # Compile entire optimized pipeline and retrain
    from sklearn.pipeline import Pipeline
    full_pipeline = Pipeline([('tfidf', vectorizer), ('clf', best_model)])
    full_pipeline.fit(X.iloc[train_idx], y_train)
    
    # Save artifacts
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(full_pipeline, MODELS_DIR / "trained_model.joblib")
    joblib.dump(vectorizer, MODELS_DIR / "vectorizer.joblib")
    joblib.dump(label_encoder, MODELS_DIR / "label_encoder.joblib")

    return results, best_name

# -----------------------------------------
# STEP 14: SUMMARY
# -----------------------------------------
def main():
    print("========== DATASET CLEANING & OPTIMIZATION ==========")
    df_final, orig_size, allowed_labels = create_balanced_dataset()
    
    print("\n========== MODEL TRAINING & EVALUATION ==========")
    results, best_model_name = evaluate_framework(df_final)
    
    print("\n========== FINAL SUMMARY ==========")
    print(f"Total Unique Labels (Diseases):  {len(allowed_labels)}")
    print(f"Original Dataset Size:           {orig_size}")
    print(f"Cleaned Dataset Size:            {len(df_final)}")
    print("Class Distribution Target:       Strict 100 samples per class\n")
    
    print("--- Model Benchmarks ---")
    for name, mets in results.items():
        print(f"Model: {name}")
        print(f" - Top-1 Accuracy: {mets['top1']*100:.2f}%")
        print(f" - Top-3 Accuracy: {mets['top3']*100:.2f}%")
        
    print(f"\nWinning Model Selected: {best_model_name}")
    print("Saved Outputs: cleaned_dataset.csv, trained_model.joblib, vectorizer.joblib")

if __name__ == "__main__":
    main()
