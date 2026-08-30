"""
Device Capability Detection & Hardware Profile for Local Voice Runtime.
Assesses CPU, RAM, OS environment, and hardware acceleration to classify device capability into LOW_END, MID_RANGE, HIGH_END.
"""
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.voice.local.config import DeviceTier


class DeviceCapabilities(BaseModel):
    tier: DeviceTier
    cpu_count: int
    cpu_arch: str
    total_ram_mb: int
    available_ram_mb: int
    has_nnapi: bool = False
    has_gpu: bool = False
    has_npu: bool = False
    os_name: str
    os_version: str
    max_recommended_model_size_mb: int
    supported_runtimes: list[str] = Field(default_factory=lambda: ["onnx", "numpy", "rule_engine"])


def detect_device_capabilities() -> DeviceCapabilities:
    """
    Detect local host / edge device hardware profile and determine the appropriate DeviceTier.
    Uses standard library system queries without external dependencies.
    """
    cpu_count = os.cpu_count() or 4
    cpu_arch = platform.machine() or "arm64"
    total_ram_mb = 4096
    available_ram_mb = 2048

    # Query Linux /proc/meminfo or sysconf
    try:
        if hasattr(os, "sysconf"):
            if "SC_PAGE_SIZE" in os.sysconf_names and "SC_PHYS_PAGES" in os.sysconf_names:
                total_ram_mb = int((os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")) / (1024 * 1024))
                available_ram_mb = int(total_ram_mb * 0.6)
        if Path("/proc/meminfo").exists():
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        total_ram_mb = int(int(line.split()[1]) / 1024)
                    elif line.startswith("MemAvailable:"):
                        available_ram_mb = int(int(line.split()[1]) / 1024)
    except Exception:
        pass

    # Check CUDA / GPU availability
    has_gpu = False
    try:
        import torch
        has_gpu = torch.cuda.is_available()
    except ImportError:
        has_gpu = False

    # Check Android / NNAPI environment
    is_android = "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ
    has_nnapi = is_android

    # Determine Tier
    if total_ram_mb <= 2500 or cpu_count <= 4:
        tier = DeviceTier.LOW_END
        max_model_mb = 120
    elif total_ram_mb >= 7500 and (has_gpu or cpu_count >= 8):
        tier = DeviceTier.HIGH_END
        max_model_mb = 850
    else:
        tier = DeviceTier.MID_RANGE
        max_model_mb = 350

    runtimes = ["rule_engine", "numpy"]
    try:
        import onnxruntime
        runtimes.append("onnx")
    except ImportError:
        pass
    try:
        import torch
        runtimes.append("pytorch")
    except ImportError:
        pass

    return DeviceCapabilities(
        tier=tier,
        cpu_count=cpu_count,
        cpu_arch=cpu_arch,
        total_ram_mb=total_ram_mb,
        available_ram_mb=available_ram_mb,
        has_nnapi=has_nnapi,
        has_gpu=has_gpu,
        has_npu=has_nnapi or (tier == DeviceTier.HIGH_END),
        os_name=platform.system(),
        os_version=platform.release(),
        max_recommended_model_size_mb=max_model_mb,
        supported_runtimes=runtimes,
    )
