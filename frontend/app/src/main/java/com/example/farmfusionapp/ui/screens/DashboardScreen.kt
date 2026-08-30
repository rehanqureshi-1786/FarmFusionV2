package com.example.farmfusionapp.ui.screens

import android.app.Activity
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.TrendingUp
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.util.lerp
import androidx.core.view.WindowCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.navigation.NavController
import java.util.Calendar
import kotlin.math.absoluteValue

// Explicitly importing the R class to resolve drawable and string reference errors
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.components.*
import com.example.farmfusionapp.utils.*
import com.example.farmfusionapp.viewmodel.AuthViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private data class HomeAction(
    val title: String,
    val subtitle: String,
    val iconVector: ImageVector? = null,
    val iconDrawable: Int? = null,
    val route: String,
    val colors: List<Color>,
    val iconTint: Color,
    val illustration: Int
)

private data class SuggestionPill(
    val title: String,
    val note: String,
    val icon: ImageVector,
    val tint: Color
)

// --- SHIMMER LOADING MODIFIER ---
fun Modifier.shimmerEffect(): Modifier = composed {
    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim by transition.animateFloat(
        initialValue = -500f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_translate"
    )
    background(
        brush = Brush.linearGradient(
            colors = listOf(
                Color.White.copy(alpha = 0.1f),
                Color.White.copy(alpha = 0.5f),
                Color.White.copy(alpha = 0.1f)
            ),
            start = Offset(translateAnim, translateAnim),
            end = Offset(translateAnim + 300f, translateAnim + 300f)
        ),
        shape = RoundedCornerShape(8.dp)
    )
}

