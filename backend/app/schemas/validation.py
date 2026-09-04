"""
Typed Pydantic schemas for Phase F6 Validation Node, Immutable Fact Sets, and Cross-Tool Consistency.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class CheckSeverity(str, Enum):
    BLOCKING = "BLOCKING"     # Fatal error / severe contradiction; requires regeneration or fallback
    WARNING = "WARNING"       # Non-fatal disparity or caveat; surfaces in envelope warnings
    INFO = "INFO"             # Advisory note


class ValidationCheck(BaseModel):
    """Result of an individual deterministic validator check."""
    model_config = ConfigDict(extra="forbid")

    check_name: str
    passed: bool
    severity: CheckSeverity = CheckSeverity.BLOCKING
    details: str
    target_tool: Optional[str] = None


class VerifiedFact(BaseModel):
    """
    Atomic verified numeric or categorical fact extracted strictly from specialist tool execution.
    The LLM response synthesis must preserve these values with 100% immutability.
    """
    model_config = ConfigDict(extra="forbid")

    key: str = Field(..., description="Fact identifier e.g. 'mandi_price', 'temperature_c', 'risk_score'")
    value: Union[float, int, str] = Field(..., description="Verified value from specialist engine")
    unit: Optional[str] = Field(None, description="Physical agronomic unit e.g. 'INR/quintal', 'C', 'mm', '%'")
    source_tool: str = Field(..., description="Name of the specialist tool that produced this fact")
    is_numeric: bool = Field(default=True, description="True if value is numeric and must undergo regex checks")


class VerifiedFactSet(BaseModel):
    """Machine-readable collection of immutable facts provided to the LLM synthesizer."""
    model_config = ConfigDict(extra="forbid")

    facts: List[VerifiedFact] = Field(default_factory=list)

    def get_fact(self, key: str) -> Optional[VerifiedFact]:
        for f in self.facts:
            if f.key == key:
                return f
        return None

    def to_prompt_text(self) -> str:
        """Formatted representation for injection into LLM system/user prompts."""
        if not self.facts:
            return "No numerical tool facts recorded."
        lines = []
        for f in self.facts:
            u_str = f" {f.unit}" if f.unit else ""
            lines.append(f"- {f.key}: {f.value}{u_str} (Source: {f.source_tool})")
        return "\n".join(lines)


class CrossToolConsistencyResult(BaseModel):
    """Validation report on multi-tool interactions (e.g. Weather rain vs Irrigation need)."""
    model_config = ConfigDict(extra="forbid")

    consistent: bool
    issue_description: Optional[str] = None
    participating_tools: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Output contract of the Validation / Safety Node."""
    model_config = ConfigDict(extra="forbid")

    is_valid: bool = Field(..., description="True if all blocking validation checks passed")
    checks: List[ValidationCheck] = Field(default_factory=list)
    verified_facts: VerifiedFactSet = Field(default_factory=VerifiedFactSet)
    cross_tool_consistency: CrossToolConsistencyResult = Field(
        default_factory=lambda: CrossToolConsistencyResult(consistent=True)
    )
    confidence_tier: str = Field(default="high", description="high, medium, low, or unclear")
    aggregated_confidence: float = Field(default=0.90, ge=0.0, le=1.0, description="Calculated composite confidence")
    warnings: List[str] = Field(default_factory=list)
    action_override: Optional[str] = None
