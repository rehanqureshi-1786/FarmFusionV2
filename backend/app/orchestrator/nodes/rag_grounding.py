"""
Conditional RAG Grounding Node for LangGraph Orchestrator.
Formulates targeted knowledge queries from verified specialist tool outputs,
queries pgvector HNSW index, applies calibrated quality gating, and prepares
grounding context with attributable citations.
"""
from typing import Any, Dict, List, Optional, Tuple
import structlog
from app.orchestrator.state import OrchestratorState
from app.schemas.rag import (
    EvidenceLevel,
    GroundedDocumentChunk,
    RAGCitation,
    RAGGroundingResult,
)
from app.schemas.semantic_frame import CanonicalIntent, CapabilityType
from app.core.database import AsyncSessionLocal
from app.rag.retriever import KnowledgeRetriever

logger = structlog.get_logger(__name__)

# Calibrated empirical thresholds from scratch/calibrate_rag_similarity.py
SIMILARITY_HIGH_THRESHOLD = 0.45
SIMILARITY_LOW_THRESHOLD = 0.30


def should_trigger_rag_grounding(state: OrchestratorState) -> Tuple[bool, str]:
    """
    Deterministic rule engine determining whether RAG grounding is required.
    Returns (should_run, domain_category).
    """
    # If state requires clarification or is a pure navigation, skip RAG
    if state.get("requires_clarification") or state.get("next_action") in ["NAVIGATE", "CLARIFY", "REQUEST_INPUT"]:
        return False, "none"

    intent_str = state.get("intent", "").lower()
    tool_results = state.get("tool_results", {}) or {}

    # 1. Disease Detection: always ground with treatment knowledge if disease identified
    if any(k.startswith("disease") for k in tool_results.keys()) or intent_str in ["disease", "disease_detection"]:
        return True, "disease"

    # 2. Crop Recommendation: ground with ICAR agronomy guidelines for top crop
    if any(k.startswith("crop_rec") for k in tool_results.keys()) or intent_str in ["crop_recommendation"]:
        return True, "crop"

    # 3. Disaster Risk: ground with safety & mitigation guidelines if hazard identified
    if any(k.startswith("disaster") for k in tool_results.keys()) or intent_str in ["disaster_risk"]:
        return True, "disaster"

    # 4. Government Schemes & General Agriculture
    if intent_str in ["scheme", "government_scheme", "agricultural_knowledge", "general_agriculture"]:
        return True, "scheme" if "scheme" in intent_str else "agronomy"

    # 5. Check if RAG_KNOWLEDGE was specifically planned in task plan
    task_plan = state.get("task_plan")
    if task_plan and any(t.get("capability") == "RAG_KNOWLEDGE" for t in task_plan.get("tasks", [])):
        return True, "general"

    return False, "none"