@Composable
fun DashboardScreen(navController: NavController) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val scope = rememberCoroutineScope()
    val view = LocalView.current

    var weatherData by remember { mutableStateOf(WeatherSnapshotStore.latestWeather) }
    var locationName by remember { mutableStateOf(WeatherSnapshotStore.latestWeather?.city ?: "Waiting for location...") }
    var hasLocationPermission by remember { mutableStateOf(false) }

    // Changed to LaunchedEffect to prevent multiple redraws that break canvas loading sync
    if (!view.isInEditMode) {
        LaunchedEffect(Unit) {
            val window = (context as? Activity)?.window
            window?.let {
                WindowCompat.setDecorFitsSystemWindows(it, false)
                it.statusBarColor = android.graphics.Color.TRANSPARENT
            }
        }
    }

    val listState = rememberLazyListState()
    val density = LocalDensity.current.density

    // Standard map to cache exact pixel heights of items before they scroll off-screen
    val itemHeights = remember { mutableMapOf<Int, Int>() }

    // Unified continuous scroll tracker for smooth animations
    val totalScrollPx by remember {
        derivedStateOf {
            // Update cache with currently visible items
            listState.layoutInfo.visibleItemsInfo.forEach { itemInfo ->
                itemHeights[itemInfo.index] = itemInfo.size
            }

            val index = listState.firstVisibleItemIndex
            val offset = listState.firstVisibleItemScrollOffset.toFloat()
            val spacingPx = 22f * density // Accounts for Arrangement.spacedBy(22.dp)

            var accumulated = 0f
            // Accumulate exact heights of all scrolled-off items
            for (i in 0 until index) {
                accumulated += (itemHeights[i] ?: 0) + spacingPx
            }

            accumulated + offset
        }
    }

    // Opacity calculation fading out smoothly on scroll
    val headerOpacity by remember {
        derivedStateOf {
            val fadeDistancePx = 300f * density
            val progress = (1f - (totalScrollPx / fadeDistancePx)).coerceIn(0f, 1f)
            0.7f * progress
        }
    }

    // Parallax Math for 3D Depth
    val parallaxOffset by remember {
        derivedStateOf {
            totalScrollPx
        }
    }

    val groupedActions = remember {
        listOf(
            HomeAction(
                title = "Disease Scan",
                subtitle = "Camera + Gallery\nDiagnosis",
                iconDrawable = R.drawable.ic_disease_scan,
                route = NavRoutes.CropDisease,
                colors = listOf(Color(0xFFFFF5DE), Color(0xFFF9DEB0)),
                iconTint = Color(0xFF9A5700),
                illustration = R.drawable.ill_disease_scan
            ),
            HomeAction(
                title = "Crop Advice",
                subtitle = "AI planning for\nyour field",
                iconDrawable = R.drawable.ic_crop_advice,
                route = NavRoutes.CropRecommendation,
                colors = listOf(Color(0xFFE8F7E8), Color(0xFFCBE8CF)),
                iconTint = Color(0xFF246B3B),
                illustration = R.drawable.ill_crop_advice
            ),
            HomeAction(
                title = "Market Prices",
                subtitle = "Latest Mandi\nMovements",
                iconVector = Icons.AutoMirrored.Rounded.TrendingUp,
                route = NavRoutes.MandiPrices,
                colors = listOf(Color(0xFFEAF1FF), Color(0xFFCFE0FF)),
                iconTint = Color(0xFF235CA8),
                illustration = R.drawable.ill_market_prices
            ),
            HomeAction(
                title = "Weather",
                subtitle = "Full forecast",
                iconVector = Icons.Rounded.WbSunny,
                route = NavRoutes.Weather,
                colors = listOf(Color(0xFFE8F7FF), Color(0xFFBFE8FF)),
                iconTint = Color(0xFF0B6D97),
                illustration = R.drawable.ill_weather
            ),
            HomeAction(
                title = "Crop Services",
                subtitle = "Field support",
                iconVector = Icons.Rounded.Spa,
                route = NavRoutes.CropServices,
                colors = listOf(Color(0xFFF0F7E8), Color(0xFFDCECC5)),
                iconTint = Color(0xFF4D7A1F),
                illustration = R.drawable.ill_crop_services
            ),
            HomeAction(
                title = "Farm Store",
                subtitle = "Inputs and tools",
                iconVector = Icons.Rounded.Storefront,
                route = NavRoutes.ProductStore,
                colors = listOf(Color(0xFFFFF1E8), Color(0xFFF6D7C0)),
                iconTint = Color(0xFFA65411),
                illustration = R.drawable.ill_farm_store
            ),
            HomeAction(
                title = "Labour Help",
                subtitle = "Workers and\nnearby services",
                iconVector = Icons.Rounded.Groups,
                route = NavRoutes.LabourServices,
                colors = listOf(Color(0xFFF7EAF4), Color(0xFFE8CDE1)),
                iconTint = Color(0xFF7D3062),
                illustration = R.drawable.ill_labour_help
            ),
            HomeAction(
                title = "Animal Alert",
                subtitle = "🚧 Under Development\n(Coming Soon!)",
                iconDrawable = R.drawable.ic_animal_alert,
                route = NavRoutes.AnimalDetection,
                colors = listOf(Color(0xFFFFEAEA), Color(0xFFFFCFCF)),
                iconTint = Color(0xFFB71C1C),
                illustration = R.drawable.ill_animal_alert
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

    Box(modifier = Modifier.fillMaxSize().background(Color(0xFFF4F9F4))) {
        NeoScaffoldBackground {
            Box(modifier = Modifier.fillMaxSize()) {

                // Header Landscape Background (with Restored Smooth Parallax)
                Image(
                    painter = painterResource(id = R.drawable.ill_header_bg),
                    contentDescription = "Header Landscape",
                    contentScale = ContentScale.FillWidth,
                    modifier = Modifier
                        .fillMaxWidth()
                        .align(Alignment.TopCenter)
                        .graphicsLayer {
                            alpha = headerOpacity
                            // Positive translation pushes it slightly down against the scroll direction, creating deep parallax
                            translationY = parallaxOffset * 0.5f
                        }
                )

                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(
                        start = 0.dp,
                        end = 0.dp,
                        top = WindowInsets.statusBars.asPaddingValues().calculateTopPadding() + 14.dp,
                        bottom = 160.dp
                    ),
                    verticalArrangement = Arrangement.spacedBy(22.dp)
                ) {
                    item {
                        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                            HomeHeroHeader(location = locationName)
                        }
                    }

                    item {
                        HeroPagerSection(
                            weatherData = weatherData,
                            suggestions = suggestions,
                            onWeatherClick = { navController.navigate(NavRoutes.Weather) }
                        )
                    }

                    item {
                        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                            FrequentlyUsedServicesSection(
                                actions = groupedActions.take(4),
                                onActionClick = { navController.navigate(it.route) }
                            )
                        }
                    }

                    item {
                        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
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
    }
}

@Composable
private fun HomeHeroHeader(location: String) {
    // Dynamic Time-Aware Greeting Logic
    val currentHour = remember { Calendar.getInstance().get(Calendar.HOUR_OF_DAY) }
    val greeting = remember(currentHour) {
        when (currentHour) {
            in 5..11 -> "Good Morning,"
            in 12..16 -> "Good Afternoon,"
            in 17..20 -> "Good Evening,"
            else -> "Good Night,"
        }
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 4.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = Icons.Rounded.Agriculture,
                contentDescription = null,
                tint = Color(0xFF1B5E20),
                modifier = Modifier.size(20.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "FARMFUSION",
                style = MaterialTheme.typography.labelLarge.copy(
                    color = Color(0xFF1B5E20),
                    fontWeight = FontWeight.ExtraBold,
                    letterSpacing = 1.5.sp
                )
            )
        }
        Spacer(modifier = Modifier.height(10.dp))
        val authViewModel: AuthViewModel = remember { AuthViewModel() }
        val userInfo = remember { authViewModel.getCurrentUserInfo() }
        val userName = userInfo.third ?: "Farmer"

        Text(
            text = greeting, // Contextual Greeting applied
            style = MaterialTheme.typography.titleLarge.copy(
                fontWeight = FontWeight.Bold,
                color = Color(0xFF424242)
            )
        )
        Text(
            text = "$userName!",
            style = MaterialTheme.typography.headlineLarge.copy(
                fontWeight = FontWeight.ExtraBold,
                color = Color(0xFF1B5E20)
            )
        )

        // Location Pill
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = Color(0xFFFFF3E0).copy(alpha = 0.9f),
            modifier = Modifier.padding(top = 10.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
            ) {
                Icon(
                    imageVector = Icons.Rounded.LocationOn,
                    contentDescription = null,
                    tint = Color(0xFFFFB300),
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = location,
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = Color(0xFF5D4037),
                        fontWeight = FontWeight.Medium
                    ),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
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
    var isForward by remember { mutableStateOf(true) }

    // Auto-scrolls in a bouncing sequence (1 -> 2 -> 3 -> 2 -> 1)
    LaunchedEffect(pagerState.settledPage) {
        delay(6000)
        if (!pagerState.isScrollInProgress) {
            if (pagerState.settledPage == pageCount - 1) {
                isForward = false
            } else if (pagerState.settledPage == 0) {
                isForward = true
            }

            val nextPage = if (isForward) {
                pagerState.settledPage + 1
            } else {
                pagerState.settledPage - 1
            }

            pagerState.animateScrollToPage(
                page = nextPage.coerceIn(0, pageCount - 1),
                animationSpec = tween(durationMillis = 650, easing = FastOutSlowInEasing)
            )
        }
    }

    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
        HorizontalPager(
            state = pagerState,
            modifier = Modifier
                .fillMaxWidth()
                .height(236.dp),
            contentPadding = PaddingValues(0.dp),
            pageSpacing = 0.dp,
            beyondViewportPageCount = 1
        ) { page ->

            // Calculate absolute distance of the card from the center of the screen
            val pageOffset = ((pagerState.currentPage - page) + pagerState.currentPageOffsetFraction).absoluteValue

            // Scale math: Shrinks to 85% when departing, grows back to 100% arriving
            val scale = lerp(
                start = 0.85f,
                stop = 1f,
                fraction = 1f - pageOffset.coerceIn(0f, 1f)
            )

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 20.dp)
                    .graphicsLayer {
                        scaleX = scale
                        scaleY = scale
                    }
            ) {
                when (page) {
                    0 -> WeatherHeroCard(weatherData, onWeatherClick)
                    1 -> AlertsHeroCard()
                    2 -> SuggestionsHeroCard(suggestions)
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
                            if (isSelected) Color(0xFF2E7D32)
                            else Color.LightGray.copy(alpha = 0.6f)
                        )
                        .size(if (isSelected) 10.dp else 6.dp)
                )
            }
        }
    }
}

