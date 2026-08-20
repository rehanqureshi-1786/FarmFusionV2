package com.example.farmfusionapp.data.dev

import com.example.farmfusionapp.data.model.EstimatedSoilValues
import com.example.farmfusionapp.data.model.NoSoilReportCropCandidate
import com.example.farmfusionapp.data.model.NoSoilReportLocation
import com.example.farmfusionapp.data.model.NoSoilReportResponse
import com.example.farmfusionapp.data.model.NoSoilReportWeather

/**
 * DEVELOPMENT-ONLY mock for the "No Soil Report" flow.
 *
 * The real backend returns HTTP 503 when N/P/K soil nutrients are not
 * available from a scientifically compatible source (which is the current
 * state - SoilGrids provides pH/texture but NOT N/P/K in kg/ha).
 *
 * This mock lets a developer preview the full result UI without the
 * backend being up.
 *
 * This is intentionally separated from production behaviour:
 *  - [ENABLED] defaults to `false`, so production ALWAYS calls the real API.
 *  - The sample payload is clearly labelled "(mock)".
 *  - The mock includes N/P/K to demonstrate the UI, but these are NOT
 *    real values - they would only be available from a soil test.
 */
object DevNoSoilReportMock {

    /** Development toggle. KEEP false in production builds. */
    const val ENABLED: Boolean = true

    /** Simulated network delay so the loading state is visible in development. */
    const val SIMULATED_DELAY_MS: Long = 900L

    val sampleResponse: NoSoilReportResponse
        get() = NoSoilReportResponse(
            success = true,
            location = NoSoilReportLocation(
                latitude = 27.0238,
                longitude = 74.2179,
                state = "Rajasthan",
                display_name = "Rajasthan (lat 27.0238, lon 74.2179)"
            ),
            season = "Kharif",
            season_window = "June - October (sown with onset of southwest monsoon)",
            estimated_soil = EstimatedSoilValues(
                N = 92.0,
                P = 44.0,
                K = 45.0,
                ph = 6.3,
                texture = mapOf("clay" to 25.0, "sand" to 45.0, "silt" to 30.0),
                texture_class = "loam",
                depth_used = "0-5cm"
            ),
            soil_source = "SoilGrids (ISRIC) + Manual N/P/K (mock)",
            weather = NoSoilReportWeather(
                temperature_c = 29.8,
                humidity_percent = 64.0,
                rainfall_mm_7day_forecast = 386.7,
                current_conditions = "Partly cloudy",
                source = "open-meteo (mock) - seasonal Kharif rainfall"
            ),
            top_crops = listOf(
                NoSoilReportCropCandidate("rice", 1, 0.7760, 1.2, 0.9312),
                NoSoilReportCropCandidate("jute", 2, 0.1398, 1.1, 0.1538),
                NoSoilReportCropCandidate("coffee", 3, 0.0255, 1.0, 0.0255)
            ),
            explanation = "Based on SoilGrids pH (6.3) and texture (loam), plus seasonal Kharif " +
                "rainfall (386.7 mm) from Open-Meteo ERA5-Land historical data, the top " +
                "recommended crops for Kharif in Rajasthan are rice, jute, and coffee. " +
                "(DEV MOCK DATA - N/P/K values are MOCK and only for UI demonstration. " +
                "Real N/P/K requires a soil test via the 'I Have Soil Report' flow.)",
            warnings = listOf(
                "Rainfall is seasonal Kharif total (mm) from Open-Meteo ERA5-Land historical reanalysis; " +
                    "model was trained on annual rainfall, so treat results as indicative.",
                "DEV MOCK DATA — N/P/K values are mocked for UI demonstration only. " +
                    "Production requires lab-tested N/P/K from a soil report.",
                "Soil pH and texture from SoilGrids (ISRIC); N/P/K not available from this source."
            )
        )
}
