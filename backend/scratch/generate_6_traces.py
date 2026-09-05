"""
Generate live end-to-end traces for the 6 canonical scenarios:
1. Disease + RAG
2. Crop + RAG
3. Weather + Irrigation
4. Mandi + Forecast
5. Disaster + RAG
6. Disease without image -> navigation
"""
import asyncio
import json
from app.orchestrator.graph import orchestrator_graph
from app.orchestrator.state import OrchestratorState


async def run_trace(name: str, initial_state: OrchestratorState):
    print("=" * 80)
    print(f"CANONICAL TRACE: {name}")
    print("=" * 80)
    final_state = await orchestrator_graph.ainvoke(
        initial_state,
        config={"configurable": {"thread_id": f"trace_{name.lower().replace(' ', '_')}"}}
    )
    
    print("\n[STAGE 1: INPUT]")
    print(f"User Query: {final_state.get('user_input')}")
    print(f"Detected Language: {final_state.get('detected_language')}, Dialect: {final_state.get('detected_dialect')}")
    
    print("\n[STAGE 2: INTENT & PLANNER]")
    print(f"Intent: {final_state.get('intent')} (Confidence: {final_state.get('intent_confidence')})")
    print(f"Next Action: {final_state.get('next_action')}")
    task_plan = final_state.get("task_plan")
    if task_plan:
        print(f"Planned Tasks: {[t.get('capability') for t in task_plan.get('tasks', [])]}")
        
    print("\n[STAGE 3: TOOL EXECUTION]")
    print(f"Completed Tasks: {final_state.get('completed_tasks')}")
    print(f"Tool Output Keys: {list(final_state.get('tool_output', {}).keys())}")
    
    print("\n[STAGE 4: CONDITIONAL RAG GROUNDING]")
    rag = final_state.get("rag_grounding") or {}
    print(f"Status: {rag.get('status')}")
    print(f"Domain: {rag.get('domain')}")
    print(f"Evidence Level: {rag.get('evidence_level')}")
    print(f"Formulated Query: {rag.get('query')}")
    print(f"Citations Count: {len(rag.get('citations', []))}")
    if rag.get("citations"):
        for c in rag["citations"][:2]:
            print(f"  - Source: {c.get('title')} ({c.get('organization')}) | URL: {c.get('source_url')}")
            
    print("\n[STAGE 5: VALIDATION & SAFETY]")
    val = final_state.get("validation_result") or {}
    print(f"Is Valid: {val.get('is_valid')}")
    print(f"Confidence Tier: {val.get('confidence_tier')}")
    facts = final_state.get("verified_facts") or []
    print(f"Verified Fact Set ({len(facts)} facts):")
    for f in facts:
        print(f"  - {f.get('key')}: {f.get('value')} {f.get('unit') or ''}")
    print(f"Warnings: {val.get('warnings')}")
    
    print("\n[STAGE 6: RESPONSE ENVELOPE]")
    env = final_state.get("response_envelope") or {}
    print(f"Action: {env.get('action_payload', {}).get('action')}")
    if env.get('action_payload', {}).get('destination'):
        print(f"Destination: {env.get('action_payload', {}).get('destination')}")
    if env.get('action_payload', {}).get('required_input'):
        print(f"Required Input: {env.get('action_payload', {}).get('required_input')}")
    if env.get('action_payload', {}).get('call_reason'):
        print(f"Call Reason: {env.get('action_payload', {}).get('call_reason')}")
    print(f"Response Text: \"{env.get('response_text')}\"")
    print(f"Confidence: {env.get('confidence')}")
    print("=" * 80 + "\n")


from io import BytesIO
from PIL import Image


def get_real_leaf_image_bytes():
    buf = BytesIO()
    img = Image.new("RGB", (300, 300), color="green")
    img.save(buf, format="JPEG")
    return buf.getvalue()


async def main():
    # 1. Disease + RAG (with valid leaf image)
    await run_trace("1. Disease + RAG", {
        "user_input": "मेरी टमाटर की फसल में पत्ती पर धब्बे दिख रहे हैं, यह कौन सा रोग है?",
        "detected_language": "hi",
        "detected_dialect": None,
        "session_id": "s_disease_rag",
        "active_crop": "Tomato",
        "image_bytes": get_real_leaf_image_bytes(),
    })

    # 2. Crop + RAG
    await run_trace("2. Crop + RAG", {
        "user_input": "कोटा में रबी के लिए कौन सी फसल लगाना सबसे अच्छा रहेगा?",
        "detected_language": "hi",
        "detected_dialect": None,
        "session_id": "s_crop_rag",
        "farmer_context": {"location_name": "Kota", "latitude": 25.18, "longitude": 75.83},
    })

    # 3. Weather + Irrigation
    await run_trace("3. Weather + Irrigation", {
        "user_input": "आज मौसम कैसा रहेगा और क्या गेहूं में पानी देना चाहिए?",
        "detected_language": "hi",
        "detected_dialect": None,
        "session_id": "s_weather_irrigation",
        "active_crop": "Wheat",
        "farmer_context": {"location_name": "Jaipur", "latitude": 26.91, "longitude": 75.78},
    })

    # 4. Mandi + Forecast
    await run_trace("4. Mandi + Forecast", {
        "user_input": "कोटा मंडी में सोयाबीन का क्या भाव है और क्या मुझे अभी बेचना चाहिए?",
        "detected_language": "hi",
        "detected_dialect": None,
        "session_id": "s_mandi_forecast",
        "farmer_context": {"location_name": "Kota"},
    })

    # 5. Disaster + RAG
    await run_trace("5. Disaster + RAG", {
        "user_input": "क्या अगले हफ्ते बाड़मेर में बाढ़ या भारी बारिश का खतरा है?",
        "detected_language": "hi",
        "detected_dialect": None,
        "session_id": "s_disaster_rag",
        "farmer_context": {"location_name": "Barmer", "latitude": 25.75, "longitude": 71.40},
    })

    # 6. Disease without image -> navigation
    await run_trace("6. Disease without image -> navigation", {
        "user_input": "मेरी फसल में कोई कीड़ा या बीमारी लग गई है, जांच करो",
        "detected_language": "hi",
        "detected_dialect": None,
        "session_id": "s_disease_no_image",
    })


if __name__ == "__main__":
    asyncio.run(main())
