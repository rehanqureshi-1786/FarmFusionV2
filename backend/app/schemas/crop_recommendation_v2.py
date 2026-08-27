"""
Pydantic v2 Schemas for FarmFusion Crop Recommendation Agent V2.
Includes transparent provenance and data status fields.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CropRecommendationV2Item(BaseModel):
    crop_name: str
    hindi_name: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_tier: str = Field(..., description="high, medium, low, unclear")
    suitability_level: str = Field(..., description="Highly Suitable, Suitable, Moderately Suitable, Not Recommended")
    category: str = Field(default="cereal")
    water_requirement: str
    sowing_window: str
    growing_duration_months: int
    expected_yield_tons: float
    market_demand: str = Field(default="medium")
    estimated_profit_usd: float = Field(..., description="Approximate historical gross benchmark in USD (not live price)")
    estimated_profit_inr: float = Field(..., description="Approximate historical gross benchmark in INR (not live price)")
    benchmark_gross_return_usd: Optional[float] = None
    benchmark_gross_return_inr: Optional[float] = None
    economic_data_status: str = Field(default="benchmark_estimate_not_live_price")
    contributing_factors: List[str] = []
    management_notes: List[str] = []
    score_source: str = Field(default="farmfusion_heuristic")
    agronomic_source: str = Field(default="ICAR Handbook of Agriculture / FAO Ecocrop")
    source: str = Field(default="local_agent", description="local_agent or groq_fallback")


class CropRecommendationV2Response(BaseModel):
    success: bool = True
    top_recommendation: str
    confidence_tier: str
    is_reliable: bool
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    recommendation_source: str = "local_agent"
    recommendations: List[CropRecommendationV2Item]
    insights: str
    season: str
    season_window: str
    mode: str = Field(..., description="MODE_A_SOIL_REPORT or MODE_B_NO_SOIL_REPORT")
    confidence_disclaimer: str = Field(
        default="Confidence scores represent heuristic model alignment with agro-climatic parameters, not guaranteed crop yield or production certainty."
    )
    economic_disclaimer: str = Field(
        default="Economic return values represent approximate gross historical benchmarks for planning only. NOT live mandi prices or guaranteed profit."
    )
    timestamp: str
