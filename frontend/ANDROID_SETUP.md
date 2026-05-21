# FarmFusion Android Setup Guide

Your Android app is now connected to the FastAPI backend! 🎉

## 📱 Current State

Your app now has:
- ✅ Retrofit configured for backend API calls
- ✅ CropRecommendationViewModel for data management
- ✅ Repository pattern for clean architecture
- ✅ Loading states and error handling
- ✅ Real AI recommendations from backend

## 🚀 How to Run

### Step 1: Start the Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

You should see: `📚 API Documentation: http://localhost:8000/docs`

### Step 2: Open Android Studio

1. Open Android Studio
2. Select "Open an Existing Project"
3. Navigate to: `FarmFusion/frontend`
4. Wait for Gradle sync to complete

### Step 3: Configure Backend URL

In `app/src/main/java/com/example/farmfusionapp/utils/Constants.kt`:

```kotlin
// For Android Emulator (default)
const val FARMFUSION_BASE_URL = "http://10.0.2.2:8000/"

// For Real Device (same WiFi) - find your computer's IP:
// Windows: ipconfig | findstr IPv4
// Mac/Linux: ifconfig | grep inet
// const val FARMFUSION_BASE_URL = "http://192.168.1.XXX:8000/"
```

### Step 4: Run the App

1. Select your device/emulator
2. Click Run (▶️)
3. Navigate to Crop Recommendation
4. Select soil type → "No Report" → Wait for AI recommendations!

## 📁 New Files Added

### Network Layer
- `network/FarmFusionApi.kt` - API interface with backend endpoints
- Updated `network/RetrofitInstance.kt` - Added backend URL

### Data Layer
- `data/model/CropRecommendationModels.kt` - Request/response data classes
- `data/repository/CropRecommendationRepository.kt` - API calls with error handling

### UI Layer
- Updated `viewmodel/CropRecommendationViewModel.kt` - Complete implementation
- Updated `ui/screens/CropRecommendationScreen.kt` - Connected to backend

### Utils
- Updated `utils/Constants.kt` - Backend URL configuration

## 🔗 API Flow

```
User selects Soil Type → "No Report" → Auto Analysis screen
                                    ↓
                            ViewModel.fetchRecommendations()
                                    ↓
                            Repository calls Retrofit API
                                    ↓
                            POST /crop/recommend
                                    ↓
                            FastAPI processes with AI Agent
                                    ↓
                            Returns recommendations
                                    ↓
                            Screen shows results!
```

## 🧪 Testing the Connection

### Test 1: Backend is Running

Open browser: `http://localhost:8000/docs`

You should see Swagger UI with your API documentation.

### Test 2: From Android Emulator

In Android Studio Terminal:
```bash
adb shell
ping 10.0.2.2
```

This should ping your computer's localhost.

### Test 3: API Test in App

Add this to a button click or on app start:

```kotlin
val viewModel: CropRecommendationViewModel = viewModel()
viewModel.testConnection()
```

## 🐛 Common Issues

### "Connection refused"
- Backend not running
- Wrong BASE_URL
- Firewall blocking port 8000

### "HTTP 404"
- Wrong endpoint URL
- Check if `/crop/recommend` exists in backend

### "JSON parsing error"
- Mismatched data models
- Backend response doesn't match Kotlin classes

### "CORS error"
- Add your Android IP to backend CORS settings
- Edit `backend/app/core/config.py`

## 📊 What Data Flows

### Request (Android → Backend)
```json
{
    "location": "Mumbai, India",
    "soil_type": "loamy",
    "rainfall_mm": 1200.0,
    "temperature_c": 30.0,
    "farm_size_acres": 2.5
}
```

### Response (Backend → Android)
```json
{
    "success": true,
    "recommendations": [
        {
            "crop_name": "Maize",
            "confidence_score": 0.92,
            "expected_yield_tons": 11.25,
            "market_demand": "high",
            "estimated_profit_usd": 750.0,
            "growing_duration_months": 4,
            "water_requirement": "medium"
        }
    ],
    "ai_insights": "Great choice for loamy soil!...",
    "timestamp": "2024-03-26T14:30:00"
}
```

## 🎯 Next Steps

1. **Add Location Service** - Get user's real location instead of hardcoded "Mumbai"
2. **Add Weather API** - Get real rainfall/temperature data
3. **Disease Detection** - Connect `CropDiseaseScreen.kt` to backend `/disease/detect`
4. **Market Prices** - Connect `MandiPricesScreen.kt` to backend `/market/predict`
5. **Firebase Auth** - Add user authentication
6. **PostgreSQL Database** - Store user history

## 📚 Key Classes Reference

| Class | Purpose |
|-------|---------|
| `FarmFusionApi` | Defines API endpoints |
| `CropRecommendationRepository` | Makes API calls |
| `CropRecommendationViewModel` | Manages UI state |
| `CropRecommendRequest` | Data sent to backend |
| `CropRecommendResponse` | Data received from backend |
| `CropRecommendationItem` | Single crop recommendation |

## 💡 Pro Tips

1. **Use Logcat** - Filter by "FarmFusion" to see API calls
2. **Check Network Inspector** - Android Studio has built-in network profiler
3. **Use Breakpoints** - Debug step-by-step in ViewModel
4. **Mock Data** - For testing, create fake responses

## 🆘 Need Help?

1. Check if backend is running: `curl http://localhost:8000/health`
2. Test API manually: Use Postman or browser at `/docs`
3. Check Android logs: Logcat in Android Studio
4. Verify URL: Make sure BASE_URL matches your setup

Happy coding! 🌾🚀
