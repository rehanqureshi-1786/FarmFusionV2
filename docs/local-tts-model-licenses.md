# FarmFusion Local Neural TTS Model License & Provenance Inventory

## 1. Governance & Licensing Framework

FarmFusion's on-device neural voice intelligence stack relies strictly on authentic open-source neural weights released under explicit research and open-source licenses. All models are downloaded directly from verified upstream repositories without modifications to weights or parameter structures.

---

## 2. Model License Inventory

| Target Language | Language Code | Model Name | Upstream Repository / Author | License Type | Commercial Use Terms | Checkpoint Size | Sample Rate | Runtime Engine |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Hindi** | `hi` | `farmfusion_tts_hindi_vits_v1` | `facebook/mms-tts-hin` (Meta AI) | `CC-BY-NC 4.0` | Non-commercial research / education | 145 MB | 16,000 Hz | PyTorch / Transformers / CPU |
| **Marathi** | `mr` | `farmfusion_tts_marathi_vits_v1` | `facebook/mms-tts-mar` (Meta AI) | `CC-BY-NC 4.0` | Non-commercial research / education | 145 MB | 16,000 Hz | PyTorch / Transformers / CPU |
| **Gujarati** | `gu` | `farmfusion_tts_gujarati_vits_v1` | `facebook/mms-tts-guj` (Meta AI) | `CC-BY-NC 4.0` | Non-commercial research / education | 145 MB | 16,000 Hz | PyTorch / Transformers / CPU |
| **Bengali** | `bn` | `farmfusion_tts_bengali_vits_v1` | `facebook/mms-tts-ben` (Meta AI) | `CC-BY-NC 4.0` | Non-commercial research / education | 145 MB | 16,000 Hz | PyTorch / Transformers / CPU |
| **Tamil** | `ta` | `farmfusion_tts_tamil_vits_v1` | `facebook/mms-tts-tam` (Meta AI) | `CC-BY-NC 4.0` | Non-commercial research / education | 145 MB | 16,000 Hz | PyTorch / Transformers / CPU |
| **Telugu** | `te` | `farmfusion_tts_telugu_vits_v1` | `facebook/mms-tts-tel` (Meta AI) | `CC-BY-NC 4.0` | Non-commercial research / education | 145 MB | 16,000 Hz | PyTorch / Transformers / CPU |
| **Punjabi** | `pa` | `farmfusion_tts_punjabi_vits_v1` | `facebook/mms-tts-pan` (Meta AI) | `CC-BY-NC 4.0` | Non-commercial research / education | 145 MB | 16,000 Hz | PyTorch / Transformers / CPU |

---

## 3. Modular Mobile Distribution Strategy

To prevent bloating the base Android APK (which would exceed 1 GB if all weights were bundled), FarmFusion follows a **Modular Language Pack Architecture**:

1. **Base Android Application**: Ships with core NLU rules, intent slots, and cloud Bhashini client ($<30\text{ MB}$).
2. **On-Demand Language Pack Download**: The farmer selects their primary language during onboarding. The 145 MB VITS neural model package is downloaded on-demand over Wi-Fi/cellular and stored in the app's sandboxed external files directory.
3. **Hardware Requirements**:
   - RAM: $\sim 150\text{ MB}$ dynamic memory per active model.
   - Storage: $145\text{ MB}$ flash storage per installed language pack.
   - Execution: 100% CPU compatible (ARM64 / x86_64).
