package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.*
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.launch

/**
 * ViewModel for Weather feature
 * Connects to backend /weather endpoints
 */
class WeatherViewModel : ViewModel() {

    private val api = RetrofitInstance.api

    // State for current weather
    private val _currentState = mutableStateOf<WeatherState>(WeatherState.Idle)
    val currentState: State<WeatherState> = _currentState

    // State for forecast
    private val _forecastState = mutableStateOf<ForecastState>(ForecastState.Idle)
    val forecastState: State<ForecastState> = _forecastState

    // State for farming weather (combined)
    private val _farmingState = mutableStateOf<FarmingWeatherState>(FarmingWeatherState.Idle)
    val farmingState: State<FarmingWeatherState> = _farmingState

    /**
     * Get current weather
     * GET /weather/current
     */
    fun getCurrentWeather(latitude: Double, longitude: Double) {
        viewModelScope.launch {
            _currentState.value = WeatherState.Loading

            try {
                val response = api.getCurrentWeather(latitude, longitude)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _currentState.value = WeatherState.Success(it)
                    } ?: run {
                        _currentState.value = WeatherState.Error("Empty response")
                    }
                } else {
                    _currentState.value = WeatherState.Error("Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _currentState.value = WeatherState.Error(e.message ?: "Unknown error")
            }
        }
    }

    /**
     * Get weather forecast
     * GET /weather/forecast
     */
    fun getForecast(latitude: Double, longitude: Double, days: Int = 5) {
        viewModelScope.launch {
            _forecastState.value = ForecastState.Loading

            try {
                val response = api.getWeatherForecast(latitude, longitude, days)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _forecastState.value = ForecastState.Success(it)
                    } ?: run {
                        _forecastState.value = ForecastState.Error("Empty response")
                    }
                } else {
                    _forecastState.value = ForecastState.Error("Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _forecastState.value = ForecastState.Error(e.message ?: "Unknown error")
            }
        }
    }

    /**
     * Get comprehensive farming weather
     * GET /weather/farming
     */
    fun getFarmingWeather(latitude: Double, longitude: Double, days: Int = 7) {
        viewModelScope.launch {
            _farmingState.value = FarmingWeatherState.Loading

            try {
                val response = api.getFarmingWeather(latitude, longitude, days)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _farmingState.value = FarmingWeatherState.Success(it)
                    } ?: run {
                        _farmingState.value = FarmingWeatherState.Error("Empty response")
                    }
                } else {
                    _farmingState.value = FarmingWeatherState.Error(
                        "Error: ${response.code()}"
                    )
                }
            } catch (e: Exception) {
                _farmingState.value = FarmingWeatherState.Error(
                    e.message ?: "Unknown error"
                )
            }
        }
    }

    // State classes
    sealed class WeatherState {
        object Idle : WeatherState()
        object Loading : WeatherState()
        data class Success(val response: WeatherResponse) : WeatherState()
        data class Error(val message: String) : WeatherState()
    }

    sealed class ForecastState {
        object Idle : ForecastState()
        object Loading : ForecastState()
        data class Success(val response: WeatherForecastResponse) : ForecastState()
        data class Error(val message: String) : ForecastState()
    }

    sealed class FarmingWeatherState {
        object Idle : FarmingWeatherState()
        object Loading : FarmingWeatherState()
        data class Success(val response: FarmingWeatherResponse) : FarmingWeatherState()
        data class Error(val message: String) : FarmingWeatherState()
    }
}
