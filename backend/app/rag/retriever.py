"""
Vector search retriever querying pgvector HNSW index for DocumentChunks.
"""
from typing import Sequence
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rag import DocumentChunk
from app.rag.embedder import BGEM3Embedder

logger = structlog.get_logger(__name__)


class KnowledgeRetriever:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedder = BGEM3Embedder()

    async def search(
        self,
        query: str,
        doc_type: str | None = None,
        top_k: int = 4
    ) -> list[dict]:
        """
        Search document chunks using cosine distance ordering (<-> operator).
        Returns top_k matching document chunks.
        """
        logger.info("rag_search_query", query=query, doc_type=doc_type, top_k=top_k)
        query_vector = await self.embedder.aembed_text(query)
        
        stmt = select(DocumentChunk)
        if doc_type:
            stmt = stmt.where(DocumentChunk.doc_type == doc_type)
            
        # Order by vector distance if pgvector is active
        if hasattr(DocumentChunk.embedding, "l2_distance"):
            stmt = stmt.order_by(DocumentChunk.embedding.l2_distance(query_vector))
        else:
            stmt = stmt.order_by(DocumentChunk.id.desc())
            
        stmt = stmt.limit(top_k)
        result = await self.db.execute(stmt)
        chunks: Sequence[DocumentChunk] = result.scalars().all()

        results = []
        for c in chunks:
            results.append({
                "id": c.id,
                "title": c.title,
                "doc_type": c.doc_type,
                "content": c.content,
                "source_url": c.source_url,
                "metadata": c.metadata_json or {}
            })
        return results