@Composable
private fun WeatherHeroCard(weatherData: DisplayWeatherData?, onClick: () -> Unit) {
    val haptic = LocalHapticFeedback.current
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessLow),
        label = "weather_scale"
    )

    Surface(
        modifier = Modifier
            .fillMaxSize()
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
            }
            .shadow(12.dp, RoundedCornerShape(32.dp))
            .clickable(
                interactionSource = interactionSource,
                indication = null,
                onClick = {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onClick()
                }
            ),
        shape = RoundedCornerShape(32.dp),
        color = Color.White
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.linearGradient(
                        colors = listOf(Color(0xFF4CAF50), Color(0xFF388E3C), Color(0xFF1B5E20))
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
                    .padding(horizontal = 20.dp, vertical = 18.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                // TOP HEADER ROW
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column {
                        // Made smaller and thinner
                        Text(
                            text = "Weather Forecast",
                            style = MaterialTheme.typography.labelMedium.copy(
                                color = Color.White.copy(alpha = 0.8f),
                                fontWeight = FontWeight.Normal
                            )
                        )
                        // SHIMMER STATE
                        if (weatherData == null) {
                            Box(modifier = Modifier.padding(top = 4.dp).width(120.dp).height(28.dp).shimmerEffect())
                        } else {
                            Text(
                                text = weatherData.city,
                                style = MaterialTheme.typography.titleLarge.copy(
                                    color = Color.White,
                                    fontWeight = FontWeight.ExtraBold,
                                    fontSize = 24.sp
                                )
                            )
                        }
                    }

                    Icon(
                        imageVector = when {
                            weatherData?.description?.contains("cloud", ignoreCase = true) == true -> Icons.Rounded.WbCloudy
                            weatherData?.description?.contains("rain", ignoreCase = true) == true -> Icons.Rounded.BeachAccess
                            else -> Icons.Rounded.WbSunny
                        },
                        contentDescription = null,
                        tint = Color.White,
                        modifier = Modifier.size(44.dp)
                    )
                }

                // MIDDLE TEMPERATURE ROW
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // SHIMMER STATE
                    if (weatherData == null) {
                        Box(modifier = Modifier.width(110.dp).height(80.dp).shimmerEffect())
                        Spacer(modifier = Modifier.width(16.dp))
                        Box(modifier = Modifier.height(50.dp).width(1.dp).background(Color.White.copy(alpha = 0.4f)))
                        Spacer(modifier = Modifier.width(16.dp))
                        Column {
                            Box(modifier = Modifier.width(100.dp).height(20.dp).shimmerEffect())
                            Spacer(modifier = Modifier.height(4.dp))
                            Box(modifier = Modifier.width(140.dp).height(16.dp).shimmerEffect())
                        }
                    } else {
                        // Increased temperature value font size & added Celsius
                        Text(
                            text = "${weatherData.temperature}°C",
                            style = MaterialTheme.typography.displayLarge.copy(
                                fontWeight = FontWeight.SemiBold,
                                color = Color.White,
                                fontSize = 64.sp
                            )
                        )

                        Spacer(modifier = Modifier.width(16.dp))

                        // Added Vertical Line separator
                        Box(
                            modifier = Modifier
                                .height(56.dp)
                                .width(1.dp)
                                .background(Color.White.copy(alpha = 0.5f))
                        )

                        Spacer(modifier = Modifier.width(16.dp))

                        Column {
                            Text(
                                text = weatherData.description.replaceFirstChar { it.uppercase() },
                                style = MaterialTheme.typography.titleMedium.copy(
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 18.sp
                                )
                            )
                            Text(
                                text = "Feels like ${weatherData.temperature.plus(2)}°C", // Added Celsius
                                style = MaterialTheme.typography.bodyMedium.copy(
                                    color = Color.White.copy(alpha = 0.8f)
                                )
                            )
                        }
                    }
                }

                // BOTTOM FROSTED CAPSULE ROW
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(24.dp))
                        .background(Color.White.copy(alpha = 0.28f)) // Increased opacity for frosted look
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    WeatherStatItem(Icons.Rounded.WaterDrop, "Humidity", weatherData?.let { "${it.humidity}%" } ?: "--")
                    Box(modifier = Modifier.height(24.dp).width(1.dp).background(Color.White.copy(alpha = 0.3f)))
                    WeatherStatItem(Icons.Rounded.Air, "Wind", weatherData?.let { "${it.windSpeed.toInt()} km/h" } ?: "--")
                    Box(modifier = Modifier.height(24.dp).width(1.dp).background(Color.White.copy(alpha = 0.3f)))
                    WeatherStatItem(Icons.Rounded.Speed, "Pressure", weatherData?.let { "${it.pressure ?: "--"} hPa" } ?: "--")
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
                modifier = Modifier.size(170.dp).align(Alignment.BottomEnd).offset(x = 30.dp, y = 30.dp)
            )

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 20.dp, vertical = 18.dp),
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
                        modifier = Modifier.size(30.dp)
                    )
                }

                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    AlertItem("Pest Warning", "Nearby reports of Locust swarms.")
                    AlertItem("Market Price Drop", "Wheat rates slightly down in your area.")
                }

                Button(
                    onClick = { },
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White.copy(alpha = 0.25f)),
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 6.dp)
                ) {
                    Text("Review All Alerts", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                }
            }
        }
    }
}

