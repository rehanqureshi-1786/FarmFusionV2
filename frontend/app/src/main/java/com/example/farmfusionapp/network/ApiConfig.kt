package com.example.farmfusionapp.network

object ApiConfig {
    // Android emulator default: 10.0.2.2 points to the host machine's localhost.
    // Real device on the same Wi‑Fi: replace with your machine's LAN IP, e.g. http://192.168.1.10:8000/
    const val BASE_URL = "http://localhost:8000/"

    // If you need the Render cloud backend, use:
    // const val BASE_URL = "https://farmfusion1.onrender.com/"

    // If you use a physical device on the same network, use your computer's local IP:
    // const val BASE_URL = "http://192.168.31.2:8000/"
}
