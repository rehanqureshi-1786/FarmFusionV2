"""
Voice & Language Evaluation Metrics for FarmFusion.
Computes:
- Word Error Rate (WER) & Character Error Rate (CER)
- Agricultural Entity Accuracy (Crucial for crops, soil, chemicals, diseases)
- Intent Classification & Slot Filling Weighted F1
- Dialect Identification Precision, Recall, Confusion Matrix
"""
from typing import List, Dict, Any, Tuple
import structlog

logger = structlog.get_logger(__name__)


def compute_levenshtein_distance(ref: List[str], hyp: List[str]) -> int:
    """Compute Levenshtein edit distance between two token lists."""
    r_len, h_len = len(ref), len(hyp)
    dp = [[0] * (h_len + 1) for _ in range(r_len + 1)]

    for i in range(r_len + 1):
        dp[i][0] = i
    for j in range(h_len + 1):
        dp[0][j] = j

    for i in range(1, r_len + 1):
        for j in range(1, h_len + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    return dp[r_len][h_len]


def compute_wer(references: List[str], hypotheses: List[str]) -> float:
    """Compute Word Error Rate (WER)."""
    total_words = 0
    total_errors = 0

    for ref, hyp in zip(references, hypotheses):
        ref_words = ref.strip().split()
        hyp_words = hyp.strip().split()
        if not ref_words:
            continue
        errors = compute_levenshtein_distance(ref_words, hyp_words)
        total_errors += errors
        total_words += len(ref_words)

    return round(total_errors / max(1, total_words), 4)


def compute_cer(references: List[str], hypotheses: List[str]) -> float:
    """Compute Character Error Rate (CER)."""
    total_chars = 0
    total_errors = 0

    for ref, hyp in zip(references, hypotheses):
        ref_chars = list(ref.replace(" ", ""))
        hyp_chars = list(hyp.replace(" ", ""))
        if not ref_chars:
            continue
        errors = compute_levenshtein_distance(ref_chars, hyp_chars)
        total_errors += errors
        total_chars += len(ref_chars)

    return round(total_errors / max(1, total_chars), 4)


def compute_agricultural_entity_accuracy(
    references: List[str],
    hypotheses: List[str],
    known_entities: List[str]
) -> float:
    """
    Evaluate transcription accuracy specifically on critical agricultural entity keywords.
    """
    total_entities = 0
    correct_entities = 0

    for ref, hyp in zip(references, hypotheses):
        ref_tokens = set(ref.split())
        hyp_tokens = set(hyp.split())

        for ent in known_entities:
            if ent in ref_tokens:
                total_entities += 1
                if ent in hyp_tokens:
                    correct_entities += 1

    if total_entities == 0:
        return 1.0
    return round(correct_entities / total_entities, 4)