@Composable
private fun AlertItem(title: String, desc: String) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        Box(modifier = Modifier.size(6.dp).background(Color.White, CircleShape))
        Column {
            Text(title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.sp)
            Text(desc, color = Color.White.copy(alpha = 0.85f), fontSize = 11.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
    }
}

@Composable
private fun SuggestionsHeroCard(suggestions: List<SuggestionPill>) {
    Surface(
        modifier = Modifier.fillMaxSize(),
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
            Icon(
                imageVector = Icons.Rounded.TipsAndUpdates,
                contentDescription = null,
                tint = Color.White.copy(alpha = 0.1f),
                modifier = Modifier.size(170.dp).align(Alignment.BottomEnd).offset(x = 30.dp, y = 30.dp)
            )

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 20.dp, vertical = 18.dp),
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

                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    suggestions.take(2).forEach { suggestion ->
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            Icon(suggestion.icon, null, tint = Color.White, modifier = Modifier.size(18.dp))
                            Column {
                                Text(suggestion.title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                                Text(suggestion.note, color = Color.White.copy(alpha = 0.85f), fontSize = 11.sp, maxLines = 1)
                            }
                        }
                    }
                }

                Text(
                    "Discover more tailored advice in individual service screens.",
                    color = Color.White.copy(alpha = 0.75f),
                    fontSize = 11.sp,
                    lineHeight = 14.sp
                )
            }
        }
    }
}

