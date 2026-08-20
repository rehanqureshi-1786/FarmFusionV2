package com.example.farmfusionapp.network

import com.example.farmfusionapp.data.model.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

/**
 * FarmFusion Backend API Interface
 * These endpoints connect to your Python FastAPI backend
 */
interface FarmFusionApi {

    // ============ CROP RECOMMENDATIONS ============

    @POST("api/v1/crop/recommend")
    suspend fun getCropRecommendations(
        @Body request: CropRecommendRequest
    ): Response<CropRecommendResponse>

    // ============ CROP RECOMMENDATION - NO SOIL REPORT ============

    @POST("api/v1/crop-recommendation/no-soil-report")
    suspend fun getNoSoilReportRecommendations(
        @Body request: NoSoilReportRequest
    ): Response<NoSoilReportResponse>

    @GET("api/v1/crop/history")
    suspend fun getCropRecommendationHistory(
        @Query("firebase_token") token: String,
        @Query("limit") limit: Int = 10
    ): Response<CropHistoryResponse>

    // ============ DISEASE DETECTION ============

    /**
     * Updated to match latest backend logic:
     * image is Multipart, crop_type and firebase_token are Query parameters
     */
    @Multipart
    @POST("api/v1/disease/detect")
    suspend fun detectDisease(
        @Part image: MultipartBody.Part,
        @Query("crop_type") cropType: String?,
        @Query("firebase_token") token: String? = null,
        @Query("response_language") language: String? = null
    ): Response<DiseaseDetectResponse>

    @GET("api/v1/disease/history")
    suspend fun getDiseaseHistory(
        @Query("firebase_token") token: String,
        @Query("limit") limit: Int = 10
    ): Response<DiseaseHistoryResponse>

    @GET("api/v1/disease/info/{disease_name}")
    suspend fun getDiseaseInfo(
        @Path("disease_name") diseaseName: String
    ): Response<DiseaseInfoResponse>

    // ============ MARKET PRICES ============

    @GET("api/v1/market/prices")
    suspend fun getMarketPrices(
        @Query("state") state: String? = "India",
        @Query("district") district: String? = null,
        @Query("crop") crop: String? = null
    ): Response<MarketPricesResponse>

    @POST("api/v1/market/predict")
    suspend fun predictPrices(
        @Body request: MarketPredictionRequest
    ): Response<MarketPredictionResponse>

    @GET("api/v1/market/trends")
    suspend fun getPriceTrends(
        @Query("crop") crop: String,
        @Query("region") region: String = "India",
        @Query("months") months: Int = 6
    ): Response<MarketTrendsResponse>

    // ============ WEATHER ============

    @GET("api/v1/weather/current")
    suspend fun getCurrentWeather(
        @Query("lat") latitude: Double,
        @Query("lon") longitude: Double
    ): Response<WeatherResponse>

    @GET("api/v1/weather/forecast")
    suspend fun getWeatherForecast(
        @Query("lat") latitude: Double,
        @Query("lon") longitude: Double,
        @Query("days") days: Int = 5
    ): Response<WeatherForecastResponse>

    @GET("api/v1/weather/farming")
    suspend fun getFarmingWeather(
        @Query("lat") latitude: Double,
        @Query("lon") longitude: Double,
        @Query("days") days: Int = 7
    ): Response<FarmingWeatherResponse>

    // ============ VOICE ASSISTANT ============

    @POST("api/v1/voice")
    suspend fun processVoice(
        @Body request: VoiceQueryRequest
    ): Response<VoiceQueryResponse>

    // ============ AUTHENTICATION ============

    @POST("api/v1/auth/verify")
    suspend fun verifyAuthToken(
        @Query("firebase_token") token: String
    ): Response<AuthResponse>

    @GET("api/v1/auth/user/{uid}")
    suspend fun getUserInfo(
        @Path("uid") uid: String
    ): Response<UserInfoResponse>

    // ============ USER & FARMS ============

    @GET("api/v1/users/profile")
    suspend fun getUserProfile(
        @Query("firebase_token") token: String
    ): Response<UserProfileResponse>

    @PUT("api/v1/users/profile")
    suspend fun updateLanguage(
        @Query("firebase_token") token: String,
        @Query("language") language: String
    ): Response<UserProfileResponse>

    @GET("api/v1/users/farms")
    suspend fun getUserFarms(
        @Query("firebase_token") token: String
    ): Response<UserFarmsResponse>

    @POST("api/v1/users/farms")
    suspend fun createFarm(
        @Query("firebase_token") token: String,
        @Query("name") name: String,
        @Query("location") location: String,
        @Query("latitude") latitude: Double,
        @Query("longitude") longitude: Double,
        @Query("soil_type") soilType: String,
        @Query("farm_size_acres") farmSize: Double,
        @Query("annual_rainfall_mm") rainfall: Double = 0.0,
        @Query("avg_temperature_c") temperature: Double = 25.0
    ): Response<CreateFarmResponse>

    @GET("api/v1/users/farms/{farm_id}")
    suspend fun getFarmDetails(
        @Path("farm_id") farmId: Int,
        @Query("firebase_token") token: String
    ): Response<FarmDetailsResponse>

    // ============ AGRI STORE ============

    @GET("api/v1/store/recommendations")
    suspend fun getStoreRecommendations(
        @Query("firebase_token") token: String? = null,
        @Query("category") category: String? = null
    ): Response<StoreRecommendationsResponse>

    // ============ HEALTH & TEST ============

    @GET("api/v1/crop/test")
    suspend fun testConnection(): Response<Map<String, Any>>

    @GET("health")
    suspend fun checkHealth(): Response<Map<String, Any>>
}
