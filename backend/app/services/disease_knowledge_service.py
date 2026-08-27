"""
Disease Knowledge Service: Queries structured agricultural knowledge base (ICAR / SAU / CIBRC aligned).
Provides structured symptoms, biological control, cultural control, chemical control, and product recommendations.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

KNOWLEDGE_BASE_PATH = Path(__file__).resolve().parent.parent / "data" / "disease_knowledge_base.json"


class DiseaseKnowledgeService:
    _data: Optional[Dict[str, Any]] = None

    @classmethod
    def _load(cls) -> Dict[str, Any]:
        if cls._data is None:
            if not KNOWLEDGE_BASE_PATH.exists():
                logger.error("disease_knowledge_base_not_found", path=str(KNOWLEDGE_BASE_PATH))
                cls._data = {}
            else:
                try:
                    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
                        cls._data = json.load(f)
                    logger.info("disease_knowledge_base_loaded", count=len(cls._data))
                except Exception as e:
                    logger.error("disease_knowledge_base_load_error", error=str(e))
                    cls._data = {}
        return cls._data

    @classmethod
    def get_by_class_key(cls, class_key: str) -> Optional[Dict[str, Any]]:
        """Look up knowledge entry by exact class key (e.g. 'Tomato___Late_blight')."""
        data = cls._load()
        return data.get(class_key)

    @classmethod
    def lookup(cls, disease_name: str, crop_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Flexible search by disease name and/or crop name.
        Returns matching structured knowledge dictionary or clean fallback.
        """
        data = cls._load()
        
        # 1. Exact match by key
        if disease_name in data:
            return data[disease_name]

        # 2. Normalize and search keys
        d_norm = disease_name.lower().replace(" ", "_").replace("-", "_")
        c_norm = (crop_name or "").lower().strip()

        # Try key containing both crop and disease tokens
        for key, entry in data.items():
            k_lower = key.lower()
            if c_norm and c_norm in k_lower and d_norm in k_lower:
                return entry

        # Try key containing disease token
        for key, entry in data.items():
            if d_norm in key.lower() or entry.get("disease", "").lower() == disease_name.lower():
                return entry

        # 3. Match by normalized disease string containment
        for key, entry in data.items():
            entry_d = entry.get("disease", "").lower()
            if d_norm in entry_d or entry_d in d_norm:
                if not c_norm or c_norm in key.lower() or c_norm in entry.get("crop", "").lower():
                    return entry

        # 4. Multi-token scoring (requiring high token match ratio)
        d_tokens = [t for t in d_norm.split("_") if len(t) > 2]
        best_match = None
        best_score = 0.0

        if d_tokens:
            for key, entry in data.items():
                k_lower = key.lower()
                entry_crop = entry.get("crop", "").lower()
                
                # If crop is specified and differs completely, do not match another crop's disease
                if c_norm and (c_norm not in k_lower and c_norm not in entry_crop):
                    continue

                matched_tokens = sum(1 for token in d_tokens if token in k_lower)
                match_ratio = matched_tokens / len(d_tokens)

                # Require at least 50% of disease tokens to match
                if match_ratio >= 0.5:
                    score = match_ratio * 10
                    if score > best_score:
                        best_score = score
                        best_match = entry

        if best_match and best_score >= 5.0:
            return best_match

        # Healthy fallback
        if "healthy" in d_norm:
            return {
                "crop": crop_name or "General Crop",
                "disease": "Healthy Plant",
                "scientific_name": "N/A",
                "symptoms": ["No disease symptoms observed."],
                "causes": ["Normal physiological condition."],
                "favorable_conditions": ["Optimal agronomic conditions."],
                "prevention": ["Maintain standard balanced fertilization and irrigation."],
                "cultural_control": ["Regular weeding and monitoring."],
                "biological_control": ["Preserve natural beneficial insects."],
                "chemical_control": ["No chemical treatment required."],
                "active_ingredients": [],
                "product_categories": ["Organic Compost", "Bio-fertilizer"],
                "treatment_notes": ["Plant is healthy. No pesticide intervention required."],
                "severity_guidance": ["Zero risk."],
                "sources": ["ICAR Agricultural Knowledge Base"]
            }

        # Unknown fallback without hallucinated chemicals
        return {
            "crop": crop_name or "Unknown Crop",
            "disease": disease_name or "Unidentified Condition",
            "scientific_name": "NOT_AVAILABLE",
            "symptoms": ["Visible leaf pathology requiring expert field inspection."],
            "causes": ["Unverified field etiology."],
            "favorable_conditions": ["Unknown."],
            "prevention": ["Follow standard good agricultural practices and crop rotation."],
            "cultural_control": ["Isolate or prune visibly damaged leaf areas; avoid overhead watering."],
            "biological_control": ["Apply organic neem oil spray (1500 ppm @ 3 ml/L) as a safe broad-spectrum protective measure."],
            "chemical_control": [
                "Follow product label and local agricultural extension / Krishi Vigyan Kendra (KVK) guidance for crop-specific dosage."
            ],
            "active_ingredients": [],
            "product_categories": ["Neem Oil Bio-pesticide", "PPE Kit", "General Crop Protection"],
            "treatment_notes": [
                "Exact dosage and chemical treatment cannot be verified without confirmed laboratory identification. Consult your local KVK / Agriculture Officer before applying synthetic chemicals."
            ],
            "severity_guidance": ["Consult local agricultural officer if symptoms spread rapidly."],
            "sources": ["Local Krishi Vigyan Kendra (KVK) Advisory"]
        }

    @classmethod
    def list_all_classes(cls) -> List[str]:
        return list(cls._load().keys())
