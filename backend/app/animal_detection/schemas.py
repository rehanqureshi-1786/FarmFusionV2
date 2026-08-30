"""
Pydantic v2 schemas and validation for IoT Animal Intrusion Detection System.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator


VALID_SENSORS = {
    "IR_1", "IR_2", "IR_3", "IR_4", "IR_5", "IR_6",
    "PIR_1", "PIR_2"
}
VALID_SENSOR_TYPES = {"IR", "PIR"}
VALID_STATUSES = {"detected", "cleared"}


class DetectionEventCreate(BaseModel):
    device_id: str = Field(default="NODE_01", max_length=50, description="Identifier of the ESP32 node")
    sensor: str = Field(..., max_length=50, description="Sensor name e.g. IR_1, IR_2, PIR_1")
    sensor_type: str = Field(..., max_length=20, description="Type of sensor: IR or PIR")
    status: str = Field(..., max_length=20, description="Status: detected or cleared")

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("device_id cannot be empty")
        if len(s) > 50:
            raise ValueError("device_id cannot exceed 50 characters")
        return s

    @field_validator("sensor_type")
    @classmethod
    def validate_sensor_type(cls, v: str) -> str:
        upper_v = v.strip().upper()
        if upper_v not in VALID_SENSOR_TYPES:
            raise ValueError(f"sensor_type must be one of {sorted(VALID_SENSOR_TYPES)}")
        return upper_v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        lower_v = v.strip().lower()
        if lower_v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        return lower_v

    @field_validator("sensor")
    @classmethod
    def validate_sensor(cls, v: str) -> str:
        s = v.strip().upper()
        if not s:
            raise ValueError("sensor cannot be empty")
        if s not in VALID_SENSORS:
            raise ValueError(f"sensor must be one of valid sensors {sorted(VALID_SENSORS)}")
        return s


class DetectionEventResponse(BaseModel):
    id: int
    device_id: str
    sensor: str
    sensor_type: str
    status: str
    timestamp: str


class SensorDetail(BaseModel):
    status: str       # cleared, detected, or offline
    health: str       # online or offline
    sensor_type: str  # IR or PIR
    last_seen: Optional[str] = None


class LatestStatusResponse(BaseModel):
    device_id: str
    overall_status: str  # AREA_CLEAR, INTRUSION_DETECTED, SENSORS_OFFLINE, or NODE_OFFLINE
    sensors: Dict[str, SensorDetail]
    detected_sensors: List[str]
    offline_sensors: List[str]
    last_updated: Optional[str] = None


class HistoryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    events: List[DetectionEventResponse]


class HeartbeatRequest(BaseModel):
    device_id: str = Field(default="NODE_01", max_length=50, description="Identifier of the ESP32 node")
    sensors: Optional[Dict[str, str]] = Field(default=None, description="Optional map of sensor statuses, e.g. {'IR_1': 'cleared'}")

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("device_id cannot be empty")
        if len(s) > 50:
            raise ValueError("device_id cannot exceed 50 characters")
        return s


class DeviceStatusResponse(BaseModel):
    device_id: str
    status: str  # ONLINE or OFFLINE
    last_seen: Optional[str] = None
    timeout_seconds: int = 15
