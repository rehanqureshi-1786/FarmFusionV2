package com.example.farmfusionapp.data.repository

import com.example.farmfusionapp.data.model.CropRecommendRequest
import com.example.farmfusionapp.data.model.CropRecommendResponse
import com.example.farmfusionapp.data.model.NoSoilReportRequest
import com.example.farmfusionapp.data.model.NoSoilReportResponse
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.utils.Resource
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
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
        preferredLanguage: String = "en",
        nitrogen: Double? = null,
        phosphorus: Double? = null,
        potassium: Double? = null,
        ph: Double? = null
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
                longitude = longitude,
                nitrogen = nitrogen,
                phosphorus = phosphorus,
                potassium = potassium,
                ph = ph
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
     * Get crop recommendations by uploading a Soil Health Card (Image or PDF).
     */
    fun getCropRecommendationsFromDocument(
        documentBytes: ByteArray,
        filename: String,
        mimeType: String,
        farmSizeAcres: Double,
        location: String?,
        latitude: Double?,
        longitude: Double?,
        soilType: String?,
        rainfallMm: Double?,
        temperatureC: Double?,
        preferredLanguage: String
    ): Flow<Resource<CropRecommendResponse>> = flow {
        emit(Resource.Loading())

        try {
            val mediaType = mimeType.toMediaTypeOrNull() ?: "application/octet-stream".toMediaTypeOrNull()
            val fileRequestBody = documentBytes.toRequestBody(mediaType, 0, documentBytes.size)
            val filePart = MultipartBody.Part.createFormData("document", filename, fileRequestBody)

            val textMediaType = "text/plain".toMediaTypeOrNull()
            val farmSizeBody = farmSizeAcres.toString().toRequestBody(textMediaType)
            val locationBody = location?.toRequestBody(textMediaType)
            val latBody = latitude?.toString()?.toRequestBody(textMediaType)
            val lonBody = longitude?.toString()?.toRequestBody(textMediaType)
            val soilTypeBody = soilType?.toRequestBody(textMediaType)
            val rainBody = rainfallMm?.toString()?.toRequestBody(textMediaType)
            val tempBody = temperatureC?.toString()?.toRequestBody(textMediaType)
            val langBody = preferredLanguage.toRequestBody(textMediaType)

            val response = api.recommendFromDocument(
                document = filePart,
                farmSizeAcres = farmSizeBody,
                location = locationBody,
                latitude = latBody,
                longitude = lonBody,
                soilType = soilTypeBody,
                rainfallMm = rainBody,
                temperatureC = tempBody,
                preferredLanguage = langBody
            )

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
     * The backend derives soil (SoilGrids) + weather (Open-Meteo) from latitude/longitude.
     * When N/P/K is unavailable, the backend returns real data provenance and recommendation_available=false.
     *
     * @param latitude Device latitude
     * @param longitude Device longitude
     * @param state Optional state name
     * @param soilType Optional farmer-selected soil texture (e.g. Sandy Soil)
     * @param locationName Optional full reverse-geocoded place name
     * @return Flow of Resource (Loading, Success, or Error)
     */
    fun getNoSoilReportRecommendations(
        latitude: Double,
        longitude: Double,
        state: String?,
        soilType: String? = null,
        locationName: String? = null
    ): Flow<Resource<NoSoilReportResponse>> = flow {
        emit(Resource.Loading())

        try {
            val request = NoSoilReportRequest(
                latitude = latitude,
                longitude = longitude,
                state = state,
                soil_type = soilType,
                location_name = locationName
            )

            val response = api.getNoSoilReportRecommendations(request)

            if (response.isSuccessful) {
                response.body()?.let { result ->
                    if (result.success) {
                        emit(Resource.Success(result))
                    } else {
                        emit(Resource.Error(result.message ?: "API returned unsuccessful response"))
                    }
                } ?: emit(Resource.Error("Empty response from server"))
            } else if (response.code() == 503) {
                emit(
                    Resource.Error(
                        "Soil or weather data service is currently unavailable for this location. " +
                            "Please try again or provide a soil report."
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
