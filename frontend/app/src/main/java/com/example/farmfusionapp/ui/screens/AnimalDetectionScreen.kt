package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.*
import com.example.farmfusionapp.utils.AppLocalizer
import com.example.farmfusionapp.viewmodel.AnimalDetectionViewModel
import kotlinx.coroutines.delay

// --- FarmFusion Brand Palette for IoT Intrusion ---
private val FarmGreenPrimary = Color(0xFF2E7D32)
private val FarmGreenDark = Color(0xFF1B5E20)
private val FarmGreenLight = Color(0xFFE8F5E9)
private val FarmGreenBorder = Color(0xFFA5D6A7)
private val AlertCrimson = Color(0xFFD32F2F)
private val AlertCrimsonLight = Color(0xFFFFEBEE)
private val WarningAmber = Color(0xFFF57C00)
private val WarningAmberLight = Color(0xFFFFF3E0)
private val NeutralDark = Color(0xFF1A1A1A)
private val NeutralGray = Color(0xFF757575)
private val SoftBg = Color(0xFFF7FBF7)

// Zone mapping keys for 14-language localization lookup
private val SENSOR_ZONE_KEYS = mapOf(
    "IR_1" to Pair("north boundary", "north perimeter beam"),
    "IR_2" to Pair("east boundary", "east perimeter beam"),
    "IR_3" to Pair("south boundary", "south perimeter beam"),
    "IR_4" to Pair("west boundary", "west perimeter beam"),
    "IR_5" to Pair("orchard edge", "fruit tree boundary"),
    "IR_6" to Pair("gate line", "main entrance tripwire"),
    "PIR_1" to Pair("main crop zone", "crop field motion"),
    "PIR_2" to Pair("grain storage", "storage shed motion")
)

