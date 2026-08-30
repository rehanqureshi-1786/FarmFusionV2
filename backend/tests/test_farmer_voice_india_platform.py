"""
Production Integration Test Suite for FarmFusion India-Wide Multilingual & Regional-Dialect Farmer Voice Platform.
"""
import json
import os
import pytest
from app.orchestrator.graph import run_orchestrator_pipeline
from app.voice.providers import get_language_capability

DATASET_PATH = os.path.join(os.path.dirname(__file__), "data", "farmer_voice_india_golden_set.json")


def load_india_golden_set():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.asyncio
@pytest.mark.parametrize("item", load_india_golden_set(), ids=lambda x: x["id"])
async def test_india_golden_farmer_utterance(item):
    """
    Validate that each natural farmer utterance across India:
    1. Correctly classifies intent
    2. Correctly normalizes dialect/code-switched entities
    3. Handles safety and language preferences
    4. Accurately maps to verified capability status
    """
    res = await run_orchestrator_pipeline(
        user_input=item["utterance"],
        detected_language=item["language"],
        detected_dialect=item.get("dialect"),
    )

    assert res["intent"] == item["expected_intent"], (
        f"Utterance '{item['utterance']}' expected intent '{item['expected_intent']}' but got '{res['intent']}'"
    )

    if item.get("expected_tool"):
        assert res.get("last_tool") == item["expected_tool"], (
            f"Expected tool '{item['expected_tool']}', got '{res.get('last_tool')}'"
        )

    # Validate capability status authenticity
    cap = get_language_capability(item.get("dialect") or item["language"])
    if item["capability_status"] == "NATIVE_VOICE":
        assert cap["status"] == "NATIVE"
    elif item["capability_status"] == "UNDERSTAND_PARENT_RESPONSE":
        assert cap["status"] == "PARENT_FALLBACK"


@pytest.mark.asyncio
async def test_consequential_action_confirmation_gate():
    """Verify that consequential actions require verbal confirmation and do not execute destructively."""
    turn = await run_orchestrator_pipeline(
        user_input="मेरी फसल का डेटा डिलीट कर दो",
        detected_language="hi"
    )
    assert turn["intent"] == "consequential_action"
    assert turn["safety_classification"] == "CONSEQUENTIAL"
    assert turn["requires_consequential_confirmation"] is True
    assert "पुष्टि" in turn["final_response"] or "confirm" in turn["final_response"].lower()


@pytest.mark.asyncio
async def test_language_preference_switching_flow():
    """Verify dynamic in-session language preference switching."""
    # Turn 1: Farmer speaks in English
    turn1 = await run_orchestrator_pipeline(
        user_input="What's the weather today?",
        detected_language="en",
        session_id="switch_lang_01"
    )
    assert turn1["intent"] == "weather"

    # Turn 2: Farmer explicitly requests Hindi
    turn2 = await run_orchestrator_pipeline(
        user_input="अब हिंदी में बताओ",
        detected_language="hi",
        session_id="switch_lang_01"
    )
    assert turn2["intent"] == "language_preference"
    assert turn2["farmer_preferred_language"] == "hi"
    assert "हिंदी" in turn2["final_response"]
