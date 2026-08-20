package com.example.farmfusionapp.data.model

// ============ AUTH RESPONSES ============

data class AuthResponse(
    val success: Boolean,
    val message: String,
    val user: UserData?
)

data class UserData(
    val id: Int,
    val firebase_uid: String,
    val phone_number: String?,
    val name: String?,
    val email: String?,
    val language_preference: String,
    val created_at: String?
)

data class UserInfoResponse(
    val success: Boolean,
    val user: FirebaseUserData?
)

data class FirebaseUserData(
    val uid: String,
    val phone_number: String?,
    val email: String?,
    val name: String?,
    val photo_url: String?,
    val disabled: Boolean
)

data class UserProfileResponse(
    val success: Boolean,
    val profile: UserProfile?
)

data class UserProfile(
    val id: Int,
    val firebase_uid: String,
    val phone_number: String?,
    val name: String?,
    val email: String?,
    val language_preference: String,
    val created_at: String?,
    val farm_count: Int
)

// ============ FARM RESPONSES ============

data class UserFarmsResponse(
    val success: Boolean,
    val farms: List<FarmData>
)

data class FarmData(
    val id: Int,
    val name: String,
    val location: String,
    val latitude: Double,
    val longitude: Double,
    val soil_type: String,
    val farm_size_acres: Double,
    val annual_rainfall_mm: Double,
    val avg_temperature_c: Double,
    val created_at: String?
)

data class CreateFarmResponse(
    val success: Boolean,
    val message: String,
    val farm: FarmData?
)

data class FarmDetailsResponse(
    val success: Boolean,
    val farm: FarmData?
)

// ============ CROP HISTORY ============

data class CropHistoryResponse(
    val success: Boolean,
    val data: List<CropHistoryItem>
)

data class CropHistoryItem(
    val id: Int,
    val location: String,
    val soil_type: String,
    val recommendations: List<Map<String, Any>>,
    val insights: String?,
    val created_at: String?
)

// ============ DISEASE RESPONSES ============

data class DiseaseDetectResponse(
    val success: Boolean,
    val data: DiseaseResult?
)

data class DiseaseResult(
    @com.google.gson.annotations.SerializedName("disease") val disease_name: String?,
    @com.google.gson.annotations.SerializedName("confidence") val confidence: Double?,
    @com.google.gson.annotations.SerializedName("severity") val severity: String?,
    @com.google.gson.annotations.SerializedName("description") val description: String?,
    @com.google.gson.annotations.SerializedName("treatment") val treatment_suggestions: List<String>?,
    @com.google.gson.annotations.SerializedName("prevention") val prevention_tips: List<String>?,
    @com.google.gson.annotations.SerializedName("crop_type") val crop_type: String?,
    @com.google.gson.annotations.SerializedName("timestamp") val timestamp: String?,
    @com.google.gson.annotations.SerializedName("source") val source: String?,
    @com.google.gson.annotations.SerializedName("is_plant_image") val is_plant_image: Boolean?,
    @com.google.gson.annotations.SerializedName("can_analyze") val can_analyze: Boolean?,
    @com.google.gson.annotations.SerializedName("invalid_image_reason") val invalid_image_reason: String?,
    @com.google.gson.annotations.SerializedName("ai_analyzed") val ai_analyzed: Boolean?,
    @com.google.gson.annotations.SerializedName("store_recommendations") val store_recommendations: List<StoreRecommendationItem>?
)

data class DiseaseHistoryResponse(
    val success: Boolean,
    val data: List<DiseaseHistoryItem>
)

data class DiseaseHistoryItem(
    val id: Int? = null,
    val crop_type: String? = null,
    val disease_name: String? = null,
    val confidence: Double? = null,
    val severity: String? = null,
    val created_at: String? = null
)

data class DiseaseInfoResponse(
    val success: Boolean,
    val data: DiseaseInfo?
)

data class DiseaseInfo(
    val found: Boolean,
    val name: String?,
    val description: String?,
    val treatment: List<String>?,
    val prevention: List<String>?,
    val severity: String?,
    val message: String?
)

// ============ MARKET RESPONSES ============

data class MarketPricesResponse(
    val data: List<MarketPrice>,
    val count: Int,
    val region: String
)

data class MarketPrice(
    val state: String,
    val district: String,
    val market: String,
    val commodity: String,
    val variety: String,
    val grade: String,
    val arrival_date: String,
    val min_price: Double,
    val max_price: Double,
    val modal_price: Double,
    val source: String
)

data class MarketPredictionRequest(
    val commodity: String,
    val state: String,
    val district: String? = null,
    val current_price: Double? = null,
    val prediction_months: Int = 3
)

data class MarketPredictionResponse(
    val commodity: String?,
    val region: String?,
    val current_price: Double?,
    val predictions: List<PricePrediction>?,
    val best_time_to_sell: String?,
    val ai_analysis: String?,
    val source: String?
)

data class PricePrediction(
    val month: String,
    val predicted_price: Double,
    val trend: String,
    val confidence: Double
)

data class MarketTrendsResponse(
    val success: Boolean = true,
    val data: MarketTrends?
)

data class MarketTrends(
    val crop_name: String,
    val region: String,
    val source: String?,
    val trend_data: List<TrendDataPoint>
)

data class TrendDataPoint(
    val date: String,
    val predicted_price: Double,
    val trend: String
)

// ============ AGRI STORE (RECOMMENDATIONS) ============

data class StoreRecommendationsResponse(
    val success: Boolean,
    val source: String,
    val items: List<StoreRecommendationItem>
)

data class StoreRecommendationItem(
    val title: String = "",
    val subtitle: String = "",
    val category: String = "",
    val image_url: String? = null,
    val shop_url: String = ""
)

// ============ WEATHER RESPONSES ============

data class WeatherResponse(
    val success: Boolean,
    val data: WeatherData?
)

data class WeatherData(
    val location: String,
    val temperature_c: Double,
    val feels_like_c: Double,
    val humidity_percent: Int,
    val pressure_hpa: Int,
    val weather: String,
    val wind_speed_ms: Double,
    val visibility_m: Int,
    val cloudiness_percent: Int,
    val sunrise: String?,
    val sunset: String?,
    val farming_advice: String,
    val source: String?
)

data class WeatherForecastResponse(
    val success: Boolean,
    val data: ForecastData?
)

data class ForecastData(
    val location: String,
    val forecast: List<DailyForecast>,
    val farming_advice: String,
    val source: String?
)

data class DailyForecast(
    val date: String,
    val temperature_c: Double,
    val humidity_percent: Int,
    val weather: String,
    val wind_speed_ms: Double,
    val rain_chance: Double
)

data class FarmingWeatherResponse(
    val success: Boolean,
    val data: FarmingWeatherData?
)

data class FarmingWeatherData(
    val current: WeatherData?,
    val forecast: ForecastData?,
    val farming_summary: String
)

// ============ DASHBOARD ALERTS ============

data class UrgentAlertResponse(
    val success: Boolean,
    val title: String,
    val message: String,
    val severity: String,
    val source: String? = null,
    val updated_at: String? = null
)

// ============ VOICE ASSISTANT ============

data class VoiceQueryRequest(
    val query: String,
    val location: String? = null,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val language_hint: String? = null
)

data class VoiceQueryResponse(
    val intent: String,
    val action: String,
    val response: String,
    val data: Map<String, Any>?,
    val detected_language: String,
    val confidence: Double,
    val follow_up_suggestions: List<String>?,
    val timestamp: String
)