@Composable
fun AnimalDetectionScreen(
    navController: NavController,
    vm: AnimalDetectionViewModel = viewModel()
) {
    val currentLang = LocalAppLanguage.current
    val scrollState = rememberScrollState()
    val latestState by vm.latestStatusState
    val historyState by vm.historyState
    val isAutoRefresh by vm.isAutoRefreshEnabled
    val isRepellentActive by vm.isRepellentActive
    val isSimulating by vm.isSimulating
    val toastMessage by vm.toastMessage
    val selectedFilter by vm.selectedFilter

    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(toastMessage) {
        toastMessage?.let {
            snackbarHostState.showSnackbar(it, duration = SnackbarDuration.Short)
            vm.clearToast()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = SoftBg,
        contentWindowInsets = WindowInsets(0, 0, 0, 0)
    ) { _ ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(SoftBg)
        ) {
            // Background Illustration anchored at the very top, completely covering upper area
            Image(
                painter = painterResource(id = R.drawable.ill_animal_alert_top),
                contentDescription = "Wild Animal Alert Background",
                contentScale = ContentScale.Crop,
                alignment = Alignment.TopCenter,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(420.dp)
            )

            // Gradient overlay to blend into soft background
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(
                                Color.Transparent,
                                SoftBg.copy(alpha = 0.35f),
                                SoftBg.copy(alpha = 0.85f),
                                SoftBg
                            ),
                            startY = 200f,
                            endY = 780f
                        )
                    )
            )

            // Main Scrollable Content
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(scrollState)
            ) {
                // 1. Top Bar & Node Health Badge (behind status bar)
                TopHeaderSection(
                    navController = navController,
                    latestState = latestState,
                    currentLang = currentLang,
                    onToggleAutoRefresh = { vm.toggleAutoRefresh(!isAutoRefresh) }
                )

                Spacer(modifier = Modifier.height(8.dp))

                // 2. Hero Security Status & Intrusion Radar Card
                HeroSecurityCard(
                    latestState = latestState,
                    isRepellentActive = isRepellentActive,
                    currentLang = currentLang,
                    onToggleRepellent = { vm.toggleRepellent(!isRepellentActive) },
                    onSendHeartbeat = { vm.sendNodeHeartbeat() },
                    onRetry = { vm.refreshAll() }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 3. Quick Simulation Bar (Live IoT Testing Controls)
                QuickSimulationBar(
                    isSimulating = isSimulating,
                    currentLang = currentLang,
                    onTriggerTest = { sensor, type -> vm.triggerSensorSimulation(sensor, type, "detected") },
                    onClearAll = {
                        SENSOR_ZONE_KEYS.keys.forEach { sName ->
                            val sType = if (sName.startsWith("PIR")) "PIR" else "IR"
                            vm.triggerSensorSimulation(sName, sType, "cleared")
                        }
                    },
                    onSendHeartbeat = { vm.sendNodeHeartbeat() }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 4. Perimeter Sensor Matrix Grid
                PerimeterSensorMatrixSection(
                    latestState = latestState,
                    isSimulating = isSimulating,
                    currentLang = currentLang,
                    onTriggerSensor = { sensor, type, currentStatus ->
                        val nextStatus = if (currentStatus == "detected") "cleared" else "detected"
                        vm.triggerSensorSimulation(sensor, type, nextStatus)
                    }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 5. Smart Deterrent & Audio-Strobe Defense Section
                SmartDeterrentControlCard(
                    isRepellentActive = isRepellentActive,
                    currentLang = currentLang,
                    onToggleRepellent = { vm.toggleRepellent(!isRepellentActive) }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 6. Real-Time Incident History Log
                IntrusionHistorySection(
                    historyState = historyState,
                    selectedFilter = selectedFilter,
                    currentLang = currentLang,
                    onSelectFilter = { vm.setFilter(it) },
                    onRefresh = { vm.fetchHistory() }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 7. How It Works Timeline (Preserved with Sensor Illustration)
                HowItWorksSection(currentLang = currentLang)

                // Bottom Buffer for Navigation Bar
                Spacer(modifier = Modifier.height(110.dp))
            }
        }
    }
}

// ==========================================
// 1. TOP HEADER SECTION
// ==========================================

@Composable
private fun TopHeaderSection(
    navController: NavController,
    latestState: AnimalDetectionViewModel.LatestStatusState,
    currentLang: String,
    onToggleAutoRefresh: () -> Unit
) {
    val strings = LocalStrings.current
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .statusBarsPadding()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Surface(
                shape = CircleShape,
                color = Color.White.copy(alpha = 0.92f),
                shadowElevation = 1.5.dp,
                modifier = Modifier.size(38.dp)
            ) {
                IconButton(
                    onClick = { navController.popBackStack() },
                    modifier = Modifier.fillMaxSize()
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Rounded.ArrowBack,
                        contentDescription = "Back",
                        tint = NeutralDark,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            // Screen Title
            Text(
                text = strings.dashboard.animalIntrusion,
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp,
                color = NeutralDark
            )

            // Right Action: Online / Offline Hardware Connectivity Card
            val isOnline = when (latestState) {
                is AnimalDetectionViewModel.LatestStatusState.Success -> latestState.data.overall_status != "NODE_OFFLINE"
                else -> false
            }

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = if (isOnline) Color(0xFFE8F5E9) else Color(0xFFFFEBEE),
                border = BorderStroke(1.dp, if (isOnline) Color(0xFFA5D6A7) else Color(0xFFFFCDD2)),
                modifier = Modifier.clickable { onToggleAutoRefresh() }
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(if (isOnline) Color(0xFF2E7D32) else Color(0xFFD32F2F))
                    )
                    Spacer(modifier = Modifier.width(5.dp))
                    Text(
                        text = if (isOnline) AppLocalizer.localizeAnimalDetectionPhrase("online", currentLang) else AppLocalizer.localizeAnimalDetectionPhrase("offline", currentLang),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isOnline) Color(0xFF2E7D32) else Color(0xFFD32F2F)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // Headline & Subtitle
        Column(modifier = Modifier.padding(horizontal = 8.dp)) {
            Text(
                text = strings.animalDetection.animalDetection,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = NeutralDark
            )
            Text(
                text = strings.animalDetection.liveCameraFeed,
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = FarmGreenPrimary
            )
            Text(
                text = AppLocalizer.localizeAnimalDetectionPhrase("animal alert header desc", currentLang),
                fontSize = 13.sp,
                color = Color.DarkGray,
                modifier = Modifier.padding(top = 4.dp),
                lineHeight = 18.sp
            )
        }
    }
}

// ==========================================
// 2. HERO LIVE SECURITY CARD
// ==========================================

@Composable
private fun HeroSecurityCard(
    latestState: AnimalDetectionViewModel.LatestStatusState,
    isRepellentActive: Boolean,
    currentLang: String,
    onToggleRepellent: () -> Unit,
    onSendHeartbeat: () -> Unit,
    onRetry: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(26.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
            .shadow(6.dp, RoundedCornerShape(26.dp)),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        when (latestState) {
            is AnimalDetectionViewModel.LatestStatusState.Loading -> {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        CircularProgressIndicator(color = FarmGreenPrimary, strokeWidth = 3.dp)
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(AppLocalizer.localizeAnimalDetectionPhrase("connecting to iot gateway", currentLang), fontSize = 13.sp, color = NeutralGray)
                    }
                }
            }

            is AnimalDetectionViewModel.LatestStatusState.Error -> {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        imageVector = Icons.Rounded.CloudOff,
                        contentDescription = null,
                        tint = WarningAmber,
                        modifier = Modifier.size(40.dp)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = AppLocalizer.localizeAnimalDetectionPhrase("iot telemetry gateway offline", currentLang),
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        color = NeutralDark
                    )
                    Text(
                        text = AppLocalizer.localizeAnimalDetectionPhrase("backend connected tap below", currentLang),
                        fontSize = 12.sp,
                        color = NeutralGray,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(vertical = 6.dp)
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(
                            onClick = onSendHeartbeat,
                            colors = ButtonDefaults.buttonColors(containerColor = FarmGreenPrimary),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Icon(Icons.Rounded.Bolt, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(AppLocalizer.localizeAnimalDetectionPhrase("wake node heartbeat", currentLang), fontSize = 13.sp)
                        }
                        OutlinedButton(
                            onClick = onRetry,
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text(AppLocalizer.localizeAnimalDetectionPhrase("retry", currentLang), fontSize = 13.sp, color = FarmGreenPrimary)
                        }
                    }
                }
            }

            is AnimalDetectionViewModel.LatestStatusState.Success -> {
                val data = latestState.data
                val overall = data.overall_status
                val isDetected = overall == "INTRUSION_DETECTED" || data.detected_sensors.isNotEmpty()
                val isOffline = overall == "NODE_OFFLINE"

                val heroBgColor = when {
                    isDetected -> Color(0xFFFFF1F1)
                    isOffline -> Color(0xFFFFF8E1)
                    else -> Color(0xFFF1F8E9)
                }

                val heroAccentColor = when {
                    isDetected -> AlertCrimson
                    isOffline -> WarningAmber
                    else -> FarmGreenPrimary
                }

                // Pulsing animation for active intrusion
                val infiniteTransition = rememberInfiniteTransition(label = "pulse")
                val pulseScale by infiniteTransition.animateFloat(
                    initialValue = 1f,
                    targetValue = if (isDetected) 1.15f else 1f,
                    animationSpec = infiniteRepeatable(
                        animation = tween(600, easing = FastOutSlowInEasing),
                        repeatMode = RepeatMode.Reverse
                    ),
                    label = "scale"
                )

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(
                            Brush.verticalGradient(
                                colors = listOf(heroBgColor, Color.White)
                            )
                        )
                        .padding(20.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(54.dp)
                                    .clip(CircleShape)
                                    .background(heroAccentColor.copy(alpha = 0.15f)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = when {
                                        isDetected -> Icons.Rounded.WarningAmber
                                        isOffline -> Icons.Rounded.SignalWifiOff
                                        else -> Icons.Rounded.Security
                                    },
                                    contentDescription = null,
                                    tint = heroAccentColor,
                                    modifier = Modifier.size(30.dp)
                                )
                            }
                            Spacer(modifier = Modifier.width(14.dp))
                            Column {
                                Text(
                                    text = when {
                                        isDetected -> AppLocalizer.localizeAnimalDetectionPhrase("intrusion detected", currentLang)
                                        isOffline -> AppLocalizer.localizeAnimalDetectionPhrase("node offline", currentLang)
                                        else -> AppLocalizer.localizeAnimalDetectionPhrase("perimeter secure", currentLang)
                                    },
                                    fontSize = 17.sp,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = heroAccentColor
                                )
                                Text(
                                    text = when {
                                        isDetected -> {
                                            val sensorStr = data.detected_sensors.joinToString(", ") { sKey ->
                                                val zonePair = SENSOR_ZONE_KEYS[sKey]
                                                if (zonePair != null) {
                                                    "$sKey (${AppLocalizer.localizeAnimalDetectionPhrase(zonePair.first, currentLang)})"
                                                } else sKey
                                            }
                                            val alertTemplate = AppLocalizer.localizeAnimalDetectionPhrase("alert in sensors", currentLang)
                                            if (alertTemplate.contains("%s")) alertTemplate.replace("%s", sensorStr) else "$alertTemplate $sensorStr"
                                        }
                                        isOffline -> AppLocalizer.localizeAnimalDetectionPhrase("waiting for esp32 keep alive", currentLang)
                                        else -> AppLocalizer.localizeAnimalDetectionPhrase("all 8 sensors active clear", currentLang)
                                    },
                                    fontSize = 12.sp,
                                    color = if (isDetected) AlertCrimson else Color.DarkGray,
                                    fontWeight = if (isDetected) FontWeight.SemiBold else FontWeight.Normal
                                )
                            }
                        }

                        // Status Badge
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = heroAccentColor.copy(alpha = 0.12f),
                            border = BorderStroke(1.dp, heroAccentColor.copy(alpha = 0.3f))
                        ) {
                            Text(
                                text = data.device_id,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = heroAccentColor,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Live Telemetry Stats Bar
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(16.dp))
                            .background(Color.White)
                            .border(1.dp, Color(0xFFE5E7EB), RoundedCornerShape(16.dp))
                            .padding(vertical = 12.dp, horizontal = 16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        StatPillItem(
                            label = AppLocalizer.localizeAnimalDetectionPhrase("active sensors", currentLang),
                            value = "${data.sensors.values.count { it.health == "online" }}/8",
                            color = FarmGreenPrimary
                        )
                        Box(modifier = Modifier.height(26.dp).width(1.dp).background(Color(0xFFE0E0E0)))
                        StatPillItem(
                            label = AppLocalizer.localizeAnimalDetectionPhrase("intrusions", currentLang),
                            value = "${data.detected_sensors.size}",
                            color = if (data.detected_sensors.isNotEmpty()) AlertCrimson else NeutralDark
                        )
                        Box(modifier = Modifier.height(26.dp).width(1.dp).background(Color(0xFFE0E0E0)))
                        StatPillItem(
                            label = AppLocalizer.localizeAnimalDetectionPhrase("offline", currentLang),
                            value = "${data.offline_sensors.size}",
                            color = if (data.offline_sensors.isNotEmpty()) WarningAmber else NeutralDark
                        )
                    }

                    if (isDetected) {
                        Spacer(modifier = Modifier.height(14.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Button(
                                onClick = onToggleRepellent,
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (isRepellentActive) Color(0xFF374151) else AlertCrimson
                                ),
                                shape = RoundedCornerShape(14.dp),
                                modifier = Modifier.weight(1f).height(46.dp)
                            ) {
                                Icon(
                                    imageVector = if (isRepellentActive) Icons.Rounded.VolumeOff else Icons.Rounded.VolumeUp,
                                    contentDescription = null,
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = if (isRepellentActive) AppLocalizer.localizeAnimalDetectionPhrase("stop repellent", currentLang) else AppLocalizer.localizeAnimalDetectionPhrase("sound alarm", currentLang),
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    } else if (isOffline) {
                        Spacer(modifier = Modifier.height(12.dp))
                        Button(
                            onClick = onSendHeartbeat,
                            colors = ButtonDefaults.buttonColors(containerColor = FarmGreenPrimary),
                            shape = RoundedCornerShape(14.dp),
                            modifier = Modifier.fillMaxWidth().height(44.dp)
                        ) {
                            Icon(Icons.Rounded.CellTower, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(AppLocalizer.localizeAnimalDetectionPhrase("send esp32 node heartbeat", currentLang), fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                        }
                    }
                }
            }

            else -> Unit
        }
    }
}

@Composable
private fun StatPillItem(label: String, value: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = label, fontSize = 11.sp, color = NeutralGray)
        Text(
            text = value,
            fontSize = 16.sp,
            fontWeight = FontWeight.ExtraBold,
            color = color
        )
    }
}

