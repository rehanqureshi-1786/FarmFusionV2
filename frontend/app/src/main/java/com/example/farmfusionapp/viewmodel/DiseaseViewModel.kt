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

class DiseaseViewModel : ViewModel() {

    private val api = RetrofitInstance.api

    private val _detectState = mutableStateOf<DiseaseDetectState>(DiseaseDetectState.Idle)
    val detectState: State<DiseaseDetectState> = _detectState

    private val _historyState = mutableStateOf<DiseaseHistoryState>(DiseaseHistoryState.Idle)
    val historyState: State<DiseaseHistoryState> = _historyState

    private val _infoState = mutableStateOf<DiseaseInfoState>(DiseaseInfoState.Idle)
    val infoState: State<DiseaseInfoState> = _infoState

    fun detectDisease(
        imageFile: File,
        cropType: String?,
        firebaseToken: String? = null,
        responseLanguage: String? = null,
        mimeType: String = "image/jpeg"
    ) {
        viewModelScope.launch {
            _detectState.value = DiseaseDetectState.Loading

            try {
                if (!imageFile.exists()) {
                    _detectState.value = DiseaseDetectState.Error("Image file not found: ${imageFile.absolutePath}")
                    return@launch
                }

                if (!imageFile.isFile || !imageFile.canRead()) {
                    _detectState.value = DiseaseDetectState.Error("Image file is not readable: ${imageFile.absolutePath}")
                    return@launch
                }

                val fileSize = imageFile.length()
                if (fileSize == 0L) {
                    _detectState.value = DiseaseDetectState.Error("Image file is empty (0 bytes)")
                    return@launch
                }

                android.util.Log.d("DiseaseViewModel", "Uploading image: ${imageFile.name} (${fileSize} bytes)")

                val requestFile = try {
                    imageFile.asRequestBody(mimeType.toMediaTypeOrNull())
                } catch (e: Exception) {
                    _detectState.value = DiseaseDetectState.Error("Failed to prepare image for upload: ${e.message}")
                    android.util.Log.e("DiseaseViewModel", "Error creating request body", e)
                    return@launch
                }

                val imagePart = MultipartBody.Part.createFormData(
                    "image",
                    imageFile.name,
                    requestFile
                )

                val response = try {
                    api.detectDisease(
                        imagePart,
                        cropType,
                        firebaseToken,
                        responseLanguage
                    )
                } catch (e: Exception) {
                    _detectState.value = DiseaseDetectState.Error("Network request failed: ${e.message ?: "Unknown error"}")
                    android.util.Log.e("DiseaseViewModel", "API request failed", e)
                    return@launch
                }

                if (response.isSuccessful) {
                    response.body()?.let { body ->
                        android.util.Log.d("DiseaseViewModel", "Response received: disease=${body.data?.disease_name}, success=${body.success}")

                        val rawJson = com.google.gson.Gson().toJson(body)
                        android.util.Log.d("DiseaseDebug", "Full parsed body as JSON: $rawJson")

                        if (body.data == null) {
                            _detectState.value = DiseaseDetectState.Error("Server returned no disease data")
                            return@launch
                        }

                        _detectState.value = DiseaseDetectState.Success(body)
                    } ?: run {
                        _detectState.value = DiseaseDetectState.Error("Server response body is empty")
                    }
                } else {
                    val errorBody = try {
                        response.errorBody()?.string() ?: "No error details"
                    } catch (e: Exception) {
                        "Unable to read error details"
                    }
                    _detectState.value = DiseaseDetectState.Error(
                        "Server Error: ${response.code()} - ${response.message()}\n$errorBody"
                    )
                    android.util.Log.e("DiseaseViewModel", "API error: ${response.code()} - $errorBody")
                }
            } catch (e: Exception) {
                _detectState.value = DiseaseDetectState.Error("Unexpected error: ${e.message ?: "Unknown error"}")
                android.util.Log.e("DiseaseViewModel", "Unexpected exception", e)
            }
        }
    }

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