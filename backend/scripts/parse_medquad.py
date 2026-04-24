from __future__ import annotations

import sys
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def parse_xml_file(path: Path) -> list[dict[str, str]]:
    """Parse a MedQuAD-style XML file and return a list of Q&A dictionaries."""
    rows: list[dict[str, str]] = []
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Skipping malformed XML: {path}")
        return rows

    for qa in root.findall(".//QAPair"):
        question = (qa.findtext("Question") or "").strip()
        answer = (qa.findtext("Answer") or "").strip()
        focus = (qa.findtext("Focus") or qa.findtext("FocusArea") or "").strip()
        qtype = (qa.findtext("QuestionType") or qa.findtext("QType") or "").strip()

        if not question and not answer:
            continue

        rows.append(
            {
                "question": question,
                "answer": answer,
                "focus": focus,
                "qtype": qtype,
                "source_file": path.name,
            }
        )
    return rows


def parse_csv_file(path: Path) -> list[dict[str, str]]:
    """Parse a CSV file with Q&A data and normalise column names."""
    rows: list[dict[str, str]] = []
    try:
        data = pd.read_csv(path).fillna("")
    except Exception as exc:
        print(f"Skipping unreadable CSV {path}: {exc}")
        return rows

    # Normalise column names to lowercase with underscores
    data.columns = [c.strip().lower().replace(" ", "_") for c in data.columns]

    for _, row in data.iterrows():
        # Support multiple possible column name variants
        question = str(
            row.get("question", row.get("questions", ""))
        ).strip()
        answer = str(
            row.get("answer", row.get("answers", ""))
        ).strip()
        focus = str(
            row.get("focus", row.get("focus_area", row.get("focusarea", "")))
        ).strip()
        qtype = str(
            row.get("qtype", row.get("question_type", row.get("questiontype", "")))
        ).strip()
        source = str(
            row.get("source", row.get("source_file", ""))
        ).strip()

        if not question and not answer:
            continue

        rows.append(
            {
                "question": question,
                "answer": answer,
                "focus": focus,
                "qtype": qtype,
                "source_file": source if source else path.name,
            }
        )
    return rows


def main() -> None:
    medquad_dir = ROOT_DIR / "backend" / "data" / "medquad"
    output_path = ROOT_DIR / "backend" / "data" / "medquad_processed.csv"

    # Collect XML and CSV files from the medquad directory
    files = list(medquad_dir.rglob("*.xml")) + list(medquad_dir.rglob("*.csv"))

    # Also check the root dataset directory for a medquad CSV
    dataset_dir = ROOT_DIR / "dataset"
    if dataset_dir.exists():
        for csv_file in dataset_dir.glob("medquad*.csv"):
            if csv_file not in files:
                files.append(csv_file)

    if not files:
        raise FileNotFoundError(
            f"No XML or CSV files found in {medquad_dir} or {dataset_dir}"
        )

    rows: list[dict[str, str]] = []
    for file_path in files:
        print(f"Parsing: {file_path}")
        if file_path.suffix.lower() == ".xml":
            rows.extend(parse_xml_file(file_path))
        elif file_path.suffix.lower() == ".csv":
            rows.extend(parse_csv_file(file_path))

    dataframe = pd.DataFrame(rows, columns=["question", "answer", "focus", "qtype", "source_file"])
    dataframe = dataframe.fillna("")
    dataframe = dataframe[(dataframe["question"] != "") | (dataframe["answer"] != "")]

    # Deduplicate
    before = len(dataframe)
    dataframe = dataframe.drop_duplicates(subset=["question", "answer"], keep="first")
    after = len(dataframe)
    if before != after:
        print(f"Removed {before - after} duplicate rows.")

    dataframe.to_csv(output_path, index=False)
    print(f"Saved {len(dataframe)} MedQuAD rows to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"MedQuAD parsing failed: {exc}", file=sys.stderr)
        raise
