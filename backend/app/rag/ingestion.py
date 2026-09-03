"""
Agricultural Knowledge Ingestion Pipeline for FarmFusion Vector RAG.
Extracts, structures, embeds, and indexes authoritative agronomic knowledge:
- ICAR Crop Cultivation Guides (32 Indian crops)
- Plant Disease Treatment & Management Protocols (49 pathologies)
- Regional Agro-ecological Suitability Matrices
- National Agricultural Welfare Schemes (PM-KISAN, PMFBY, KCC, Soil Health Card)
"""
import asyncio
import json
import os
import sqlite3
import sys
from typing import Any, Dict, List
import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import app.models
from app.core.config import settings
from app.models.rag import DocumentChunk
from app.rag.embedder import BGEM3Embedder

logger = structlog.get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISEASE_KB_PATH = os.path.join(BASE_DIR, "data", "disease_knowledge_base.json")
AGRI_DB_PATH = os.path.join(BASE_DIR, "data", "agriculture", "farmfusion_agriculture.db")


def load_disease_chunks() -> List[Dict[str, Any]]:
    """Generates structured chunks from the verified 49-disease knowledge base."""
    if not os.path.exists(DISEASE_KB_PATH):
        logger.warning("disease_kb_file_missing", path=DISEASE_KB_PATH)
        return []

    with open(DISEASE_KB_PATH, "r", encoding="utf-8") as f:
        kb = json.load(f)

    chunks = []
    for key, data in kb.items():
        crop = data.get("crop", key.split("___")[0] if "___" in key else "General")
        name = data.get("name", key.split("___")[-1].replace("_", " ") if "___" in key else key)

        symptoms = "\n- ".join(data.get("symptoms", []))
        bio_ctrl = "\n- ".join(data.get("biological_control", []))
        chem_ctrl = "\n- ".join(data.get("chemical_control", []))
        cultural_ctrl = "\n- ".join(data.get("cultural_control", []))
        products = ", ".join(data.get("product_recommendations", []))

        content = (
            f"# Crop: {crop}\n"
            f"## Disease: {name}\n\n"
            f"### Visual Symptoms:\n- {symptoms}\n\n"
            f"### Cultural & Preventive Management:\n- {cultural_ctrl}\n\n"
            f"### Biological & Organic Control:\n- {bio_ctrl}\n\n"
            f"### Chemical Control & Fungicide/Bactericide Protocols:\n- {chem_ctrl}\n\n"
            f"### Recommended Products & Chemical Actives:\n{products}\n"
        )

        chunks.append({
            "title": f"{crop} - {name} Identification and Treatment Guide",
            "doc_type": "disease_guide",
            "content": content,
            "source_url": "https://icar.org.in/plant-protection-guidelines",
            "metadata": {
                "crop": crop.lower(),
                "disease": name.lower(),
                "topic": "plant_pathology",
                "organization": "ICAR-NCIPM",
                "trust_level": "official_verified",
            }
        })
    return chunks


