package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.components.*
import com.example.farmfusionapp.utils.*
import kotlinx.coroutines.launch

import com.example.farmfusionapp.data.model.WeatherAlertItemUi
import com.example.farmfusionapp.data.model.AgriculturalAdvisoryResponse
import com.example.farmfusionapp.data.model.DisasterRiskRequest
import com.example.farmfusionapp.data.model.DisasterRiskResponse

data class DisplayWeatherData(
    val temperature: Int,
    val feelsLike: Int? = null,
    val description: String,
    val humidity: Int,
    val windSpeed: Double,
    val city: String,
    val advice: String,
    val timestamp: String? = null,
    val forecast: List<DailyForecast> = emptyList(),
    val alerts: List<WeatherAlertItemUi> = emptyList(),
    val advisory: AgriculturalAdvisoryResponse? = null,
    val disasterRisk: DisasterRiskResponse? = null,
    val pressure: Int? = null
)

data class DailyForecast(
    val day: String,
    val high: Int,
    val low: Int,
    val condition: String,
    val rainProbability: Int = 0,
    val precipitationMm: Double = 0.0
)

object WeatherSnapshotStore {
    var latestWeather by mutableStateOf<DisplayWeatherData?>(null)
    var latestLanguage by mutableStateOf<String?>(null)
    var latestError by mutableStateOf<String?>(null)
    var lastUpdatedAt by mutableLongStateOf(0L)
}

fun shouldRefreshWeather(currentLanguage: String? = null, maxAgeMs: Long = 10 * 60 * 1000L): Boolean {
    if (WeatherSnapshotStore.latestWeather == null) return true
    if (currentLanguage != null && WeatherSnapshotStore.latestLanguage != null && WeatherSnapshotStore.latestLanguage != currentLanguage) return true
    return System.currentTimeMillis() - WeatherSnapshotStore.lastUpdatedAt > maxAgeMs
}

