# Farm Assistant Voice Screen Integration Audit

## 1. Production Screen & Component Identification

| Component | File Path | Role |
| :--- | :--- | :--- |
| **Main Screen Composable** | [`frontend/app/src/main/java/com/example/farmfusionapp/ui/screens/VoiceAssistantScreen.kt`](file:///home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/ui/screens/VoiceAssistantScreen.kt) | Primary Farm Assistant UI, Mic controller, chat timeline, debug panel, navigation actions. |
| **Navigation Route** | [`frontend/app/src/main/java/com/example/farmfusionapp/ui/screens/AppNav.kt`](file:///home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/ui/screens/AppNav.kt) | `NavRoutes.VoiceAssistant` (`"voice_assistant"`), linked from BottomBar & Dashboard. |
| **ViewModel** | [`frontend/app/src/main/java/com/example/farmfusionapp/viewmodel/VoiceViewModel.kt`](file:///home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/viewmodel/VoiceViewModel.kt) | Manages `VoiceState` (`Idle`, `Loading`, `Success`, `Error`), communicates with API. |
| **Retrofit Network Client** | [`frontend/app/src/main/java/com/example/farmfusionapp/network/FarmFusionApi.kt`](file:///home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/network/FarmFusionApi.kt) | `@POST("api/v1/voice") suspend fun processVoice(...)`. |
| **Data Contract Models** | [`frontend/app/src/main/java/com/example/farmfusionapp/data/model/ApiModels.kt`](file:///home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/data/model/ApiModels.kt) | `VoiceQueryRequest`, `VoiceQueryResponse`. |
| **Backend Route Handler** | [`backend/app/api/v1/voice.py`](file:///home/rdj/FarmFusionFinal/backend/app/api/v1/voice.py) | `POST /api/v1/voice` calling LangGraph Orchestrator & Local Neural TTS. |
| **Backend Data Model** | [`backend/app/models/voice.py`](file:///home/rdj/FarmFusionFinal/backend/app/models/voice.py) | Pydantic v2 `VoiceQueryResponse`. |
| **Local Neural TTS Engine**| [`backend/app/voice/local/tts/local_tts.py`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/tts/local_tts.py) | Synthesizes 16 kHz 16-bit PCM WAV across 24 verified Indian checkpoints. |

---

## 2. End-to-End Architecture & Response Flow

```
[Farmer Speaks] (Android SpeechRecognizer / Mic Input)
       │
       ▼
[VoiceAssistantScreen.kt]
       │  (Captures text transcript + user selected/preferred language)
       ▼
[VoiceViewModel.kt]
       │  (Dispatches POST /api/v1/voice with query, location, language_hint)
       ▼
[Backend FastAPI: /api/v1/voice]
       │
       ├── 1. Run LangGraph Orchestrator Pipeline (Intent classification + ToolRegistry)
       │      ├── Weather Tool (Open-Meteo)
       │      ├── Mandi Tool (Prophet + LightGBM ML)
       │      ├── Crop Recommendation Tool (XGBoost V2)
       │      ├── Disease Detection / Scheme RAG
       │      └── Response Synthesis (Zero data fabrication, localized text)
       │
       ├── 2. Provider Router Decides TTS Path:
       │      ├── Installed Local Neural VITS (hi, mr, gu, bn, ta, te, pa, kn, ml, or, as, mai, bgc, hne, ur, etc.)
       │      └── Dialect Fallback (e.g. Marwari -> Parent Hindi VITS with is_native=False)
       │
       └── 3. Synthesize Authentic 16 kHz WAV Audio & Base64 Encode in VoiceQueryResponse
       │
       ▼
[Android Farm Assistant Screen]
       │
       ├── Displays localized text in farmer's language/dialect
       ├── Displays farmer-friendly badge (e.g. "मराठी आवाज" or "मारवाड़ी उत्तर • हिन्दी आवाज")
       ├── Disables microphone during playback to prevent feedback loops
       ├── Plays authentic 16 kHz WAV audio directly via Android MediaPlayer
       └── Supports replay, speech rate, follow-up suggestions, and in-app navigation
```
