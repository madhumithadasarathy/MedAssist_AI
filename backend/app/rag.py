from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from .config import get_settings

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover
    faiss = None


@dataclass(slots=True)
class RetrievedDocument:
    question: str
    answer: str
    source: str
    score: float
    focus: str | None = None
    qtype: str | None = None


class MedQuadRetriever:
    def __init__(self, index_dir: Path | None = None) -> None:
        settings = get_settings()
        self.index_dir = index_dir or settings.medquad_index_dir
        self.index = None
        self.metadata: list[dict[str, str]] = []
        self.encoder: SentenceTransformer | None = None
        self.loaded = False
        self.load()

    def load(self) -> None:
        index_file = self.index_dir / "index.faiss"
        metadata_file = self.index_dir / "metadata.json"

        if faiss is None or not index_file.exists() or not metadata_file.exists():
            self.loaded = False
            return

        self.index = faiss.read_index(str(index_file))
        self.metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.encoder = SentenceTransformer(model_name)
        self.loaded = True

    def search(self, query: str, top_k: int = 3) -> list[RetrievedDocument]:
        if not self.loaded or self.index is None or self.encoder is None:
            raise FileNotFoundError(
                "RAG index artifacts were not found. Run backend/scripts/build_vector_index.py first."
            )

        embedding = self.encoder.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(np.asarray(embedding, dtype="float32"), top_k)

        results: list[RetrievedDocument] = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0 or idx >= len(self.metadata):
                continue
            row = self.metadata[idx]
            results.append(
                RetrievedDocument(
                    question=row.get("question", ""),
                    answer=row.get("answer", ""),
                    source=row.get("source", "MedQuAD"),
                    score=round(float(score), 4),
                    focus=row.get("focus") or None,
                    qtype=row.get("qtype") or None,
                )
            )
        return results


def load_processed_medquad(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path).fillna("")