// ==========================================
// 3. QUICK SIMULATION & TESTING BAR
// ==========================================

@Composable
private fun QuickSimulationBar(
    isSimulating: Boolean,
    currentLang: String,
    onTriggerTest: (String, String) -> Unit,
    onClearAll: () -> Unit,
    onSendHeartbeat: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(20.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Rounded.Science,
                        contentDescription = null,
                        tint = FarmGreenPrimary,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = AppLocalizer.localizeAnimalDetectionPhrase("live iot simulation testing", currentLang),
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = NeutralDark
                    )
                }
                if (isSimulating) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp, color = FarmGreenPrimary)
                }
            }

            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = AppLocalizer.localizeAnimalDetectionPhrase("live iot sim desc", currentLang),
                fontSize = 12.sp,
                color = NeutralGray,
                lineHeight = 16.sp
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Quick Action Chips
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ActionTestChip(
                    icon = Icons.Rounded.Warning,
                    label = AppLocalizer.localizeAnimalDetectionPhrase("trigger ir1 breach", currentLang),
                    color = AlertCrimson,
                    onClick = { onTriggerTest("IR_1", "IR") }
                )
                ActionTestChip(
                    icon = Icons.Rounded.DirectionsRun,
                    label = AppLocalizer.localizeAnimalDetectionPhrase("trigger pir1 motion", currentLang),
                    color = WarningAmber,
                    onClick = { onTriggerTest("PIR_1", "PIR") }
                )
                ActionTestChip(
                    icon = Icons.Rounded.CellTower,
                    label = AppLocalizer.localizeAnimalDetectionPhrase("send keep alive ping", currentLang),
                    color = FarmGreenPrimary,
                    onClick = onSendHeartbeat
                )
                ActionTestChip(
                    icon = Icons.Rounded.CheckCircle,
                    label = AppLocalizer.localizeAnimalDetectionPhrase("clear all sensors", currentLang),
                    color = Color(0xFF455A64),
                    onClick = onClearAll
                )
            }
        }
    }
}

