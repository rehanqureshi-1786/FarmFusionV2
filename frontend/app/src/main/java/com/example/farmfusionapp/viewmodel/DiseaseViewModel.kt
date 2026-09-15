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

            val resultState: DiseaseDetectState = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                try {
                    if (!imageFile.exists()) {
                        return@withContext DiseaseDetectState.Error("Image file not found: ${imageFile.absolutePath}")
                    }

                    if (!imageFile.isFile || !imageFile.canRead()) {
                        return@withContext DiseaseDetectState.Error("Image file is not readable: ${imageFile.absolutePath}")
                    }

                    val fileSize = imageFile.length()
                    if (fileSize == 0L) {
                        return@withContext DiseaseDetectState.Error("Image file is empty (0 bytes)")
                    }

                    android.util.Log.d("DiseaseViewModel", "Uploading image: ${imageFile.name} (${fileSize} bytes)")

                    val requestFile = try {
                        imageFile.asRequestBody(mimeType.toMediaTypeOrNull())
                    } catch (e: Exception) {
                        android.util.Log.e("DiseaseViewModel", "Error creating request body", e)
                        return@withContext DiseaseDetectState.Error("Failed to prepare image for upload: ${e.message}")
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
                        android.util.Log.e("DiseaseViewModel", "API request failed", e)
                        return@withContext DiseaseDetectState.Error("Network request failed: ${e.message ?: "Unknown error"}")
                    }

                    if (response.isSuccessful) {
                        response.body()?.let { body ->
                            android.util.Log.d("DiseaseViewModel", "Response received: disease=${body.data?.disease_name}, success=${body.success}")

                            if (body.data == null) {
                                return@withContext DiseaseDetectState.Error("Server returned no disease data")
                            }

                            DiseaseDetectState.Success(body)
                        } ?: DiseaseDetectState.Error("Server response body is empty")
                    } else {
                        val errorBody = try {
                            response.errorBody()?.string() ?: "No error details"
                        } catch (e: Exception) {
                            "Unable to read error details"
                        }
                        android.util.Log.e("DiseaseViewModel", "API error: ${response.code()} - $errorBody")
                        DiseaseDetectState.Error(
                            "Server Error: ${response.code()} - ${response.message()}\n$errorBody"
                        )
                    }
                } catch (e: Exception) {
                    android.util.Log.e("DiseaseViewModel", "Unexpected exception", e)
                    DiseaseDetectState.Error("Unexpected error: ${e.message ?: "Unknown error"}")
                }
            }
            _detectState.value = resultState
        }
    }

    fun getHistory(firebaseToken: String? = null, limit: Int = 10) {
        viewModelScope.launch {
            _historyState.value = DiseaseHistoryState.Loading

            val resultState: DiseaseHistoryState = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                try {
                    val response = api.getDiseaseHistory(firebaseToken, limit)

                    if (response.isSuccessful) {
                        response.body()?.let {
                            DiseaseHistoryState.Success(it)
                        } ?: DiseaseHistoryState.Success(
                            DiseaseHistoryResponse(true, emptyList())
                        )
                    } else {
                        DiseaseHistoryState.Error(
                            "Error: ${response.code()}"
                        )
                    }
                } catch (e: Exception) {
                    DiseaseHistoryState.Error(e.message ?: "Unknown error")
                }
            }
            _historyState.value = resultState
        }
    }

    fun getDiseaseInfo(diseaseName: String) {
        viewModelScope.launch {
            _infoState.value = DiseaseInfoState.Loading

            val resultState: DiseaseInfoState = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                try {
                    val response = api.getDiseaseInfo(diseaseName)

                    if (response.isSuccessful) {
                        response.body()?.let {
                            DiseaseInfoState.Success(it)
                        } ?: DiseaseInfoState.Error("No information found")
                    } else {
                        DiseaseInfoState.Error(
                            "Error: ${response.code()}"
                        )
                    }
                } catch (e: Exception) {
                    DiseaseInfoState.Error(e.message ?: "Unknown error")
                }
            }
            _infoState.value = resultState
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