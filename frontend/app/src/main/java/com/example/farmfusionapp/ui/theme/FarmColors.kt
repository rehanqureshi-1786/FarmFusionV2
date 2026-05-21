package com.example.farmfusionapp.ui.theme

import androidx.compose.ui.graphics.Color

/**
 * FarmFusion Premium Design System Colors
 * Agriculture-inspired, professional palette with strong readability
 * Supports both Light and Dark themes
 */
object FarmColors {

    // ============================================
    // PRIMARY - Deep Forest Green (Crops/Nature)
    // ============================================
    val Primary50 = Color(0xFFF1F8F4)   // Lightest background
    val Primary100 = Color(0xFFE8F5E9)  // Subtle highlights
    val Primary200 = Color(0xFFC8E6C9)  // Light accent
    val Primary300 = Color(0xFF8BC34A)  // Medium accent
    val Primary400 = Color(0xFF4A7C59)  // Secondary green
    val Primary500 = Color(0xFF2D5A3D)  // Main primary
    val Primary600 = Color(0xFF1F4231)  // Darker primary (pressed)
    val Primary700 = Color(0xFF1A3A2A)  // Darkest
    val Primary900 = Color(0xFF121E16)  // Dark theme backgrounds
    val Primary950 = Color(0xFF0D1510)  // Darkest surfaces

    // ============================================
    // ACCENT - Muted Gold/Amber (Premium/AI)
    // ============================================
    val Accent50 = Color(0xFFFCFAF5)    // Warm white
    val Accent100 = Color(0xFFF9F3E3)  // Cream background
    val Accent200 = Color(0xFFEDD9A3)  // Light gold
    val Accent300 = Color(0xFFD4A84B)  // Bright gold (dark theme)
    val Accent400 = Color(0xFFC49A3B)  // Amber
    val Accent500 = Color(0xFFB8860B)  // Deep gold (main accent)
    val Accent600 = Color(0xFF8B6914)  // Dark gold
    val Accent900 = Color(0xFF3D2E10)  // Dark theme backgrounds
    val Accent950 = Color(0xFF2A1F0A)  // Deepest

    // ============================================
    // NEUTRALS - Earthy, warm tones
    // ============================================
    // Light Theme
    val Neutral0 = Color(0xFFFFFFFF)     // Pure white
    val Neutral50 = Color(0xFFFAFAF8)  // Warm white (page bg)
    val Neutral100 = Color(0xFFF5F5F0) // Off-white (card bg)
    val Neutral200 = Color(0xFFE8E8E3) // Light gray
    val Neutral300 = Color(0xFFD4D4CF) // Border gray
    val Neutral400 = Color(0xFFA3A39E) // Medium gray
    val Neutral500 = Color(0xFF73736E) // Text secondary
    val Neutral600 = Color(0xFF52524D) // Dark gray
    val Neutral700 = Color(0xFF3D3D39) // Text primary light
    val Neutral800 = Color(0xFF262622) // Near black
    val Neutral900 = Color(0xFF1A1A16) // Text primary

    // Dark Theme variants
    val DarkSurface = Color(0xFF1E1E1A)
    val DarkElevated = Color(0xFF2A2A26)
    val DarkBorder = Color(0xFF3D3D39)

    // ============================================
    // SEMANTIC COLORS
    // ============================================
    // Success - Healthy crops
    val Success50 = Color(0xFFDCFCE7)
    val Success100 = Color(0xFFBBF7D0)
    val Success400 = Color(0xFF4ADE80)  // Dark theme
    val Success500 = Color(0xFF22C55E)  // Main success
    val Success900 = Color(0xFF14532D)  // Dark bg

    // Warning - Weather alerts
    val Warning50 = Color(0xFFFEF3C7)
    val Warning100 = Color(0xFFFDE68A)
    val Warning400 = Color(0xFFFBBF24)  // Dark theme
    val Warning500 = Color(0xFFF59E0B)  // Main warning
    val Warning900 = Color(0xFF713F12)  // Dark bg

    // Error - Disease detected
    val Error50 = Color(0xFFFEE2E2)
    val Error100 = Color(0xFFFECACA)
    val Error400 = Color(0xFFF87171)  // Dark theme
    val Error500 = Color(0xFFEF4444)  // Main error
    val Error900 = Color(0xFF450A0A)  // Dark bg

    // Info - Water/irrigation
    val Info50 = Color(0xFFDBEAFE)
    val Info100 = Color(0xFFBFDBFE)
    val Info400 = Color(0xFF60A5FA)  // Dark theme
    val Info500 = Color(0xFF3B82F6)  // Main info
    val Info900 = Color(0xFF1E3A5F)  // Dark bg

