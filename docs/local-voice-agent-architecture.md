# FarmFusion Local Voice Intelligence & Trainable Agent Architecture

## 1. Executive Summary

FarmFusion's Local Voice Intelligence Layer extends the multilingual Farmer Operating Assistant into a modular, trainable, on-device runnable speech and language agent. It bridges edge execution (Android / Jetpack Compose) and server-side processing (FastAPI / LangGraph) with strict zero-fabrication rules, deterministic agricultural tool groundings, and explicit fallback transparency.

---

## 2. Target System Architecture

```
                                  FARMER
                                    |
                                    v
                            Audio / Text Input
                                    |
                                    v
                           Voice Runtime Router
                                    |
              +---------------------+---------------------+
              |                                           |
         [OFFLINE / LOCAL]                             [HYBRID / CLOUD]
              |                                           |
              v                                           v
         Local ASR                                    Bhashini /
     (ONNX / Whisper Tiny)                          Cloud Providers
              |                                           |
              +---------------------+---------------------+
                                    |
                                    v
                        Language & Dialect Layer
                   (LID + Morphological Normalization)
                                    |
                                    v
                         Agricultural NLU Layer
                    (Intent & Slot Semantic Parser)
                                    |
                                    v
                         Canonical Semantic Form
                                    |
                                    v
                          FarmFusion Agent Core
                       (LangGraph Orchestrator)
                                    |
                                    v
                         Typed Tool Registry
           (Crop Rec V2, Mandi Prophet, Open-Meteo Weather)
                                    |
                                    v
                         Verified Tool Result
                                    |
                                    v
                      Multilingual Response Layer
                  (Rural Grounded Synthesizer)
                                    |
              +---------------------+---------------------+
              |                                           |
          Local TTS                                   Cloud TTS
      (Piper / ONNX VITS)                        (Bhashini / Indic-TTS)
              |                                           |
              +---------------------+---------------------+
                                    |
                                    v
                                  FARMER
```

---

## 3. Core Subsystems & Components

### 3.1 Strict Local Model Interfaces (`backend/app/voice/local/`)

Every on-device model conforms to a strict interface exposing lifecycle methods and capabilities without leaking implementation details:

| Component | Abstract Base Interface | Engine Implementation | Supported Runtimes |
| :--- | :--- | :--- | :--- |
| **ASR** | `LocalASRModel` (`load`, `is_available`, `transcribe`) | `LocalASREngine` | ONNX Int8, Conformer, Whisper-tiny |
| **Language ID** | `LocalLanguageDetector` (`detect_language`) | `LocalLanguageDetectorEngine` | Unicode Script Blocks + Grapheme Lexicon |
| **Dialect** | `LocalDialectModel` (`detect_and_normalize`) | `LocalDialectEngine` | Morphological Dialect Grammar + Term Registry |
| **Agri NLU** | `LocalAgriculturalNLU` (`parse`) | `LocalAgriculturalNLUEngine` | Deterministic Agricultural Rule Engine |
| **Response** | `LocalResponseModel` (`generate_response`) | `LocalResponseEngine` | Rule-based Grounded Agricultural Synthesizer |
| **TTS** | `LocalTTSModel` (`synthesize`) | `LocalTTSEngine` | Piper ONNX Int8, VITS |

> **Zero-Fabrication Guarantee**: If a model binary does not exist on disk, `is_available()` returns `False` and inference returns explicit `MODEL_NOT_AVAILABLE`. FarmFusion never simulates or fabricates audio or agricultural predictions.

---

### 3.2 Device Capability Detection (`capabilities.py`)

To ensure smooth performance across low-end and high-end rural smartphones, the runtime dynamically detects device constraints:

```python
class DeviceTier(str, Enum):
    LOW_END = "low_end"       # <= 2.5GB RAM, <= 4 CPU cores -> Max model size: 120MB (Rule NLU + Int8 Tiny)
    MID_RANGE = "mid_range"   # 3GB-6GB RAM, 6-8 CPU cores -> Max model size: 350MB (ONNX Int8 ASR/TTS)
    HIGH_END = "high_end"     # >= 8GB RAM, NPU/GPU -> Max model size: 850MB (Full Indic models)
```

---

### 3.3 Modular Language Pack Architecture (`package_manager.py`)

Language support is decoupled into modular packs in `backend/app/voice/local/language_packs/`. The base application remains lightweight, while language-specific assets are loaded dynamically:

