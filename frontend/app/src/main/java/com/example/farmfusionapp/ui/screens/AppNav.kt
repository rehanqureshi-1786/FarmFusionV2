package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.compose.*
import com.example.farmfusionapp.ui.components.GlassFloatingVoiceButton
import com.example.farmfusionapp.ui.components.HomeBottomBar
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.viewmodel.AuthViewModel

import dev.chrisbanes.haze.HazeState
import dev.chrisbanes.haze.haze

// GLOBAL BLUR TRIGGER
val LocalGlobalBlur = compositionLocalOf<MutableState<Boolean>> {
    error("No global blur state provided")
}

object NavRoutes {
    const val LanguageSelection = "language_selection"
    const val Splash = "splash"
    const val Login = "login"
    const val Register = "register"
    const val Dashboard = "dashboard"
    const val CropServices = "crop_services"
    const val CropRecommendation = "crop_recommendation"
    const val CropSowing = "crop_sowing"
    const val CropMonitoring = "crop_monitoring"
    const val CropDisease = "crop_disease"
    const val CropHarvesting = "crop_harvesting"
    const val CropSelling = "crop_selling"
    const val AnimalDetection = "animal_detection"
    const val LabourServices = "labour_services"
    const val MandiPrices = "mandi_prices"
    const val ProductStore = "product_store"
    const val DynamicStore = "dynamic_store" // ADDED: Preserved Backend Logic Route
    const val FinancialServices = "financial_services"
    const val Weather = "weather"
    const val VoiceAssistant = "voice_assistant"
    const val Alerts = "alerts"
    const val Profile = "profile"
    const val Settings = "settings"
}

@Composable
fun AppNav() {
    val authViewModel: AuthViewModel = remember { AuthViewModel() }
    val navController = rememberNavController()
    val context = LocalContext.current
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    // RESTORED: CropDisease included so the nav bar remains visible
    val mainRoutes = listOf(
        NavRoutes.Dashboard,
        NavRoutes.MandiPrices,
        NavRoutes.CropDisease,
        NavRoutes.Weather,
        NavRoutes.Profile
    )

    val showBottomBar = currentRoute in mainRoutes

    // Mic only appears on the Dashboard (Home Screen)
    val showMicButton = currentRoute == NavRoutes.Dashboard

    val savedLanguage = AuthStore.getLanguage(context)
    val startDestination = if (savedLanguage == null) {
        NavRoutes.LanguageSelection
    } else {
        NavRoutes.Splash
    }

    // Permanent enlarge on Dashboard, permanent shrink everywhere else
    val forceShrink = currentRoute != NavRoutes.Dashboard

    val hazeState = remember { HazeState() }
    val globalBlurState = remember { mutableStateOf(false) }

    val globalBlurRadius by animateDpAsState(
        targetValue = if (globalBlurState.value) 16.dp else 0.dp,
        animationSpec = tween(durationMillis = 300),
        label = "global_blur"
    )

    CompositionLocalProvider(LocalGlobalBlur provides globalBlurState) {
        Scaffold(
            containerColor = Color(0xFFF4F9F4), // Unified soft green background
            modifier = Modifier
                .fillMaxSize()
                .blur(radius = globalBlurRadius),
            bottomBar = {
                if (showBottomBar) {
                    Box(
                        modifier = Modifier
                            .navigationBarsPadding()
                            .padding(horizontal = 20.dp, vertical = 16.dp)
                    ) {
                        HomeBottomBar(
                            navController = navController,
                            currentRoute = currentRoute,
                            isShrunk = forceShrink,
                            hazeState = hazeState
                        )
                    }
                }
            },
            floatingActionButton = {
                if (showMicButton) {
                    GlassFloatingVoiceButton(
                        modifier = Modifier
                            .navigationBarsPadding()
                            .offset(y = 38.dp),
                        onClick = { navController.navigate(NavRoutes.VoiceAssistant) }
                    )
                }
            }
        ) { _ ->
            NavHost(
                navController = navController,
                startDestination = startDestination,
                modifier = Modifier.fillMaxSize().haze(state = hazeState)
            ) {
                composable(NavRoutes.LanguageSelection) { LanguageSelectionScreen(navController) }
                composable(NavRoutes.Splash) { SplashScreen(navController, authViewModel) }
                composable(NavRoutes.Login) { LoginScreen(navController) }
                composable(NavRoutes.Register) { RegisterScreen(navController) }
                composable(NavRoutes.Dashboard) { DashboardScreen(navController) }
                composable(NavRoutes.CropServices) { CropServicesScreen(navController) }
                composable(NavRoutes.CropRecommendation) { CropRecommendationScreen(navController) }
                composable(NavRoutes.CropSowing) { CropSowingScreen(navController) }
                composable(NavRoutes.CropMonitoring) { CropMonitoringScreen(navController) }
                composable(NavRoutes.CropDisease) { CropDiseaseScreen(navController) }
                composable(NavRoutes.CropHarvesting) { CropHarvestingScreen(navController) }
                composable(NavRoutes.CropSelling) { CropSellingScreen(navController) }
                composable(NavRoutes.AnimalDetection) { AnimalDetectionScreen(navController) }
                composable(NavRoutes.LabourServices) { LabourServicesScreen(navController) }
                composable(NavRoutes.MandiPrices) { MandiPricesScreen(navController) }

                // UPDATED: The split route logic for your Farm Store
                composable(NavRoutes.ProductStore) { MarketplaceScreen(navController) } // New Premium UI
                composable(NavRoutes.DynamicStore) { StoreRecommendationsScreen(navController) } // Safe Dynamic Logic

                composable(NavRoutes.FinancialServices) { FinancialServicesScreen(navController) }
                composable(NavRoutes.Weather) { WeatherScreen(navController) }
                composable(NavRoutes.VoiceAssistant) { VoiceAssistantScreen(navController) }
                composable(NavRoutes.Alerts) { AlertsScreen(navController) }
                composable(NavRoutes.Profile) { ProfileScreen(navController) }
            }
        }
    }
}