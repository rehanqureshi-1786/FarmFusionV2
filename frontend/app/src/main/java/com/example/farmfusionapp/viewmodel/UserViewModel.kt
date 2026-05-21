package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.*
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.launch

/**
 * ViewModel for User management and Farms
 * Connects to backend /users and /auth endpoints
 */
class UserViewModel : ViewModel() {

    private val api = RetrofitInstance.api

    // Auth state
    private val _authState = mutableStateOf<AuthState>(AuthState.Idle)
    val authState: State<AuthState> = _authState

    // Profile state
    private val _profileState = mutableStateOf<ProfileState>(ProfileState.Idle)
    val profileState: State<ProfileState> = _profileState

    // Farms state
    private val _farmsState = mutableStateOf<FarmsState>(FarmsState.Idle)
    val farmsState: State<FarmsState> = _farmsState

    // Create farm state
    private val _createFarmState = mutableStateOf<CreateFarmState>(CreateFarmState.Idle)
    val createFarmState: State<CreateFarmState> = _createFarmState

    /**
     * Verify Firebase token and get/create user
     * POST /auth/verify
     */
    fun verifyAuthToken(firebaseToken: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading

            try {
                val response = api.verifyAuthToken(firebaseToken)

                if (response.isSuccessful) {
                    response.body()?.let {
                        if (it.success) {
                            _authState.value = AuthState.Success(it)
                        } else {
                            _authState.value = AuthState.Error(it.message)
                        }
                    } ?: run {
                        _authState.value = AuthState.Error("Empty response")
                    }
                } else {
                    _authState.value = AuthState.Error("Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _authState.value = AuthState.Error(e.message ?: "Unknown error")
            }
        }
    }

    /**
     * Get user profile
     * GET /users/profile
     */
    fun getUserProfile(firebaseToken: String) {
        viewModelScope.launch {
            _profileState.value = ProfileState.Loading

            try {
                val response = api.getUserProfile(firebaseToken)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _profileState.value = ProfileState.Success(it)
                    } ?: run {
                        _profileState.value = ProfileState.Error("Empty response")
                    }
                } else {
                    _profileState.value = ProfileState.Error("Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _profileState.value = ProfileState.Error(e.message ?: "Unknown error")
            }
        }
    }

    /**
     * Get user's farms
     * GET /users/farms
     */
    fun getUserFarms(firebaseToken: String) {
        viewModelScope.launch {
            _farmsState.value = FarmsState.Loading

            try {
                val response = api.getUserFarms(firebaseToken)

                if (response.isSuccessful) {
                    response.body()?.let {
                        _farmsState.value = FarmsState.Success(it)
                    } ?: run {
                        _farmsState.value = FarmsState.Success(
                            UserFarmsResponse(true, emptyList())
                        )
                    }
                } else {
                    _farmsState.value = FarmsState.Error("Error: ${response.code()}")
                }
            } catch (e: Exception) {
                _farmsState.value = FarmsState.Error(e.message ?: "Unknown error")
            }
        }
    }

    /**
     * Create a new farm
     * POST /users/farms
     */
    fun createFarm(
        firebaseToken: String,
        name: String,
        location: String,
        latitude: Double,
        longitude: Double,
        soilType: String,
        farmSize: Double,
        rainfall: Double = 0.0,
        temperature: Double = 25.0
    ) {
        viewModelScope.launch {
            _createFarmState.value = CreateFarmState.Loading

            try {
                val response = api.createFarm(
                    firebaseToken, name, location, latitude, longitude,
                    soilType, farmSize, rainfall, temperature
                )

                if (response.isSuccessful) {
                    response.body()?.let {
                        _createFarmState.value = CreateFarmState.Success(it)
                    } ?: run {
                        _createFarmState.value = CreateFarmState.Error("Empty response")
                    }
                } else {
                    _createFarmState.value = CreateFarmState.Error(
                        "Error: ${response.code()}"
                    )
                }
            } catch (e: Exception) {
                _createFarmState.value = CreateFarmState.Error(
                    e.message ?: "Unknown error"
                )
            }
        }
    }

    /**
     * Update user language preference
     * PUT /users/profile
     */
    fun updateLanguage(firebaseToken: String, languageCode: String, onResult: (Boolean, String) -> Unit) {
        viewModelScope.launch {
            try {
                val response = api.updateLanguage(firebaseToken, languageCode)
                if (response.isSuccessful && response.body()?.success == true) {
                    onResult(true, "Language updated successfully")
                } else {
                    onResult(false, "Failed to update language on server")
                }
            } catch (e: Exception) {
                onResult(false, e.message ?: "Network error")
            }
        }
    }

    fun resetCreateFarmState() {
        _createFarmState.value = CreateFarmState.Idle
    }

    // State classes
    sealed class AuthState {
        object Idle : AuthState()
        object Loading : AuthState()
        data class Success(val response: AuthResponse) : AuthState()
        data class Error(val message: String) : AuthState()
    }

    sealed class ProfileState {
        object Idle : ProfileState()
        object Loading : ProfileState()
        data class Success(val response: UserProfileResponse) : ProfileState()
        data class Error(val message: String) : ProfileState()
    }

    sealed class FarmsState {
        object Idle : FarmsState()
        object Loading : FarmsState()
        data class Success(val response: UserFarmsResponse) : FarmsState()
        data class Error(val message: String) : FarmsState()
    }

    sealed class CreateFarmState {
        object Idle : CreateFarmState()
        object Loading : CreateFarmState()
        data class Success(val response: CreateFarmResponse) : CreateFarmState()
        data class Error(val message: String) : CreateFarmState()
    }
}