@Composable
private fun ActionTestChip(
    icon: ImageVector,
    label: String,
    color: Color,
    onClick: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(12.dp),
        color = color.copy(alpha = 0.1f),
        border = BorderStroke(1.dp, color.copy(alpha = 0.3f)),
        modifier = Modifier.clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(imageVector = icon, contentDescription = null, tint = color, modifier = Modifier.size(16.dp))
            Spacer(modifier = Modifier.width(6.dp))
            Text(text = label, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = color)
        }
    }
}

// ==========================================
// 4. PERIMETER SENSOR MATRIX GRID
// ==========================================

@Composable
private fun PerimeterSensorMatrixSection(
    latestState: AnimalDetectionViewModel.LatestStatusState,
    isSimulating: Boolean,
    currentLang: String,
    onTriggerSensor: (String, String, String) -> Unit
) {
    Column(modifier = Modifier.padding(horizontal = 16.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = AppLocalizer.localizeAnimalDetectionPhrase("perimeter sensor grid", currentLang),
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold,
                color = NeutralDark
            )
            Text(
                text = AppLocalizer.localizeAnimalDetectionPhrase("8 nodes total", currentLang),
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium,
                color = NeutralGray
            )
        }

        Spacer(modifier = Modifier.height(10.dp))

        val sensorsMap = (latestState as? AnimalDetectionViewModel.LatestStatusState.Success)?.data?.sensors ?: emptyMap()

        // 6 IR Boundary Tripwires
        Text(
            text = AppLocalizer.localizeAnimalDetectionPhrase("boundary ir beams header", currentLang),
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = FarmGreenPrimary,
            modifier = Modifier.padding(vertical = 4.dp, horizontal = 2.dp)
        )

        val irSensors = listOf("IR_1", "IR_2", "IR_3", "IR_4", "IR_5", "IR_6")
        irSensors.chunked(2).forEach { rowSensors ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                rowSensors.forEach { sensorKey ->
                    val detail = sensorsMap[sensorKey]
                    val status = detail?.status ?: "offline"
                    val health = detail?.health ?: "offline"
                    val zoneKey = SENSOR_ZONE_KEYS[sensorKey] ?: Pair("north boundary", "north perimeter beam")
                    val zoneTitle = AppLocalizer.localizeAnimalDetectionPhrase(zoneKey.first, currentLang)
                    val zoneDesc = AppLocalizer.localizeAnimalDetectionPhrase(zoneKey.second, currentLang)

                    SensorTileCard(
                        modifier = Modifier.weight(1f),
                        sensorKey = sensorKey,
                        sensorType = "IR",
                        zoneTitle = zoneTitle,
                        zoneDesc = zoneDesc,
                        status = status,
                        health = health,
                        currentLang = currentLang,
                        onClickToggle = {
                            onTriggerSensor(sensorKey, "IR", status)
                        }
                    )
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
        }

        Spacer(modifier = Modifier.height(6.dp))

        // 2 PIR Thermal Motion Detectors
        Text(
            text = AppLocalizer.localizeAnimalDetectionPhrase("wide angle pir header", currentLang),
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = FarmGreenPrimary,
            modifier = Modifier.padding(vertical = 4.dp, horizontal = 2.dp)
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            listOf("PIR_1", "PIR_2").forEach { sensorKey ->
                val detail = sensorsMap[sensorKey]
                val status = detail?.status ?: "offline"
                val health = detail?.health ?: "offline"
                val zoneKey = SENSOR_ZONE_KEYS[sensorKey] ?: Pair("main crop zone", "crop field motion")
                val zoneTitle = AppLocalizer.localizeAnimalDetectionPhrase(zoneKey.first, currentLang)
                val zoneDesc = AppLocalizer.localizeAnimalDetectionPhrase(zoneKey.second, currentLang)

                SensorTileCard(
                    modifier = Modifier.weight(1f),
                    sensorKey = sensorKey,
                    sensorType = "PIR",
                    zoneTitle = zoneTitle,
                    zoneDesc = zoneDesc,
                    status = status,
                    health = health,
                    currentLang = currentLang,
                    onClickToggle = {
                        onTriggerSensor(sensorKey, "PIR", status)
                    }
                )
            }
        }
    }
}

