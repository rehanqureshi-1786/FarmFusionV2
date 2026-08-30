"""
Multi-Dimensional Voice & Language Evaluation Runner for FarmFusion.
Evaluates models across distinct demographic slices:
1. Normal standard speech
2. Rural farmer speech
3. Code-switched utterances
4. Agricultural domain vocabulary
5. Regional dialect speech (Marwari, Mewari, Bhojpuri, etc.)
"""
from typing import Dict, List, Any, Optional
import structlog
from pydantic import BaseModel, Field

from ml_training.voice.evaluation.metrics import (
    compute_wer,
    compute_cer,
    compute_agricultural_entity_accuracy
)

logger = structlog.get_logger(__name__)


class SliceEvaluationResult(BaseModel):
    slice_name: str
    sample_count: int
    wer: float
    cer: float
    agri_entity_accuracy: float
    intent_accuracy: Optional[float] = None
    failure_examples: List[Dict[str, str]] = Field(default_factory=list)


class ModelEvaluationReport(BaseModel):
    model_id: str
    overall_wer: float
    overall_cer: float
    overall_agri_accuracy: float
    slices: Dict[str, SliceEvaluationResult]
    latency_ms_per_second_audio: float
    model_size_mb: float


class VoiceModelEvaluator:
    @staticmethod
    def evaluate_asr_model(
        model_id: str,
        test_samples: List[Dict[str, Any]],
        known_agri_entities: Optional[List[str]] = None,
        model_size_mb: float = 38.0,
        latency_ms: float = 45.0,
    ) -> ModelEvaluationReport:
        entities = known_agri_entities or ["गेहूं", "बाजरा", "कपास", "सरसों", "यूरिया", "डीएपी", "झुलसा", "इल्ली", "जोधपुर"]
        
        # Partition into demographic slices
        slices_data: Dict[str, List[Dict[str, Any]]] = {
            "standard_speech": [],
            "rural_speech": [],
            "code_switched": [],
            "agricultural_vocabulary": [],
            "regional_dialect": [],
        }

        all_refs = []
        all_hyps = []

        for item in test_samples:
            ref = item.get("reference", "")
            hyp = item.get("hypothesis", "")
            tags = item.get("tags", ["standard_speech"])
            
            all_refs.append(ref)
            all_hyps.append(hyp)

            for t in tags:
                if t in slices_data:
                    slices_data[t].append(item)

        slice_results: Dict[str, SliceEvaluationResult] = {}
        for slice_name, items in slices_data.items():
            if not items:
                continue
            refs = [it.get("reference", "") for it in items]
            hyps = [it.get("hypothesis", "") for it in items]
            
            wer = compute_wer(refs, hyps)
            cer = compute_cer(refs, hyps)
            agri_acc = compute_agricultural_entity_accuracy(refs, hyps, entities)
            
            failures = []
            for r, h in zip(refs, hyps):
                if r != h and len(failures) < 5:
                    failures.append({"ref": r, "hyp": h})

            slice_results[slice_name] = SliceEvaluationResult(
                slice_name=slice_name,
                sample_count=len(items),
                wer=wer,
                cer=cer,
                agri_entity_accuracy=agri_acc,
                failure_examples=failures,
            )

        overall_wer = compute_wer(all_refs, all_hyps) if all_refs else 0.0
        overall_cer = compute_cer(all_refs, all_hyps) if all_refs else 0.0
        overall_agri = compute_agricultural_entity_accuracy(all_refs, all_hyps, entities) if all_refs else 1.0

        return ModelEvaluationReport(
            model_id=model_id,
            overall_wer=overall_wer,
            overall_cer=overall_cer,
            overall_agri_accuracy=overall_agri,
            slices=slice_results,
            latency_ms_per_second_audio=latency_ms,
            model_size_mb=model_size_mb,
        )
