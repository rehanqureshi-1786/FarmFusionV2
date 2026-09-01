package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
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

data class DisplayWeatherData(
    val temperature: Int,
    val description: String,
    val humidity: Int,
    val windSpeed: Double,
    val pressure: Int,
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

            // Strictly unscrollable layout spaced to fill the screen
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(
                        start = 24.dp,
                        end = 24.dp,
                        top = 56.dp,
                        bottom = 116.dp
                    ),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                when {
                    isLoading -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { WeatherLoadingState() }
                    errorMessage != null -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
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
                        // 1. Hero Weather Card
                        WeatherHeroCard(weatherData!!)

                        // 2. Stat Cards Row
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            WeatherStatCard("Humidity", "${weatherData!!.humidity}%", Icons.Rounded.WaterDrop, Modifier.weight(1f))
                            WeatherStatCard("Wind", "${weatherData!!.windSpeed.toInt()} km/h", Icons.Rounded.Air, Modifier.weight(1f))
                            WeatherStatCard("Pressure", "${weatherData!!.pressure} hPa", Icons.Rounded.Speed, Modifier.weight(1f))
                        }

                        // 3. Compact Weather Guidance Card
                        WeatherGuidanceCard(weatherData!!.advice)

                        // 4. Outlook Forecast Section
                        Column {
                            Column(modifier = Modifier.padding(bottom = 8.dp)) {
                                Text(
                                    text = "Outlook",
                                    style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                                )
                                Text(
                                    text = "Short view for quick farm planning",
                                    style = MaterialTheme.typography.bodyMedium.copy(color = Color.DarkGray)
                                )
                            }
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                sampleForecast(weatherData!!).forEach { forecast ->
                                    OutlookCard(forecast, Modifier.weight(1f))
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
                        Text(
                            text = "Current Conditions",
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
                            fontWeight = FontWeight.Black,
                            color = Color.White,
                            fontSize = 72.sp
                        )
                    )
                    Spacer(modifier = Modifier.width(20.dp))
                    Column(verticalArrangement = Arrangement.Center) {
                        Text(
                            text = weatherData.description.replaceFirstChar { it.uppercase() },
                            style = MaterialTheme.typography.titleMedium.copy(color = Color.White, fontWeight = FontWeight.Bold, fontSize = 17.sp)
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = "Feels like ${weatherData.temperature + 2}°C",
                            style = MaterialTheme.typography.labelMedium.copy(color = Color.White.copy(alpha = 0.85f))
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
private fun WeatherGuidanceCard(advice: String) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(22.dp),
        color = Color(0xFFF4FAF4),
        shadowElevation = 0.dp
    ) {
        Box(modifier = Modifier.fillMaxWidth()) {

            // Scaled-down plant illustration anchored to bottom-right
            Image(
                painter = painterResource(id = R.drawable.ill_plant_guidance),
                contentDescription = "Plant Illustration",
                contentScale = ContentScale.Fit,
                modifier = Modifier
                    .width(82.dp) // Adjusted width for cleaner proportions
                    .align(Alignment.BottomEnd)
                    .padding(end = 12.dp)
            )

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 14.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Rounded.CloudQueue,
                        contentDescription = null,
                        tint = Color(0xFF2E7D32),
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Weather guidance",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1B5E20),
                            fontSize = 15.sp
                        )
                    )
                }
                Text(
                    text = "AI-friendly weather summary for today",
                    style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray, fontSize = 11.sp),
                    modifier = Modifier.padding(start = 26.dp, top = 2.dp)
                )

                Spacer(modifier = Modifier.height(10.dp))

                // Single-row advice pill
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = Color.White,
                    shadowElevation = 0.dp
                ) {
                    Text(
                        text = advice.ifBlank { "Good weather conditions for farm work" },
                        style = MaterialTheme.typography.bodyMedium.copy(
                            color = Color(0xFF1B1B1B),
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 12.5.sp
                        ),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                    )
                }
            }
        }
    }
}

@Composable
private fun OutlookCard(forecast: DailyForecast, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.height(106.dp),
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

private fun sampleForecast(weatherData: DisplayWeatherData): List<DailyForecast> = listOf(
    DailyForecast("Today", weatherData.temperature + 2, weatherData.temperature - 3, weatherData.description),
    DailyForecast("Tomorrow", weatherData.temperature + 1, weatherData.temperature - 4, "Partly cloudy"),
    DailyForecast("Thu", weatherData.temperature, weatherData.temperature - 2, "Clear"),
    DailyForecast("Fri", weatherData.temperature - 1, weatherData.temperature - 4, "Cloudy")
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
                    pressure = backendData.pressure_hpa,
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