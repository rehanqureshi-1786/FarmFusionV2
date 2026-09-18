package com.example.farmfusionapp.viewmodel

import android.app.Application
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.ColdStorageItem
import com.example.farmfusionapp.data.repository.ColdStorageRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch

sealed class ColdStorageUiState {
    object Loading : ColdStorageUiState()
    data class Success(
        val items: List<ColdStorageItem>,
        val searchRadiusKm: Double = 50.0,
        val searchedArea: String? = null,
        val autoExpanded: Boolean = false
    ) : ColdStorageUiState()
    data class Error(val message: String) : ColdStorageUiState()
}

class ColdStorageViewModel(application: Application) : AndroidViewModel(application) {

    private val _uiState = mutableStateOf<ColdStorageUiState>(ColdStorageUiState.Loading)
    val uiState: State<ColdStorageUiState> = _uiState

    // User's physical location (from GPS or LocationSnapshotStore)
    val userLat = mutableStateOf<Double?>(null)
    val userLng = mutableStateOf<Double?>(null)

    // Current active filters
    val selectedRadius = mutableStateOf(50.0) // 10.0, 25.0, 50.0, 100.0
    val selectedCrop = mutableStateOf<String?>(null)
    val searchQuery = mutableStateOf("")
    val activeSearchedArea = mutableStateOf<String?>(null)

    private var currentJob: Job? = null

    init {
        // Initial fallback load with default coordinates until device GPS is initialized
        loadStorages()
    }

    fun initUserLocation(lat: Double, lng: Double) {
        val isDifferent = userLat.value != lat || userLng.value != lng
        userLat.value = lat
        userLng.value = lng
        if (isDifferent && searchQuery.value.isBlank()) {
            loadStorages()
        }
    }

    fun loadStorages(queryOverride: String? = null) {
        val queryToUse = (queryOverride ?: searchQuery.value).trim()
        val radiusToUse = selectedRadius.value
        val cropToUse = selectedCrop.value
        val lat = userLat.value ?: 26.9124
        val lng = userLng.value ?: 75.7873

        currentJob?.cancel()
        currentJob = viewModelScope.launch {
            _uiState.value = ColdStorageUiState.Loading
            try {
                val response = ColdStorageRepository.search(
                    context = getApplication(),
                    query = queryToUse.ifBlank { null },
                    latitude = lat,
                    longitude = lng,
                    radius = radiusToUse,
                    crop = cropToUse,
                    limit = 50
                )
                activeSearchedArea.value = response.searchedArea
                _uiState.value = ColdStorageUiState.Success(
                    items = response.results,
                    searchRadiusKm = response.searchRadiusKm,
                    searchedArea = response.searchedArea,
                    autoExpanded = response.autoExpanded
                )
            } catch (e: Exception) {
                _uiState.value = ColdStorageUiState.Error(
                    e.message ?: "Unable to load cold storage facilities"
                )
            }
        }
    }

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
        // If user clears the text to blank, automatically reload current location storages
        if (query.isBlank() && activeSearchedArea.value != null) {
            clearSearch()
        }
    }

    fun submitSearch(query: String) {
        searchQuery.value = query
        loadStorages(query)
    }

    fun clearSearch() {
        searchQuery.value = ""
        activeSearchedArea.value = null
        loadStorages("")
    }

    fun selectRadius(radiusKm: Double) {
        if (selectedRadius.value != radiusKm) {
            selectedRadius.value = radiusKm
            loadStorages()
        }
    }

    fun selectCrop(crop: String?) {
        if (selectedCrop.value != crop) {
            selectedCrop.value = crop
            loadStorages()
        }
    }
}
