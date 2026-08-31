# FarmFusion — Global India-Wide Language Synchronization, Dynamic Location & Weather Cleanup Report

---

## 1. Executive Summary

This integration establishes a single, canonical India-wide source of truth for languages, regional dialects, dynamic geographic location, and real-time weather across the entire FarmFusion system (FastAPI backend, LangGraph Orchestrator, and Android Kotlin UI).

---

## 2. Global Source of Truth for Languages

- **Canonical Registry**: `backend/app/voice/languages.py` (`LANGUAGE_REGISTRY`) & `backend/app/voice/providers.py`.
- **Android Mirror**: `frontend/app/src/main/java/com/example/farmfusionapp/data/model/LanguageRegistry.kt`.
- **Total Languages & Varieties**: **38 distinct entries**.

### Inventory Breakdown
1. **Scheduled / Primary Languages (14 Tier 1)**:
   - Hindi (`hi`), English (`en`), Gujarati (`gu`), Marathi (`mr`), Punjabi (`pa`), Bengali (`bn`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), Malayalam (`ml`), Odia (`or`), Assamese (`as`), Urdu (`ur`), Maithili (`mai`).
2. **Regional Dialects & Varieties (24 Tier 2)**:
   - **Rajasthani**: Marwari (`rwr`), Mewari (`mew`), Dhundhari (`dhu`), Harauti (`har`), Shekhawati (`swv`), Wagdi (`wbr`).
   - **Hindi Belt**: Bhojpuri (`bho`), Awadhi (`awa`), Magahi (`mag`), Chhattisgarhi (`hne`), Bundeli (`bns`), Haryanvi (`bgc`), Braj (`bra`).
   - **Himalayan**: Garhwali (`gbm`), Kumaoni (`kfy`), Nepali (`ne`).
   - **Punjabi Varieties**: Malwai (`mup`), Doabi (`doa`).
   - **Western Varieties**: Varhadi (`vah`), Kathiawari (`kat`), Konkani (`kok`).
   - **Southern Regional**: Tulu (`tcy`), Kodava (`kfa`).
   - **Classical**: Sanskrit (`sa`).

---

## 3. Truthful Capability Indicators & Zero Fabrication

- **Tier 1 (Native Voice)**: Displays `✓ Voice available`. Uses direct Bhashini / Local VITS neural TTS and end-to-end ASR.
- **Tier 2 (Dialect / Variety)**: Displays `✓ Understanding • △ Voice fallback`. Recognizes regional agrarian vocabulary through semantic normalization while truthfully narrating audio via the verified parent-language TTS engine (`hi`, `mr`, `gu`, `pa`, `kn`). Parent-language audio is never falsely labeled as native dialect audio.

---

## 4. Global Language Propagation & Persistence

- **Storage**: Persisted to Android `AuthStore` using `KEY_LANGUAGE` and `KEY_DIALECT`.
- **UI Lifecycle**:
  - `ProfileScreen.kt` displays the active native language & dialect title dynamically (e.g. `मारवाड़ी (Marwari)`).
  - `LanguageSelectionScreen.kt` provides live search, category filtering (`All`, `Primary`, `Regional`), and 1-tap selection.
  - `VoiceAssistantScreen.kt` auto-initializes to the user's global profile preference and allows conversational switching.
  - `LocaleHelper.wrap()` synchronizes the active Android configuration across the whole application.

---

## 5. Dynamic Location Source of Truth

- **Strict Resolution Priority**:
  1. `GPS / FusedLocationProviderClient` (High Accuracy)
  2. `Saved Farm Location / Profile Location` (if GPS is disabled)
  3. Clear fallback: `"Location unavailable"` (Never defaults silently to Udaipur, Nagpur, or any fake city).
- **All Production Code Verified**:
  - `DashboardScreen.kt`: Uses dynamic reverse-geocoded locality or `"Location unavailable"`.
  - `WeatherScreen.kt`: Uses real device coordinates and dynamic locality.
  - `MandiPricesScreen.kt`: Defaults to current GPS locality dynamically.
  - `tools/registry.py` & `voice_service.py`: Centroid fallback replaced with generic central India coordinates `(20.5937, 78.9629)`.

---

## 6. Weather & Pressure Cleanup

- **Pressure Removal**:
  - Completely removed hardcoded `"Pressure: 1012 hPa"` from `DashboardScreen.kt` Hero Card.
  - Removed `pressure` from `DisplayWeatherData` model and `WeatherHero` in `WeatherScreen.kt`.
  - Farmer-facing weather cards now focus exclusively on high-utility agricultural parameters: **Temperature**, **Relative Humidity (%)**, and **Wind Speed (km/h)**.
- **No Hardcoded Weather Numbers**:
  - All weather values are dynamically retrieved from the Open-Meteo live API via `WeatherService.get_current_weather()`.

---

## 7. Verification & Regression Test Results

| Test Domain | Result | Passed / Total |
|---|---|---|
| **Backend Pytest Suite** | `PASSED` | **245 / 245 (100%)** |
| **Mandi Price Intelligence** | `PASSED` | **13 / 13 (100%)** |
| **Voice Multilingual Platform** | `PASSED` | **21 / 21 (100%)** |
| **Android Kotlin Compilation** | `BUILD SUCCESSFUL` | 0 errors |
| **Android Unit Tests** | `PASSED` | `:app:testDebugUnitTest` Successful |

---

## 8. Physical Device Status

- Host ADB status: `List of devices attached` (empty).
- When a physical Android device is connected, run `./gradlew installDebug` to verify on-device.