@Composable
private fun SensorTileCard(
    modifier: Modifier = Modifier,
    sensorKey: String,
    sensorType: String,
    zoneTitle: String,
    zoneDesc: String,
    status: String,
    health: String,
    currentLang: String,
    onClickToggle: () -> Unit
) {
    val isDetected = status == "detected"
    val isOnline = health == "online"

    val cardBg = when {
        isDetected -> Color(0xFFFFEBEE)
        !isOnline -> Color(0xFFF9FAFB)
        else -> Color.White
    }

    val borderColor = when {
        isDetected -> Color(0xFFEF5350)
        !isOnline -> Color(0xFFE5E7EB)
        else -> Color(0xFFE8F5E9)
    }

    val stateColor = when {
        isDetected -> AlertCrimson
        !isOnline -> NeutralGray
        else -> FarmGreenPrimary
    }

    Card(
        shape = RoundedCornerShape(18.dp),
        modifier = modifier
            .shadow(if (isDetected) 4.dp else 1.dp, RoundedCornerShape(18.dp)),
        colors = CardDefaults.cardColors(containerColor = cardBg),
        border = BorderStroke(1.5.dp, borderColor)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Status Pill (top right, keeping top-left position blank)
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = stateColor.copy(alpha = 0.15f)
                ) {
                    Text(
                        text = when {
                            isDetected -> AppLocalizer.localizeAnimalDetectionPhrase("detected", currentLang)
                            !isOnline -> AppLocalizer.localizeAnimalDetectionPhrase("offline", currentLang)
                            else -> AppLocalizer.localizeAnimalDetectionPhrase("clear", currentLang)
                        },
                        fontSize = 10.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = stateColor,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = sensorKey,
                fontSize = 14.sp,
                fontWeight = FontWeight.ExtraBold,
                color = NeutralDark
            )
            Text(
                text = zoneTitle,
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium,
                color = Color.DarkGray,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            Text(
                text = zoneDesc,
                fontSize = 10.sp,
                color = NeutralGray,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Action Button (ONLY this element is tappable)
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = stateColor.copy(alpha = 0.08f),
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(8.dp))
                    .clickable(onClick = onClickToggle)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 6.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = if (isDetected) AppLocalizer.localizeAnimalDetectionPhrase("tap to clear", currentLang) else AppLocalizer.localizeAnimalDetectionPhrase("tap to test trigger", currentLang),
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        color = stateColor
                    )
                }
            }
        }
    }
}

