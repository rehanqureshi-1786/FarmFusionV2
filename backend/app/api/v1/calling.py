"""
FastAPI router for FarmFusion Kisan Voice Calling Agent.
Verified against Vobiz Webhook & WebSocket Media Stream specifications.
"""

import os
import json
import base64
import asyncio
import urllib.parse
import structlog
import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Response, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.schemas.calling import KisanCallRequest, KisanCallResponse, KisanCallSummaryResponse, CallTranscriptTurn
from app.calling_agent.service import kisan_calling_service
from app.calling_agent.orchestrator import KisanVoiceOrchestrator
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/calling", tags=["Kisan Calling Agent"])

@router.post("/call", response_model=KisanCallResponse)
async def initiate_kisan_call(request: KisanCallRequest):
    """
    Initiates an AI outbound phone call to a farmer for mandi alerts, weather warnings, or advisory.
    Validates E.164 phone numbers and enforces 5-minute duplicate-call cooldown.
    """
    try:
        return await kisan_calling_service.trigger_call(request, bypass_cooldown=request.bypass_cooldown)
    except ValueError as e:
        status_code = 429 if "cooldown active" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error("call_initiation_unexpected_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to initiate call: {str(e)}")

@router.get("/recent")
async def get_recent_kisan_calls():
    """Returns real-time list of recent calls for the Calling Agent Dashboard UI."""
    return {
        "calls": kisan_calling_service.get_recent_calls(),
        "vobiz_number": os.getenv("VOBIZ_PHONE_NUMBER", "+918064265824"),
        "env_diagnostics": {
            "has_groq": bool(os.getenv("GROQ_API_KEY") or settings.groq_api_key),
            "has_sarvam": bool(os.getenv("SARVAM_API_KEY") or settings.sarvam_api_key),
            "has_openrouter": bool(os.getenv("OPENROUTER_API_KEY") or settings.openrouter_api_key),
        },
        "status": "ready"
    }

@router.post("/simulate-turn")
async def simulate_calling_turn(payload: dict):
    """
    Simulates an interactive voice turn with the LangGraph Orchestrator for the Calling UI.
    Enables live testing and validation directly in the web browser.
    """
    from app.orchestrator.graph import run_orchestrator_pipeline
    from app.calling_agent.orchestrator import KisanVoiceOrchestrator

    user_input = payload.get("user_input", "").strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="user_input is required")

    farmer_name = payload.get("farmer_name", "Kisan")
    language = payload.get("language", "hi")
    location = payload.get("location", "India")
    crop_name = payload.get("crop_name") or None
    mandi_name = payload.get("mandi_name") or None
    session_id = payload.get("session_id") or f"sim_{farmer_name}"

    farmer_ctx = {
        "farmer_name": farmer_name,
        "name": farmer_name,
        "location_name": location,
        "city": location,
        "active_crop": crop_name,
        "active_market": mandi_name,
        "session_type": "telephony",
    }

    try:
        res = await run_orchestrator_pipeline(
            user_input=user_input,
            detected_language=language,
            session_id=session_id,
            farmer_context=farmer_ctx,
            active_crop=crop_name,
        )

        raw_resp = (
            res.get("final_response")
            or (res.get("response_envelope") or {}).get("response_text")
            or ""
        )
        clean_resp = KisanVoiceOrchestrator._clean_for_telephony(raw_resp)
        if not clean_resp:
            clean_resp = (
                f"जी {farmer_name} जी, आपकी बात समझ आ गई है।"
                if language == "hi"
                else f"Understood {farmer_name}. FarmFusion is here to assist you."
            )

        return {
            "user_input": user_input,
            "response_text": clean_resp,
            "intent": res.get("intent"),
            "completed_tasks": res.get("completed_tasks", []),
            "session_id": session_id,
            "active_crop": res.get("active_crop") or crop_name,
            "active_market": res.get("active_market") or mandi_name,
        }
    except Exception as e:
        logger.error("simulation_turn_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@router.get("/ui")
async def serve_calling_agent_ui():
    """Serves the interactive Calling Agent Web UI."""
    from fastapi.responses import FileResponse
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    _repo_root = os.path.dirname(_backend_dir)
    _calling_html = os.path.join(_repo_root, "dashboard", "calling.html")
    if not os.path.exists(_calling_html):
        _calling_html = os.path.join(_backend_dir, "dashboard", "calling.html")

    if os.path.exists(_calling_html):
        return FileResponse(_calling_html, media_type="text/html")
    raise HTTPException(status_code=404, detail="Calling UI HTML file not found")

@router.post("/trigger-mandi-alert", response_model=KisanCallResponse)
async def trigger_mandi_alert_call(
    phone: str,
    farmer_name: str,
    crop_name: str,
    mandi_name: str,
    current_price: float,
    target_price: float,
    language: str = "hi"
):
    """
    Convenience endpoint to trigger a phone call when a mandi crop price crosses the target threshold.
    """
    req = KisanCallRequest(
        phone=phone,
        farmer_name=farmer_name,
        call_type="mandi_price_alert",
        language=language,
        crop_name=crop_name,
        mandi_name=mandi_name,
        current_price=current_price,
        target_price=target_price,
        agent_instruction=f"Notify the farmer that {crop_name} in {mandi_name} mandi has reached ₹{int(current_price)}/quintal. Ask if they want to sell today or wait."
    )
    try:
        return await kisan_calling_service.trigger_call(req)
    except ValueError as e:
        status_code = 429 if "cooldown active" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))

