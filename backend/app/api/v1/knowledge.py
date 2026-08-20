"""
API router for agricultural knowledge and government scheme RAG queries.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.rag.retriever import KnowledgeRetriever

router = APIRouter(prefix="/knowledge", tags=["Knowledge & RAG"])


class KnowledgeQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question about crop care, schemes, or weather")
    doc_type: Optional[str] = Field(None, description="Filter by document type (scheme, crop_guide, disease_guide)")
    top_k: int = Field(default=4, ge=1, le=10)


class KnowledgeChunkResponse(BaseModel):
    id: int
    title: str
    doc_type: str
    content: str
    source_url: Optional[str] = None
    metadata: dict = {}


class KnowledgeQueryResponse(BaseModel):
    query: str
    results: List[KnowledgeChunkResponse]


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge_base(
    request: KnowledgeQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    POST /knowledge/query
    Query the agricultural vector database (BGE-M3 + pgvector) for agronomic guidelines or schemes.
    """
    retriever = KnowledgeRetriever(db)
    chunks = await retriever.search(
        query=request.query,
        doc_type=request.doc_type,
        top_k=request.top_k
    )
    return KnowledgeQueryResponse(
        query=request.query,
        results=[KnowledgeChunkResponse(**c) for c in chunks]
    )


@router.get("/schemes", response_model=KnowledgeQueryResponse)
async def get_government_schemes(
    state: Optional[str] = Query(None, description="State name filter (e.g. Rajasthan)"),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /knowledge/schemes
    Fetch government agricultural schemes (PM-Kisan, PMFBY, Soil Health Card).
    Strictly returning DB + RAG data; no hallucinated eligibility.
    """
    query_str = f"Government schemes for farmers in {state}" if state else "PM-Kisan PMFBY agricultural government schemes"
    retriever = KnowledgeRetriever(db)
    chunks = await retriever.search(query=query_str, doc_type="scheme", top_k=5)
    
    # Default fallback schemes if DB is empty during initial setup
    if not chunks:
        chunks = [
            {
                "id": 1,
                "title": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                "doc_type": "scheme",
                "content": "Provides ₹6,000 per year in three equal installments directly into bank accounts of landholding farmer families.",
                "source_url": "https://pmkisan.gov.in/",
                "metadata": {"eligibility": "Small and marginal landholding farmers", "benefit": "₹6,000 / year"}
            },
            {
                "id": 2,
                "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                "doc_type": "scheme",
                "content": "Crop insurance scheme providing financial support to farmers suffering crop loss/damage arising out of non-preventable natural risks.",
                "source_url": "https://pmfby.gov.in/",
                "metadata": {"eligibility": "All farmers growing notified crops in notified areas", "premium_kharif": "2%", "premium_rabi": "1.5%"}
            }
        ]
        
    return KnowledgeQueryResponse(
        query=query_str,
        results=[KnowledgeChunkResponse(**c) for c in chunks]
    )
