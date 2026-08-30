# FarmFusion Multilingual & Regional Dialect Voice Model Training Pipeline

## 1. Executive Summary

This document specifies FarmFusion's reproducible training infrastructure for Indian language and regional dialect voice models. It establishes data provenance, licensing gates, speaker-disjoint splitting, lightweight edge model architectures, and multi-dimensional demographic evaluation without synthesizing fake speech or modifying existing crop/disease models.

---

## 2. Training Repository Layout

The voice training infrastructure lives inside `ml_training/voice/`, decoupled from existing crop recommendation models:

```
ml_training/voice/
├── datasets/
│   ├── manifest.py       # DatasetManifest schema & approval gates
│   ├── loader.py         # Type A/B/C/D dataset loaders (Speaker-disjoint partitioning)
│   ├── gates.py          # Pre-training quality & licensing verification gates
│   └── ingestion.py      # Authenticated dialect & speech data ingestion
├── preprocessing/
│   ├── audio_processor.py# PCM16 normalization, SNR estimation, VAD trimming
│   └── text_normalizer.py# Unicode NFKC, Nukta normalization, entity canonicalization
├── lid/
│   └── train_lid.py      # Language identification training (14 Indian languages)
├── dialect/
│   └── train_dialect.py  # Dialect classifier training (Marwari, Mewari, Bhojpuri, etc.)
├── nlu/
│   ├── schema.py         # Canonical agricultural intents & typed slots
│   └── train_nlu.py      # Lightweight intent & slot model training
├── asr/
│   └── train_asr.py      # ASR adaptation specs (PEFT / LoRA on IndicWhisper)
├── tts/
│   └── train_tts.py      # TTS voice adaptation specs (Piper / VITS)
├── evaluation/
│   ├── metrics.py        # WER, CER, Agricultural Entity Accuracy, F1
│   └── evaluate.py       # Demographic slice evaluation (standard, rural, dialect)
├── export/
│   ├── exporter.py       # Versioned model export (models/<task>/<lang>/<ver>/)
│   └── packager.py       # Modular Language Pack bundle generator
└── configs/              # Standard training hyperparameter templates
```

---

## 3. Dataset Requirements, Provenance & Licensing Policy

### 3.1 Supported Dataset Types

| Dataset Type | Description | Strict Quality Requirements |
| :--- | :--- | :--- |
| **`text_only`** | Plain text utterances for LID/Dialect identification | Labeled by language/dialect, normalized script, min 10 samples. |
| **`intent_slot`** | Text utterances labeled with agricultural intent & slots | Annotated with canonical FarmFusion intents and typed entity slots. |
| **`audio_asr`** | Speech audio + verbatim text transcript | Clean mono PCM16 @ 16kHz, labeled `speaker_id` for disjoint splitting, duration 0.5s–30s, SNR > 10dB. |
| **`audio_tts`** | Studio/clean single or multi-speaker audio + phonetic transcripts | 22.05kHz mono audio, exact phonetic alignments, zero background noise. |

### 3.2 Licensing & Approval Gate

Every dataset requires a `DatasetManifest` registered with:
- `license`: Must be an approved open/research/commercial license (`GODL-India`, `CC-BY-4.0`, `MIT`, `Apache-2.0`).
- `approved_for_training = true`: Explicit verification by the team.
- `is_synthetic = false`: **Synthetic speech data is strictly rejected by validation gates.**

```python
# Gate Enforcement: Training halts immediately if validation fails
DatasetQualityGate.assert_gate(manifest, data_file_path, min_samples=20)
```

---

## 4. Training Pipelines by Modality

### 4.1 Language Identification (LID)
- **Architecture**: Character 2-to-4 gram TF-IDF + Calibrated Logistic Regression.
- **Languages Covered**: All 14 Indian languages (`hi`, `gu`, `mr`, `pa`, `bn`, `ta`, `te`, `kn`, `ml`, `or`, `as`, `ur`, `mai`, `en`).
- **Target Size**: $< 5$ MB.
- **Latency**: $< 2$ ms on CPU.

