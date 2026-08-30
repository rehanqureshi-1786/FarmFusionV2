# India-Wide Multilingual & Regional-Dialect Voice Platform Capability Map

## Executive Summary & Baseline Verification

- **Repository Root**: `/home/rdj/FarmFusionFinal`
- **Python Version**: `Python 3.13.12`
- **Virtual Environment**: `/home/rdj/FarmFusionFinal/backend/venv`
- **Baseline Test Command**: `backend/venv/bin/pytest backend/tests/ -v`
- **Baseline Test Count**: **94 / 94 PASSED (100%)**
- **Architecture Principle**: *Agricultural intelligence is language-independent. Language is an interface layer.*

---

## 1. Architectural Pipeline

```
                    FARMER
                       │
                       ▼
                VOICE INPUT
                       │
                       ▼
             LANGUAGE DETECTION (Bhashini / FastText / Script)
                       │
                       ▼
            DIALECT DETECTION (Grammar markers & regional lexicon)
                       │
                       ▼
          ASR / SPEECH NORMALIZATION (Tier-specific provider)
                       │
                       ▼
        AGRICULTURAL VOCABULARY NORMALIZATION (Canonical Entity Mapping)
                       │
                       ▼
            FARMER OPERATING ASSISTANT (Deterministic Orchestrator)
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          WEATHER    CROP      MANDI
          DISEASE    SCHEMES   SOIL
          CARE      NAVIGATION OTHER
             │         │         │
             └─────────┼─────────┘
                       ▼
                VERIFIED RESULT (Zero Data Fabrication)
                       │
                       ▼
               RESPONSE LOCALIZER (Fallback Ladder)
                       │
                       ▼
                 DIALECT / LANGUAGE SPEECH
                       │
                       ▼
                     TTS (Bhashini / IndicTTS / On-Device)
                       │
                       ▼
                    FARMER
```

---

## 2. Three-Tier Language & Dialect Classification

### Tier 1 — Full Native Voice (ASR + NLU + Response + TTS)
Farmer speaks in their native language and receives spoken and visual responses in the same language.

| Language | Code | Script | Bhashini ASR | Bhashini TTS | IndicTTS | Status |
|---|---|---|---|---|---|---|
| **Hindi** | `hi` | Devanagari | Yes | Yes | Yes | **Verified Native** |
| **English (India)** | `en` | Latin | Yes | Yes | Yes | **Verified Native** |
| **Marathi** | `mr` | Devanagari | Yes | Yes | Yes | **Verified Native** |
| **Gujarati** | `gu` | Gujarati | Yes | Yes | Yes | **Verified Native** |
| **Punjabi** | `pa` | Gurmukhi | Yes | Yes | Yes | **Verified Native** |
| **Bengali** | `bn` | Bengali | Yes | Yes | Yes | **Verified Native** |
| **Telugu** | `te` | Telugu | Yes | Yes | Yes | **Verified Native** |
| **Tamil** | `ta` | Tamil | Yes | Yes | Yes | **Verified Native** |
| **Kannada** | `kn` | Kannada | Yes | Yes | Yes | **Verified Native** |
| **Malayalam** | `ml` | Malayalam | Yes | Yes | Yes | **Verified Native** |
| **Odia** | `or` | Odia | Yes | Yes | Yes | **Verified Native** |
| **Assamese** | `as` | Assamese | Yes | Yes | Yes | **Verified Native** |
| **Urdu** | `ur` | Perso-Arabic | Yes | Yes | Yes | **Verified Native** |
| **Maithili** | `mai` | Devanagari | Yes | Yes | Yes | **Verified Native** |

---

### Tier 2 — Native Understanding + Parent Language Fallback
Farmer speaks regional language or dialect. System understands grammar markers and vocabulary, extracts canonical intent, and verbalizes response via closest verified parent language voice.

| Regional Language / Dialect | Code | Parent Language | Understanding / NLU | ASR Provider | TTS Fallback | Status |
|---|---|---|---|---|---|---|
| **Mewari** | `mew` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Marwari** | `rwr` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Dhundhari** | `dhu` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Harauti** | `har` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Shekhawati** | `swv` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Wagdi** | `wbr` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Bhojpuri** | `bho` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Awadhi** | `awa` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Magahi** | `mag` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Chhattisgarhi** | `hne` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Bundeli** | `bns` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Haryanvi** | `bgc` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Braj** | `bra` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Garhwali** | `gbm` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Kumaoni** | `kfy` | `hi` (Hindi) | Native grammar & lexicon | Hindi ASR | Hindi TTS | **Verified Fallback** |
| **Malwai** | `mup` | `pa` (Punjabi) | Native grammar & lexicon | Punjabi ASR | Punjabi TTS | **Verified Fallback** |
| **Doabi** | `doa` | `pa` (Punjabi) | Native grammar & lexicon | Punjabi ASR | Punjabi TTS | **Verified Fallback** |
| **Varhadi** | `vah` | `mr` (Marathi) | Native grammar & lexicon | Marathi ASR | Marathi TTS | **Verified Fallback** |
| **Kathiawari** | `kat` | `gu` (Gujarati) | Native grammar & lexicon | Gujarati ASR | Gujarati TTS | **Verified Fallback** |
| **Tulu** | `tcy` | `kn` (Kannada) | Native grammar & lexicon | Kannada ASR | Kannada TTS | **Verified Fallback** |
| **Kodava** | `kfa` | `kn` (Kannada) | Native grammar & lexicon | Kannada ASR | Kannada TTS | **Verified Fallback** |
| **Konkani** | `kok` | `mr` / `kn` | Native grammar & lexicon | Marathi/Kannada ASR | Marathi TTS | **Verified Fallback** |

