"""
API Integration tests for /api/v1/knowledge endpoints with PostgreSQL pgvector.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_knowledge_query_api_returns_vector_matches():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/knowledge/query",
            json={
                "query": "What fungicide is recommended for apple scab?",
                "doc_type": "disease_guide",
                "top_k": 3
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "What fungicide is recommended for apple scab?"
        assert len(data["results"]) > 0
        top = data["results"][0]
        assert "apple" in top["title"].lower() or "apple" in top["content"].lower()
        assert "similarity" in top
        assert top["similarity"] > 0.35


@pytest.mark.asyncio
async def test_knowledge_schemes_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/knowledge/schemes?state=Rajasthan")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["results"]) > 0
        assert any("pm-kisan" in r["title"].lower() or "bima" in r["title"].lower() for r in data["results"])