def load_crop_agronomy_chunks() -> List[Dict[str, Any]]:
    """Extracts structured cultivation profiles from ICAR crop profiles database."""
    if not os.path.exists(AGRI_DB_PATH):
        logger.warning("agri_db_file_missing", path=AGRI_DB_PATH)
        return []

    conn = sqlite3.connect(AGRI_DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    chunks = []
    # 1. ICAR Crop Profiles
    try:
        profiles = cur.execute("SELECT * FROM icar_crop_profiles;").fetchall()
        for p in profiles:
            p_dict = dict(p)
            crop_name = p_dict.get("crop_name", "Unknown").capitalize()
            content = (
                f"# ICAR Agronomic Package of Practices: {crop_name}\n\n"
                f"### Climate & Soil Requirements:\n"
                f"- Optimal Temperature Range: {p_dict.get('min_temp_c', 'N/A')}°C to {p_dict.get('max_temp_c', 'N/A')}°C\n"
                f"- Annual Rainfall Requirement: {p_dict.get('min_rainfall_mm', 'N/A')} mm to {p_dict.get('max_rainfall_mm', 'N/A')} mm\n"
                f"- Suitable Soil Types: {p_dict.get('suitable_soils', 'Well-drained loamy to clay loam')}\n"
                f"- Soil pH Tolerance: {p_dict.get('min_ph', '6.0')} - {p_dict.get('max_ph', '7.5')}\n\n"
                f"### Nutrient & Fertilizer Application (NPK kg/ha):\n"
                f"- Recommended Nitrogen (N): {p_dict.get('rec_n_kg_ha', 'N/A')} kg/ha\n"
                f"- Recommended Phosphorus (P2O5): {p_dict.get('rec_p_kg_ha', 'N/A')} kg/ha\n"
                f"- Recommended Potassium (K2O): {p_dict.get('rec_k_kg_ha', 'N/A')} kg/ha\n\n"
                f"### Sowing & Growth Cycle:\n"
                f"- Cropping Season: {p_dict.get('season', 'Kharif/Rabi')}\n"
                f"- Optimal Sowing Window: {p_dict.get('sowing_window', 'June-July or October-November')}\n"
                f"- Crop Duration to Maturity: {p_dict.get('duration_days', '110-130')} days\n"
            )
            chunks.append({
                "title": f"{crop_name} - ICAR Agronomic Cultivation Guide",
                "doc_type": "crop_guide",
                "content": content,
                "source_url": "https://icar.org.in/crop-science-handbook",
                "metadata": {
                    "crop": crop_name.lower(),
                    "topic": "crop_cultivation",
                    "organization": "ICAR-IARI",
                    "trust_level": "official_verified",
                }
            })
    except Exception as e:
        logger.error("error_loading_icar_crop_profiles", error=str(e))

    # 2. Regional Suitability Summaries
    try:
        regs = cur.execute("SELECT state, crop_name, priority_tier, suitability_multiplier, agro_climatic_zone, crida_contingency_notes FROM regional_crop_suitability;").fetchall()
        for r in regs:
            r_dict = dict(r)
            state = r_dict.get("state", "India")
            crop = r_dict.get("crop_name", "Crop")
            tier = r_dict.get("priority_tier", "Recommended")
            zone = r_dict.get("agro_climatic_zone", "Agro-ecological Zone")
            contingency = r_dict.get("crida_contingency_notes") or "Standard regional farm management."
            content = (
                f"# Regional Agro-Climatic Suitability: {crop} in {state}\n\n"
                f"- Agro-Climatic Zone: {zone}\n"
                f"- Regional Priority Tier: {tier}\n"
                f"- CRIDA Farm Contingency Guidance: {contingency}\n"
                f"- Regional Farm Practices: Adopt moisture conservation, certified seeds, and soil-test-based fertilizer schedules.\n"
            )
            chunks.append({
                "title": f"Regional Suitability: {crop} Cultivation in {state}",
                "doc_type": "regional_guide",
                "content": content,
                "source_url": "https://agricoop.nic.in/en/agro-climatic-zones",
                "metadata": {
                    "state": state.lower(),
                    "crop": crop.lower(),
                    "topic": "regional_suitability",
                    "organization": "ICAR-CRIDA",
                    "trust_level": "official_verified",
                }
            })
    except Exception as e:
        logger.error("error_loading_regional_suitability", error=str(e))

    conn.close()
    return chunks


def load_government_schemes_chunks() -> List[Dict[str, Any]]:
    """Official guidelines for major Indian agricultural welfare and insurance schemes."""
    schemes = [
        {
            "title": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) Scheme Guidelines",
            "doc_type": "scheme",
            "content": (
                "# Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)\n\n"
                "### Scheme Overview:\n"
                "PM-KISAN is a central sector scheme providing income support to all landholding farmer families across India.\n\n"
                "### Financial Benefit:\n"
                "- Annual financial support of Rs. 6,000 per eligible farmer family.\n"
                "- Released in three equal four-monthly installments of Rs. 2,000 directly into Aadhaar-linked bank accounts via DBT.\n\n"
                "### Eligibility & Exclusions:\n"
                "- Eligible: All landholder farmer families with cultivable landholding in their names.\n"
                "- Excluded: Institutional landholders, serving/retired government employees, income tax payees, and constitutional post holders.\n\n"
                "### Application & e-KYC Verification:\n"
                "- Mandatory e-KYC via PM-KISAN portal (pmkisan.gov.in) or mobile app using OTP/facial recognition.\n"
                "- Required documents: Aadhaar card, land ownership record (Khasra/Khatauni), active bank passbook.\n"
            ),
            "source_url": "https://pmkisan.gov.in/",
            "metadata": {
                "scheme_name": "pm_kisan",
                "topic": "income_support",
                "organization": "Ministry of Agriculture & Farmers Welfare",
                "trust_level": "official_verified"
            }
        },
        {
            "title": "PMFBY (Pradhan Mantri Fasal Bima Yojana) Crop Insurance Guidelines",
            "doc_type": "scheme",
            "content": (
                "# Pradhan Mantri Fasal Bima Yojana (PMFBY)\n\n"
                "### Scheme Overview:\n"
                "PMFBY provides comprehensive risk insurance coverage against non-preventable natural risks from pre-sowing to post-harvest stages.\n\n"
                "### Premium Rates for Farmers:\n"
                "- Kharif Food & Oilseed Crops: Maximum 2.0% of Sum Insured.\n"
                "- Rabi Food & Oilseed Crops: Maximum 1.5% of Sum Insured.\n"
                "- Annual Commercial / Horticultural Crops: Maximum 5.0% of Sum Insured.\n"
                "- Remaining premium subsidy is shared 50:50 by Central and State Governments.\n\n"
                "### Risk Coverage Stages:\n"
                "1. Prevented Sowing / Planting Risk due to adverse seasonal weather.\n"
                "2. Standing Crop Loss due to drought, dry spells, flood, inundation, pests, and diseases.\n"
                "3. Post-Harvest Losses (up to 14 days) due to unseasonal cyclone/cyclonic rains or localized storms.\n"
                "4. Localized Calamities: Hailstorm, landslide, cloudburst.\n\n"
                "### Claim Intimation Window:\n"
                "- In case of localized calamity or post-harvest loss, intimation must be submitted within 72 hours via Crop Insurance App or toll-free helpline 14447.\n"
            ),
            "source_url": "https://pmfby.gov.in/",
            "metadata": {
                "scheme_name": "pmfby",
                "topic": "crop_insurance",
                "organization": "Ministry of Agriculture & Farmers Welfare",
                "trust_level": "official_verified"
            }
        },
        {
            "title": "Kisan Credit Card (KCC) Scheme Rules & Concessional Credit",
            "doc_type": "scheme",
            "content": (
                "# Kisan Credit Card (KCC) Scheme\n\n"
                "### Scheme Purpose:\n"
                "Provides timely short-term credit to farmers for crop cultivation, post-harvest expenses, farm asset maintenance, and allied activities.\n\n"
                "### Interest Subvention & Effective Rates:\n"
                "- Baseline Interest Rate: 9% per annum.\n"
                "- Government of India Interest Subvention: 2% (bringing rate to 7%).\n"
                "- Prompt Repayment Incentive (PRI): Additional 3% discount for farmers repaying within one year.\n"
                "- Net Effective Interest Rate for prompt repaying farmers: 4.0% per annum on loans up to Rs. 3,00,000.\n\n"
                "### Collateral-Free Limit:\n"
                "- Up to Rs. 1,60,000 without requiring any collateral or agricultural land mortgage.\n"
            ),
            "source_url": "https://www.myscheme.gov.in/schemes/kcc",
            "metadata": {
                "scheme_name": "kcc",
                "topic": "agricultural_credit",
                "organization": "NABARD / RBI",
                "trust_level": "official_verified"
            }
        },
        {
            "title": "Soil Health Card (SHC) Scheme & Fertilizer Advisory Guidelines",
            "doc_type": "scheme",
            "content": (
                "# Soil Health Card (SHC) Scheme\n\n"
                "### Scheme Overview:\n"
                "Assists farmers in identifying soil nutrient status and prescribing balanced fertilizer and organic manure application.\n\n"
                "### 12 Parameters Analyzed:\n"
                "1. Primary Nutrients: Nitrogen (N), Phosphorus (P), Potassium (K)\n"
                "2. Secondary Nutrient: Sulphur (S)\n"
                "3. Micronutrients: Zinc (Zn), Iron (Fe), Copper (Cu), Manganese (Mn), Boron (B)\n"
                "4. Physical / Chemical Properties: pH (acidity/alkalinity), Electrical Conductivity (EC - salinity), Organic Carbon (OC)\n\n"
                "### Recommendation Benefit:\n"
                "- Prevents costly over-application of Urea (Nitrogen).\n"
                "- Recommends specific doses based on soil test to maximize crop yield while reducing input costs by 15-25%.\n"
            ),
            "source_url": "https://soilhealth.dac.gov.in/",
            "metadata": {
                "scheme_name": "soil_health_card",
                "topic": "soil_fertility",
                "organization": "Ministry of Agriculture & Farmers Welfare",
                "trust_level": "official_verified"
            }
        }
    ]
    return schemes


