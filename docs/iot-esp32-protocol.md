# FarmFusion IoT - ESP32 Animal Intrusion Detection Protocol

## 1. Hardware Architecture & Pin Mapping

The FarmFusion Animal Intrusion Detection Node runs on an **ESP32 Dev Module** managing 8 digital sensors and 1 active alarm buzzer:

| Sensor Name | Sensor Type | GPIO Pin | Trigger Level | Idle State | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **IR_1** | IR Beam | `GPIO 27` | `LOW` (0) | `HIGH` (1) | Perimeter Beam #1 |
| **IR_2** | IR Beam | `GPIO 26` | `LOW` (0) | `HIGH` (1) | Perimeter Beam #2 |
| **IR_3** | IR Beam | `GPIO 32` | `LOW` (0) | `HIGH` (1) | Perimeter Beam #3 |
| **IR_4** | IR Beam | `GPIO 33` | `LOW` (0) | `HIGH` (1) | Perimeter Beam #4 |
| **IR_5** | IR Beam | `GPIO 18` | `LOW` (0) | `HIGH` (1) | Perimeter Beam #5 |
| **IR_6** | IR Beam | `GPIO 19` | `LOW` (0) | `HIGH` (1) | Perimeter Beam #6 |
| **PIR_1** | PIR Motion | `GPIO 23` | `HIGH` (1) | `LOW` (0) | Field Motion Sector A |
| **PIR_2** | PIR Motion | `GPIO 22` | `HIGH` (1) | `LOW` (0) | Field Motion Sector B |
| **BUZZER** | Alarm Buzzer| `GPIO 25` | `HIGH` (1) | `LOW` (0) | Local Acoustic Deterrent |

---

## 2. Timing & Sampling Semantics

- **Sampling Interval**: `30 ms`
- **Hysteresis Window**: 5 consecutive samples (`150 ms` minimum stable state required before firing state transition).
- **Hold Duration**: `150 ms`
- **Unified Heartbeat Interval**: `1500 ms` (1.5 seconds)
- **Node Timeout Threshold**: `12 seconds`
- **Sensor Timeout Threshold**: `15 seconds`

---

## 3. REST API Contract & Payloads

### 1. State-Change Intrusion Event
- **Endpoint**: `POST /api/v1/animal-detection`
- **Trigger**: Fired immediately upon a debounced state change (detected or cleared).
- **Request Body**:
```json
{
  "device_id": "NODE_01",
  "sensor": "IR_1",
  "sensor_type": "IR",
  "status": "detected"
}
```
- **Response** (`201 Created`):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "device_id": "NODE_01",
    "sensor": "IR_1",
    "sensor_type": "IR",
    "status": "detected",
    "timestamp": "2026-08-31T00:45:00.000000Z"
  }
}
```

---

### 2. Unified Keep-Alive Heartbeat
- **Endpoint**: `POST /api/v1/animal-detection/heartbeat`
- **Interval**: Fired every 1.5 seconds by ESP32 main loop.
- **Request Body**:
```json
{
  "device_id": "NODE_01",
  "sensors": {
    "IR_1": "cleared",
    "IR_2": "cleared",
    "IR_3": "cleared",
    "IR_4": "cleared",
    "IR_5": "cleared",
    "IR_6": "cleared",
    "PIR_1": "cleared",
    "PIR_2": "cleared"
  }
}
```
- **Response** (`200 OK`):
```json
{
  "status": "acknowledged",
  "device_id": "NODE_01",
  "timestamp": "2026-08-31T00:45:00.000000Z"
}
```

---

### 3. Real-Time WebSocket Channel
- **Endpoint**: `WS /api/v1/ws/animal-detection`
- **Message Format**:
```json
{
  "event": "animal_detection",
  "data": {
    "event_id": 1,
    "device_id": "NODE_01",
    "sensor": "IR_1",
    "sensor_type": "IR",
    "status": "detected",
    "timestamp": "2026-08-31T00:45:00.000000Z"
  }
}
```
