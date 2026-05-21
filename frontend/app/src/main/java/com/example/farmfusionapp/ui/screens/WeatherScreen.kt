package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.BorderStroke
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.ui.components.*
import com.example.farmfusionapp.utils.*
import kotlinx.coroutines.launch

data class DisplayWeatherData(
    val temperature: Int,
    val description: String,
    val humidity: Int,
    val windSpeed: Double,
    val city: String,
    val advice: String,
    val forecast: List<DailyForecast> = emptyList()
)

data class DailyForecast(
    val day: String,
    val high: Int,
    val low: Int,
    val condition: String
)

object WeatherSnapshotStore {
    var latestWeather by mutableStateOf<DisplayWeatherData?>(null)
    var latestError by mutableStateOf<String?>(null)
    var lastUpdatedAt by mutableLongStateOf(0L)
}

fun shouldRefreshWeather(maxAgeMs: Long = 10 * 60 * 1000L): Boolean {
    if (WeatherSnapshotStore.latestWeather == null) return true
    return System.currentTimeMillis() - WeatherSnapshotStore.lastUpdatedAt > maxAgeMs
}

suspend fun refreshWeatherSnapshotIfNeeded(
    context: android.content.Context,
    force: Boolean = false,
    onResult: (DisplayWeatherData?, String?) -> Unit
) {
    if (!force && !shouldRefreshWeather()) {
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

    Column(modifier = Modifier.fillMaxSize()) {
        CenterAlignedTopAppBar(
            title = { Text("Weather", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)) },
            navigationIcon = {
                IconButton(onClick = { navController.popBackStack() }) {
                    Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                }
            }
        )
        NeoScaffoldBackground(
            modifier = Modifier.fillMaxSize()
        ) {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(20.dp),
                verticalArrangement = Arrangement.spacedBy(18.dp)
            ) {
                when {
                    isLoading -> item { WeatherLoadingState() }
                    errorMessage != null -> item {
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
                    weatherData != null -> {
                        item { WeatherHero(weatherData!!) }
                        item {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(14.dp)
                            ) {
                                WeatherInfoCard("Humidity", "${weatherData!!.humidity}%", Icons.Rounded.WaterDrop, Modifier.weight(1f))
                                WeatherInfoCard("Wind", "${weatherData!!.windSpeed.toInt()} km/h", Icons.Rounded.Air, Modifier.weight(1f))
                            }
                        }
                        item {
                            NeoSectionTitle("Field guidance", "AI-friendly weather summary for today")
                        }
                        item {
                            GlassPanel {
                                Text(
                                    text = weatherData!!.advice,
                                    style = MaterialTheme.typography.bodyLarge
                                )
                            }
                        }
                        item {
                            NeoSectionTitle("Outlook", "Short view for quick farm planning")
                        }
                        items(sampleForecast(weatherData!!)) { forecast ->
                            ForecastRow(forecast)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun WeatherLoadingState() {
    NeoCard {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            CircularProgressIndicator()
            Text("Loading live weather", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold))
            Text("Fetching your field conditions and advice.", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun WeatherErrorState(message: String, onRetry: () -> Unit) {
    NeoCard(containerColor = MaterialTheme.colorScheme.errorContainer) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Icon(Icons.Rounded.ErrorOutline, contentDescription = null, tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(32.dp))
            Text("Weather unavailable", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
            Text(message, style = MaterialTheme.typography.bodyMedium)
            PremiumButton(text = "Try Again", onClick = onRetry)
        }
    }
}

@Composable
private fun WeatherHero(weatherData: DisplayWeatherData) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .height(280.dp)
            .shadow(16.dp, RoundedCornerShape(32.dp)),
        shape = RoundedCornerShape(32.dp),
        color = Color.White
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.linearGradient(
                        colors = listOf(
                            Color(0xFF4FC3F7),
                            Color(0xFF29B6F6),
                            Color(0xFF039BE5)
                        )
                    )
                )
        ) {
            // Background Decorative Circles
            Box(
                modifier = Modifier
                    .size(180.dp)
                    .offset(x = (-40).dp, y = (-40).dp)
                    .background(Color.White.copy(alpha = 0.1f), CircleShape)
            )
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .align(Alignment.BottomEnd)
                    .offset(x = 30.dp, y = 30.dp)
                    .background(Color.White.copy(alpha = 0.15f), CircleShape)
            )

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(26.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Rounded.LocationOn,
                                contentDescription = null,
                                tint = Color.White.copy(alpha = 0.9f),
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = weatherData.city,
                                style = MaterialTheme.typography.titleMedium.copy(
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold
                                )
                            )
                        }
                        Text(
                            text = "Current Conditions",
                            style = MaterialTheme.typography.labelMedium.copy(
                                color = Color.White.copy(alpha = 0.8f)
                            )
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
                        modifier = Modifier.size(56.dp)
                    )
                }

                Column {
                    Text(
                        text = "${weatherData.temperature}°",
                        style = MaterialTheme.typography.displayLarge.copy(
                            fontWeight = FontWeight.Black,
                            color = Color.White,
                            fontSize = 84.sp
                        )
                    )
                    Text(
                        text = weatherData.description.replaceFirstChar { it.uppercase() },
                        style = MaterialTheme.typography.headlineSmall.copy(
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    )
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(20.dp))
                        .background(Color.White.copy(alpha = 0.2f))
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    WeatherHeroStat(Icons.Rounded.WaterDrop, "Humidity", "${weatherData.humidity}%")
                    Box(modifier = Modifier.height(24.dp).width(1.dp).background(Color.White.copy(alpha = 0.3f)))
                    WeatherHeroStat(Icons.Rounded.Air, "Wind", "${weatherData.windSpeed.toInt()} km/h")
                    Box(modifier = Modifier.height(24.dp).width(1.dp).background(Color.White.copy(alpha = 0.3f)))
                    WeatherHeroStat(Icons.Rounded.Compress, "Pressure", "1012 hPa")
                }
            }
        }
    }
}