async def ingest_all_knowledge(clear_existing: bool = False) -> int:
    """Orchestrates extraction, dense vector embedding, and insertion into pgvector."""
    db_url = settings.effective_async_database_url
    engine = create_async_engine(db_url, echo=False)

    embedder = BGEM3Embedder()
    print("Extracting authoritative documents...")
    all_chunks = []
    all_chunks.extend(load_disease_chunks())
    all_chunks.extend(load_crop_agronomy_chunks())
    all_chunks.extend(load_government_schemes_chunks())

    print(f"Total structured documents prepared for ingestion: {len(all_chunks)}")

    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        if clear_existing:
            await session.execute(text("DELETE FROM document_chunks;"))
            await session.commit()
            print("Cleared existing document chunks.")

        batch_size = 10
        total_inserted = 0

        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            for item in batch:
                vector = await embedder.aembed_text(item["content"])
                doc = DocumentChunk(
                    title=item["title"],
                    doc_type=item["doc_type"],
                    content=item["content"],
                    source_url=item.get("source_url"),
                    metadata_json=item.get("metadata", {}),
                    embedding=vector
                )
                session.add(doc)
            await session.commit()
            total_inserted += len(batch)
            print(f"  Ingested {total_inserted}/{len(all_chunks)} chunks into pgvector...")

        # Create HNSW index for fast sub-millisecond similarity search
        try:
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw 
                ON document_chunks USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))
            await session.commit()
            print("[INDEX] HNSW cosine vector index created/verified on document_chunks.")
        except Exception as e:
            logger.warning("hnsw_index_creation_warning", error=str(e))

    await engine.dispose()
    return total_inserted


if __name__ == "__main__":
    count = asyncio.run(ingest_all_knowledge(clear_existing=True))
    print(f"\nINGESTION COMPLETE: {count} verified agricultural knowledge chunks indexed in pgvector.")
