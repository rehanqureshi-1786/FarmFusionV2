# FarmFusion Custom Neural TTS Gap Analysis

## 1. Executive Summary

This gap analysis documents the precise linguistic varieties where **no suitable open-source pretrained neural TTS model exists** in Meta MMS, AI4Bharat, or other open repositories. It establishes the exact technical and dataset requirements necessary if custom fine-tuning or training is to be undertaken in future phases.

---

## 2. Unrepresented Varieties Requiring Custom Fine-Tuning

| Language / Dialect | Geographic Belt | Farmer Demographics | Dominant Script | Baseline Pretrained Model to Fine-Tune | Required Clean Speech Data | Target Speaker Count | Estimated Compute Requirements |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Marwari (`rwr`)** | Western Rajasthan (Jodhpur, Barmer, Bikaner, Jaisalmer, Nagaur) | $\sim 8.5\text{M}$ farmers (Pearl millet, guar, cumin, mustard) | Devanagari | `facebook/mms-tts-hin` (Hindi VITS) | 15–20 hours transcribed | 4–6 native speakers | 1x NVIDIA T4 (8 GPU-hours) |
| **Mewari (`mtr`)** | Southern Rajasthan (Udaipur, Rajsamand, Chittorgarh, Bhilwara) | $\sim 5.2\text{M}$ farmers (Maize, wheat, pulses) | Devanagari | `facebook/mms-tts-hin` (Hindi VITS) | 10–15 hours transcribed | 3–5 native speakers | 1x NVIDIA T4 (6 GPU-hours) |
| **Bhojpuri (`bho`)** | Eastern UP & Western Bihar (Varanasi, Gorakhpur, Patna, Bhojpur) | $\sim 35\text{M}$ farmers (Sugarcane, wheat, rice) | Devanagari | `facebook/mms-tts-hin` (Hindi VITS) | 20–25 hours transcribed | 6–8 native speakers | 1x NVIDIA T4 (10 GPU-hours) |
| **Gondi (`gon`)** | Central India (Madhya Pradesh, Chhattisgarh, Maharashtra, Telangana) | $\sim 3.0\text{M}$ tribal farmers (Millets, pulses, forest produce) | Devanagari / Telugu | `facebook/mms-tts-tel` (Telugu VITS) | 15–20 hours transcribed | 4–6 native speakers | 1x NVIDIA T4 (8 GPU-hours) |
| **Santali (`sat`)** | Jharkhand, West Bengal, Odisha | $\sim 7.5\text{M}$ tribal farmers (Paddy, vegetables) | Ol Chiki / Roman | `facebook/mms-tts-ben` (Bengali VITS) | 20 hours transcribed | 4–6 native speakers | 1x NVIDIA T4 (8 GPU-hours) |
| **Kashmiri (`kas`)** | Jammu & Kashmir | $\sim 2.5\text{M}$ farmers (Apples, saffron, walnuts) | Perso-Arabic / Devanagari | `facebook/mms-tts-urd-script_arabic` | 15 hours transcribed | 4–6 native speakers | 1x NVIDIA T4 (8 GPU-hours) |
| **Konkani (`kok`)** | Goa, Coastal Maharashtra & Karnataka | $\sim 2.0\text{M}$ farmers (Cashew, paddy, spices) | Devanagari / Kannada | `facebook/mms-tts-mar` (Marathi VITS) | 12 hours transcribed | 3–5 native speakers | 1x NVIDIA T4 (6 GPU-hours) |

---

## 3. Decision Matrix: When is Custom Training Justified?

Custom training is **NOT** proposed indiscriminately. It is justified only when:
1. **No Native Checkpoint Exists Upstream**: Verified that neither Meta MMS nor AI4Bharat has an open checkpoint.
2. **High Agronomic Relevance**: Farmer population exceeds 1 million in key crop belts.
3. **Phonetic Divergence from Parent**: Where parent language TTS causes high farmer cognitive load or intelligibility degradation (e.g. distinct Marwari verbal conjugations `-ला`, `-सी` vs Hindi `-गा`).
4. **Legitimate Data Provenance**: Verified dataset with explicit CC / open audio licenses (never scraped copyrighted audio).

*Current Action*: **ZERO CUSTOM TRAINING INITIATED** (Awaiting explicit user directive).
