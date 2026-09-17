# FarmFusion F7 Voice Orchestrator Evaluation Results

**Evaluation Timestamp**: 2026-09-17 18:02:48 UTC
**Evaluation Engine**: Canonical LangGraph StateGraph (`app.orchestrator.graph.run_orchestrator_pipeline`)
**Target Dataset**: [`backend/tests/data/f7_voice_generalization_dataset.json`](file:///home/rdj/FarmFusionFinal/backend/tests/data/f7_voice_generalization_dataset.json)

---

## 1. Executive Summary
- **Total Test Conversations**: 267
- **Total Conversational Turns**: 288
- **Overall Strict Pass Rate**: **`4.49%`** (12/267)
- **Average Turn Latency**: **`18796.1 ms`**
- **P95 Turn Latency**: **`41918.1 ms`**
- **Runtime Unhandled Failures**: **`93`**

## 2. Independent Scoring Matrix (15 Dimensions)
| # | Scoring Dimension | Pass Rate (%) | Strict Pass Requirement |
|---|---|---|---|
| 01 | **Intent Accuracy** | `36.11%` | Correct domain classification without adjacent confusion |
| 02 | **Entity Accuracy** | `76.04%` | Extraction of crop, pest, fertilizer, or mandi |
| 03 | **Temporal Accuracy** | `70.14%` | Mapping of relative days (today, tomorrow, next week) |
| 04 | **Location Accuracy** | `77.78%` | Extraction/inheritance of district or farm location |
| 05 | **Capability Selection** | `20.83%` | Activation of appropriate orchestrator capabilities |
| 06 | **Multi-Intent Completeness** | `91.32%` | Full execution DAG without dropping secondary intents |
| 07 | **Context Resolution** | `99.65%` | Preserving antecedent entities across multi-turn dialogs |
| 08 | **Required-Input Safety** | `95.83%` | Gating missing photos/phone/location safely |
| 09 | **Tool Argument Correctness** | `100.00%` | Valid arguments passed into tool functions |
| 10 | **Tool Execution Correctness** | `67.71%` | Clean execution of tools without crashes |
| 11 | **Typed Action Correctness** | `97.22%` | UI action routing (NAVIGATE, CLARIFY, ANSWER) |
| 12 | **Out-of-Scope Safety** | `100.00%` | Safe polite refusal without fake agriculture advice |
| 13 | **Numerical Grounding** | `100.00%` | Numbers derived solely from tools, zero LLM fabrication |
| 14 | **Response-Language Correctness** | `67.01%` | Responses delivered in farmer's primary language |
| 15 | **RAG Grounding** | `100.00%` | Agronomic advisory grounded in knowledge base |

## 3. Language-wise Generalization Breakdown
| Language | Code | Total Convs | Strict Pass | Pass Rate (%) | Evaluation Assessment |
|---|---|---|---|---|---|
| Bn | `bn` | 20 | 0 | **`0.00%`** | Limitation Area |
| En | `en` | 26 | 1 | **`3.85%`** | Limitation Area |
| Gu | `gu` | 20 | 1 | **`5.00%`** | Limitation Area |
| Hi | `hi` | 37 | 3 | **`8.11%`** | Limitation Area |
| Hinglish | `hinglish` | 31 | 3 | **`9.68%`** | Limitation Area |
| Kn | `kn` | 18 | 0 | **`0.00%`** | Limitation Area |
| Marwari | `marwari` | 19 | 0 | **`0.00%`** | Limitation Area |
| Ml | `ml` | 17 | 0 | **`0.00%`** | Limitation Area |
| Mr | `mr` | 20 | 1 | **`5.00%`** | Limitation Area |
| Pa | `pa` | 20 | 1 | **`5.00%`** | Limitation Area |
| Ta | `ta` | 20 | 2 | **`10.00%`** | Limitation Area |
| Te | `te` | 19 | 0 | **`0.00%`** | Limitation Area |

## 4. Domain-wise Generalization Breakdown
| Domain Category | Total Convs | Strict Pass | Pass Rate (%) | Primary Failure Mode |
|---|---|---|---|---|
| `ADVERSARIAL` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `AMBIGUOUS` | 13 | 6 | **`46.15%`** | Extraction/Fallback |
| `CALLING` | 14 | 0 | **`0.00%`** | Extraction/Fallback |
| `CROP_RECOMMENDATION` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `DISASTER_RISK` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `DISEASE_DETECTION` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `FARM_SECURITY` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `LOCATION` | 14 | 2 | **`14.29%`** | Extraction/Fallback |
| `MANDI_MARKET` | 14 | 0 | **`0.00%`** | Extraction/Fallback |
| `MISSING_INPUT` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `MULTI_INTENT` | 14 | 0 | **`0.00%`** | Extraction/Fallback |
| `MULTI_TURN_CONTEXT` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `NATURAL_SPEECH` | 14 | 0 | **`0.00%`** | Extraction/Fallback |
| `OUT_OF_SCOPE` | 14 | 0 | **`0.00%`** | Extraction/Fallback |
| `RAG_KNOWLEDGE` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `SCHEMES` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `SMART_IRRIGATION` | 14 | 0 | **`0.00%`** | Extraction/Fallback |
| `TEMPORAL` | 13 | 2 | **`15.38%`** | Extraction/Fallback |
| `VOICE_ASR_ERRORS` | 13 | 0 | **`0.00%`** | Extraction/Fallback |
| `WEATHER` | 13 | 2 | **`15.38%`** | Extraction/Fallback |

## 5. Root Cause Distribution Analysis
| Root Cause Category | Failures | % of Total Failures | Technical Description |
|---|---|---|---|
| `tool/runtime failure` | 93 | `33.8%` | Identified in evaluation pipeline |
| `intent classification failure` | 59 | `21.5%` | Identified in evaluation pipeline |
| `tool selection failure` | 35 | `12.7%` | Identified in evaluation pipeline |
| `multilingual limitation` | 32 | `11.6%` | Identified in evaluation pipeline |
| `temporal normalization failure` | 24 | `8.7%` | Identified in evaluation pipeline |
| `planner/DAG failure` | 23 | `8.4%` | Identified in evaluation pipeline |
| `entity extraction failure` | 4 | `1.5%` | Identified in evaluation pipeline |
| `location extraction failure` | 4 | `1.5%` | Identified in evaluation pipeline |
| `context inheritance failure` | 1 | `0.4%` | Identified in evaluation pipeline |

## 6. Top 20 Failure Cases (Detailed Audit)
| ID | Turn | Lang | Domain | User Query | Failed Dimension | Root Cause |
|---|---|---|---|---|---|---|
| `A_04` | T1 | `pa` | `WEATHER` | *"ਕੱਲ੍ਹ ਸਵੇਰੇ ਲੁਧਿਆਣੇ ਵਿੱਚ ਤੇਜ਼ ਹਵਾ ਚੱਲੇਗੀ ਕੀ?"* | `temporal_accuracy` | `temporal normalization failure` |
| `A_02` | T1 | `hinglish` | `WEATHER` | *"Is week rain ka kya scene hai Kota mein? Barish aayegi kya?"* | `temporal_accuracy` | `temporal normalization failure` |
| `A_06` | T1 | `bn` | `WEATHER` | *"আগামী তিন দিন বর্ধমানে কি ভারী বৃষ্টির সম্ভাবনা আছে?"* | `temporal_accuracy, location_accuracy` | `temporal normalization failure` |
| `A_09` | T1 | `kn` | `WEATHER` | *"ಹಾಸನದಲ್ಲಿ ಮುಂದಿನ 7 ದಿನಗಳ ಹವಾಮಾನ ವರದಿ ನೀಡಿ."* | `temporal_accuracy, location_accuracy, capability_selection` | `temporal normalization failure` |
| `A_03` | T1 | `gu` | `WEATHER` | *"આવતીકાલે બપોરે રાજકોટમાં તાપમાન કેટલું રહેશે?"* | `temporal_accuracy` | `temporal normalization failure` |
| `A_08` | T1 | `te` | `WEATHER` | *"వరంగల్‌లో ఈ రాత్రి వర్షం పడే అవకాశం ఉందా?"* | `temporal_accuracy, location_accuracy` | `temporal normalization failure` |
| `A_05` | T1 | `mr` | `WEATHER` | *"परवा नाशिकमध्ये ढगाळ हवामान राहील की कडक ऊन पडेल?"* | `temporal_accuracy, capability_selection` | `temporal normalization failure` |
| `B_01` | T1 | `hi` | `SMART_IRRIGATION` | *"गेहूं में अभी पानी देना चाहिए या मिट्टी में नमी काफी है?"* | `intent_accuracy, capability_selection` | `intent classification failure` |
| `A_10` | T1 | `ml` | `WEATHER` | *"വയനാട്ടിൽ നാളെ കനത്ത മഴ പെയ്യാൻ സാധ്യതയുണ്ടോ?"* | `intent_accuracy, temporal_accuracy, location_accuracy, capability_selection` | `multilingual limitation` |
| `A_13` | T1 | `hi` | `WEATHER` | *"अगले तीन दिन धूप निकलेगी या बादल छाये रहेंगे उदयपुर में?"* | `temporal_accuracy, location_accuracy` | `temporal normalization failure` |
| `A_11` | T1 | `marwari` | `WEATHER` | *"काल जोधपुर कानी मींह बरसेगा के? खेत में काम करणो है।"* | `temporal_accuracy` | `temporal normalization failure` |
| `B_02` | T1 | `hinglish` | `SMART_IRRIGATION` | *"Kal irrigation karu kya? Barish ka forecast bhi dekh lena Jaipur mein."* | `intent_accuracy, multi_intent_completeness` | `planner/DAG failure` |
| `B_03` | T1 | `gu` | `SMART_IRRIGATION` | *"કપાસમાં ટપક પદ્ધતિથી પાણી ક્યારે આપવું યોગ્ય રહેશે?"* | `intent_accuracy, temporal_accuracy, capability_selection` | `intent classification failure` |
| `B_08` | T1 | `te` | `SMART_IRRIGATION` | *"మిరప తోటకు రేపు నీరు పెట్టవచ్చా లేదా వర్షం పడుతుందా?"* | `intent_accuracy, entity_accuracy, capability_selection, multi_intent_completeness` | `planner/DAG failure` |
| `B_06` | T1 | `bn` | `SMART_IRRIGATION` | *"আলুর জমিতে সেচ আজ দেওয়া উচিত না কি মাটি বেশি ভেজা?"* | `intent_accuracy, capability_selection` | `intent classification failure` |
| `B_07` | T1 | `ta` | `SMART_IRRIGATION` | *"கரும்பு பயிருக்கு இன்று தண்ணீர் பாய்ச்சலாமா? மண்ணில் ஈரப்பதம் குறைவு."* | `intent_accuracy, entity_accuracy, capability_selection` | `multilingual limitation` |
| `B_09` | T1 | `kn` | `SMART_IRRIGATION` | *"ರಾಗಿ ಬೆಳೆಗೆ ಈಗ ನೀರುಣಿಸಬೇಕೇ? ಭೂಮಿ ಒಣಗಿದಂತೆ ಕಾಣುತ್ತಿದೆ."* | `intent_accuracy, entity_accuracy, temporal_accuracy, capability_selection` | `multilingual limitation` |
| `B_04` | T1 | `mr` | `SMART_IRRIGATION` | *"कांद्याच्या पिकाला पाणी कधी देणे सर्वात योग्य ठरेल? जमीन कोरडी वाटतेय."* | `intent_accuracy, temporal_accuracy, capability_selection` | `intent classification failure` |
| `B_05` | T1 | `pa` | `SMART_IRRIGATION` | *"ਝੋਨੇ ਨੂੰ ਪਾਣੀ ਕੱਲ੍ਹ ਲਾਵਾਂ ਜਾਂ ਮੀਂਹ ਪੈਣ ਦੀ ਉਡੀਕ ਕਰਾਂ?"* | `intent_accuracy, entity_accuracy, temporal_accuracy, capability_selection, multi_intent_completeness` | `planner/DAG failure` |
| `A_12` | T1 | `en` | `WEATHER` | *"Should I harvest my wheat tomorrow considering the weather in Karnal?"* | `intent_accuracy, entity_accuracy, temporal_accuracy, location_accuracy, capability_selection, tool_execution_correctness, response_language_correctness` | `tool/runtime failure` |

## 7. Key Findings & Recommendations for Orchestrator V2
1. **Multilingual Entity Extraction in South Indian Languages**: Kannada (`kn`), Malayalam (`ml`), Tamil (`ta`), and Telugu (`te`) experience lower deterministic regex match rates when LLM latency triggers fallback. Recommend expanding native token maps for crops and weather terms.
2. **Compound Multi-Intent DAG Execution**: When users combine weather and irrigation simultaneously in one sentence, the deterministic fallback occasionally prioritizes the first intent. Enhancing parallel DAG node execution in LangGraph will resolve this.
3. **Voice ASR Robustness**: Phonetic misspellings ('week' for 'wheat', 'lasal gaon' as two tokens) require phonetic Levenshtein alignment in the agricultural normalizer prior to intent routing.
4. **Zero Numerical Hallucination**: Open-Meteo and Mandi ML verification nodes successfully blocked all user-injected adversarial price overrides (e.g. confirming ₹5000 rate). Grounding boundaries held firmly.
