"""
Pydantic v2 schemas for Crop Disease Detection Agent.
"""
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

ConfidenceTier = Literal["high", "medium", "low", "unclear"]
DiagnosisStatus = Literal["identified", "possible", "uncertain", "healthy", "error"]


class TreatmentPlan(BaseModel):
    biological: List[str] = Field(default_factory=list, description="Biological and bio-control methods")
    cultural: List[str] = Field(default_factory=list, description="Cultural, sanitation, and preventive field practices")
    chemical: List[str] = Field(default_factory=list, description="Chemical controls with active ingredients and safety precautions")
    active_ingredients: List[str] = Field(default_factory=list, description="Recommended active ingredient molecules")
    treatment_notes: List[str] = Field(default_factory=list, description="Dosage guidance and disclaimers")


class StoreItemRecommendation(BaseModel):
    title: str
    subtitle: str
    category: str
    image_url: Optional[str] = None
    shop_url: str


class TopPredictionItem(BaseModel):
    class_name: str
    class_index: Optional[int] = None
    crop: Optional[str] = None
    disease: Optional[str] = None
    confidence: float
    confidence_tier: Optional[str] = None


class DiseaseDetectionData(BaseModel):
    crop_type: Optional[str] = None
    disease_name: str
    scientific_name: Optional[str] = None
    confidence: float
    confidence_tier: ConfidenceTier
    diagnosis_status: DiagnosisStatus
    severity: str = "unknown"
    description: str = ""
    symptoms: List[str] = Field(default_factory=list)
    causes: List[str] = Field(default_factory=list)
    favorable_conditions: List[str] = Field(default_factory=list)
    prevention_tips: List[str] = Field(default_factory=list)
    treatment_suggestions: List[str] = Field(default_factory=list)
    treatment: TreatmentPlan = Field(default_factory=TreatmentPlan)
    product_categories: List[str] = Field(default_factory=list)
    store_recommendations: List[StoreItemRecommendation] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    ai_analyzed: bool = True
    is_reliable: bool = True
    model_version: str = "v2_38class"
    top_predictions: List[TopPredictionItem] = Field(default_factory=list)
    inference_source: str = "ML_VISION"  # ML_VISION or GEMINI_FALLBACK or UNKNOWN
    message: Optional[str] = None
    timestamp: Optional[str] = None


class DiseaseDetectionResponse(BaseModel):
    success: bool
    data: Optional[DiseaseDetectionData] = None
    error: Optional[str] = None


class DiseaseHistoryItem(BaseModel):
    id: int
    crop_type: Optional[str] = None
    disease_name: str
    confidence: float
    severity: str
    created_at: Optional[str] = None


class DiseaseHistoryResponse(BaseModel):
    success: bool
    data: List[DiseaseHistoryItem] = Field(default_factory=list)
    error: Optional[str] = None
