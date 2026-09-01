package com.example.farmfusionapp.data.model

import java.util.Locale

/**
 * Unified India-Wide Multilingual & Regional Dialect Registry for FarmFusion.
 * Exact 1-to-1 reflection of backend/app/voice/languages.py (LANGUAGE_REGISTRY).
 */
data class AppLanguage(
    val code: String,
    val name: String,
    val nativeName: String,
    val script: String,
    val isDialect: Boolean = false,
    val parentLanguage: String? = null,
    val supportTier: Int = 1, // 1: Full Native Voice, 2: Understanding + Fallback
    val nativeTts: Boolean = true,
    val fallbackLanguage: String = "hi",
    val regions: List<String> = emptyList()
) {
    val displayTitle: String get() = "$nativeName ($name)"
    val capabilityLabel: String get() = if (supportTier == 1) "✓ Voice available" else "✓ Understanding • △ Voice fallback"
    
    fun getLocale(): Locale {
        return when (code) {
            "en" -> Locale("en", "IN")
            "hi" -> Locale("hi", "IN")
            "gu" -> Locale("gu", "IN")
            "mr" -> Locale("mr", "IN")
            "pa" -> Locale("pa", "IN")
            "bn" -> Locale("bn", "IN")
            "ta" -> Locale("ta", "IN")
            "te" -> Locale("te", "IN")
            "kn" -> Locale("kn", "IN")
            "ml" -> Locale("ml", "IN")
            "or" -> Locale("or", "IN")
            "as" -> Locale("as", "IN")
            "ur" -> Locale("ur", "IN")
            "mai" -> Locale("mai", "IN")
            else -> {
                val parent = parentLanguage ?: "hi"
                Locale(parent, "IN")
            }
        }
    }
}

object LanguageRegistry {
    val scheduledLanguages = listOf(
        AppLanguage(code = "hi", name = "Hindi", nativeName = "हिन्दी", script = "Devanagari", supportTier = 1, nativeTts = true, regions = listOf("National")),
        AppLanguage(code = "en", name = "English", nativeName = "English", script = "Latin", supportTier = 1, nativeTts = true, regions = listOf("National")),
        AppLanguage(code = "gu", name = "Gujarati", nativeName = "ગુજરાતી", script = "Gujarati", supportTier = 1, nativeTts = true, regions = listOf("Gujarat")),
        AppLanguage(code = "mr", name = "Marathi", nativeName = "मराठी", script = "Devanagari", supportTier = 1, nativeTts = true, regions = listOf("Maharashtra")),
        AppLanguage(code = "pa", name = "Punjabi", nativeName = "ਪੰਜਾਬੀ", script = "Gurmukhi", supportTier = 1, nativeTts = true, regions = listOf("Punjab")),
        AppLanguage(code = "bn", name = "Bengali", nativeName = "বাংলা", script = "Bengali", supportTier = 1, nativeTts = true, regions = listOf("West Bengal")),
        AppLanguage(code = "ta", name = "Tamil", nativeName = "தமிழ்", script = "Tamil", supportTier = 1, nativeTts = true, regions = listOf("Tamil Nadu")),
        AppLanguage(code = "te", name = "Telugu", nativeName = "తెలుగు", script = "Telugu", supportTier = 1, nativeTts = true, regions = listOf("Andhra Pradesh", "Telangana")),
        AppLanguage(code = "kn", name = "Kannada", nativeName = "ಕನ್ನಡ", script = "Kannada", supportTier = 1, nativeTts = true, regions = listOf("Karnataka")),
        AppLanguage(code = "ml", name = "Malayalam", nativeName = "മലയാളം", script = "Malayalam", supportTier = 1, nativeTts = true, regions = listOf("Kerala")),
        AppLanguage(code = "or", name = "Odia", nativeName = "ଓଡ଼ିଆ", script = "Odia", supportTier = 1, nativeTts = true, regions = listOf("Odisha")),
        AppLanguage(code = "as", name = "Assamese", nativeName = "অসমীয়া", script = "Bengali-Assamese", supportTier = 1, nativeTts = true, regions = listOf("Assam")),
        AppLanguage(code = "ur", name = "Urdu", nativeName = "اردو", script = "Perso-Arabic", supportTier = 1, nativeTts = true, regions = listOf("National")),
        AppLanguage(code = "mai", name = "Maithili", nativeName = "मैथिली", script = "Devanagari", supportTier = 1, nativeTts = true, regions = listOf("Bihar", "Jharkhand"))
    )