    // ============================================
    // LEGACY COLOR ALIASES (for backward compatibility)
    // ============================================
    @Deprecated("Use Primary500") val Green500 = Primary500
    @Deprecated("Use Primary700") val Green700 = Primary600
    @Deprecated("Use Primary100") val Green100 = Primary100
    @Deprecated("Use Primary50") val Green50 = Primary50
    @Deprecated("Use Primary900") val Green900 = Primary900

    @Deprecated("Use Accent500") val Yellow500 = Accent500
    @Deprecated("Use Accent100") val Yellow100 = Accent100
    @Deprecated("Use Accent300") val Yellow300 = Accent300

    @Deprecated("Use Neutral700") val Brown500 = Neutral700
    @Deprecated("Use Neutral100") val Brown100 = Neutral100
    @Deprecated("Use Neutral300") val Brown300 = Neutral300
    @Deprecated("Use Neutral700") val Brown700 = Neutral700

    @Deprecated("Use Success500") val Success = Success500
    @Deprecated("Use Warning500") val Warning = Warning500
    @Deprecated("Use Error500") val Error = Error500
    @Deprecated("Use Info500") val Info = Info500

    @Deprecated("Use Neutral50") val BackgroundLight = Neutral50
    @Deprecated("Use Neutral900") val BackgroundDark = Neutral900
    @Deprecated("Use Neutral0") val SurfaceLight = Neutral0
    @Deprecated("Use DarkSurface") val SurfaceDark = DarkSurface

    @Deprecated("Use Neutral900") val TextPrimaryLight = Neutral900
    @Deprecated("Use Neutral500") val TextSecondaryLight = Neutral500
    @Deprecated("Use Neutral400") val TextHintLight = Neutral400

    // Agriculture-specific semantic colors
    val SoilBrown = Color(0xFF5D4037)
    val CropGreen = Success500
    val SkyBlue = Info500
    val WheatGold = Accent500
    val TomatoRed = Error500
}

/**
 * Light Theme Color Scheme
 */
object LightThemeColors {
    val Primary = FarmColors.Primary500
    val OnPrimary = Color.White
    val PrimaryContainer = FarmColors.Primary100
    val OnPrimaryContainer = FarmColors.Primary700

    val Secondary = FarmColors.Accent500
    val OnSecondary = Color.White
    val SecondaryContainer = FarmColors.Accent100
    val OnSecondaryContainer = FarmColors.Accent900

    val Tertiary = FarmColors.Info500
    val OnTertiary = Color.White
    val TertiaryContainer = FarmColors.Info100
    val OnTertiaryContainer = FarmColors.Info900

    val Background = FarmColors.Neutral50
    val OnBackground = FarmColors.Neutral900

    val Surface = Color.White
    val OnSurface = FarmColors.Neutral900
    val SurfaceVariant = FarmColors.Neutral100
    val OnSurfaceVariant = FarmColors.Neutral700

    val Outline = FarmColors.Neutral300
    val OutlineVariant = FarmColors.Neutral200

    val Error = FarmColors.Error500
    val OnError = Color.White
    val ErrorContainer = FarmColors.Error100
    val OnErrorContainer = FarmColors.Error900

    val Success = FarmColors.Success500
    val OnSuccess = Color.White
    val Warning = FarmColors.Warning500
    val OnWarning = Color.White
}

/**
 * Dark Theme Color Scheme
 */
object DarkThemeColors {
    val Primary = FarmColors.Primary400
    val OnPrimary = Color.White
    val PrimaryContainer = FarmColors.Primary700
    val OnPrimaryContainer = FarmColors.Primary100

    val Secondary = FarmColors.Accent300
    val OnSecondary = Color.Black
    val SecondaryContainer = FarmColors.Accent900
    val OnSecondaryContainer = FarmColors.Accent100

    val Tertiary = FarmColors.Info400
    val OnTertiary = Color.Black
    val TertiaryContainer = FarmColors.Info900
    val OnTertiaryContainer = FarmColors.Info100

    val Background = FarmColors.Primary950
    val OnBackground = FarmColors.Neutral50

    val Surface = FarmColors.DarkSurface
    val OnSurface = FarmColors.Neutral50
    val SurfaceVariant = FarmColors.DarkElevated
    val OnSurfaceVariant = FarmColors.Neutral200

    val Outline = FarmColors.DarkBorder
    val OutlineVariant = FarmColors.Neutral600

    val Error = FarmColors.Error400
    val OnError = Color.Black
    val ErrorContainer = FarmColors.Error900
    val OnErrorContainer = FarmColors.Error100

    val Success = FarmColors.Success400
    val OnSuccess = Color.Black
    val Warning = FarmColors.Warning400
    val OnWarning = Color.Black
}
