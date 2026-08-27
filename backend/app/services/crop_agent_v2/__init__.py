"""
FarmFusion Crop Recommendation Agent V2 Module.
"""
from app.services.crop_agent_v2.agent import CropRecommendationAgentV2, crop_agent_v2
from app.services.crop_agent_v2.agriculture_db import AgricultureRepository, agriculture_repo
from app.services.crop_agent_v2.local_engine import LocalCropEngine, local_crop_engine
from app.services.crop_agent_v2.ranking_engine import AgronomicRankingEngine, ranking_engine
from app.services.crop_agent_v2.fallback_engine import GroqFallbackEngine, fallback_engine

__all__ = [
    "CropRecommendationAgentV2",
    "crop_agent_v2",
    "AgricultureRepository",
    "agriculture_repo",
    "LocalCropEngine",
    "local_crop_engine",
    "AgronomicRankingEngine",
    "ranking_engine",
    "GroqFallbackEngine",
    "fallback_engine",
]
