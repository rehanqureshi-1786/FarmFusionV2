package com.example.farmfusionapp.network

object ApiConfig {
    // Default to localhost so a real Android device connected via USB (adb reverse)
    // can reach the local backend. Change to your deployed URL for production.
    const val BASE_URL = "http://10.44.57.226:8000/"

    // If you need the Render cloud backend, set to:
    // const val BASE_URL = "https://farmfusion1.onrender.com/"

    // If you run on the Android emulator instead, use:
    // const val BASE_URL = "http://10.0.2.2:8000/"
}
