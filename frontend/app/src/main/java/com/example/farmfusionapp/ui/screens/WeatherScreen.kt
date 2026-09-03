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
    val strings = LocalStrings.current
    val currentLang = LocalAppLanguage.current
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
                        text = AppLocalizer.localizeWeatherPhrase("weather", currentLang),
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
                                WeatherStatCard(strings.weather.humidity, "${weatherData!!.humidity}%", Icons.Rounded.WaterDrop, Modifier.weight(1f))
                                WeatherStatCard(strings.weather.windSpeed, "${weatherData!!.windSpeed.toInt()} km/h", Icons.Rounded.Air, Modifier.weight(1f))
                            }
                        }

                        // 4. Rich Advisory or Field Guidance
                        if (weatherData!!.advisory != null) {
                            item {
                                Column(modifier = Modifier.padding(start = 24.dp, end = 24.dp, top = 8.dp, bottom = 4.dp)) {
                                    Text(
                                        text = strings.weather.agriculturalAdvisory,
                                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                                    )
                                    Text(
                                        text = AppLocalizer.localizeWeatherPhrase("agronomic guidance sub", currentLang),
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
                                        text = strings.weather.agriculturalAdvisory,
                                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                                    )
                                    Text(
                                        text = AppLocalizer.localizeWeatherPhrase("farm operations sub", currentLang),
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
                                    text = strings.weather.forecast7Days,
                                    style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                                )
                                Text(
                                    text = AppLocalizer.localizeWeatherPhrase("7day forecast sub", currentLang),
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
    val currentLang = LocalAppLanguage.current
    val strings = LocalStrings.current
    val localizedCity = remember(weatherData.city, currentLang) {
        AppLocalizer.localizeCity(weatherData.city, currentLang)
    }
    val localizedCondition = remember(weatherData.description, currentLang) {
        AppLocalizer.localizeWeatherCondition(weatherData.description, currentLang)
    }

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
                                text = localizedCity,
                                style = MaterialTheme.typography.titleMedium.copy(color = Color.White, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                            )
                        }
                        val timeLabel = remember(weatherData.timestamp, strings) {
                            if (!weatherData.timestamp.isNullOrBlank()) {
                                try {
                                    if (weatherData.timestamp.contains("T")) {
                                        "${strings.weather.weatherForecast} • " + weatherData.timestamp.substringAfter("T").take(5)
                                    } else {
                                        "${strings.weather.weatherForecast} • " + weatherData.timestamp
                                    }
                                } catch (e: Exception) {
                                    strings.weather.weatherForecast
                                }
                            } else {
                                strings.weather.weatherForecast
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
                            text = localizedCondition.ifBlank { weatherData.description.replaceFirstChar { it.uppercase() } },
                            style = MaterialTheme.typography.titleMedium.copy(
                                color = Color.White,
                                fontWeight = FontWeight.Bold,
                                fontSize = 18.sp
                            )
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = "${strings.weather.feelsLike} ${weatherData.feelsLike ?: weatherData.temperature}°C",
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
    val currentLang = LocalAppLanguage.current
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
            Text(AppLocalizer.localizeDay(forecast.day, currentLang), style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold, color = Color.DarkGray))

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
private fun AgriculturalAdvisoryCard(advisory: AgriculturalAdvisoryResponse) {
    val currentLang = LocalAppLanguage.current
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
                    title = AppLocalizer.localizeWeatherPhrase("irrigation guidance", currentLang),
                    content = advisory.irrigation_advice,
                    containerColor = Color(0xFFE1F5FE),
                    borderColor = Color(0xFFB3E5FC)
                )
            }

            if (advisory.spraying_advice.isNotBlank()) {
                AdvisoryPillarRow(
                    icon = Icons.Rounded.Spa,
                    iconTint = Color(0xFF689F38),
                    title = AppLocalizer.localizeWeatherPhrase("spraying window", currentLang),
                    content = advisory.spraying_advice,
                    containerColor = Color(0xFFF1F8E9),
                    borderColor = Color(0xFFDCEDC8)
                )
            }

            if (advisory.fieldwork_advice.isNotBlank()) {
                AdvisoryPillarRow(
                    icon = Icons.Rounded.Agriculture,
                    iconTint = Color(0xFFE65100),
                    title = AppLocalizer.localizeWeatherPhrase("field operations harvest", currentLang),
                    content = advisory.fieldwork_advice,
                    containerColor = Color(0xFFFFF3E0),
                    borderColor = Color(0xFFFFE0B2)
                )
            }

            if (advisory.assumptions.isNotEmpty()) {
                val localizedAssumptions = advisory.assumptions.map { AppLocalizer.localizeWeatherPhrase(it, currentLang) }
                Text(
                    text = "${AppLocalizer.localizeWeatherPhrase("assumptions", currentLang)} ${localizedAssumptions.joinToString(" • ")}",
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
    val currentLang = LocalAppLanguage.current
    val guidance = remember(weatherData, currentLang) { generateFieldGuidance(weatherData, currentLang) }

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
                            text = "${AppLocalizer.localizeWeatherPhrase("condition label", currentLang)} ${AppLocalizer.localizeWeatherCondition(weatherData.description, currentLang)}",
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
                                text = AppLocalizer.localizeWeatherPhrase("not suitable today", currentLang),
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
                                text = AppLocalizer.localizeWeatherPhrase("recommended suitable", currentLang),
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
                                text = AppLocalizer.localizeWeatherPhrase("key precautions", currentLang),
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

fun generateFieldGuidance(weather: DisplayWeatherData, langCode: String = "hi"): FieldGuidance {
    val desc = weather.description.lowercase().trim()
    val temp = weather.temperature
    val humidity = weather.humidity
    val wind = weather.windSpeed
    val lang = if (langCode == "od") "or" else langCode

    fun t(
        en: String, hi: String, gu: String, mr: String, pa: String, bn: String,
        ta: String, te: String, kn: String, ml: String, or: String, asStr: String, ur: String, mai: String
    ): String = when (lang) {
        "gu" -> gu
        "mr" -> mr
        "pa" -> pa
        "bn" -> bn
        "ta" -> ta
        "te" -> te
        "kn" -> kn
        "ml" -> ml
        "or" -> or
        "as" -> asStr
        "ur" -> ur
        "mai" -> mai
        "en" -> en
        else -> hi
    }

    return when {
        desc.contains("thunder") || desc.contains("storm") || desc.contains("hail") || desc.contains("squall") || desc.contains("lightning") -> {
            FieldGuidance(
                headline = t(
                    "Thunderstorm & Severe Weather Alert", "आंधी-तूफान एवं तेज मौसम चेतावनी", "વાવાઝોડું અને ભારે પવનની ચેતવણી",
                    "वादळी वारे आणि जोरदार पावसाचा इशारा", "ਤੂਫਾਨ ਅਤੇ ਖਰਾਬ ਮੌਸਮ ਦੀ ਚੇਤਾਵਨੀ", "বজ্রবিদ্যুৎসহ ঝড়ের সতর্কতা",
                    "இடி மின்னல் மற்றும் புயல் எச்சரிக்கை", "ఉరుములతో కూడిన తుఫాను హెచ్చరిక", "ಗುಡುಗು ಮಿಂಚಿನ ಬಿರುಗಾಳಿ ಎಚ್ಚರಿಕೆ",
                    "ഇടിമിന്നലോടുകൂടിയ കൊടുങ്കാറ്റ് മുന്നറിയിപ്പ്", "ଘଡ଼ଘଡ଼ି ଏବଂ ଝଡ଼ବର୍ଷା ସତର୍କତା", "ধুমুহা আৰু বজ্ৰপাতৰ সতৰ্কবাৰ্তা",
                    "گرج چمک اور تیز طوفان کا الرٹ", "आंधी-तूफान आ ठनका केर चेतावनी"
                ),
                summary = t(
                    "Severe storm conditions active. High risk of crop lodging, physical damage, and field safety hazards.",
                    "खेत में तेज आंधी और तूफान का खतरा है। फसलों के गिरने और नुकसान की आशंका अधिक है।",
                    "ખેતરમાં ભારે વાવાઝોડાનું જોખમ છે. પાક પડી જવાની અને નુકસાનની શક્યતા વધુ છે.",
                    "शेतात जोरदार वादळाचा धोका आहे. पिके आडवी होण्याचा आणि नुकसानीचा संभव आहे.",
                    "ਖੇਤ ਵਿੱਚ ਤੇਜ਼ ਤੂਫਾਨ ਦਾ ਖਤਰਾ ਹੈ। ਫਸਲਾਂ ਦੇ ਡਿੱਗਣ ਦਾ ਵੱਧ ਖਦਸ਼ਾ ਹੈ।",
                    "মাঠে ভারী ঝড়ের সম্ভাবনা রয়েছে। ফসল হেলে পড়ার ঝুঁকি অত্যন্ত বেশি।",
                    "வயலில் கடுமையான புயல் அபாயம் உள்ளது. பயிர்கள் சாய்ந்து சேதமடையும் வாய்ப்பு அதிகம்.",
                    "పొలంలో తీవ్రమైన తుఫాను ప్రమాదం ఉంది. పంటలు పడిపోయే అవకాశం ఎక్కువ.",
                    "ಹೊಲದಲ್ಲಿ ಭಾರೀ ಬಿರುಗಾಳಿ ಅಪಾಯವಿದೆ. ಬೆಳೆಗಳು ಉರುಳಿಬೀಳುವ ಸಾಧ್ಯತೆ ಹೆಚ್ಚು.",
                    "പാടത്ത് കനത്ത കൊടുങ്കാറ്റ് ഭീഷണിയുണ്ട്. വിളകൾ നിലംപൊത്താൻ സാധ്യതയുണ്ട്.",
                    "ଜମିରେ ପ୍ରବଳ ଝଡ଼ର ଆଶଙ୍କା ଅଛି। ଫସଲ ନଷ୍ଟ ହେବାର ସମ୍ଭାବନା ଅଧିକ।",
                    "পথাৰত ধুমুহাৰ সম্ভাৱনা আছে। শস্য মাটিত বাগৰি পৰাৰ আশংকা বেছি।",
                    "کھیت میں شدید طوفان کا خطرہ ہے۔ فصلیں گرنے کا امکان زیادہ ہے۔",
                    "खेत मे तेज आंधी केर खतरा अछि। फसल खसबय केर आशंका बेसी अछि।"
                ),
                badge = t(
                    "DANGER / PAUSE OPERATIONS", "खतरा / खेत कार्य रोकें", "જોખમ / ખેતી કામ મુલતવી રાખો",
                    "धोका / शेती कामे थांबवा", "ਖਤਰਾ / ਖੇਤ ਕੰਮ ਰੋਕੋ", "বিপদ / মাঠের কাজ বন্ধ রাখুন",
                    "அபாயம் / பணிகளை நிறுத்துங்கள்", "ప్రమాదం / పనులు నిలిపివేయండి", "ಅಪಾಯ / ಕೆಲಸಗಳನ್ನು ನಿಲ್ಲಿಸಿ",
                    "അപകടം / പണികൾ നിർത്തുക", "ବିପଦ / କାର୍ଯ୍ୟ ବନ୍ଦ ରଖନ୍ତୁ", "বিপদ / কাম স্থগিত ৰাখক",
                    "خطرہ / کام روک دیں", "खतरा / खेत काज रोकि दिअ"
                ),
                badgeColor = Color(0xFFFFEBEE),
                badgeTextColor = Color(0xFFC62828),
                icon = Icons.Rounded.Thunderstorm,
                notSuitableFor = listOf(
                    t("All open-field manual & tractor operations", "खुले खेत में मजदूरी व ट्रैक्टर का काम", "ખુલ્લા ખેતમાં મજૂરી અને ટ્રેક્ટરનું કામ", "उघड्या शेतात मजुरी व ट्रॅक्टरची कामे", "ਖੁੱਲ੍ਹੇ ਖੇਤ ਵਿੱਚ ਟਰੈਕਟਰ ਦਾ ਕੰਮ", "খোলা মাঠে ট্রাক্টরের কাজ ও শ্রম", "திறந்தவெளி களப்பணிகள்", "బహిరంగ పొలం పనులు & ట్రాక్టర్ పనులు", "ಬಯಲು ಹೊಲದ ಕೆಲಸಗಳು", "തുറസ്സായ പാടത്തെ പണികൾ", "ଖୋଲା ଜମିରେ ଟ୍ରାକ୍ଟର କାମ", "পথাৰত ট্ৰেক্টৰৰ কাম", "کھلے کھیت میں ٹریکٹر کا کام", "खुल्ला खेत मे मजदूरी आ ट्रैक्टर केर काज"),
                    t("Chemical spraying or top-dress fertilization", "कीटनाशक छिड़काव व खाद डालना", "દવા છંટકાવ અને ખાતર આપવું", "कीटकनाशक फवारणी व खत टाकणे", "ਸਪਰੇਅ ਅਤੇ ਖਾਦ ਪਾਉਣਾ", "কীটনাশক স্প্রে ও সার প্রয়োগ", "மருந்து தெளித்தல் & உரமிடுதல்", "పిచికారీ & ఎరువులు వేయడం", "ಸಿಂಪಡಣೆ ಮತ್ತು ಗೊಬ್ಬರ ಹಾಕುವುದು", "മരുന്ന് തളിക്കലും വളപ്രയോഗവും", "ଔଷଧ ସ୍ପ୍ରେ ଏବଂ ଖତ ଦେବା", "কীটনাশক স্প্ৰে' আৰু সাৰ প্ৰয়োগ", "اسپرے اور کھاد ڈالنا", "कीटनाशक छिड़काव आ खाद देब")
                ),
                suitableFor = listOf(
                    t("Sheltering farm livestock & equipment", "पशुओं व कृषि उपकरणों को सुरक्षित स्थान पर रखें", "પશુઓ અને સાધનોને સલામત સ્થળે રાખો", "जनावरे व अवजारे सुरक्षित ठिकाणी ठेवा", "ਪਸ਼ੂਆਂ ਅਤੇ ਸੰਦਾਂ ਨੂੰ ਸੁਰੱਖਿਅਤ ਥਾਂ ਰੱਖੋ", "গবাদি পশু ও কৃষি সরঞ্জাম নিরাপদ স্থানে রাখুন", "கால்நடைகள் மற்றும் கருவிகளைப் பாதுகாக்கவும்", "పశువులు మరియు పనిముట్లను రక్షించండి", "ಜಾನುವಾರು ಮತ್ತು ಉಪಕರಣಗಳನ್ನು ರಕ್ಷಿಸಿ", "കന്നുകാലികളെയും ഉപകരണങ്ങളെയും സംരക്ഷിക്കുക", "ପଶୁ ଏବଂ ଯନ୍ତ୍ରପାତି ସୁରକ୍ଷିତ ସ୍ଥାନରେ ରଖନ୍ତୁ", "পশুধন আৰু যন্ত্ৰপাতি সুৰক্ষিত ঠাইত ৰাখক", "مویشیوں اور اوزاروں کو محفوظ کریں", "पशु आ उपकरण के सुरक्षित स्थान पर राखू"),
                    t("Inspecting indoor grain storage & seeds", "अनाज गोदाम व बीज भंडारण की जांच", "અનાજ ગોડાઉન અને બિયારણ ચકાસો", "गोदामातील धान्य व बियाणे तपासा", "ਅਨਾਜ ਭੰਡਾਰ ਅਤੇ ਬੀਜ ਚੈੱਕ ਕਰੋ", "শস্যের গুদাম ও বীজ পরীক্ষা করুন", "தானியக் கிடங்குகளைப் பரிசோதிக்கவும்", "ధాన్యపు నిల్వలను తనిఖీ చేయండి", "ಧಾನ್ಯ ಸಂಗ್ರಹಣೆಯನ್ನು ಪರಿಶೀಲಿಸಿ", "ധാന്യ സംഭരണം പരിശോധിക്കുക", "ଶସ୍ୟ ଗୋଦାମ ଯାଞ୍ଚ କରନ୍ତୁ", "শস্য ভঁৰাল পৰীক্ষা কৰক", "اناج کے گودام کا معائنہ کریں", "अनाज गोदाम केर जांच करू")
                ),
                precautions = listOf(
                    t("Provide physical staking for tall crops", "लंबी फसलों (टमाटर, केला, गन्ना) को सहारा दें", "ઊંચા પાકને ટેકો આપો", "उंच पिकांना आधार द्या", "ਲੰਬੀਆਂ ਫਸਲਾਂ ਨੂੰ ਸਹਾਰਾ ਦਿਓ", "লম্বা ফসলকে খুঁটি দিয়ে বাঁধুন", "உயரமான பயிர்களுக்கு முட்டுக் கொடுக்கவும்", "ఎత్తైన పంటలకు ఊతం ఇవ్వండి", "ಎತ್ತರದ ಬೆಳೆಗಳಿಗೆ ಆಧಾರ ನೀಡಿ", "ഉയരമുള്ള വിളകൾക്ക് താങ്ങ് നൽകുക", "ଡେଙ୍ଗା ଫସଲକୁ ଆଶ୍ରୟ ଦିଅନ୍ତୁ", "ওখ শস্যক খুঁটিৰে বান্ধক", "لمبی فصلوں کو سہارا دیں", "पैघ फसल के सहारा दिअ"),
                    t("Secure greenhouse panels & nursery netting", "पॉलीहाउस व नर्सरी की जाली को मजबूती से बांधें", "પોલીહાઉસ અને નેટ મજબૂત રીતે બાંધો", "पॉलीहाऊस व शेडनेट घट्ट बांधा", "ਪੌਲੀਹਾਊਸ ਅਤੇ ਜਾਲੀ ਮਜ਼ਬੂਤ ਕਰੋ", "পলিহাউস ও শেডনেট শক্ত করে বাঁধুন", "பசுமைக் குடில் மற்றும் வலைகளைப் பாதுகாக்கவும்", "పాలీహౌస్ మరియు షేడ్ నెట్లను కట్టండి", "ಪಾಲಿಹೌಸ್ ನೆಟ್‌ಗಳನ್ನು ಭದ್ರಪಡಿಸಿ", "പോളിഹൗസ് നെറ്റുകൾ സുരക്ഷിതമാക്കുക", "ପଲିହାଉସ୍ ଏବଂ ନେଟ୍ ବାନ୍ଧନ୍ତୁ", "পলিহাউচৰ নেট সুৰক্ষিত কৰক", "گرین ہاؤس اور جالیوں کو مضبوط کریں", "पॉलीहाउस आ नर्सरी केर जाली कस क बान्हू")
                )
            )
        }
        desc.contains("heavy rain") || desc.contains("torrential") || desc.contains("heavy shower") || desc.contains("dense drizzle") -> {
            FieldGuidance(
                headline = t(
                    "Heavy Rain Advisory", "भारी बारिश की सलाह", "ભારે વરસાદની સલાહ",
                    "मुसळधार पावसाची पूर्वसूचना", "ਭਾਰੀ ਮੀਂਹ ਦੀ ਸਲਾਹ", "ভারী বৃষ্টির সতর্কতা",
                    "கனமழை எச்சரிக்கை", "భారీ వర్షపు సలహా", "ಭಾರೀ ಮಳೆಯ ಸಲಹೆ",
                    "കനത്ത മഴ മുന്നറിയിപ്പ്", "ପ୍ରବଳ ବର୍ଷା ସତର୍କତା", "প্ৰবল বৰষুণৰ পৰামৰ্শ",
                    "شدید بارش کا مشورہ", "भारी वर्षा केर सलाह"
                ),
                summary = t(
                    "Heavy rainfall occurring. Soil saturation is critical with severe runoff and leaching risks.",
                    "भारी बारिश जारी है। खेत में जलभराव रोकने के लिए तुरंत जल निकासी सुनिश्चित करें।",
                    "ભારે વરસાદ ચાલુ છે. ખેતરમાં પાણી ભરાતું અટકાવવા નિકાલની વ્યવસ્થા કરો.",
                    "मुसळधार पाऊस सुरू आहे. शेतात पाणी साचू नये म्हणून चर काढा.",
                    "ਭਾਰੀ ਮੀਂਹ ਪੈ ਰਿਹਾ ਹੈ। ਪਾਣੀ ਦੀ ਨਿਕਾਸੀ ਦਾ ਤੁਰੰਤ ਪ੍ਰਬੰਧ ਕਰੋ।",
                    "ভারী বৃষ্টিপাত হচ্ছে। ক্ষেতে জমে থাকা পানি দ্রুত নিষ্কাশন করুন।",
                    "கனமழை பெய்கிறது. வயலில் தேங்கிய நீரை உடனே வெளியேற்றவும்.",
                    "భారీ వర్షం కురుస్తోంది. పొలంలో నీరు నిలవకుండా డ్రైనేజీ చేయండి.",
                    "ಭಾರೀ ಮಳೆಯಾಗುತ್ತಿದೆ. ಹೊಲದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಕಾಲುವೆ ಮಾಡಿ.",
                    "കനത്ത മഴ പെയ്യുന്നു. വെള്ളക്കെട്ട് ഒഴിവാക്കാൻ ചാലുകൾ കീറുക.",
                    "ପ୍ରବଳ ବର୍ଷା ହେଉଛି। ଜମିରୁ ପାଣି ନିଷ୍କାସନ ବ୍ୟବସ୍ଥା କରନ୍ତୁ।",
                    "প্ৰবল বৰষুণ হৈ আছে। পথাৰৰ পৰা পানী ওলাই যোৱাৰ ব্যৱস্থা কৰক।",
                    "شدید بارش ہو رہی ہے۔ نکاسی آب کا فوری انتظام کریں۔",
                    "भारी वर्षा भ रहल अछि। खेत सं पानि निकालय केर व्यवस्था करू।"
                ),
                badge = t(
                    "HEAVY RAIN / RESTRICTED", "भारी बारिश / सीमित कार्य", "ભારે વરસાદ / કામ મર્યાદિત",
                    "मुसळधार पाऊस / मर्यादित कामे", "ਭਾਰੀ ਮੀਂਹ / ਸੀਮਤ ਕੰਮ", "ভারী বৃষ্টি / সীমিত কাজ",
                    "கனமழை / மட்டுப்படுத்தப்பட்டது", "భారీ వర్షం / పరిమిత పనులు", "ಭಾರೀ ಮಳೆ / ಸೀಮಿತ ಕೆಲಸ",
                    "കനത്ത മഴ / നിയന്ത്രിതം", "ପ୍ରବଳ ବର୍ଷା / ସୀମିତ କାର୍ଯ୍ୟ", "প্ৰবল বৰষুণ / সীমিত কাম",
                    "شدید بارش / محدود کام", "भारी वर्षा / सीमित काज"
                ),
                badgeColor = Color(0xFFFFEBEE),
                badgeTextColor = Color(0xFFC62828),
                icon = Icons.Rounded.BeachAccess,
                notSuitableFor = listOf(
                    t("Chemical pesticide spraying (immediate wash-off)", "दवा का छिड़काव (दवा धुलने का खतरा)", "દવાનો છંટકાવ (ધોવાઈ જવાનું જોખમ)", "फवारणी (औषध वाहून जाण्याची भीती)", "ਸਪਰੇਅ ਕਰਨਾ (ਮੀਂਹ ਨਾਲ ਧੁਲਣ ਦਾ ਖਤਰਾ)", "কীটনাশক স্প্রে (ধুয়ে যাওয়ার ঝুঁকি)", "மருந்து தெளித்தல் (கரைந்து போகும்)", "పిచிகారీ (కొట్టుకుపోయే ప్రమాదం)", "ಸಿಂಪಡಣೆ (ತೊಳೆದು ಹೋಗುವ ಅಪಾಯ)", "മരുന്ന് തളിക്കൽ (ഒഴുകിപ്പോകും)", "ଔଷଧ ସ୍ପ୍ରେ (ଧୋଇ ହୋଇଯିବ)", "ঔষধ স্প্ৰে' কৰা", "اسپرے کرنا (دھلنے کا خطرہ)", "दवाई छिड़काव (दवाई बहायब केर डर)"),
                    t("Heavy tractor tilling (causes severe soil compaction)", "गीली मिट्टी में भारी जुताई", "ભીની જમીનમાં ટ્રેક્ટર ચલાવવું", "ओल्या जमिनीत नांगरणी", "ਗਿੱਲੀ ਜ਼ਮੀਨ ਵਿੱਚ ਵਾਹੀ", "ভেজা মাটিতে চাষ দেওয়া", "ஈர நிலத்தில் உழுதல்", "తడి నేలలో దుక్కి దున్నడం", "ತೇವ ಭೂಮಿಯಲ್ಲಿ ಉಳುಮೆ", "നനഞ്ഞ നിലം ഉഴൽ", "ଓଦା ମାଟିରେ ହଳ କରିବା", "তিতা মাটিত হাল বোৱা", "گیلی زمین میں ہل چلانا", "ओसिल माटी मे जोताई")
                ),
                suitableFor = listOf(
                    t("Rainwater harvesting in farm ponds", "खेत के तालाबों में वर्षा जल संचयन", "ખેત તલાવડીમાં પાણીનો સંગ્રહ", "शेततळ्यात पावसाचे पाणी साठवणे", "ਖੇਤ ਦੇ ਛੱਪੜਾਂ 'ਚ ਪਾਣੀ ਇਕੱਠਾ ਕਰਨਾ", "পুকুরে বৃষ্টির পানি সংরক্ষণ", "பண்ணைக் குட்டைகளில் மழைநீர் சேகரிப்பு", "పంట కుంటలలో వర్షపు నీటి నిల్వ", "ಕೃಷಿ ಹೊಂಡಗಳಲ್ಲಿ ಮಳೆನೀರು ಸಂಗ್ರಹ", "കൃഷിത്തോട്ടങ്ങളിൽ മഴവെള്ള സംഭരണം", "ପୋଖରୀରେ ବର୍ଷା ଜଳ ସଂରକ୍ଷଣ", "পানী সংৰক্ষণ কৰা", "کھیت کے تالاب میں پانی جمع کرنا", "खेत केर पोखरि मे पानि संचय"),
                    t("Checking drainage outlets", "जल निकासी नालियों की सफाई", "નિકાલ ગટરોની સફાઈ", "पाणी वाहून जाणाऱ्या चरांची स्वच्छता", "ਨਿਕਾਸੀ ਨਾਲੀਆਂ ਦੀ ਸਫ਼ਾਈ", "পানি নিষ্কাশন নালা পরিষ্কার", "வடிகால் வாய்க்கால்களைச் சரிபார்த்தல்", "కాలువలను శుభ్రం చేయడం", "ಚರಂಡಿಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸುವುದು", "ഡ്രെയിനേജ് ചാലുകൾ വൃത്തിയാക്കൽ", "ନିଷ୍କାସନ ନାଳ ସଫା କରିବା", "পানী ওলোৱা নলা চাফা কৰা", "نکاسی نالیوں کی صفائی", "जल निकासी केर नाली साफ करब")
                ),
                precautions = listOf(
                    t("Clear field drainage channels immediately", "खेत से पानी निकालने की व्यवस्था रखें", "પાણીનો નિકાલ ચાલુ રાખો", "पाण्याचा निचरा सुरळीत ठेवा", "ਪਾਣੀ ਦੀ ਨਿਕਾਸੀ ਸੁਚਾਰੂ ਰੱਖੋ", "পানি দ্রুত বের করে দিন", "நீர் தேங்குவதைத் தடுக்கவும்", "నీరు నిలవకుండా చూడండి", "ನೀರು ಸರಾಗವಾಗಿ ಹರಿಯಲು ಬಿಡಿ", "വെള്ളം കെട്ടിനിൽക്കാൻ അനുവദിക്കരുത്", "ଜମିରେ ପାଣି ଜମିବାକୁ ଦିଅନ୍ତୁ ନାହିଁ", "পানী ওলাই যাবলৈ দিয়ক", "پانی کا نکاس یقینی بنائیں", "खेत सं पानि बहाबय केर व्यवस्था राखू")
                )
            )
        }
        else -> {
            FieldGuidance(
                headline = t(
                    "Optimal Field Conditions", "अनुकूल कृषि मौसम", "ખેતી માટે અનુકૂળ હવામાન",
                    "शेती कामांसाठी अनुकूल हवामान", "ਖੇਤੀ ਕੰਮਾਂ ਲਈ ਢੁਕਵਾਂ ਮੌਸਮ", "মাঠের কাজের জন্য অনুকূল আবহাওয়া",
                    "களப்பணிகளுக்கு உகந்த வானிலை", "పొలం పనులకు అనుకూల వాతావరణం", "ಕೃಷಿ ಕೆಲಸಗಳಿಗೆ ಉತ್ತಮ ಹವಾಮಾನ",
                    "കൃഷിപ്പണികൾക്ക് അനുകൂല കാലാവസ്ഥ", "କୃଷି କାର୍ଯ୍ୟ ପାଇଁ ଅନୁକୂଳ ପାଣିପାଗ", "কৃষি কামৰ বাবে উপযোগী বতৰ",
                    "کھیتی کے کاموں کے لیے سازگار موسم", "कृषि काज लेल अनुकूल मौसम"
                ),
                summary = t(
                    "Stable weather conditions. Favorable for chemical spraying, weeding, and routine fieldwork.",
                    "मौसम सामान्य और स्थिर है। दवा छिड़काव, निराई-गुड़ाई और नियमित खेती कार्यों के लिए उत्तम दिन।",
                    "હવામાન શાંત અને અનુકૂળ છે. દવા છંટકાવ, નીંદણ અને નિયમિત ખેતી કાર્યો માટે ઉત્તમ દિવસ.",
                    "हवामान स्थिर व स्वच्छ आहे. फवारणी, खुरपणी आणि दैनंदिन शेती कामांसाठी अतिशय चांगला दिवस.",
                    "ਮੌਸਮ ਸ਼ਾਂਤ ਅਤੇ ਸਾਫ਼ ਹੈ। ਸਪਰੇਅ, ਗੋਡੀ ਅਤੇ ਆਮ ਖੇਤ ਕੰਮਾਂ ਲਈ ਵਧੀਆ ਦਿਨ।",
                    "আবহাওয়া স্থিতিশীল রয়েছে। স্প্রে, আগাছা পরিষ্কার ও নিয়মিত মাঠের কাজের জন্য উপযুক্ত দিন।",
                    "வானிலை சீராக உள்ளது. மருந்து தெளித்தல், களையெடுத்தல் மற்றும் வழக்கமான பணிகளுக்கு உகந்தது.",
                    "వాతావరణం ప్రశాంతంగా ఉంది. పిచికారీ, కలుపు తీయడం మరియు సాధారణ పనులకు అనుకూలం.",
                    "ಹವಾಮಾನವು ಸ್ಥಿರವಾಗಿದೆ. ಸಿಂಪಡಣೆ, ಕಳೆ ಕೀಳುವುದು ಮತ್ತು ದಿನನಿತ್ಯದ ಕೃಷಿ ಕೆಲಸಗಳಿಗೆ ಸೂಕ್ತವಾಗಿದೆ.",
                    "കാലാവസ്ഥ ശാന്തമാണ്. മരുന്ന് തളിക്കൽ, കളപറിക്കൽ, പതിവ് പണികൾ എന്നിവയ്ക്ക് അനുകൂലം.",
                    "ପାଣିପାଗ ସ୍ଥିର ରହିଛି। ସ୍ପ୍ରେ, ଘାସ ବଛା ଏବଂ ନିୟମିତ କ୍ଷେତ କାର୍ଯ୍ୟ ପାଇଁ ଉତ୍ତମ ଦିନ।",
                    "বতৰ অনুকূল হৈ আছে। ঔষধ স্প্ৰে' কৰা আৰু পথাৰৰ নিয়মীয়া কামৰ বাবে ভাল সময়।",
                    "موسم سازگار ہے۔ اسپرے، گوڈی اور روزمرہ کے کاموں کے لیے بہترین دن۔",
                    "मौसम सामान्य आ स्थिर अछि। दवाई छिड़काव आ खेत काज लेल उत्तम दिन।"
                ),
                badge = t(
                    "OPTIMAL / GOOD FOR FIELDWORK", "अनुकूल / कार्य के लिए उपयुक्त", "અનુકૂળ / કામ માટે શ્રેષ્ઠ",
                    "अनुकूल / शेतीसाठी उत्तम", "ਅਨੁਕੂਲ / ਕੰਮ ਲਈ ਵਧੀਆ", "অনুকূল / কাজের জন্য উপযুক্ত",
                    "உகந்தது / பணிகளுக்கு ஏற்றது", "అనుకూలం / పనులకు మంచిది", "ಉತ್ತಮ / ಕೆಲಸಕ್ಕೆ ಸೂಕ್ತ",
                    "അനുകൂലം / പണികൾക്ക് ഉചിതം", "ଅନୁକୂଳ / କାର୍ଯ୍ୟ ପାଇଁ ଉତ୍ତମ", "অনুকূল / কামৰ বাবে ভাল",
                    "سازگار / کام کے لیے بہترین", "अनुकूल / काज लेल उपयुक्त"
                ),
                badgeColor = Color(0xFFE8F5E9),
                badgeTextColor = Color(0xFF1B5E20),
                icon = Icons.Rounded.WbSunny,
                notSuitableFor = listOf(
                    t("Over-irrigating without assessing soil moisture", "बिना जरूरत अधिक सिंचाई", "જરૂર વગર વધુ પિયત", "गरजेपेक्षा जास्त पाणी देणे", "ਲੋੜ ਤੋਂ ਵੱਧ ਸਿੰਚਾਈ", "অতিরিক্ত সেচ প্রদান", "தேவையின்றி அதிக பாசனம்", "అవసరానికి మించి నీరు పెట్టడం", "ಅತಿಯಾದ ನೀರಾವರಿ", "അമിതമായ നനയ്ക്കൽ", "ଅତ୍ୟଧିକ ଜଳସେଚନ", "অধিক জলসিঞ্চন", "ضرورت سے زیادہ آبپاشی", "बिना आवश्यकताक बेसी पटौनी")
                ),
                suitableFor = listOf(
                    t("Foliar pesticide, herbicide & nutrient spraying", "दवा व पोषक तत्वों का छिड़काव", "દવા અને પોષક તત્વોનો છંટકાવ", "कीटकनाशके व खतांची फवारणी", "ਸਪਰੇਅ ਅਤੇ ਖਾਦ ਪਾਉਣਾ", "কীটনাশক ও পুষ্টি উপাদান স্প্রে", "மருந்து மற்றும் ஊட்டச்சத்து தெளித்தல்", "పిచికారీ & పోషకాల పిచికారీ", "ಸಿಂಪಡಣೆ ಮತ್ತು ಪೋಷಕಾಂಶಗಳ ನೀಡಿಕೆ", "മരുന്ന് തളിക്കലും വളപ്രയോഗവും", "ଔଷଧ ଏବଂ ପୋଷକ ତତ୍ତ୍ୱ ସ୍ପ୍ରେ", "ঔষধ আৰু সাৰ স্প্ৰে' কৰা", "اسپرے اور غذائی اجزاء ڈالنا", "दवाई आ पोषक तत्व केर छिड़काव"),
                    t("Weed removal and manual intercultural operations", "निराई-गुड़ाई व खरपतवार नियंत्रण", "નીંદામણ અને ગોડ કામ", "खुरपणी व आंतरमशागत", "ਨਦੀਨ ਕੱਢਣਾ ਅਤੇ ਗੋਡੀ", "আগাছা পরিষ্কার ও নিড়ানি", "களை எடுத்தல் மற்றும் இடைப்பயிற்சி", "కలుపు తీత & అంతరకృషి", "ಕಳೆ ಕೀಳುವುದು ಮತ್ತು ಅಂತರಬೇಸಾಯ", "കളപറിക്കലും ഇടവിള പണികളും", "ଘାସ ବାଛିବା ଏବଂ କୋଡ଼ିବା", "বন-বাত নিৰ্মূল কৰা", "گھاس کاٹنا اور گوڈی کرنا", "सोहनी आ कोड़नी")
                ),
                precautions = listOf(
                    t("Inspect soil moisture before next irrigation", "मिट्टी की नमी देखकर ही अगली सिंचाई करें", "ભેજ ચકાસીને જ પિયત આપો", "मातीतील ओलावा पाहूनच पाणी द्या", "ਨਮੀ ਦੇਖ ਕੇ ਹੀ ਸਿੰਚਾਈ ਕਰੋ", "আর্দ্রতা দেখে সেচ দিন", "மண் ஈரப்பதத்தைப் பார்த்து பாசனம் செய்யுங்கள்", "తేమ చూసి నీరు పెట్టండి", "ತೇವಾಂಶ ನೋಡಿ ನೀರು ಕೊಡಿ", "ഈർപ്പം നോക്കി നനയ്ക്കുക", "ଓଦା ଦେଖି ଜଳସେଚନ କରନ୍ତୁ", "আৰ্দ্ৰতা চাই পানী দিয়ক", "نمی دیکھ کر آبپاشی کریں", "माटी मे नमी देखि क पटौनी करू")
                )
            )
        }
    }
}

// Data Handling
@Composable
private fun WeatherLoadingState() {
    val currentLang = LocalAppLanguage.current
    NeoCard {
        Column(
            modifier = Modifier.fillMaxWidth().padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            CircularProgressIndicator(color = Color(0xFF2E7D32))
            Text(AppLocalizer.localizeWeatherPhrase("loading live weather", currentLang), style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold))
            Text(AppLocalizer.localizeWeatherPhrase("fetching field conditions", currentLang), style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun WeatherErrorState(message: String, onRetry: () -> Unit) {
    val currentLang = LocalAppLanguage.current
    NeoCard(containerColor = MaterialTheme.colorScheme.errorContainer) {
        Column(modifier = Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Icon(Icons.Rounded.ErrorOutline, contentDescription = null, tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(32.dp))
            Text(AppLocalizer.localizeWeatherPhrase("weather unavailable", currentLang), style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
            Text(message, style = MaterialTheme.typography.bodyMedium)
            PremiumButton(text = AppLocalizer.localizeWeatherPhrase("try again", currentLang), onClick = onRetry)
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
                    advisory = advisoryObj
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