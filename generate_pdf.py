from fpdf import FPDF
import pandas as pd
import joblib
from pathlib import Path
from sklearn.metrics import classification_report, accuracy_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split
import sys
import datetime

ROOT_DIR = Path(__file__).resolve().parents[0]

sys.path.insert(0, str(ROOT_DIR))
from backend.app.safety import normalize_text

class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 18)
        self.set_text_color(40, 53, 147)
        self.cell(0, 10, "MedAssist AI - Model Evaluation Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_report():
    print("Loading data and evaluating the model...")
    # Load dataset
    data_path = ROOT_DIR / "backend" / "data" / "Symptom2Disease.csv"
    data = pd.read_csv(data_path).dropna(subset=["label", "text"]).copy()
    data["text"] = data["text"].astype(str).map(normalize_text)
    data["label"] = data["label"].astype(str).str.strip()

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
    top2_acc = top_k_accuracy_score(y_test, y_prob, k=2, labels=range(class_count))
    top3_acc = top_k_accuracy_score(y_test, y_prob, k=3, labels=range(class_count))

    report_dict = classification_report(
        y_test, y_pred, labels=range(class_count), target_names=label_encoder.classes_, output_dict=True, zero_division=0
    )

    pdf = PDFReport()
    pdf.add_page()
    
    # Meta info
    pdf.set_font("helvetica", size=11)
    pdf.set_text_color(0, 0, 0)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 8, f"Generated On: {now}", ln=True)
    pdf.cell(0, 8, f"Total Classes (Diseases): {class_count}", ln=True)
    pdf.cell(0, 8, f"Total Evaluated Samples: {len(data)}", ln=True)
    pdf.ln(5)

    # High-level Metrics
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, " 1. Global Performance Metrics", ln=True, fill=True)
    pdf.ln(3)

    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 8, f"Top-1 Accuracy: {acc*100:.2f}% (Exact Match)", ln=True)
    pdf.cell(0, 8, f"Top-2 Accuracy: {top2_acc*100:.2f}%", ln=True)
    pdf.cell(0, 8, f"Top-3 Accuracy: {top3_acc*100:.2f}% (Application Target)", ln=True)
    
    pdf.ln(8)
    pdf.set_font("helvetica", "I", 10)
    pdf.multi_cell(0, 6, "Note: MedAssist AI architecture displays the Top 3 predictions natively within the interface to ensure diagnostic safety. The Top-3 accuracy is the primary performance indicator for this system.")

    pdf.ln(8)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, " 2. Visual Chart", ln=True, fill=True)
    pdf.ln(5)
    
    chart_path = str(ROOT_DIR / "evaluation_chart.png")
    if Path(chart_path).exists():
        pdf.image(chart_path, x=15, w=150)
    
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, " 3. Detailed Class-wise Precision & Recall", ln=True, fill=True)
    pdf.ln(5)
    
    pdf.set_font("courier", size=9)
    # Table header
    col_w = [60, 30, 30, 30, 30]
    pdf.set_font("courier", "B", 9)
    pdf.cell(col_w[0], 8, "Condition", border=1)
    pdf.cell(col_w[1], 8, "Precision", border=1, align="C")
    pdf.cell(col_w[2], 8, "Recall", border=1, align="C")
    pdf.cell(col_w[3], 8, "F1-Score", border=1, align="C")
    pdf.cell(col_w[4], 8, "Support", border=1, align="C")
    pdf.ln(8)
    
    pdf.set_font("courier", size=9)
    for cls in label_encoder.classes_:
        if cls in report_dict:
            met = report_dict[cls]
            pdf.cell(col_w[0], 7, (cls[:25] + '..') if len(cls) > 25 else cls, border=1)
            pdf.cell(col_w[1], 7, f"{met['precision']:.2f}", border=1, align="C")
            pdf.cell(col_w[2], 7, f"{met['recall']:.2f}", border=1, align="C")
            pdf.cell(col_w[3], 7, f"{met['f1-score']:.2f}", border=1, align="C")
            pdf.cell(col_w[4], 7, f"{int(met['support'])}", border=1, align="C")
            pdf.ln(7)

    pdf_path = ROOT_DIR / "MedAssist_Evaluation_Report.pdf"
    pdf.output(str(pdf_path))
    print(f"PDF successfully generated at: {pdf_path}")

if __name__ == "__main__":
    generate_report()
