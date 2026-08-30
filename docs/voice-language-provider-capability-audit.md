# Voice Language & Provider Capability Audit: FarmFusion Voice Platform

## 1. Executive Summary & Verification Baseline

- **Repository**: `FarmFusionFinal`
- **Execution Test Command**: `backend/venv/bin/pytest backend/tests/ -v`
- **Verified Baseline Test Count**: **131 / 131 PASSED (100%)**
- **Core Principle**: Agricultural intelligence is language-independent. The voice layer is an honest interface preserving zero data fabrication and strict audio privacy.
- **Audited Distinction**:
  - `NATIVE`: Authentic end-to-end native voice (ASR + NLU + Response Generation + TTS in the same language).
  - `PARENT_FALLBACK`: Dialect / regional language understanding via NLU/lexicon + canonical tool execution + parent language response & TTS.
  - `VOCABULARY_ONLY`: Local agricultural terms mapped into canonical entity IDs.
  - `UNSUPPORTED`: Not supported by current provider infrastructure.

---

## 2. Complete Language & Dialect Capability Matrix

| Language / Variety | ISO / Code | Script | ASR Avail | ASR Provider | ASR Conf | TTS Avail | TTS Provider | Translation | Lang Detect | Dialect Detect | Ag Vocab | NLU | Native Response | Parent Fallback | Offline Support | Code-Switching | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Hindi** | `hi` | Devanagari | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | Yes | Yes (10 cats) | Yes | Yes | `en` | Partial (text/models) | Yes | **NATIVE** |
| **English (India)** | `en` | Latin | Yes | Bhashini / Whisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Marathi** | `mr` | Devanagari | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | Yes | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Gujarati** | `gu` | Gujarati | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | Yes | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Punjabi** | `pa` | Gurmukhi | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | Yes | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Bengali** | `bn` | Bengali | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Telugu** | `te` | Telugu | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Tamil** | `ta` | Tamil | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `en` | Partial | Yes | **NATIVE** |
| **Kannada** | `kn` | Kannada | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | Yes | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Malayalam** | `ml` | Malayalam | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `en` | Partial | Yes | **NATIVE** |
| **Odia** | `or` | Odia | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Assamese** | `as` | Assamese | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `bn` | Partial | Yes | **NATIVE** |
| **Urdu** | `ur` | Perso-Arabic | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Maithili** | `mai` | Devanagari | Yes | Bhashini / IndicWhisper | Yes | Yes | Bhashini / IndicTTS | Yes | Yes | No | Yes | Yes | Yes | `hi` | Partial | Yes | **NATIVE** |
| **Konkani** | `kok` | Devanagari | Fallback | Marathi ASR | Yes | Fallback | Marathi TTS | Local | Yes | No | Yes | Yes | No | `mr` | Partial | Yes | **PARENT_FALLBACK** |
| **Nepali** | `ne` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | No | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Sanskrit** | `sa` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | No | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Mewari** | `mew` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Marwari** | `rwr` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Dhundhari** | `dhu` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Harauti** | `har` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Shekhawati** | `swv` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Wagdi** | `wbr` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Bhojpuri** | `bho` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Awadhi** | `awa` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Magahi** | `mag` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Chhattisgarhi**| `hne`| Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Bundeli** | `bns` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Haryanvi** | `bgc` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Braj** | `bra` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Garhwali** | `gbm` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Kumaoni** | `kfy` | Devanagari | Fallback | Hindi ASR | Yes | Fallback | Hindi TTS | Local | Yes | Yes | Yes | Yes | No | `hi` | Partial | Yes | **PARENT_FALLBACK** |
| **Malwai** | `mup` | Gurmukhi | Fallback | Punjabi ASR | Yes | Fallback | Punjabi TTS | Local | Yes | Yes | Yes | Yes | No | `pa` | Partial | Yes | **PARENT_FALLBACK** |
| **Doabi** | `doa` | Gurmukhi | Fallback | Punjabi ASR | Yes | Fallback | Punjabi TTS | Local | Yes | Yes | Yes | Yes | No | `pa` | Partial | Yes | **PARENT_FALLBACK** |
| **Varhadi** | `vah` | Devanagari | Fallback | Marathi ASR | Yes | Fallback | Marathi TTS | Local | Yes | Yes | Yes | Yes | No | `mr` | Partial | Yes | **PARENT_FALLBACK** |
| **Kathiawari** | `kat` | Gujarati | Fallback | Gujarati ASR | Yes | Fallback | Gujarati TTS | Local | Yes | Yes | Yes | Yes | No | `gu` | Partial | Yes | **PARENT_FALLBACK** |
| **Tulu** | `tcy` | Kannada | Fallback | Kannada ASR | Yes | Fallback | Kannada TTS | Local | Yes | Yes | Yes | Yes | No | `kn` | Partial | Yes | **PARENT_FALLBACK** |
| **Kodava** | `kfa` | Kannada | Fallback | Kannada ASR | Yes | Fallback | Kannada TTS | Local | Yes | Yes | Yes | Yes | No | `kn` | Partial | Yes | **PARENT_FALLBACK** |

---

## 3. Summary Breakdown of Verified Capabilities

- **Native ASR + Native TTS (Full Native Voice)**: **14 Languages** (Hindi, English, Marathi, Gujarati, Punjabi, Bengali, Telugu, Tamil, Kannada, Malayalam, Odia, Assamese, Urdu, Maithili)
- **Dialect Understanding + Parent-Language Response/TTS**: **24 Dialects & Varieties** (Mewari, Marwari, Dhundhari, Harauti, Shekhawati, Wagdi, Bhojpuri, Awadhi, Magahi, Chhattisgarhi, Bundeli, Haryanvi, Braj, Garhwali, Kumaoni, Malwai, Doabi, Varhadi, Kathiawari, Tulu, Kodava, Konkani, Nepali, Sanskrit)
- **Agricultural Vocabulary Normalization Catalog**: **10 Categories** (Crops, Diseases, Fertilizers, Soil Types, Operations, Irrigation, Weather, Mandi, Equipment, Schemes)
- **Code-Switching Support**: Enabled across all languages/dialects.
- **Audio Privacy**: Strict in-memory processing with immediate deletion (`del audio_bytes`).