```
language_packs/
├── hi/               # Hindi (Tier 1 - Native)
├── gu/               # Gujarati (Tier 1 - Native)
├── mr/               # Marathi (Tier 1 - Native)
├── pa/               # Punjabi (Tier 1 - Native)
├── bn/               # Bengali (Tier 1 - Native)
├── ta/               # Tamil (Tier 1 - Native)
├── te/               # Telugu (Tier 1 - Native)
├── kn/               # Kannada (Tier 1 - Native)
├── ml/               # Malayalam (Tier 1 - Native)
├── or/               # Odia (Tier 2 - Partial)
├── as/               # Assamese (Tier 2 - Partial)
├── ur/               # Urdu (Tier 2 - Partial)
├── mai/              # Maithili (Tier 2 - Partial)
├── hi_rwr/           # Marwari Dialect (Tier 3 - Vocabulary Only + Hindi Parent TTS Fallback)
└── hi_mew/           # Mewari Dialect (Tier 3 - Vocabulary Only + Hindi Parent TTS Fallback)
```

Each language pack contains:
1. `metadata.json`: Pack ID, language/dialect, version, support tier (`NATIVE`, `PARTIAL`, `FALLBACK`, `VOCABULARY_ONLY`), size, model references.
2. `vocabulary.json`: 10-category verified agricultural lexicon (crops, soil, pests, fertilizers, operations).
3. `normalization.json`: Dialect variant to canonical entity mapping.
4. `prompts.json`: Grounded templates tailored for rural vocabulary.

---

### 3.4 Runtime Modes (`OFFLINE`, `HYBRID`, `ONLINE`)

| Mode | ASR Behavior | NLU / Tool Execution | Weather / Mandi Live Data | TTS Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **`OFFLINE`** | Local ONNX ASR (if installed) or honest `MODEL_NOT_AVAILABLE` | Local rule NLU + Local Crop Knowledge / Rules | **Never fabricated**. Returns explicit offline notice: *"मौसम/मंडी भाव के लिए इंटरनेट आवश्यक है"* | Local Piper TTS (if installed) or text-only response |
| **`HYBRID`** *(Default)* | Tries Local ASR $\to$ Falls back to Bhashini | Full LangGraph Orchestrator + Deterministic ToolRegistry | Real-time Open-Meteo & Prophet models | Tries Local TTS $\to$ Falls back to Bhashini / Indic-TTS |
| **`ONLINE`** | Bhashini Cloud ASR | Full LangGraph Orchestrator + Cloud LLM Synthesizer | Real-time Open-Meteo & Prophet models | Bhashini Cloud TTS |

---

## 4. Trainability & Model Evolution Pipeline

The architecture is built to ingest newly trained models without modifying the agent core:

```
                  Raw Farmer Speech & Dialect Utterances
                                    |
                                    v
                     Data Annotation & Audio Curation
                                    |
                                    v
               Model Fine-Tuning (Whisper / Conformer / Piper)
                                    |
                                    v
                    ONNX Export & Int8 Quantization
                                    |
                                    v
                 Model Checksum & Manifest Registration
                     (`LocalModelManifest` in Registry)
                                    |
                                    v
                       Packaged Language Pack Release
```

### Future Training Checkpoints:
1. **ASR**: Fine-tune `IndicWhisper` / `Conformer` on regional Marwari (`rwr`), Mewari (`mew`), and Bhojpuri (`bho`) field recordings.
2. **NLU**: Train a lightweight Intent Classification model on code-switched Hinglish/regional agronomic queries.
3. **TTS**: Train Piper VITS acoustic voice models for Marwari and Mewari to eliminate parent Hindi voice fallback.

---

## 5. Security, Verification & Data Governance

1. **Audio Privacy**: Raw voice audio bytes are never persisted to disk. They are held in memory during inference and immediately deallocated.
2. **Model Integrity**: Downloaded model binaries require SHA-256 checksum verification before runtime activation.
3. **Bandwidth Policy**: Model pack downloads are restricted on cellular data unless explicitly permitted by the user.
4. **Data Grounding**: All numeric agricultural figures (NPK, weather, mandi prices) come strictly from deterministic tools (Crop Model V2, Prophet, Open-Meteo) — LLMs and voice synthesizers never estimate or invent numbers.
