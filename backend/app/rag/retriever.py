"""
Vector search retriever querying pgvector HNSW index for DocumentChunks.
Provides semantic search with cosine distance, metadata filtering,
similarity scores, and context assembly for LLM grounding.
"""
from typing import Any, Dict, List, Optional, Sequence
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rag import DocumentChunk
from app.rag.embedder import BGEM3Embedder

logger = structlog.get_logger(__name__)


class KnowledgeRetriever:
    """Production vector search retriever against PostgreSQL pgvector."""

    def __init__(self, db: AsyncSession, embedder: Optional[BGEM3Embedder] = None):
        self.db = db
        self.embedder = embedder or BGEM3Embedder()

    async def search(
        self,
        query: str,
        doc_type: Optional[str] = None,
        crop: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Search document chunks using cosine distance (<=> operator).
        Returns top_k matching document chunks with similarity scores.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        logger.info("rag_vector_search_start", query=clean_query, doc_type=doc_type, top_k=top_k)
        query_vector = await self.embedder.aembed_text(clean_query)

        # Build query using cosine distance
        stmt = select(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
        )

        if doc_type:
            stmt = stmt.where(DocumentChunk.doc_type == doc_type)

        stmt = stmt.order_by("distance").limit(top_k)
        result = await self.db.execute(stmt)
        rows = result.all()

        results = []
        for chunk, dist in rows:
            dist_val = float(dist) if dist is not None else 1.0
            similarity = round(max(0.0, 1.0 - dist_val), 4)
            meta = chunk.metadata_json or {}

            # Optional in-memory filter on crop if specified
            if crop and meta.get("crop") and crop.lower() not in meta.get("crop", "").lower():
                continue

            results.append({
                "id": chunk.id,
                "title": chunk.title,
                "doc_type": chunk.doc_type,
                "content": chunk.content,
                "source_url": chunk.source_url,
                "similarity": similarity,
                "distance": round(dist_val, 4),
                "metadata": meta,
            })

        logger.info("rag_vector_search_complete", matches=len(results), top_score=results[0]["similarity"] if results else 0.0)
        return results

    async def get_grounding_context(
        self,
        query: str,
        doc_type: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """
        Retrieves top-k relevant knowledge chunks and compiles a markdown context block
        for direct injection into LLM prompts with source attribution.
        """
        chunks = await self.search(query=query, doc_type=doc_type, top_k=top_k)
        if not chunks:
            return ""

        context_blocks = []
        for idx, c in enumerate(chunks, 1):
            org = c["metadata"].get("organization", "Agricultural Advisory")
            context_blocks.append(
                f"### [Source {idx}]: {c['title']} ({org})\n"
                f"{c['content']}\n"
                f"*Reference: {c['source_url']} (Relevance: {c['similarity']:.2%})*\n"
            )

        return "\n---\n".join(context_blocks)
