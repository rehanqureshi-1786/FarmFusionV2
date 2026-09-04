"""
Disease Service:
Coordinates vision ML classification, agricultural knowledge base retrieval,
safety confidence tiering, and Amazon affiliate product recommendations.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.agents.disease_agent import DiseaseDetectionAgent
from app.db.models import DiseaseDetection
from app.services.disease_knowledge_service import DiseaseKnowledgeService
from app.services.disease_ml_service import DiseaseMLService
from app.services.plant_gatekeeper_service import PlantGatekeeperService
from app.services.store_recommendation_service import StoreRecommendationService

logger = structlog.get_logger(__name__)


class DiseaseService:
    @staticmethod
    def get_disease_info(disease_name: str, crop_name: Optional[str] = None) -> Dict[str, Any]:
        """Look up ICAR/CIBRC aligned symptoms, prevention and treatment for a disease."""
        return DiseaseKnowledgeService.lookup(disease_name, crop_name)

    @staticmethod
    async def detect_disease(
        image_bytes: bytes,
        db: AsyncSession,
        user_id: Optional[int] = None,
        firebase_uid: Optional[str] = None,
        image_filename: Optional[str] = None,
        crop_type: Optional[str] = None,
        response_language: str = "en",
    ) -> Optional[Dict[str, Any]]:
        """
        Fixed Disease Detection Pipeline:
        1. Primary: Lightweight PyTorch/EfficientNet-B3 inference
        2. Fallback: Gemini Vision API if local model is absent
        3. Strict 4-Tier Confidence Scoring (high/medium/low/unclear)
        4. Knowledge Base enrichment (Symptoms, Biological/Cultural/Chemical control)
        5. Amazon Affiliate Product Recommendations
        6. Database storage
        """
        logger.info("disease_detection_start", crop=crop_type, lang=response_language)

        detected_crop: Optional[str] = crop_type
        detected_disease: str = "Unknown"
        confidence: float = 0.0
        confidence_tier: str = "unclear"
        severity: str = "unknown"
        description: str = ""
        inference_source: str = "UNKNOWN"

        top_predictions = []
        model_version = "v2_38class"
        is_reliable = False

        # Step 0: Gatekeeper - Verify image depicts a genuine plant, leaf, crop, or fruit
        gate_res = PlantGatekeeperService.verify_plant(image_bytes)
        if not gate_res.get("is_plant", False):
            logger.info("disease_detection_rejected_non_plant", reason=gate_res.get("reason"), object=gate_res.get("detected_object"))
            reason_text = gate_res.get("reason", "non-plant object")
            invalid_reason = f"No Plant Detected ({reason_text}). Please upload a clear photo of a plant leaf or crop."
            response_data = {
                "disease_name": "No Plant Detected",
                "crop_type": "None",
                "scientific_name": None,
                "confidence": 0.0,
                "confidence_tier": "unclear",
                "diagnosis_status": "no_plant",
                "severity": "none",
                "description": "No crop leaf, plant, or agricultural foliage was detected in this image. The disease detection system only analyzes plants and crops. Please point your camera directly at a plant leaf, stem, or fruit in good lighting.",
                "symptoms": [],
                "causes": [],
                "favorable_conditions": [],
                "prevention_tips": [
                    "Point camera directly at a plant leaf, stem, or fruit in good lighting.",
                    "Ensure the plant is in focus without excessive blur or glare.",
                    "Avoid scanning non-agricultural objects, electronic devices, or general indoor surfaces."
                ],
                "treatment_suggestions": [],
                "treatment": {
                    "biological": [],
                    "cultural": [],
                    "chemical": [],
                    "active_ingredients": [],
                    "treatment_notes": ["No plant detected. No chemical or biological treatment is required."]
                },
                "product_categories": [],
                "store_recommendations": [],
                "sources": [],
                "ai_analyzed": True,
                "can_analyze": False,
                "is_plant_image": False,
                "invalid_image_reason": invalid_reason,
                "is_reliable": False,
                "model_version": "plant_gatekeeper_v1",
                "top_predictions": [],
                "inference_source": "PLANT_GATEKEEPER",
                "message": "No Plant Detected. Please upload or capture a clear photo of a plant leaf.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            from app.services.disease_translation import localize_disease_response
            return localize_disease_response(response_data, response_language)

        # Step 1: Try local EfficientNet-B3 ML model
        ml_result = DiseaseMLService.predict(image_bytes, crop_hint=crop_type)
        if ml_result:
            detected_crop = ml_result.get("crop") or crop_type or "General Crop"
            detected_disease = ml_result.get("disease", "Unknown")
            confidence = ml_result.get("confidence", 0.0)
            confidence_tier = ml_result.get("confidence_tier", "unclear")
            top_predictions = ml_result.get("top_predictions", [])
            model_version = ml_result.get("model_version", "v2_38class")
            is_reliable = ml_result.get("is_reliable", False)
            inference_source = "ML_VISION"
            description = f"Pathology pattern matching {detected_disease} in {detected_crop}."
        else:
            # Step 2: Fallback to Gemini Vision Agent
            try:
                agent = DiseaseDetectionAgent()
                gemini_result = agent.detect(
                    image_bytes,
                    crop_type=crop_type,
                    response_language=response_language,
                )
                if gemini_result:
                    detected_disease = gemini_result.get("disease", "Unknown")
                    confidence = float(gemini_result.get("confidence", 0.0))
                    confidence_tier = DiseaseMLService.calculate_confidence_tier(confidence)
                    severity = gemini_result.get("severity", "medium")
                    description = gemini_result.get("description", "")
                    detected_crop = crop_type or "General Crop"
                    model_version = "gemini_vision"
                    inference_source = "GEMINI_FALLBACK"
            except Exception as e:
                logger.warning("gemini_vision_fallback_failed", error=str(e))

        # Check for meaningful AI analysis
        is_healthy = "healthy" in detected_disease.lower()
        is_uncertain = confidence_tier in ("low", "unclear") or detected_disease.lower() in ("unknown", "", "unable to determine")
        if ml_result is None:
            is_reliable = not is_uncertain

        if is_healthy:
            diagnosis_status = "healthy"
        elif is_uncertain:
            diagnosis_status = "uncertain"
        elif confidence_tier == "high":
            diagnosis_status = "identified"
        else:
            diagnosis_status = "possible"

        # Step 3: Retrieve ICAR Agricultural Knowledge Base
        knowledge = DiseaseKnowledgeService.lookup(detected_disease, detected_crop)

        scientific_name = knowledge.get("scientific_name")
        symptoms = knowledge.get("symptoms", [])
        causes = knowledge.get("causes", [])
        favorable_conditions = knowledge.get("favorable_conditions", [])
        prevention_tips = knowledge.get("prevention", [])
        biological_control = knowledge.get("biological_control", [])
        cultural_control = knowledge.get("cultural_control", [])
        chemical_control = knowledge.get("chemical_control", [])
        active_ingredients = knowledge.get("active_ingredients", [])
        treatment_notes = knowledge.get("treatment_notes", [])
        product_categories = knowledge.get("product_categories", [])
        sources = knowledge.get("sources", [])

        # Build treatment suggestions flat list for backward compatibility with mobile UI
        treatment_suggestions = []
        if biological_control:
            treatment_suggestions.append(f"Biological: {biological_control[0]}")
        if chemical_control and not is_uncertain and not is_healthy:
            treatment_suggestions.append(f"Chemical: {chemical_control[0]}")
        if cultural_control:
            treatment_suggestions.append(f"Cultural: {cultural_control[0]}")
        if not treatment_suggestions and treatment_notes:
            treatment_suggestions = treatment_notes

        # Step 4: Amazon Affiliate Store Recommendations
        store_items = []
        if not is_healthy and not is_uncertain:
            store_res = StoreRecommendationService.build(
                source="disease",
                disease_name=detected_disease,
                crop_hint=detected_crop,
                active_ingredients=active_ingredients,
                product_categories=product_categories,
            )
            store_items = store_res.get("items", [])

        # User-friendly guidance message based on confidence tier
        if confidence_tier == "high":
            tier_msg = "Confident identification."
        elif confidence_tier == "medium":
            tier_msg = "Possible disease — consider confirming with an agricultural extension expert or local KVK."
        elif confidence_tier == "low":
            tier_msg = "Low diagnostic confidence. Chemical treatment is not advised without physical laboratory inspection."
        else:
            tier_msg = "Unable to reliably identify the disease. Please upload a clear photo of an infected leaf in good lighting."

        response_data = {
            "disease_name": detected_disease,
            "crop_type": detected_crop,
            "scientific_name": scientific_name,
            "confidence": confidence,
            "confidence_tier": confidence_tier,
            "diagnosis_status": diagnosis_status,
            "severity": severity if severity != "unknown" else ("high" if confidence_tier == "high" else "medium"),
            "description": description or f"Symptoms and management profile for {detected_disease}.",
            "symptoms": symptoms,
            "causes": causes,
            "favorable_conditions": favorable_conditions,
            "prevention_tips": prevention_tips,
            "treatment_suggestions": treatment_suggestions,
            "treatment": {
                "biological": biological_control,
                "cultural": cultural_control,
                "chemical": chemical_control if not is_uncertain else [],
                "active_ingredients": active_ingredients if not is_uncertain else [],
                "treatment_notes": treatment_notes,
            },
            "product_categories": product_categories,
            "store_recommendations": store_items,
            "sources": sources,
            "ai_analyzed": True,
            "can_analyze": True,
            "is_plant_image": True,
            "is_reliable": is_reliable,
            "model_version": model_version,
            "top_predictions": top_predictions,
            "inference_source": inference_source,
            "message": tier_msg,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "disease_diagnosis_complete",
            source=inference_source,
            model_version=model_version,
            crop=detected_crop,
            disease=detected_disease,
            confidence=confidence,
            confidence_tier=confidence_tier,
            is_reliable=is_reliable,
        )

        # Step 5: Save record in database if user is identified
        if user_id is None and firebase_uid:
            from app.services.user_service import UserService
            user = await UserService.get_user_by_firebase_uid(firebase_uid, db)
            user_id = user.id if user else None

        if user_id is not None:
            detection_record = DiseaseDetection(
                user_id=user_id,
                image_url=image_filename,
                crop_type=detected_crop,
                disease_name=detected_disease,
                confidence=confidence,
                severity=response_data["severity"],
                description=description,
                treatment_suggestions=treatment_suggestions,
                prevention_tips=prevention_tips,
            )
            db.add(detection_record)
            await db.commit()

        from app.services.disease_translation import localize_disease_response
        return localize_disease_response(response_data, response_language)

    @staticmethod
    async def get_user_disease_history(
        user_id: Optional[int] = None,
        db: AsyncSession = None,
        limit: int = 10,
        firebase_uid: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get disease detection history for a user from database."""
        if user_id is None and firebase_uid:
            from app.services.user_service import UserService
            user = await UserService.get_user_by_firebase_uid(firebase_uid, db)
            user_id = user.id if user else None

        if user_id is None or db is None:
            return []

        query = (
            select(DiseaseDetection)
            .where(DiseaseDetection.user_id == user_id)
            .order_by(DiseaseDetection.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        records = result.scalars().all()

        return [
            {
                "id": r.id,
                "disease_name": r.disease_name,
                "confidence": r.confidence,
                "description": r.description,
                "crop_type": r.crop_type,
                "severity": r.severity,
                "treatment_suggestions": r.treatment_suggestions,
                "prevention_tips": r.prevention_tips,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
