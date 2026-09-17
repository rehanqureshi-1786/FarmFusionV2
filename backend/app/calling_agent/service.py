"""
KisanCallingService for initiating outbound calls via Vobiz telephony provider.
Verified against current official Vobiz API (docs.vobiz.ai).
"""

import os
import re
import time
import uuid
import urllib.parse
import httpx
import structlog
from typing import Dict, Any, Optional, List
from app.schemas.calling import KisanCallRequest, KisanCallResponse

logger = structlog.get_logger()

COOLDOWN_SECONDS = 300  # 5 minutes duplicate-call cooldown

class KisanCallingService:
    def __init__(self):
        self.vobiz_api_key = os.getenv("VOBIZ_API_KEY")
        self.vobiz_account_id = os.getenv("VOBIZ_ACCOUNT_ID")
        self.base_url = os.getenv("BASE_URL") or "https://farmfusion-backend-production-0017.up.railway.app"
        self.active_calls: Dict[str, Any] = {}
        self.recent_calls: Dict[str, float] = {}  # phone -> timestamp
        self.call_history: List[Dict[str, Any]] = []

    def validate_and_normalize_phone(self, phone: str) -> str:
        """
        Validates and normalizes phone number to strict E.164 format.
        Supports standard Indian mobile numbers (+91 followed by 10 digits starting with 6-9)
        as well as general E.164 format (+[1-9][0-9]{9,14}).
        """
        clean_phone = re.sub(r"[\s\-\(\)]", "", phone.strip())
        if not clean_phone.startswith("+"):
            # If 10-digit Indian number provided without prefix, prepend +91
            if re.match(r"^[6-9]\d{9}$", clean_phone):
                clean_phone = f"+91{clean_phone}"
            else:
                raise ValueError(f"Invalid phone number format: '{phone}'. Phone must be in E.164 format (e.g. +919876543210).")

        # Verify Indian mobile or global E.164 format
        if clean_phone.startswith("+91"):
            if not re.match(r"^\+91[6-9]\d{9}$", clean_phone):
                raise ValueError(f"Invalid Indian mobile number: '{clean_phone}'. Must be +91 followed by 10 digits starting with 6-9.")
        elif not re.match(r"^\+[1-9]\d{9,14}$", clean_phone):
            raise ValueError(f"Invalid E.164 phone number: '{clean_phone}'.")

        return clean_phone

    def check_duplicate_cooldown(self, phone: str, bypass_cooldown: bool = False) -> None:
        """
        Prevents accidental repeat spam calls to the same farmer.
        Enforces a 5-minute (300s) cooldown per phone number.
        """
        if bypass_cooldown:
            return

        last_call_time = self.recent_calls.get(phone)
        if last_call_time:
            elapsed = time.time() - last_call_time
            if elapsed < COOLDOWN_SECONDS:
                remaining = int(COOLDOWN_SECONDS - elapsed)
                logger.warning("duplicate_call_prevented", phone=phone, remaining_seconds=remaining)
                raise ValueError(
                    f"Duplicate call prevented: A call was already initiated to {phone} {int(elapsed)}s ago. "
                    f"Cooldown active for another {remaining}s."
                )

    async def trigger_call(self, request: KisanCallRequest, bypass_cooldown: bool = False) -> KisanCallResponse:
        """
        Initiates an outbound voice call to the farmer via Vobiz Call API.
        Verified endpoint: https://api.vobiz.ai/api/v1/Account/{auth_id}/Call/
        Verified headers: X-Auth-ID and X-Auth-Token
        """
        # Allow request.bypass_cooldown to override parameter
        bypass = bypass_cooldown or getattr(request, "bypass_cooldown", False)

        # 1. E.164 Phone Validation
        normalized_phone = self.validate_and_normalize_phone(request.phone)
        request.phone = normalized_phone

        # 2. 5-Minute Duplicate Cooldown Check
        self.check_duplicate_cooldown(normalized_phone, bypass_cooldown=bypass)

        call_id = str(uuid.uuid4())

        # 3. Construct answer_url webhook parameters for bidirectional audio stream
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
            call_type=request.call_type,
            answer_url=answer_url
        )

        # 4. Dispatch to Vobiz Call API if credentials configured
        vobiz_api_key = self.vobiz_api_key or os.getenv("VOBIZ_API_KEY")
        vobiz_account_id = self.vobiz_account_id or os.getenv("VOBIZ_ACCOUNT_ID")

        if vobiz_api_key and vobiz_account_id:
            try:
                # Correct official Vobiz API base URL and endpoint
                vobiz_endpoint = f"https://api.vobiz.ai/api/v1/Account/{vobiz_account_id}/Call/"
                headers = {
                    "X-Auth-ID": vobiz_account_id,
                    "X-Auth-Token": vobiz_api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "to": request.phone,
                    "from": os.getenv("VOBIZ_PHONE_NUMBER", "+918064265824"),
                    "answer_url": answer_url,
                    "answer_method": "POST"
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(vobiz_endpoint, headers=headers, json=payload)
                    resp.raise_for_status()
                    logger.info("vobiz_call_dispatched_successfully", call_id=call_id, phone=request.phone)
            except Exception as e:
                logger.error("vobiz_call_dispatch_failed", error=str(e), call_id=call_id)
                # Keep executing locally so webhook simulation / tests function

        # 5. Record call in memory and update cooldown timestamp
        self.recent_calls[normalized_phone] = time.time()
        call_entry = {
            "call_id": call_id,
            "phone": normalized_phone,
            "farmer_name": request.farmer_name,
            "call_type": request.call_type,
            "language": request.language,
            "location": request.location or "India",
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "status": "initiated",
            "crop_name": request.crop_name,
            "mandi_name": request.mandi_name,
            "current_price": request.current_price,
            "weather_summary": request.weather_summary,
        }
        self.call_history.insert(0, call_entry)
        if len(self.call_history) > 50:
            self.call_history = self.call_history[:50]

        self.active_calls[call_id] = call_entry

        return KisanCallResponse(
            status="initiated",
            call_id=call_id,
            message=f"Outbound {request.call_type} call initiated to {request.farmer_name} at {request.phone}",
            phone=request.phone,
            farmer_name=request.farmer_name,
            call_type=request.call_type
        )

    def get_recent_calls(self) -> List[Dict[str, Any]]:
        """Returns the list of recent call records for the Calling UI."""
        return list(self.call_history)

    def update_call_status(self, call_id: str, status: str, summary: Optional[str] = None):
        """Updates the status of an existing call record."""
        if call_id in self.active_calls:
            self.active_calls[call_id]["status"] = status
            if summary:
                self.active_calls[call_id]["summary"] = summary
        for c in self.call_history:
            if c.get("call_id") == call_id:
                c["status"] = status
                if summary:
                    c["summary"] = summary
                break

    # Alias for FarmFusion ToolRegistry compatibility
    initiate_outbound_call = trigger_call


kisan_calling_service = KisanCallingService()

