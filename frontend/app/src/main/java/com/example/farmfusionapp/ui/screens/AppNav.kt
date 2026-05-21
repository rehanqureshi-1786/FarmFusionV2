package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.compose.*
import com.example.farmfusionapp.ui.components.GlassFloatingVoiceButton
import com.example.farmfusionapp.ui.components.HomeBottomBar
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.viewmodel.AuthViewModel

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

    val mainRoutes = listOf(
        NavRoutes.Dashboard,
        NavRoutes.MandiPrices,
        NavRoutes.CropDisease,
        NavRoutes.Weather,
        NavRoutes.Profile
    )
    
    val showBottomBar = currentRoute in mainRoutes

    val startDestination = NavRoutes.Splash

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                Surface(
                    modifier = Modifier
                        .navigationBarsPadding()
                        .padding(horizontal = 20.dp, vertical = 12.dp)
                        .height(68.dp),
                    shape = RoundedCornerShape(20.dp),
                    color = Color.White.copy(alpha = 0.95f),
                    tonalElevation = 0.dp,
                    shadowElevation = 10.dp,
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFF0F0F0))
                ) {
                    HomeBottomBar(navController, currentRoute)
                }
            }
        },
        floatingActionButton = {
            if (showBottomBar) {
                GlassFloatingVoiceButton(
                    modifier = Modifier
                        .navigationBarsPadding()
                        .padding(bottom = 12.dp),
                    onClick = { navController.navigate(NavRoutes.VoiceAssistant) }
                )
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController, 
            startDestination = startDestination,
            modifier = Modifier.padding(if (showBottomBar) innerPadding else androidx.compose.foundation.layout.PaddingValues(0.dp))
        ) {
            // Language selection screen has been disabled.
            // composable(NavRoutes.LanguageSelection) {
            //     LanguageSelectionScreen(navController)
            // }

            composable(NavRoutes.Splash) {
                SplashScreen(navController, authViewModel)
            }

            composable(NavRoutes.Login) {
                LoginScreen(navController)
            }

            composable(NavRoutes.Register) {
                RegisterScreen(navController)
            }

            composable(NavRoutes.Dashboard) {
                DashboardScreen(navController)
            }

            composable(NavRoutes.CropServices) {
                CropServicesScreen(navController)
            }

            composable(NavRoutes.CropRecommendation) {
                CropRecommendationScreen(navController)
            }

            composable(NavRoutes.CropSowing) {
                CropSowingScreen(navController)
            }

            composable(NavRoutes.CropMonitoring) {
                CropMonitoringScreen(navController)
            }

            composable(NavRoutes.CropDisease) {
                CropDiseaseScreen(navController)
            }

            composable(NavRoutes.CropHarvesting) {
                CropHarvestingScreen(navController)
            }

            composable(NavRoutes.CropSelling) {
                CropSellingScreen(navController)
            }

            composable(NavRoutes.AnimalDetection) {
                AnimalDetectionScreen(navController)
            }

            composable(NavRoutes.LabourServices) {
                LabourServicesScreen(navController)
            }

            composable(NavRoutes.MandiPrices) {
                MandiPricesScreen(navController)
            }

            composable(NavRoutes.ProductStore) {
                ProductStoreScreen(navController)
            }

            composable(NavRoutes.FinancialServices) {
                FinancialServicesScreen(navController)
            }

            composable(NavRoutes.Weather) {
                WeatherScreen(navController)
            }

            composable(NavRoutes.VoiceAssistant) {
                VoiceAssistantScreen(navController)
            }

            composable(NavRoutes.Alerts) {
                AlertsScreen(navController)
            }

            composable(NavRoutes.Profile) {
                ProfileScreen(navController)
            }
        }
    }
}
