"""Local, reusable sentence-transformer embeddings for monitoring events."""

from __future__ import annotations

from functools import lru_cache

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


class EmbeddingService:
    """Loads the embedding model lazily and keeps one instance per process."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover
                message = "sentence-transformers is required for semantic search."
                raise RuntimeError(message) from exc
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """Return a normalized 384-dimensional vector as native Python floats."""
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Text to embed must not be empty.")
        vector = self._get_model().encode(cleaned, normalize_embeddings=True)
        result = [float(value) for value in vector.tolist()]
        if len(result) != EMBEDDING_DIMENSION:
            raise RuntimeError(f"Expected {EMBEDDING_DIMENSION} dimensions, got {len(result)}.")
        return result


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Application-wide embedding service singleton."""
    return EmbeddingService()
