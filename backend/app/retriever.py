from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

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
        self.index_dir = index_dir or self.settings.faiss_index_path
        self._index = None
        self._metadata: list[dict[str, str]] = []
        self._encoder = None # Lazy loading
        self.loaded = False
        self.semantic_active = False

    def _ensure_loaded(self) -> None:
        """Lazy loader for RAG metadata and index."""
        if not self.loaded:
            self.load()

    def _get_encoder(self):
        """Lazy loading of SentenceTransformer on CPU."""
        if self._encoder is None:
            try:
                from sentence_transformers import SentenceTransformer
                model_name = "sentence-transformers/all-MiniLM-L6-v2"
                logger.info(f"🤖 Initializing SentenceTransformer (CPU-only lazy load): {model_name}")
                # Explicitly force CPU for HuggingFace Spaces compatibility
                self._encoder = SentenceTransformer(model_name, device="cpu")
            except Exception as e:
                logger.error(f"❌ Failed to lazy-load SentenceTransformer: {e}")
                self.semantic_active = False
                return None
        return self._encoder

    def load(self) -> None:
        """
        Load RAG metadata and FAISS index.
        The transformer model (encoder) is lazy-loaded on first search.
        """
        metadata_file = self.index_dir / "metadata.json"
        index_file = self.index_dir / "index.faiss"

        # 1. LOAD METADATA
        try:
            if metadata_file.exists():
                logger.info(f"📂 Loading RAG metadata from {metadata_file}")
                self._metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
                self.loaded = True 
                logger.info("✅ RAG METADATA LOADED")
            else:
                logger.error(f"❌ RAG metadata file NOT FOUND: {metadata_file}")
                self.loaded = False
                return
        except Exception as e:
            logger.error(f"🔥 Critical error loading RAG metadata: {e}", exc_info=True)
            self.loaded = False
            return

        # 2. LOAD FAISS
        try:
            if faiss is not None and index_file.exists():
                logger.info(f"🔍 Loading FAISS index from {index_file}")
                self._index = faiss.read_index(str(index_file))
                self.semantic_active = True
                logger.info("✅ FAISS INDEX LOADED")
            else:
                logger.warning("⚠️ FAISS index or library missing. Semantic search disabled.")
                self.semantic_active = False
        except Exception as e:
            logger.error(f"⚠️ Could not load FAISS: {e}. Using keyword fallback.", exc_info=True)
            self.semantic_active = False

    def search(self, query: str, top_k: int = 3) -> list[RetrievedDocument]:
        """
        Search for relevant documents. 
        Uses semantic search if available, otherwise falls back to keyword overlap.
        """
        self._ensure_loaded()
        if not self.loaded:
            logger.error("Attempted to search while retriever not loaded.")
            return []

        # Try semantic search if FAISS is active
        if self.semantic_active and self._index is not None:
            encoder = self._get_encoder()
            if encoder is not None:
                try:
                    return self._semantic_search(query, top_k)
                except Exception as e:
                    logger.error(f"Semantic search failed: {e}. Falling back to keywords.", exc_info=True)
        
        return self._keyword_fallback_search(query, top_k)

    def _semantic_search(self, query: str, top_k: int = 3) -> list[RetrievedDocument]:
        """Perform semantic search using FAISS and lazy-loaded BERT embeddings."""
        encoder = self._get_encoder()
        if encoder is None or self._index is None:
            raise RuntimeError("Required semantic components are missing.")
            
        embedding = encoder.encode([query], normalize_embeddings=True)
        scores, indices = self._index.search(np.asarray(embedding, dtype="float32"), top_k)

        results: list[RetrievedDocument] = []
        for score, idx in zip(scores[0], indices[0], strict=False):
            if idx < 0 or idx >= len(self._metadata):
                continue
            row = self._metadata[idx]
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

    def _keyword_fallback_search(self, query: str, top_k: int = 3) -> list[RetrievedDocument]:
        """
        Perform a simple keyword overlap search over question and focus fields.
        """
        logger.info(f"⚙️ Running keyword fallback search for: '{query}'")
        query_terms = set(re.findall(r'\w+', query.lower()))
        if not query_terms:
            return []

        scored_results = []
        for row in self._metadata:
            text_to_match = f"{row.get('question', '')} {row.get('focus', '')} {row.get('answer', '')[:200]}".lower()
            match_count = sum(1 for term in query_terms if term in text_to_match)
            
            if match_count > 0:
                score = match_count / len(query_terms)
                scored_results.append((score, row))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        results: list[RetrievedDocument] = []
        for score, row in scored_results[:top_k]:
            results.append(
                RetrievedDocument(
                    question=row.get("question", ""),
                    answer=row.get("answer", ""),
                    source=row.get("source", "MedQuAD (Fallback)"),
                    score=round(float(score), 4),
                    focus=row.get("focus") or None,
                    qtype=row.get("qtype") or None,
                )
            )
        return results