@Composable
private fun FrequentlyUsedServicesSection(
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
                text = "Quick Actions",
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.ExtraBold,
                    color = Color(0xFF1B5E20)
                )
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            actions.forEach { action ->
                FrequentlyUsedCard(
                    action = action,
                    onClick = { onActionClick(action) }
                )
            }
        }
    }
}

@Composable
private fun FrequentlyUsedCard(
    action: HomeAction,
    onClick: () -> Unit
) {
    val haptic = LocalHapticFeedback.current
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    // Tactile Spring Animation
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.92f else 1f,
        animationSpec = spring(dampingRatio = 0.6f, stiffness = 300f),
        label = "quickActionScale"
    )

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp),
        modifier = Modifier
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
            }
            .clickable(
                interactionSource = interactionSource,
                indication = null,
                onClick = {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onClick()
                }
            )
    ) {
        Surface(
            modifier = Modifier
                .width(76.dp)
                .height(88.dp)
                .shadow(
                    elevation = 8.dp,
                    shape = RoundedCornerShape(20.dp),
                    spotColor = Color(0xFF1B5E20).copy(alpha = 0.15f),
                    ambientColor = Color.Black.copy(alpha = 0.05f)
                ),
            shape = RoundedCornerShape(20.dp),
            color = Color.White,
            border = BorderStroke(1.dp, Color(0xFFF0F5F0))
        ) {
            Box(contentAlignment = Alignment.Center) {
                if (action.iconVector != null) {
                    Icon(
                        imageVector = action.iconVector,
                        contentDescription = action.title,
                        tint = action.iconTint,
                        modifier = Modifier.size(34.dp)
                    )
                } else if (action.iconDrawable != null) {
                    Image(
                        painter = painterResource(id = action.iconDrawable),
                        contentDescription = action.title,
                        modifier = Modifier.size(40.dp),
                        contentScale = ContentScale.Fit
                    )
                }
            }
        }
        Text(
            text = action.title.split(" ").first(),
            style = MaterialTheme.typography.labelMedium.copy(
                fontWeight = FontWeight.Bold,
                color = Color(0xFF424242)
            )
        )
    }
}

