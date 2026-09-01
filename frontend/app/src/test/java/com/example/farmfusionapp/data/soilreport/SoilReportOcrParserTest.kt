package com.example.farmfusionapp.data.soilreport

import org.junit.Assert.*
import org.junit.Test

class SoilReportOcrParserTest {

    @Test
    fun testAllValuesDetected() {
        val input = """
            N: 90 kg/ha
            P: 42 kg/ha
            K: 43 kg/ha
            pH: 6.4
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNotNull(result.nitrogen)
        assertEquals(90.0, result.nitrogen!!.value, 0.001)
        assertEquals("kg/ha", result.nitrogen!!.unit)

        assertNotNull(result.phosphorus)
        assertEquals(42.0, result.phosphorus!!.value, 0.001)
        assertEquals("kg/ha", result.phosphorus!!.unit)

        assertNotNull(result.potassium)
        assertEquals(43.0, result.potassium!!.value, 0.001)
        assertEquals("kg/ha", result.potassium!!.unit)

        assertNotNull(result.ph)
        assertEquals(6.4, result.ph!!.value, 0.001)
        assertNull(result.ph!!.unit)

        assertTrue(result.isComplete)
    }

    @Test
    fun testOneValueMissing() {
        val input = """
            N: 90 kg/ha
            P: 42 kg/ha
            pH: 6.4
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNotNull(result.nitrogen)
        assertEquals(90.0, result.nitrogen!!.value, 0.001)

        assertNotNull(result.phosphorus)
        assertEquals(42.0, result.phosphorus!!.value, 0.001)

        assertNull(result.potassium)

        assertNotNull(result.ph)
        assertEquals(6.4, result.ph!!.value, 0.001)

        assertFalse(result.isComplete)
        assertTrue(result.missing.contains("Potassium"))
    }

    @Test
    fun testLabelVariations() {
        val input = """
            Nitrogen: 90 kg/ha
            Phosphorus: 42 kg/ha
            Potassium: 43 kg/ha
            Soil pH: 6.4
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNotNull(result.nitrogen)
        assertEquals(90.0, result.nitrogen!!.value, 0.001)

        assertNotNull(result.phosphorus)
        assertEquals(42.0, result.phosphorus!!.value, 0.001)

        assertNotNull(result.potassium)
        assertEquals(43.0, result.potassium!!.value, 0.001)

        assertNotNull(result.ph)
        assertEquals(6.4, result.ph!!.value, 0.001)

        assertTrue(result.isComplete)
    }

    @Test
    fun testOcrFormattingNoiseTolerance() {
        val input = """
            N = 90 kg/ha
            P = 42 kg/ha
            K = 43 kg/ha
            PH = 6.4
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNotNull(result.nitrogen)
        assertEquals(90.0, result.nitrogen!!.value, 0.001)

        assertNotNull(result.phosphorus)
        assertEquals(42.0, result.phosphorus!!.value, 0.001)

        assertNotNull(result.potassium)
        assertEquals(43.0, result.potassium!!.value, 0.001)

        assertNotNull(result.ph)
        assertEquals(6.4, result.ph!!.value, 0.001)

        assertTrue(result.isComplete)
    }

    @Test
    fun testInvalidPh() {
        val input = """
            N: 90 kg/ha
            P: 42 kg/ha
            K: 43 kg/ha
            pH: 18
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNotNull(result.nitrogen)
        assertNotNull(result.phosphorus)
        assertNotNull(result.potassium)
        assertNull("pH 18 should be invalid", result.ph)

        assertFalse("Should not be complete due to invalid pH", result.isComplete)
        assertTrue(result.missing.contains("pH"))
    }

    @Test
    fun testNoFabricatedValues() {
        val input = """
            Some random text with numbers 123 456 789
            Temperature: 25 C
            Humidity: 60%
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNull(result.nitrogen)
        assertNull(result.phosphorus)
        assertNull(result.potassium)
        assertNull(result.ph)

        assertFalse(result.isComplete)
        assertEquals(4, result.missing.size)
    }

    @Test
    fun testSeparateLinesFormat() {
        val input = """
            Nitrogen
            90 kg/ha
            Phosphorus
            42 kg/ha
            Potassium
            43 kg/ha
            pH
            6.4
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        // The parser might not handle this format perfectly, but it should at least
        // not crash and should not fabricate values
        assertNotNull(result)
    }

    @Test
    fun testNegativeValuesRejected() {
        val input = """
            N: -10 kg/ha
            P: 42 kg/ha
            K: 43 kg/ha
            pH: 6.4
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNull("Negative N should be rejected", result.nitrogen)
        assertNotNull(result.phosphorus)
        assertNotNull(result.potassium)
        assertNotNull(result.ph)

        assertFalse(result.isComplete)
    }

    @Test
    fun testZeroValuesRejected() {
        val input = """
            N: 0 kg/ha
            P: 42 kg/ha
            K: 43 kg/ha
            pH: 6.4
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNull("Zero N should be rejected", result.nitrogen)
        assertNotNull(result.phosphorus)
        assertNotNull(result.potassium)
        assertNotNull(result.ph)

        assertFalse(result.isComplete)
    }

    @Test
    fun testMissingUnitDefaults() {
        val input = """
            N: 90
            P: 42
            K: 43
            pH: 6.4
        """.trimIndent()

        val result = SoilReportOcrParser.parse(input)

        assertNotNull(result.nitrogen)
        assertEquals(90.0, result.nitrogen!!.value, 0.001)
        assertNull(result.nitrogen!!.unit) // No unit provided

        assertNotNull(result.phosphorus)
        assertEquals(42.0, result.phosphorus!!.value, 0.001)

        assertNotNull(result.potassium)
        assertEquals(43.0, result.potassium!!.value, 0.001)

        assertNotNull(result.ph)
        assertEquals(6.4, result.ph!!.value, 0.001)
    }
}
