# Phase F6: Grounded Response Synthesis & Typed Response Envelope

## Executive Summary

The **Response Synthesizer Node** (`app/orchestrator/nodes/synthesizer.py`) synthesizes rural-friendly, conversational explanations (1–3 sentences max) in Indian languages and dialects while enforcing **100% numerical truth**. The synthesizer emits a canonical `ResponseEnvelope` consumed by the Kotlin Android frontend, Bhashini TTS voice synthesis, and automated telephony calling agents.

---

## 1. Synthesis Pipeline Architecture

```
Validated Tool Results + Verified Fact Set + Validated RAG Chunks
                            ↓
             [ Cloud LLM Synthesis Attempt ]
           (OpenRouter Gemma 3 12B / Groq)
                            ↓
           [ Numerical Immutability Check ]
                     /            \
                 Pass              Fail (Altered Number)
                  /                  \
          Emit Envelope          [ Retry Once with Mandate ]
                                     /            \
                                  Pass            Fail
                                   /                \
                           Emit Envelope     Deterministic Safe Fallback
```

---

## 2. Structured Response Envelope Contract

The orchestrator produces a validated Pydantic model (`app/schemas/envelope.py`):

```json
{
  "response_text": "आज कोटा मंडी में सोयाबीन का औसत भाव ₹2260 प्रति क्विंटल दर्ज किया गया है। मॉडल के अनुसार आगे भाव में नरमी आ सकती है, अभी बेचना फायदेमंद रहेगा।",
  "action_payload": {
    "action": "ANSWER",
    "destination": null,
    "android_route": null,
    "required_input": null,
    "target_phone": null,
    "call_reason": null,
    "notification_title": null,
    "notification_body": null
  },
  "citations": [],
  "verified_facts": [
    {
      "key": "mandi_current_price",
      "value": 2260.0,
      "unit": "INR/quintal",
      "source_tool": "mandi_current_price_tool",
      "is_numeric": true
    }
  ],
  "confidence": 0.95,
  "confidence_tier": "high",
  "warnings": [],
  "language": "hi",
  "dialect": null,
  "tts_language": "hi",
  "native_tts": true,
  "fallback_used": false,
  "fallback_reason": null
}
```

---

## 3. Client Action Directives

All client actions are strictly typed enums:

| Action Directive | Trigger Conditions | Client Behavior (Android / Calling) |
| :--- | :--- | :--- |
| `ANSWER` | Normal agricultural advice | Renders chat card, plays TTS voice |
| `CLARIFY` | Intent confidence `< 0.6` or ambiguous query | Prompts farmer with clarifying speech |
| `NAVIGATE` | Intent navigation, or disease without leaf photo | Navigates Kotlin `navController` to target screen |
| `REQUEST_INPUT` | Missing mandatory slot (e.g. `LEAF_IMAGE`) | Opens camera viewfinder / audio prompt |
| `CALL` | Critical disaster warning (`CRITICAL` level) | Dispatches automated telephony alert |
| `NOTIFY` | IoT animal perimeter intrusion / price alerts | Posts Android push notification |

---

## 4. Multilingual & Dialect Preservation

All numbers and units are preserved with exact equality across languages:

| Language | Regional Localized Output | Verified Numerical Fact |
| :--- | :--- | :--- |
| **Hindi (`hi`)** | `आज कोटा में सोयाबीन का औसत भाव ₹2260 प्रति क्विंटल दर्ज किया गया है।` | `2260.0` |
| **Gujarati (`gu`)** | `આજે કોટામાં સોયાબીનનો સરેરાશ ભાવ ₹2260 પ્રતિ ક્વિન્ટલ છે.` | `2260.0` |
| **Marathi (`mr`)** | `आज कोटा मध्ये सोयाबीनचा सरासरी भाव ₹2260 प्रति क्विंटल आहे.` | `2260.0` |
| **Punjabi (`pa`)** | `ਅੱਜ ਕੋਟਾ ਵਿੱਚ ਸੋਇਆਬੀਨ ਦਾ ਭਾਅ ₹2260 ਪ੍ਰਤੀ ਕੁਇੰਟਲ ਹੈ।` | `2260.0` |
| **Marwari (`rwr`)** | `आज कोटा मंडी में सोयाबीन रो भाव ₹2260 प्रति क्विंटल चाल रैयो है।` | `2260.0` |
| **English (`en`)** | `Today at Kota, the modal price for Soybean is ₹2260 per quintal.` | `2260.0` |

---

## 5. Deterministic Safe Fallback Synthesizer

If cloud LLM providers are unreachable, return malformed JSON, or violate numerical constraints:
- The system immediately invokes `deterministic_fallback_synthesizer`.
- Generates natural, idiomatically translated responses covering all 14 intents.
- Appends verified RAG treatment protocols and ICAR citations.
- Guarantees 100% service uptime with zero risk of hallucinations.
