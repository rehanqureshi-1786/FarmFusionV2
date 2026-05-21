# FarmFusion

> FarmFusion — an AI-assisted farming assistant mobile app and FastAPI backend.

This repository was prepared for a hackathon demo: a Kotlin Android frontend that talks to a Python FastAPI backend providing crop recommendations, disease detection, marketplace and weather features.

**Highlights**
- Mobile-first demo using Retrofit + Kotlin for Android
- FastAPI backend with SQLAlchemy / aiosqlite and Firebase authentication
- Agents for crop, market, and weather recommendations
- Ready for deployment to Render (see `render.yaml`) and GitHub

**Live demo goal**
Make the backend public (Render or similar) so the Android app can call the APIs directly.

## Quick start (developer)

Prerequisites
- Python 3.11+, pip
- Android Studio (for the frontend) or an Android device
- `adb` for device networking

Backend
1. Create a Python virtualenv and install deps:

```bash
python3 -m venv .recover-env
source .recover-env/bin/activate
pip install -r backend/requirements.txt
```

2. Configure environment
- Copy `backend/.env.example` to `backend/.env` and fill values. Do NOT commit your real secrets.

3. Run the backend (from repo root):

```bash
source .recover-env/bin/activate
python backend/run.py
```

4. If debugging with a device, forward the port:

```bash
adb reverse tcp:8000 tcp:8000
```

Frontend (Android)
1. Open `frontend/app` in Android Studio.
2. Update `ApiConfig.BASE_URL` to point at your backend (e.g. `http://10.0.2.2:8000` for emulator or the Render URL when deployed).
3. Build and run on device or emulator.

## Deployment notes
- A `render.yaml` is provided to deploy the `backend` service on Render. Add secrets (Firebase credentials) via Render's dashboard, not in the repo.
- The repo `.gitignore` excludes `backend/.env` and `backend/credentials/` — keep credentials local.

## Contributing
- Open issues or PRs.
- For code style, follow existing project conventions.

## Files of interest
- `backend/app` — FastAPI application and services
- `backend/run.py` — convenience runner
- `frontend/app` — Android app source (Kotlin)
- `backend/.env.example` — example env file (fill locally)

## License
This project is provided for hackathon/demo purposes. Check with maintainers for licensing.