@router.post("/trigger-weather-alert", response_model=KisanCallResponse)
async def trigger_weather_alert_call(
    phone: str,
    farmer_name: str,
    location: str,
    weather_warning: str,
    language: str = "hi"
):
    """
    Convenience endpoint to trigger a voice phone call for severe weather/frost/heavy rainfall alert.
    """
    req = KisanCallRequest(
        phone=phone,
        farmer_name=farmer_name,
        call_type="weather_warning",
        language=language,
        location=location,
        weather_summary=weather_warning,
        agent_instruction=f"Warn the farmer about upcoming weather: {weather_warning}. Advise crop protection measures."
    )
    try:
        return await kisan_calling_service.trigger_call(req)
    except ValueError as e:
        status_code = 429 if "cooldown active" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))

@router.api_route("/webhook/inbound", methods=["GET", "POST"])
async def telephony_inbound_webhook(request: Request):
    """
    Inbound webhook called by Vobiz / Plivo when the farmer answers or dials the call.
    Returns XML instructions to establish a bidirectional audio stream via WebSocket.
    """
    query_params = dict(request.query_params)
    if request.method == "POST":
        try:
            form_data = await request.form()
            for k, v in form_data.items():
                if k not in query_params:
                    query_params[k] = str(v)
        except Exception:
            pass

    # Extract incoming caller phone number if this is an inbound call from a farmer
    caller_phone = query_params.get("From")
    if caller_phone and "farmer_name" not in query_params:
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.user import User
            from sqlalchemy import select
            clean_digits = "".join(filter(str.isdigit, caller_phone))[-10:]
            if clean_digits:
                async with AsyncSessionLocal() as db_session:
                    stmt = select(User).where(User.phone.like(f"%{clean_digits}"))
                    res = await db_session.execute(stmt)
                    user = res.scalars().first()
                    if user:
                        if user.full_name:
                            query_params["farmer_name"] = user.full_name
                        if user.preferred_language:
                            query_params["language"] = user.preferred_language
                        loc = user.district or user.village or user.state
                        if loc:
                            query_params["location"] = loc
        except Exception as e:
            logger.warning("inbound_farmer_db_lookup_error", error=str(e))

    req_host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.hostname
    if req_host and ("railway.app" in req_host or "trycloudflare.com" in req_host or "ngrok" in req_host):
        base_ws = f"wss://{req_host}"
    else:
        base_ws = settings.base_ws_url or os.getenv("BASE_WS_URL", "wss://farmfusion-backend-production-0017.up.railway.app")
    ws_query = urllib.parse.urlencode(query_params)
    if ws_query:
        escaped_query = ws_query.replace("&", "&amp;")
        stream_url = f"{base_ws.rstrip('/')}/ws/calling/stream?{escaped_query}"
    else:
        stream_url = f"{base_ws.rstrip('/')}/ws/calling/stream"

    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Stream bidirectional="true" keepCallAlive="true" contentType="audio/x-mulaw;rate=8000">{stream_url}</Stream>
</Response>"""
    return Response(content=xml_response, media_type="application/xml")



@router.api_route("/webhook/hangup", methods=["GET", "POST"])
async def telephony_hangup_webhook(request: Request):
    """
    Webhook called by Vobiz when a call ends/hangs up.
    Captures call termination reason, duration, and status.
    """
    try:
        data = {}
        if request.method == "POST":
            try:
                data = await request.json()
            except Exception:
                data = dict(await request.form())
        else:
            data = dict(request.query_params)
        logger.info("telephony_call_hangup_logged", data=data)
        return JSONResponse(content={"status": "hangup_logged"})
    except Exception as e:
        logger.warning("hangup_logging_error", error=str(e))
        return JSONResponse(content={"status": "error", "message": str(e)})

@router.api_route("/webhook/fallback", methods=["GET", "POST"])
async def telephony_fallback_webhook(request: Request):
    """
    Fallback webhook called by Vobiz if the primary answer URL fails.
    """
    logger.warning("telephony_fallback_answer_invoked")
    xml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Kisan Mitra service is reconnecting. Please stay on the line.</Speak>
</Response>"""
    return Response(content=xml_response, media_type="application/xml")

