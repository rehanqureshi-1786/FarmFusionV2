package com.example.farmfusionapp.data.soilreport

/**
 * Data model for soil report values extracted by OCR and verified by the farmer.
 *
 * These are the N/P/K/pH inputs that feed the backend's `CropRecommendationInput`
 * contract. Values and units are preserved as reported; nothing is silently
 * converted. If a value could not be detected, [status] is [SoilValueStatus.MISSING]
 * and the farmer is required to supply it before the API is called.
 */
enum class SoilValueStatus {
    /** Value was read by OCR from the soil report. */
    DETECTED,

    /** Value was not found by OCR and must be entered by the farmer. */
    MISSING,

    /** Value was entered/corrected by the farmer manually. */
    MANUAL
}

/**
 * A single soil property with the reported value and its unit.
 *
 * @param value numeric value if known, else null
 * @param unit  the unit exactly as reported (e.g. "kg/ha", "ppm", "mg/kg").
 *              "unknown" when the OCR text did not include a recognizable unit.
 * @param status provenance of the value (OCR / missing / manual)
 */
data class SoilReportValue(
    val value: Double? = null,
    val unit: String? = null,
    val status: SoilValueStatus = SoilValueStatus.MISSING
) {
    val isPresent: Boolean get() = value != null

    /** Return a copy with a manually supplied value, clearly labelled MANUAL. */
    fun withManualValue(newValue: Double): SoilReportValue =
        copy(value = newValue, status = SoilValueStatus.MANUAL, unit = unit ?: "unknown")
}

/**
 * Result of OCR over a soil report photo.
 *
 * @param warnings human-readable notes (e.g. suspicious pH) surfaced for the
 *                  farmer to review — never used to silently discard data.
 */
data class SoilReportOcrResult(
    val nitrogen: SoilReportValue = SoilReportValue(),
    val phosphorus: SoilReportValue = SoilReportValue(),
    val potassium: SoilReportValue = SoilReportValue(),
    val ph: SoilReportValue = SoilReportValue(),
    val warnings: List<String> = emptyList()
) {
    /** True only when every required value is present and could be submitted. */
    val isComplete: Boolean
        get() = nitrogen.isPresent && phosphorus.isPresent && potassium.isPresent && ph.isPresent
}
