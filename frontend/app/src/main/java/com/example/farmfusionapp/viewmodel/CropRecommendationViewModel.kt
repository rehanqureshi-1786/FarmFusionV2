package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.CropRecommendationItem
import com.example.farmfusionapp.data.model.NoSoilReportResponse
import com.example.farmfusionapp.data.repository.CropRecommendationRepository
import com.example.farmfusionapp.utils.Resource
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch

/**
 * ViewModel for Crop Recommendation feature
 * Manages UI state and connects to Repository
 */
class CropRecommendationViewModel : ViewModel() {

    private val repository = CropRecommendationRepository()

    // State for crop recommendations
    private val _recommendations = mutableStateOf<List<CropRecommendationItem>>(emptyList())
    val recommendations: State<List<CropRecommendationItem>> = _recommendations

    // State for AI insights
    private val _aiInsights = mutableStateOf("")
    val aiInsights: State<String> = _aiInsights

    // Loading state
    private val _isLoading = mutableStateOf(false)
    val isLoading: State<Boolean> = _isLoading

    // Error state
    private val _error = mutableStateOf<String?>(null)
    val error: State<String?> = _error

    // Success state
    private val _isSuccess = mutableStateOf(false)
    val isSuccess: State<Boolean> = _isSuccess

    // ============ NO SOIL REPORT FLOW STATE ============

    private val _noSoilReportResult = mutableStateOf<NoSoilReportResponse?>(null)
    val noSoilReportResult: State<NoSoilReportResponse?> = _noSoilReportResult

    private val _isNoSoilReportLoading = mutableStateOf(false)
    val isNoSoilReportLoading: State<Boolean> = _isNoSoilReportLoading

    private val _noSoilReportError = mutableStateOf<String?>(null)
    val noSoilReportError: State<String?> = _noSoilReportError

    private val _isNoSoilReportSuccess = mutableStateOf(false)
    val isNoSoilReportSuccess: State<Boolean> = _isNoSoilReportSuccess

    /**
     * Fetch crop recommendations for the "I don't have a soil report" flow.
     *
     * The backend derives soil + weather from the coordinates and returns the
     * top 3 crops after running the ML model + regional validation.
     *
     * @param latitude  Device latitude
     * @param longitude Device longitude
     * @param state     Optional state name (regional scoring hint)
     */
    fun fetchNoSoilReportRecommendations(
        latitude: Double,
        longitude: Double,
        state: String?
    ) {
        repository.getNoSoilReportRecommendations(latitude, longitude, state)
            .onEach { result ->
                when (result) {
                    is Resource.Loading -> {
                        _isNoSoilReportLoading.value = true
                        _noSoilReportError.value = null
                        _isNoSoilReportSuccess.value = false
                    }
                    is Resource.Success -> {
                        _isNoSoilReportLoading.value = false
                        _noSoilReportResult.value = result.data
                        _isNoSoilReportSuccess.value = true
                    }
                    is Resource.Error -> {
                        _isNoSoilReportLoading.value = false
                        _noSoilReportError.value = result.message
                        _isNoSoilReportSuccess.value = false
                    }
                }
            }.launchIn(viewModelScope)
    }

    /**
     * Clear only the No-Soil-Report flow state.
     */
    fun resetNoSoilReportState() {
        _noSoilReportResult.value = null
        _isNoSoilReportLoading.value = false
        _noSoilReportError.value = null
        _isNoSoilReportSuccess.value = false
    }

    /**
     * Fetch crop recommendations from AI backend
     *
     * @param location User's location (city, country)
     * @param soilType Selected soil type (Black, Red, Alluvial, Sandy)
     * @param rainfallMm Annual rainfall in mm
     * @param temperatureC Average temperature in Celsius
     * @param farmSizeAcres Farm size in acres
     */
    fun fetchRecommendations(
        location: String = "Mumbai, India",
        soilType: String,
        rainfallMm: Double = -1.0,
        temperatureC: Double = 25.0,
        farmSizeAcres: Double = 1.0,
        budgetUsd: Double? = null,
        latitude: Double? = null,
        longitude: Double? = null,
        preferredLanguage: String = "en"
    ) {
        // Map frontend soil types to backend expected values
        val backendSoilType = when (soilType.lowercase()) {
            "black soil" -> "loamy"
            "red soil" -> "clay"
            "alluvial soil" -> "silty"
            "sandy soil" -> "sandy"
            else -> soilType.lowercase()
        }

        repository.getCropRecommendations(
            location = location,
            soilType = backendSoilType,
            rainfallMm = rainfallMm,
            temperatureC = temperatureC,
            farmSizeAcres = farmSizeAcres,
            budgetUsd = budgetUsd,
            latitude = latitude,
            longitude = longitude,
            preferredLanguage = preferredLanguage
        ).onEach { result ->
            when (result) {
                is Resource.Loading -> {
                    _isLoading.value = true
                    _error.value = null
                    _isSuccess.value = false
                }
                is Resource.Success -> {
                    _isLoading.value = false
                    result.data?.let { response ->
                        _recommendations.value = response.recommendations
                        _aiInsights.value = response.ai_insights
                        _isSuccess.value = true
                    }
                }
                is Resource.Error -> {
                    _isLoading.value = false
                    _error.value = result.message
                    _isSuccess.value = false
                }
            }
        }.launchIn(viewModelScope)
    }

    /**
     * Clear error state
     */
    fun clearError() {
        _error.value = null
    }

    /**
     * Reset all state
     */
    fun resetState() {
        _recommendations.value = emptyList()
        _aiInsights.value = ""
        _isLoading.value = false
        _error.value = null
        _isSuccess.value = false
    }

    /**
     * Test backend connection
     */
    fun testConnection() {
        viewModelScope.launch {
            val isConnected = repository.testConnection()
            if (!isConnected) {
                _error.value = "Cannot connect to backend. Make sure server is running."
            } else {
                _error.value = null
            }
        }
    }
}
