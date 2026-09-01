package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.CropRecommendationItem
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
        rainfallMm: Double = 1000.0,
        temperatureC: Double = 28.0,
        farmSizeAcres: Double = 2.0,
        budgetUsd: Double? = null,
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
