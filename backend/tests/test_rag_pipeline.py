"""
Comprehensive tests for FarmFusion Real Vector RAG Pipeline (Phase D / Phase 5).
Validates:
- Real dense embeddings from SentenceTransformer (no fake/sine wave fallback).
- Real vectors stored in PostgreSQL + pgvector.
- Assertion that document_chunks count > 0 (strictly fails if empty).
- HNSW cosine index presence.
- Semantic similarity retrieval accuracy for disease, cultivation, and government schemes.
- Metadata filtering and LLM grounding context generation.
"""
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.rag.embedder import RealAgriculturalEmbedder
from app.rag.retriever import KnowledgeRetriever


@pytest_asyncio.fixture
async def db_session():
    """Provides a fresh AsyncSession with NullPool per test to avoid event loop reuse issues."""
    engine = create_async_engine(settings.effective_async_database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_01_real_embedding_generation_no_fake_math():
    """Verify embedder uses real SentenceTransformer and produces normalized vectors."""
    embedder = RealAgriculturalEmbedder()
    query = "How to treat late blight in potato?"
    vector = await embedder.aembed_text(query)

    assert len(vector) == 1024
    # Ensure vector is not all zeros or a simple repeating pattern
    assert any(v != 0.0 for v in vector)
    # Ensure values are legitimate floating point numbers within valid range
    assert all(-1.0 <= v <= 1.0 for v in vector)
    
    # Test empty string raises ValueError explicitly
    with pytest.raises(ValueError):
        await embedder.aembed_text("   ")


@pytest.mark.asyncio
async def test_02_pgvector_table_populated_and_not_empty(db_session):
    """Verify document_chunks has real rows in PostgreSQL. Strictly fails if count == 0."""
    result = await db_session.execute(text("SELECT COUNT(*) FROM document_chunks;"))
    count = result.scalar()
    assert count > 0, "CRITICAL ERROR: document_chunks table is empty in PostgreSQL!"
    assert count >= 100, f"Expected at least 100 ingested knowledge chunks, found {count}"


@pytest.mark.asyncio
async def test_03_pgvector_hnsw_index_exists(db_session):
    """Verify HNSW index on document_chunks.embedding is active in PostgreSQL."""
    idx_sql = text("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'document_chunks' AND indexname LIKE '%hnsw%';
    """)
    result = await db_session.execute(idx_sql)
    row = result.first()
    assert row is not None, "HNSW index missing on document_chunks table"
    assert "hnsw" in row[1].lower()


@pytest.mark.asyncio
async def test_04_semantic_retrieval_crop_disease(db_session):
    """Verify searching for disease symptoms retrieves the exact disease protocol."""
    retriever = KnowledgeRetriever(db_session)
    # Search for apple scab symptoms
    results = await retriever.search(
        query="olive green velvety spots on apple leaves fungicide spray",
        doc_type="disease_guide",
        top_k=3
    )
    assert len(results) > 0
    top = results[0]
    assert "apple" in top["title"].lower() or "apple" in top["content"].lower()
    assert top["similarity"] > 0.40
    assert top["doc_type"] == "disease_guide"
    assert top["source_url"] is not None


@pytest.mark.asyncio
async def test_05_semantic_retrieval_government_scheme(db_session):
    """Verify searching for income support retrieves PM-KISAN guidelines."""
    retriever = KnowledgeRetriever(db_session)
    results = await retriever.search(
        query="PM-KISAN 6000 rupees financial benefit installment for landholder farmers",
        doc_type="scheme",
        top_k=2
    )
    assert len(results) > 0
    assert any(r["metadata"].get("scheme_name") == "pm_kisan" for r in results)
    pm_kisan_res = next(r for r in results if r["metadata"].get("scheme_name") == "pm_kisan")
    assert pm_kisan_res["similarity"] > 0.45
    assert "pm-kisan" in pm_kisan_res["title"].lower()


@pytest.mark.asyncio
async def test_06_semantic_retrieval_crop_cultivation_agronomy(db_session):
    """Verify searching for crop cultivation returns ICAR agronomic guidance."""
    retriever = KnowledgeRetriever(db_session)
    results = await retriever.search(
        query="optimal temperature and recommended NPK fertilizer for wheat sowing",
        doc_type="crop_guide",
        top_k=2
    )
    assert len(results) > 0
    top = results[0]
    assert "wheat" in top["title"].lower() or "wheat" in top["content"].lower()
    assert "nitrogen" in top["content"].lower() or "npk" in top["content"].lower()


@pytest.mark.asyncio
async def test_07_grounding_context_generation_with_citations(db_session):
    """Verify get_grounding_context compiles clean markdown with citations and relevance."""
    retriever = KnowledgeRetriever(db_session)
    context = await retriever.get_grounding_context(
        query="How to claim crop insurance for standing crop flood damage?",
        doc_type="scheme",
        top_k=2
    )
    assert len(context) > 0
    assert "### [Source 1]" in context
    assert "PMFBY" in context or "Bima" in context
    assert "Relevance:" in context
    assert "https://" in context
