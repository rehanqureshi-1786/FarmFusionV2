package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.KeyboardArrowRight
import androidx.compose.material.icons.automirrored.rounded.ShowChart
import androidx.compose.material.icons.automirrored.rounded.TrendingUp
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import com.example.farmfusionapp.R
import com.example.farmfusionapp.viewmodel.AuthViewModel
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.util.lerp
import kotlin.math.absoluteValue
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.navigation.NavController
import androidx.navigation.compose.currentBackStackEntryAsState
import com.example.farmfusionapp.ui.components.*
import com.example.farmfusionapp.utils.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private data class HomeAction(
    val title: String,
    val subtitle: String,
    val icon: ImageVector,
    val route: String,
    val colors: List<Color>,
    val iconTint: Color
)

private data class SuggestionPill(
    val title: String,
    val note: String,
    val icon: ImageVector,
    val tint: Color
)

@Composable
fun DashboardScreen(navController: NavController) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val scope = rememberCoroutineScope()
    var weatherData by remember { mutableStateOf(WeatherSnapshotStore.latestWeather) }
    var locationName by remember { mutableStateOf(WeatherSnapshotStore.latestWeather?.city ?: LocationSnapshotStore.latestCity ?: "Location unavailable") }
    var hasLocationPermission by remember { mutableStateOf(false) }

    val groupedActions = remember {
        listOf(
            HomeAction(
                title = "Disease Scan",
                subtitle = "Camera + gallery diagnosis",
                icon = Icons.Rounded.CameraAlt,
                route = NavRoutes.CropDisease,
                colors = listOf(Color(0xFFFFF5DE), Color(0xFFF9DEB0)),
                iconTint = Color(0xFF9A5700)
            ),
            HomeAction(
                title = "Crop Advice",
                subtitle = "AI planning for your field",
                icon = Icons.Rounded.AutoAwesome,
                route = NavRoutes.CropRecommendation,
                colors = listOf(Color(0xFFE8F7E8), Color(0xFFCBE8CF)),
                iconTint = Color(0xFF246B3B)
            ),
            HomeAction(
                title = "Market Prices",
                subtitle = "Latest mandi movements",
                icon = Icons.AutoMirrored.Rounded.ShowChart,
                route = NavRoutes.MandiPrices,
                colors = listOf(Color(0xFFEAF1FF), Color(0xFFCFE0FF)),
                iconTint = Color(0xFF235CA8)
            ),
            HomeAction(
                title = "Weather",
                subtitle = "Full forecast",
                icon = Icons.Rounded.WbSunny,
                route = NavRoutes.Weather,
                colors = listOf(Color(0xFFE8F7FF), Color(0xFFBFE8FF)),
                iconTint = Color(0xFF0B6D97)
            ),
            HomeAction(
                title = "Crop Services",
                subtitle = "Field support",
                icon = Icons.Rounded.Spa,
                route = NavRoutes.CropServices,
                colors = listOf(Color(0xFFF0F7E8), Color(0xFFDCECC5)),
                iconTint = Color(0xFF4D7A1F)
            ),
            HomeAction(
                title = "Farm Store",
                subtitle = "Inputs and tools",
                icon = Icons.Rounded.Storefront,
                route = NavRoutes.ProductStore,
                colors = listOf(Color(0xFFFFF1E8), Color(0xFFF6D7C0)),
                iconTint = Color(0xFFA65411)
            ),
            HomeAction(
                title = "Labour Help",
                subtitle = "Workers and nearby services",
                icon = Icons.Rounded.Groups,
                route = NavRoutes.LabourServices,
                colors = listOf(Color(0xFFF7EAF4), Color(0xFFE8CDE1)),
                iconTint = Color(0xFF7D3062)
            ),
            HomeAction(
                title = "Animal Alert",
                subtitle = "🚧 Under Development - Coming Soon!",
                icon = Icons.Rounded.Pets,
                route = NavRoutes.AnimalDetection,
                colors = listOf(Color(0xFFFFEAEA), Color(0xFFFFCFCF)),
                iconTint = Color(0xFFB71C1C)
            )
        )
    }

    val suggestions = remember {
        listOf(
            SuggestionPill(
                title = "Rain watch",
                note = "Plan spray before evening showers.",
                icon = Icons.Rounded.NotificationsActive,
                tint = Color(0xFFFF8E3B)
            ),
            SuggestionPill(
                title = "Water check",
                note = "Irrigation reminder from the forecast.",
                icon = Icons.Rounded.WaterDrop,
                tint = Color(0xFF2B7FFF)
            ),
            SuggestionPill(
                title = "AI tip",
                note = "Use mic for a quick farm question.",
                icon = Icons.Rounded.TipsAndUpdates,
                tint = Color(0xFF1F9D63)
            )
        )
    }

    fun refreshWeather(force: Boolean = false) {
        scope.launch {
            refreshWeatherSnapshotIfNeeded(context, force = force) { data, _ ->
                weatherData = data ?: WeatherSnapshotStore.latestWeather
                if (data != null) locationName = data.city
            }
        }
    }

    LocationPermissionEffect(
        context = context,
        onPermissionGranted = {
            hasLocationPermission = true
            refreshWeather(force = true)
        },
        onPermissionDenied = {
            hasLocationPermission = false
            locationName = "Location permission needed"
        }
    )

    DisposableEffect(lifecycleOwner, hasLocationPermission) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME && hasLocationPermission) refreshWeather()
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    LaunchedEffect(weatherData?.city) {
        if (!weatherData?.city.isNullOrBlank()) {
            locationName = weatherData?.city ?: locationName
        }
    }

    LaunchedEffect(Unit) {
        val appLanguage = LanguagePreferences.getSelectedLanguage(context) ?: "en"
        val lat = LocationSnapshotStore.latestLatitude
        val lon = LocationSnapshotStore.latestLongitude
        if (lat != null && lon != null) {
            val city = getCityFromLocation(context, lat, lon, appLanguage)
            if (!city.isNullOrBlank()) {
                locationName = city
            }
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        NeoScaffoldBackground {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .statusBarsPadding(),
                contentPadding = PaddingValues(start = 20.dp, end = 20.dp, top = 14.dp, bottom = 24.dp),
                verticalArrangement = Arrangement.spacedBy(18.dp)
            ) {
                item {
                    HomeHeroHeader(
                        location = locationName,
                        onProfileClick = { navController.navigate(NavRoutes.Profile) }
                    )
                }

                item {
                    HeroPagerSection(
                        weatherData = weatherData,
                        suggestions = suggestions,
                        onWeatherClick = { navController.navigate(NavRoutes.Weather) }
                    )
                }

                item {
                    FrequentlyUsedSection(
                        actions = groupedActions.take(4),
                        onActionClick = { navController.navigate(it.route) }
                    )
                }

                item {
                    ActionGroup(
                        actions = groupedActions,
                        onActionClick = {
                            if (it.route == NavRoutes.ProductStore) {
                                AgriStoreContext.setBrowse()
                            }
                            navController.navigate(it.route)
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun HomeHeroHeader(
    location: String,
    onProfileClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Rounded.Agriculture,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "FARMFUSION",
                    style = MaterialTheme.typography.labelLarge.copy(
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.ExtraBold,
                        letterSpacing = 2.sp
                    )
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            val authViewModel: AuthViewModel = remember { AuthViewModel() }
            val userInfo = remember { authViewModel.getCurrentUserInfo() }
            val userName = userInfo.third ?: "Farmer"
            Text(
                text = "${stringResource(R.string.welcome_to)} $userName!",
                style = MaterialTheme.typography.headlineMedium.copy(
                    fontWeight = FontWeight.ExtraBold,
                    color = Color(0xFF1B1B1B)
                )
            )
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(top = 4.dp)
            ) {
                Icon(
                    imageVector = Icons.Rounded.LocationOn,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.secondary,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = location,
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontWeight = FontWeight.Medium
                    ),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }

        Surface(
            onClick = onProfileClick,
            modifier = Modifier
                .size(56.dp)
                .shadow(6.dp, CircleShape),
            shape = CircleShape,
            color = Color.White,
            border = BorderStroke(2.dp, Brush.linearGradient(listOf(Color(0xFF81C784), Color(0xFF2E7D32))))
        ) {
            Box(contentAlignment = Alignment.Center) {
                Icon(
                    imageVector = Icons.Rounded.Person,
                    contentDescription = "Profile",
                    modifier = Modifier.size(32.dp),
                    tint = Color(0xFF2E7D32)
                )
            }
        }
    }
}

@Composable
private fun HeroPagerSection(
    weatherData: DisplayWeatherData?,
    suggestions: List<SuggestionPill>,
    onWeatherClick: () -> Unit
) {
    val pageCount = 3
    val pagerState = rememberPagerState(pageCount = { pageCount })
    val scope = rememberCoroutineScope()

    LaunchedEffect(pagerState.currentPage) {
        delay(8000)
        val nextPage = (pagerState.currentPage + 1) % pageCount
        pagerState.animateScrollToPage(nextPage)
    }

    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
            HorizontalPager(
                state = pagerState,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(220.dp)
                    .clip(RoundedCornerShape(32.dp)),
                contentPadding = PaddingValues(horizontal = 0.dp),
                pageSpacing = 16.dp,
                beyondViewportPageCount = 1
            ) { page ->
                Box(modifier = Modifier.fillMaxSize()) {
                    when (page) {
                        0 -> WeatherHeroCard(weatherData, onWeatherClick)
                        1 -> AlertsHeroCard()
                        2 -> SuggestionsHeroCard(suggestions)
                    }
                }
            }
        }

        Row(
            modifier = Modifier
                .height(8.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            repeat(pageCount) { iteration ->
                val isSelected = pagerState.currentPage == iteration
                Box(
                    modifier = Modifier
                        .padding(horizontal = 4.dp)
                        .clip(CircleShape)
                        .background(
                            if (isSelected) MaterialTheme.colorScheme.primary
                            else Color.LightGray
                        )
                        .size(if (isSelected) 10.dp else 6.dp)
                )
            }
        }
    }

@Composable
private fun WeatherHeroCard(weatherData: DisplayWeatherData?, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        modifier = Modifier
            .fillMaxSize()
            .shadow(12.dp, RoundedCornerShape(32.dp)),
        shape = RoundedCornerShape(32.dp),
        color = Color.White
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.linearGradient(
                        colors = listOf(Color(0xFF4FC3F7), Color(0xFF29B6F6), Color(0xFF039BE5))
                    )
                )
        ) {
            Box(
                modifier = Modifier
                    .size(150.dp)
                    .offset(x = (-30).dp, y = (-30).dp)
                    .background(Color.White.copy(alpha = 0.1f), CircleShape)
            )
            Box(
                modifier = Modifier
                    .size(100.dp)
                    .align(Alignment.BottomEnd)
                    .offset(x = 20.dp, y = 20.dp)
                    .background(Color.White.copy(alpha = 0.15f), CircleShape)
            )

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column {
                        Text(
                            text = "Weather Forecast",
                            style = MaterialTheme.typography.labelLarge.copy(
                                color = Color.White.copy(alpha = 0.9f),
                                fontWeight = FontWeight.Bold
                            )
                        )
                        Text(
                            text = weatherData?.city ?: "Locating...",
                            style = MaterialTheme.typography.titleLarge.copy(
                                color = Color.White,
                                fontWeight = FontWeight.ExtraBold
                            )
                        )
                    }

                    Icon(
                        imageVector = when {
                            weatherData?.description?.contains("cloud", ignoreCase = true) == true -> Icons.Rounded.WbCloudy
                            weatherData?.description?.contains("rain", ignoreCase = true) == true -> Icons.Rounded.BeachAccess
                            else -> Icons.Rounded.WbSunny
                        },
                        contentDescription = null,
                        tint = Color.White,
                        modifier = Modifier.size(48.dp)
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = weatherData?.let { "${it.temperature}°" } ?: "--°",
                        style = MaterialTheme.typography.displayLarge.copy(
                            fontWeight = FontWeight.Black,
                            color = Color.White,
                            fontSize = 72.sp
                        )
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Text(
                            text = weatherData?.description ?: "Clear Sky",
                            style = MaterialTheme.typography.titleMedium.copy(
                                color = Color.White,
                                fontWeight = FontWeight.Bold
                            )
                        )
                        Text(
                            text = "Feels like ${weatherData?.temperature?.plus(2)}°",
                            style = MaterialTheme.typography.bodyMedium.copy(
                                color = Color.White.copy(alpha = 0.8f)
                            )
                        )
                    }
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(20.dp))
                        .background(Color.White.copy(alpha = 0.2f))
                        .padding(horizontal = 24.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    WeatherStatItem(Icons.Rounded.WaterDrop, "Humidity", weatherData?.let { "${it.humidity}%" } ?: "--")
                    Box(modifier = Modifier.height(24.dp).width(1.dp).background(Color.White.copy(alpha = 0.3f)))
                    WeatherStatItem(Icons.Rounded.Air, "Wind Speed", weatherData?.let { "${it.windSpeed.toInt()} km/h" } ?: "--")
                }
            }
        }
    }
}

