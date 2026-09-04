package com.example.farmfusionapp.network

object ApiConfig {

    // Active for USB with `adb reverse tcp:8000 tcp:8000`:
    //const val BASE_URL = "http://127.0.0.1:8000/"

    // Laptop Wi-Fi IP (if running over Wi-Fi without USB):
    const val BASE_URL = "http://10.44.57.226:8000/"

    // If running on Android Studio Emulator:
    // const val BASE_URL = "http://10.0.2.2:8000/"

    // If using Render cloud deployment:
    // const val BASE_URL = "https://farmfusion1.onrender.com/"
}