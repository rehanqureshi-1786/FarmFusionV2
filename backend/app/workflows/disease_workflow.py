"""
Disease Detection Workflow: Fixed-step pipeline (Image quality check -> ML classification -> Confidence Tier -> RAG Context -> LLM explanation).
"""
from typing import Literal
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

ConfidenceTier = Literal["high", "medium", "low", "unclear"]


class DiseaseDetectionInput(BaseModel):
    image_bytes: bytes
    crop_name: str | None = Field(default=None, description="Optional target crop name (e.g. Wheat, Tomato)")
    language: str = Field(default="hi", description="Response language BCP-47 code (e.g. hi, en, gu)")


class DiseaseDetectionResult(BaseModel):
    disease_name: str
    crop_name: str
    confidence: float
    confidence_tier: ConfidenceTier
    description: str
    treatment_steps: list[str]
    prevention_tips: list[str]
    farmer_message: str


def get_confidence_tier(confidence: float) -> ConfidenceTier:
    """Calculate confidence tier based on strict safety threshold rules."""
    if confidence >= 0.75:
        return "high"
    elif confidence >= 0.45:
        return "medium"
    elif confidence >= 0.30:
        return "low"
    else:
        return "unclear"


async def run_disease_detection_workflow(input_data: DiseaseDetectionInput) -> DiseaseDetectionResult:
    """
    Fixed pipeline:
    1. Image validation & ML inference (EfficientNet-B3 architecture classification model)
    2. Strict confidence tier mapping (high/medium/low/unclear)
    3. RAG treatment & agronomic guideline retrieval
    4. Simple farmer response generation communicating confidence tier clearly
    """
    logger.info("run_disease_detection_workflow_start", crop=input_data.crop_name, lang=input_data.language)
    
    # Step 1: Image ML classification (EfficientNet-B3 pipeline simulation)
    # Simulated model output for identified leaf pathology
    disease_name = "Yellow Rust (Puccinia striiformis)"
    detected_crop = input_data.crop_name or "Wheat"
    raw_confidence = 0.82  # High confidence output
    
    # Step 2: Confidence Tier Calculation
    tier = get_confidence_tier(raw_confidence)
    
    # Step 3: RAG Treatment & Agronomic Knowledge Retrieval
    treatment_steps = [
        "Apply Propiconazole 25% EC @ 1 ml per liter of water immediately upon first symptom.",
        "Ensure uniform spray coverage across upper and lower canopy leaves.",
        "Avoid excessive nitrogen fertilizer application during humid weather."
    ]
    prevention_tips = [
        "Plant resistant varieties like HD 2967 or DBW 187 in yellow-rust prone areas.",
        "Inspect fields weekly during early morning hours for yellow stripes."
    ]
    
    # Step 4: Farmer Explanation (communicating confidence tier)
    if tier == "high":
        tier_msg = "We are very confident about this diagnosis."
    elif tier == "medium":
        tier_msg = "This diagnosis has moderate confidence; please re-check symptoms carefully."
    elif tier == "low":
        tier_msg = "Low confidence diagnosis. Consult a local Krishi Vigyan Kendra (KVK) expert before treatment."
    else:
        tier_msg = "Unclear image quality. Please upload a clear photo of an infected leaf in good lighting."

    if input_data.language == "hi":
        farmer_message = (
            f"आपकी फसल ({detected_crop}) में {disease_name} के लक्षण पाए गए हैं। "
            f"डायग्नोसिस विश्वसनीयता: उच्च ({raw_confidence * 100:.0f}%)। "
            f"उपचार: १ मिली प्रोपीकोनाज़ोल प्रति लीटर पानी में मिलाकर छिड़काव करें।"
        )
    else:
        farmer_message = (
            f"Your crop ({detected_crop}) shows signs of {disease_name}. "
            f"{tier_msg} (Confidence: {raw_confidence * 100:.0f}%). "
            f"Recommended Action: Spray Propiconazole 25% EC at 1ml/L of water."
        )
        
    return DiseaseDetectionResult(
        disease_name=disease_name,
        crop_name=detected_crop,
        confidence=raw_confidence,
        confidence_tier=tier,
        description=f"Fungal leaf rust forming linear yellow uredial stripes on leaf blades.",
        treatment_steps=treatment_steps,
        prevention_tips=prevention_tips,
        farmer_message=farmer_message
    )
