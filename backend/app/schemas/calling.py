from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class KisanCallRequest(BaseModel):
    phone: str = Field(..., description="Farmer's phone number with country code (e.g. +919876543210)")
    farmer_name: str = Field(..., description="Full name of the farmer")
    call_type: str = Field("general_advisory", description="mandi_price_alert | weather_warning | pest_advisory | crop_guidance | general_advisory")
    language: str = Field("hi", description="BCP-47 language code (hi, en, gu, mr, pa, bn, ta, te, kn)")
    location: Optional[str] = Field("India", description="Farmer village, district or state")
    crop_name: Optional[str] = Field(None, description="Target crop (e.g. Wheat, Gram, Mustard)")
    mandi_name: Optional[str] = Field(None, description="Relevant Mandi name if mandi price alert")
    current_price: Optional[float] = Field(None, description="Current market price per quintal")
    target_price: Optional[float] = Field(None, description="Target alert price per quintal")
    weather_summary: Optional[str] = Field(None, description="Current weather or forecast warning")
    agent_instruction: Optional[str] = Field(
        None,
        description="Custom dynamic prompt instruction injected directly into the LLM conversation."
    )
    callback_url: Optional[str] = Field(None, description="Webhook URL to receive post-call transcript and AI summary")

class KisanCallResponse(BaseModel):
    status: str = "success"
    call_id: str
    message: str
    phone: str
    farmer_name: str
    call_type: str

class CallTranscriptTurn(BaseModel):
    speaker: str
    text: str

class KisanCallSummaryResponse(BaseModel):
    call_id: str
    farmer_name: str
    phone: str
    status: str
    call_type: str
    summary: str
    transcript: List[CallTranscriptTurn] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
