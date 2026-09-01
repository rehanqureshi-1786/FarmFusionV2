package com.example.farmfusionapp.data.model

/**
 * Data classes for Crop Recommendation API
 * These match the JSON structure from your FastAPI backend
 */

/**
 * Request sent TO backend when asking for crop recommendations
 * Matches backend: CropRecommendRequest
 */
data class CropRecommendRequest(
    val location: String,
    val soil_type: String,
    val rainfall_mm: Double,
    val temperature_c: Double,
    val farm_size_acres: Double,
    val budget_usd: Double? = null,
    val preferred_language: String = "en",
    val latitude: Double? = null,
    val longitude: Double? = null,
    val nitrogen: Double? = null,
    val phosphorus: Double? = null,
    val potassium: Double? = null,
    val ph: Double? = null
)

/**
 * Response received FROM backend with recommendations
 * Matches backend: CropRecommendResponse
 */
data class CropRecommendResponse(
    val success: Boolean,
    val recommendations: List<CropRecommendationItem>,
    val ai_insights: String,
    val timestamp: String
)

/**
 * Single crop recommendation details
 * Matches backend: CropRecommendation
 */
data class CropRecommendationItem(
    val crop_name: String,
    val confidence_score: Double,
    val expected_yield_tons: Double,
    val market_demand: String,
    val estimated_profit_usd: Double,
    val growing_duration_months: Int,
    val water_requirement: String
) {
    /**
     * Helper function to format confidence as percentage
     * Example: 0.92 → "92%"
     */
    fun confidencePercentage(): String {
        return "${(confidence_score * 100).toInt()}%"
    }

    /**
     * Helper function to format profit with currency
     */
    fun formattedProfit(): String {
        return "₹${(estimated_profit_usd * 83).toInt()}" // Convert USD to INR roughly
    }

    /**
     * Get emoji for crop
     */
    fun cropEmoji(): String {
        return when (crop_name.lowercase()) {
            "maize", "corn" -> "🌽"
            "wheat" -> "🌾"
            "rice" -> "🍚"
            "cotton" -> "☁️"
            "sugarcane" -> "🎋"
            "tomatoes", "tomato" -> "🍅"
            "potatoes", "potato" -> "🥔"
            "beans" -> "🫘"
            "groundnuts", "peanuts" -> "🥜"
            else -> "🌱"
        }
    }

    /**
     * Get demand indicator emoji
     */
    fun demandEmoji(): String {
        return when (market_demand.lowercase()) {
            "high" -> "📈"
            "medium" -> "➡️"
            "low" -> "📉"
            else -> "📊"
        }
    }

    /**
     * Get water requirement emoji
     */
    fun waterEmoji(): String {
        return when (water_requirement.lowercase()) {
            "high" -> "💧💧💧"
            "medium" -> "💧💧"
            "low" -> "💧"
            else -> "💧"
        }
    }
}
