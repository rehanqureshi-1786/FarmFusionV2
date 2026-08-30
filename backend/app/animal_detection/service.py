"""
Async Service Layer for IoT Animal Intrusion Detection System.
Implements transactional persistence, offline timeouts, and granular sensor evaluation
using FarmFusion's SQLAlchemy 2.0 Async architecture.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.animal_detection import AnimalDetection, DeviceStatus, SensorStatus
from app.animal_detection.schemas import (
    DetectionEventCreate,
    DetectionEventResponse,
    SensorDetail,
    LatestStatusResponse,
    HistoryResponse,
    DeviceStatusResponse
)

logger = structlog.get_logger(__name__)

NODE_TIMEOUT_SECONDS = 12
SENSOR_TIMEOUT_SECONDS = 15

DEFAULT_SENSORS: List[Tuple[str, str]] = [
    ("IR_1", "IR"),
    ("IR_2", "IR"),
    ("IR_3", "IR"),
    ("IR_4", "IR"),
    ("IR_5", "IR"),
    ("IR_6", "IR"),
    ("PIR_1", "PIR"),
    ("PIR_2", "PIR")
]


class AnimalDetectionService:
    """Async database service managing IoT telemetry, state evaluation, and history."""

    @staticmethod
    def get_utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    async def record_event(
        cls,
        db: AsyncSession,
        payload: DetectionEventCreate
    ) -> DetectionEventResponse:
        """
        Stores state-change event, updates sensor status and device status atomically.
        """
        now_utc = cls.get_utc_now()
        sensor_name = payload.sensor.strip().upper()
        sensor_type = payload.sensor_type.strip().upper()
        status = payload.status.strip().lower()
        device_id = payload.device_id.strip()

        # 1. Insert History Record
        event_record = AnimalDetection(
            device_id=device_id,
            sensor=sensor_name,
            sensor_type=sensor_type,
            status=status,
            timestamp=now_utc
        )
        db.add(event_record)

        # 2. Update/Upsert Device Status
        dev_stmt = select(DeviceStatus).where(DeviceStatus.device_id == device_id)
        dev_res = await db.execute(dev_stmt)
        dev_obj = dev_res.scalar_one_or_none()
        if dev_obj:
            dev_obj.last_seen = now_utc
        else:
            db.add(DeviceStatus(device_id=device_id, last_seen=now_utc))

        # 3. Update/Upsert Sensor Status
        sens_stmt = select(SensorStatus).where(
            SensorStatus.device_id == device_id,
            SensorStatus.sensor == sensor_name
        )
        sens_res = await db.execute(sens_stmt)
        sens_obj = sens_res.scalar_one_or_none()
        if sens_obj:
            sens_obj.sensor_type = sensor_type
            sens_obj.status = status
            sens_obj.last_seen = now_utc
        else:
            db.add(SensorStatus(
                device_id=device_id,
                sensor=sensor_name,
                sensor_type=sensor_type,
                status=status,
                last_seen=now_utc
            ))

        await db.commit()
        await db.refresh(event_record)

        return DetectionEventResponse(
            id=event_record.id,
            device_id=event_record.device_id,
            sensor=event_record.sensor,
            sensor_type=event_record.sensor_type,
            status=event_record.status,
            timestamp=event_record.timestamp.isoformat()
        )

    @classmethod
    async def record_sensor_telemetry(
        cls,
        db: AsyncSession,
        device_id: str,
        sensor: str,
        sensor_type: str,
        status: str
    ) -> str:
        """Updates keep-alive telemetry for a specific sensor and node without writing full event history."""
        now_utc = cls.get_utc_now()
        sensor_name = sensor.strip().upper()
        sensor_type = sensor_type.strip().upper()
        status_val = status.strip().lower()
        dev_id = device_id.strip()

        # Update Device Status
        dev_stmt = select(DeviceStatus).where(DeviceStatus.device_id == dev_id)
        dev_res = await db.execute(dev_stmt)
        dev_obj = dev_res.scalar_one_or_none()
        if dev_obj:
            dev_obj.last_seen = now_utc
        else:
            db.add(DeviceStatus(device_id=dev_id, last_seen=now_utc))

        # Update Sensor Status
        sens_stmt = select(SensorStatus).where(
            SensorStatus.device_id == dev_id,
            SensorStatus.sensor == sensor_name
        )
        sens_res = await db.execute(sens_stmt)
        sens_obj = sens_res.scalar_one_or_none()
        if sens_obj:
            sens_obj.sensor_type = sensor_type
            sens_obj.status = status_val
            sens_obj.last_seen = now_utc
        else:
            db.add(SensorStatus(
                device_id=dev_id,
                sensor=sensor_name,
                sensor_type=sensor_type,
                status=status_val,
                last_seen=now_utc
            ))

        await db.commit()
        return now_utc.isoformat()

    @classmethod
    async def update_heartbeat(
        cls,
        db: AsyncSession,
        device_id: str,
        sensors: Optional[Dict[str, str]] = None
    ) -> str:
        """Updates Node heartbeat and optionally all sensor keep-alives in a single atomic transaction."""
        now_utc = cls.get_utc_now()
        dev_id = device_id.strip()

        # Update Device Status
        dev_stmt = select(DeviceStatus).where(DeviceStatus.device_id == dev_id)
        dev_res = await db.execute(dev_stmt)
        dev_obj = dev_res.scalar_one_or_none()
        if dev_obj:
            dev_obj.last_seen = now_utc
        else:
            db.add(DeviceStatus(device_id=dev_id, last_seen=now_utc))

        if sensors:
            for s_name, s_status in sensors.items():
                clean_name = s_name.strip().upper()
                s_type = "PIR" if clean_name.startswith("PIR") else "IR"
                clean_status = s_status.strip().lower()

                sens_stmt = select(SensorStatus).where(
                    SensorStatus.device_id == dev_id,
                    SensorStatus.sensor == clean_name
                )
                sens_res = await db.execute(sens_stmt)
                sens_obj = sens_res.scalar_one_or_none()
                if sens_obj:
                    sens_obj.sensor_type = s_type
                    sens_obj.status = clean_status
                    sens_obj.last_seen = now_utc
                else:
                    db.add(SensorStatus(
                        device_id=dev_id,
                        sensor=clean_name,
                        sensor_type=s_type,
                        status=clean_status,
                        last_seen=now_utc
                    ))

        await db.commit()
        return now_utc.isoformat()

    @classmethod
    async def get_latest_status(
        cls,
        db: AsyncSession,
        device_id: str = "NODE_01"
    ) -> LatestStatusResponse:
        """
        Derives granular per-sensor health and overall status.
        When Node is ONLINE:
          - Default sensors are online & cleared.
          - If a sensor has reported detection within SENSOR_TIMEOUT_SECONDS, status is 'detected'.
          - If a sensor hasn't reported within SENSOR_TIMEOUT_SECONDS, status remains 'cleared' (active detecting).
        When Node is OFFLINE:
          - Overall status is 'NODE_OFFLINE' and all sensors report 'offline'.
        """
        sensors_dict: Dict[str, SensorDetail] = {}
        last_updated: Optional[str] = None
        dt_now = cls.get_utc_now()
        dev_id = device_id.strip()

        # Evaluate Node online status (12s timeout)
        node_status = await cls.get_device_status(db, device_id=dev_id, timeout_seconds=NODE_TIMEOUT_SECONDS)
        is_node_online = (node_status.status == "ONLINE")

        # Initialize default sensor matrix
        for s_name, s_type in DEFAULT_SENSORS:
            sensors_dict[s_name] = SensorDetail(
                status="cleared" if is_node_online else "offline",
                health="online" if is_node_online else "offline",
                sensor_type=s_type,
                last_seen=node_status.last_seen if is_node_online else None
            )

        # Query active records from sensor_status
        stmt = select(SensorStatus).where(SensorStatus.device_id == dev_id)
        res = await db.execute(stmt)
        rows = res.scalars().all()

        for row in rows:
            s_name = row.sensor
            s_type = row.sensor_type
            s_status = row.status
            s_seen_dt = row.last_seen
            s_seen_iso = s_seen_dt.isoformat() if s_seen_dt else None

            if is_node_online:
                sensor_health = "online"
                sensor_eval_status = "cleared"

                if s_seen_dt:
                    if s_seen_dt.tzinfo is None:
                        s_seen_dt = s_seen_dt.replace(tzinfo=timezone.utc)
                    diff = (dt_now - s_seen_dt).total_seconds()
                    if 0 <= diff <= SENSOR_TIMEOUT_SECONDS:
                        sensor_eval_status = s_status

                sensors_dict[s_name] = SensorDetail(
                    status=sensor_eval_status,
                    health=sensor_health,
                    sensor_type=s_type,
                    last_seen=s_seen_iso
                )
            else:
                sensors_dict[s_name] = SensorDetail(
                    status="offline",
                    health="offline",
                    sensor_type=s_type,
                    last_seen=s_seen_iso
                )

            if last_updated is None or (s_seen_iso and s_seen_iso > last_updated):
                last_updated = s_seen_iso

        detected_list = [
            s for s, detail in sensors_dict.items()
            if detail.health == "online" and detail.status == "detected"
        ]
        offline_list = [
            s for s, detail in sensors_dict.items()
            if detail.health == "offline"
        ]

        if not is_node_online:
            overall = "NODE_OFFLINE"
        elif detected_list:
            overall = "INTRUSION_DETECTED"
        elif offline_list:
            overall = "SENSORS_OFFLINE"
        else:
            overall = "AREA_CLEAR"

        return LatestStatusResponse(
            device_id=dev_id,
            overall_status=overall,
            sensors=sensors_dict,
            detected_sensors=detected_list,
            offline_sensors=offline_list,
            last_updated=last_updated
        )

    @classmethod
    async def get_history(
        cls,
        db: AsyncSession,
        device_id: Optional[str] = "NODE_01",
        sensor: Optional[str] = None,
        sensor_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> HistoryResponse:
        """Queries paginated detection event history with optional filters."""
        query = select(AnimalDetection)
        count_query = select(func.count(AnimalDetection.id))

        if device_id:
            query = query.where(AnimalDetection.device_id == device_id.strip())
            count_query = count_query.where(AnimalDetection.device_id == device_id.strip())

        if sensor:
            query = query.where(AnimalDetection.sensor == sensor.strip().upper())
            count_query = count_query.where(AnimalDetection.sensor == sensor.strip().upper())

        if sensor_type:
            query = query.where(AnimalDetection.sensor_type == sensor_type.strip().upper())
            count_query = count_query.where(AnimalDetection.sensor_type == sensor_type.strip().upper())

        # Total count
        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0

        # Paginated results
        query = query.order_by(desc(AnimalDetection.timestamp), desc(AnimalDetection.id)).limit(limit).offset(offset)
        res = await db.execute(query)
        rows = res.scalars().all()

        events = [
            DetectionEventResponse(
                id=row.id,
                device_id=row.device_id,
                sensor=row.sensor,
                sensor_type=row.sensor_type,
                status=row.status,
                timestamp=row.timestamp.isoformat()
            )
            for row in rows
        ]

        return HistoryResponse(
            total=total,
            limit=limit,
            offset=offset,
            events=events
        )

    @classmethod
    async def get_device_status(
        cls,
        db: AsyncSession,
        device_id: str = "NODE_01",
        timeout_seconds: int = 12
    ) -> DeviceStatusResponse:
        """Determines ONLINE/OFFLINE status based on device heartbeat last_seen age."""
        dev_id = device_id.strip()
        stmt = select(DeviceStatus).where(DeviceStatus.device_id == dev_id)
        res = await db.execute(stmt)
        dev_obj = res.scalar_one_or_none()

        status = "OFFLINE"
        last_seen_iso = None

        if dev_obj and dev_obj.last_seen:
            last_seen_dt = dev_obj.last_seen
            if last_seen_dt.tzinfo is None:
                last_seen_dt = last_seen_dt.replace(tzinfo=timezone.utc)
            last_seen_iso = last_seen_dt.isoformat()
            dt_now = cls.get_utc_now()
            diff = (dt_now - last_seen_dt).total_seconds()
            if 0 <= diff <= timeout_seconds:
                status = "ONLINE"
            else:
                status = "OFFLINE"

        return DeviceStatusResponse(
            device_id=dev_id,
            status=status,
            last_seen=last_seen_iso,
            timeout_seconds=timeout_seconds
        )
