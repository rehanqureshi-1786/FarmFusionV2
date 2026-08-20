package com.example.farmfusionapp.data.model

/**
 * Data classes for the "No Soil Report" crop recommendation flow.
 *
 * These match the FastAPI endpoint:
 *     POST /api/v1/crop-recommendation/no-soil-report
 *
 * Field names map 1:1 to the backend JSON (snake_case, plus the literal
 * uppercase "N"/"P"/"K"/"ph" keys inside `estimated_soil`), so Gson can parse
 * them without extra annotations. Optional fields are nullable so the app is
 * resilient to a malformed / partial response.
 */

/** Request sent to the backend. `state` is optional. */
data class NoSoilReportRequest(
    val latitude: Double,
    val longitude: Double,
    val state: String? = null
)

/** Response from the backend. */
data class NoSoilReportResponse(
    val success: Boolean = false,
    val location: NoSoilReportLocation? = null,
    val season: String? = null,
    val season_window: String? = null,
    val estimated_soil: EstimatedSoilValues? = null,
    val soil_source: String? = null,
    val weather: NoSoilReportWeather? = null,
    val top_crops: List<NoSoilReportCropCandidate>? = null,
    val explanation: String? = null,
    val warnings: List<String>? = null
)

data class NoSoilReportLocation(
    val latitude: Double = 0.0,
    val longitude: Double = 0.0,
    val state: String? = null,
    val display_name: String? = null
)

/** N/P/K/pH are the literal keys used by the backend. Texture info is optional. */
data class EstimatedSoilValues(
    val N: Double = 0.0,
    val P: Double = 0.0,
    val K: Double = 0.0,
    val ph: Double = 0.0,
    val texture: Map<String, Double>? = null,
    val texture_class: String? = null,
    val depth_used: String? = null
)

data class NoSoilReportWeather(
    val temperature_c: Double = 0.0,
    val humidity_percent: Double = 0.0,
    val rainfall_mm_7day_forecast: Double = 0.0,
    val rainfall_mm: Double? = null,
    val rainfall_source: String? = null,
    val current_conditions: String? = null,
    val source: String? = null
)

data class NoSoilReportCropCandidate(
    val crop_name: String = "",
    val rank: Int = 0,
    val model_probability: Double = 0.0,
    val regional_score: Double = 0.0,
    val final_score: Double = 0.0
)
