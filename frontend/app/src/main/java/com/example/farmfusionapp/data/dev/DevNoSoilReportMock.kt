package com.example.farmfusionapp.data.dev

import com.example.farmfusionapp.data.model.EnvironmentalCropRecommendation
import com.example.farmfusionapp.data.model.NoSoilReportResponse
import com.example.farmfusionapp.data.model.ProvenanceField
import com.example.farmfusionapp.data.model.ProvenanceLocation
import com.example.farmfusionapp.data.model.ProvenanceNutrients
import com.example.farmfusionapp.data.model.ProvenanceRainfall
import com.example.farmfusionapp.data.model.ProvenanceSoil
import com.example.farmfusionapp.data.model.ProvenanceWeather

/**
 * DEVELOPMENT-ONLY mock for the "No Soil Report" flow.
 *
 * ALWAYS disabled (ENABLED = false) in production builds.
 */
object DevNoSoilReportMock {

    /** Development toggle. ALWAYS false in production builds. */
    const val ENABLED: Boolean = false

    /** Simulated network delay so the loading state is visible in development. */
    const val SIMULATED_DELAY_MS: Long = 900L

    val sampleResponse: NoSoilReportResponse
        get() = NoSoilReportResponse(
            success = true,
            recommendation_available = true,
            recommendation_mode = "ENVIRONMENTAL_SUITABILITY",
            location = ProvenanceLocation(
                latitude = 24.5854,
                longitude = 73.7125,
                state = "Rajasthan",
                display_name = "Udaipur, Rajasthan, India",
                source = "Device GPS"
            ),
            season = "Kharif",
            season_window = "June - October (sown with onset of southwest monsoon)",
            weather = ProvenanceWeather(
                temperature = ProvenanceField(27.4, "°C", "Open-Meteo", "REAL"),
                humidity = ProvenanceField(68.0, "%", "Open-Meteo", "REAL"),
                current_conditions = "Partly cloudy",
                weather_available = true
            ),
            rainfall = ProvenanceRainfall(
                annual_rainfall = ProvenanceField(941.5, "mm", "Open-Meteo ERA5-Land", "REAL", period = "2025"),
                period = "2025",
                rainfall_available = true
            ),
            soil = ProvenanceSoil(
                farmer_selected_type = "Sandy Soil",
                ph = ProvenanceField(7.2, null, "SoilGrids (ISRIC)", "REAL", depth = "0-5cm"),
                sand = ProvenanceField(70.0, "%", "SoilGrids (ISRIC)", "REAL", depth = "0-5cm"),
                clay = ProvenanceField(15.0, "%", "SoilGrids (ISRIC)", "REAL", depth = "0-5cm"),
                silt = ProvenanceField(15.0, "%", "SoilGrids (ISRIC)", "REAL", depth = "0-5cm"),
                texture_class = "sandy_loam",
                depth_used = "0-5cm",
                soil_data_available = true
            ),
            nutrients = ProvenanceNutrients(
                nitrogen = ProvenanceField(null, "kg/ha", null, "UNAVAILABLE"),
                phosphorus = ProvenanceField(null, "kg/ha", null, "UNAVAILABLE"),
                potassium = ProvenanceField(null, "kg/ha", null, "UNAVAILABLE")
            ),
            recommendations = listOf(
                EnvironmentalCropRecommendation(
                    crop_name = "Pearl Millet (Bajra)",
                    hindi_name = "बाजरा",
                    suitability_level = "Highly Suitable",
                    suitability_score = 0.92,
                    season = "Kharif",
                    water_requirement = "Low (250 - 400 mm)",
                    contributing_factors = listOf(
                        "Current Kharif season matches optimal crop sowing window.",
                        "Selected Sandy Soil is highly suitable for root growth and nutrient exchange.",
                        "Annual rainfall (941.5 mm) is within viable crop threshold."
                    ),
                    management_notes = emptyList()
                ),
                EnvironmentalCropRecommendation(
                    crop_name = "Maize (Corn)",
                    hindi_name = "मक्का",
                    suitability_level = "Suitable",
                    suitability_score = 0.78,
                    season = "Kharif",
                    water_requirement = "Moderate (500 - 750 mm)",
                    contributing_factors = listOf(
                        "Annual rainfall meets precipitation requirements.",
                        "Temperature (27.4°C) is in optimal range."
                    ),
                    management_notes = listOf("Ensure proper field drainage.")
                )
            ),
            explanation = "Evaluated against ICAR/FAO agronomic criteria using real location, weather, and SoilGrids data.",
            warnings = listOf(
                "N/P/K soil nutrients are unavailable without a laboratory Soil Health Card."
            )
        )
}