    val regionalDialects = listOf(
        AppLanguage(code = "rwr", name = "Marwari", nativeName = "मारवाड़ी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Rajasthan")),
        AppLanguage(code = "mew", name = "Mewari", nativeName = "मेवाड़ी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Udaipur", "Rajasthan")),
        AppLanguage(code = "dhu", name = "Dhundhari", nativeName = "ढूंढाड़ी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Jaipur", "Rajasthan")),
        AppLanguage(code = "har", name = "Harauti", nativeName = "हाड़ौती", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Kota", "Rajasthan")),
        AppLanguage(code = "swv", name = "Shekhawati", nativeName = "शेखावाटी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Sikar", "Rajasthan")),
        AppLanguage(code = "wbr", name = "Wagdi", nativeName = "वागड़ी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Banswara", "Dungarpur")),
        AppLanguage(code = "bho", name = "Bhojpuri", nativeName = "भोजपुरी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("UP", "Bihar")),
        AppLanguage(code = "awa", name = "Awadhi", nativeName = "अवधी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Central UP")),
        AppLanguage(code = "mag", name = "Magahi", nativeName = "मगही", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Bihar")),
        AppLanguage(code = "hne", name = "Chhattisgarhi", nativeName = "छत्तीसगढ़ी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Chhattisgarh")),
        AppLanguage(code = "bns", name = "Bundeli", nativeName = "बुंदेली", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Bundelkhand")),
        AppLanguage(code = "bgc", name = "Haryanvi", nativeName = "हरियाणवी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Haryana")),
        AppLanguage(code = "bra", name = "Braj", nativeName = "ब्रज भाषा", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Mathura", "UP")),
        AppLanguage(code = "gbm", name = "Garhwali", nativeName = "गढ़वाली", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Uttarakhand")),
        AppLanguage(code = "kfy", name = "Kumaoni", nativeName = "कुमाऊँनी", script = "Devanagari", isDialect = true, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Uttarakhand")),
        AppLanguage(code = "ne", name = "Nepali", nativeName = "नेपाली", script = "Devanagari", isDialect = false, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("Sikkim", "West Bengal")),
        AppLanguage(code = "mup", name = "Malwai", nativeName = "ਮਲਵਈ", script = "Gurmukhi", isDialect = true, parentLanguage = "pa", supportTier = 2, nativeTts = false, fallbackLanguage = "pa", regions = listOf("Punjab")),
        AppLanguage(code = "doa", name = "Doabi", nativeName = "ਦੁਆਬੀ", script = "Gurmukhi", isDialect = true, parentLanguage = "pa", supportTier = 2, nativeTts = false, fallbackLanguage = "pa", regions = listOf("Punjab")),
        AppLanguage(code = "vah", name = "Varhadi", nativeName = "वऱ्हाडी", script = "Devanagari", isDialect = true, parentLanguage = "mr", supportTier = 2, nativeTts = false, fallbackLanguage = "mr", regions = listOf("Vidarbha")),
        AppLanguage(code = "kat", name = "Kathiawari", nativeName = "કાઠિયાવાડી", script = "Gujarati", isDialect = true, parentLanguage = "gu", supportTier = 2, nativeTts = false, fallbackLanguage = "gu", regions = listOf("Saurashtra")),
        AppLanguage(code = "kok", name = "Konkani", nativeName = "कोंकणी", script = "Devanagari", isDialect = false, parentLanguage = "mr", supportTier = 2, nativeTts = false, fallbackLanguage = "mr", regions = listOf("Goa", "Maharashtra")),
        AppLanguage(code = "tcy", name = "Tulu", nativeName = "ತುಳು", script = "Kannada", isDialect = false, parentLanguage = "kn", supportTier = 2, nativeTts = false, fallbackLanguage = "kn", regions = listOf("Karnataka")),
        AppLanguage(code = "kfa", name = "Kodava", nativeName = "ಕೊಡವ", script = "Kannada", isDialect = false, parentLanguage = "kn", supportTier = 2, nativeTts = false, fallbackLanguage = "kn", regions = listOf("Coorg")),
        AppLanguage(code = "sa", name = "Sanskrit", nativeName = "संस्कृतम्", script = "Devanagari", isDialect = false, parentLanguage = "hi", supportTier = 2, nativeTts = false, fallbackLanguage = "hi", regions = listOf("National"))
    )

    val allLanguages: List<AppLanguage> = scheduledLanguages + regionalDialects

    fun findByCode(code: String?): AppLanguage? {
        if (code.isNullOrBlank()) return null
        val c = code.trim().lowercase()
        return allLanguages.firstOrNull { it.code.lowercase() == c }
    }
}
