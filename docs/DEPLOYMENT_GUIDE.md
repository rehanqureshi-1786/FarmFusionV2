# FarmFusion Production Deployment & Environment Guide

This document provides complete instructions for deploying the FarmFusion backend, configuring the Android mobile client, and provisioning ESP32 IoT edge nodes.

---

## 1. Backend Production Deployment

The FarmFusion backend is built with FastAPI (async Python), SQLAlchemy 2.x, Alembic, and supports REST APIs, WebSocket streaming (Vobiz AI telephony audio), and async background tasks.

### Production Start Commands

#### Option A: Direct Uvicorn (Recommended for PaaS like Render, Railway, AWS ECS)
```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
```
*Note: Run with 1 worker if utilizing in-memory WebSocket connection managers or single-instance state, or scale workers behind a Redis-backed pub/sub adapter.*

#### Option B: Standard Python Runner
```bash
python run.py
```
`run.py` automatically reads `$PORT` (default: 8000) and disables hot reloading in production environments.

#### Option C: Docker Container
```bash
docker build -t farmfusion-backend backend/
docker run -p 8000:8000 --env-file backend/.env farmfusion-backend
```

### Health Check Endpoint
- **URL**: `GET /health`
- **Response**:
  ```json
  {"status": "healthy", "version": "1.0.0", "app_name": "FarmFusion API"}
  ```

---

## 2. Environment Variables Specification

Ensure the following environment variables are set in your deployment environment (see `backend/.env.example` for full list):

| Variable | Description | Example / Default |
|---|---|---|
| `BASE_URL` | Public HTTPS URL for webhooks and callbacks | `https://api.farmfusion.app` |
| `BASE_WS_URL` | Public WSS URL for Vobiz telephony stream | `wss://api.farmfusion.app` |
| `PORT` | Web server listening port | `8000` |
| `DATABASE_URL` | PostgreSQL connection string with pgvector | `postgresql+asyncpg://user:pass@host:5432/farmfusion` |
| `OPENROUTER_API_KEY` | OpenRouter key for Gemma 3 12B / Qwen LLMs | `sk-or-v1-...` |
| `SARVAM_API_KEY` | Sarvam AI key for Hindi ASR / TTS | `...` |
| `DEEPGRAM_API_KEY` | Deepgram key for fast STT/TTS fallback | `...` |
| `VOBIZ_ACCOUNT_ID` | Vobiz Telephony account identifier | `...` |
| `VOBIZ_API_KEY` | Vobiz Telephony authentication token | `...` |
| `VOBIZ_PHONE_NUMBER` | Vobiz inbound/outbound phone number | `+91...` |
| `OPEN_METEO_BASE_URL` | Open-Meteo weather API base | `https://api.open-meteo.com/v1/forecast` |
| `ENVIRONMENT` | Environment type | `production` / `development` |

---

## 3. Telephony & WebSocket Endpoints

- **Inbound Call Webhook**: `POST /api/v1/calling/inbound`
- **Telephony Event Webhook**: `POST /api/v1/calling/events`
- **WebSocket Audio Stream**: `WS /ws/calling/stream/{call_id}`
- **Vobiz Bi-directional Audio Streaming**: Full duplex audio streaming handled over WebSockets for real-time Hindi voice conversation with farmers.

---

## 4. Android Client Configuration

The Android application uses Gradle `BuildConfig` to cleanly separate development and production environments:

- **Debug Build (`debug`)**:
  - `BASE_URL`: `http://10.0.2.2:8000/` (Android Emulator loopback)
- **Release Build (`release`)**:
  - `BASE_URL`: `https://farmfusion1.onrender.com/` (or your production domain `https://api.farmfusion.app/`)

### Building Release APK / AAB
```bash
cd frontend
./gradlew assembleRelease
```
To point the release build to a custom production domain, update `frontend/app/build.gradle.kts`:
```kotlin
buildTypes {
    release {
        buildConfigField("String", "BASE_URL", "\"https://api.farmfusion.app/\"")
    }
}
```

---

## 5. ESP32 IoT Edge Node Provisioning

FarmFusion detects animal intrusions via ESP32 edge nodes equipped with 6x IR sensors and 2x PIR motion sensors.

### Production Architecture
```
ESP32 Node (Field)
      │
      ▼ (Wi-Fi / Cellular Gateway)
Public Internet
      │
      ▼ (HTTPS POST)
Public FarmFusion Endpoint (https://api.farmfusion.app/api/v1/animal-detection)
      │
      ▼
FarmFusion Backend Core -> Alerts / Telephony / Farmer Notification
```

### Provisioning Steps
1. Open `esp32/animal_detection.ino` or copy `esp32/config.h.example` to `esp32/config.h`.
2. Configure Wi-Fi SSID and Password for the field network:
   ```cpp
   const char* WIFI_SSID     = "FIELD_WIFI_SSID";
   const char* WIFI_PASSWORD = "FIELD_WIFI_PASSWORD";
   ```
3. Configure the public FarmFusion backend domain:
   ```cpp
   const char* SERVER_HOST   = "api.farmfusion.app";
   const int   SERVER_PORT   = 443; // Or 80
   ```
4. Flash the firmware to ESP32 Dev Module via Arduino IDE or PlatformIO.