@Composable
private fun AlertsHeroCard() {
    Surface(
        modifier = Modifier
            .fillMaxSize()
            .shadow(12.dp, RoundedCornerShape(32.dp)),
        shape = RoundedCornerShape(32.dp),
        color = Color.White
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.linearGradient(
                        colors = listOf(Color(0xFFFF7043), Color(0xFFFF5722), Color(0xFFE64A19))
                    )
                )
        ) {
            Icon(
                imageVector = Icons.Rounded.NotificationsActive,
                contentDescription = null,
                tint = Color.White.copy(alpha = 0.1f),
                modifier = Modifier.size(180.dp).align(Alignment.BottomEnd).offset(x = 30.dp, y = 30.dp)
            )

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column {
                        Text(
                            text = "Field Alerts",
                            style = MaterialTheme.typography.labelLarge.copy(
                                color = Color.White.copy(alpha = 0.9f),
                                fontWeight = FontWeight.Bold
                            )
                        )
                        Text(
                            text = "2 Active Notices",
                            style = MaterialTheme.typography.titleLarge.copy(
                                color = Color.White,
                                fontWeight = FontWeight.ExtraBold
                            )
                        )
                    }
                    Icon(
                        Icons.Rounded.ErrorOutline,
                        null,
                        tint = Color.White,
                        modifier = Modifier.size(32.dp)
                    )
                }

                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    AlertItem("Pest Warning", "Nearby reports of Locust swarms.")
                    AlertItem("Market Price Drop", "Wheat rates slightly down in your area.")
                }

                Button(
                    onClick = { },
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White.copy(alpha = 0.2f)),
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                ) {
                    Text("Review All Alerts", color = Color.White, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
private fun AlertItem(title: String, desc: String) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Box(modifier = Modifier.size(6.dp).background(Color.White, CircleShape))
        Column {
            Text(title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp)
            Text(desc, color = Color.White.copy(alpha = 0.8f), fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
    }
}

@Composable
private fun SuggestionsHeroCard(suggestions: List<SuggestionPill>) {
    Surface(
        modifier = Modifier
            .fillMaxSize()
            .shadow(12.dp, RoundedCornerShape(32.dp)),
        shape = RoundedCornerShape(32.dp),
        color = Color.White
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.linearGradient(
                        colors = listOf(Color(0xFF66BB6A), Color(0xFF43A047), Color(0xFF2E7D32))
                    )
                )
        ) {
            Icon(
                imageVector = Icons.Rounded.TipsAndUpdates,
                contentDescription = null,
                tint = Color.White.copy(alpha = 0.1f),
                modifier = Modifier.size(180.dp).align(Alignment.BottomEnd).offset(x = 30.dp, y = 30.dp)
            )

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text(
                        text = "Smart Suggestions",
                        style = MaterialTheme.typography.labelLarge.copy(
                            color = Color.White.copy(alpha = 0.9f),
                            fontWeight = FontWeight.Bold
                        )
                    )
                    Text(
                        text = "AI Farm Tips",
                        style = MaterialTheme.typography.titleLarge.copy(
                            color = Color.White,
                            fontWeight = FontWeight.ExtraBold
                        )
                    )
                }

                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    suggestions.take(2).forEach { suggestion ->
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Icon(suggestion.icon, null, tint = Color.White, modifier = Modifier.size(20.dp))
                            Column {
                                Text(suggestion.title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                                Text(suggestion.note, color = Color.White.copy(alpha = 0.8f), fontSize = 12.sp, maxLines = 1)
                            }
                        }
                    }
                }

                Text(
                    "Discover more tailored advice in individual service screens.",
                    color = Color.White.copy(alpha = 0.7f),
                    fontSize = 11.sp,
                    lineHeight = 14.sp
                )
            }
        }
    }
}

