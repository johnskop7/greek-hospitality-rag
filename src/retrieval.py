"""Retrieval: embed chunks with e5, store them in a FAISS index, search.

- e5 needs prefixes: chunks are encoded as "passage: ...", questions as "query: ...".
- Embeddings are normalized, so inner product = cosine similarity.
  faiss.IndexFlatIP is an *exact* inner-product search: for ~180 chunks it gives
  the same results as numpy, but it is the standard tool and scales to many
  more documents.
- The index is saved to index/ (ignored by Git) with a meta.json, so notebooks
  and the API load it in seconds instead of re-embedding everything.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import faiss
import numpy as np
import torch
from sentence_transformers import CrossEncoder, SentenceTransformer

from src.config import (CHUNK_SIZE, EMBEDDING_MODEL, INDEX_DIR, N_CANDIDATES,
                        OVERLAP, RERANKER_MODEL)

SearchFn = Callable[[str, int], list[int]]  # (question, k) -> ordered chunk indices


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


class Retriever:
    """e5 embeddings + FAISS index over a list of chunks."""

    def __init__(self, model: SentenceTransformer, index: faiss.Index, chunks: list[dict],
                 model_name: str = EMBEDDING_MODEL):
        self.model = model
        self.index = index
        self.chunks = chunks
        self.model_name = model_name

    # --- building and persistence -------------------------------------------
    @classmethod
    def build(cls, chunks: list[dict], model_name: str = EMBEDDING_MODEL,
              device: str | None = None, batch_size: int = 16) -> "Retriever":
        model = SentenceTransformer(model_name, device=device or get_device())
        passages = ["passage: " + c["text"] for c in chunks]
        embeddings = model.encode(passages, normalize_embeddings=True,
                                  batch_size=batch_size, show_progress_bar=True)
        embeddings = np.asarray(embeddings, dtype="float32")   # FAISS needs float32
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return cls(model, index, chunks, model_name)

    def save(self, index_dir: Path = INDEX_DIR) -> None:
        index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_dir / "chunks.faiss"))
        with open(index_dir / "chunks.json", "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False)
        meta = {
            "embedding_model": self.model_name,
            "chunk_size": CHUNK_SIZE,
            "overlap": OVERLAP,
            "n_chunks": len(self.chunks),
            "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with open(index_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    @classmethod
    def load(cls, index_dir: Path = INDEX_DIR, device: str | None = None) -> "Retriever":
        meta = json.loads((index_dir / "meta.json").read_text(encoding="utf-8"))
        # A stale index silently gives wrong results, so refuse to use one built
        # with different settings than the current config.
        expected = {"embedding_model": EMBEDDING_MODEL, "chunk_size": CHUNK_SIZE,
                    "overlap": OVERLAP}
        stale = {k: (meta.get(k), v) for k, v in expected.items() if meta.get(k) != v}
        if stale:
            raise ValueError(f"Index in {index_dir} is stale (saved, config): {stale}. "
                             "Rebuild it with: python -m src.build_index")
        index = faiss.read_index(str(index_dir / "chunks.faiss"))
        chunks = json.loads((index_dir / "chunks.json").read_text(encoding="utf-8"))
        if index.ntotal != len(chunks):
            raise ValueError("chunks.faiss and chunks.json are out of sync; rebuild the index")
        model = SentenceTransformer(meta["embedding_model"], device=device or get_device())
        return cls(model, index, chunks, meta["embedding_model"])

    # --- search --------------------------------------------------------------
    def search_with_scores(self, question: str, k: int) -> list[tuple[int, float]]:
        """Top-k (chunk index, cosine similarity), most similar first."""
        q = self.model.encode("query: " + question, normalize_embeddings=True)
        q = np.asarray(q, dtype="float32").reshape(1, -1)
        scores, ids = self.index.search(q, min(k, self.index.ntotal))
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]

    def search(self, question: str, k: int) -> list[int]:
        """Top-k chunk indices, most similar first (the SearchFn the evaluator expects)."""
        return [i for i, _ in self.search_with_scores(question, k)]


class Reranker:
    """Cross-encoder that re-scores (question, chunk) pairs read *together*.

    Experiment only: ~4 s per question on a GTX 1650 Ti and far slower on CPU,
    so it is not used in the deployed app.
    """

    def __init__(self, model_name: str = RERANKER_MODEL, device: str | None = None,
                 fp16: bool = True, max_length: int = 512):
        self.device = device or get_device()
        self.model = CrossEncoder(model_name, max_length=max_length, device=self.device)
        if fp16 and self.device == "cuda":
            self.model.model.half()   # ~1.1 GB instead of ~2.3 GB on the GPU

    def rerank(self, question: str, candidates: list[int], chunks: list[dict],
               batch_size: int = 8) -> list[int]:
        pairs = [(question, chunks[i]["text"]) for i in candidates]   # no "query: " prefix
        scores = self.model.predict(pairs, batch_size=batch_size, show_progress_bar=False)
        return [candidates[i] for i in np.argsort(scores)[::-1]]


def make_rerank_search(retriever: Retriever, reranker: Reranker,
                       n_candidates: int = N_CANDIDATES) -> SearchFn:
    """e5 top-n_candidates -> reranker; positions after n_candidates keep e5 order."""
    def search(question: str, k: int) -> list[int]:
        ranked = retriever.search(question, max(k, n_candidates))
        candidates, rest = ranked[:n_candidates], ranked[n_candidates:]
        return (reranker.rerank(question, candidates, retriever.chunks) + rest)[:k]
    return search


def time_search(search: SearchFn, questions: list[str], k: int = 5) -> float:
    """Average seconds per query, after one warm-up call (not counted)."""
    search(questions[0], k)
    sync = torch.cuda.synchronize if torch.cuda.is_available() else (lambda: None)
    sync()
    start = time.perf_counter()
    for q in questions:
        search(q, k)
    sync()   # GPU work is asynchronous: wait for it before stopping the clock
    return (time.perf_counter() - start) / len(questions)
