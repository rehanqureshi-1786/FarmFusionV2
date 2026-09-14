package com.example.farmfusionapp.network

import com.example.farmfusionapp.BuildConfig

/**
 * Global Network Configuration for FarmFusion Android client.
 *
 * BASE_URL points to the live Railway production cloud backend:
 * https://farmfusion-backend-production-0017.up.railway.app/
 */
object ApiConfig {
    val BASE_URL: String = BuildConfig.BASE_URL.ifEmpty {
        "https://farmfusion-backend-production-0017.up.railway.app/"
    }
}
