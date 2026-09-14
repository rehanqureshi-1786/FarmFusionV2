package com.example.farmfusionapp.network

import com.example.farmfusionapp.BuildConfig

/**
 * Global Network Configuration for FarmFusion Android client.
 *
 * BASE_URL is automatically selected based on the active Build Variant:
 * - Debug & Release: https://farmfusion-backend-production-0017.up.railway.app/
 *
 * For local physical device testing over USB:
 *   Run `adb reverse tcp:8000 tcp:8000` from your workstation terminal.
 */
object ApiConfig {
    val BASE_URL: String = BuildConfig.BASE_URL
}

