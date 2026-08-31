# FarmFusion Global Language & Regional Dialect Registry Audit

**Source of Truth**: `backend/app/voice/languages.py` (`LANGUAGE_REGISTRY`) & `backend/app/voice/providers.py`  
**Total Registered Languages & Regional Dialects**: **38 Entries**  
**Scheduled / Primary Languages**: 14 (Tier 1 Full Native Voice)  
**Regional Varieties / Dialects**: 24 (Tier 2 Understanding + Verified Parent Fallback)  

---

## 1. Complete India-Wide Language & Dialect Inventory

| Code | Language / Variety | Native Name | Type | Tier | Parent Language | Script | TTS Capability | ASR Capability |
|---|---|---|---|---|---|---|---|---|
| `hi` | Hindi | हिन्दी | Primary | 1 | None | Devanagari | Native (Bhashini/Local) | Native |
| `en` | English (India) | English | Primary | 1 | None | Latin | Native | Native |
| `gu` | Gujarati | ગુજરાતી | Primary | 1 | None | Gujarati | Native | Native |
| `mr` | Marathi | मराठी | Primary | 1 | None | Devanagari | Native | Native |
| `pa` | Punjabi | ਪੰਜਾਬੀ | Primary | 1 | None | Gurmukhi | Native | Native |
| `bn` | Bengali | বাংলা | Primary | 1 | None | Bengali | Native | Native |
| `ta` | Tamil | தமிழ் | Primary | 1 | None | Tamil | Native | Native |
| `te` | Telugu | తెలుగు | Primary | 1 | None | Telugu | Native | Native |
| `kn` | Kannada | ಕನ್ನಡ | Primary | 1 | None | Kannada | Native | Native |
| `ml` | Malayalam | മലയാളം | Primary | 1 | None | Malayalam | Native | Native |
| `or` | Odia | ଓଡ଼ିଆ | Primary | 1 | None | Odia | Native | Native |
| `as` | Assamese | অসমীয়া | Primary | 1 | None | Bengali-Assamese | Native | Native |
| `ur` | Urdu | اردو | Primary | 1 | None | Perso-Arabic | Native | Native |
| `mai` | Maithili | मैथिली | Primary | 1 | None | Devanagari | Native | Native |
| `rwr` | Marwari | मारवाड़ी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `mew` | Mewari | मेवाड़ी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `dhu` | Dhundhari | ढूंढाड़ी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `har` | Harauti | हाड़ौती | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `swv` | Shekhawati | शेखावाटी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `wbr` | Wagdi | वागड़ी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `bho` | Bhojpuri | भोजपुरी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `awa` | Awadhi | अवधी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `mag` | Magahi | मगही | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `hne` | Chhattisgarhi | छत्तीसगढ़ी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `bns` | Bundeli | बुंदेली | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `bgc` | Haryanvi | हरियाणवी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `bra` | Braj | ब्रज भाषा | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `gbm` | Garhwali | गढ़वाली | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `kfy` | Kumaoni | कुमाऊँनी | Dialect | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `ne` | Nepali | नेपाली | Primary/Reg | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |
| `mup` | Malwai | ਮਲਵਈ | Dialect | 2 | Punjabi (`pa`) | Gurmukhi | Regional Voice Fallback (`pa`) | Native Normalization |
| `doa` | Doabi | ਦੁਆਬੀ | Dialect | 2 | Punjabi (`pa`) | Gurmukhi | Regional Voice Fallback (`pa`) | Native Normalization |
| `vah` | Varhadi | वऱ्हाडी | Dialect | 2 | Marathi (`mr`) | Devanagari | Regional Voice Fallback (`mr`) | Native Normalization |
| `kat` | Kathiawari | કાઠિયાવાડી | Dialect | 2 | Gujarati (`gu`) | Gujarati | Regional Voice Fallback (`gu`) | Native Normalization |
| `kok` | Konkani | कोंकणी | Scheduled/Reg | 2 | Marathi (`mr`) | Devanagari | Regional Voice Fallback (`mr`) | Native Normalization |
| `tcy` | Tulu | ತುಳು | Regional | 2 | Kannada (`kn`) | Kannada | Regional Voice Fallback (`kn`) | Native Normalization |
| `kfa` | Kodava | ಕೊಡವ | Regional | 2 | Kannada (`kn`) | Kannada | Regional Voice Fallback (`kn`) | Native Normalization |
| `sa` | Sanskrit | संस्कृतम् | Scheduled | 2 | Hindi (`hi`) | Devanagari | Regional Voice Fallback (`hi`) | Native Normalization |

---

## 2. Architectural Truth & Capability Distinction

1. **Language vs Dialect Separation**:
   - Primary languages (`hi`, `gu`, `mr`, `pa`, `bn`, `ta`, `te`, `kn`, `ml`, `or`, `as`, `ur`, `mai`, `en`) maintain **native neural TTS and end-to-end ASR**.
   - Regional dialects (`rwr`, `mew`, `bho`, `bgc`, `hne`, etc.) are recognized through **probabilistic agricultural dialect detection and semantic vocabulary normalization**, while their audio generation uses verified parent-language TTS fallback (`hi`, `mr`, `gu`, `pa`, `kn`).
2. **Zero Fabrication**:
   - The UI and API never falsely label parent-language audio as native dialect audio.
   - Capability badges display `✓ Voice Available` for Tier 1 and `✓ Understanding • △ Voice Fallback` for Tier 2.
3. **Global Synchronization**:
   - When selected in **Profile → Language**, the setting persists across the application (Dashboard, Weather, Mandi, Farm Assistant, Voice Assistant, Notifications).
