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
import sys
import warnings

# Suppress unimportant warnings for clean logs
warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "backend" / "data"
MODELS_DIR = ROOT_DIR / "backend" / "app" / "models"

# -----------------------------------------
# STEP 1: LOAD DATA
# -----------------------------------------
def load_data():
    """Load both datasets, drop nulls, lowercase text, and validate."""
    symp_path = DATA_DIR / "Symptom2Disease.csv"
    medquad_path = DATA_DIR / "medquad_processed.csv"

    if not symp_path.exists() or not medquad_path.exists():
        raise FileNotFoundError("Missing datasets in backend/data directory.")

    df_symp = pd.read_csv(symp_path).dropna(subset=["text", "label"])
    df_symp["text"] = df_symp["text"].astype(str).str.lower().str.strip()
    df_symp["label"] = df_symp["label"].astype(str).str.strip()

    df_medquad = pd.read_csv(medquad_path)
    # The actual column name in medquad might be 'focus_area' instead of 'focus'
    if 'focus_area' in df_medquad.columns:
        df_medquad = df_medquad.rename(columns={'focus_area': 'focus'})
        
    df_medquad = df_medquad.dropna(subset=["question", "answer", "focus"])
    df_medquad["question"] = df_medquad["question"].astype(str).str.lower()
    df_medquad["answer"] = df_medquad["answer"].astype(str).str.lower()
    df_medquad["focus"] = df_medquad["focus"].astype(str).str.strip()

    return df_symp, df_medquad


# -----------------------------------------
# STEP 2 & 5: DATA AUGMENTATION
# -----------------------------------------

TEMPLATES = [
    "i have {}",
    "i am experiencing {}",
    "symptoms include {}",
    "i am suffering from {}",
    "for the past few days, i have {}",
    "lately i feel {}",
    "my main issues are {}"
]

SYNONYMS = {
    "fever": ["high temperature", "running a temperature"],
    "headache": ["head pain", "migraine", "throbbing head"],
    "stomach pain": ["abdominal pain", "tummy ache", "stomach cramps"],
    "tired": ["fatigue", "exhausted", "lethargic"],
    "cough": ["hacking cough", "persistent cough"],
    "runny nose": ["nasal congestion", "stuffy nose"],
    "nausea": ["feeling sick", "want to vomit"]
}

def apply_synonyms(text):
    for word, syns in SYNONYMS.items():
        if word in text:
            text = text.replace(word, random.choice(syns))
    return text

def shuffle_symptoms(text):
    parts = [p.strip() for p in re.split(r',| and ', text) if p.strip()]
    if len(parts) > 1:
        random.shuffle(parts)
        return " and ".join(parts)
    return text

def generate_variations(text, num_variations=5):
    variations = set([text])
    
    for _ in range(num_variations * 2): # Try generating safely
        if len(variations) >= num_variations:
            break
            
        choice = random.randint(1, 3)
        new_text = text
        
        if choice == 1:
            new_text = random.choice(TEMPLATES).format(new_text)
        elif choice == 2:
            new_text = shuffle_symptoms(new_text)
        elif choice == 3:
            new_text = apply_synonyms(new_text)
            
        # Clean double spaces
        new_text = re.sub(r'\s+', ' ', new_text).strip()
        
        if new_text and new_text != "{}":
            variations.add(new_text)
            
    return list(variations)

def augment_data(df, target_samples_per_class=50):
    """Identify imbalanced classes and generate augmented rows."""
    counts = df["label"].value_axis = df["label"].value_counts()
    
    augmented_rows = []
    
    for label, count in counts.items():
        class_subset = df[df["label"] == label]["text"].tolist()
        
        # Decide how many variations to generate per text (heavier augmentation if minority class)
        variations_per_text = 5
        if count < target_samples_per_class:
            variations_per_text = 10 
            
        for text in class_subset:
            new_texts = generate_variations(text, num_variations=variations_per_text)
            for nt in new_texts:
                augmented_rows.append({"label": label, "text": nt})
                
    aug_df = pd.DataFrame(augmented_rows)
    return pd.concat([df, aug_df])


# -----------------------------------------
# STEP 3: MEDQUAD → TRAINING DATA
# -----------------------------------------
def convert_medquad(df_medquad):
    """Extract symptom answers connected to disease focuses."""
    mq_rows = []
    
    for _, row in df_medquad.iterrows():
        question = row["question"]
        answer = row["answer"]
        focus = row["focus"]
        
        # If question is asking about symptoms
        if "symptom" in question or "sign" in question:
            # Clean and translate the answer to an input-like sentence
            cleaned_ans = answer.replace(".", ",").strip()
            # Remove giant paragraph citations if they exist
            cleaned_ans = re.sub(r'\[.*?\]', '', cleaned_ans)
            
            # Splitting long paragraphs into manageable sentence chunks safely
            sentences = [s.strip() for s in cleaned_ans.split(',') if len(s.split()) > 2 and len(s.split()) < 20]
            
            for sentence in sentences:
                mq_rows.append({
                    "text": random.choice(TEMPLATES).format(sentence),
                    "label": focus.title()
                })
                
    return pd.DataFrame(mq_rows)