suspend fun refreshWeatherSnapshotIfNeeded(
    context: android.content.Context,
    force: Boolean = false,
    onResult: (DisplayWeatherData?, String?) -> Unit
) {
    val currentLang = LanguagePreferences.getSelectedLanguage(context) ?: "en"
    if (!force && !shouldRefreshWeather(currentLang)) {
        onResult(WeatherSnapshotStore.latestWeather, WeatherSnapshotStore.latestError)
        return
    }
    fetchWeatherFromLocation(context, onResult)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WeatherScreen(navController: NavController) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var weatherData by remember { mutableStateOf(WeatherSnapshotStore.latestWeather) }
    var errorMessage by remember { mutableStateOf<String?>(WeatherSnapshotStore.latestError) }
    var isLoading by remember { mutableStateOf(weatherData == null) }

    LocationPermissionEffect(
        context = context,
        onPermissionGranted = {
            isLoading = weatherData == null
            scope.launch {
                refreshWeatherSnapshotIfNeeded(context) { data, error ->
                    weatherData = data ?: weatherData
                    errorMessage = error
                    isLoading = false
                }
            }
        },
        onPermissionDenied = {
            errorMessage = "Location permission is needed for weather."
            isLoading = false
        }
    )

    // Edge-to-edge background container
    Box(modifier = Modifier.fillMaxSize().background(Color(0xFFF1F8E9))) {

        // Fullscreen background illustration
        Image(
            painter = painterResource(id = R.drawable.ill_weather_bg),
            contentDescription = "Weather Landscape Background",
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize()
        )

        Column(modifier = Modifier.fillMaxSize()) {
            CenterAlignedTopAppBar(
                title = {
                    Text(
                        text = "Weather",
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1B5E20)
                        )
                    )
                },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(
                            Icons.AutoMirrored.Rounded.ArrowBack,
                            contentDescription = "Back",
                            tint = Color(0xFF1B5E20)
                        )
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color.Transparent
                )
            )

            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                // No horizontal padding here so child rows can bleed to the edges!
                contentPadding = PaddingValues(top = 24.dp, bottom = 116.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                when {
                    isLoading -> item {
                        Box(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp), contentAlignment = Alignment.Center) {
                            WeatherLoadingState()
                        }
                    }
                    errorMessage != null -> item {
                        Box(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp), contentAlignment = Alignment.Center) {
                            WeatherErrorState(errorMessage!!) {
                                isLoading = true
                                errorMessage = null
                                scope.launch {
                                    refreshWeatherSnapshotIfNeeded(context, force = true) { data, error ->
                                        weatherData = data ?: weatherData
                                        errorMessage = error
                                        isLoading = false
                                    }
                                }
                            }
                        }
                    }
                    weatherData != null -> {

                        // 1. Weather Alerts
                        if (weatherData!!.alerts.isNotEmpty()) {
                            item {
                                Box(modifier = Modifier.padding(horizontal = 24.dp)) {
                                    WeatherAlertsBanner(weatherData!!.alerts)
                                }
                            }
                        }

                        // 1.5. Disaster Risk & Early Warning
                        if (weatherData!!.disasterRisk != null && weatherData!!.disasterRisk!!.predictions.isNotEmpty()) {
                            item {
                                Box(modifier = Modifier.padding(horizontal = 24.dp)) {
                                    DisasterRiskCard(weatherData!!.disasterRisk!!)
                                }
                            }
                        }

                        // 2. Hero Weather Card
                        item {
                            Box(modifier = Modifier.padding(horizontal = 24.dp)) {
                                WeatherHeroCard(weatherData!!)
                            }
                        }

                        // 3. Stat Cards Row
                        item {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 24.dp),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                WeatherStatCard("Humidity", "${weatherData!!.humidity}%", Icons.Rounded.WaterDrop, Modifier.weight(1f))
                                WeatherStatCard("Wind", "${weatherData!!.windSpeed.toInt()} km/h", Icons.Rounded.Air, Modifier.weight(1f))
                            }
                        }

                        // 4. Rich Advisory or Field Guidance
                        if (weatherData!!.advisory != null) {
                            item {
                                Column(modifier = Modifier.padding(start = 24.dp, end = 24.dp, top = 8.dp, bottom = 4.dp)) {
                                    Text(
                                        text = "Agricultural Advisory",
                                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                                    )
                                    Text(
                                        text = "Actionable agronomic guidance for field operations",
                                        style = MaterialTheme.typography.bodyMedium.copy(color = Color.DarkGray)
                                    )
                                }
                            }
                            item {
                                Box(modifier = Modifier.padding(horizontal = 24.dp)) {
                                    AgriculturalAdvisoryCard(weatherData!!.advisory!!)
                                }
                            }
                        } else {
                            item {
                                Column(modifier = Modifier.padding(start = 24.dp, end = 24.dp, top = 8.dp, bottom = 4.dp)) {
                                    Text(
                                        text = "Field guidance",
                                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                                    )
                                    Text(
                                        text = "Actionable farm operations & suitability for today",
                                        style = MaterialTheme.typography.bodyMedium.copy(color = Color.DarkGray)
                                    )
                                }
                            }
                            item {
                                Box(modifier = Modifier.padding(horizontal = 24.dp)) {
                                    FieldGuidanceCard(weatherData!!)
                                }
                            }
                        }

                        // 6. Outlook Forecast Section (Horizontally Scrollable)
                        item {
                            Column(modifier = Modifier.padding(start = 24.dp, end = 24.dp, top = 8.dp, bottom = 4.dp)) {
                                Text(
                                    text = "Outlook",
                                    style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                                )
                                Text(
                                    text = "7-day forecast for farm planning",
                                    style = MaterialTheme.typography.bodyMedium.copy(color = Color.DarkGray)
                                )
                            }
                        }
                        item {
                            LazyRow(
                                modifier = Modifier.fillMaxWidth(),
                                // This content padding ensures the cards bleed properly to the edge of the device screen while scrolling!
                                contentPadding = PaddingValues(horizontal = 24.dp),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                items(weatherData!!.forecast) { forecast ->
                                    OutlookCard(forecast, modifier = Modifier.width(85.dp))
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun WeatherHeroCard(weatherData: DisplayWeatherData) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .height(180.dp)
            .shadow(16.dp, RoundedCornerShape(24.dp), spotColor = Color(0xFF2E7D32).copy(alpha = 0.4f)),
        shape = RoundedCornerShape(24.dp),
        color = Color.Transparent
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.linearGradient(
                        colors = listOf(Color(0xFF55B059), Color(0xFF2E7D32))
                    )
                )
        ) {
            Box(modifier = Modifier.size(220.dp).offset(x = (-60).dp, y = (-60).dp).background(Color.White.copy(alpha = 0.06f), CircleShape))
            Box(modifier = Modifier.size(160.dp).align(Alignment.BottomEnd).offset(x = 40.dp, y = 40.dp).background(Color.White.copy(alpha = 0.08f), CircleShape))

            Column(
                modifier = Modifier.fillMaxSize().padding(22.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Rounded.LocationOn, contentDescription = null, tint = Color.White, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = weatherData.city,
                                style = MaterialTheme.typography.titleMedium.copy(color = Color.White, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                            )
                        }
                        val timeLabel = remember(weatherData.timestamp) {
                            if (!weatherData.timestamp.isNullOrBlank()) {
                                try {
                                    if (weatherData.timestamp.contains("T")) {
                                        "Updated at " + weatherData.timestamp.substringAfter("T").take(5)
                                    } else {
                                        "Updated " + weatherData.timestamp
                                    }
                                } catch (e: Exception) {
                                    "Current Conditions"
                                }
                            } else {
                                "Current Conditions"
                            }
                        }
                        Text(
                            text = timeLabel,
                            style = MaterialTheme.typography.labelMedium.copy(color = Color.White.copy(alpha = 0.85f)),
                            modifier = Modifier.padding(start = 22.dp, top = 2.dp)
                        )
                    }

                    Icon(
                        imageVector = when {
                            weatherData.description.contains("cloud", ignoreCase = true) -> Icons.Rounded.WbCloudy
                            weatherData.description.contains("rain", ignoreCase = true) -> Icons.Rounded.BeachAccess
                            else -> Icons.Rounded.WbSunny
                        },
                        contentDescription = null,
                        tint = Color.White,
                        modifier = Modifier.size(42.dp)
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "${weatherData.temperature}°C",
                        style = MaterialTheme.typography.displayLarge.copy(
                            fontWeight = FontWeight.SemiBold,
                            color = Color.White,
                            fontSize = 64.sp
                        )
                    )

                    Spacer(modifier = Modifier.width(16.dp))

                    // Vertical Line separator exactly matching DashboardScreen
                    Box(
                        modifier = Modifier
                            .height(56.dp)
                            .width(1.dp)
                            .background(Color.White.copy(alpha = 0.5f))
                    )

                    Spacer(modifier = Modifier.width(16.dp))

                    Column(verticalArrangement = Arrangement.Center) {
                        Text(
                            text = weatherData.description.replaceFirstChar { it.uppercase() },
                            style = MaterialTheme.typography.titleMedium.copy(
                                color = Color.White,
                                fontWeight = FontWeight.Bold,
                                fontSize = 18.sp
                            )
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = "Feels like ${weatherData.feelsLike ?: weatherData.temperature}°C",
                            style = MaterialTheme.typography.bodyMedium.copy(
                                color = Color.White.copy(alpha = 0.8f)
                            )
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun WeatherStatCard(label: String, value: String, icon: androidx.compose.ui.graphics.vector.ImageVector, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.height(96.dp),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        shadowElevation = 2.dp
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            Canvas(modifier = Modifier.fillMaxWidth().height(35.dp).align(Alignment.BottomCenter)) {
                val wavePath = Path().apply {
                    moveTo(0f, size.height * 0.4f)
                    quadraticBezierTo(size.width * 0.25f, 0f, size.width * 0.5f, size.height * 0.5f)
                    quadraticBezierTo(size.width * 0.75f, size.height, size.width, size.height * 0.6f)
                    lineTo(size.width, size.height)
                    lineTo(0f, size.height)
                    close()
                }
                drawPath(wavePath, color = Color(0xFFF1F8E9))
            }

            Column(
                modifier = Modifier.fillMaxSize().padding(horizontal = 14.dp, vertical = 10.dp),
                verticalArrangement = Arrangement.Top,
                horizontalAlignment = Alignment.Start
            ) {
                Box(
                    modifier = Modifier.size(28.dp).background(Color(0xFFF1F8E9), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(icon, contentDescription = null, tint = Color(0xFF2E7D32), modifier = Modifier.size(14.dp))
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text(label, style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray))
                Text(value, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
            }
        }
    }
}

@Composable
private fun OutlookCard(forecast: DailyForecast, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.height(116.dp),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        shadowElevation = 2.dp
    ) {
        Column(
            modifier = Modifier.fillMaxSize().padding(vertical = 10.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text(forecast.day, style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold, color = Color.DarkGray))

            RealWeatherIcon(condition = forecast.condition)

            if (forecast.precipitationMm > 0.0) {
                Text(
                    text = "${forecast.precipitationMm} mm",
                    style = MaterialTheme.typography.labelSmall.copy(color = Color(0xFF1976D2), fontSize = 10.sp)
                )
            }

            Text(
                text = "${forecast.high}° / ${forecast.low}°",
                style = MaterialTheme.typography.labelLarge.copy(
                    fontWeight = FontWeight.ExtraBold,
                    color = Color(0xFF2E7D32)
                )
            )
        }
    }
}

@Composable
private fun RealWeatherIcon(condition: String, modifier: Modifier = Modifier) {
    Box(modifier = modifier.size(36.dp), contentAlignment = Alignment.Center) {
        when {
            condition.contains("rain", true) -> {
                Icon(Icons.Rounded.Cloud, contentDescription = null, tint = Color(0xFF90A4AE), modifier = Modifier.size(28.dp).offset(y = (-4).dp))
                Icon(Icons.Rounded.WaterDrop, contentDescription = null, tint = Color(0xFF42A5F5), modifier = Modifier.size(12.dp).offset(x = (-6).dp, y = 10.dp))
                Icon(Icons.Rounded.WaterDrop, contentDescription = null, tint = Color(0xFF42A5F5), modifier = Modifier.size(12.dp).offset(x = 6.dp, y = 10.dp))
            }
            condition.contains("partly", true) || (condition.contains("cloud", true) && condition.contains("sun", true)) -> {
                Icon(Icons.Rounded.WbSunny, contentDescription = null, tint = Color(0xFFFFCA28), modifier = Modifier.size(24.dp).offset(x = 8.dp, y = (-6).dp))
                Icon(Icons.Rounded.Cloud, contentDescription = null, tint = Color(0xFF81D4FA), modifier = Modifier.size(26.dp).offset(x = (-4).dp, y = 4.dp))
            }
            condition.contains("cloud", true) -> {
                Icon(Icons.Rounded.Cloud, contentDescription = null, tint = Color(0xFFB0BEC5), modifier = Modifier.size(24.dp).offset(x = 6.dp, y = (-4).dp))
                Icon(Icons.Rounded.Cloud, contentDescription = null, tint = Color(0xFF81D4FA), modifier = Modifier.size(30.dp).offset(x = (-4).dp, y = 4.dp))
            }
            else -> {
                Icon(Icons.Rounded.WbSunny, contentDescription = null, tint = Color(0xFFFFCA28), modifier = Modifier.size(32.dp))
            }
        }
    }
}

@Composable
private fun WeatherAlertsBanner(alerts: List<WeatherAlertItemUi>) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        alerts.forEach { alert ->
            val isEmergency = alert.severity.equals("EMERGENCY", ignoreCase = true)
            val isWarning = alert.severity.equals("WARNING", ignoreCase = true)

            val bgColor = when {
                isEmergency -> Color(0xFFFFEBEE)
                isWarning -> Color(0xFFFFF8E1)
                else -> Color(0xFFE3F2FD)
            }
            val borderColor = when {
                isEmergency -> Color(0xFFEF5350)
                isWarning -> Color(0xFFFFCA28)
                else -> Color(0xFF90CAF9)
            }
            val textColor = when {
                isEmergency -> Color(0xFFC62828)
                isWarning -> Color(0xFFE65100)
                else -> Color(0xFF1565C0)
            }
            val icon = when {
                isEmergency -> Icons.Rounded.Warning
                isWarning -> Icons.Rounded.WarningAmber
                else -> Icons.Rounded.Info
            }

            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                color = bgColor,
                border = BorderStroke(1.dp, borderColor),
                shadowElevation = 2.dp
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(icon, contentDescription = null, tint = textColor, modifier = Modifier.size(20.dp))
                        Text(
                            text = alert.title.ifBlank { "${alert.alert_type} Warning" },
                            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = textColor),
                            modifier = Modifier.weight(1f)
                        )
                        Surface(
                            shape = RoundedCornerShape(8.dp),
                            color = textColor
                        ) {
                            Text(
                                text = alert.severity.uppercase(),
                                style = MaterialTheme.typography.labelSmall.copy(color = Color.White, fontWeight = FontWeight.ExtraBold, fontSize = 10.sp),
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }

                    if (alert.message.isNotBlank()) {
                        Text(
                            text = alert.message,
                            style = MaterialTheme.typography.bodyMedium.copy(color = textColor)
                        )
                    }

                    if (alert.farming_recommendation.isNotBlank()) {
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = Color.White.copy(alpha = 0.7f),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier.padding(10.dp),
                                verticalAlignment = Alignment.Top,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Icon(Icons.Rounded.CheckCircle, contentDescription = null, tint = Color(0xFF2E7D32), modifier = Modifier.size(16.dp))
                                Text(
                                    text = alert.farming_recommendation,
                                    style = MaterialTheme.typography.bodySmall.copy(color = Color(0xFF1B5E20), fontWeight = FontWeight.SemiBold)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun DisasterRiskCard(disasterRisk: DisasterRiskResponse) {
    val prediction = disasterRisk.predictions.firstOrNull() ?: return
    val alert = disasterRisk.alert
    val isCritical = prediction.risk_level.equals("CRITICAL", ignoreCase = true)
    val isHigh = prediction.risk_level.equals("HIGH", ignoreCase = true)
    val isMedium = prediction.risk_level.equals("MEDIUM", ignoreCase = true)
    var showDetails by remember { mutableStateOf(false) }

    val containerColor = when {
        isCritical -> Color(0xFFFFEBEE)
        isHigh -> Color(0xFFFFF3E0)
        isMedium -> Color(0xFFFFFDE7)
        else -> Color(0xFFE8F5E9)
    }
    val borderColor = when {
        isCritical -> Color(0xFFE53935)
        isHigh -> Color(0xFFFF9800)
        isMedium -> Color(0xFFFFD54F)
        else -> Color(0xFF81C784)
    }
    val primaryColor = when {
        isCritical -> Color(0xFFB71C1C)
        isHigh -> Color(0xFFE65100)
        isMedium -> Color(0xFFF57F17)
        else -> Color(0xFF2E7D32)
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = containerColor,
        border = BorderStroke(1.5.dp, borderColor),
        shadowElevation = if (isCritical || isHigh) 4.dp else 2.dp
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header Row: Badge & Horizon
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Icon(
                        imageVector = if (isCritical || isHigh) Icons.Rounded.Warning else Icons.Rounded.Info,
                        contentDescription = "Disaster Risk",
                        tint = primaryColor,
                        modifier = Modifier.size(24.dp)
                    )
                    Text(
                        text = "DISASTER RISK",
                        style = MaterialTheme.typography.labelMedium.copy(
                            fontWeight = FontWeight.Black,
                            color = primaryColor,
                            letterSpacing = 1.sp
                        )
                    )
                }

                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = primaryColor
                ) {
                    Text(
                        text = "${prediction.risk_level} (${prediction.risk_score.toInt()}%)",
                        style = MaterialTheme.typography.labelSmall.copy(
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.sp
                        ),
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    )
                }
            }

            // Hazard Type and Window
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = prediction.disaster_type,
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontWeight = FontWeight.ExtraBold,
                        color = Color(0xFF1B1B1B)
                    )
                )
                Text(
                    text = "Probability: ${(prediction.probability * 100).toInt()}% • Next 48 hours",
                    style = MaterialTheme.typography.bodySmall.copy(
                        fontWeight = FontWeight.Medium,
                        color = Color.DarkGray
                    )
                )
            }

            // Trigger Factors
            if (prediction.trigger_factors.isNotEmpty()) {
                Surface(
                    shape = RoundedCornerShape(14.dp),
                    color = Color.White.copy(alpha = 0.7f),
                    border = BorderStroke(0.8.dp, borderColor.copy(alpha = 0.5f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = "Observed Key Triggers:",
                            style = MaterialTheme.typography.labelSmall.copy(
                                fontWeight = FontWeight.Bold,
                                color = primaryColor
                            )
                        )
                        prediction.trigger_factors.forEach { factor ->
                            Row(
                                verticalAlignment = Alignment.Top,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Text("•", style = MaterialTheme.typography.bodySmall.copy(color = primaryColor, fontWeight = FontWeight.Bold))
                                Text(factor, style = MaterialTheme.typography.bodySmall.copy(color = Color(0xFF2E2E2E)))
                            }
                        }
                    }
                }
            }

            // Outbound Calling Notice (if active)
            if (alert.alert_status == "TRIGGERED") {
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = Color(0xFFEDE7F6),
                    border = BorderStroke(1.dp, Color(0xFFB39DDB)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Rounded.Phone,
                            contentDescription = "Calling Active",
                            tint = Color(0xFF512DA8),
                            modifier = Modifier.size(18.dp)
                        )
                        Text(
                            text = "Priority emergency voice alert initiated via Kisan Calling Agent.",
                            style = MaterialTheme.typography.bodySmall.copy(
                                color = Color(0xFF311B92),
                                fontWeight = FontWeight.SemiBold
                            )
                        )
                    }
                }
            }

            // Recommendations Section
            if (prediction.recommendations.isNotEmpty()) {
                if (showDetails) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            text = "Actionable Farm Precautions:",
                            style = MaterialTheme.typography.labelMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1B1B1B)
                            )
                        )
                        prediction.recommendations.forEach { rec ->
                            Row(
                                verticalAlignment = Alignment.Top,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Rounded.CheckCircle,
                                    contentDescription = null,
                                    tint = primaryColor,
                                    modifier = Modifier.size(14.dp).padding(top = 2.dp)
                                )
                                Text(
                                    text = rec,
                                    style = MaterialTheme.typography.bodySmall.copy(
                                        color = Color(0xFF212121),
                                        fontWeight = FontWeight.Normal
                                    )
                                )
                            }
                        }
                    }
                }

                // Action Button: Take Precautions
                Button(
                    onClick = { showDetails = !showDetails },
                    colors = ButtonDefaults.buttonColors(containerColor = primaryColor),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = if (showDetails) "Hide Precautions" else "Take Precautions",
                        style = MaterialTheme.typography.labelLarge.copy(
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    )
                }
            }
        }
    }
}

