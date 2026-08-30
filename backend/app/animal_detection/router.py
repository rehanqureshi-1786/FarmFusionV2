"""
FastAPI Router for IoT Animal Intrusion Detection System.
Includes REST endpoints for event ingestion, heartbeat, status, and WebSocket broadcasting.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.animal_detection.schemas import (
    DetectionEventCreate,
    DetectionEventResponse,
    LatestStatusResponse,
    HistoryResponse,
    HeartbeatRequest,
    DeviceStatusResponse
)
from app.animal_detection.service import AnimalDetectionService
from app.animal_detection.websocket_manager import manager

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/animal-detection", tags=["IoT Animal Intrusion Detection"])
ws_router = APIRouter(prefix="/api/v1/ws", tags=["IoT WebSocket Real-Time"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Post Animal Intrusion Event",
    description="Ingests debounced state transitions from ESP32 nodes and broadcasts to real-time WebSocket clients."
)
async def post_detection_event(
    payload: DetectionEventCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Store event atomically in PostgreSQL / SQLAlchemy
        recorded_event: DetectionEventResponse = await AnimalDetectionService.record_event(db, payload)

        # 2. Broadcast event JSON over WebSocket
        broadcast_payload = {
            "event": "animal_detection",
            "data": {
                "event_id": recorded_event.id,
                "device_id": recorded_event.device_id,
                "sensor": recorded_event.sensor,
                "sensor_type": recorded_event.sensor_type,
                "status": recorded_event.status,
                "timestamp": recorded_event.timestamp
            }
        }
        await manager.broadcast(broadcast_payload)

        return {
            "status": "success",
            "data": recorded_event
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception("failed_to_record_detection_event", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record and broadcast event: {str(e)}"
        )


@router.post(
    "/sensor-heartbeat",
    summary="Per-Sensor Keep-Alive Telemetry",
    description="Periodic keep-alive from ESP32 to maintain per-sensor ONLINE status without duplicating history logs."
)
async def post_sensor_heartbeat(
    payload: DetectionEventCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        timestamp = await AnimalDetectionService.record_sensor_telemetry(
            db=db,
            device_id=payload.device_id,
            sensor=payload.sensor,
            sensor_type=payload.sensor_type,
            status=payload.status
        )

        # Broadcast telemetry update over WebSocket
        broadcast_payload = {
            "event": "sensor_telemetry",
            "data": {
                "device_id": payload.device_id,
                "sensor": payload.sensor.upper(),
                "sensor_type": payload.sensor_type.upper(),
                "status": payload.status.lower(),
                "health": "online",
                "timestamp": timestamp
            }
        }
        await manager.broadcast(broadcast_payload)

        return {
            "status": "acknowledged",
            "device_id": payload.device_id,
            "sensor": payload.sensor.upper(),
            "timestamp": timestamp
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception("failed_to_record_sensor_heartbeat", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record sensor heartbeat: {str(e)}"
        )


@router.get("/latest", response_model=LatestStatusResponse, summary="Get Granular Sensor Status & Node Health")
async def get_latest_status(
    device_id: str = Query(default="NODE_01"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await AnimalDetectionService.get_latest_status(db, device_id=device_id)
    except Exception as e:
        logger.exception("failed_to_fetch_latest_status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch latest status: {str(e)}"
        )


@router.get("/history", response_model=HistoryResponse, summary="Get Intrusion Event History")
async def get_detection_history(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    sensor: Optional[str] = Query(default=None),
    sensor_type: Optional[str] = Query(default=None),
    device_id: Optional[str] = Query(default="NODE_01"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await AnimalDetectionService.get_history(
            db=db,
            device_id=device_id,
            sensor=sensor,
            sensor_type=sensor_type,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.exception("failed_to_fetch_history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )


@router.get("/status", response_model=DeviceStatusResponse, summary="Get Node Online/Offline Health")
async def get_device_status(
    device_id: str = Query(default="NODE_01"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await AnimalDetectionService.get_device_status(db, device_id=device_id)
    except Exception as e:
        logger.exception("failed_to_fetch_device_status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch device status: {str(e)}"
        )


@router.post("/heartbeat", summary="Unified ESP32 Keep-Alive")
async def post_heartbeat(
    payload: HeartbeatRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        timestamp = await AnimalDetectionService.update_heartbeat(
            db=db,
            device_id=payload.device_id,
            sensors=payload.sensors
        )

        if payload.sensors:
            for s_name, s_status in payload.sensors.items():
                clean_name = s_name.strip().upper()
                s_type = "PIR" if clean_name.startswith("PIR") else "IR"
                broadcast_payload = {
                    "event": "sensor_telemetry",
                    "data": {
                        "device_id": payload.device_id,
                        "sensor": clean_name,
                        "sensor_type": s_type,
                        "status": s_status.strip().lower(),
                        "health": "online",
                        "timestamp": timestamp
                    }
                }
                await manager.broadcast(broadcast_payload)

        return {
            "status": "acknowledged",
            "device_id": payload.device_id,
            "timestamp": timestamp
        }
    except Exception as e:
        logger.exception("failed_to_record_heartbeat", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record heartbeat: {str(e)}"
        )


@ws_router.websocket("/animal-detection")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)