@Composable
private fun WeatherHeroStat(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, value: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, null, tint = Color.White, modifier = Modifier.size(16.dp))
        Spacer(modifier = Modifier.width(6.dp))
        Column {
            Text(value, style = MaterialTheme.typography.labelLarge.copy(color = Color.White, fontWeight = FontWeight.Bold))
            Text(label, style = MaterialTheme.typography.labelSmall.copy(color = Color.White.copy(alpha = 0.7f)))
        }
    }
}

@Composable
private fun WeatherInfoCard(label: String, value: String, icon: androidx.compose.ui.graphics.vector.ImageVector, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.height(100.dp),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        shadowElevation = 4.dp,
        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(18.dp))
                }
            }
            Column {
                Text(label, style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray))
                Text(value, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
            }
        }
    }
}

@Composable
private fun ForecastRow(forecast: DailyForecast) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        shadowElevation = 2.dp,
        border = BorderStroke(1.dp, Color(0xFFF5F5F5))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .background(Color(0xFFF5F5F5), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = when {
                            forecast.condition.contains("cloud", ignoreCase = true) -> Icons.Rounded.WbCloudy
                            forecast.condition.contains("rain", ignoreCase = true) -> Icons.Rounded.BeachAccess
                            else -> Icons.Rounded.WbSunny
                        },
                        contentDescription = null,
                        tint = if (forecast.condition.contains("sun", ignoreCase = true)) Color(0xFFFFB300) else Color(0xFF0288D1),
                        modifier = Modifier.size(24.dp)
                    )
                }
                Column {
                    Text(forecast.day, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold))
                    Text(forecast.condition, style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray))
                }
            }
            Text(
                text = "${forecast.high}° / ${forecast.low}°",
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.ExtraBold,
                    color = MaterialTheme.colorScheme.primary
                )
            )
        }
    }
}

private fun sampleForecast(weatherData: DisplayWeatherData): List<DailyForecast> = listOf(
    DailyForecast("Today", weatherData.temperature + 2, weatherData.temperature - 3, weatherData.description),
    DailyForecast("Tomorrow", weatherData.temperature + 1, weatherData.temperature - 4, "Partly cloudy"),
    DailyForecast("Thu", weatherData.temperature, weatherData.temperature - 2, "Clear"),
    DailyForecast("Fri", weatherData.temperature - 1, weatherData.temperature - 4, "Windy"),
)

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
        val response = farmFusionApi.getCurrentWeather(latitude, longitude)

        if (response.isSuccessful && response.body() != null) {
            val body = response.body()!!
            val backendData = body.data
            if (body.success && backendData != null) {
                val backendLocation = backendData.location.trim()
                val currentStableCity = WeatherSnapshotStore.latestWeather?.city ?: LocationSnapshotStore.latestCity
                val resolvedBroadCity = getCityFromLocation(context, latitude, longitude, appLanguage)
                val city = when {
                    !resolvedBroadCity.isNullOrBlank() -> resolvedBroadCity
                    backendLocation.isNotEmpty() && !backendLocation.equals("Unknown", ignoreCase = true) -> backendLocation
                    !currentStableCity.isNullOrBlank() -> currentStableCity
                    else -> "Location unavailable"
                }

                val data = DisplayWeatherData(
                    temperature = backendData.temperature_c.toInt(),
                    description = backendData.weather,
                    humidity = backendData.humidity_percent,
                    windSpeed = backendData.wind_speed_ms,
                    city = city,
                    advice = backendData.farming_advice
                )
                WeatherSnapshotStore.latestWeather = data
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