def construct_verified_rag_query(state: OrchestratorState, domain: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Derives authoritative RAG query strictly from verified upstream tool outputs.
    Returns (query_string, doc_type_filter, crop_filter).
    """
    tool_results = state.get("tool_results", {}) or {}
    legacy_output = state.get("tool_output", {}) or {}

    if domain == "disease":
        disease_task = next((v for k, v in tool_results.items() if "disease" in k), legacy_output)
        disease_name = disease_task.get("disease_name") or disease_task.get("predicted_disease") or "Plant Disease"
        crop = disease_task.get("crop") or state.get("active_crop") or "Crop"
        # Avoid speculative queries; formulate crisp agronomic query
        return f"{crop} {disease_name} treatment management control measures", "disease_guide", crop.lower()

    if domain == "crop":
        crop_task = next((v for k, v in tool_results.items() if "crop" in k), legacy_output)
        top_crop = crop_task.get("top_crop") or crop_task.get("crop_name") or state.get("active_crop") or "Wheat"
        return f"{top_crop} cultivation agronomy package of practices optimal temperature soil", "crop_guide", top_crop.lower()

    if domain == "disaster":
        disaster_task = next((v for k, v in tool_results.items() if "disaster" in k), legacy_output)
        hazard = disaster_task.get("peak_disaster_type") or disaster_task.get("current_disaster_type") or "Adverse Weather"
        location = disaster_task.get("location") or "agricultural field"
        return f"{hazard} mitigation drainage crop protection precautions and preparedness", None, None

    if domain == "scheme":
        user_input = state.get("user_input", "Government schemes for farmers")
        return f"{user_input} eligibility benefits application process", "scheme", None

    # General agricultural knowledge / crop care
    user_input = state.get("user_input", "agricultural best practices")
    sf = state.get("semantic_frame") or {}
    sf_entities = sf.get("entities") or {} if isinstance(sf, dict) else {}
    crop = sf_entities.get("crop") or state.get("active_crop")
    if crop:
        crop_clean = str(crop).strip()
        return f"{crop_clean} {user_input} crop care management package of practices", "crop_guide", crop_clean.lower()
    return user_input, None, None


async def rag_grounding_node(state: OrchestratorState) -> OrchestratorState:
    """
    Executes conditional RAG grounding:
    1. Checks if RAG is appropriate.
    2. Builds query from verified tool outputs.
    3. Runs vector search via pgvector.
    4. Applies empirical quality calibration (HIGH, LOW, NO evidence).
    5. Formulates structured RAGGroundingResult and injects into OrchestratorState.
    """
    should_run, domain = should_trigger_rag_grounding(state)
    if not should_run:
        logger.info("rag_grounding_skipped", reason="intent_or_action_does_not_require_rag")
        state["rag_grounding"] = RAGGroundingResult(
            status="SKIPPED",
            domain="none",
            evidence_level=EvidenceLevel.NO_EVIDENCE,
        ).model_dump()
        return state

    query, doc_type, crop_filter = construct_verified_rag_query(state, domain)
    logger.info("rag_grounding_start", query=query, domain=domain, doc_type=doc_type, crop=crop_filter)

    try:
        async with AsyncSessionLocal() as session:
            retriever = KnowledgeRetriever(session)
            raw_matches = await retriever.search(
                query=query,
                doc_type=doc_type,
                crop=crop_filter,
                top_k=3,
            )

        if not raw_matches:
            logger.info("rag_grounding_no_matches", query=query)
            state["rag_grounding"] = RAGGroundingResult(
                status="NO_RELEVANT_CHUNKS",
                query=query,
                domain=domain,
                evidence_level=EvidenceLevel.NO_EVIDENCE,
                documents=[],
                citations=[],
                grounding_context_text="No verified agronomic documents matched the query.",
            ).model_dump()
            return state

        top_score = raw_matches[0]["similarity"]
        if top_score >= SIMILARITY_HIGH_THRESHOLD:
            evidence = EvidenceLevel.HIGH_EVIDENCE
        elif top_score >= SIMILARITY_LOW_THRESHOLD:
            evidence = EvidenceLevel.LOW_EVIDENCE
        else:
            evidence = EvidenceLevel.NO_EVIDENCE

        # Filter documents based on threshold
        grounded_docs: List[GroundedDocumentChunk] = []
        citations: List[RAGCitation] = []
        context_blocks: List[str] = []

        if evidence != EvidenceLevel.NO_EVIDENCE:
            for idx, m in enumerate(raw_matches, 1):
                if m["similarity"] < SIMILARITY_LOW_THRESHOLD:
                    continue
                meta = m.get("metadata", {}) or {}
                org = meta.get("organization", "ICAR")
                doc = GroundedDocumentChunk(
                    chunk_id=m["id"],
                    title=m["title"],
                    doc_type=m["doc_type"],
                    content=m["content"],
                    source_url=m.get("source_url"),
                    similarity=m["similarity"],
                    organization=org,
                    metadata=meta,
                )
                grounded_docs.append(doc)
                citations.append(doc.to_citation())
                context_blocks.append(
                    f"### [Source {idx}]: {doc.title} ({org})\n"
                    f"{doc.content}\n"
                    f"*Reference: {doc.source_url or 'Verified Official Catalog'} (Relevance: {doc.similarity:.2%})*\n"
                )

        compiled_context = "\n".join(context_blocks) if context_blocks else "No authoritative grounding chunks met the quality threshold."

        rag_result = RAGGroundingResult(
            status="SUCCESS",
            query=query,
            domain=domain,
            evidence_level=evidence,
            documents=grounded_docs,
            citations=citations,
            grounding_context_text=compiled_context,
        )

        state["rag_grounding"] = rag_result.model_dump()
        state["rag_citations"] = [c.model_dump() for c in citations]
        logger.info(
            "rag_grounding_complete",
            query=query,
            matches_count=len(grounded_docs),
            top_similarity=top_score,
            evidence_level=evidence.value,
        )

    except Exception as e:
        logger.error("rag_grounding_failed", query=query, error=str(e))
        state["rag_grounding"] = RAGGroundingResult(
            status="ERROR",
            query=query,
            domain=domain,
            evidence_level=EvidenceLevel.NO_EVIDENCE,
            error_message=str(e),
        ).model_dump()

    return state