---

### Tier 3 — Dialect & Agricultural Vocabulary Normalization
Maps dialect surface forms, local crop slang, and colloquial measurements to canonical internal representations.

---

## 3. Agricultural Vocabulary Normalization Matrix

| Category | Dialect / Colloquial Surface Form | Canonical Entity ID | Language / Region |
|---|---|---|---|
| **Crops** | "बाजरो", "बाजरी", "बाजरा", "sajjalu", "kambu" | `pearl_millet` | Rajasthan, Gujarat, Haryana, South |
| **Crops** | "डांगर", "भात", "धान", "चावल", "nellu" | `rice_paddy` | Gujarat, Maharashtra, North, South |
| **Crops** | "सींगदाना", "भूंगली", "भूंगफली", "मूंगफली", "kadale" | `groundnut` | Rajasthan, Gujarat, Karnataka |
| **Crops** | "नरमा", "कापूस", "कपास", "रूई", "paruthi" | `cotton` | Punjab, Maharashtra, North, Tamil Nadu |
| **Crops** | "राई", "तोरी", "सरसों", "sarson", "kadugu" | `mustard` | Rajasthan, Haryana, South |
| **Crops** | "छोला", "बूट", "हरबरा", "चना", "kadale_kalu" | `chickpea` | MP, Maharashtra, North, Karnataka |
| **Crops** | "ईख", "ऊस", "शेरडी", "गन्ना", "karumbu" | `sugarcane` | UP, Maharashtra, Gujarat, Tamil Nadu |
| **Crops** | "कांदा", "डुंगरी", "प्याज", "vengayam", "ullipayalu" | `onion` | Maharashtra, Gujarat, South |
| **Crops** | "बटाटा", "आलू", "urulaikizhangu" | `potato` | Maharashtra, Gujarat, South |
| **Crops** | "लसन", "लहसुन", "poondu", "vellulli" | `garlic` | Rajasthan, MP, South |
| **Soil Types** | "रेत", "रेतीली", "बलुई", "बलुआ" | `sandy_soil` | Rajasthan, Arid zones |
| **Soil Types** | "काली", "रेगुर", "काली दोमट" | `black_soil` | Maharashtra, MP, Gujarat |
| **Soil Types** | "दोमट", "जलोढ़", "चिकनी दोमट" | `alluvial_soil` | Indo-Gangetic Plains |
| **Soil Types** | "लाल", "लाल मिट्टी" | `red_soil` | South, Odisha, Jharkhand |
| **Soil Types** | "चिकनी", "मटियार", "clay" | `clay_soil` | Puddle/Wetland zones |
| **Operations** | "बोवणो", "बुवाई", "वावणी", "पेरणी" | `sowing` | Rajasthan, Gujarat, Maharashtra |
| **Operations** | "कटाई", "लूणी", "कापणी" | `harvesting` | Rajasthan, North, Maharashtra |
| **Mandi** | "भाव", "दर", "दाम", "कीमत", "rate" | `mandi_price` | All India |
| **Weather** | "हवामान", "વાતાવરણ", "ਮੌਸਮ", "मौसम" | `weather` | Maharashtra, Gujarat, Punjab, North |

---

## 4. Response Localization & Fallback Ladder

When synthesizing farmer-facing speech:
1. **Level 1 (Direct)**: If target language has verified native TTS, synthesize in that language.
2. **Level 2 (Parent Language)**: If dialect has parent language (e.g. Mewari $\to$ Hindi, Kathiawari $\to$ Gujarati, Malwai $\to$ Punjabi), format natural parent language response with preserved colloquial terms.
3. **Level 3 (National Standard Fallback)**: Fallback to Hindi if regional language synthesis is degraded.
4. **Level 4 (Universal Safety Fallback)**: Fallback to English if Hindi synthesis is unavailable.

---

## 5. Offline & Degraded Mode Capability Matrix

| Capability | Online Mode | Offline / Local Mode |
|---|---|---|
| **Weather** | Live Open-Meteo API | Cached daily forecast + Historical average |
| **Crop Recommendation (Mode A)** | Full XGBoost V2 inference | Full XGBoost V2 inference (Local model) |
| **Crop Recommendation (Mode B)** | SoilGrids estimated pH + Suitability | Local Soil type matrix + ICAR Suitability |
| **Disease Knowledge** | Live RAG + ICAR Knowledge base | SQLite ICAR Disease Knowledge Base |
| **Market Prices** | Live Agmarknet API + Prophet ML | Cached Mandi modal prices + LightGBM forecast |
| **Agricultural Vocabulary** | In-memory trie / synonym lookup | In-memory trie / synonym lookup |
| **Navigation** | Whitelist destination routing | Whitelist destination routing |

---

## 6. Safety & Audio Privacy Guarantees

1. **Zero Data Fabrication**: $N, P, K, \text{pH}$, weather, and mandi prices are strictly verified. Mode B explicitly reports $N/P/K$ as `UNAVAILABLE`.
2. **In-Memory Audio Life Cycle**: Audio bytes are processed in memory and deleted (`del audio_bytes`) immediately upon completion.
3. **Discrete Confidence Separation**: ASR confidence, language confidence, intent confidence, and agronomic recommendation scores remain distinct.
