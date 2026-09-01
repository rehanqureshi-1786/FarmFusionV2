package com.example.farmfusionapp.data.soilreport

/**
 * Parser for soil report OCR text.
 *
 * Extracts N, P, K, and pH values from raw OCR text.
 * Supports various label formats and formatting variations.
 * Never invents missing values - missing values remain null.
 */
object SoilReportOcrParser {

    private const val NUM = "(\\d+(?:\\.\\d+)?)"
    private const val UNITS = "kg/ha|ppm|mg/kg|kg"

    /**
     * Result of parsing OCR text for soil report values.
     */
    data class ParsedSoilValues(
        val nitrogen: ParsedValue? = null,
        val phosphorus: ParsedValue? = null,
        val potassium: ParsedValue? = null,
        val ph: ParsedValue? = null
    ) {
        /** Whether all required values were found */
        val isComplete: Boolean
            get() = nitrogen != null && phosphorus != null && potassium != null && ph != null

        /** List of missing value names */
        val missing: List<String>
            get() = buildList {
                if (nitrogen == null) add("Nitrogen")
                if (phosphorus == null) add("Phosphorus")
                if (potassium == null) add("Potassium")
                if (ph == null) add("pH")
            }
    }

    /**
     * A parsed value with its source metadata.
     */
    data class ParsedValue(
        val value: Double,
        val unit: String?,           // e.g., "kg/ha", "ppm", "mg/kg"
        val rawText: String,         // Original OCR text segment
        val source: Source = Source.OCR
    ) {
        /** Human-readable display with unit */
        val displayText: String
            get() = when {
                unit != null && unit.isNotBlank() -> "$value $unit"
                else -> value.toString()
            }
    }

    /**
     * Source of the value.
     */
    enum class Source {
        OCR,            // Extracted from OCR
        MANUAL          // Entered/corrected by farmer
    }

    /**
     * Parse OCR text to extract N, P, K, pH values.
     *
     * @param ocrText Raw text from OCR
     * @return ParsedSoilValues with detected values (null if not found)
     */
    fun parse(ocrText: String): ParsedSoilValues {
        val lines = ocrText.lines()
            .map { it.trim() }
            .filter { it.isNotBlank() }

        return ParsedSoilValues(
            nitrogen = findNutrient(lines, "nitrogen|n"),
            phosphorus = findNutrient(lines, "phosphorus|p"),
            potassium = findNutrient(lines, "potassium|k"),
            ph = findPh(lines)
        )
    }

    /**
     * Try three strategies in order:
     *  1. Same-line:  "<label>[:=] <number> [unit]"
     *  2. Same-line:  "<label> <number> [unit]"   (separator lost by OCR)
     *  3. Next-line:  "<label>" line directly followed by "<number> [unit]"
     */
    private fun findNutrient(
        lines: List<String>,
        labelAlternation: String
    ): ParsedValue? {
        val label = "\\b(?:$labelAlternation)\\b"
        val sameLineSep = Regex("(?i)$label\\s*[=:]\\s*$NUM\\s*($UNITS)?")
        val sameLineLoose = Regex("(?i)^$label\\s+$NUM\\s*($UNITS)?\\s*$")

        for (line in lines) {
            val m = sameLineSep.find(line) ?: sameLineLoose.find(line)
            if (m != null) {
                val parsed = build(m.groupValues[1].toDouble(), m.groupValues.getOrNull(2), line)
                if (parsed != null) return parsed
            }
        }

        val labelOnly = Regex("(?i)^$label\\s*:?$")
        val valueLine = Regex("(?i)^$NUM\\s*($UNITS)?\\s*$")
        for (i in 0 until lines.size - 1) {
            if (labelOnly.matches(lines[i])) {
                val vm = valueLine.find(lines[i + 1])
                if (vm != null) {
                    val parsed = build(vm.groupValues[1].toDouble(), vm.groupValues.getOrNull(2), lines[i + 1])
                    if (parsed != null) return parsed
                }
            }
        }
        return null
    }

    private fun findPh(lines: List<String>): ParsedValue? {
        val label = "\\b(?:soil\\s*)?ph\\b"
        val sameLine = Regex("(?i)$label\\s*[=:]?\\s*$NUM")
        for (line in lines) {
            val m = sameLine.find(line)
            if (m != null) {
                val v = m.groupValues[1].toDouble()
                if (v in 0.0..14.0) return ParsedValue(v, null, line, Source.OCR)
            }
        }

        val labelOnly = Regex("(?i)^(?:soil\\s*)?ph\\s*:?$")
        val valueLine = Regex("^(\\d+(?:\\.\\d+)?)\\s*$")
        for (i in 0 until lines.size - 1) {
            if (labelOnly.matches(lines[i])) {
                val vm = valueLine.find(lines[i + 1])
                if (vm != null) {
                    val v = vm.groupValues[1].toDouble()
                    if (v in 0.0..14.0) return ParsedValue(v, null, lines[i + 1], Source.OCR)
                }
            }
        }
        return null
    }

    private fun build(value: Double, unit: String?, rawText: String): ParsedValue? {
        if (value <= 0) return null   // reject zero/negative N/P/K values; never fabricate
        // Preserve the unit exactly as reported; if OCR found none, keep null.
        val cleanUnit = unit?.takeIf { it.isNotBlank() }
        return ParsedValue(value, cleanUnit, rawText, Source.OCR)
    }
}
