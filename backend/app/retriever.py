from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from .config import get_settings

try:
    import faiss  # type: ignore
except ImportError:
    faiss = None

# Initialize logger
logger = logging.getLogger(__name__)

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
        self.settings = get_settings()
        # Use settings.faiss_index_path (renamed in config.py) or provided index_dir
        self.index_dir = index_dir or self.settings.faiss_index_path
        self.index = None
        self.metadata: list[dict[str, str]] = []
        self.encoder: SentenceTransformer | None = None
        self.loaded = False
        self.load()

    def load(self) -> None:
        """Load the FAISS index and metadata.json with robust error handling."""
        try:
            # Ensure correct path usage
            index_file = self.index_dir / "index.faiss"
            metadata_file = self.index_dir / "metadata.json"

            if faiss is None:
                logger.error("❌ FAISS library is not installed.")
                self.loaded = False
                return

            if not index_file.exists():
                logger.error(f"❌ FAISS index file not found: {index_file}")
                self.loaded = False
                return

            if not metadata_file.exists():
                logger.error(f"❌ RAG metadata file not found: {metadata_file}")
                self.loaded = False
                return

            # Load FAISS index using faiss.read_index()
            logger.info(f"Loading FAISS index from {index_file}")
            self.index = faiss.read_index(str(index_file))
            
            # Load metadata.json
            logger.info(f"Loading RAG metadata from {metadata_file}")
            self.metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            
            # Initialize the encoder
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            logger.info(f"Initializing SentenceTransformer: {model_name}")
            self.encoder = SentenceTransformer(model_name)
            
            self.loaded = True
            logger.info("✅ RAG LOADED")
        except Exception as e:
            logger.error(f"❌ Failed to load MedQuadRetriever: {str(e)}", exc_info=True)
            self.loaded = False

    def search(self, query: str, top_k: int = 3) -> list[RetrievedDocument]:
        """Perform semantic search against the FAISS index."""
        if not self.loaded or self.index is None or self.encoder is None:
            raise FileNotFoundError(
                "RAG index artifacts were not found or loaded."
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
