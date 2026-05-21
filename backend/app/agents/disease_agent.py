from typing import Dict, Any


class DiseaseDetectionAgent:
    def detect(self, image_url: str) -> Dict[str, Any]:
        return {"disease": "healthy", "confidence": 0.98}
