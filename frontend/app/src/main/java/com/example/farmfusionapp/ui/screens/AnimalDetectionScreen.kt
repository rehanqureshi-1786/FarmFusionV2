package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.data.model.DetectionEventModel
import com.example.farmfusionapp.data.model.LatestStatusModel
import com.example.farmfusionapp.data.model.SensorDetailModel
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnimalDetectionScreen(navController: NavController) {
    val coroutineScope = rememberCoroutineScope()
    var latestStatus by remember { mutableStateOf<LatestStatusModel?>(null) }
    var historyEvents by remember { mutableStateOf<List<DetectionEventModel>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    var isRefreshing by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    suspend fun fetchData() {
        try {
            val statusRes = RetrofitInstance.api.getAnimalDetectionLatest("NODE_01")
            if (statusRes.isSuccessful) {
                latestStatus = statusRes.body()
                errorMessage = null
            }

            val histRes = RetrofitInstance.api.getAnimalDetectionHistory("NODE_01", limit = 20)
            if (histRes.isSuccessful) {
                historyEvents = histRes.body()?.events.orEmpty()
            }
        } catch (e: Exception) {
            errorMessage = e.message ?: "Network error"
        } finally {
            isLoading = false
            isRefreshing = false
        }
    }

    // Initial fetch + periodic auto-refresh every 3 seconds
    LaunchedEffect(Unit) {
        fetchData()
        while (true) {
            delay(3000)
            try {
                val statusRes = RetrofitInstance.api.getAnimalDetectionLatest("NODE_01")
                if (statusRes.isSuccessful) {
                    latestStatus = statusRes.body()
                }
                val histRes = RetrofitInstance.api.getAnimalDetectionHistory("NODE_01", limit = 20)
                if (histRes.isSuccessful) {
                    historyEvents = histRes.body()?.events.orEmpty()
                }
            } catch (_: Exception) {}
        }
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            Icons.Rounded.Shield,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(24.dp)
                        )
                        Text(
                            "Farm Perimeter Security",
                            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(
                        onClick = {
                            isRefreshing = true
                            coroutineScope.launch { fetchData() }
                        }
                    ) {
                        Icon(
                            Icons.Rounded.Refresh,
                            contentDescription = "Refresh",
                            tint = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        NeoScaffoldBackground(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // 1. Overall Status Card
                    item {
                        val status = latestStatus?.overall_status ?: "NODE_OFFLINE"
                        val (bannerColor, icon, title, subtitle) = when (status) {
                            "INTRUSION_DETECTED" -> Quad(
                                Color(0xFFEF4444),
                                Icons.Rounded.Warning,
                                "ANIMAL INTRUSION DETECTED",
                                "Active perimeter breach on: ${latestStatus?.detected_sensors?.joinToString(", ") ?: "Perimeter"}"
                            )
                            "AREA_CLEAR" -> Quad(
                                Color(0xFF10B981),
                                Icons.Rounded.CheckCircle,
                                "AREA IS SECURE & CLEAR",
                                "All 8 active sensors online and monitoring perimeter."
                            )
                            "SENSORS_OFFLINE" -> Quad(
                                Color(0xFFF59E0B),
                                Icons.Rounded.SensorsOff,
                                "SENSORS OFFLINE",
                                "Some sensors are not reporting: ${latestStatus?.offline_sensors?.joinToString(", ") ?: ""}"
                            )
                            else -> Quad(
                                Color(0xFF6B7280),
                                Icons.Rounded.WifiOff,
                                "ESP32 NODE DISCONNECTED",
                                "Hardware node 'NODE_01' is offline. Waiting for Wi-Fi keep-alive..."
                            )
                        }

                        Surface(
                            shape = RoundedCornerShape(20.dp),
                            color = bannerColor.copy(alpha = 0.12f),
                            border = BorderStroke(1.5.dp, bannerColor.copy(alpha = 0.4f)),
                            modifier = Modifier
                                .fillMaxWidth()
                                .shadow(4.dp, RoundedCornerShape(20.dp))
                        ) {
                            Row(
                                modifier = Modifier.padding(18.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(16.dp)
                            ) {
                                Surface(
                                    shape = CircleShape,
                                    color = bannerColor,
                                    modifier = Modifier.size(52.dp)
                                ) {
                                    Box(contentAlignment = Alignment.Center) {
                                        Icon(icon, contentDescription = null, tint = Color.White, modifier = Modifier.size(28.dp))
                                    }
                                }
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        title,
                                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Black, color = bannerColor)
                                    )
                                    Text(
                                        subtitle,
                                        style = MaterialTheme.typography.bodySmall.copy(color = Color(0xFF374151))
                                    )
                                }
                            }
                        }
                    }

                    // 2. Sensor Matrix Section
                    item {
                        Text(
                            "Perimeter Sensors (6x IR + 2x PIR)",
                            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }

                    item {
                        val defaultSensors = listOf(
                            "IR_1" to "IR", "IR_2" to "IR", "IR_3" to "IR",
                            "IR_4" to "IR", "IR_5" to "IR", "IR_6" to "IR",
                            "PIR_1" to "PIR", "PIR_2" to "PIR"
                        )
                        val sensorsMap = latestStatus?.sensors ?: emptyMap()

                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            // 2 rows of 4 sensors
                            defaultSensors.chunked(4).forEach { rowSensors ->
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    rowSensors.forEach { (sName, sType) ->
                                        val detail = sensorsMap[sName]
                                        val isOnline = detail?.health == "online"
                                        val isDetected = detail?.status == "detected"

                                        val cardColor = when {
                                            !isOnline -> Color(0xFFF3F4F6)
                                            isDetected -> Color(0xFFFEE2E2)
                                            else -> Color(0xFFECFDF5)
                                        }
                                        val borderColor = when {
                                            !isOnline -> Color(0xFFD1D5DB)
                                            isDetected -> Color(0xFFEF4444)
                                            else -> Color(0xFF10B981)
                                        }
                                        val statusLabel = when {
                                            !isOnline -> "OFFLINE"
                                            isDetected -> "DETECTED"
                                            else -> "CLEAR"
                                        }

                                        Surface(
                                            shape = RoundedCornerShape(12.dp),
                                            color = cardColor,
                                            border = BorderStroke(1.dp, borderColor),
                                            modifier = Modifier.weight(1f)
                                        ) {
                                            Column(
                                                modifier = Modifier.padding(8.dp),
                                                horizontalAlignment = Alignment.CenterHorizontally,
                                                verticalArrangement = Arrangement.spacedBy(2.dp)
                                            ) {
                                                Text(
                                                    sName,
                                                    style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold)
                                                )
                                                Text(
                                                    sType,
                                                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp, color = Color.Gray)
                                                )
                                                Text(
                                                    statusLabel,
                                                    style = MaterialTheme.typography.labelSmall.copy(
                                                        fontWeight = FontWeight.Bold,
                                                        fontSize = 10.sp,
                                                        color = borderColor
                                                    )
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // 3. History Timeline Section
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "Recent Intrusion Events",
                                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
                            )
                            Text(
                                "${historyEvents.size} events",
                                style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray)
                            )
                        }
                    }

                    if (historyEvents.isEmpty()) {
                        item {
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = Color.White.copy(alpha = 0.8f),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Box(
                                    modifier = Modifier.padding(24.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        "No animal intrusion events logged yet.",
                                        style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray)
                                    )
                                }
                            }
                        }
                    } else {
                        items(historyEvents) { event ->
                            val isDet = event.status.lowercase() == "detected"
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = Color.White,
                                shadowElevation = 1.dp,
                                border = BorderStroke(1.dp, Color(0xFFE5E7EB)),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Row(
                                    modifier = Modifier.padding(12.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                                    ) {
                                        Icon(
                                            if (isDet) Icons.Rounded.NotificationsActive else Icons.Rounded.CheckCircleOutline,
                                            contentDescription = null,
                                            tint = if (isDet) Color(0xFFEF4444) else Color(0xFF10B981),
                                            modifier = Modifier.size(22.dp)
                                        )
                                        Column {
                                            Text(
                                                "${event.sensor} (${event.sensor_type})",
                                                style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold)
                                            )
                                            Text(
                                                event.timestamp.take(19).replace("T", " "),
                                                style = MaterialTheme.typography.labelSmall.copy(fontSize = 11.sp, color = Color.Gray)
                                            )
                                        }
                                    }

                                    Surface(
                                        shape = RoundedCornerShape(8.dp),
                                        color = if (isDet) Color(0xFFFEE2E2) else Color(0xFFECFDF5)
                                    ) {
                                        Text(
                                            if (isDet) "DETECTED" else "CLEARED",
                                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                            style = MaterialTheme.typography.labelSmall.copy(
                                                fontWeight = FontWeight.Bold,
                                                color = if (isDet) Color(0xFFEF4444) else Color(0xFF10B981)
                                            )
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

private data class Quad<A, B, C, D>(val first: A, val second: B, val third: C, val fourth: D)
