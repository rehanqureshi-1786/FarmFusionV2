package com.example.farmfusionapp.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.model.*
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * ViewModel for IoT Animal Intrusion Detection System
 * Interacts with /api/v1/animal-detection endpoints to deliver real-time perimeter security.
 */
class AnimalDetectionViewModel : ViewModel() {

    private val api = RetrofitInstance.api

    // --- State Holders ---
    private val _latestStatusState = mutableStateOf<LatestStatusState>(LatestStatusState.Idle)
    val latestStatusState: State<LatestStatusState> = _latestStatusState

    private val _historyState = mutableStateOf<HistoryState>(HistoryState.Idle)
    val historyState: State<HistoryState> = _historyState

    private val _deviceStatusState = mutableStateOf<DeviceStatusState>(DeviceStatusState.Idle)
    val deviceStatusState: State<DeviceStatusState> = _deviceStatusState

    private val _selectedFilter = mutableStateOf("ALL") // "ALL", "IR", "PIR"
    val selectedFilter: State<String> = _selectedFilter

    private val _isAutoRefreshEnabled = mutableStateOf(true)
    val isAutoRefreshEnabled: State<Boolean> = _isAutoRefreshEnabled

    private val _isRepellentActive = mutableStateOf(false)
    val isRepellentActive: State<Boolean> = _isRepellentActive

    private val _isSimulating = mutableStateOf(false)
    val isSimulating: State<Boolean> = _isSimulating

    private val _toastMessage = mutableStateOf<String?>(null)
    val toastMessage: State<String?> = _toastMessage

    private var pollingJob: Job? = null

    init {
        refreshAll()
        startAutoPolling()
    }

    fun startAutoPolling(intervalMs: Long = 4000L) {
        pollingJob?.cancel()
        pollingJob = viewModelScope.launch {
            while (isActive) {
                if (_isAutoRefreshEnabled.value) {
                    fetchLatestStatus(silent = true)
                }
                delay(intervalMs)
            }
        }
    }

    fun toggleAutoRefresh(enabled: Boolean) {
        _isAutoRefreshEnabled.value = enabled
        if (enabled && pollingJob?.isActive != true) {
            startAutoPolling()
        }
    }

    fun setFilter(filter: String) {
        _selectedFilter.value = filter
        val sensorType = if (filter == "ALL") null else filter
        fetchHistory(sensorType = sensorType)
    }

    fun refreshAll(deviceId: String = "NODE_01") {
        fetchLatestStatus(deviceId = deviceId, silent = false)
        fetchDeviceStatus(deviceId = deviceId)
        val sensorType = if (_selectedFilter.value == "ALL") null else _selectedFilter.value
        fetchHistory(deviceId = deviceId, sensorType = sensorType)
    }

    fun fetchLatestStatus(deviceId: String = "NODE_01", silent: Boolean = false) {
        viewModelScope.launch {
            if (!silent && _latestStatusState.value !is LatestStatusState.Success) {
                _latestStatusState.value = LatestStatusState.Loading
            }
            try {
                val response = api.getAnimalDetectionLatest(deviceId = deviceId)
                if (response.isSuccessful) {
                    response.body()?.let {
                        _latestStatusState.value = LatestStatusState.Success(it)
                    } ?: run {
                        if (!silent) _latestStatusState.value = LatestStatusState.Error("Empty telemetry data")
                    }
                } else {
                    if (!silent) _latestStatusState.value = LatestStatusState.Error("Server returned code ${response.code()}")
                }
            } catch (e: Exception) {
                if (!silent) _latestStatusState.value = LatestStatusState.Error(e.message ?: "Failed to reach IoT gateway")
            }
        }
    }

