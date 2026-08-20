package com.example.farmfusionapp.data.repository

import com.example.farmfusionapp.data.dev.DevNoSoilReportMock
import com.example.farmfusionapp.data.model.CropRecommendRequest
import com.example.farmfusionapp.data.model.CropRecommendResponse
import com.example.farmfusionapp.data.model.NoSoilReportRequest
import com.example.farmfusionapp.data.model.NoSoilReportResponse
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.utils.Resource
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import retrofit2.HttpException
import java.io.IOException

/**
 * Repository for Crop Recommendation API calls
 * Follows the Repository pattern - single source of truth for data
 */
class CropRecommendationRepository {

    private val api = RetrofitInstance.farmFusionApi

    /**
     * Get crop recommendations from the backend AI
     *
     * @param location Farm location (e.g., "Nairobi, Kenya" or "Mumbai, India")
     * @param soilType Type of soil (e.g., "loamy", "clay", "sandy", "black", "red")
     * @param rainfallMm Annual rainfall in millimeters
     * @param temperatureC Average temperature in Celsius
     * @param farmSizeAcres Farm size in acres
     * @param preferredLanguage User's language preference (e.g., "hi" for Hindi)
     * @return Flow of Resource (Loading, Success, or Error)
     */
    fun getCropRecommendations(
        location: String,
        soilType: String,
        rainfallMm: Double,
        temperatureC: Double,
        farmSizeAcres: Double,
        budgetUsd: Double? = null,
        latitude: Double? = null,
        longitude: Double? = null,
        preferredLanguage: String = "en"
    ): Flow<Resource<CropRecommendResponse>> = flow {
        emit(Resource.Loading())

        try {
            val request = CropRecommendRequest(
                location = location,
                soil_type = soilType.lowercase(),
                rainfall_mm = rainfallMm,
                temperature_c = temperatureC,
                farm_size_acres = farmSizeAcres,
                budget_usd = budgetUsd,
                preferred_language = preferredLanguage,
                latitude = latitude,
                longitude = longitude
            )

            val response = api.getCropRecommendations(request)

            if (response.isSuccessful) {
                response.body()?.let { result ->
                    if (result.success) {
                        emit(Resource.Success(result))
                    } else {
                        emit(Resource.Error("API returned unsuccessful response"))
                    }
                } ?: emit(Resource.Error("Empty response from server"))
            } else {
                emit(Resource.Error("Error ${response.code()}: ${response.message()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("HTTP Error: ${e.message ?: "Unknown error"}"))
        } catch (e: IOException) {
            emit(Resource.Error("Network Error: Check your internet connection"))
        } catch (e: Exception) {
            emit(Resource.Error("Error: ${e.message ?: "Unknown error"}"))
        }
    }

    /**
     * Get crop recommendations when the farmer has NO soil report.
     *
     * The backend derives soil (SIS India) + weather from latitude/longitude,
     * runs the ML model, and returns the top 3 crops.
     *
     * @param latitude Device latitude
     * @param longitude Device longitude
     * @param state Optional state name (used only by the regional scoring layer)
     * @return Flow of Resource (Loading, Success, or Error)
     */
    fun getNoSoilReportRecommendations(
        latitude: Double,
        longitude: Double,
        state: String?
    ): Flow<Resource<NoSoilReportResponse>> = flow {
        emit(Resource.Loading())

        // ------------------------------------------------------------------
        // DEVELOPMENT-ONLY mock (see DevNoSoilReportMock). Disabled by default,
        // so production always calls the real backend.
        // ------------------------------------------------------------------
        if (DevNoSoilReportMock.ENABLED) {
            delay(DevNoSoilReportMock.SIMULATED_DELAY_MS)
            emit(Resource.Success(DevNoSoilReportMock.sampleResponse))
            return@flow
        }

        try {
            val request = NoSoilReportRequest(
                latitude = latitude,
                longitude = longitude,
                state = state
            )

            val response = api.getNoSoilReportRecommendations(request)

            if (response.isSuccessful) {
                response.body()?.let { result ->
                    if (result.success) {
                        emit(Resource.Success(result))
                    } else {
                        emit(Resource.Error("API returned unsuccessful response"))
                    }
                } ?: emit(Resource.Error("Empty response from server"))
            } else if (response.code() == 503) {
                // SIS India soil API not configured / unavailable on the server.
                emit(
                    Resource.Error(
                        "Soil information is currently unavailable for this location. " +
                            "Please try again later or provide a soil report."
                    )
                )
            } else {
                emit(Resource.Error("Error ${response.code()}: ${response.message()}"))
            }
        } catch (e: HttpException) {
            emit(Resource.Error("HTTP Error: ${e.message ?: "Unknown error"}"))
        } catch (e: IOException) {
            emit(Resource.Error("Network Error: Check your internet connection"))
        } catch (e: Exception) {
            emit(Resource.Error("Error: ${e.message ?: "Unknown error"}"))
        }
    }

    /**
     * Test if backend connection is working
     */
    suspend fun testConnection(): Boolean {
        return try {
            val response = api.checkHealth()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }
}
