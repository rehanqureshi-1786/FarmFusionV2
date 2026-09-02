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
        return await kisan_calling_service.trigger_call(request)
    except ValueError as e:
        status_code = 429 if "cooldown active" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error("call_initiation_unexpected_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to initiate call: {str(e)}")

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
    Inbound webhook called by Vobiz / Plivo when the farmer answers the call.
    Returns XML instructions to establish a bidirectional audio stream via WebSocket.
    """
    query_params = dict(request.query_params)
    base_ws = settings.base_ws_url or os.getenv("BASE_WS_URL", "wss://farmfusion.app")
    ws_query = urllib.parse.urlencode(query_params)
    stream_url = f"{base_ws.rstrip('/')}/ws/calling/stream?{ws_query}"

    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Connecting to Kisan Mitra.</Speak>
    <Stream bidirectional="true" keepCallAlive="true">{stream_url}</Stream>
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
    call_id = query_params.get("call_id")

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
        call_id=call_id
    )

    try:
        # Start orchestrator greeting
        await orchestrator.start()

        while True:
            raw_text = await websocket.receive_text()
            data = json.loads(raw_text)
            event = data.get("event")

            # 1. Connection initiation metadata event
            if event == "start":
                logger.info("telephony_stream_metadata_received", call_id=call_id, format=data.get("mediaFormat"))

            # 2. Inbound audio chunk from phone (supports both "media" and "playAudio" frame envelopes)
            elif event in ("media", "playAudio"):
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
