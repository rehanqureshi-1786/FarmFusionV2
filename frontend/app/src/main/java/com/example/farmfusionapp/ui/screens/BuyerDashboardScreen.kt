package com.example.farmfusionapp.ui.screens

import android.app.Activity
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.TrendingUp
import androidx.compose.material.icons.rounded.NotificationsActive
import androidx.compose.material.icons.rounded.Storefront
import androidx.compose.material.icons.rounded.TipsAndUpdates
import androidx.compose.material.icons.rounded.WaterDrop
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.utils.AppLocalizer
import com.example.farmfusionapp.utils.LanguagePreferences
import com.example.farmfusionapp.utils.LocationPermissionEffect
import com.example.farmfusionapp.utils.LocationSnapshotStore
import com.example.farmfusionapp.utils.getCityFromLocation
import kotlinx.coroutines.launch

@Composable
fun BuyerDashboardScreen(navController: NavController) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val scope = rememberCoroutineScope()
    val view = LocalView.current

    var weatherData by remember { mutableStateOf(WeatherSnapshotStore.latestWeather) }
    var locationName by remember { mutableStateOf(WeatherSnapshotStore.latestWeather?.city ?: "Waiting for location...") }
    var hasLocationPermission by remember { mutableStateOf(false) }

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
    val itemHeights = remember { mutableMapOf<Int, Int>() }

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

    // Buyer feature cards: 2 prominent action cards
    val buyerActions = remember {
        listOf(
            HomeAction(
                title = "Price Trends",
                subtitle = "Live Mandi Rates",
                iconVector = Icons.AutoMirrored.Rounded.TrendingUp,
                route = NavRoutes.BuyerPriceTrends,
                colors = listOf(Color(0xFFEAF1FF), Color(0xFFCFE0FF)),
                iconTint = Color(0xFF235CA8),
                illustration = R.drawable.ill_market_prices
            ),
            HomeAction(
                title = "Available Listings",
                subtitle = "Direct Farmer Stocks",
                iconVector = Icons.Rounded.Storefront,
                route = NavRoutes.AvailableListings,
                colors = listOf(Color(0xFFE8F7E8), Color(0xFFCBE8CF)),
                iconTint = Color(0xFF246B3B),
                illustration = R.drawable.ill_crop_services
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
                            onWeatherClick = {
                                navController.navigate(NavRoutes.Weather) {
                                    popUpTo(NavRoutes.BuyerDashboard) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            onCallClick = {
                                dialKisanHelpline(context)
                            },
                            onVoiceClick = {
                                navController.navigate(NavRoutes.VoiceAssistant) {
                                    popUpTo(NavRoutes.BuyerDashboard) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }

                    item {
                        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                            FarmingAssistantCallCard(
                                onCallClick = { dialKisanHelpline(context) },
                                onVoiceClick = {
                                    navController.navigate(NavRoutes.VoiceAssistant) {
                                        popUpTo(NavRoutes.BuyerDashboard) {
                                            saveState = true
                                        }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                },
                                title = "AI Buying Assistant",
                                description = "Speak directly to your AI assistant for mandi prices, crop arrivals, quality guidance, and more."
                            )
                        }
                    }

                    // Two Feature Cards: Price Trends & Available Listings
                    item {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 20.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            Text(
                                text = "Market & Sourcing",
                                style = MaterialTheme.typography.titleLarge.copy(
                                    fontWeight = FontWeight.ExtraBold,
                                    color = Color(0xFF1B5E20)
                                )
                            )

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                buyerActions.forEach { action ->
                                    ModernActionCard(
                                        modifier = Modifier.weight(1f),
                                        action = action,
                                        onClick = {
                                            navController.navigate(action.route) {
                                                popUpTo(NavRoutes.BuyerDashboard) {
                                                    saveState = true
                                                }
                                                launchSingleTop = true
                                                restoreState = true
                                            }
                                        }
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
