"""
BGE-M3 Embedder service (1024-dimensional embeddings for agricultural RAG).
"""
import math
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)

EMBEDDING_DIM = 1024


class BGEM3Embedder:
    """Embedder wrapper producing 1024-dimensional vectors."""
    
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model_name
        self._model = None

    def embed_text(self, text: str) -> list[float]:
        """
        Generate 1024-dimensional embedding for text input.
        Uses sentence_transformers if available, otherwise deterministic feature hash embedding.
        """
        try:
            if self._model is None:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            vector = self._model.encode(text).tolist()
            return vector
        except Exception as e:
            logger.warning("bge_m3_fallback_embedding", error=str(e), model=self.model_name)
            # Deterministic 1024-dim fallback embedding vector for offline testing
            text_bytes = text.encode("utf-8")
            vector = []
            for i in range(EMBEDDING_DIM):
                val = math.sin((i + 1) * len(text_bytes) + sum(text_bytes))
                vector.append(round(val, 6))
            return vector

    async def aembed_text(self, text: str) -> list[float]:
        """Async wrapper for embed_text."""
        return self.embed_text(text)