// ==========================================
// 5. SMART DETERRENT & STROBE CARD
// ==========================================

@Composable
private fun SmartDeterrentControlCard(
    isRepellentActive: Boolean,
    currentLang: String,
    onToggleRepellent: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(22.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        shape = CircleShape,
                        color = if (isRepellentActive) Color(0xFFFFEBEE) else FarmGreenLight,
                        modifier = Modifier.size(44.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = if (isRepellentActive) Icons.Rounded.VolumeUp else Icons.Rounded.VolumeOff,
                                contentDescription = null,
                                tint = if (isRepellentActive) AlertCrimson else FarmGreenPrimary,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = AppLocalizer.localizeAnimalDetectionPhrase("acoustic strobe deterrent", currentLang),
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = NeutralDark
                        )
                        Text(
                            text = if (isRepellentActive) AppLocalizer.localizeAnimalDetectionPhrase("ultrasonic repellent active", currentLang) else AppLocalizer.localizeAnimalDetectionPhrase("standby auto triggers", currentLang),
                            fontSize = 12.sp,
                            color = if (isRepellentActive) AlertCrimson else NeutralGray
                        )
                    }
                }

                Switch(
                    checked = isRepellentActive,
                    onCheckedChange = { onToggleRepellent() },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = AlertCrimson,
                        uncheckedThumbColor = Color.White,
                        uncheckedTrackColor = Color(0xFFBDBDBD)
                    )
                )
            }

            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = AppLocalizer.localizeAnimalDetectionPhrase("smart deterrent desc", currentLang),
                fontSize = 12.sp,
                color = Color.DarkGray,
                lineHeight = 16.sp
            )
        }
    }
}

