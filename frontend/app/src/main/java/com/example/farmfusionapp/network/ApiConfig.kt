package com.example.farmfusionapp.network

import com.example.farmfusionapp.BuildConfig

/**
 * Global Network Configuration for FarmFusion Android client.
 *
 * BASE_URL is automatically selected based on the active Build Variant:
 * - Debug:   http://10.0.2.2:8000/ (Android Studio Emulator) or ADB reverse
 * - Release: https://farmfusion1.onrender.com/ (Production public HTTPS endpoint)
 *
 * For physical device testing over USB:
 *   Run `adb reverse tcp:8000 tcp:8000` from your workstation terminal.
 */
object ApiConfig {
    val BASE_URL: String = BuildConfig.BASE_URL
}

