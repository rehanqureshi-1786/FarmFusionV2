import asyncio
from app.rag.embedder import RealAgriculturalEmbedder
from app.core.database import AsyncSessionLocal
from app.rag.retriever import KnowledgeRetriever

QUERIES = [
    # In-Domain: Disease
    ("disease", "Tomato Early Blight treatment and fungicide control"),
    ("disease", "Potato Late Blight symptoms and management"),
    ("disease", "Apple scab identification and spray schedule"),
    # In-Domain: Crop
    ("crop", "Wheat cultivation package of practices optimal temperature"),
    ("crop", "Rice cultivation soil requirement and rainfall"),
    ("crop", "Cotton pest management and sowing time"),
    # In-Domain: Disaster
    ("disaster", "Flood risk management drainage and crop protection"),
    ("disaster", "Drought management dryland farming practices"),
    # In-Domain: Schemes
    ("scheme", "PM-KISAN financial assistance eligibility"),
    ("scheme", "Pradhan Mantri Fasal Bima Yojana crop insurance claim"),
    ("scheme", "Soil Health Card testing parameters"),
    # Out-of-Domain / Unsupported
    ("unsupported", "How to buy Bitcoin cryptocurrency trading online"),
    ("unsupported", "Latest Bollywood movies release dates box office"),
    ("unsupported", "Quantum mechanics electron spin equation"),
    ("unsupported", "Best Italian pasta recipe with parmesan cheese"),
]

async def calibrate():
    embedder = RealAgriculturalEmbedder()
    async with AsyncSessionLocal() as session:
        retriever = KnowledgeRetriever(session, embedder=embedder)
        
        print("=== RAG RETRIEVAL SIMILARITY CALIBRATION ===")
        domain_scores = {}
        for category, q in QUERIES:
            results = await retriever.search(q, top_k=3)
            top_sim = results[0]["similarity"] if results else 0.0
            top_title = results[0]["title"] if results else "None"
            print(f"[{category.upper():11}] TopSim: {top_sim:.4f} | Query: \"{q[:45]}...\" -> \"{top_title[:40]}\"")
            if category not in domain_scores:
                domain_scores[category] = []
            domain_scores[category].append(top_sim)

        print("\n=== SUMMARY DISTRIBUTIONS ===")
        for cat, scores in domain_scores.items():
            avg_s = sum(scores) / len(scores)
            min_s = min(scores)
            max_s = max(scores)
            print(f"{cat.upper():12}: min={min_s:.4f}, avg={avg_s:.4f}, max={max_s:.4f}")

if __name__ == "__main__":
    asyncio.run(calibrate())