// ==========================================
// 6. REAL-TIME INCIDENT HISTORY LOG
// ==========================================

@Composable
private fun IntrusionHistorySection(
    historyState: AnimalDetectionViewModel.HistoryState,
    selectedFilter: String,
    currentLang: String,
    onSelectFilter: (String) -> Unit,
    onRefresh: () -> Unit
) {
    Column(modifier = Modifier.padding(horizontal = 16.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = AppLocalizer.localizeAnimalDetectionPhrase("intrusion incident log", currentLang),
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold,
                color = NeutralDark
            )
            IconButton(onClick = onRefresh, modifier = Modifier.size(28.dp)) {
                Icon(
                    imageVector = Icons.Rounded.Refresh,
                    contentDescription = "Refresh history",
                    tint = FarmGreenPrimary,
                    modifier = Modifier.size(18.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Filter Chips
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf(
                "ALL" to AppLocalizer.localizeAnimalDetectionPhrase("all events", currentLang),
                "IR" to AppLocalizer.localizeAnimalDetectionPhrase("ir tripwires", currentLang),
                "PIR" to AppLocalizer.localizeAnimalDetectionPhrase("pir motion", currentLang)
            ).forEach { (code, label) ->
                val isSelected = selectedFilter == code
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = if (isSelected) FarmGreenPrimary else Color.White,
                    border = BorderStroke(1.dp, if (isSelected) FarmGreenPrimary else Color(0xFFE0E0E0)),
                    modifier = Modifier.clickable { onSelectFilter(code) }
                ) {
                    Text(
                        text = label,
                        fontSize = 12.sp,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                        color = if (isSelected) Color.White else NeutralDark,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        when (historyState) {
            is AnimalDetectionViewModel.HistoryState.Loading -> {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(strokeWidth = 2.dp, modifier = Modifier.size(24.dp), color = FarmGreenPrimary)
                }
            }

            is AnimalDetectionViewModel.HistoryState.Error -> {
                Card(
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Text(
                        text = historyState.message,
                        fontSize = 12.sp,
                        color = NeutralGray,
                        modifier = Modifier.padding(16.dp),
                        textAlign = TextAlign.Center
                    )
                }
            }

            is AnimalDetectionViewModel.HistoryState.Success -> {
                val events = historyState.data.events
                if (events.isEmpty()) {
                    Card(
                        shape = RoundedCornerShape(18.dp),
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color.White)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Icon(
                                imageVector = Icons.Rounded.VerifiedUser,
                                contentDescription = null,
                                tint = FarmGreenPrimary,
                                modifier = Modifier.size(36.dp)
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = AppLocalizer.localizeAnimalDetectionPhrase("perimeter peaceful", currentLang),
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp,
                                color = NeutralDark
                            )
                            Text(
                                text = AppLocalizer.localizeAnimalDetectionPhrase("no intrusion incidents recorded", currentLang),
                                fontSize = 12.sp,
                                color = NeutralGray,
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                } else {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        events.take(6).forEach { event ->
                            HistoryEventItem(event, currentLang)
                        }
                    }
                }
            }

            else -> Unit
        }
    }
}

@Composable
private fun HistoryEventItem(event: DetectionEventModel, currentLang: String) {
    val isDetected = event.status.lowercase() == "detected"
    val zoneKey = SENSOR_ZONE_KEYS[event.sensor] ?: Pair("north boundary", "north perimeter beam")
    val zoneTitle = AppLocalizer.localizeAnimalDetectionPhrase(zoneKey.first, currentLang)

    Card(
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Surface(
                    shape = CircleShape,
                    color = if (isDetected) AlertCrimsonLight else FarmGreenLight,
                    modifier = Modifier.size(38.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = if (isDetected) Icons.Rounded.Warning else Icons.Rounded.CheckCircle,
                            contentDescription = null,
                            tint = if (isDetected) AlertCrimson else FarmGreenPrimary,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = "${event.sensor} • $zoneTitle",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold,
                        color = NeutralDark
                    )
                    val timeLabel = AppLocalizer.localizeAnimalDetectionPhrase("timestamp label", currentLang)
                    val formattedTime = formatTimestamp(event.timestamp)
                    Text(
                        text = if (timeLabel.contains("%s")) timeLabel.replace("%s", formattedTime) else "$timeLabel $formattedTime",
                        fontSize = 11.sp,
                        color = NeutralGray
                    )
                }
            }

            Surface(
                shape = RoundedCornerShape(8.dp),
                color = if (isDetected) AlertCrimson.copy(alpha = 0.12f) else FarmGreenPrimary.copy(alpha = 0.12f)
            ) {
                Text(
                    text = if (isDetected) AppLocalizer.localizeAnimalDetectionPhrase("breach", currentLang) else AppLocalizer.localizeAnimalDetectionPhrase("cleared", currentLang),
                    fontSize = 11.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = if (isDetected) AlertCrimson else FarmGreenPrimary,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        }
    }
}

private fun formatTimestamp(iso: String): String {
    return try {
        if (iso.contains("T")) {
            val parts = iso.split("T")
            val date = parts[0]
            val time = parts[1].substringBefore(".").take(5)
            "$date $time"
        } else {
            iso
        }
    } catch (e: Exception) {
        iso
    }
}

// ==========================================
// 7. HOW IT WORKS SECTION (WITH SENSOR ILLUST)
// ==========================================

@Composable
private fun HowItWorksSection(currentLang: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Text(
            text = AppLocalizer.localizeAnimalDetectionPhrase("how iot system works", currentLang),
            fontSize = 17.sp,
            fontWeight = FontWeight.Bold,
            color = FarmGreenPrimary,
            modifier = Modifier.padding(bottom = 12.dp, start = 4.dp)
        )

        Card(
            shape = RoundedCornerShape(24.dp),
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
        ) {
            Box(modifier = Modifier.fillMaxWidth()) {
                // Timeline Steps (Left Side)
                Column(
                    modifier = Modifier
                        .fillMaxWidth(0.65f)
                        .padding(start = 18.dp, top = 18.dp, bottom = 18.dp, end = 8.dp)
                ) {
                    StepTimelineItem(
                        icon = Icons.Rounded.Sensors,
                        title = AppLocalizer.localizeAnimalDetectionPhrase("step1 title", currentLang),
                        desc = AppLocalizer.localizeAnimalDetectionPhrase("step1 desc", currentLang)
                    )
                    StepTimelineItem(
                        icon = Icons.Rounded.NotificationsActive,
                        title = AppLocalizer.localizeAnimalDetectionPhrase("step2 title", currentLang),
                        desc = AppLocalizer.localizeAnimalDetectionPhrase("step2 desc", currentLang)
                    )
                    StepTimelineItem(
                        icon = Icons.Rounded.Security,
                        title = AppLocalizer.localizeAnimalDetectionPhrase("step3 title", currentLang),
                        desc = AppLocalizer.localizeAnimalDetectionPhrase("step3 desc", currentLang),
                        isLast = true
                    )
                }

                // Sensor Illustration (Right Side)
                Image(
                    painter = painterResource(id = R.drawable.ill_animal_alert_sensor),
                    contentDescription = "Sensor System Mounted",
                    contentScale = ContentScale.Fit,
                    alignment = Alignment.BottomEnd,
                    modifier = Modifier
                        .matchParentSize()
                        .padding(start = 20.dp)
                        .offset(y = 15.dp)
                )
            }
        }
    }
}

@Composable
private fun StepTimelineItem(icon: ImageVector, title: String, desc: String, isLast: Boolean = false) {
    Row(modifier = Modifier.height(IntrinsicSize.Min)) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.width(32.dp)
        ) {
            Surface(
                shape = CircleShape,
                color = FarmGreenLight,
                modifier = Modifier.size(32.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = FarmGreenPrimary,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
            if (!isLast) {
                Canvas(
                    modifier = Modifier
                        .width(2.dp)
                        .weight(1f)
                        .padding(vertical = 4.dp)
                ) {
                    drawLine(
                        color = Color(0xFFC8E6C9),
                        start = Offset(0f, 0f),
                        end = Offset(0f, size.height),
                        strokeWidth = 3f,
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(10f, 10f), 0f)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.width(12.dp))

        Column(modifier = Modifier.padding(bottom = if (isLast) 0.dp else 20.dp)) {
            Text(
                text = title,
                fontSize = 13.sp,
                fontWeight = FontWeight.Bold,
                color = NeutralDark
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = desc,
                fontSize = 11.sp,
                color = NeutralGray,
                lineHeight = 15.sp
            )
        }
    }
}