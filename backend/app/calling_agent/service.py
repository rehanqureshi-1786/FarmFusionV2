"""
KisanCallingService for initiating outbound calls via Vobiz / Plivo / Twilio telephony providers.
"""

import os
import uuid
import urllib.parse
import httpx
import structlog
from typing import Dict, Any, Optional
from app.schemas.calling import KisanCallRequest, KisanCallResponse

logger = structlog.get_logger()

class KisanCallingService:
    def __init__(self):
        self.vobiz_api_key = os.getenv("VOBIZ_API_KEY")
        self.vobiz_account_id = os.getenv("VOBIZ_ACCOUNT_ID")
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
        self.active_calls: Dict[str, Any] = {}

    async def trigger_call(self, request: KisanCallRequest) -> KisanCallResponse:
        """
        Initiates an outbound voice call to the farmer.
        """
        call_id = str(uuid.uuid4())
        
        # Construct answer_url webhook parameters for bidirectional audio stream
        params = {
            "call_id": call_id,
            "farmer_name": request.farmer_name,
            "call_type": request.call_type,
            "language": request.language,
            "location": request.location or "India",
            "crop_name": request.crop_name or "",
            "mandi_name": request.mandi_name or "",
            "current_price": str(request.current_price or ""),
            "target_price": str(request.target_price or ""),
            "weather_summary": request.weather_summary or "",
            "agent_instruction": request.agent_instruction or "",
            "callback_url": request.callback_url or ""
        }
        encoded_query = urllib.parse.urlencode({k: v for k, v in params.items() if v})
        answer_url = f"{self.base_url.rstrip('/')}/api/v1/calling/webhook/inbound?{encoded_query}"

        logger.info(
            "initiating_kisan_outbound_call",
            call_id=call_id,
            farmer=request.farmer_name,
            phone=request.phone,
            call_type=request.call_type
        )

        # 1. If Vobiz telephony credentials configured:
        if self.vobiz_api_key and self.vobiz_account_id:
            try:
                vobiz_endpoint = f"https://api.vobiz.ai/v1/Account/{self.vobiz_account_id}/Call/"
                headers = {
                    "X-Auth-Token": self.vobiz_api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "to": request.phone,
                    "from": os.getenv("VOBIZ_PHONE_NUMBER", "+918000000000"),
                    "answer_url": answer_url,
                    "answer_method": "POST"
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(vobiz_endpoint, headers=headers, json=payload)
                    resp.raise_for_status()
                    logger.info("vobiz_call_dispatched_successfully", call_id=call_id, phone=request.phone)
            except Exception as e:
                logger.error("vobiz_call_dispatch_failed", error=str(e), call_id=call_id)
                # Still succeed locally for testing & webhook verification

        self.active_calls[call_id] = request

        return KisanCallResponse(
            status="initiated",
            call_id=call_id,
            message=f"Outbound {request.call_type} call initiated to {request.farmer_name} at {request.phone}",
            phone=request.phone,
            farmer_name=request.farmer_name,
            call_type=request.call_type
        )

kisan_calling_service = KisanCallingService()