@Composable
private fun FrequentlyUsedSection(
    actions: List<HomeAction>,
    onActionClick: (HomeAction) -> Unit
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Frequently Used Services",
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold)
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            actions.forEach { action ->
                RecentlyUsedButton(
                    icon = action.icon,
                    label = action.title.split(" ").first(),
                    onClick = { onActionClick(action) },
                    colors = action.colors,
                    iconTint = action.iconTint
                )
            }
        }
    }
}

@Composable
private fun WeatherStatItem(icon: ImageVector, label: String, value: String) {
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
private fun ActionGroup(
    actions: List<HomeAction>,
    onActionClick: (HomeAction) -> Unit
) {
    Column(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Farm Services",
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold)
            )
        }

        actions.chunked(2).forEach { rowActions ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                rowActions.forEach { action ->
                    ModernActionCard(
                        modifier = Modifier.weight(1f),
                        action = action,
                        onClick = { onActionClick(action) }
                    )
                }
                if (rowActions.size == 1) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
private fun ModernActionCard(
    modifier: Modifier = Modifier,
    action: HomeAction,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        modifier = modifier.height(140.dp),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        shadowElevation = 2.dp,
        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .background(action.colors[0], RoundedCornerShape(12.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = action.icon,
                    contentDescription = null,
                    tint = action.iconTint,
                    modifier = Modifier.size(24.dp)
                )
            }

            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = action.title,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1B1B1B)
                    )
                )
                Text(
                    text = action.subtitle,
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = Color.Gray
                    ),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }
    }
}

