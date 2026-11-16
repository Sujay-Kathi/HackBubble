"""
Embedding generator using SentenceTransformer all-MiniLM-L6-v2 (384-dim).
Provides batch embedding with model versioning for pgvector storage.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_VERSION = "1.0"
EMBEDDING_DIM = 384

_model: Any = None
_model_load_failed = False


def _load_model() -> Any:
    """Lazy-load the SentenceTransformer model (singleton)."""
    global _model, _model_load_failed
    if _model is None and not _model_load_failed:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            _model = SentenceTransformer(MODEL_NAME)
            logger.info("Loaded SentenceTransformer model: %s", MODEL_NAME)
        except ImportError:
            logger.warning("sentence_transformers not installed; using zero-vector fallback")
            _model_load_failed = True
        except Exception as exc:  # noqa: BLE001 - degrade instead of failing requests
            logger.warning(
                "Could not load SentenceTransformer model (%s); using deterministic fallback",
                exc,
            )
            _model_load_failed = True
    return _model


def embed_text(text: str) -> list[float]:
    """
    Embed a single text string.
    Returns a 384-dim float list (or zero vector if model unavailable).
    """
    if not text or not text.strip():
        return [0.0] * EMBEDDING_DIM

    model = _load_model()
    if model is None:
        return _deterministic_fallback(text)

    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of texts for efficiency.
    Returns a list of 384-dim float lists.
    """
    if not texts:
        return []

    model = _load_model()
    if model is None:
        return [_deterministic_fallback(t) for t in texts]

    vecs = model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
    return [v.tolist() for v in vecs]


def embed_skills(skills: list[str]) -> list[float]:
    """
    Produce a single embedding for a skills list by joining them.
    """
    text = ", ".join(skills) if skills else ""
    return embed_text(text)


def cosine_similarity_py(a: list[float], b: list[float]) -> float:
    """
    Pure-Python cosine similarity for SQLite test fallback
    (pgvector not available in test mode).
    """
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


def _deterministic_fallback(text: str) -> list[float]:
    """
    Deterministic pseudo-embedding when the model is unavailable.
    Uses SHA-256 hash to seed a stable random vector (unit-normalized).
    NOT semantically meaningful — it keeps the API functional and tests stable
    without the model, but production deployments should provide the real model.
    """
    seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(EMBEDDING_DIM).astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def get_model_version() -> str:
    return MODEL_VERSION
