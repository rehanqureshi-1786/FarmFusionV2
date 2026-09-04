"""
Typed Pydantic schemas for Phase F6 RAG Grounding, Evidence Calibration, and Citations.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceLevel(str, Enum):
    """Calibrated RAG evidence classification based on empirical similarity distributions."""
    HIGH_EVIDENCE = "HIGH_EVIDENCE"   # similarity >= 0.50: Strong verified ICAR document match
    LOW_EVIDENCE = "LOW_EVIDENCE"     # 0.35 <= similarity < 0.50: Partial / tentative relevance
    NO_EVIDENCE = "NO_EVIDENCE"       # similarity < 0.35: No relevant domain documentation found


class RAGCitation(BaseModel):
    """Attributable document citation corresponding strictly to retrieved chunks."""
    model_config = ConfigDict(extra="forbid")

    chunk_id: int = Field(..., description="Database chunk primary key ID")
    title: str = Field(..., description="Document title")
    source_url: Optional[str] = Field(None, description="Authoritative reference URL")
    organization: str = Field(default="ICAR", description="Issuing agricultural institution")
    doc_type: str = Field(default="agricultural_guide", description="Document type classification")
    similarity_score: float = Field(default=0.85, ge=0.0, le=1.0, description="Cosine similarity score")


class GroundedDocumentChunk(BaseModel):
    """Individual retrieved and validated knowledge chunk."""
    model_config = ConfigDict(extra="forbid")

    chunk_id: int
    title: str
    doc_type: str
    content: str
    source_url: Optional[str] = None
    similarity: float = Field(..., ge=0.0, le=1.0)
    organization: str = Field(default="ICAR")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_citation(self) -> RAGCitation:
        return RAGCitation(
            chunk_id=self.chunk_id,
            title=self.title,
            source_url=self.source_url,
            organization=self.organization,
            doc_type=self.doc_type,
            similarity_score=self.similarity,
        )


class RAGGroundingResult(BaseModel):
    """Strongly typed output contract of the conditional RAG grounding node."""
    model_config = ConfigDict(extra="forbid")

    status: str = Field(default="SUCCESS", description="SUCCESS, NO_RELEVANT_CHUNKS, SKIPPED, or ERROR")
    query: str = Field(default="", description="Targeted query constructed from verified tool outputs")
    domain: str = Field(default="general", description="Target domain: disease, crop, disaster, scheme, etc.")
    evidence_level: EvidenceLevel = Field(default=EvidenceLevel.NO_EVIDENCE)
    documents: List[GroundedDocumentChunk] = Field(default_factory=list)
    citations: List[RAGCitation] = Field(default_factory=list)
    grounding_context_text: str = Field(default="", description="Compiled context block for LLM prompt")
    error_message: Optional[str] = None
