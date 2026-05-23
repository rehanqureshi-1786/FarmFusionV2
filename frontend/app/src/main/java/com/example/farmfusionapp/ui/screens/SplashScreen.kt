package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavController
import com.example.farmfusionapp.viewmodel.AuthViewModel

/**
 * SplashScreen - Initial loading screen to verify session
 */
@Composable
fun SplashScreen(navController: NavController, viewModel: AuthViewModel) {
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        // Authentication disabled for local development — go directly to dashboard
        navController.navigate(NavRoutes.Dashboard) {
            popUpTo(NavRoutes.Splash) { inclusive = true }
        }
    }

    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator()
    }
}
