package com.example.farmfusionapp.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/**
 * FarmFusion Premium Typography System
 * - Modern, readable fonts optimized for farmers
 * - Strong hierarchy with professional weights
 * - Optimized for both English and Hindi text
 * - Large sizes for outdoor readability
 */

// Font family - Using system fonts for performance
// On Android, this will use Roboto/Noto Sans
private val AppFontFamily = FontFamily.Default

// ============================================
// DISPLAY - Large headlines, hero text
// ============================================
val displayLarge = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.Bold,
    fontSize = 32.sp,
    lineHeight = 40.sp,
    letterSpacing = (-0.5).sp
)

val displayMedium = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.Bold,
    fontSize = 28.sp,
    lineHeight = 36.sp,
    letterSpacing = (-0.5).sp
)

val displaySmall = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 24.sp,
    lineHeight = 32.sp,
    letterSpacing = (-0.3).sp
)

// ============================================
// HEADLINE - Section titles
// ============================================
val headlineLarge = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 24.sp,
    lineHeight = 32.sp,
    letterSpacing = (-0.3).sp
)

val headlineMedium = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 20.sp,
    lineHeight = 28.sp,
    letterSpacing = (-0.2).sp
)

val headlineSmall = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 18.sp,
    lineHeight = 24.sp,
    letterSpacing = (-0.1).sp
)

// ============================================
// TITLE - Card titles, button text
// ============================================
val titleLarge = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 20.sp,
    lineHeight = 28.sp,
    letterSpacing = 0.sp
)

val titleMedium = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 16.sp,
    lineHeight = 24.sp,
    letterSpacing = 0.sp
)

val titleSmall = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 14.sp,
    lineHeight = 20.sp,
    letterSpacing = 0.sp
)

// ============================================
// BODY - Main content text
// ============================================
val bodyLarge = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.Normal,
    fontSize = 16.sp,
    lineHeight = 24.sp,
    letterSpacing = 0.sp
)

val bodyMedium = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.Normal,
    fontSize = 14.sp,
    lineHeight = 20.sp,
    letterSpacing = 0.sp
)

val bodySmall = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.Normal,
    fontSize = 12.sp,
    lineHeight = 16.sp,
    letterSpacing = 0.1.sp
)

// ============================================
// LABEL - Buttons, chips, tags
// ============================================
val labelLarge = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.Medium,
    fontSize = 14.sp,
    lineHeight = 20.sp,
    letterSpacing = 0.1.sp
)

val labelMedium = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.Medium,
    fontSize = 12.sp,
    lineHeight = 16.sp,
    letterSpacing = 0.2.sp
)

val labelSmall = TextStyle(
    fontFamily = AppFontFamily,
    fontWeight = FontWeight.SemiBold,
    fontSize = 10.sp,
    lineHeight = 14.sp,
    letterSpacing = 0.2.sp
)

/**
 * Material 3 Typography mapping
 * Maps our custom typography to Material 3's semantic slots
 */
val FarmTypography = Typography(
    // Display
    displayLarge = displayLarge,
    displayMedium = displayMedium,
    displaySmall = displaySmall,

    // Headline
    headlineLarge = headlineLarge,
    headlineMedium = headlineMedium,
    headlineSmall = headlineSmall,

    // Title
    titleLarge = titleLarge,
    titleMedium = titleMedium,
    titleSmall = titleSmall,

    // Body
    bodyLarge = bodyLarge,
    bodyMedium = bodyMedium,
    bodySmall = bodySmall,

    // Label
    labelLarge = labelLarge,
    labelMedium = labelMedium,
    labelSmall = labelSmall
)

// Legacy export for backward compatibility
val Typography = FarmTypography

// Legacy style aliases for generated UI code that still uses uppercase names.
val androidx.compose.material3.Typography.DisplayLarge get() = displayLarge
val androidx.compose.material3.Typography.DisplayMedium get() = displayMedium
val androidx.compose.material3.Typography.DisplaySmall get() = displaySmall
val androidx.compose.material3.Typography.HeadlineLarge get() = headlineLarge
val androidx.compose.material3.Typography.HeadlineMedium get() = headlineMedium
val androidx.compose.material3.Typography.HeadlineSmall get() = headlineSmall
val androidx.compose.material3.Typography.TitleLarge get() = titleLarge
val androidx.compose.material3.Typography.TitleMedium get() = titleMedium
val androidx.compose.material3.Typography.TitleSmall get() = titleSmall
val androidx.compose.material3.Typography.BodyLarge get() = bodyLarge
val androidx.compose.material3.Typography.BodyMedium get() = bodyMedium
val androidx.compose.material3.Typography.BodySmall get() = bodySmall
val androidx.compose.material3.Typography.LabelLarge get() = labelLarge
val androidx.compose.material3.Typography.LabelMedium get() = labelMedium
val androidx.compose.material3.Typography.LabelSmall get() = labelSmall
