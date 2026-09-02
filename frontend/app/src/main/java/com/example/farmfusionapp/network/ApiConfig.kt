package com.example.farmfusionapp.network

object ApiConfig {
    // Current Laptop Wi-Fi Local Network IP (interface wlp2s0):
    const val BASE_URL = "http://10.188.230.222:8000/"

    // If connected via USB with 'adb reverse tcp:8000 tcp:8000', you can also use:
    // const val BASE_URL = "http://127.0.0.1:8000/"

    // If running on Android Studio Emulator:
    // const val BASE_URL = "http://10.0.2.2:8000/"

    // If using Render cloud deployment:
    // const val BASE_URL = "https://farmfusion1.onrender.com/"
}
