# FarmFusion Project Map for Debugging

Use this as a quick handoff for ChatGPT or another AI assistant.

## 1) Project root
- /home/rdj/FarmFusionFinal/
  - README.md
  - settings.gradle.kts
  - build.gradle.kts
  - gradlew
  - backend/
  - frontend/

## 2) Backend code
- /home/rdj/FarmFusionFinal/backend/
  - main.py                  # FastAPI app entry
  - run.py                  # uvicorn runner
  - requirements.txt
  - .env                    # local runtime config (API keys, DB)
  - .env.example
  - docker-compose.yml
  - alembic.ini
  - alembic/
    - env.py
  - app/
    - core/
      - config.py           # environment config / API keys / DB URL setup
      - database.py         # SQLAlchemy async engine and session
      - security.py
    - api/
      - v1/
        - market.py         # market/mandi endpoints
        - voice.py          # voice assistant API
    - routes/
      - weather.py          # weather routes
      - market.py           # market routes
      - crop.py
      - disease.py
      - auth.py
      - voice.py
      - diagnostics.py      # live config checks and diagnostics
    - services/
      - weather_service.py
      - market_service.py
      - crop_service.py
      - disease_service.py
      - auth_service.py
    - agents/
      - weather_agent.py    # Open-Meteo based weather logic
      - market_agent.py     # mandi/market logic and price prediction
      - groq_client.py
      - gemini_client.py
      - openai_client.py
      - grok_client.py
      - crop_agent.py
      - disease_agent.py
    - models/
      - schemas.py
      - crop.py
      - user.py
      - voice.py
      - rag.py
    - orchestrator/
      - graph.py
      - state.py
      - nodes/
        - intent_classification.py
        - tool_router.py
        - synthesizer.py
    - tools/
      - weather_tool.py
    - workflows/
      - market_forecasting.py
    - db/
      - database.py
      - models.py
      - base.py
    - schemas/
      - market.py
      - voice.py
      - user.py
      - crop.py

## 3) Frontend Android app
- /home/rdj/FarmFusionFinal/frontend/
  - app/
    - src/main/
      - AndroidManifest.xml
      - java/com/example/farmfusionapp/
        - network/
          - ApiConfig.kt     # backend URL (phone/emulator config)
          - RetrofitInstance.kt
          - WeatherApi.kt
          - FarmFusionApi.kt
        - ui/screens/
          - WeatherScreen.kt
          - CropScreen.kt
          - DiseaseScreen.kt
          - VoiceAssistantScreen.kt
        - utils/
          - Constants.kt
        - viewmodel/
        - repository/
        - data/

## 4) Key files for weather/backend debugging
- Backend weather:
  - /home/rdj/FarmFusionFinal/backend/app/agents/weather_agent.py
  - /home/rdj/FarmFusionFinal/backend/app/routes/weather.py
  - /home/rdj/FarmFusionFinal/backend/app/services/weather_service.py
  - /home/rdj/FarmFusionFinal/backend/.env
- Frontend weather screen:
  - /home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/ui/screens/WeatherScreen.kt
  - /home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/network/ApiConfig.kt

## 5) Key files for mandi/market debugging
- /home/rdj/FarmFusionFinal/backend/app/agents/market_agent.py
- /home/rdj/FarmFusionFinal/backend/app/services/market_service.py
- /home/rdj/FarmFusionFinal/backend/app/api/v1/market.py
- /home/rdj/FarmFusionFinal/backend/app/workflows/market_forecasting.py

## 6) Key files for API keys and config
- /home/rdj/FarmFusionFinal/backend/.env
- /home/rdj/FarmFusionFinal/backend/.env.example
- /home/rdj/FarmFusionFinal/backend/app/core/config.py

## 7) Useful debug endpoints
- Backend health:
  - http://localhost:8000/health
- Diagnostics:
  - http://localhost:8000/api/v1/diagnostics/config
  - http://localhost:8000/api/v1/diagnostics/weather-agent
  - http://localhost:8000/api/v1/diagnostics/ai-agents
- Weather API:
  - http://localhost:8000/api/v1/weather/test

## 8) Paste-ready prompt for ChatGPT

"I’m debugging this FarmFusion project. Please inspect the following files and explain the root cause of the issue.

Backend:
- backend/main.py
- backend/run.py
- backend/app/core/config.py
- backend/app/routes/diagnostics.py
- backend/app/agents/weather_agent.py
- backend/app/agents/market_agent.py
- backend/app/services/weather_service.py
- backend/app/services/market_service.py
- backend/.env

Frontend:
- frontend/app/src/main/java/com/example/farmfusionapp/network/ApiConfig.kt
- frontend/app/src/main/java/com/example/farmfusionapp/network/RetrofitInstance.kt
- frontend/app/src/main/java/com/example/farmfusionapp/ui/screens/WeatherScreen.kt

Issue: [describe exact error here].
Please tell me the likely root cause, exact file(s) involved, and the fix steps."

## 9) Quick triage order
When debugging, start in this order:
1. backend/.env
2. backend/app/core/config.py
3. backend/main.py or backend/run.py
4. backend/app/routes/diagnostics.py
5. backend/app/agents/weather_agent.py or market_agent.py
6. frontend/app/src/main/java/com/example/farmfusionapp/network/ApiConfig.kt
7. frontend app screen making the request

## 10) Common problem areas
- wrong backend URL in Android app
- placeholder API keys instead of real keys
- backend not listening on port 8000
- wrong environment variables / missing `.env`
- SQLite vs PostgreSQL mismatch
- phone/emulator network mismatch (10.0.2.2 vs LAN IP)