@Composable
private fun AgriculturalAdvisoryCard(advisory: AgriculturalAdvisoryResponse) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        shadowElevation = 3.dp,
        border = BorderStroke(1.dp, Color(0xFFECEFF1))
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            if (advisory.summary.isNotBlank()) {
                Text(
                    text = advisory.summary,
                    style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold, color = Color(0xFF37474F))
                )
            }

            if (advisory.irrigation_advice.isNotBlank()) {
                AdvisoryPillarRow(
                    icon = Icons.Rounded.WaterDrop,
                    iconTint = Color(0xFF0288D1),
                    title = "Irrigation Guidance",
                    content = advisory.irrigation_advice,
                    containerColor = Color(0xFFE1F5FE),
                    borderColor = Color(0xFFB3E5FC)
                )
            }

            if (advisory.spraying_advice.isNotBlank()) {
                AdvisoryPillarRow(
                    icon = Icons.Rounded.Spa,
                    iconTint = Color(0xFF689F38),
                    title = "Spraying Window",
                    content = advisory.spraying_advice,
                    containerColor = Color(0xFFF1F8E9),
                    borderColor = Color(0xFFDCEDC8)
                )
            }

            if (advisory.fieldwork_advice.isNotBlank()) {
                AdvisoryPillarRow(
                    icon = Icons.Rounded.Agriculture,
                    iconTint = Color(0xFFE65100),
                    title = "Field Operations & Harvest",
                    content = advisory.fieldwork_advice,
                    containerColor = Color(0xFFFFF3E0),
                    borderColor = Color(0xFFFFE0B2)
                )
            }

            if (advisory.assumptions.isNotEmpty()) {
                Text(
                    text = "Assumptions: ${advisory.assumptions.joinToString(" • ")}",
                    style = MaterialTheme.typography.labelSmall.copy(
                        color = Color.Gray,
                        fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                    ),
                    modifier = Modifier.padding(top = 2.dp)
                )
            }
        }
    }
}

