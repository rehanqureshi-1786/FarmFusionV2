# 🎤 FarmFusion Voice Assistant

A production-ready multilingual voice assistant for Indian farmers, built with FastAPI and Groq AI.

## 🌟 Features

- **🧠 AI-Powered Intent Detection**: Automatically understands farmer queries
- **🌐 Multilingual Support**: Hindi, Hinglish, English, Marathi, Gujarati, Punjabi, Tamil, Telugu, Kannada, Malayalam, Bengali
- **🎯 Smart Actions**: Returns appropriate actions for Android app
- **💬 Natural Responses**: Responds in the same language as input
- **⚡ Fast & Efficient**: Uses Groq's ultra-fast LLM inference
- **🔄 Fallback System**: Graceful degradation when AI is unavailable

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Make sure you're in the backend directory
cd backend

# Install requirements (if not already installed)
pip install -r requirements.txt

# Add groq to requirements if not present
pip install groq
```

### 2. Set Up Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Groq API Key (Required for voice assistant)
# Get your free key at: https://console.groq.com
GROQ_API_KEY=your_groq_api_key_here

# Optional: Set custom model (defaults to llama-3.3-70b-versatile)
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 4. Test the Voice Assistant

Open your browser and go to: `http://localhost:8000/docs`

## 📚 API Documentation

### Main Endpoint: `POST /api/v1/voice`

Process farmer voice/text queries.

#### Request Format

