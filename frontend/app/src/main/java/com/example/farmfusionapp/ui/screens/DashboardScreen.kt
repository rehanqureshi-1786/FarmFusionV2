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
import kotlin.math.sin
import kotlin.math.cos
import androidx.compose.foundation.Canvas
import androidx.compose.ui.graphics.Path

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

    // Fast continuous scroll tracker via lambda providers (zero recomposition on scroll)
    val headerOpacityProvider: () -> Float = remember {
        {
            listState.layoutInfo.visibleItemsInfo.forEach { itemInfo ->
                itemHeights[itemInfo.index] = itemInfo.size
            }

            val index = listState.firstVisibleItemIndex
            val offset = listState.firstVisibleItemScrollOffset.toFloat()
            val spacingPx = 22f * density

            var accumulated = 0f
            for (i in 0 until index) {
                accumulated += (itemHeights[i] ?: 0) + spacingPx
            }

            val totalScroll = accumulated + offset
            val fadeDistancePx = 300f * density
            val progress = (1f - (totalScroll / fadeDistancePx)).coerceIn(0f, 1f)
            0.7f * progress
        }
    }

    val parallaxOffsetProvider: () -> Float = remember {
        {
            val index = listState.firstVisibleItemIndex
            val offset = listState.firstVisibleItemScrollOffset.toFloat()
            val spacingPx = 22f * density

            var accumulated = 0f
            for (i in 0 until index) {
                accumulated += (itemHeights[i] ?: 0) + spacingPx
            }

            accumulated + offset
        }
    }

    val currentLang = LocalAppLanguage.current
    val strings = LocalStrings.current

    val groupedActions = remember(strings) {
        listOf(
            HomeAction(
                title = strings.dashboard.diseaseScan,
                subtitle = strings.dashboard.diseaseScanSub,
                iconDrawable = R.drawable.ic_disease_scan,
                route = NavRoutes.CropDisease,
                colors = listOf(Color(0xFFFFF5DE), Color(0xFFF9DEB0)),
                iconTint = Color(0xFF9A5700),
                illustration = R.drawable.ill_disease_scan
            ),
            HomeAction(
                title = strings.dashboard.cropAdvice,
                subtitle = strings.dashboard.cropAdviceSub,
                iconDrawable = R.drawable.ic_crop_advice,
                route = NavRoutes.CropRecommendation,
                colors = listOf(Color(0xFFE8F7E8), Color(0xFFCBE8CF)),
                iconTint = Color(0xFF246B3B),
                illustration = R.drawable.ill_crop_advice
            ),
            HomeAction(
                title = strings.dashboard.marketRates,
                subtitle = strings.dashboard.marketRatesSub,
                iconVector = Icons.AutoMirrored.Rounded.TrendingUp,
                route = NavRoutes.MandiPrices,
                colors = listOf(Color(0xFFEAF1FF), Color(0xFFCFE0FF)),
                iconTint = Color(0xFF235CA8),
                illustration = R.drawable.ill_market_prices
            ),
            HomeAction(
                title = strings.dashboard.weatherForecast,
                subtitle = strings.dashboard.weatherForecastSub,
                iconVector = Icons.Rounded.WbSunny,
                route = NavRoutes.Weather,
                colors = listOf(Color(0xFFE8F7FF), Color(0xFFBFE8FF)),
                iconTint = Color(0xFF0B6D97),
                illustration = R.drawable.ill_weather
            ),
            HomeAction(
                title = strings.dashboard.cropServices,
                subtitle = strings.dashboard.cropServicesSub,
                iconVector = Icons.Rounded.Spa,
                route = NavRoutes.CropServices,
                colors = listOf(Color(0xFFF0F7E8), Color(0xFFDCECC5)),
                iconTint = Color(0xFF4D7A1F),
                illustration = R.drawable.ill_crop_services
            ),
            HomeAction(
                title = strings.dashboard.labourHelp,
                subtitle = strings.dashboard.labourHelpSub,
                iconVector = Icons.Rounded.Groups,
                route = NavRoutes.LabourServices,
                colors = listOf(Color(0xFFF7EAF4), Color(0xFFE8CDE1)),
                iconTint = Color(0xFF7D3062),
                illustration = R.drawable.ill_labour_help
            ),
            HomeAction(
                title = strings.dashboard.animalIntrusion,
                subtitle = strings.dashboard.animalIntrusionSub,
                iconDrawable = R.drawable.ic_animal_alert,
                route = NavRoutes.AnimalDetection,
                colors = listOf(Color(0xFFFFEAEA), Color(0xFFFFCFCF)),
                iconTint = Color(0xFFB71C1C),
                illustration = R.drawable.ill_animal_alert
            )
        )
    }

    val suggestions = remember(currentLang) {
        listOf(
            SuggestionPill(
                title = AppLocalizer.localizeDashboardPhrase("rain watch", currentLang),
                note = AppLocalizer.localizeDashboardPhrase("rain watch desc", currentLang),
                icon = Icons.Rounded.NotificationsActive,
                tint = Color(0xFFFF8E3B)
            ),
            SuggestionPill(
                title = AppLocalizer.localizeDashboardPhrase("water check", currentLang),
                note = AppLocalizer.localizeDashboardPhrase("water check desc", currentLang),
                icon = Icons.Rounded.WaterDrop,
                tint = Color(0xFF2B7FFF)
            ),
            SuggestionPill(
                title = AppLocalizer.localizeDashboardPhrase("ai tip", currentLang),
                note = AppLocalizer.localizeDashboardPhrase("ai tip desc", currentLang),
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
            locationName = AppLocalizer.localizeDashboardPhrase("location permission needed", currentLang)
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

                // Header Landscape Background with Living Dawn Animation & Flapping Birds
                AnimatedHeaderLandscape(
                    headerOpacity = headerOpacityProvider,
                    parallaxOffset = parallaxOffsetProvider,
                    modifier = Modifier.align(Alignment.TopCenter)
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
    val currentLang = LocalAppLanguage.current
    val strings = LocalStrings.current
    val localizedCity = remember(location, currentLang) {
        AppLocalizer.localizeCity(location, currentLang)
    }

    // Dynamic Time-Aware Greeting Logic in all 14 languages
    val currentHour = remember { Calendar.getInstance().get(Calendar.HOUR_OF_DAY) }
    val greetingKey = when (currentHour) {
        in 5..11 -> "good morning"
        in 12..16 -> "good afternoon"
        in 17..20 -> "good evening"
        else -> "good night"
    }
    val greeting = AppLocalizer.localizeDashboardPhrase(greetingKey, currentLang)

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
        val rawUserName = userInfo.third
        val userName = if (rawUserName.isNullOrBlank() || rawUserName.equals("Farmer", ignoreCase = true)) {
            AppLocalizer.localizeDashboardPhrase("farmer", currentLang)
        } else {
            rawUserName
        }

        Text(
            text = "$greeting,", // Contextual Greeting applied in 14 languages
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
            color = Color(0xFFFFF3E0).copy(alpha = 0.92f),
            border = BorderStroke(1.dp, Color(0xFFFFE0B2)),
            modifier = Modifier.padding(top = 10.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
            ) {
                Icon(
                    imageVector = Icons.Rounded.LocationOn,
                    contentDescription = null,
                    tint = Color(0xFFFF9800),
                    modifier = Modifier.size(14.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = localizedCity,
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = Color(0xFF5D4037),
                        fontWeight = FontWeight.SemiBold
                    ),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }
    }
}

private data class BirdSpec(
    val baseRelX: Float,
    val baseRelY: Float,
    val wingSpanDp: Float,
    val flapCycles: Int,
    val phaseOffset: Float,
    val thermalOffsetX: Float,
    val thermalOffsetY: Float,
    val alpha: Float
)

@Composable
private fun AnimatedHeaderLandscape(
    modifier: Modifier = Modifier,
    headerOpacity: () -> Float,
    parallaxOffset: () -> Float
) {
    val density = LocalDensity.current.density
    val transition = rememberInfiniteTransition(label = "landscape_sky_anim")
    val reusableBirdPath = remember { Path() }

    // Master harmonic loop (16 seconds) - everything syncs smoothly to exact integer harmonics
    val masterProgress by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 16000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "master_progress"
    )

    val masterRad = masterProgress * 2f * Math.PI.toFloat()

    Box(
        modifier = modifier
            .fillMaxWidth()
            .graphicsLayer {
                alpha = headerOpacity()
                translationY = parallaxOffset() * 0.5f
            }
    ) {
        // Base Clean Landscape Artwork
        Image(
            painter = painterResource(id = R.drawable.ill_header_bg),
            contentDescription = "Header Landscape",
            contentScale = ContentScale.FillWidth,
            modifier = Modifier.fillMaxWidth()
        )

        // Dynamic Sky Animation Layer (Sun Aura + Morning Mist + Flapping Birds in Formation)
        Canvas(
            modifier = Modifier.matchParentSize()
        ) {
            val currentAlpha = headerOpacity()
            if (currentAlpha <= 0.01f) return@Canvas

            val w = size.width
            val h = size.height
            if (w <= 0f || h <= 0f) return@Canvas

            // --- A. Warm Sun Dawn Aura & Breathing Rays ---
            val sunPulse = 0.90f + 0.16f * (sin(masterRad * 2f) * 0.5f + 0.5f)
            val sunCenterX = w * 0.785f
            val sunCenterY = h * 0.575f
            val baseSunRadius = w * 0.17f

            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        Color(0xFFFFEE58).copy(alpha = 0.25f * sunPulse),
                        Color(0xFFFFB300).copy(alpha = 0.08f * sunPulse),
                        Color.Transparent
                    ),
                    center = Offset(sunCenterX, sunCenterY),
                    radius = baseSunRadius * sunPulse
                ),
                center = Offset(sunCenterX, sunCenterY),
                radius = baseSunRadius * sunPulse
            )

            // Ambient warmth halo
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        Color(0xFFFFF9C4).copy(alpha = 0.12f),
                        Color.Transparent
                    ),
                    center = Offset(sunCenterX, sunCenterY),
                    radius = baseSunRadius * 1.7f
                ),
                center = Offset(sunCenterX, sunCenterY),
                radius = baseSunRadius * 1.7f
            )

            // --- B. Gentle Mountain Mist Drift (Harmonic sway, no teleport) ---
            val mistOffsetX = sin(masterRad) * (w * 0.12f)
            drawOval(
                brush = Brush.radialGradient(
                    colors = listOf(
                        Color.White.copy(alpha = 0.14f),
                        Color.Transparent
                    ),
                    center = Offset(w * 0.45f + mistOffsetX, h * 0.67f),
                    radius = w * 0.35f
                ),
                topLeft = Offset(w * 0.15f + mistOffsetX, h * 0.64f),
                size = androidx.compose.ui.geometry.Size(w * 0.70f, h * 0.06f)
            )

            // --- C. Animated Flock of Birds Flapping Wings in Harmonic Flight ---
            // Each bird has an integer number of flap cycles in 16 seconds (e.g. 6 to 8 flaps = ~2.0-2.6s per flap).
            // Because flapCycles is an integer, sin(masterRad * cycles) is mathematically 100% continuous
            // across the loop restart with ZERO jump or reset twitch.
            val birds = listOf(
                // Lead bird (majestic, prominent)
                BirdSpec(
                    baseRelX = 0.74f,
                    baseRelY = 0.42f,
                    wingSpanDp = 18f,
                    flapCycles = 8,
                    phaseOffset = 0f,
                    thermalOffsetX = 0f,
                    thermalOffsetY = 0f,
                    alpha = 0.88f
                ),
                // Left flank
                BirdSpec(
                    baseRelX = 0.68f,
                    baseRelY = 0.45f,
                    wingSpanDp = 15f,
                    flapCycles = 7,
                    phaseOffset = 0.8f,
                    thermalOffsetX = 0.4f,
                    thermalOffsetY = 0.6f,
                    alpha = 0.82f
                ),
                // Right high soarer
                BirdSpec(
                    baseRelX = 0.80f,
                    baseRelY = 0.39f,
                    wingSpanDp = 16f,
                    flapCycles = 7,
                    phaseOffset = 1.6f,
                    thermalOffsetX = 0.8f,
                    thermalOffsetY = 1.1f,
                    alpha = 0.85f
                ),
                // Distant high bird
                BirdSpec(
                    baseRelX = 0.84f,
                    baseRelY = 0.46f,
                    wingSpanDp = 12f,
                    flapCycles = 6,
                    phaseOffset = 2.4f,
                    thermalOffsetX = 1.2f,
                    thermalOffsetY = 1.5f,
                    alpha = 0.65f
                ),
                // Trailing left
                BirdSpec(
                    baseRelX = 0.63f,
                    baseRelY = 0.48f,
                    wingSpanDp = 13f,
                    flapCycles = 8,
                    phaseOffset = 3.2f,
                    thermalOffsetX = 1.6f,
                    thermalOffsetY = 2.0f,
                    alpha = 0.70f
                ),
                // Trailing right
                BirdSpec(
                    baseRelX = 0.70f,
                    baseRelY = 0.50f,
                    wingSpanDp = 11f,
                    flapCycles = 6,
                    phaseOffset = 4.0f,
                    thermalOffsetX = 2.0f,
                    thermalOffsetY = 2.5f,
                    alpha = 0.62f
                )
            )

            for (bird in birds) {
                // Exact integer harmonic angle guarantees perfect continuity across loop boundary
                val birdFlapAngle = (masterRad * bird.flapCycles) + bird.phaseOffset
                val sinVal = sin(birdFlapAngle)
                // Aerodynamic glide shaping: gently extends glide at top of upstroke
                val flap = if (sinVal > 0.72f) 0.72f + (sinVal - 0.72f) * 0.35f else sinVal

                // Closed-curve thermal soaring drift: continuous harmonic oscillation so flock floats majestically
                val driftX = (sin(masterRad + bird.thermalOffsetX) * 16f * density) +
                             (cos(masterRad * 2f + bird.thermalOffsetY) * 4f * density)
                val driftY = (cos(masterRad + bird.thermalOffsetY) * 5f * density) +
                             (sin(masterRad * 2f) * 2f * density)

                // Thermal bobbing: slight lift on power stroke
                val bobbing = sinVal * (bird.wingSpanDp * density * 0.12f)
                val birdX = w * bird.baseRelX + driftX
                val birdY = h * bird.baseRelY + driftY + bobbing

                val spanPx = bird.wingSpanDp * density
                val tipDy = -spanPx * 0.44f * flap
                val elbowDy = -spanPx * 0.32f * (flap + 0.35f)

                reusableBirdPath.reset()
                // Left Wing
                reusableBirdPath.moveTo(birdX, birdY - 1.2f * density)
                reusableBirdPath.quadraticTo(
                    birdX - spanPx * 0.5f,
                    birdY + elbowDy - 1.8f * density,
                    birdX - spanPx,
                    birdY + tipDy
                )
                reusableBirdPath.quadraticTo(
                    birdX - spanPx * 0.45f,
                    birdY + elbowDy + 1.6f * density,
                    birdX,
                    birdY + 1.8f * density
                )
                // Right Wing
                reusableBirdPath.quadraticTo(
                    birdX + spanPx * 0.45f,
                    birdY + elbowDy + 1.6f * density,
                    birdX + spanPx,
                    birdY + tipDy
                )
                reusableBirdPath.quadraticTo(
                    birdX + spanPx * 0.5f,
                    birdY + elbowDy - 1.8f * density,
                    birdX,
                    birdY - 1.2f * density
                )
                reusableBirdPath.close()

                drawPath(
                    path = reusableBirdPath,
                    color = Color(0xFF263627).copy(alpha = bird.alpha)
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
                .height(238.dp),
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
    val strings = LocalStrings.current
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
                            text = strings.weather.weatherForecast,
                            style = MaterialTheme.typography.labelMedium.copy(
                                color = Color.White.copy(alpha = 0.8f),
                                fontWeight = FontWeight.Normal
                            )
                        )
                        // SHIMMER STATE
                        if (weatherData == null) {
                            Box(modifier = Modifier.padding(top = 4.dp).width(120.dp).height(28.dp).shimmerEffect())
                        } else {
                            val currentLang = LocalAppLanguage.current
                            Text(
                                text = AppLocalizer.localizeCity(weatherData.city, currentLang),
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

                        val currentLang = LocalAppLanguage.current
                        val localizedCondition = AppLocalizer.localizeWeatherCondition(weatherData.description, currentLang)

                        Column {
                            Text(
                                text = localizedCondition.ifBlank { weatherData.description.replaceFirstChar { it.uppercase() } },
                                style = MaterialTheme.typography.titleMedium.copy(
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 18.sp
                                )
                            )
                            Text(
                                text = "${strings.weather.feelsLike} ${weatherData.temperature.plus(2)}°C", // Added Celsius
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
                        .padding(horizontal = 24.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    WeatherStatItem(Icons.Rounded.WaterDrop, strings.weather.humidity, weatherData?.let { "${it.humidity}%" } ?: "--")
                    Box(modifier = Modifier.height(24.dp).width(1.dp).background(Color.White.copy(alpha = 0.3f)))
                    WeatherStatItem(Icons.Rounded.Air, strings.weather.windSpeed, weatherData?.let { "${it.windSpeed.toInt()} km/h" } ?: "--")
                }
            }
        }
    }
}

@Composable
private fun AlertsHeroCard() {
    val currentLang = LocalAppLanguage.current
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
                    Column(modifier = Modifier.weight(1f, fill = false)) {
                        Text(
                            text = AppLocalizer.localizeDashboardPhrase("field alerts", currentLang),
                            style = MaterialTheme.typography.labelMedium.copy(
                                color = Color.White.copy(alpha = 0.9f),
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 12.sp
                            )
                        )
                        Text(
                            text = AppLocalizer.localizeDashboardPhrase("active notices", currentLang),
                            style = MaterialTheme.typography.titleLarge.copy(
                                color = Color.White,
                                fontWeight = FontWeight.ExtraBold,
                                fontSize = 20.sp,
                                lineHeight = 24.sp
                            )
                        )
                    }
                    Icon(
                        Icons.Rounded.ErrorOutline,
                        null,
                        tint = Color.White,
                        modifier = Modifier.size(28.dp)
                    )
                }

                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    AlertItem(
                        AppLocalizer.localizeDashboardPhrase("pest warning", currentLang),
                        AppLocalizer.localizeDashboardPhrase("pest warning desc", currentLang)
                    )
                    AlertItem(
                        AppLocalizer.localizeDashboardPhrase("market price drop", currentLang),
                        AppLocalizer.localizeDashboardPhrase("market price drop desc", currentLang)
                    )
                }

                Button(
                    onClick = { },
                    colors = ButtonDefaults.buttonColors(containerColor = Color.White.copy(alpha = 0.25f)),
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(horizontal = 18.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = AppLocalizer.localizeDashboardPhrase("review all alerts", currentLang),
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
        }
    }
}