@Composable
private fun SuggestionCard(suggestion: SuggestionPill) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        shadowElevation = 2.dp,
        border = BorderStroke(1.dp, Color(0xFFF5F5F5))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .background(suggestion.tint.copy(alpha = 0.1f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = suggestion.icon,
                    contentDescription = null,
                    tint = suggestion.tint,
                    modifier = Modifier.size(24.dp)
                )
            }
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = suggestion.title,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
                )
                Text(
                    text = suggestion.note,
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = Color.Gray
                    )
                )
            }
            Icon(
                imageVector = Icons.AutoMirrored.Rounded.KeyboardArrowRight,
                contentDescription = null,
                tint = Color.LightGray,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

@Composable
private fun HomeBottomBar(navController: NavController) {
    val currentRoute = navController.currentBackStackEntryAsState().value?.destination?.route

    val items = listOf(
        Triple("Home", NavRoutes.Dashboard, Icons.Rounded.Dashboard),
        Triple("Rates", NavRoutes.MandiPrices, Icons.Rounded.BarChart),
        Triple("Scan", NavRoutes.CropDisease, Icons.Rounded.CenterFocusStrong),
        Triple("Weather", NavRoutes.Weather, Icons.Rounded.CloudQueue),
        Triple("Profile", NavRoutes.Profile, Icons.Rounded.Person)
    )

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        items.forEach { (label, route, icon) ->
            val selected = currentRoute == route
            val primaryColor = MaterialTheme.colorScheme.primary

            Column(
                modifier = Modifier
                    .weight(1f)
                    .clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null
                    ) { if (!selected) navController.navigate(route) }
                    .padding(vertical = 4.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .size(42.dp)
                        .shadow(
                            elevation = if (selected) 4.dp else 0.dp,
                            shape = RoundedCornerShape(12.dp),
                            spotColor = primaryColor.copy(alpha = 0.3f)
                        ),
                    color = if (selected) Color.White else Color.Transparent,
                    border = if (selected) BorderStroke(1.dp, Color(0xFFF0F0F0)) else null
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(
                                if (selected) {
                                    Brush.verticalGradient(listOf(primaryColor.copy(alpha = 0.1f), Color.White))
                                } else {
                                    Brush.verticalGradient(listOf(Color.Transparent, Color.Transparent))
                                }
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = icon,
                            contentDescription = label,
                            tint = if (selected) primaryColor else Color.Gray,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontWeight = if (selected) FontWeight.ExtraBold else FontWeight.Medium,
                        color = if (selected) primaryColor else Color.Gray,
                        fontSize = 10.sp
                    ),
                    maxLines = 1
                )
            }
        }
    }
}