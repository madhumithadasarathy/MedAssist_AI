from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    import faiss  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "faiss is required to build the vector index. Install faiss-cpu before running this script."
    ) from exc

from backend.app.config import get_settings  # noqa: E402


def main() -> None:
    settings = get_settings()
    input_path = settings.medquad_processed_path
    output_dir = settings.faiss_index_path

    if not input_path.exists():
        raise FileNotFoundError(
            f"Processed MedQuAD file not found at {input_path}. Run parse_medquad.py first."
        )

    data = pd.read_csv(input_path).fillna("")
    if data.empty:
        raise ValueError("Processed MedQuAD file is empty.")

    search_texts = (
        data["question"].astype(str)
        + " "
        + data["answer"].astype(str)
        + " "
        + data.get("focus", pd.Series([""] * len(data))).astype(str)
    ).tolist()

    encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = encoder.encode(
        search_texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    embeddings = np.asarray(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    output_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(output_dir / "index.faiss"))

    metadata = []
    for _, row in data.iterrows():
        metadata.append(
            {
                "question": str(row.get("question", "")),
                "answer": str(row.get("answer", "")),
                "source": "MedQuAD",
                "focus": str(row.get("focus", "")),
                "qtype": str(row.get("qtype", "")),
                "source_file": str(row.get("source_file", "")),
            }
        )

    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved FAISS index and metadata to {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Vector index build failed: {exc}", file=sys.stderr)
        raise