@Composable
private fun AdvisoryPillarRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    iconTint: Color,
    title: String,
    content: String,
    containerColor: Color,
    borderColor: Color
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        color = containerColor,
        border = BorderStroke(1.dp, borderColor)
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(icon, contentDescription = null, tint = iconTint, modifier = Modifier.size(18.dp))
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.Bold, color = iconTint)
                )
            }
            Text(
                text = content,
                style = MaterialTheme.typography.bodySmall.copy(color = Color(0xFF263238), lineHeight = 18.sp)
            )
        }
    }
}

@Composable
private fun FieldGuidanceCard(weatherData: DisplayWeatherData) {
    val guidance = remember(weatherData) { generateFieldGuidance(weatherData) }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        shadowElevation = 3.dp,
        border = BorderStroke(1.dp, Color(0xFFECEFF1))
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    modifier = Modifier.weight(1f),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .background(guidance.badgeColor, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = guidance.icon,
                            contentDescription = null,
                            tint = guidance.badgeTextColor,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                    Column {
                        Text(
                            text = guidance.headline,
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1B1B1B)
                            )
                        )
                        Text(
                            text = "Condition: ${weatherData.description.replaceFirstChar { it.uppercase() }}",
                            style = MaterialTheme.typography.bodySmall.copy(
                                color = Color.Gray
                            )
                        )
                    }
                }
            }

            Surface(
                shape = RoundedCornerShape(12.dp),
                color = guidance.badgeColor
            ) {
                Text(
                    text = guidance.badge,
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontWeight = FontWeight.Black,
                        color = guidance.badgeTextColor
                    ),
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                )
            }

            Text(
                text = guidance.summary,
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = Color(0xFF37474F),
                    lineHeight = 20.sp
                )
            )

            if (guidance.notSuitableFor.isNotEmpty()) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    color = Color(0xFFFFF5F5),
                    border = BorderStroke(1.dp, Color(0xFFFFCDD2))
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Rounded.Cancel,
                                contentDescription = null,
                                tint = Color(0xFFD32F2F),
                                modifier = Modifier.size(18.dp)
                            )
                            Text(
                                text = "Not Suitable For Today:",
                                style = MaterialTheme.typography.labelLarge.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFFC62828)
                                )
                            )
                        }
                        guidance.notSuitableFor.forEach { item ->
                            Row(
                                modifier = Modifier.padding(start = 6.dp),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.Top
                            ) {
                                Text(
                                    text = "•",
                                    color = Color(0xFFD32F2F),
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp
                                )
                                Text(
                                    text = item,
                                    style = MaterialTheme.typography.bodySmall.copy(
                                        color = Color(0xFF424242)
                                    )
                                )
                            }
                        }
                    }
                }
            }

            if (guidance.suitableFor.isNotEmpty()) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    color = Color(0xFFF1F8E9),
                    border = BorderStroke(1.dp, Color(0xFFC8E6C9))
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Rounded.CheckCircle,
                                contentDescription = null,
                                tint = Color(0xFF2E7D32),
                                modifier = Modifier.size(18.dp)
                            )
                            Text(
                                text = "Recommended & Suitable:",
                                style = MaterialTheme.typography.labelLarge.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF1B5E20)
                                )
                            )
                        }
                        guidance.suitableFor.forEach { item ->
                            Row(
                                modifier = Modifier.padding(start = 6.dp),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.Top
                            ) {
                                Text(
                                    text = "•",
                                    color = Color(0xFF2E7D32),
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp
                                )
                                Text(
                                    text = item,
                                    style = MaterialTheme.typography.bodySmall.copy(
                                        color = Color(0xFF2E7D32)
                                    )
                                )
                            }
                        }
                    }
                }
            }

            if (guidance.precautions.isNotEmpty()) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    color = Color(0xFFF0F7FF),
                    border = BorderStroke(1.dp, Color(0xFFBBDEFB))
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Rounded.Info,
                                contentDescription = null,
                                tint = Color(0xFF1976D2),
                                modifier = Modifier.size(18.dp)
                            )
                            Text(
                                text = "Key Precautions:",
                                style = MaterialTheme.typography.labelLarge.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF0D47A1)
                                )
                            )
                        }
                        guidance.precautions.forEach { item ->
                            Row(
                                modifier = Modifier.padding(start = 6.dp),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.Top
                            ) {
                                Text(
                                    text = "•",
                                    color = Color(0xFF1976D2),
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp
                                )
                                Text(
                                    text = item,
                                    style = MaterialTheme.typography.bodySmall.copy(
                                        color = Color(0xFF1565C0)
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

data class FieldGuidance(
    val headline: String,
    val summary: String,
    val badge: String,
    val badgeColor: Color,
    val badgeTextColor: Color,
    val icon: androidx.compose.ui.graphics.vector.ImageVector,
    val notSuitableFor: List<String>,
    val suitableFor: List<String>,
    val precautions: List<String>
)

fun generateFieldGuidance(weather: DisplayWeatherData): FieldGuidance {
    val desc = weather.description.lowercase().trim()
    val temp = weather.temperature
    val humidity = weather.humidity
    val wind = weather.windSpeed

    return when {
        desc.contains("thunder") || desc.contains("storm") || desc.contains("hail") || desc.contains("squall") || desc.contains("lightning") -> {
            FieldGuidance(
                headline = "Thunderstorm & Severe Weather Alert",
                summary = "Severe storm conditions active. High risk of crop lodging, physical damage, and field safety hazards.",
                badge = "DANGER / PAUSE OPERATIONS",
                badgeColor = Color(0xFFFFEBEE),
                badgeTextColor = Color(0xFFC62828),
                icon = Icons.Rounded.Thunderstorm,
                notSuitableFor = listOf(
                    "All open-field manual & tractor operations",
                    "Chemical spraying or top-dress fertilization",
                    "Working with metallic machinery or standing under isolated trees"
                ),
                suitableFor = listOf(
                    "Sheltering farm livestock & equipment",
                    "Inspecting indoor grain storage & seeds"
                ),
                precautions = listOf(
                    "Provide physical staking for tall crops (banana, tomato, sugarcane)",
                    "Secure greenhouse panels, polytunnels, and nursery shade netting"
                )
            )
        }
        desc.contains("heavy rain") || desc.contains("torrential") || desc.contains("heavy shower") || desc.contains("dense drizzle") -> {
            FieldGuidance(
                headline = "Heavy Rain Advisory",
                summary = "Heavy rainfall occurring. Soil saturation is critical with severe runoff and leaching risks.",
                badge = "HEAVY RAIN / RESTRICTED",
                badgeColor = Color(0xFFFFEBEE),
                badgeTextColor = Color(0xFFC62828),
                icon = Icons.Rounded.BeachAccess,
                notSuitableFor = listOf(
                    "Chemical pesticide & fertilizer spraying (immediate wash-off)",
                    "Grain harvesting and open-air drying",
                    "Heavy tractor tilling (causes severe soil compaction & tractor stuck)",
                    "Nitrogen fertilizer broadcasting (causes leaching into groundwater)"
                ),
                suitableFor = listOf(
                    "Rainwater harvesting in farm ponds and recharge pits",
                    "Checking nursery drainage outlets"
                ),
                precautions = listOf(
                    "Clear field drainage channels immediately to prevent waterlogging & root rot",
                    "Inspect field bunds to avoid breach and topsoil erosion"
                )
            )
        }
        desc.contains("rain") || desc.contains("drizzle") || desc.contains("shower") || desc.contains("precipitation") || desc.contains("wet") -> {
            FieldGuidance(
                headline = "Rainy Conditions Guidance",
                summary = "Wet weather and rain showers present. Topsoil is damp with high ambient moisture.",
                badge = "RAINY / SPRAYING DELAYED",
                badgeColor = Color(0xFFE3F2FD),
                badgeTextColor = Color(0xFF1565C0),
                icon = Icons.Rounded.BeachAccess,
                notSuitableFor = listOf(
                    "Foliar pesticide & fungicide spraying (wash-off risk)",
                    "Harvesting mature grains or fodder hay",
                    "Applying dry urea or soluble chemical fertilizers"
                ),
                suitableFor = listOf(
                    "Transplanting paddy and rainfed Kharif seedlings",
                    "Planting tree saplings & agroforestry borders",
                    "Maintaining farm drainage furrows"
                ),
                precautions = listOf(
                    "Allow foliage to dry for at least 24 hours before scheduling foliar sprays",
                    "Ensure nursery beds have raised slopes to drain excess water"
                )
            )
        }
        desc.contains("wind") || desc.contains("gale") || desc.contains("breeze") || wind >= 18.0 -> {
            FieldGuidance(
                headline = "High Wind Warning",
                summary = "Elevated wind speeds (${wind.toInt()} km/h). Air turbulence causes chemical drift and uneven droplet deposition.",
                badge = "HIGH WIND / NO SPRAY",
                badgeColor = Color(0xFFFFF3E0),
                badgeTextColor = Color(0xFFE65100),
                icon = Icons.Rounded.Air,
                notSuitableFor = listOf(
                    "Foliar spraying & dusting (causes severe drift to non-target crops)",
                    "Crop residue burning (extreme wildfire hazard)",
                    "Sprinkler irrigation (uneven distribution patterns)"
                ),
                suitableFor = listOf(
                    "Soil plowing and manual weeding at ground level",
                    "Repairing drip irrigation lines and ground pipes"
                ),
                precautions = listOf(
                    "Provide earthing-up and staking for vulnerable standing crops",
                    "Check and tie down polyhouse plastic sheets & nursery netting"
                )
            )
        }
        desc.contains("heat") || desc.contains("hot") || temp >= 35 -> {
            FieldGuidance(
                headline = "High Heat & Evaporation Stress",
                summary = "High temperature ($temp°C). Rapid evapotranspiration stress on soil and plant tissues.",
                badge = "HEAT STRESS / IRRIGATE",
                badgeColor = Color(0xFFFFF3E0),
                badgeTextColor = Color(0xFFE65100),
                icon = Icons.Rounded.WbSunny,
                notSuitableFor = listOf(
                    "Midday chemical spraying (rapid evaporation & chemical leaf scorching)",
                    "Midday seedling transplanting (severe transplant shock)",
                    "Heavy physical fieldwork during peak noon hours"
                ),
                suitableFor = listOf(
                    "Early morning or late evening drip irrigation",
                    "Applying organic straw mulching to conserve root moisture",
                    "Deep summer plowing (soil solarization for pest control)"
                ),
                precautions = listOf(
                    "Irrigate in split doses during cooler morning/evening hours",
                    "Provide shade covers and clean water for farm livestock"
                )
            )
        }
        desc.contains("cold") || desc.contains("frost") || desc.contains("snow") || desc.contains("freeze") || desc.contains("ice") || temp <= 10 -> {
            FieldGuidance(
                headline = "Cold Wave & Frost Advisory",
                summary = "Low temperature ($temp°C). Horticultural and vegetable crops are at risk of frost injury.",
                badge = "FROST RISK / PROTECT CROPS",
                badgeColor = Color(0xFFE1F5FE),
                badgeTextColor = Color(0xFF0277BD),
                icon = Icons.Rounded.AcUnit,
                notSuitableFor = listOf(
                    "Nitrogen fertilizer application (spurs tender growth susceptible to frost)",
                    "Heavy cold water flooding late at night",
                    "Exposing tender nursery saplings without cover"
                ),
                suitableFor = listOf(
                    "Light evening irrigation (raises soil thermal mass against frost)",
                    "Covering vegetable beds with straw/plastic thatch",
                    "Pruning dormant orchard trees"
                ),
                precautions = listOf(
                    "Generate light smoke on orchard windward boundaries during freezing nights",
                    "Harvest mature vegetable produce early before night frost"
                )
            )
        }
        desc.contains("fog") || desc.contains("mist") || desc.contains("haze") || humidity >= 80 -> {
            FieldGuidance(
                headline = "Fog & High Humidity Advisory",
                summary = "High relative humidity ($humidity%). Prolonged leaf wetness promotes rapid fungal & bacterial pathogen sporulation.",
                badge = "HIGH HUMIDITY / DISEASE WATCH",
                badgeColor = Color(0xFFEDE7F6),
                badgeTextColor = Color(0xFF512DA8),
                icon = Icons.Rounded.WaterDrop,
                notSuitableFor = listOf(
                    "Overhead sprinkler irrigation (further prolongs canopy wetness)",
                    "Early morning spraying while heavy dew is dripping",
                    "Dense storage of damp harvested produce"
                ),
                suitableFor = listOf(
                    "Scouting crops for fungal leaf spots, blights, and powdery mildew",
                    "Applying prophylactic bio-fungicides (Trichoderma / Pseudomonas)",
                    "Pruning lower diseased leaves to improve inter-row ventilation"
                ),
                precautions = listOf(
                    "Scout undersides of leaves and crop crowns daily for early disease signs",
                    "Allow morning dew to completely evaporate before starting harvest"
                )
            )
        }
        desc.contains("cloud") || desc.contains("overcast") -> {
            FieldGuidance(
                headline = "Cloudy & Overcast Weather",
                summary = "Diffused sunlight and mild transpiration. Favorable conditions for root establishment.",
                badge = "MILD / GOOD FOR PLANTING",
                badgeColor = Color(0xFFF1F8E9),
                badgeTextColor = Color(0xFF33691E),
                icon = Icons.Rounded.WbCloudy,
                notSuitableFor = listOf(
                    "Sun-drying harvested grains and seeds (slow drying & mold risk)",
                    "Solar soil disinfestation"
                ),
                suitableFor = listOf(
                    "Transplanting seedlings with minimal wilting shock",
                    "Inter-cultivation, manual weeding, and hoeing",
                    "Fertilizer side-dressing and incorporation"
                ),
                precautions = listOf(
                    "Monitor sucking pests (aphids, jassids) which proliferate under overcast skies",
                    "Maintain proper row spacing for light penetration"
                )
            )
        }
        desc.contains("clear") || desc.contains("sun") || desc.contains("bright") -> {
            FieldGuidance(
                headline = "Optimal Sunny Conditions",
                summary = "Clear skies with abundant solar radiation. Ideal day for chemical protection and harvesting.",
                badge = "OPTIMAL / IDEAL FOR SPRAYING",
                badgeColor = Color(0xFFE8F5E9),
                badgeTextColor = Color(0xFF1B5E20),
                icon = Icons.Rounded.WbSunny,
                notSuitableFor = listOf(
                    "Broadcasting uncovered volatile nitrogen fertilizers in peak sunlight",
                    "Flood irrigation during hot noon hours"
                ),
                suitableFor = listOf(
                    "Foliar pesticide, herbicide, and micronutrient spraying",
                    "Harvesting and sun-drying agricultural produce",
                    "Tractor plowing, harrowing, and field bed preparation"
                ),
                precautions = listOf(
                    "Schedule field irrigation in the early morning to minimize evaporation loss",
                    "Inspect soil moisture depth before scheduling next irrigation"
                )
            )
        }
        else -> {
            FieldGuidance(
                headline = "General Field Operations Guidance",
                summary = "Stable seasonal weather conditions. Suitable for routine farm maintenance and crop care.",
                badge = "FAVORABLE FOR FARM WORK",
                badgeColor = Color(0xFFE8F5E9),
                badgeTextColor = Color(0xFF1B5E20),
                icon = Icons.Rounded.Grass,
                notSuitableFor = listOf(
                    "Over-irrigating without assessing soil moisture level"
                ),
                suitableFor = listOf(
                    "Routine crop scouting and pest monitoring",
                    "Weed removal and intercultural operations",
                    "Scheduled nutrient management and irrigation"
                ),
                precautions = listOf(
                    "Maintain clear irrigation and drainage channels across the field",
                    "Keep farm tools clean and disinfected between plots"
                )
            )
        }
    }
}

// Data Handling
@Composable
private fun WeatherLoadingState() {
    NeoCard {
        Column(
            modifier = Modifier.fillMaxWidth().padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            CircularProgressIndicator(color = Color(0xFF2E7D32))
            Text("Loading live weather", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold))
            Text("Fetching your field conditions...", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun WeatherErrorState(message: String, onRetry: () -> Unit) {
    NeoCard(containerColor = MaterialTheme.colorScheme.errorContainer) {
        Column(modifier = Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Icon(Icons.Rounded.ErrorOutline, contentDescription = null, tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(32.dp))
            Text("Weather unavailable", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
            Text(message, style = MaterialTheme.typography.bodyMedium)
            PremiumButton(text = "Try Again", onClick = onRetry)
        }
    }
}

suspend fun fetchWeatherFromLocation(
    context: android.content.Context,
    onResult: (DisplayWeatherData?, String?) -> Unit
) {
    try {
        val location = getDeviceLocation(context)
        if (location == null) {
            WeatherSnapshotStore.latestError = "Could not get device location. Please enable GPS and try again."
            onResult(null, "Could not get device location. Please enable GPS and try again.")
            return
        }

        val appLanguage = LanguagePreferences.getSelectedLanguage(context) ?: "en"
        val farmFusionApi = com.example.farmfusionapp.network.RetrofitInstance.farmFusionApi
        val latitude = location.first
        val longitude = location.second
        val response = farmFusionApi.getCurrentWeather(latitude, longitude, language = appLanguage)

        if (response.isSuccessful && response.body() != null) {
            val body = response.body()!!
            val backendData = body.data
            if (body.success && backendData != null) {
                val backendLocation = (backendData.location ?: backendData.location_name ?: "").trim()
                val currentStableCity = WeatherSnapshotStore.latestWeather?.city ?: LocationSnapshotStore.latestCity
                val resolvedBroadCity = getCityFromLocation(context, latitude, longitude, appLanguage)
                val city = when {
                    !resolvedBroadCity.isNullOrBlank() -> resolvedBroadCity
                    backendLocation.isNotEmpty() && !backendLocation.equals("Unknown", ignoreCase = true) -> backendLocation
                    !currentStableCity.isNullOrBlank() -> currentStableCity
                    else -> "Location unavailable"
                }

                // Fetch real 7-day forecast from backend
                val realForecastList = mutableListOf<DailyForecast>()
                try {
                    val forecastResponse = farmFusionApi.getWeatherForecast(latitude, longitude, days = 7, language = appLanguage)
                    if (forecastResponse.isSuccessful && forecastResponse.body() != null) {
                        val fBody = forecastResponse.body()!!
                        val dailyList = fBody.data?.forecast ?: emptyList()
                        dailyList.forEachIndexed { index, item ->
                            val dayLabel = when (index) {
                                0 -> "Today"
                                1 -> "Tomorrow"
                                else -> {
                                    try {
                                        java.time.LocalDate.parse(item.date).dayOfWeek.name.take(3).lowercase().replaceFirstChar { it.uppercase() }
                                    } catch (e: Exception) {
                                        item.date
                                    }
                                }
                            }
                            val high = (item.temperature_max_c ?: (item.temperature_c + 2)).toInt()
                            val low = (item.temperature_min_c ?: (item.temperature_c - 2)).toInt()
                            val conditionText = item.weather.ifBlank { "Clear" }
                            val rainProb = item.rain_chance.toInt()
                            val precipMm = item.precipitation_mm ?: 0.0
                            realForecastList.add(DailyForecast(dayLabel, high, low, conditionText, rainProbability = rainProb, precipitationMm = precipMm))
                        }
                    }
                } catch (fe: Exception) {
                    // Fallback to empty forecast list if network glitch occurs during forecast leg
                }

                // Fetch real weather alerts from backend
                val alertList = mutableListOf<WeatherAlertItemUi>()
                try {
                    val alertsResponse = farmFusionApi.getWeatherAlerts(latitude, longitude, days = 7, language = appLanguage)
                    if (alertsResponse.isSuccessful && alertsResponse.body() != null) {
                        alertList.addAll(alertsResponse.body()!!.alerts)
                    }
                } catch (ae: Exception) {
                    // Fallback: alerts remain empty, does not break current weather
                }

                // Fetch structured agricultural advisory from backend
                var advisoryObj: AgriculturalAdvisoryResponse? = null
                try {
                    val advResponse = farmFusionApi.getAgriculturalAdvisory(latitude, longitude, language = appLanguage)
                    if (advResponse.isSuccessful && advResponse.body() != null) {
                        advisoryObj = advResponse.body()
                    }
                } catch (ave: Exception) {
                    // Fallback: advisory remains null, does not break current weather
                }

                // Fetch AI Disaster Risk & Early Warning from backend
                var disasterRiskObj: DisasterRiskResponse? = null
                try {
                    val disResponse = farmFusionApi.getDisasterRisk(
                        DisasterRiskRequest(
                            lat = latitude,
                            lon = longitude,
                            location_name = city,
                            language = appLanguage
                        )
                    )
                    if (disResponse.isSuccessful && disResponse.body() != null) {
                        disasterRiskObj = disResponse.body()
                    }
                } catch (de: Exception) {
                    // Fallback: disasterRisk remains null, does not break current weather
                }

                val weatherDesc = (backendData.weather ?: backendData.condition ?: "").trim()
                val windSpeed = if (backendData.wind_speed_ms > 0.0) {
                    backendData.wind_speed_ms
                } else {
                    (backendData.wind_speed_kmh ?: 0.0) / 3.6
                }

                val data = DisplayWeatherData(
                    temperature = backendData.temperature_c.toInt(),
                    feelsLike = backendData.feels_like_c.toInt(),
                    description = weatherDesc.ifBlank { "Clear" },
                    humidity = backendData.humidity_percent,
                    windSpeed = windSpeed,
                    city = city,
                    advice = backendData.farming_advice ?: "Good weather conditions for farm work",
                    timestamp = backendData.timestamp,
                    forecast = realForecastList,
                    alerts = alertList,
                    advisory = advisoryObj,
                    disasterRisk = disasterRiskObj
                )
                WeatherSnapshotStore.latestWeather = data
                WeatherSnapshotStore.latestLanguage = appLanguage
                WeatherSnapshotStore.latestError = null
                WeatherSnapshotStore.lastUpdatedAt = System.currentTimeMillis()
                onResult(data, null)
            } else {
                WeatherSnapshotStore.latestError = "Failed to get weather data."
                onResult(null, "Failed to get weather data.")
            }
        } else {
            val message = if (response.code() == 503) {
                "Real weather service is unavailable right now. Please try again in a moment."
            } else {
                "Backend unreachable. Error: ${response.code()}"
            }
            WeatherSnapshotStore.latestError = message
            onResult(null, message)
        }
    } catch (e: Exception) {
        WeatherSnapshotStore.latestError = "Network Error: ${e.message}"
        onResult(null, "Network Error: ${e.message}")
    }
}