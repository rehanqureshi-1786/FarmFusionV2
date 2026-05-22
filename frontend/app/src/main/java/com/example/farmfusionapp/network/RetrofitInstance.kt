package com.example.farmfusionapp.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitInstance {

    /**
     * OkHttp client with logging and timeouts
     * Used for all APIs
     */
    private val okHttpClient: OkHttpClient by lazy {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        OkHttpClient.Builder()
            .addInterceptor { chain ->
                // Render free tier returns 503 while the service wakes from sleep.
                var request = chain.request()
                var response = chain.proceed(request)
                var attempt = 0
                while (response.code == 503 && attempt < 3) {
                    response.close()
                    attempt++
                    Thread.sleep(15_000L)
                    response = chain.proceed(request)
                }
                response
            }
            .addInterceptor(logging)
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()
    }

    /**
     * External Weather API (OpenWeatherMap)
     */
    val openWeatherApi: WeatherApi by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.openweathermap.org/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(WeatherApi::class.java)
    }

    /**
     * FarmFusion Backend API (Your FastAPI server)
     * Used for crop recommendations, disease detection, market prices, etc.
     */
    val farmFusionApi: FarmFusionApi by lazy {
        Retrofit.Builder()
            .baseUrl(ApiConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(FarmFusionApi::class.java)
    }

    /**
     * Convenience alias for farmFusionApi
     * Used in ViewModels
     */
    val api: FarmFusionApi
        get() = farmFusionApi
}
