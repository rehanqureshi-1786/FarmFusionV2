package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.VoiceQueryRequest
import com.example.farmfusionapp.data.model.VoiceQueryResponse
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.launch

class VoiceViewModel : ViewModel() {

    private val _voiceState = mutableStateOf<VoiceState>(VoiceState.Idle)
    val voiceState: State<VoiceState> = _voiceState

    fun processVoiceQuery(
        query: String,
        location: String? = null,
        latitude: Double? = null,
        longitude: Double? = null,
        languageHint: String? = null
    ) {
        viewModelScope.launch {
            _voiceState.value = VoiceState.Loading
            try {
                val request = VoiceQueryRequest(query, location, latitude, longitude, languageHint)
                val response = RetrofitInstance.api.processVoice(request)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _voiceState.value = VoiceState.Success(it)
                    } ?: run {
                        _voiceState.value = VoiceState.Error("Empty response from assistant")
                    }
                } else {
                    _voiceState.value = VoiceState.Error("Assistant Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _voiceState.value = VoiceState.Error(e.message ?: "Network error")
            }
        }
    }

    fun resetState() {
        _voiceState.value = VoiceState.Idle
    }

    sealed class VoiceState {
        object Idle : VoiceState()
        object Loading : VoiceState()
        data class Success(val response: VoiceQueryResponse) : VoiceState()
        data class Error(val message: String) : VoiceState()
    }
}