# -----------------------------------------
# STEP 4: MERGE DATASETS
# -----------------------------------------
def create_expanded_dataset():
    print("Step 1: Loading Original Datasets...")
    df_symp, df_medquad = load_data()
    orig_length = len(df_symp)
    print(f" -> Found {orig_length} original samples.")
    
    print("Step 2 & 5: Heavily Augmenting Original Symptom Data (Handling Imbalances)...")
    df_symp_aug = augment_data(df_symp, target_samples_per_class=50)
    
    print("Step 3: Extracting Conversational Sentences from MedQuAD...")
    df_mq = convert_medquad(df_medquad)
    
    print("Step 4: Merging and Deduplicating...")
    df_final = pd.concat([df_symp_aug, df_mq]).drop_duplicates(subset=["text"])
    
    # Capitalize labels uniformly
    df_final["label"] = df_final["label"].str.title()
    
    # Filter out rare classes (less than 5 samples) to ensure Stratified splits don't fail
    label_counts = df_final["label"].value_counts()
    valid_labels = label_counts[label_counts >= 5].index
    df_final = df_final[df_final["label"].isin(valid_labels)]
    
    # Save the expanded dataset
    expanded_path = DATA_DIR / "expanded_dataset.csv"
    df_final.to_csv(expanded_path, index=False)
    
    print(f" -> Expanded dataset significantly to {len(df_final)} samples. Saved to {expanded_path.name}")
    return df_final, orig_length


# -----------------------------------------
# STEP 6-8: TRAINING PIPELINE & UPGRADES
# -----------------------------------------
def train_and_evaluate(df):
    print("Step 6: Optimizing Feature Engineering...")
    label_encoder = LabelEncoder()
    X = df["text"]
    y = label_encoder.fit_transform(df["label"])
    
    # Extract Vectorizer (Using unigrams, bigrams, and trigrams)
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=8000,
        stop_words='english'
    )
    X_vec = vectorizer.fit_transform(X)
    
    # Establish CV Split
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    test_idx = list(cv.split(X_vec, y))[0][1]
    train_idx = list(cv.split(X_vec, y))[0][0]
    
    X_train, X_test = X_vec[train_idx], X_vec[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    num_classes = len(label_encoder.classes_)
    
    print("Step 7 & 8: Benchmarking Upgraded Models...")
    
    # Define Models
    models = {
        "LogisticRegression (Balanced)": LogisticRegression(class_weight='balanced', max_iter=2000, C=1.0),
        "LinearSVC (Calibrated)": CalibratedClassifierCV(LinearSVC(class_weight='balanced', max_iter=2000, C=0.5))
    }
    
    best_model = None
    best_acc = 0
    best_name = ""
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        top3 = top_k_accuracy_score(y_test, y_prob, k=3, labels=range(num_classes))
        
        print(f"\n--- {name} ---")
        print(f"Top-1 Accuracy: {acc*100:.2f}%")
        print(f"Top-3 Accuracy: {top3*100:.2f}%")
        
        if acc > best_acc:
            best_acc = acc
            best_model = model
            best_name = name
            
    print(f"\nWinner Selected: {best_name}")
    
    # Step 9: Save Models
    print("Step 9: Saving Trained Pipeline Outputs...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build complete sklearn pipeline with winner inside to avoid manual transform step later
    from sklearn.pipeline import Pipeline
    full_pipeline = Pipeline([
        ('tfidf', vectorizer),
        ('clf', best_model)
    ])
    
    # We must refit the exact pipeline locally just to save it correctly mapped 
    # (Since we trained on vectorized subset matrices above)
    full_pipeline.fit(X.iloc[train_idx], y_train)
    
    joblib.dump(full_pipeline, MODELS_DIR / "symptom_classifier.joblib")
    joblib.dump(label_encoder, MODELS_DIR / "label_encoder.joblib")
    joblib.dump(vectorizer, MODELS_DIR / "vectorizer.joblib")
    
    print(f"Artifacts saved in {MODELS_DIR}!")
    
    return label_encoder, best_name, acc, len(np.unique(y_test))

# -----------------------------------------
# STEP 11: MAIN RUNNER
# -----------------------------------------
def main():
    print("========== MEDASSIST AI - ML ENHANCEMENT PIPELINE ==========")
    df_expanded, orig_size = create_expanded_dataset()
    
    label_encoder, best_model, acc, num_classes = train_and_evaluate(df_expanded)
    
    print("\n========== FINAL PIPELINE SUMMARY ==========")
    print(f"Original Dataset Size:   {orig_size}")
    print(f"Final Dataset Size:      {len(df_expanded)}")
    print(f"Total Unique Diseases:   {len(label_encoder.classes_)}")
    print(f"Winning ML Algorithm:    {best_model}")
    print("============================================================")

if __name__ == "__main__":
    main()
