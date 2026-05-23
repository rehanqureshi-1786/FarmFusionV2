# 🚀 FarmFusion Voice Assistant - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd backend
pip install groq
```

### Step 2: Add API Key

Create/edit `.env` file in `backend/` folder:

```env
GROQ_API_KEY=gsk_your_api_key_here
```

Get your free key at: https://console.groq.com

### Step 3: Run Server

```bash
python main.py
```

Server starts at: http://localhost:8000

### Step 4: Test It

Open browser: http://localhost:8000/docs

Click on `POST /api/v1/voice` → Try it out

**Test Query:**
```json
{
    "query": "गेहूं का रेट क्या है"
}
```

## 📱 API Usage (Android)

### Kotlin Example

```kotlin
// Data classes
data class VoiceRequest(
    val query: String,
    val location: String? = null
)

data class VoiceResponse(
    val intent: String,
    val action: String,
    val response: String,  // Response in farmer's language!
    val data: Map<String, Any>?
)

// API call
@POST("/api/v1/voice")
suspend fun processVoice(@Body request: VoiceRequest): VoiceResponse

// Usage
val response = api.processVoice(VoiceRequest(
    query = "gehu ka rate kya hai"
))

// Handle response
when (response.action) {
    "show_result" -> textView.text = response.response
    "open_camera" -> openCamera()
}
```

## 🧪 Test with cURL

### Hindi Query
```bash
curl -X POST "http://localhost:8000/api/v1/voice" \
  -H "Content-Type: application/json" \
  -d '{"query": "गेहूं का रेट क्या है"}'
```

### Hinglish Query
```bash
curl -X POST "http://localhost:8000/api/v1/voice" \
  -H "Content-Type: application/json" \
  -d '{"query": "gehu ka rate kya hai"}'
```

### English Query
```bash
curl -X POST "http://localhost:8000/api/v1/voice" \
  -H "Content-Type: application/json" \
  -d '{"query": "what is wheat price?"}'
```

## 🎯 Example Queries

| Intent | Hindi | Hinglish | English |
|--------|-------|----------|---------|
| Weather | आज मौसम कैसा है | mausam kaisa hai | what's the weather |
| Price | गेहूं का रेट | gehu ka rate | wheat price |
| Crop | क्या बोएं | konsi fasal | which crop |
| Disease | पत्ते पीले हो रहे | paudhe ki bimari | plant disease |

## 🔧 Troubleshooting

### "Groq API key not configured"
- Add `GROQ_API_KEY` to your `.env` file
- Get key from https://console.groq.com

### "Cannot connect to server"
- Make sure server is running: `python main.py`
- Check port 8000 is not in use

### "Module not found: groq"
- Run: `pip install groq`

## 📊 Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/voice` | Main voice/text query endpoint |
| `GET /api/v1/voice/health` | Check if voice assistant is working |
| `GET /api/v1/voice/languages` | List supported languages |
| `GET /api/v1/voice/intents` | List supported intents |
| `GET /api/v1/voice/examples` | Get example queries |

## ✅ Success Checklist

- [ ] Server starts without errors
- [ ] POST /api/v1/voice returns JSON response
- [ ] Hindi queries work
- [ ] Hinglish queries work
- [ ] English queries work
- [ ] Response is in the same language as input
- [ ] Intent is correctly detected

## 🎤 For Hackathon Demo

**Quick Demo Script:**

1. Show: `http://localhost:8000/docs`
2. Click: POST `/api/v1/voice`
3. Enter: `{"query": "गेहूं का रेट क्या है"}`
4. Execute → Show AI response in Hindi
5. Try: `{"query": "mausam kaisa hai"}`
6. Show: Response in Hinglish

**Key Points:**
- ✅ Understands farmer's natural language
- ✅ Responds in the same language
- ✅ No manual language selection needed
- ✅ Works with voice or text input

## 📚 Full Documentation

See `VOICE_ASSISTANT.md` for complete documentation.

## 🆘 Need Help?

- Check server logs in terminal
- Test with `/api/v1/voice/health` endpoint
- Review `VOICE_ASSISTANT.md`
