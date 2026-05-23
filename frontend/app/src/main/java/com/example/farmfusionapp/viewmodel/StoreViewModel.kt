package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.StoreRecommendationItem
import com.example.farmfusionapp.data.model.StoreRecommendationsResponse
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.launch

class StoreViewModel : ViewModel() {

    private val api = RetrofitInstance.api

    private val _storeState = mutableStateOf<StoreState>(StoreState.Idle)
    val storeState: State<StoreState> = _storeState

    fun getRecommendations(token: String? = null, category: String? = null) {
        viewModelScope.launch {
            _storeState.value = StoreState.Loading
            try {
                val response = api.getStoreRecommendations(token, category)
                if (response.isSuccessful) {
                    response.body()?.let {
                        if (it.success) {
                            _storeState.value = StoreState.Success(it.items)
                        } else {
                            _storeState.value = StoreState.Error("Failed to load recommendations")
                        }
                    } ?: run {
                        _storeState.value = StoreState.Error("Empty response from server")
                    }
                } else {
                    _storeState.value = StoreState.Error("Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _storeState.value = StoreState.Error(e.message ?: "Unknown error")
            }
        }
    }

    sealed class StoreState {
        object Idle : StoreState()
        object Loading : StoreState()
        data class Success(val items: List<StoreRecommendationItem>) : StoreState()
        data class Error(val message: String) : StoreState()
    }
}
