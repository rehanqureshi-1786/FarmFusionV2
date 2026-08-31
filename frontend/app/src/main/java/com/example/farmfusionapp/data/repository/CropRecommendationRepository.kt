package com.example.farmfusionapp.data.repository

import com.example.farmfusionapp.data.model.CropRecommendRequest
import com.example.farmfusionapp.data.model.CropRecommendResponse
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.utils.Resource
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
                preferred_language = preferredLanguage
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
