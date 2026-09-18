package com.example.farmfusionapp.ui.screens

import android.app.Activity
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.TrendingUp
import androidx.compose.material.icons.rounded.Person
import androidx.compose.material.icons.rounded.Storefront
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalConfiguration
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

                val screenWidth = LocalConfiguration.current.screenWidthDp.dp
                val statusBarTop = WindowInsets.statusBars.asPaddingValues().calculateTopPadding()
                // ill_header_bg is 1254x1254 (1:1), with the visual illustration artwork concluding at y ≈ 1160px
                val illustrationEnd = screenWidth * (1160f / 1254f)
                var headerHeightPx by remember { mutableIntStateOf(0) }
                val headerHeightDp = if (density > 0f && headerHeightPx > 0) (headerHeightPx / density).dp else 115.dp
                val totalHeaderBottom = statusBarTop + 14.dp + headerHeightDp
                val spacerHeight = if (illustrationEnd > totalHeaderBottom) illustrationEnd - totalHeaderBottom else 16.dp

                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(
                        start = 0.dp,
                        end = 0.dp,
                        top = statusBarTop + 14.dp,
                        bottom = 36.dp
                    )
                ) {
                    item {
                        Column(
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 20.dp)
                                    .onGloballyPositioned { coords ->
                                        headerHeightPx = coords.size.height
                                    }
                            ) {
                                HomeHeroHeader(location = locationName)

                                // Round User Profile Icon
                                Surface(
                                    onClick = {
                                        navController.navigate(NavRoutes.BuyerProfile)
                                    },
                                    modifier = Modifier
                                        .align(Alignment.TopEnd)
                                        .size(44.dp),
                                    shape = CircleShape,
                                    color = Color.White.copy(alpha = 0.95f),
                                    border = BorderStroke(1.5.dp, Color(0xFFC8E6C9)),
                                    shadowElevation = 3.dp
                                ) {
                                    Box(contentAlignment = Alignment.Center) {
                                        Icon(
                                            imageVector = Icons.Rounded.Person,
                                            contentDescription = "Profile",
                                            tint = Color(0xFF1B5E20),
                                            modifier = Modifier.size(24.dp)
                                        )
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(spacerHeight))

                            // Two Feature Cards: Price Trends & Available Listings
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
}
