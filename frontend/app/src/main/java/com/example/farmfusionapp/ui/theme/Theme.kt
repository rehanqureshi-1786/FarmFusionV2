package com.example.farmfusionapp.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

/**
 * Theme mode options
 */
enum class ThemeMode {
    LIGHT,
    DARK,
    SYSTEM
}

/**
 * Custom theme state holder
 */
object FarmFusionThemeState {
    var themeMode by mutableStateOf(ThemeMode.LIGHT)

    val isDarkTheme: Boolean
        @Composable
        get() = when (themeMode) {
            ThemeMode.LIGHT -> false
            ThemeMode.DARK -> true
            ThemeMode.SYSTEM -> isSystemInDarkTheme()
        }
}

/**
 * Light color scheme based on premium design system
 */
private val LightColorScheme = lightColorScheme(
    primary = LightThemeColors.Primary,
    onPrimary = LightThemeColors.OnPrimary,
    primaryContainer = LightThemeColors.PrimaryContainer,
    onPrimaryContainer = LightThemeColors.OnPrimaryContainer,

    secondary = LightThemeColors.Secondary,
    onSecondary = LightThemeColors.OnSecondary,
    secondaryContainer = LightThemeColors.SecondaryContainer,
    onSecondaryContainer = LightThemeColors.OnSecondaryContainer,

    tertiary = LightThemeColors.Tertiary,
    onTertiary = LightThemeColors.OnTertiary,
    tertiaryContainer = LightThemeColors.TertiaryContainer,
    onTertiaryContainer = LightThemeColors.OnTertiaryContainer,

    background = LightThemeColors.Background,
    onBackground = LightThemeColors.OnBackground,

    surface = LightThemeColors.Surface,
    onSurface = LightThemeColors.OnSurface,
    surfaceVariant = LightThemeColors.SurfaceVariant,
    onSurfaceVariant = LightThemeColors.OnSurfaceVariant,

    error = LightThemeColors.Error,
    onError = LightThemeColors.OnError,
    errorContainer = LightThemeColors.ErrorContainer,
    onErrorContainer = LightThemeColors.OnErrorContainer,

    outline = LightThemeColors.Outline,
    outlineVariant = LightThemeColors.OutlineVariant,
)

/**
 * Dark color scheme based on premium design system
 */
private val DarkColorScheme = darkColorScheme(
    primary = DarkThemeColors.Primary,
    onPrimary = DarkThemeColors.OnPrimary,
    primaryContainer = DarkThemeColors.PrimaryContainer,
    onPrimaryContainer = DarkThemeColors.OnPrimaryContainer,

    secondary = DarkThemeColors.Secondary,
    onSecondary = DarkThemeColors.OnSecondary,
    secondaryContainer = DarkThemeColors.SecondaryContainer,
    onSecondaryContainer = DarkThemeColors.OnSecondaryContainer,

    tertiary = DarkThemeColors.Tertiary,
    onTertiary = DarkThemeColors.OnTertiary,
    tertiaryContainer = DarkThemeColors.TertiaryContainer,
    onTertiaryContainer = DarkThemeColors.OnTertiaryContainer,

    background = DarkThemeColors.Background,
    onBackground = DarkThemeColors.OnBackground,

    surface = DarkThemeColors.Surface,
    onSurface = DarkThemeColors.OnSurface,
    surfaceVariant = DarkThemeColors.SurfaceVariant,
    onSurfaceVariant = DarkThemeColors.OnSurfaceVariant,

    error = DarkThemeColors.Error,
    onError = DarkThemeColors.OnError,
    errorContainer = DarkThemeColors.ErrorContainer,
    onErrorContainer = DarkThemeColors.OnErrorContainer,

    outline = DarkThemeColors.Outline,
    outlineVariant = DarkThemeColors.OutlineVariant,
)

/**
 * Composition local for extended colors (success, warning)
 */
val LocalExtendedColors = compositionLocalOf {
    ExtendedColors(
        success = LightThemeColors.Success,
        onSuccess = LightThemeColors.OnSuccess,
        warning = LightThemeColors.Warning,
        onWarning = LightThemeColors.OnWarning
    )
}

/**
 * Extended colors for semantic states
 */
data class ExtendedColors(
    val success: androidx.compose.ui.graphics.Color,
    val onSuccess: androidx.compose.ui.graphics.Color,
    val warning: androidx.compose.ui.graphics.Color,
    val onWarning: androidx.compose.ui.graphics.Color
)

/**
 * Main theme composable
 */
@Composable
fun FarmFusionAppTheme(
    darkTheme: Boolean = FarmFusionThemeState.isDarkTheme,
    dynamicColor: Boolean = false, // Disabled for consistent brand colors
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val extendedColors = if (darkTheme) {
        ExtendedColors(
            success = DarkThemeColors.Success,
            onSuccess = DarkThemeColors.OnSuccess,
            warning = DarkThemeColors.Warning,
            onWarning = DarkThemeColors.OnWarning
        )
    } else {
        ExtendedColors(
            success = LightThemeColors.Success,
            onSuccess = LightThemeColors.OnSuccess,
            warning = LightThemeColors.Warning,
            onWarning = LightThemeColors.OnWarning
        )
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            // Status bar matches surface color
            window.statusBarColor = colorScheme.surface.toArgb()

            // Navigation bar
            window.navigationBarColor = colorScheme.surface.toArgb()

            val insetsController = WindowCompat.getInsetsController(window, view)
            insetsController.isAppearanceLightStatusBars = !darkTheme
            insetsController.isAppearanceLightNavigationBars = !darkTheme
        }
    }

    CompositionLocalProvider(LocalExtendedColors provides extendedColors) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = FarmTypography,
            content = content
        )
    }
}

/**
 * Extension to access extended colors
 */
val MaterialTheme.extendedColors: ExtendedColors
    @Composable
    get() = LocalExtendedColors.current
