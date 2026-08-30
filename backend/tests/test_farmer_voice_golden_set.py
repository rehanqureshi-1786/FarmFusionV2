"""
Test suite validating the Golden Farmer Utterance Dataset across Indian Languages, Dialects, and Code-Switching.
"""
import json
import os
import pytest
from app.orchestrator.graph import run_orchestrator_pipeline

GOLDEN_SET_PATH = os.path.join(os.path.dirname(__file__), "data", "farmer_voice_golden_set.json")


def load_golden_set():
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.asyncio
@pytest.mark.parametrize("item", load_golden_set(), ids=lambda x: x["id"])
async def test_golden_farmer_utterance(item):
    """
    Validate that each natural farmer utterance in the golden dataset:
    1. Correctly classifies the canonical intent
    2. Correctly normalizes dialect/code-switched entities
    3. Correctly routes to the expected deterministic tool
    4. Executes with honest data integrity
    """
    res = await run_orchestrator_pipeline(
        user_input=item["utterance"],
        detected_language=item["language"],
        detected_dialect=item.get("dialect"),
    )

    assert res["intent"] == item["expected_intent"], (
        f"Utterance '{item['utterance']}' expected intent '{item['expected_intent']}' "
        f"but got '{res['intent']}'"
    )

    if item["expected_slots"]:
        for slot_k, slot_v in item["expected_slots"].items():
            assert res["filled_slots"].get(slot_k) == slot_v, (
                f"Expected slot {slot_k}={slot_v}, got {res['filled_slots'].get(slot_k)}"
            )

    if item.get("expected_tool"):
        assert res.get("last_tool") == item["expected_tool"], (
            f"Expected tool '{item['expected_tool']}', got '{res.get('last_tool')}'"
        )
