package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.DiseaseDetectResponse
import com.example.farmfusionapp.data.model.DiseaseHistoryResponse
import com.example.farmfusionapp.data.model.DiseaseInfoResponse
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File

/**
 * ViewModel for Disease Detection feature
 * Connects to backend /disease endpoints
 */
class DiseaseViewModel : ViewModel() {

    private val api = RetrofitInstance.api

    // State for disease detection
    private val _detectState = mutableStateOf<DiseaseDetectState>(DiseaseDetectState.Idle)
    val detectState: State<DiseaseDetectState> = _detectState

    // State for history
    private val _historyState = mutableStateOf<DiseaseHistoryState>(DiseaseHistoryState.Idle)
    val historyState: State<DiseaseHistoryState> = _historyState

    // State for disease info
    private val _infoState = mutableStateOf<DiseaseInfoState>(DiseaseInfoState.Idle)
    val infoState: State<DiseaseInfoState> = _infoState

    /**
     * Upload image and detect disease
     * POST /api/v1/disease/detect
     */
    fun detectDisease(
        imageFile: File,
        cropType: String?,
        firebaseToken: String? = null,
        mimeType: String = "image/jpeg"
    ) {
        viewModelScope.launch {
            _detectState.value = DiseaseDetectState.Loading

            try {
                // Wake Render free-tier instance before the heavier multipart request.
                runCatching { api.checkHealth() }

                if (!imageFile.exists()) {
                    _detectState.value = DiseaseDetectState.Error("Image file not found at: ${imageFile.absolutePath}")
                    return@launch
                }

                val requestFile = imageFile.asRequestBody(mimeType.toMediaTypeOrNull())
                val imagePart = MultipartBody.Part.createFormData(
                    "image",
                    imageFile.name,
                    requestFile
                )

                val response = api.detectDisease(
                    imagePart,
                    cropType,
                    firebaseToken
                )

                if (response.isSuccessful) {
                    response.body()?.let {
                        _detectState.value = DiseaseDetectState.Success(it)
                    } ?: run {
                        _detectState.value = DiseaseDetectState.Error("Empty response from server")
                    }
                } else {
                    _detectState.value = DiseaseDetectState.Error(
                        "Server Error: ${response.code()} - ${response.message()}"
                    )
                }
            } catch (e: Exception) {
                _detectState.value = DiseaseDetectState.Error("Network Error: ${e.message ?: "Unknown error"}")
            }
        }
    }

    /**
     * Get disease detection history
     * GET /disease/history
     */
    fun getHistory(firebaseToken: String, limit: Int = 10) {
        viewModelScope.launch {
            _historyState.value = DiseaseHistoryState.Loading

            try {
                val response = api.getDiseaseHistory(firebaseToken, limit)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _historyState.value = DiseaseHistoryState.Success(it)
                    } ?: run {
                        _historyState.value = DiseaseHistoryState.Success(
                            DiseaseHistoryResponse(true, emptyList())
                        )
                    }
                } else {
                    _historyState.value = DiseaseHistoryState.Error(
                        "Error: ${response.code()}"
                    )
                }
            } catch (e: Exception) {
                _historyState.value = DiseaseHistoryState.Error(e.message ?: "Unknown error")
            }
        }
    }

    /**
     * Get disease information
     * GET /api/v1/disease/info/{disease_name}
     */
    fun getDiseaseInfo(diseaseName: String) {
        viewModelScope.launch {
            _infoState.value = DiseaseInfoState.Loading

            try {
                val response = api.getDiseaseInfo(diseaseName)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _infoState.value = DiseaseInfoState.Success(it)
                    } ?: run {
                        _infoState.value = DiseaseInfoState.Error("No information found")
                    }
                } else {
                    _infoState.value = DiseaseInfoState.Error(
                        "Error: ${response.code()}"
                    )
                }
            } catch (e: Exception) {
                _infoState.value = DiseaseInfoState.Error(e.message ?: "Unknown error")
            }
        }
    }

    fun resetDetectState() {
        _detectState.value = DiseaseDetectState.Idle
    }

    // State classes
    sealed class DiseaseDetectState {
        object Idle : DiseaseDetectState()
        object Loading : DiseaseDetectState()
        data class Success(val response: DiseaseDetectResponse) : DiseaseDetectState()
        data class Error(val message: String) : DiseaseDetectState()
    }

    sealed class DiseaseHistoryState {
        object Idle : DiseaseHistoryState()
        object Loading : DiseaseHistoryState()
        data class Success(val response: DiseaseHistoryResponse) : DiseaseHistoryState()
        data class Error(val message: String) : DiseaseHistoryState()
    }

    sealed class DiseaseInfoState {
        object Idle : DiseaseInfoState()
        object Loading : DiseaseInfoState()
        data class Success(val response: DiseaseInfoResponse) : DiseaseInfoState()
        data class Error(val message: String) : DiseaseInfoState()
    }
}