    fun fetchHistory(deviceId: String = "NODE_01", sensorType: String? = null) {
        viewModelScope.launch {
            _historyState.value = HistoryState.Loading
            try {
                val response = api.getAnimalDetectionHistory(
                    deviceId = deviceId,
                    limit = 30,
                    offset = 0,
                    sensorType = sensorType
                )
                if (response.isSuccessful) {
                    response.body()?.let {
                        _historyState.value = HistoryState.Success(it)
                    } ?: run {
                        _historyState.value = HistoryState.Error("No history events available")
                    }
                } else {
                    _historyState.value = HistoryState.Error("Failed to fetch history: ${response.code()}")
                }
            } catch (e: Exception) {
                _historyState.value = HistoryState.Error(e.message ?: "Network error fetching history")
            }
        }
    }

    fun fetchDeviceStatus(deviceId: String = "NODE_01") {
        viewModelScope.launch {
            try {
                val response = api.getDeviceStatus(deviceId = deviceId)
                if (response.isSuccessful) {
                    response.body()?.let {
                        _deviceStatusState.value = DeviceStatusState.Success(it)
                    }
                }
            } catch (e: Exception) {
                // Ignore silent background status check
            }
        }
    }

    fun triggerSensorSimulation(sensor: String, sensorType: String, status: String = "detected", deviceId: String = "NODE_01") {
        viewModelScope.launch {
            _isSimulating.value = true
            try {
                val req = DetectionEventCreateRequest(
                    device_id = deviceId,
                    sensor = sensor,
                    sensor_type = sensorType,
                    status = status
                )
                val response = api.postDetectionEvent(req)
                if (response.isSuccessful) {
                    _toastMessage.value = if (status == "detected") "⚠️ Alert triggered on $sensor ($sensorType)" else "✅ Cleared $sensor ($sensorType)"
                    fetchLatestStatus(deviceId = deviceId, silent = true)
                    val currentType = if (_selectedFilter.value == "ALL") null else _selectedFilter.value
                    fetchHistory(deviceId = deviceId, sensorType = currentType)
                } else {
                    _toastMessage.value = "Failed to simulate trigger: ${response.code()}"
                }
            } catch (e: Exception) {
                _toastMessage.value = "Simulation error: ${e.message}"
            } finally {
                _isSimulating.value = false
            }
        }
    }

    fun sendNodeHeartbeat(deviceId: String = "NODE_01") {
        viewModelScope.launch {
            _isSimulating.value = true
            try {
                val req = HeartbeatRequestModel(device_id = deviceId)
                val response = api.sendHeartbeat(req)
                if (response.isSuccessful) {
                    _toastMessage.value = "📡 Heartbeat acknowledged by $deviceId (Node is ONLINE)"
                    fetchLatestStatus(deviceId = deviceId, silent = true)
                    fetchDeviceStatus(deviceId = deviceId)
                } else {
                    _toastMessage.value = "Heartbeat failed: ${response.code()}"
                }
            } catch (e: Exception) {
                _toastMessage.value = "Heartbeat connection error: ${e.message}"
            } finally {
                _isSimulating.value = false
            }
        }
    }

    fun toggleRepellent(activate: Boolean) {
        _isRepellentActive.value = activate
        _toastMessage.value = if (activate) {
            "🔊 Ultrasonic Deterrent & Strobe Active!"
        } else {
            "🔇 Deterrent deactivated"
        }
    }

    fun clearToast() {
        _toastMessage.value = null
    }

    override fun onCleared() {
        super.onCleared()
        pollingJob?.cancel()
    }

    // --- State Sealed Classes ---
    sealed class LatestStatusState {
        object Idle : LatestStatusState()
        object Loading : LatestStatusState()
        data class Success(val data: LatestStatusModel) : LatestStatusState()
        data class Error(val message: String) : LatestStatusState()
    }

    sealed class HistoryState {
        object Idle : HistoryState()
        object Loading : HistoryState()
        data class Success(val data: HistoryResponseModel) : HistoryState()
        data class Error(val message: String) : HistoryState()
    }

    sealed class DeviceStatusState {
        object Idle : DeviceStatusState()
        data class Success(val data: DeviceStatusModel) : DeviceStatusState()
        data class Error(val message: String) : DeviceStatusState()
    }
}
