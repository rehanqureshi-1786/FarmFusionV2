"""
Local Response Generator for FarmFusion.
Grounded response synthesis using verified tool payloads and dialect rules.
"""
from typing import Dict, Any, Optional
import structlog
from app.voice.local.response.base import LocalResponseModel, LocalResponseResult
from app.orchestrator.nodes.synthesizer import response_synthesizer_node
from app.orchestrator.state import OrchestratorState

logger = structlog.get_logger(__name__)


class LocalResponseEngine(LocalResponseModel):
    def __init__(self, model_id: str = "farmfusion_response_agri_slm_v1"):
        self.model_id = model_id
        self._loaded = True

    def load(self) -> bool:
        self._loaded = True
        return True

    def is_available(self) -> bool:
        return self._loaded

    def capabilities(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "task": "response",
            "is_available": True,
            "runtime": "rule_engine",
        }

    async def generate_response(
        self,
        intent: str,
        tool_payload: Dict[str, Any],
        language: str = "hi",
        dialect: Optional[str] = None
    ) -> LocalResponseResult:
        state: OrchestratorState = {
            "intent": intent,
            "tool_output": tool_payload,
            "tool_status": "success",
            "detected_language": language,
            "detected_dialect": dialect,
            "requires_clarification": False,
        }

        updated_state = await response_synthesizer_node(state)

        return LocalResponseResult(
            response_text=updated_state.get("final_response", ""),
            response_language=updated_state.get("response_language", language),
            response_dialect=updated_state.get("response_dialect", dialect),
            grounded=True,
            model_id=self.model_id,
        )