@Composable
private fun AlertItem(title: String, desc: String) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
        Box(modifier = Modifier.size(6.5.dp).background(Color.White, CircleShape))
        Column(modifier = Modifier.weight(1f, fill = false)) {
            Text(title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.5.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text(desc, color = Color.White.copy(alpha = 0.9f), fontSize = 11.5.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
    }
}

@Composable
private fun SuggestionsHeroCard(suggestions: List<SuggestionPill>) {
    val currentLang = LocalAppLanguage.current
    Surface(
        modifier = Modifier.fillMaxSize().shadow(12.dp, RoundedCornerShape(32.dp)),
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
                        text = AppLocalizer.localizeDashboardPhrase("smart suggestions", currentLang),
                        style = MaterialTheme.typography.labelMedium.copy(
                            color = Color.White.copy(alpha = 0.9f),
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 12.sp
                        )
                    )
                    Text(
                        text = AppLocalizer.localizeDashboardPhrase("ai farm tips", currentLang),
                        style = MaterialTheme.typography.titleLarge.copy(
                            color = Color.White,
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 20.sp,
                            lineHeight = 24.sp
                        )
                    )
                }

                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    suggestions.take(2).forEach { suggestion ->
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            Icon(suggestion.icon, null, tint = Color.White, modifier = Modifier.size(18.dp))
                            Column(modifier = Modifier.weight(1f, fill = false)) {
                                Text(suggestion.title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.5.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                Text(suggestion.note, color = Color.White.copy(alpha = 0.9f), fontSize = 11.5.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            }
                        }
                    }
                }

                Text(
                    text = AppLocalizer.localizeDashboardPhrase("discover more tailored advice", currentLang),
                    color = Color.White.copy(alpha = 0.8f),
                    fontSize = 11.sp,
                    lineHeight = 14.sp,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
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
    val strings = LocalStrings.current
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
                text = strings.dashboard.farmActions,
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
    val strings = LocalStrings.current
    Column(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = strings.dashboard.cropServices,
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