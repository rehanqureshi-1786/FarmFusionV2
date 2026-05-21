package com.example.farmfusionapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.example.farmfusionapp.ui.screens.AppNav
import com.example.farmfusionapp.ui.theme.FarmFusionAppTheme
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.utils.LocaleHelper
import com.example.farmfusionapp.utils.LocationPermissionEffect

class MainActivity : ComponentActivity() {
    override fun attachBaseContext(newBase: android.content.Context) {
        val lang = AuthStore.getLanguage(newBase) ?: "en"
        super.attachBaseContext(LocaleHelper.wrap(newBase, lang))
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            FarmFusionAppTheme {
                val context = LocalContext.current
                var permissionGranted by remember { mutableStateOf(false) }

                // Request location permission immediately on app startup
                LocationPermissionEffect(
                    context = context,
                    onPermissionGranted = { permissionGranted = true },
                    onPermissionDenied = { /* Handled in specific screens if needed */ }
                )

                Surface(
                    modifier = Modifier.fillMaxSize()
                ) {
                    AppNav()
                }
            }
        }
    }
}
