"""
Evaluation suite running 100 golden queries against the Phase F3 Semantic Extraction Layer.

Measures:
1. Intent Accuracy
2. Entity Accuracy (Crop and Market/City)
3. Capability Detection Accuracy
4. Required Input Accuracy (specifically the LEAF_IMAGE gate)
5. Multi-turn slot inheritance accuracy
"""
import json
from pathlib import Path
import pytest

from app.orchestrator.semantic_extractor import (
    extract_semantic_frame,
    extract_semantic_frame_deterministic,
)
from app.schemas.semantic_frame import (
    CanonicalIntent,
    CapabilityType,
    RequiredInput,
    UserContext,
    ConversationContext,
    FarmLocation,
)


@pytest.fixture
def golden_queries():
    data_path = Path(__file__).parent / "data" / "semantic_extraction_golden_100.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_100_queries_semantic_extraction(golden_queries):
    """
    Evaluates all 100 golden queries across accuracy dimensions.
    """
    total = len(golden_queries)
    intent_correct = 0
    crop_correct = 0
    crop_evaluated = 0
    market_correct = 0
    market_evaluated = 0
    input_gate_correct = 0
    capabilities_correct = 0

    failures = []

    for item in golden_queries:
        q_id = item["id"]
        raw_text = item["query"]
        lang = item.get("language", "hi")
        dialect = item.get("dialect")

        frame = await extract_semantic_frame(
            raw_text=raw_text,
            detected_language=lang,
            detected_dialect=dialect,
            session_id=f"eval_{q_id}"
        )

        # 1. Check Intent
        expected_intent = item["expected_intent"]
        is_intent_ok = (frame.intent.value == expected_intent)
        if is_intent_ok:
            intent_correct += 1
        else:
            failures.append(f"[{q_id}] Intent Mismatch: Got {frame.intent.value}, Expected {expected_intent} ('{raw_text}')")

        # 2. Check Crop (if specified)
        expected_crop = item.get("expected_crop")
        if expected_crop:
            crop_evaluated += 1
            if frame.entities.crop and frame.entities.crop.lower() == expected_crop.lower():
                crop_correct += 1
            else:
                failures.append(f"[{q_id}] Crop Mismatch: Got {frame.entities.crop}, Expected {expected_crop}")

        # 3. Check Market (if specified)
        expected_market = item.get("expected_market")
        if expected_market:
            market_evaluated += 1
            got_market = frame.entities.market or frame.entities.city or (frame.entities.markets[0] if frame.entities.markets else None)
            if got_market and got_market.lower() == expected_market.lower():
                market_correct += 1
            else:
                failures.append(f"[{q_id}] Market Mismatch: Got {got_market}, Expected {expected_market}")

        # 4. Check Required Input (Leaf image gate)
        expected_input = item["expected_required_input"]
        if frame.required_input.value == expected_input:
            input_gate_correct += 1
        else:
            failures.append(f"[{q_id}] RequiredInput Mismatch: Got {frame.required_input.value}, Expected {expected_input}")

        # 5. Check Capabilities (Subset or exact match)
        expected_caps = item.get("expected_capabilities", [])
        actual_caps = [c.value for c in frame.required_capabilities]
        all_caps_matched = all(c in actual_caps for c in expected_caps)
        if all_caps_matched:
            capabilities_correct += 1

    intent_acc = (intent_correct / total) * 100
    crop_acc = (crop_correct / crop_evaluated * 100) if crop_evaluated else 100.0
    market_acc = (market_correct / market_evaluated * 100) if market_evaluated else 100.0
    input_gate_acc = (input_gate_correct / total) * 100
    caps_acc = (capabilities_correct / total) * 100

    print(f"\n=======================================================")
    print(f"PHASE F3 SEMANTIC EXTRACTION EVALUATION REPORT (100 Queries)")
    print(f"=======================================================")
    print(f"Total Evaluated Queries:       {total}")
    print(f"Intent Accuracy:              {intent_acc:.2f}% ({intent_correct}/{total})")
    print(f"Crop Entity Accuracy:         {crop_acc:.2f}% ({crop_correct}/{crop_evaluated})")
    print(f"Market Entity Accuracy:       {market_acc:.2f}% ({market_correct}/{market_evaluated})")
    print(f"Required Input Gate Accuracy: {input_gate_acc:.2f}% ({input_gate_correct}/{total})")
    print(f"Capability Detection Accuracy:{caps_acc:.2f}% ({capabilities_correct}/{total})")
    print(f"=======================================================")

    if failures:
        print("Sample Failure Details (First 5):")
        for f in failures[:5]:
            print(f"  - {f}")

    assert intent_acc >= 95.0, f"Intent accuracy {intent_acc:.2f}% is below 95%"
    assert input_gate_acc >= 98.0, f"Input gate accuracy {input_gate_acc:.2f}% is below 98%"
    assert crop_acc >= 90.0, f"Crop accuracy {crop_acc:.2f}% is below 90%"


@pytest.mark.asyncio
async def test_multiturn_context_inheritance():
    """
    Test that SemanticFrame inherits active crop and farm location across turns.
    Turn 1: 'Gehu ka bhav batao.' -> crop=Wheat
    Turn 2: 'Jaipur mein.' -> crop=Wheat, market=Jaipur
    """
    # Turn 1
    frame_turn1 = await extract_semantic_frame(
        raw_text="Gehu ka bhav batao.",
        detected_language="hi",
        session_id="multi_turn_test_sess",
    )
    assert frame_turn1.intent == CanonicalIntent.MANDI_PRICE
    assert frame_turn1.entities.crop == "Wheat"

    # Context passed to Turn 2
    conv_ctx = ConversationContext(
        turn_index=1,
        active_crop="Wheat",
        last_intent="mandi_price",
    )

    # Turn 2
    frame_turn2 = await extract_semantic_frame(
        raw_text="Jaipur mein.",
        detected_language="hi",
        conversation_context=conv_ctx,
        session_id="multi_turn_test_sess",
    )
    # Inherits Wheat from context and extracts Jaipur from text
    assert frame_turn2.entities.crop == "Wheat"
    assert frame_turn2.entities.market == "Jaipur"
    assert frame_turn2.intent == CanonicalIntent.MANDI_PRICE


@pytest.mark.asyncio
async def test_contextual_location_inheritance():
    """
    If farmer context has a registered location, use it when none is spoken.
    """
    user_ctx = UserContext(
        farm_location=FarmLocation(
            city="Udaipur",
            district="Udaipur",
            state="Rajasthan",
            latitude=24.5854,
            longitude=73.7125,
        )
    )

    frame = await extract_semantic_frame(
        raw_text="आज मौसम कैसा रहेगा?",
        detected_language="hi",
        user_context=user_ctx,
    )
    assert frame.intent == CanonicalIntent.WEATHER
    assert frame.entities.city == "Udaipur"
    assert frame.entities.district == "Udaipur"
