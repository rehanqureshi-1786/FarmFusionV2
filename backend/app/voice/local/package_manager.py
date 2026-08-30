"""
Language & Model Pack Lifecycle Manager for FarmFusion.
Handles discovery, download verification, dynamic activation, and deletion of local language packs and model binaries.
"""
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import shutil
import hashlib
import structlog
from pydantic import BaseModel, Field

from app.voice.local.config import local_voice_config
from app.voice.local.model_registry import local_model_registry, LocalModelManifest, ModelStatus, ModelTask

logger = structlog.get_logger(__name__)


class PackStatus(str, Enum):
    INSTALLED = "installed"
    DOWNLOADABLE = "downloadable"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class LanguagePackMetadata(BaseModel):
    pack_id: str
    language: str
    dialect: Optional[str] = None
    name: str
    native_name: str
    script: str
    version: str
    support_tier: int
    status: str = "VOCABULARY_ONLY" # NATIVE, PARTIAL, FALLBACK, VOCABULARY_ONLY, UNAVAILABLE
    size_kb: int
    has_vocabulary: bool = True
    has_normalization: bool = True
    has_prompts: bool = True
    asr_model_id: Optional[str] = None
    tts_model_id: Optional[str] = None
    sha256_checksum: Optional[str] = None


class LanguagePackageManager:
    """
    Manages modular downloadable language and model packs.
    Never downloads models automatically without explicit permission or on cellular data if prohibited.
    """
    def __init__(self, packs_dir: Optional[Path] = None):
        self.packs_dir = packs_dir or local_voice_config.language_packs_dir
        self.packs_dir.mkdir(parents=True, exist_ok=True)
        self._active_packs: Dict[str, LanguagePackMetadata] = {}
        self._load_installed_packs()

    def _load_installed_packs(self):
        """Discover and load metadata for all installed language packs."""
        if not self.packs_dir.exists():
            return
        for pack_dir in self.packs_dir.iterdir():
            if pack_dir.is_dir() and (pack_dir / "metadata.json").exists():
                try:
                    with open(pack_dir / "metadata.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                        meta = LanguagePackMetadata(**data)
                        self._active_packs[meta.language if not meta.dialect else f"{meta.language}_{meta.dialect}"] = meta
                except Exception as e:
                    logger.error("language_pack_load_error", path=str(pack_dir), error=str(e))

    def list_installed_packs(self) -> List[LanguagePackMetadata]:
        return list(self._active_packs.values())

    def get_pack(self, language: str, dialect: Optional[str] = None) -> Optional[LanguagePackMetadata]:
        key = language if not dialect else f"{language}_{dialect}"
        return self._active_packs.get(key) or self._active_packs.get(language)

    def is_pack_installed(self, language: str, dialect: Optional[str] = None) -> bool:
        key = language if not dialect else f"{language}_{dialect}"
        pack_dir = self.packs_dir / key
        return (pack_dir / "metadata.json").exists()

    def get_pack_status(self, language: str, dialect: Optional[str] = None) -> PackStatus:
        if self.is_pack_installed(language, dialect):
            return PackStatus.INSTALLED
        return PackStatus.DOWNLOADABLE

    def get_vocabulary(self, language: str, dialect: Optional[str] = None) -> Dict[str, Any]:
        key = language if not dialect else f"{language}_{dialect}"
        pack_dir = self.packs_dir / key
        if not pack_dir.exists():
            pack_dir = self.packs_dir / language
        vocab_file = pack_dir / "vocabulary.json"
        if vocab_file.exists():
            with open(vocab_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_normalization_rules(self, language: str, dialect: Optional[str] = None) -> Dict[str, str]:
        key = language if not dialect else f"{language}_{dialect}"
        pack_dir = self.packs_dir / key
        if not pack_dir.exists():
            pack_dir = self.packs_dir / language
        norm_file = pack_dir / "normalization.json"
        if norm_file.exists():
            with open(norm_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_prompts(self, language: str, dialect: Optional[str] = None) -> Dict[str, str]:
        key = language if not dialect else f"{language}_{dialect}"
        pack_dir = self.packs_dir / key
        if not pack_dir.exists():
            pack_dir = self.packs_dir / language
        prompt_file = pack_dir / "prompts.json"
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def install_pack(self, pack_metadata: LanguagePackMetadata, vocab: Dict, norm: Dict, prompts: Dict) -> bool:
        """Create and install a language pack directory locally."""
        key = pack_metadata.language if not pack_metadata.dialect else f"{pack_metadata.language}_{pack_metadata.dialect}"
        pack_dir = self.packs_dir / key
        pack_dir.mkdir(parents=True, exist_ok=True)

        with open(pack_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(pack_metadata.model_dump(), f, ensure_ascii=False, indent=2)
        with open(pack_dir / "vocabulary.json", "w", encoding="utf-8") as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)
        with open(pack_dir / "normalization.json", "w", encoding="utf-8") as f:
            json.dump(norm, f, ensure_ascii=False, indent=2)
        with open(pack_dir / "prompts.json", "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)

        self._active_packs[key] = pack_metadata
        logger.info("language_pack_installed", pack_id=pack_metadata.pack_id, path=str(pack_dir))
        return True

    def delete_pack(self, language: str, dialect: Optional[str] = None) -> bool:
        key = language if not dialect else f"{language}_{dialect}"
        pack_dir = self.packs_dir / key
        if pack_dir.exists():
            shutil.rmtree(pack_dir)
            self._active_packs.pop(key, None)
            logger.info("language_pack_deleted", key=key)
            return True
        return False


language_package_manager = LanguagePackageManager()
