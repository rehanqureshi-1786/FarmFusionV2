"""
Language Pack Packager for FarmFusion.
Packages trained models, vocabularies, normalization mappings, and response templates into modular language packs.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import structlog
import shutil

logger = structlog.get_logger(__name__)


class LanguagePackBundleGenerator:
    """
    Generates a packaged language bundle for runtime deployment.
    """
    @staticmethod
    def generate_bundle(
        output_dir: Path,
        language: str,
        dialect: Optional[str] = None,
        name: str = "Hindi",
        native_name: str = "हिन्दी",
        script: str = "Devanagari",
        version: str = "1.0.0",
        support_tier: int = 1,
        vocabulary: Optional[Dict[str, Any]] = None,
        normalization: Optional[Dict[str, str]] = None,
        prompts: Optional[Dict[str, str]] = None,
        asr_model_id: Optional[str] = None,
        tts_model_id: Optional[str] = None,
    ) -> Path:
        key = language if not dialect else f"{language}_{dialect}"
        pack_dir = output_dir / key
        pack_dir.mkdir(parents=True, exist_ok=True)

        vocab = vocabulary or {}
        norm = normalization or {}
        prm = prompts or {
            "greeting": "FarmFusion AI में आपका स्वागत है।",
            "weather": "आज मौसम साफ रहेगा।",
        }

        meta = {
            "pack_id": f"pack_{key}",
            "language": language,
            "dialect": dialect,
            "name": name,
            "native_name": native_name,
            "script": script,
            "version": version,
            "support_tier": support_tier,
            "status": "NATIVE" if support_tier == 1 else "PARTIAL",
            "size_kb": 25,
            "has_vocabulary": bool(vocab),
            "has_normalization": bool(norm),
            "has_prompts": bool(prm),
            "asr_model_id": asr_model_id,
            "tts_model_id": tts_model_id,
        }

        with open(pack_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        with open(pack_dir / "vocabulary.json", "w", encoding="utf-8") as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)
        with open(pack_dir / "normalization.json", "w", encoding="utf-8") as f:
            json.dump(norm, f, ensure_ascii=False, indent=2)
        with open(pack_dir / "prompts.json", "w", encoding="utf-8") as f:
            json.dump(prm, f, ensure_ascii=False, indent=2)

        logger.info("language_pack_bundle_generated", pack_dir=str(pack_dir))
        return pack_dir
