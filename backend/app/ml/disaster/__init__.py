"""
Disaster ML Module for FarmFusion.
Integrates DisasterPredictorAI ensemble model for weather-driven hazard detection.
"""

from app.ml.disaster.inference import DisasterRiskPredictor, disaster_predictor

__all__ = ["DisasterRiskPredictor", "disaster_predictor"]
