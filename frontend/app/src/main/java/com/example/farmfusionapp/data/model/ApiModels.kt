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

data class TreatmentDetail(
    val biological: List<String>? = null,
    val cultural: List<String>? = null,
    val chemical: List<String>? = null,
    val active_ingredients: List<String>? = null,
    val treatment_notes: List<String>? = null
)

data class DiseaseResult(
    @com.google.gson.annotations.SerializedName(value = "disease_name", alternate = ["disease"]) val disease_name: String? = null,
    @com.google.gson.annotations.SerializedName("scientific_name") val scientific_name: String? = null,
    @com.google.gson.annotations.SerializedName("confidence") val confidence: Double? = null,
    @com.google.gson.annotations.SerializedName("confidence_tier") val confidence_tier: String? = null,
    @com.google.gson.annotations.SerializedName("diagnosis_status") val diagnosis_status: String? = null,
    @com.google.gson.annotations.SerializedName("severity") val severity: String? = null,
    @com.google.gson.annotations.SerializedName("description") val description: String? = null,
    @com.google.gson.annotations.SerializedName("symptoms") val symptoms: List<String>? = null,
    @com.google.gson.annotations.SerializedName("treatment_suggestions") val treatment_suggestions: List<String>? = null,
    @com.google.gson.annotations.SerializedName("prevention_tips") val prevention_tips: List<String>? = null,
    @com.google.gson.annotations.SerializedName("treatment") val treatment: TreatmentDetail? = null,
    @com.google.gson.annotations.SerializedName("crop_type") val crop_type: String? = null,
    @com.google.gson.annotations.SerializedName("timestamp") val timestamp: String? = null,
    @com.google.gson.annotations.SerializedName("source") val source: String? = null,
    @com.google.gson.annotations.SerializedName("sources") val sources: List<String>? = null,
    @com.google.gson.annotations.SerializedName("message") val message: String? = null,
    @com.google.gson.annotations.SerializedName("is_plant_image") val is_plant_image: Boolean? = true,
    @com.google.gson.annotations.SerializedName("can_analyze") val can_analyze: Boolean? = true,
    @com.google.gson.annotations.SerializedName("invalid_image_reason") val invalid_image_reason: String? = null,
    @com.google.gson.annotations.SerializedName("ai_analyzed") val ai_analyzed: Boolean? = true,
    @com.google.gson.annotations.SerializedName("store_recommendations") val store_recommendations: List<StoreRecommendationItem>? = null
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
    val temperature_c: Double = 0.0,
    val humidity_percent: Int = 0,
    val weather: String = "",
    val wind_speed_ms: Double = 0.0,
    val rain_chance: Double = 0.0,
    val temperature_max_c: Double? = null,
    val temperature_min_c: Double? = null,
    val precipitation_mm: Double? = null
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
    val detected_dialect: String? = null,
    val confidence: Double,
    val input_language: String? = null,
    val input_dialect: String? = null,
    val response_language: String? = null,
    val response_dialect: String? = null,
    val tts_language: String? = null,
    val tts_dialect: String? = null,
    val tts_provider: String? = null,
    val tts_model: String? = null,
    val native_tts: Boolean? = null,
    val local_tts: Boolean? = null,
    val fallback_used: Boolean? = null,
    val fallback_reason: String? = null,
    val audio_base64: String? = null,
    val audio_format: String? = null,
    val follow_up_suggestions: List<String>?,
    val timestamp: String
)

// ============ IOT ANIMAL DETECTION ============

data class SensorDetailModel(
    val status: String,
    val health: String,
    val sensor_type: String,
    val last_seen: String? = null
)

data class LatestStatusModel(
    val device_id: String,
    val overall_status: String,
    val sensors: Map<String, SensorDetailModel>,
    val detected_sensors: List<String>,
    val offline_sensors: List<String>,
    val last_updated: String? = null
)

data class DetectionEventModel(
    val id: Int,
    val device_id: String,
    val sensor: String,
    val sensor_type: String,
    val status: String,
    val timestamp: String
)

data class HistoryResponseModel(
    val total: Int,
    val limit: Int,
    val offset: Int,
    val events: List<DetectionEventModel>
)

// ============ MANDI PRICE INTELLIGENCE ============

data class MandiProximityItemModel(
    val market_id: String? = null,
    val market: String,
    val district: String,
    val state: String,
    val distance_km: Double? = null,
    val modal_price: Double,
    val min_price: Double,
    val max_price: Double,
    val arrival_date: String,
    val unit: String = "₹/Quintal",
    val source: String,
    val freshness_status: String = "FRESH",
    val practical_score: Double = 0.0,
    val ranking_reason: String = "",
    val is_best_practical: Boolean = false,
    val is_highest_price: Boolean = false,
    val wording_label: String = "उपलब्ध दर्ज भाव"
)

data class BestMandiResponseModel(
    val commodity: String,
    val best_mandi: MandiProximityItemModel? = null,
    val best_practical_mandi: MandiProximityItemModel? = null,
    val highest_price_mandi: MandiProximityItemModel? = null,
    val ranked_mandis: List<MandiProximityItemModel>,
    val total_found: Int,
    val status: String = "SUCCESS",
    val disclaimer: String
)

data class MarketComparisonItemModel(
    val market: String,
    val district: String? = null,
    val state: String? = null,
    val modal_price: Double,
    val min_price: Double,
    val max_price: Double,
    val arrival_date: String,
    val unit: String = "₹/Quintal",
    val source: String
)

data class MandiComparisonDetailModel(
    val higher_market: String,
    val price_difference: Double,
    val percentage_difference: Double,
    val unit: String = "₹/Quintal",
    val summary_hi: String,
    val summary_en: String
)

data class MandiComparisonResponseModel(
    val commodity: String,
    val market_a: MarketComparisonItemModel,
    val market_b: MarketComparisonItemModel,
    val comparison: MandiComparisonDetailModel
)

data class AdvisoryObservedModel(
    val price: Double,
    val date: String,
    val market: String,
    val source: String,
    val unit: String = "₹/Quintal"
)

data class AdvisoryForecastModel(
    val horizon_days: Int,
    val projected_price: Double,
    val expected_change: Double,
    val percentage_change: Double,
    val trend: String,
    val confidence_level: Double,
    val lower_bound_95: Double,
    val upper_bound_95: Double,
    val model_name: String
)

data class AdvisoryDetailModel(
    val signal: String,
    val recommendation_hi: String,
    val recommendation_en: String,
    val reasoning_factors: List<String>
)

data class MandiAdvisoryResponseModel(
    val commodity: String,
    val market: String,
    val observed: AdvisoryObservedModel,
    val forecast: AdvisoryForecastModel,
    val advisory: AdvisoryDetailModel,
    val disclaimer: String
)

data class PriceAlertCreateModel(
    val commodity: String,
    val market: String? = null,
    val target_price: Double? = null,
    val direction: String = "ABOVE",
    val target_percentage_change: Double? = null,
    val user_id: String = "default_user"
)

data class PriceAlertResponseModel(
    val id: Int,
    val user_id: String,
    val commodity: String,
    val market: String? = null,
    val target_price: Double? = null,
    val direction: String,
    val target_percentage_change: Double? = null,
    val base_price: Double,
    val status: String,
    val created_at: String,
    val triggered_at: String? = null,
    val notification_status: String
)