```json
{
    "query": "गेहूं का रेट क्या है",
    "location": "Madhya Pradesh",
    "language_hint": "hi"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ | User's voice/text input |
| `location` | string | ❌ | Optional location context |
| `language_hint` | string | ❌ | Optional language code (hi, en, hi-en, etc.) |

#### Response Format

```json
{
    "intent": "get_mandi_price",
    "action": "show_result",
    "response": "गेहूं का वर्तमान भाव ₹2,150 प्रति क्विंटल है। भाव स्थिर हैं।",
    "data": {
        "crop": "wheat",
        "price": 2150,
        "unit": "per quintal",
        "trend": "stable"
    },
    "detected_language": "hi",
    "confidence": 0.95,
    "follow_up_suggestions": [
        "चावल का भाव क्या है?",
        "अगले महीने का अनुमान"
    ],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🌍 Supported Languages

| Code | Language | Script | Example |
|------|----------|--------|---------|
| `hi` | Hindi | Devanagari | "गेहूं का रेट क्या है" |
| `hi-en` | Hinglish | Roman | "gehu ka rate kya hai" |
| `en` | English | Latin | "what is wheat price" |
| `mr` | Marathi | Devanagari | "गहूंचा भाव काय आहे" |
| `gu` | Gujarati | Gujarati | "ઘઉંના ભાવ" |
| `pa` | Punjabi | Gurmukhi | "ਕਣਕ ਦੇ ਭਾਅ" |
| `ta` | Tamil | Tamil | "கோதுமை விலை" |
| `te` | Telugu | Telugu | "గోధుమ ధర" |
| `kn` | Kannada | Kannada | "ಗೋಧಿ ಬೆಲೆ" |
| `ml` | Malayalam | Malayalam | "ഗോതമ്പ് വില" |
| `bn` | Bengali | Bengali | "গমের দাম" |

## 🎯 Supported Intents

### 1. Get Weather (`get_weather`)

**Example Queries:**
- Hindi: "आज मौसम कैसा है", "कल बारिश होगी क्या"
- Hinglish: "mausam kaisa hai", "kal baarish hogi"
- English: "what's the weather today", "will it rain"

**Action:** `show_result`

### 2. Get Mandi Price (`get_mandi_price`)

**Example Queries:**
- Hindi: "गेहूं का रेट क्या है", "चावल का भाव"
- Hinglish: "gehu ka rate kya hai", "chawal ka bhav"
- English: "wheat price", "rate of rice"

**Action:** `show_result`

### 3. Crop Prediction (`crop_prediction`)

**Example Queries:**
- Hindi: "मुझे क्या बोना चाहिए", "कौन सी फसल अच्छी है"
- Hinglish: "konsi fasal lagau", "kya beej dalun"
- English: "which crop should I grow", "best crop for my land"

**Action:** `show_result`

### 4. Disease Detection (`disease_detection`)

**Example Queries:**
- Hindi: "पत्ते पीले हो रहे हैं", "कीड़े लग गए हैं"
- Hinglish: "paudhe pe kida lag gaye", "patti pe daag hai"
- English: "my plant has yellow leaves", "identify disease"

**Action:** `open_camera` (App should open camera for photo)

### 5. General Query (`general_query`)

**Example Queries:**
- Hindi: "खाद कैसे डालें", "सिंचाई कब करें"
- Hinglish: "khad kaise dale", "sichai kab karein"
- English: "how to increase yield", "farming tips"

**Action:** `show_result`

## 📱 Android Integration

### Example: Sending Voice Query from Android (Kotlin)

```kotlin
import retrofit2.http.Body
import retrofit2.http.POST

// Data classes
data class VoiceQueryRequest(
    val query: String,
    val location: String? = null,
    val languageHint: String? = null
)

data class VoiceQueryResponse(
    val intent: String,
    val action: String,
    val response: String,
    val data: Map<String, Any>?,
    val detectedLanguage: String,
    val confidence: Double,
    val followUpSuggestions: List<String>?,
    val timestamp: String
)

// API Interface
interface VoiceApi {
    @POST("/api/v1/voice")
    suspend fun processVoiceQuery(@Body request: VoiceQueryRequest): VoiceQueryResponse
}

// Usage
suspend fun sendVoiceQuery(transcribedText: String) {
    val request = VoiceQueryRequest(
        query = transcribedText,
        location = getUserLocation(),
        languageHint = null  // Auto-detect
    )

    try {
        val response = api.processVoiceQuery(request)

        // Handle based on action
        when (response.action) {
            "show_result" -> displayResult(response.response, response.data)
            "open_camera" -> openCameraForDiseaseDetection()
            "fetch_data" -> fetchAdditionalData(response.intent)
            "ask_clarification" -> askUserForMoreInfo(response.response)
        }
    } catch (e: Exception) {
        showError("Failed to process query: ${e.message}")
    }
}
```

## 🧪 Testing with cURL

### Hindi Query

```bash
curl -X POST "http://localhost:8000/api/v1/voice" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "गेहूं का रेट क्या है",
    "location": "Madhya Pradesh"
  }'
```

### Hinglish Query

```bash
curl -X POST "http://localhost:8000/api/v1/voice" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "gehu ka rate kya hai"
  }'
```

### English Query

```bash
curl -X POST "http://localhost:8000/api/v1/voice" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "what is the weather today?"
  }'
```

## 🔌 Utility Endpoints

### Get Supported Languages

```bash
GET /api/v1/voice/languages
```

### Get Supported Intents

```bash
GET /api/v1/voice/intents
```

### Get Example Queries

```bash
GET /api/v1/voice/examples
```

### Health Check

```bash
GET /api/v1/voice/health
```

### Intent Detection Only (Debug)

```bash
POST /api/v1/voice/intent-only
Content-Type: application/json

{
    "query": "gehu ka rate kya hai"
}
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Android App   │
│  (Voice Input)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   POST /voice   │
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VoiceService   │
│  (Process Query)│
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────────┐
│  Groq   │ │   Fallback  │
│   AI    │ │   (Rules)   │
└────┬────┘ └─────────────┘
     │
     ▼
┌─────────────────┐
│ DetectedIntent  │
│ (JSON Response) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute Action  │
│ (Weather/Price) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ VoiceQueryResp  │
│ (Final Output)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Android App   │
│ (Display/Act)   │
└─────────────────┘
```

## 📂 File Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── voice.py              # Pydantic models for voice assistant
│   │   └── __init__.py
│   ├── services/
│   │   ├── voice_service.py      # Intent detection & action handling
│   │   └── __init__.py
│   ├── routes/
│   │   ├── voice.py              # API endpoints
│   │   └── __init__.py
│   └── agents/
│       └── groq_client.py        # AI client (already exists)
├── main.py                       # Updated with voice router
└── .env                          # API keys
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ | - | Your Groq API key |
| `GROQ_MODEL` | ❌ | `llama-3.3-70b-versatile` | AI model to use |

### Available Groq Models

- `llama-3.3-70b-versatile` (recommended, best quality)
- `llama-3.1-8b-instant` (faster, lower quality)
- `mixtral-8x7b-32768` (balanced)
- `gemma2-9b-it` (efficient)

## 🐛 Error Handling

The voice assistant gracefully handles errors:

1. **AI Unavailable**: Falls back to keyword-based intent detection
2. **Invalid JSON**: Returns a fallback response
3. **Network Issues**: Returns error with user-friendly message

## 🎓 For Hackathons (SIH Tips)

### Demo Script

```
1. Show Hindi voice input: "गेहूं का रेट क्या है"
2. Show AI intent detection result
3. Show response in Hindi
4. Show follow-up suggestions
5. Show it works with Hinglish too
```

### Key Features to Highlight

- ✅ **Multilingual**: Works with Hindi, Hinglish, English
- ✅ **Smart AI**: Understands intent, not just keywords
- ✅ **Farmer-Friendly**: Simple, clear responses
- ✅ **Fast**: Groq provides ultra-fast inference
- ✅ **Fallback**: Works even without AI

### Judging Criteria Alignment

| Criteria | How We Address It |
|----------|-------------------|
| Innovation | AI-powered intent detection for rural India |
| Technical Complexity | Groq AI, FastAPI, Multilingual NLP |
| Practicality | Directly solves farmer's daily problems |
| Scalability | Microservice architecture, async APIs |

## 📞 Support

For issues or questions:
- Check `/docs` endpoint for API documentation
- Check `/voice/health` for service status
- Review logs in the server console

## 📝 License

This is part of the FarmFusion project for Smart India Hackathon.