### 4.2 Regional Dialect Understanding
- **Architecture**: Word-level character n-gram + morphological suffix/prefix matchers.
- **Dialects**: Marwari (`rwr`), Mewari (`mew`), Dhundhari (`dhu`), Bhojpuri (`bho`), Haryanvi (`bgc`), Awadhi (`awa`), Chhattisgarhi (`hne`).
- **Outputs**: Detected dialect + Normalized canonical agricultural text.

### 4.3 Agricultural NLU (Intent & Slot Filling)
- **Architecture**: Multi-class linear classifier with calibrated confidence scoring + Agricultural Entity Dictionary extractor.
- **Intents Covered**: 18 canonical agricultural intents (`weather`, `crop_recommendation`, `crop_care`, `disease`, `mandi`, `scheme`, `soil`, `irrigation`, `fertilizer`, `navigation`, `repeat_last`, `speech_control`, `what_if`, `greeting_help`, etc.).
- **Evaluation**: Evaluated on stratified test sets with weighted F1 and slot extraction accuracy.

### 4.4 ASR Adaptation (Speech-to-Text)
- **Base Architecture**: `ai4bharat/indicwhisper-hindi` / `Conformer-CTC`.
- **Technique**: Parameter-Efficient Fine-Tuning (PEFT / LoRA with $r=16$, $\alpha=32$).
- **Loss Weighting**: $2.0\times$ loss weight on critical agricultural entities (crop names, fertilizers, mandi market names, pest symptoms).
- **Partitioning**: Strictly speaker-disjoint splits to prevent acoustic speaker leakage.

### 4.5 TTS Voice Adaptation (Text-to-Speech)
- **Base Architecture**: `piper_vits` Int8.
- **Target**: Single-speaker high-intelligibility rural dialect voice.
- **Constraint**: No native dialect TTS claim is made until subjective MOS and objective pronunciation accuracy tests pass.

---

## 5. Multi-Dimensional Demographic Evaluation

Models are evaluated not only by overall aggregate scores, but across 5 specific demographic slices:

```python
slices = {
    "standard_speech": "Standard urban/formal language pronunciation",
    "rural_speech": "Rural acoustic environment and colloquial speech speed",
    "code_switched": "Mixed English-Hindi / Regional-English utterances",
    "agricultural_vocabulary": "Accuracy on technical crop/disease/soil keywords",
    "regional_dialect": "Utterances containing non-standard dialect syntax"
}
```

### Metrics Tracked:
- **WER (Word Error Rate)** & **CER (Character Error Rate)**
- **Agricultural Entity Accuracy** (Percentage of recognized agricultural keywords)
- **Intent Weighted F1 & Slot F1**
- **Latency (ms per second of audio)**
- **Model Binary Size (MB)**

---

## 6. Export, Optimization & Android Deployment

Trained models are exported using strict semantic versioning:

```
backend/models/voice/
├── nlu/
│   └── hi/
│       └── 1.0.0/
│           ├── agri_nlu_hi_1.0.0.joblib
│           └── metadata.json (includes SHA-256 checksum)
└── asr/
    └── rwr/
        └── 0.1.0/
            ├── rwr_conformer_int8.onnx
            └── metadata.json
```

### Packaging into Language Packs:
Trained models and vocabulary tables are compiled via `LanguagePackBundleGenerator` into:
`backend/app/voice/local/language_packs/<language_code>/`
matching the runtime format of `LanguagePackageManager` without requiring application rebuilds.

---

## 7. Operational Limitations & Honest Constraints

1. **Dialect Acoustic Data Scarcity**: Pure Marwari / Mewari conversational speech corpora remain limited. Models rely on Hindi ASR with dialect vocabulary normalization until verified field recording datasets are curated.
2. **On-Device RAM Ceilings**: Devices in the `LOW_END` tier ($\le$ 2.5GB RAM) execute rule-based NLU and cloud fallback for speech to avoid out-of-memory crashes.
3. **Zero Data Fabrication**: Weather and market numbers are never predicted by NLP/ASR models — they are always populated by deterministic tools (`Open-Meteo` & `Prophet+LightGBM`).