@Composable
private fun WeatherStatItem(icon: ImageVector, label: String, value: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, null, tint = Color.White, modifier = Modifier.size(15.dp))
        Spacer(modifier = Modifier.width(5.dp))
        Column {
            Text(value, style = MaterialTheme.typography.labelMedium.copy(color = Color.White, fontWeight = FontWeight.Bold))
            Text(label, style = MaterialTheme.typography.labelSmall.copy(color = Color.White.copy(alpha = 0.75f), fontSize = 10.sp))
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
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.ExtraBold,
                    color = Color(0xFF1B5E20)
                )
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
    val haptic = LocalHapticFeedback.current
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    // Tactile Spring Animation
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.94f else 1f,
        animationSpec = spring(dampingRatio = 0.6f, stiffness = 300f),
        label = "modernCardScale"
    )

    Surface(
        onClick = onClick,
        modifier = modifier
            .height(180.dp)
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
            }
            .clickable(
                interactionSource = interactionSource,
                indication = null,
                onClick = {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onClick()
                }
            ),
        shape = RoundedCornerShape(24.dp),
        color = action.colors[0],
        shadowElevation = 1.dp,
        border = BorderStroke(1.dp, action.colors[1].copy(alpha = 0.5f))
    ) {
        Box(modifier = Modifier.fillMaxSize()) {

            // Background Illustration Image
            Image(
                painter = painterResource(id = action.illustration),
                contentDescription = null,
                contentScale = ContentScale.Fit,
                alpha = 0.7f,
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .fillMaxWidth(0.85f)
                    .fillMaxHeight(0.7f)
                    .offset(x = 10.dp, y = 10.dp)
            )

            // Foreground Layout (Icon and Text)
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                verticalArrangement = Arrangement.Top
            ) {
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = action.colors[1],
                    shadowElevation = 4.dp,
                    modifier = Modifier.size(46.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        if (action.iconVector != null) {
                            Icon(
                                imageVector = action.iconVector,
                                contentDescription = null,
                                tint = action.iconTint,
                                modifier = Modifier.size(24.dp)
                            )
                        } else if (action.iconDrawable != null) {
                            Image(
                                painter = painterResource(id = action.iconDrawable),
                                contentDescription = null,
                                modifier = Modifier.size(28.dp),
                                contentScale = ContentScale.Fit
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(14.dp))

                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(
                        text = action.title,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1B1B1B),
                            fontSize = 15.sp
                        )
                    )
                    Text(
                        text = action.subtitle,
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = Color.Gray,
                            fontSize = 11.sp,
                            lineHeight = 14.sp
                        ),
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
        }
    }
}