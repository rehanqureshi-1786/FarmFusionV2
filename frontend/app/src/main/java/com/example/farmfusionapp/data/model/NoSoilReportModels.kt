package com.example.farmfusionapp.data.model

/**
 * Data classes for the "No Soil Report" crop recommendation and Environmental Suitability flow.
 *
 * Matches the FastAPI endpoint:
 *     POST /api/v1/crop-recommendation/no-soil-report
 */

/** Request sent to the backend. `state`, `soil_type`, and `location_name` are optional. */
data class NoSoilReportRequest(
    val latitude: Double,
    val longitude: Double,
    val state: String? = null,
    val farmer_selected_soil_type: String? = null,
    val soil_type: String? = null,
    val location_name: String? = null
)

/** Single value with complete source and status metadata. */
data class ProvenanceField(
    val value: Any? = null,
    val unit: String? = null,
    val source: String? = null,
    val status: String = "REAL",
    val estimated: Boolean = false,
    val requires_soil_test: Boolean = false,
    val note: String? = null,
    val period: String? = null,
    val depth: String? = null
) {
    fun getDoubleValue(): Double? {
        return when (value) {
            is Number -> value.toDouble()
            is String -> value.toDoubleOrNull()
            else -> null
        }
    }

    fun getDisplayString(): String {
        val d = getDoubleValue()
        return when {
            d != null && unit != null -> "${String.format(java.util.Locale.US, "%.1f", d)} $unit"
            d != null -> String.format(java.util.Locale.US, "%.1f", d)
            value != null && value.toString().isNotBlank() && value.toString() != "None" && value.toString() != "null" -> value.toString()
            else -> "Unavailable"
        }
    }
}

data class ProvenanceLocation(
    val latitude: Double = 0.0,
    val longitude: Double = 0.0,
    val display_name: String? = null,
    val state: String? = null,
    val source: String = "Device GPS"
)

data class ProvenanceWeather(
    val temperature: ProvenanceField? = null,
    val humidity: ProvenanceField? = null,
    val current_conditions: String? = null,
    val weather_available: Boolean = true
)

data class ProvenanceRainfall(
    val annual_rainfall: ProvenanceField? = null,
    val period: String? = "2025",
    val rainfall_available: Boolean = true
)

data class ProvenanceSoil(
    val farmer_selected_type: String? = null,
    val ph: ProvenanceField? = null,
    val sand: ProvenanceField? = null,
    val clay: ProvenanceField? = null,
    val silt: ProvenanceField? = null,
    val texture_class: String? = null,
    val depth_used: String? = "0-5cm",
    val soil_data_available: Boolean = false
)

data class ProvenanceNutrients(
    val nitrogen: ProvenanceField? = null,
    val phosphorus: ProvenanceField? = null,
    val potassium: ProvenanceField? = null
)

data class EnvironmentalCropRecommendation(
    val crop_name: String = "",
    val hindi_name: String? = null,
    val suitability_level: String = "Suitable",
    val suitability_score: Double = 0.0,
    val season: String = "Kharif",
    val water_requirement: String? = null,
    val contributing_factors: List<String>? = null,
    val management_notes: List<String>? = null
)

/** Response from the backend with data provenance and environmental suitability recommendations. */
data class NoSoilReportResponse(
    val success: Boolean = false,
    val recommendation_available: Boolean = true,
    val recommendation_mode: String = "ENVIRONMENTAL_SUITABILITY",
    val reason: String? = null,
    val message: String? = null,
    val location: ProvenanceLocation? = null,
    val weather: ProvenanceWeather? = null,
    val rainfall: ProvenanceRainfall? = null,
    val soil: ProvenanceSoil? = null,
    val nutrients: ProvenanceNutrients? = null,
    val soil_parameters: Map<String, Any>? = null,
    val recommendations: List<EnvironmentalCropRecommendation>? = null,
    val season: String? = null,
    val season_window: String? = null,
    val soil_source: String? = null,
    val explanation: String? = null,
    val warnings: List<String>? = null
)
