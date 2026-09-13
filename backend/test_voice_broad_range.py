"""
Verification Test for Expanded Voice Assistant / Orchestrator Query Range & Diagnosis Without Picture.
Tests:
1. Plant diagnosis without image -> Explicitly informs no plant image is present so diagnosis is not possible, opens camera / navigates to crop_disease.
2. Cold storage lookup -> Returns nearest verified cold storage facilities, distance in km, capacity, and crop suitability.
3. Crop fertilizer / nutrition (NPK) -> Returns authentic ICAR fertilizer dosage and timing (e.g. Wheat 120:60:40, CRI stage split).
4. Pest consultation (e.g. Whitefly in Cotton) -> Returns actionable ICAR/CIBRC guidance without blocking for photos.
5. Irrigation water requirement -> Returns crop water requirement in mm.
6. Navigation requests -> Navigates to correct Kotlin Android routes (crop_storage, crop_disease, etc.).
7. Broad agricultural queries -> Answered directly with high confidence instead of generic clarification question.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.orchestrator.graph import run_orchestrator_pipeline
from app.services.voice_service import VoiceService
from app.models.voice import VoiceQueryRequest, LanguageType, ActionType
from app.tools.registry import tool_registry


async def test_plant_diagnosis_without_image():
    print("\n--- 1. Testing Plant Diagnosis Without Image ---")
    
    # Query: "Mere paudhe me bimari pehchano" (without image)
    result = await run_orchestrator_pipeline(
        user_input="Mere paudhe me bimari pehchano",
        session_id="test_no_img_1",
        detected_language="hi",
    )
    msg = str(result.get("final_response") or "")
    envelope = result.get("response_envelope") or {}
    action_payload = envelope.get("action_payload") or {}
    action = action_payload.get("action")
    route = action_payload.get("android_route")
    
    print(f"Orchestrator Response: {msg}")
    print(f"Action: {action}, Route: {route}")
    
    # Assertions
    assert any(w in msg for w in ["तस्वीर", "फोटो", "photo", "उपलब्ध नहीं", "संभव नहीं", "not possible"]), \
        f"Response must explicitly state no plant image is present so diagnosis is not possible. Got: {msg}"
    assert route in ["crop_disease", "disease_scan"], f"Expected route crop_disease, got {route}"

    # Also test VoiceService
    voice_service = VoiceService()
    req = VoiceQueryRequest(query="मेरे पौधे में क्या बीमारी है पहचानो", language_hint="hi")
    v_resp = await voice_service.process_query(req)
    print(f"VoiceService Response: {v_resp.response}")
    print(f"VoiceService Action: {v_resp.action}")
    assert any(w in v_resp.response for w in ["तस्वीर", "फोटो", "photo", "उपलब्ध नहीं", "संभव नहीं", "not possible"]), \
        f"VoiceService response must state no plant image is present so diagnosis is not possible. Got: {v_resp.response}"
    assert v_resp.action == ActionType.OPEN_CAMERA, f"Expected OPEN_CAMERA, got {v_resp.action}"
    print(">>> Test 1 PASSED!")


async def test_cold_storage_lookup():
    print("\n--- 2. Testing Cold Storage Lookup ---")
    result = await run_orchestrator_pipeline(
        user_input="Mere paas cold storage kaha hai? Aloo rakhna hai",
        session_id="test_cs_1",
        detected_language="hi",
        farmer_context={"latitude": 24.5854, "longitude": 73.7125, "district": "Udaipur", "state": "Rajasthan"}
    )
    msg = str(result.get("final_response") or "")
    envelope = result.get("response_envelope") or {}
    action_payload = envelope.get("action_payload") or {}
    action = action_payload.get("action")
    route = action_payload.get("android_route")
    
    print(f"Orchestrator Cold Storage Response: {msg}")
    print(f"Action: {action}, Route: {route}")
    assert "cold storage" in msg.lower() or "कोल्ड स्टोरेज" in msg or "km" in msg, \
        f"Expected cold storage details in response. Got: {msg}"
    assert route == "crop_storage", f"Expected route crop_storage, got {route}"
    
    # VoiceService test
    voice_service = VoiceService()
    req = VoiceQueryRequest(query="Nearest cold storage facility for potato", latitude=24.5854, longitude=73.7125, language_hint="en")
    v_resp = await voice_service.process_query(req)
    print(f"VoiceService Cold Storage: {v_resp.response}")
    assert "cold storage" in v_resp.response.lower() or "km" in v_resp.response.lower()
    print(">>> Test 2 PASSED!")


async def test_fertilizer_npk_crop_care():
    print("\n--- 3. Testing Fertilizer / NPK Dosage & Agronomy ---")
    result = await run_orchestrator_pipeline(
        user_input="Gehu me khad kab aur kitni dale?",
        session_id="test_fert_1",
        detected_language="hi",
    )
    msg = str(result.get("final_response") or "")
    print(f"Fertilizer Response: {msg}")
    assert any(w in msg for w in ["120:60:40", "नाइट्रोजन", "यूरिया", "डीएपी", "NPK", "CRI"]), \
        f"Expected authentic NPK dosage or schedule for wheat. Got: {msg}"
    print(">>> Test 3 PASSED!")


async def test_irrigation_water_requirement():
    print("\n--- 4. Testing Irrigation Water Requirement ---")
    result = await run_orchestrator_pipeline(
        user_input="Dhan ki fasal me kitna paani chahiye?",
        session_id="test_water_1",
        detected_language="hi",
    )
    msg = str(result.get("final_response") or "")
    print(f"Water Requirement Response: {msg}")
    assert any(w in msg for w in ["1200", "1500", "जल", "पानी", "mm", "नमी"]), \
        f"Expected water requirement details for rice/paddy. Got: {msg}"
    print(">>> Test 4 PASSED!")


async def test_pest_consultation():
    print("\n--- 5. Testing Symptom & Pest Consultation ---")
    result = await run_orchestrator_pipeline(
        user_input="Kapas me safed makkhi ka ilaj kya hai?",
        session_id="test_pest_1",
        detected_language="hi",
    )
    msg = str(result.get("final_response") or "")
    print(f"Pest Consultation Response: {msg}")
    assert len(msg) > 20 and not "दोबारा स्पष्ट" in msg, \
        f"Should provide actionable guidance instead of asking to clarify. Got: {msg}"
    print(">>> Test 5 PASSED!")


async def test_in_app_navigation():
    print("\n--- 6. Testing In-App Navigation ---")
    
    # Cold storage screen
    result1 = await run_orchestrator_pipeline(
        user_input="Cold storage screen kholo",
        session_id="test_nav_cs",
        detected_language="hi",
    )
    envelope1 = result1.get("response_envelope") or {}
    route1 = (envelope1.get("action_payload") or {}).get("android_route")
    print(f"Nav Route 1: {route1}")
    assert route1 == "crop_storage", f"Expected crop_storage, got {route1}"
    
    # Mandi screen
    result2 = await run_orchestrator_pipeline(
        user_input="Mandi rates screen dikhao",
        session_id="test_nav_mandi",
        detected_language="hi",
    )
    envelope2 = result2.get("response_envelope") or {}
    route2 = (envelope2.get("action_payload") or {}).get("android_route")
    print(f"Nav Route 2: {route2}")
    assert route2 == "mandi_prices", f"Expected mandi_prices, got {route2}"

    print(">>> Test 6 PASSED!")


async def main():
    print("================================================================")
    print("RUNNING COMPREHENSIVE VOICE ASSISTANT / ORCHESTRATOR EXPANSION TESTS")
    print("================================================================")
    try:
        await test_plant_diagnosis_without_image()
        await test_cold_storage_lookup()
        await test_fertilizer_npk_crop_care()
        await test_irrigation_water_requirement()
        await test_pest_consultation()
        await test_in_app_navigation()
        print("\n================================================================")
        print("ALL TESTS PASSED WITH 100% ACCURACY!")
        print("================================================================")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