@router.websocket("/ws/calling/stream")
async def telephony_audio_stream_endpoint(websocket: WebSocket):
    """
    Bi-directional audio WebSocket connecting telephony network to KisanVoiceOrchestrator.
    Supports Vobiz events: start, media, playAudio, clearAudio, clearedAudio, and stop/close.
    """
    await websocket.accept()
    query_params = dict(websocket.query_params)

    farmer_name = query_params.get("farmer_name", "Kisan")
    call_type = query_params.get("call_type", "general_advisory")
    language = query_params.get("language", "hi")
    location = query_params.get("location", "India")
    crop_name = query_params.get("crop_name") or None
    mandi_name = query_params.get("mandi_name") or None
    current_price = float(query_params.get("current_price")) if query_params.get("current_price") else None
    target_price = float(query_params.get("target_price")) if query_params.get("target_price") else None
    weather_summary = query_params.get("weather_summary") or None
    agent_instruction = query_params.get("agent_instruction") or None
    callback_url = query_params.get("callback_url") or None
    call_id = query_params.get("call_id") or query_params.get("CallUUID")
    phone = query_params.get("From") or query_params.get("phone") or None
    lat = float(query_params["latitude"]) if query_params.get("latitude") else None
    lon = float(query_params["longitude"]) if query_params.get("longitude") else None

    orchestrator = KisanVoiceOrchestrator(
        websocket=websocket,
        farmer_name=farmer_name,
        call_type=call_type,
        language=language,
        location=location,
        crop_name=crop_name,
        mandi_name=mandi_name,
        current_price=current_price,
        target_price=target_price,
        weather_summary=weather_summary,
        agent_instruction=agent_instruction,
        callback_url=callback_url,
        call_id=call_id,
        latitude=lat,
        longitude=lon,
        phone=phone
    )

    try:
        # Launch greeting task in background so it starts synthesizing while socket receives start event
        asyncio.create_task(orchestrator.start())

        while True:
            raw_text = await websocket.receive_text()
            data = json.loads(raw_text)
            event = data.get("event")

            # 1. Connection initiation metadata event from Vobiz
            if event == "start":
                stream_id = (
                    data.get("start", {}).get("streamId")
                    or data.get("streamId")
                    or data.get("start", {}).get("callId")
                    or call_id
                )
                if stream_id:
                    orchestrator.set_stream_id(stream_id)
                logger.info(
                    "telephony_stream_metadata_received",
                    call_id=call_id,
                    stream_id=stream_id,
                    format=data.get("start", {}).get("mediaFormat") or data.get("mediaFormat")
                )

            # 2. Inbound audio chunk from phone (supports both "media" and "playAudio" frame envelopes)
            elif event in ("media", "playAudio"):
                stream_id = data.get("streamId") or data.get("media", {}).get("streamId")
                if stream_id and not orchestrator.stream_id:
                    orchestrator.set_stream_id(stream_id)

                media_payload = data.get("media", {}).get("payload") or data.get("payload")
                if media_payload:
                    audio_bytes = base64.b64decode(media_payload)
                    await orchestrator.process_inbound_audio(audio_bytes)

            # 3. Barge-in playback queue flush acknowledgement from Vobiz
            elif event == "clearedAudio":
                logger.info("telephony_audio_cleared_ack", farmer=farmer_name, call_id=call_id)

            # 4. Call hung up or terminated
            elif event in ("stop", "close"):
                logger.info("telephony_call_hangup_received", farmer=farmer_name, call_id=call_id)
                break

    except WebSocketDisconnect:
        logger.info("telephony_websocket_disconnected", farmer=farmer_name)
    except Exception as e:
        logger.error("telephony_websocket_error", error=str(e))
    finally:
        await orchestrator.stop()

        # Generate summary and dispatch webhook if requested
        summary = await orchestrator.generate_call_summary()
        logger.info("kisan_call_summary_generated", farmer=farmer_name, summary=summary)

        if callback_url:
            async def send_callback():
                try:
                    payload = {
                        "call_id": call_id,
                        "farmer_name": farmer_name,
                        "call_type": call_type,
                        "summary": summary,
                        "transcript": orchestrator.transcript_history
                    }
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        await client.post(callback_url, json=payload)
                except Exception as ex:
                    logger.warning("callback_dispatch_failed", error=str(ex))
            asyncio.create_task(send_callback())
