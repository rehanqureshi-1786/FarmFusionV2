"""
Comprehensive Test Suite for FarmFusion IoT Animal Intrusion Detection System.
Tests schemas, database persistence, timeout logic, REST endpoints, and WebSocket broadcasts.
"""
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base, get_db
from app.models.animal_detection import AnimalDetection, DeviceStatus, SensorStatus
from app.animal_detection.schemas import (
    DetectionEventCreate,
    DetectionEventResponse,
    LatestStatusResponse,
    HeartbeatRequest
)
from app.animal_detection.service import (
    AnimalDetectionService,
    NODE_TIMEOUT_SECONDS,
    SENSOR_TIMEOUT_SECONDS
)
from app.animal_detection.websocket_manager import manager
from app.main import app


async def get_test_session():
    """Helper to create an in-memory SQLite async session with created tables."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return test_engine, async_session


# =============================================================================
# 1. SCHEMA VALIDATION TESTS
# =============================================================================

def test_01_valid_detection_event_schemas():
    evt_ir = DetectionEventCreate(device_id="NODE_01", sensor="IR_1", sensor_type="IR", status="detected")
    assert evt_ir.sensor == "IR_1"
    assert evt_ir.sensor_type == "IR"
    assert evt_ir.status == "detected"

    evt_pir = DetectionEventCreate(device_id="NODE_01", sensor="PIR_2", sensor_type="PIR", status="cleared")
    assert evt_pir.sensor == "PIR_2"
    assert evt_pir.sensor_type == "PIR"
    assert evt_pir.status == "cleared"


def test_02_invalid_sensor_name_rejected():
    with pytest.raises(ValueError):
        DetectionEventCreate(device_id="NODE_01", sensor="UNKNOWN_SENSOR", sensor_type="IR", status="detected")


def test_03_invalid_sensor_type_rejected():
    with pytest.raises(ValueError):
        DetectionEventCreate(device_id="NODE_01", sensor="IR_1", sensor_type="ULTRASONIC", status="detected")


def test_04_invalid_status_rejected():
    with pytest.raises(ValueError):
        DetectionEventCreate(device_id="NODE_01", sensor="IR_1", sensor_type="IR", status="moving")


# =============================================================================
# 2. SERVICE LAYER & TIMEOUT TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_05_service_record_event_and_updates():
    engine, session_maker = await get_test_session()
    async with session_maker() as session:
        payload = DetectionEventCreate(device_id="NODE_01", sensor="IR_1", sensor_type="IR", status="detected")
        res = await AnimalDetectionService.record_event(session, payload)

        assert res.id is not None
        assert res.device_id == "NODE_01"
        assert res.sensor == "IR_1"
        assert res.status == "detected"

        # Verify device status updated
        dev_status = await AnimalDetectionService.get_device_status(session, "NODE_01")
        assert dev_status.status == "ONLINE"

        # Verify latest status reflects intrusion
        latest = await AnimalDetectionService.get_latest_status(session, "NODE_01")
        assert latest.overall_status == "INTRUSION_DETECTED"
        assert "IR_1" in latest.detected_sensors
        assert latest.sensors["IR_1"].status == "detected"
        assert latest.sensors["IR_1"].health == "online"
    await engine.dispose()


@pytest.mark.asyncio
async def test_06_service_heartbeat_and_area_clear():
    engine, session_maker = await get_test_session()
    async with session_maker() as session:
        # Clear all sensors
        hb_sensors = {f"IR_{i}": "cleared" for i in range(1, 7)}
        hb_sensors.update({"PIR_1": "cleared", "PIR_2": "cleared"})

        ts = await AnimalDetectionService.update_heartbeat(session, "NODE_01", sensors=hb_sensors)
        assert ts is not None

        latest = await AnimalDetectionService.get_latest_status(session, "NODE_01")
        assert latest.overall_status == "AREA_CLEAR"
        assert len(latest.detected_sensors) == 0
        assert latest.sensors["IR_1"].status == "cleared"
    await engine.dispose()


@pytest.mark.asyncio
async def test_07_service_node_timeout_detection():
    engine, session_maker = await get_test_session()
    async with session_maker() as session:
        # Simulate old heartbeat from 20 seconds ago (> 12s timeout)
        stale_time = datetime.now(timezone.utc) - timedelta(seconds=20)
        session.add(DeviceStatus(device_id="NODE_01", last_seen=stale_time))
        await session.commit()

        dev_status = await AnimalDetectionService.get_device_status(session, "NODE_01", timeout_seconds=NODE_TIMEOUT_SECONDS)
        assert dev_status.status == "OFFLINE"

        latest = await AnimalDetectionService.get_latest_status(session, "NODE_01")
        assert latest.overall_status == "NODE_OFFLINE"
        assert latest.sensors["IR_1"].health == "offline"
    await engine.dispose()


@pytest.mark.asyncio
async def test_08_service_history_pagination_and_filters():
    engine, session_maker = await get_test_session()
    async with session_maker() as session:
        # Insert multiple detection events
        for i in range(1, 6):
            await AnimalDetectionService.record_event(
                session,
                DetectionEventCreate(device_id="NODE_01", sensor=f"IR_{i}", sensor_type="IR", status="detected")
            )
        await AnimalDetectionService.record_event(
            session,
            DetectionEventCreate(device_id="NODE_01", sensor="PIR_1", sensor_type="PIR", status="detected")
        )

        # Test limit and offset
        hist = await AnimalDetectionService.get_history(session, device_id="NODE_01", limit=3, offset=0)
        assert hist.total == 6
        assert len(hist.events) == 3

        # Test filter by sensor_type
        pir_hist = await AnimalDetectionService.get_history(session, device_id="NODE_01", sensor_type="PIR")
        assert pir_hist.total == 1
        assert pir_hist.events[0].sensor == "PIR_1"
    await engine.dispose()


# =============================================================================
# 3. REST API ENDPOINT TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_09_api_post_event_and_fetch_latest():
    engine, session_maker = await get_test_session()

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "device_id": "NODE_01",
                "sensor": "IR_2",
                "sensor_type": "IR",
                "status": "detected"
            }
            res = await client.post("/api/v1/animal-detection", json=payload)
            assert res.status_code == 201
            data = res.json()
            assert data["status"] == "success"
            assert data["data"]["sensor"] == "IR_2"

            # Get latest
            latest_res = await client.get("/api/v1/animal-detection/latest?device_id=NODE_01")
            assert latest_res.status_code == 200
            latest_data = latest_res.json()
            assert latest_data["overall_status"] == "INTRUSION_DETECTED"
            assert "IR_2" in latest_data["detected_sensors"]
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_10_api_heartbeat_and_device_status():
    engine, session_maker = await get_test_session()

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            hb_payload = {
                "device_id": "NODE_01",
                "sensors": {
                    "IR_1": "cleared",
                    "IR_2": "cleared"
                }
            }
            res = await client.post("/api/v1/animal-detection/heartbeat", json=hb_payload)
            assert res.status_code == 200
            assert res.json()["status"] == "acknowledged"

            status_res = await client.get("/api/v1/animal-detection/status?device_id=NODE_01")
            assert status_res.status_code == 200
            assert status_res.json()["status"] == "ONLINE"
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_11_api_sensor_heartbeat_endpoint():
    engine, session_maker = await get_test_session()

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "device_id": "NODE_01",
                "sensor": "PIR_1",
                "sensor_type": "PIR",
                "status": "cleared"
            }
            res = await client.post("/api/v1/animal-detection/sensor-heartbeat", json=payload)
            assert res.status_code == 200
            assert res.json()["status"] == "acknowledged"
            assert res.json()["sensor"] == "PIR_1"
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_12_api_invalid_payload_returns_422():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        invalid_payload = {
            "device_id": "NODE_01",
            "sensor": "INVALID_SENSOR",
            "sensor_type": "UNKNOWN",
            "status": "active"
        }
        res = await client.post("/api/v1/animal-detection", json=invalid_payload)
        assert res.status_code == 422


# =============================================================================
# 4. WEBSOCKET BROADCAST TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_13_websocket_broadcast_on_event():
    # Test connection manager broadcast executes without error
    mock_msg = {"event": "animal_detection", "data": {"sensor": "IR_1", "status": "detected"}}
    await manager.broadcast(mock_msg)
    assert True


# =============================================================================
# 5. VOICE ASSISTANT TOOL REGISTRY INTEGRATION TEST
# =============================================================================

@pytest.mark.asyncio
async def test_14_voice_assistant_animal_detection_tool():
    from app.tools.registry import tool_registry

    tool_res = await tool_registry.execute("animal_detection_tool", slots={"device_id": "NODE_01"})
    assert tool_res.status.value == "success"
    assert tool_res.data["overall_status"] in ["AREA_CLEAR", "INTRUSION_DETECTED", "NODE_OFFLINE", "SENSORS_OFFLINE"]
    assert "खेत" in tool_res.localized_message.get("hi", "")


@pytest.mark.asyncio
async def test_15_simulated_full_iot_cycle():
    """
    Simulated 5-Step Cycle:
    1. Send Heartbeat -> Node ONLINE
    2. POST IR_1 detected -> INTRUSION_DETECTED
    3. POST IR_1 cleared -> AREA_CLEAR
    """
    engine, session_maker = await get_test_session()

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Step 1: Heartbeat
            hb_res = await client.post("/api/v1/animal-detection/heartbeat", json={"device_id": "NODE_01"})
            assert hb_res.status_code == 200

            status_1 = await client.get("/api/v1/animal-detection/status?device_id=NODE_01")
            assert status_1.json()["status"] == "ONLINE"

            # Step 2: Intrusion
            evt_res = await client.post(
                "/api/v1/animal-detection",
                json={"device_id": "NODE_01", "sensor": "IR_1", "sensor_type": "IR", "status": "detected"}
            )
            assert evt_res.status_code == 201

            latest_2 = await client.get("/api/v1/animal-detection/latest?device_id=NODE_01")
            assert latest_2.json()["overall_status"] == "INTRUSION_DETECTED"
            assert "IR_1" in latest_2.json()["detected_sensors"]

            # Step 3: Clear
            clear_res = await client.post(
                "/api/v1/animal-detection",
                json={"device_id": "NODE_01", "sensor": "IR_1", "sensor_type": "IR", "status": "cleared"}
            )
            assert clear_res.status_code == 201

            latest_3 = await client.get("/api/v1/animal-detection/latest?device_id=NODE_01")
            assert latest_3.json()["overall_status"] == "AREA_CLEAR"
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
