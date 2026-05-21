package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.*
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.launch

/**
 * ViewModel for Market Prices feature
 * Connects to backend /market endpoints
 */
class MarketViewModel : ViewModel() {

    private val api = RetrofitInstance.api

    // State for market prices
    private val _pricesState = mutableStateOf<MarketPricesState>(MarketPricesState.Idle)
    val pricesState: State<MarketPricesState> = _pricesState

    // State for predictions
    private val _predictionState = mutableStateOf<MarketPredictionState>(MarketPredictionState.Idle)
    val predictionState: State<MarketPredictionState> = _predictionState

    // State for trends
    private val _trendsState = mutableStateOf<MarketTrendsState>(MarketTrendsState.Idle)
    val trendsState: State<MarketTrendsState> = _trendsState

    // State for all mandis
    private val _mandiListState = mutableStateOf<MandiListState>(MandiListState.Idle)
    val mandiListState: State<MandiListState> = _mandiListState

    /**
     * Get current market prices
     * GET /market/prices
     */
    fun getMarketPrices(state: String? = null, district: String? = null, crop: String? = null) {
        viewModelScope.launch {
            _pricesState.value = MarketPricesState.Loading

            try {
                val response = api.getMarketPrices(state, district, crop)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _pricesState.value = MarketPricesState.Success(it)
                    } ?: run {
                        _pricesState.value = MarketPricesState.Success(
                            MarketPricesResponse(emptyList(), 0, state ?: "India")
                        )
                    }
                } else {
                    _pricesState.value = MarketPricesState.Error("Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _pricesState.value = MarketPricesState.Error(e.message ?: "Unknown error")
            }
        }
    }

    /**
     * Get list of all available mandis
     * GET /market/mandis
     * Note: For hackathon, returns mock data
     */
    fun getMandiList() {
        viewModelScope.launch {
            _mandiListState.value = MandiListState.Loading
            try {
                // For hackathon prototype - using static mock data
                // In production, this would call api.getMandis()
                val mockMandis = listOf(
                    mapOf("name" to "Azadpur Mandi", "location" to "Delhi"),
                    mapOf("name" to "Vashi Mandi", "location" to "Mumbai"),
                    mapOf("name" to "Koyambedu", "location" to "Chennai"),
                    mapOf("name" to "Begum Bazar", "location" to "Hyderabad")
                )
                _mandiListState.value = MandiListState.Success(mockMandis)
            } catch (e: Exception) {
                _mandiListState.value = MandiListState.Error(e.message ?: "Unknown error")
            }
        }
    }

    /**
     * Predict future prices using AI
     * POST /market/predict
     */
    fun predictPrices(
        commodity: String,
        state: String? = null,
        district: String? = null,
        currentPrice: Double = 0.0,
        months: Int = 3
    ) {
        viewModelScope.launch {
            _predictionState.value = MarketPredictionState.Loading

            try {
                val response = api.predictPrices(
                    MarketPredictionRequest(
                        commodity = commodity,
                        state = state ?: "India",
                        district = district,
                        current_price = currentPrice,
                        prediction_months = months
                    )
                )

                if (response.isSuccessful) {
                    response.body()?.let {
                        _predictionState.value = MarketPredictionState.Success(it)
                    } ?: run {
                        _predictionState.value = MarketPredictionState.Error("Empty response")
                    }
                } else {
                    _predictionState.value = MarketPredictionState.Error(
                        "Error: ${response.code()}"
                    )
                }
            } catch (e: Exception) {
                _predictionState.value = MarketPredictionState.Error(
                    e.message ?: "Unknown error"
                )
            }
        }
    }

    /**
     * Get price trends
     * GET /market/trends
     */
    fun getPriceTrends(crop: String, region: String = "India", months: Int = 6) {
        viewModelScope.launch {
            _trendsState.value = MarketTrendsState.Loading

            try {
                val response = api.getPriceTrends(crop, region, months)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _trendsState.value = MarketTrendsState.Success(it)
                    } ?: run {
                        _trendsState.value = MarketTrendsState.Error("No trends data")
                    }
                } else {
                    _trendsState.value = MarketTrendsState.Error("Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _trendsState.value = MarketTrendsState.Error(e.message ?: "Unknown error")
            }
        }
    }

    fun resetPredictionState() {
        _predictionState.value = MarketPredictionState.Idle
    }

    // State classes
    sealed class MarketPricesState {
        object Idle : MarketPricesState()
        object Loading : MarketPricesState()
        data class Success(val response: MarketPricesResponse) : MarketPricesState()
        data class Error(val message: String) : MarketPricesState()
    }

    sealed class MarketPredictionState {
        object Idle : MarketPredictionState()
        object Loading : MarketPredictionState()
        data class Success(val response: MarketPredictionResponse) : MarketPredictionState()
        data class Error(val message: String) : MarketPredictionState()
    }

    sealed class MarketTrendsState {
        object Idle : MarketTrendsState()
        object Loading : MarketTrendsState()
        data class Success(val response: MarketTrendsResponse) : MarketTrendsState()
        data class Error(val message: String) : MarketTrendsState()
    }

    sealed class MandiListState {
        object Idle : MandiListState()
        object Loading : MandiListState()
        data class Success(val mandis: List<Map<String, String>>) : MandiListState()
        data class Error(val message: String) : MandiListState()
    }
}
