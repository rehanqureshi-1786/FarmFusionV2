package com.example.farmfusionapp.ui.components

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.draw.blur
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.ui.theme.FarmColors
import com.example.farmfusionapp.ui.theme.FarmTypography
import com.example.farmfusionapp.ui.theme.extendedColors
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.screens.NavRoutes
import dev.chrisbanes.haze.HazeState
import dev.chrisbanes.haze.hazeChild
import dev.chrisbanes.haze.HazeStyle

// ============================================
// DESIGN SYSTEM CONSTANTS
// ============================================
object FarmDesignSystem {
    // Spacing
    val Space1 = 4.dp
    val Space2 = 8.dp
    val Space3 = 12.dp
    val Space4 = 16.dp
    val Space5 = 20.dp
    val Space6 = 24.dp
    val Space8 = 32.dp
    val Space10 = 40.dp
    val Space12 = 48.dp

    // Border Radius
    val RadiusSmall = 8.dp
    val RadiusMedium = 12.dp
    val RadiusLarge = 16.dp
    val RadiusXLarge = 20.dp
    val RadiusPill = 50.dp

    // Touch Targets (minimum 48dp for accessibility)
    val MinTouchTarget = 48.dp
    val ButtonHeightLarge = 56.dp
    val ButtonHeightMedium = 48.dp
    val FABSize = 64.dp
    val IconSizeSmall = 20.dp
    val IconSizeMedium = 24.dp
    val IconSizeLarge = 32.dp

    // Animation
    const val PressScale = 0.98f
    val ElevationDefault = 2.dp
    val ElevationRaised = 4.dp
    val ElevationFloating = 8.dp
}

// ============================================
// OPTIMIZED IMAGE WRAPPER
// ============================================
@Composable
fun OptimizedIllustration(
    drawableResId: Int,
    contentDescription: String?,
    modifier: Modifier = Modifier,
    alignment: Alignment = Alignment.Center,
    ratio: Float = 1f
) {
    Box(
        modifier = modifier.aspectRatio(ratio),
        contentAlignment = alignment
    ) {
        Image(
            painter = painterResource(id = drawableResId),
            contentDescription = contentDescription,
            contentScale = ContentScale.Fit,
            modifier = Modifier.fillMaxSize()
        )
    }
}

// ============================================
// PREMIUM BUTTONS
// ============================================
@Composable
fun PremiumButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    enabled: Boolean = true,
    isLoading: Boolean = false,
    colors: ButtonColors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.primary,
        contentColor = MaterialTheme.colorScheme.onPrimary
    ),
    shape: Shape = RoundedCornerShape(FarmDesignSystem.RadiusMedium)
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) FarmDesignSystem.PressScale else 1f,
        label = "buttonScale"
    )

    Button(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .height(FarmDesignSystem.ButtonHeightLarge)
            .scale(scale),
        shape = shape,
        enabled = enabled && !isLoading,
        colors = colors,
        interactionSource = interactionSource
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(24.dp),
                color = MaterialTheme.colorScheme.onPrimary,
                strokeWidth = 3.dp
            )
        } else {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                icon?.let {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        modifier = Modifier.size(FarmDesignSystem.IconSizeMedium)
                    )
                    Spacer(modifier = Modifier.width(FarmDesignSystem.Space3))
                }
                Text(
                    text = text,
                    style = MaterialTheme.typography.labelLarge.copy(
                        fontWeight = FontWeight.SemiBold
                    )
                )
            }
        }
    }
}

@Composable
fun PremiumSecondaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null
) {
    PremiumButton(
        text = text,
        onClick = onClick,
        modifier = modifier,
        icon = icon,
        colors = ButtonDefaults.buttonColors(
            containerColor = Color.Transparent,
            contentColor = MaterialTheme.colorScheme.primary
        ),
        shape = RoundedCornerShape(FarmDesignSystem.RadiusMedium)
    )
}

@Composable
fun GlassFloatingVoiceButton(
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        modifier = modifier
            .size(64.dp)
            .shadow(10.dp, CircleShape, spotColor = Color(0xFF2E7D32)),
        shape = CircleShape,
        color = Color.White,
        border = BorderStroke(2.dp, Brush.linearGradient(listOf(Color(0xFF81C784), Color(0xFF2E7D32)))),
        tonalElevation = 0.dp
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.linearGradient(
                        colors = listOf(
                            Color(0xFFE8F5E9).copy(alpha = 0.8f),
                            Color(0xFFC8E6C9).copy(alpha = 0.8f)
                        )
                    )
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Rounded.Mic,
                contentDescription = "Voice Assistant",
                tint = Color(0xFF2E7D32),
                modifier = Modifier.size(28.dp)
            )
        }
    }
}

@Composable
fun PremiumOutlinedButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null
) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier
            .fillMaxWidth()
            .height(FarmDesignSystem.ButtonHeightLarge),
        shape = RoundedCornerShape(FarmDesignSystem.RadiusMedium),
        border = BorderStroke(2.dp, MaterialTheme.colorScheme.primary)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            icon?.let {
                Icon(
                    imageVector = it,
                    contentDescription = null,
                    modifier = Modifier.size(FarmDesignSystem.IconSizeMedium)
                )
                Spacer(modifier = Modifier.width(FarmDesignSystem.Space3))
            }
            Text(
                text = text,
                style = MaterialTheme.typography.labelLarge.copy(
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.primary
                )
            )
        }
    }
}

// ============================================
// PREMIUM CARDS
// ============================================
@Composable
fun PremiumCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    backgroundColor: Color = MaterialTheme.colorScheme.surface,
    elevation: androidx.compose.ui.unit.Dp = FarmDesignSystem.ElevationDefault,
    content: @Composable ColumnScope.() -> Unit
) {
    val cardModifier = modifier.fillMaxWidth()

    if (onClick != null) {
        val interactionSource = remember { MutableInteractionSource() }
        val isPressed by interactionSource.collectIsPressedAsState()
        val scale by animateFloatAsState(
            targetValue = if (isPressed) FarmDesignSystem.PressScale else 1f,
            label = "cardScale"
        )

        ElevatedCard(
            onClick = onClick,
            modifier = cardModifier.scale(scale),
            shape = RoundedCornerShape(FarmDesignSystem.RadiusLarge),
            colors = CardDefaults.elevatedCardColors(containerColor = backgroundColor),
            elevation = CardDefaults.elevatedCardElevation(
                defaultElevation = if (isPressed) elevation + 2.dp else elevation
            ),
            interactionSource = interactionSource
        ) {
            Column(
                modifier = Modifier.padding(FarmDesignSystem.Space4),
                content = content
            )
        }
    } else {
        Card(
            modifier = cardModifier,
            shape = RoundedCornerShape(FarmDesignSystem.RadiusLarge),
            colors = CardDefaults.cardColors(containerColor = backgroundColor),
            elevation = CardDefaults.cardElevation(defaultElevation = elevation)
        ) {
            Column(
                modifier = Modifier.padding(FarmDesignSystem.Space4),
                content = content
            )
        }
    }
}

@Composable
fun PremiumHeroCard(
    modifier: Modifier = Modifier,
    gradient: List<Color> = listOf(
        MaterialTheme.colorScheme.primary,
        MaterialTheme.colorScheme.primaryContainer
    ),
    content: @Composable BoxScope.() -> Unit
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(FarmDesignSystem.RadiusXLarge),
        elevation = CardDefaults.cardElevation(defaultElevation = FarmDesignSystem.ElevationFloating)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.linearGradient(gradient)
                )
                .padding(FarmDesignSystem.Space5),
            content = content
        )
    }
}

// ============================================
// NEO + GLASS HYBRID SYSTEM
// ============================================

object NeoGlassTokens {
    val ScreenPadding = 20.dp
    val SectionGap = 18.dp
    val LargeCardRadius = 28.dp
    val MediumCardRadius = 22.dp
    val SmallCardRadius = 18.dp
    val FloatingOrbSize = 74.dp
    val BlurRadius = 18.dp
}

@Composable
fun NeoScaffoldBackground(
    modifier: Modifier = Modifier,
    content: @Composable BoxScope.() -> Unit
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFFBFDFA))
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.verticalGradient(
                        0.0f to Color(0xFFE8F5E9).copy(alpha = 0.4f),
                        0.5f to Color(0xFFF1F8E9).copy(alpha = 0.2f),
                        1.0f to Color(0xFFE3F2FD).copy(alpha = 0.5f)
                    )
                )
        )

        Box(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .size(500.dp)
                .offset(x = 100.dp, y = (-100).dp)
                .background(
                    Brush.radialGradient(
                        0.0f to Color(0xFF81D4FA).copy(alpha = 0.25f),
                        1.0f to Color.Transparent
                    )
                )
        )

        Box(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .size(600.dp)
                .offset(x = (-150).dp, y = 150.dp)
                .background(
                    Brush.radialGradient(
                        0.0f to Color(0xFFA5D6A7).copy(alpha = 0.35f),
                        1.0f to Color.Transparent
                    )
                )
        )

        Box(
            modifier = Modifier
                .align(Alignment.CenterEnd)
                .size(350.dp)
                .offset(x = 80.dp, y = 40.dp)
                .background(
                    Brush.radialGradient(
                        0.0f to Color(0xFFFFE082).copy(alpha = 0.2f),
                        1.0f to Color.Transparent
                    )
                )
        )

        Box(modifier = Modifier.fillMaxSize(), content = content)
    }
}

@Composable
fun NeoCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    containerColor: Color = MaterialTheme.colorScheme.surface,
    contentPadding: PaddingValues = PaddingValues(20.dp),
    content: @Composable ColumnScope.() -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val cardModifier = modifier
        .shadow(
            elevation = if (isPressed) 4.dp else 10.dp,
            shape = RoundedCornerShape(NeoGlassTokens.LargeCardRadius),
            ambientColor = if (MaterialTheme.colorScheme.background.luminance() > 0.5f) {
                Color.White.copy(alpha = 0.7f)
            } else {
                Color.Black.copy(alpha = 0.55f)
            },
            spotColor = if (MaterialTheme.colorScheme.background.luminance() > 0.5f) {
                Color.Black.copy(alpha = 0.12f)
            } else {
                MaterialTheme.colorScheme.primary.copy(alpha = 0.20f)
            }
        )
        .border(
            width = 1.dp,
            color = if (MaterialTheme.colorScheme.background.luminance() > 0.5f) {
                Color.White.copy(alpha = 0.75f)
            } else {
                Color.White.copy(alpha = 0.08f)
            },
            shape = RoundedCornerShape(NeoGlassTokens.LargeCardRadius)
        )

    val body: @Composable () -> Unit = {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(contentPadding),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            content = content
        )
    }

    if (onClick != null) {
        Surface(
            modifier = cardModifier.clickable(
                interactionSource = interactionSource,
                indication = null,
                onClick = onClick
            ),
            color = containerColor,
            shape = RoundedCornerShape(NeoGlassTokens.LargeCardRadius),
            tonalElevation = 0.dp
        ) { body() }
    } else {
        Surface(
            modifier = cardModifier,
            color = containerColor,
            shape = RoundedCornerShape(NeoGlassTokens.LargeCardRadius),
            tonalElevation = 0.dp
        ) { body() }
    }
}

@Composable
fun GlassPanel(
    modifier: Modifier = Modifier,
    contentPadding: PaddingValues = PaddingValues(18.dp),
    content: @Composable ColumnScope.() -> Unit
) {
    Surface(
        modifier = modifier,
        color = MaterialTheme.colorScheme.surface.copy(alpha = if (MaterialTheme.colorScheme.background.luminance() > 0.5f) 0.56f else 0.20f),
        shape = RoundedCornerShape(NeoGlassTokens.MediumCardRadius),
        tonalElevation = 0.dp,
        border = BorderStroke(
            1.dp,
            Color.White.copy(alpha = if (MaterialTheme.colorScheme.background.luminance() > 0.5f) 0.44f else 0.14f)
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .blur(0.dp)
                .background(Color.Transparent)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(contentPadding),
                verticalArrangement = Arrangement.spacedBy(10.dp),
                content = content
            )
        }
    }
}

@Composable
fun NeoSectionTitle(
    title: String,
    subtitle: String? = null,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier, verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = title,
            style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold)
        )
        if (!subtitle.isNullOrBlank()) {
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            )
        }
    }
}

@Composable
fun StatusCard(
    title: String,
    description: String,
    icon: ImageVector,
    status: StatusType,
    modifier: Modifier = Modifier,
    action: @Composable (() -> Unit)? = null
) {
    val (backgroundColor, contentColor, borderColor) = when (status) {
        StatusType.SUCCESS -> Triple(
            MaterialTheme.extendedColors.success.copy(alpha = 0.1f),
            MaterialTheme.extendedColors.success,
            MaterialTheme.extendedColors.success.copy(alpha = 0.3f)
        )
        StatusType.WARNING -> Triple(
            MaterialTheme.extendedColors.warning.copy(alpha = 0.1f),
            MaterialTheme.extendedColors.warning,
            MaterialTheme.extendedColors.warning.copy(alpha = 0.3f)
        )
        StatusType.ERROR -> Triple(
            MaterialTheme.colorScheme.errorContainer,
            MaterialTheme.colorScheme.error,
            MaterialTheme.colorScheme.error.copy(alpha = 0.3f)
        )
        StatusType.INFO -> Triple(
            MaterialTheme.colorScheme.tertiaryContainer,
            MaterialTheme.colorScheme.tertiary,
            MaterialTheme.colorScheme.tertiary.copy(alpha = 0.3f)
        )
    }

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(FarmDesignSystem.RadiusLarge),
        colors = CardDefaults.cardColors(containerColor = backgroundColor),
        border = BorderStroke(1.dp, borderColor)
    ) {
        Row(
            modifier = Modifier.padding(FarmDesignSystem.Space4),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(FarmDesignSystem.MinTouchTarget)
                    .background(
                        color = contentColor.copy(alpha = 0.1f),
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(FarmDesignSystem.IconSizeLarge),
                    tint = contentColor
                )
            }

            Spacer(modifier = Modifier.width(FarmDesignSystem.Space3))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.SemiBold,
                        color = contentColor
                    )
                )
                Spacer(modifier = Modifier.height(FarmDesignSystem.Space1))
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = contentColor.copy(alpha = 0.8f)
                    ),
                    maxLines = 2
                )
            }

            action?.let {
                Spacer(modifier = Modifier.width(FarmDesignSystem.Space3))
                it()
            }
        }
    }
}

enum class StatusType { SUCCESS, WARNING, ERROR, INFO }

// ============================================
// SERVICE / QUICK ACTION CARDS
// ============================================
@Composable
fun QuickActionCard(
    title: String,
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    badge: String? = null
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.97f else 1f,
        label = "quickActionScale"
    )

    ElevatedCard(
        onClick = onClick,
        modifier = modifier
            .aspectRatio(1f)
            .scale(scale),
        shape = RoundedCornerShape(FarmDesignSystem.RadiusLarge),
        colors = CardDefaults.elevatedCardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.elevatedCardElevation(
            defaultElevation = if (isPressed) FarmDesignSystem.ElevationRaised else FarmDesignSystem.ElevationDefault
        ),
        interactionSource = interactionSource
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(FarmDesignSystem.Space3),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .background(
                            color = MaterialTheme.colorScheme.primary.copy(alpha = 0.08f),
                            shape = CircleShape
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        modifier = Modifier.size(28.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                }

                Spacer(modifier = Modifier.height(FarmDesignSystem.Space2))

                Text(
                    text = title,
                    style = MaterialTheme.typography.labelLarge.copy(
                        fontWeight = FontWeight.SemiBold
                    ),
                    textAlign = TextAlign.Center,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }

            badge?.let {
                Badge(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(FarmDesignSystem.Space2)
                ) {
                    Text(it, style = MaterialTheme.typography.labelSmall)
                }
            }
        }
    }
}

@Composable
fun RecentlyUsedButton(
    icon: ImageVector,
    label: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    colors: List<Color> = listOf(Color(0xFFF5F5F5), Color.White),
    iconTint: Color = MaterialTheme.colorScheme.primary
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        label = "recentScale"
    )

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = modifier
            .scale(scale)
            .clickable(
                onClick = onClick,
                interactionSource = interactionSource,
                indication = null
            )
    ) {
        Surface(
            shape = RoundedCornerShape(20.dp),
            modifier = Modifier
                .size(68.dp)
                .shadow(
                    elevation = if (isPressed) 1.dp else 4.dp,
                    shape = RoundedCornerShape(20.dp),
                    spotColor = iconTint.copy(alpha = 0.25f)
                ),
            color = Color.White,
            border = BorderStroke(1.dp, Color(0xFFF0F0F0))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        Brush.verticalGradient(
                            listOf(colors[0].copy(alpha = 0.7f), Color.White)
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = label,
                    modifier = Modifier.size(28.dp),
                    tint = iconTint
                )
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium.copy(
                fontWeight = FontWeight.Bold,
                color = Color(0xFF444444),
                letterSpacing = 0.sp
            ),
            textAlign = TextAlign.Center,
            maxLines = 1
        )
    }
}

// ============================================
// SELECTION COMPONENTS
// ============================================
@Composable
fun SelectionCard(
    title: String,
    subtitle: String? = null,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    leadingContent: @Composable (() -> Unit)? = null
) {
    val borderColor = if (isSelected) {
        MaterialTheme.colorScheme.primary
    } else {
        MaterialTheme.colorScheme.outlineVariant
    }
    val backgroundColor = if (isSelected) {
        MaterialTheme.colorScheme.primaryContainer
    } else {
        MaterialTheme.colorScheme.surface
    }

    OutlinedCard(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(FarmDesignSystem.RadiusLarge),
        colors = CardDefaults.outlinedCardColors(containerColor = backgroundColor),
        border = BorderStroke(
            width = if (isSelected) 2.dp else 1.dp,
            color = borderColor
        )
    ) {
        Row(
            modifier = Modifier.padding(FarmDesignSystem.Space4),
            verticalAlignment = Alignment.CenterVertically
        ) {
            leadingContent?.let {
                it()
                Spacer(modifier = Modifier.width(FarmDesignSystem.Space3))
            }

            icon?.let {
                Box(
                    modifier = Modifier
                        .size(FarmDesignSystem.MinTouchTarget)
                        .background(
                            color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f),
                            shape = CircleShape
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = it,
                        contentDescription = null,
                        modifier = Modifier.size(FarmDesignSystem.IconSizeMedium),
                        tint = MaterialTheme.colorScheme.primary
                    )
                }
                Spacer(modifier = Modifier.width(FarmDesignSystem.Space3))
            }

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.SemiBold
                    )
                )
                subtitle?.let {
                    Spacer(modifier = Modifier.height(FarmDesignSystem.Space1))
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodyMedium.copy(
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    )
                }
            }

            if (isSelected) {
                Icon(
                    imageVector = Icons.Rounded.CheckCircle,
                    contentDescription = "Selected",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(24.dp)
                )
            }
        }
    }
}

// ============================================
// INPUT COMPONENTS
// ============================================
@Composable
fun PremiumTextField(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    label: String? = null,
    placeholder: String? = null,
    leadingIcon: ImageVector? = null,
    trailingIcon: ImageVector? = null,
    isError: Boolean = false,
    singleLine: Boolean = true
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier.fillMaxWidth(),
        label = label?.let { { Text(it) } },
        placeholder = placeholder?.let { { Text(it) } },
        leadingIcon = leadingIcon?.let {
            {
                Icon(
                    it,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        },
        trailingIcon = trailingIcon?.let {
            {
                Icon(
                    it,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        },
        isError = isError,
        singleLine = singleLine,
        shape = RoundedCornerShape(FarmDesignSystem.RadiusMedium),
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = MaterialTheme.colorScheme.primary,
            unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant,
            focusedContainerColor = MaterialTheme.colorScheme.surface,
            unfocusedContainerColor = MaterialTheme.colorScheme.surface
        )
    )
}

// ============================================
// VOICE COMPONENTS
// ============================================
@Composable
fun VoiceFab(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    isListening: Boolean = false,
    isShrunk: Boolean = false // New state parameter
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    val scale by animateFloatAsState(
        targetValue = if (isPressed || isListening) 0.95f else 1f,
        label = "voiceFabScale"
    )

    // 1. Matches the exact navigation bar easing to stay in perfect visual sync
    val yOffset by animateDpAsState(
        targetValue = if (isShrunk) 36.dp else 0.dp, // Drops the mic down 36dp to fill the newly created gap
        animationSpec = tween(durationMillis = 350, easing = FastOutSlowInEasing),
        label = "micOffset"
    )

    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.15f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = EaseInOutCubic),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAnim"
    )

    Box(
        modifier = modifier
            .offset(y = yOffset) // 2. Reacts fluidly to the user's scroll state
            .size(80.dp),
        contentAlignment = Alignment.Center
    ) {
        if (isListening) {
            Box(
                modifier = Modifier
                    .size(96.dp * pulseScale)
                    .background(
                        color = MaterialTheme.colorScheme.secondary.copy(alpha = 0.2f),
                        shape = CircleShape
                    )
            )
        }

        FloatingActionButton(
            onClick = onClick,
            modifier = Modifier
                .size(FarmDesignSystem.FABSize)
                .scale(scale),
            shape = CircleShape,
            containerColor = if (isListening) {
                MaterialTheme.colorScheme.secondary
            } else {
                MaterialTheme.colorScheme.secondaryContainer
            },
            contentColor = if (isListening) {
                MaterialTheme.colorScheme.onSecondary
            } else {
                MaterialTheme.colorScheme.onSecondaryContainer
            },
            elevation = FloatingActionButtonDefaults.elevation(
                defaultElevation = FarmDesignSystem.ElevationFloating
            )
        ) {
            Icon(
                imageVector = Icons.Rounded.Mic,
                contentDescription = "Voice Assistant",
                modifier = Modifier.size(28.dp)
            )
        }
    }
}

// ============================================
// SECTION COMPONENTS
// ============================================
@Composable
fun SectionHeader(
    title: String,
    modifier: Modifier = Modifier,
    actionText: String? = null,
    onActionClick: (() -> Unit)? = null
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleLarge.copy(
                fontWeight = FontWeight.SemiBold
            )
        )

        if (actionText != null && onActionClick != null) {
            TextButton(onClick = onActionClick) {
                Text(
                    text = actionText,
                    style = MaterialTheme.typography.labelLarge
                )
                Icon(
                    imageVector = Icons.AutoMirrored.Rounded.ArrowForward,
                    contentDescription = null,
                    modifier = Modifier.size(16.dp)
                )
            }
        }
    }
}

@Composable
fun StepIndicator(
    currentStep: Int,
    totalSteps: Int,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceEvenly,
        verticalAlignment = Alignment.CenterVertically
    ) {
        for (step in 1..totalSteps) {
            val isCompleted = step < currentStep
            val isCurrent = step == currentStep

            Box(
                modifier = Modifier
                    .size(10.dp)
                    .background(
                        color = when {
                            isCompleted -> MaterialTheme.colorScheme.primary
                            isCurrent -> MaterialTheme.colorScheme.primaryContainer
                            else -> MaterialTheme.colorScheme.surfaceVariant
                        },
                        shape = CircleShape
                    )
                    .border(
                        width = if (isCurrent) 2.dp else 0.dp,
                        color = MaterialTheme.colorScheme.primary,
                        shape = CircleShape
                    )
            )

            if (step < totalSteps) {
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .height(2.dp)
                        .background(
                            color = if (isCompleted) {
                                MaterialTheme.colorScheme.primary
                            } else {
                                MaterialTheme.colorScheme.surfaceVariant
                            }
                        )
                )
            }
        }
    }
}

// ============================================
// EMPTY & ERROR STATES
// ============================================
@Composable
fun EmptyState(
    title: String,
    description: String,
    icon: ImageVector,
    modifier: Modifier = Modifier,
    action: @Composable (() -> Unit)? = null
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(FarmDesignSystem.Space8),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(96.dp)
                .background(
                    color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.5f),
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.primary
            )
        }

        Spacer(modifier = Modifier.height(FarmDesignSystem.Space5))

        Text(
            text = title,
            style = MaterialTheme.typography.headlineSmall.copy(
                fontWeight = FontWeight.SemiBold
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(FarmDesignSystem.Space2))

        Text(
            text = description,
            style = MaterialTheme.typography.bodyLarge.copy(
                color = MaterialTheme.colorScheme.onSurfaceVariant
            ),
            textAlign = TextAlign.Center
        )

        action?.let {
            Spacer(modifier = Modifier.height(FarmDesignSystem.Space5))
            it()
        }
    }
}

@Composable
fun ErrorState(
    message: String,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(FarmDesignSystem.Space8),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(80.dp)
                .background(
                    color = MaterialTheme.colorScheme.errorContainer,
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Rounded.ErrorOutline,
                contentDescription = null,
                modifier = Modifier.size(40.dp),
                tint = MaterialTheme.colorScheme.error
            )
        }

        Spacer(modifier = Modifier.height(FarmDesignSystem.Space5))

        Text(
            text = "Oops! Something went wrong",
            style = MaterialTheme.typography.headlineSmall.copy(
                fontWeight = FontWeight.Bold
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(FarmDesignSystem.Space2))

        Text(
            text = message,
            style = MaterialTheme.typography.bodyLarge.copy(
                color = MaterialTheme.colorScheme.onSurfaceVariant
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(FarmDesignSystem.Space5))

        PremiumButton(
            text = "Try Again",
            onClick = onRetry,
            icon = Icons.Rounded.Refresh
        )
    }
}

// ============================================
// LOADING COMPONENTS
// ============================================
@Composable
fun LoadingScreen(
    message: String,
    modifier: Modifier = Modifier,
    subMessage: String? = null
) {
    Column(
        modifier = modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        val infiniteTransition = rememberInfiniteTransition(label = "loading")
        val scale by infiniteTransition.animateFloat(
            initialValue = 0.8f,
            targetValue = 1.2f,
            animationSpec = infiniteRepeatable(
                animation = tween(1000, easing = EaseInOutCubic),
                repeatMode = RepeatMode.Reverse
            ),
            label = "pulse"
        )

        Box(
            modifier = Modifier.size(80.dp),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator(
                modifier = Modifier.fillMaxSize(),
                strokeWidth = 4.dp,
                color = MaterialTheme.colorScheme.primary
            )

            Box(
                modifier = Modifier
                    .size(48.dp * scale)
                    .background(
                        color = MaterialTheme.colorScheme.primaryContainer,
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Rounded.Agriculture,
                    contentDescription = null,
                    modifier = Modifier.size(24.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }

        Spacer(modifier = Modifier.height(FarmDesignSystem.Space6))

        Text(
            text = message,
            style = MaterialTheme.typography.headlineSmall.copy(
                fontWeight = FontWeight.Bold
            ),
            textAlign = TextAlign.Center
        )

        subMessage?.let {
            Spacer(modifier = Modifier.height(FarmDesignSystem.Space2))
            Text(
                text = it,
                style = MaterialTheme.typography.bodyLarge.copy(
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                ),
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(horizontal = FarmDesignSystem.Space6)
            )
        }
    }
}

// ============================================
// BADGES & CHIPS
// ============================================
@Composable
fun ConfidenceBadge(
    confidence: Float,
    modifier: Modifier = Modifier
) {
    val (color, bgColor) = when {
        confidence >= 0.9f -> Pair(
            MaterialTheme.extendedColors.success,
            MaterialTheme.extendedColors.success.copy(alpha = 0.1f)
        )
        confidence >= 0.7f -> Pair(
            MaterialTheme.extendedColors.warning,
            MaterialTheme.extendedColors.warning.copy(alpha = 0.1f)
        )
        else -> Pair(
            MaterialTheme.colorScheme.error,
            MaterialTheme.colorScheme.error.copy(alpha = 0.1f)
        )
    }

    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(FarmDesignSystem.RadiusSmall),
        color = bgColor
    ) {
        Text(
            text = "${(confidence * 100).toInt()}% confidence",
            style = MaterialTheme.typography.labelMedium.copy(
                color = color,
                fontWeight = FontWeight.SemiBold
            ),
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}

@Composable
fun TrendIndicator(
    trend: Float,
    modifier: Modifier = Modifier
) {
    val (icon, color) = when {
        trend > 0 -> Pair(Icons.Rounded.TrendingUp, MaterialTheme.extendedColors.success)
        trend < 0 -> Pair(Icons.Rounded.TrendingDown, MaterialTheme.colorScheme.error)
        else -> Pair(Icons.Rounded.TrendingFlat, MaterialTheme.colorScheme.onSurfaceVariant)
    }

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(16.dp),
            tint = color
        )
        Spacer(modifier = Modifier.width(2.dp))
        Text(
            text = "${if (trend > 0) "+" else ""}${(trend * 100).toInt()}%",
            style = MaterialTheme.typography.labelSmall.copy(
                color = color,
                fontWeight = FontWeight.SemiBold
            )
        )
    }
}

// ============================================
// LEGACY COMPONENT WRAPPERS (Backward compatibility)
// ============================================
@Deprecated("Use PremiumButton instead")
@Composable
fun FarmerButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    enabled: Boolean = true,
    colors: ButtonColors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.primary,
        contentColor = MaterialTheme.colorScheme.onPrimary
    ),
    isLoading: Boolean = false
) = PremiumButton(
    text = text,
    onClick = onClick,
    modifier = modifier,
    icon = icon,
    enabled = enabled,
    isLoading = isLoading,
    colors = colors
)

@Deprecated("Use PremiumCard instead")
@Composable
fun FarmerCard(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    backgroundColor: Color = MaterialTheme.colorScheme.surface,
    content: @Composable ColumnScope.() -> Unit
) = PremiumCard(
    modifier = modifier,
    onClick = onClick,
    backgroundColor = backgroundColor,
    content = content
)

@Deprecated("Use ServiceCard instead")
@Composable
fun ServiceCard(
    title: String,
    subtitle: String,
    icon: ImageVector,
    backgroundColor: Color,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    badgeText: String? = null
) = QuickActionCard(
    title = title,
    icon = icon,
    onClick = onClick,
    modifier = modifier,
    badge = badgeText
)

@Deprecated("Use StatusCard instead")
@Composable
fun InfoCard(
    title: String,
    description: String,
    icon: ImageVector,
    modifier: Modifier = Modifier,
    backgroundColor: Color = MaterialTheme.colorScheme.primaryContainer,
    contentColor: Color = MaterialTheme.colorScheme.onPrimaryContainer
) = StatusCard(
    title = title,
    description = description,
    icon = icon,
    status = StatusType.INFO,
    modifier = modifier
)

// ============================================
// BOTTOM NAVIGATION SYSTEM
// ============================================

data class BottomNavItem(
    val label: String,
    val route: String,
    val iconVector: ImageVector? = null,
    val iconDrawable: Int? = null,
    val isPrimaryAction: Boolean = false
)

@Composable
fun HomeBottomBar(
    navController: NavController,
    currentRoute: String?,
    isShrunk: Boolean = false,
    hazeState: HazeState // Keeping the HazeState for your frosted glass!
) {
    val items = listOf(
        BottomNavItem("Home", NavRoutes.Dashboard, iconDrawable = R.drawable.nav_home),
        BottomNavItem("Rates", NavRoutes.MandiPrices, iconDrawable = R.drawable.nav_rates),
        BottomNavItem("Scan", NavRoutes.CropDisease, iconVector = Icons.Rounded.CropFree, isPrimaryAction = true),
        BottomNavItem("Weather", NavRoutes.Weather, iconDrawable = R.drawable.nav_weather),
        BottomNavItem("Profile", NavRoutes.Profile, iconDrawable = R.drawable.nav_profile)
    )

    // 1. Unified Snappy Easing (Zero bounce, zero quiver, 250ms duration)
    val fluidTweenDp = tween<Dp>(durationMillis = 350, easing = FastOutSlowInEasing)
    val fluidTweenFloat = tween<Float>(durationMillis = 350, easing = FastOutSlowInEasing)

    // 2. Container Animations
    val horizontalPadding by animateDpAsState(
        targetValue = if (isShrunk) 72.dp else 0.dp, // Drastically increased to tightly cluster the icons
        animationSpec = fluidTweenDp,
        label = "navPadding"
    )
    val barHeight by animateDpAsState(
        targetValue = if (isShrunk) 64.dp else 76.dp, // Enlarged slightly from the previous 56.dp
        animationSpec = fluidTweenDp,
        label = "navHeight"
    )
    val yOffset by animateDpAsState(
        targetValue = if (isShrunk) 16.dp else 0.dp,
        animationSpec = fluidTweenDp,
        label = "navOffset"
    )
    val shadowElevation by animateDpAsState(
        targetValue = if (isShrunk) 2.dp else 20.dp,
        animationSpec = fluidTweenDp,
        label = "navShadow"
    )

    // 3. Internal Content Animations (Slightly larger when shrunk for a premium feel)
    val iconBoxSize by animateDpAsState(
        targetValue = if (isShrunk) 40.dp else 46.dp, // Increased from 36.dp
        animationSpec = fluidTweenDp,
        label = "iconBox"
    )
    val standardIconSize by animateDpAsState(
        targetValue = if (isShrunk) 22.dp else 26.dp, // Increased from 20.dp
        animationSpec = fluidTweenDp,
        label = "stdIcon"
    )
    val primaryIconSize by animateDpAsState(
        targetValue = if (isShrunk) 20.dp else 24.dp, // Increased from 18.dp
        animationSpec = fluidTweenDp,
        label = "primIcon"
    )
    val textSizeFloat by animateFloatAsState(
        targetValue = if (isShrunk) 0f else 11f,
        animationSpec = fluidTweenFloat,
        label = "textSize"
    )

    Surface(
        modifier = Modifier
            .padding(horizontal = horizontalPadding.coerceAtLeast(0.dp))
            .fillMaxWidth()
            .height(barHeight)
            .offset(y = yOffset)
            .shadow(
                elevation = shadowElevation,
                shape = RoundedCornerShape(50.dp),
                spotColor = Color.Black.copy(alpha = 0.05f),
                ambientColor = Color.Transparent
            )
            .hazeChild(
                state = hazeState,
                shape = RoundedCornerShape(50.dp),
                style = HazeStyle(
                    tint = Color.White.copy(alpha = 0.65f),
                    blurRadius = 24.dp
                )
            ),
        shape = RoundedCornerShape(50.dp),
        color = Color.Transparent,
        border = BorderStroke(1.dp, Color.White.copy(alpha = 0.8f)),
        tonalElevation = 0.dp
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            items.forEach { item ->
                val selected = currentRoute == item.route
                val primaryColor = Color(0xFF2E7D32)
                val unselectedColor = Color.DarkGray

                Column(
                    modifier = Modifier
                        .weight(1f)
                        .clickable(
                            interactionSource = remember { MutableInteractionSource() },
                            indication = null
                        ) { if (!selected) navController.navigate(item.route) },
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    if (item.isPrimaryAction) {
                        Box(
                            modifier = Modifier
                                .size(iconBoxSize)
                                .background(primaryColor, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            if (item.iconVector != null) {
                                Icon(
                                    imageVector = item.iconVector,
                                    contentDescription = item.label,
                                    tint = Color.White,
                                    modifier = Modifier.size(primaryIconSize)
                                )
                            } else if (item.iconDrawable != null) {
                                Icon(
                                    painter = painterResource(id = item.iconDrawable),
                                    contentDescription = item.label,
                                    tint = Color.White,
                                    modifier = Modifier.size(primaryIconSize)
                                )
                            }
                        }
                    } else {
                        val tintColor = if (selected) primaryColor else unselectedColor

                        Box(
                            modifier = Modifier.size(iconBoxSize),
                            contentAlignment = Alignment.Center
                        ) {
                            if (item.iconVector != null) {
                                Icon(
                                    imageVector = item.iconVector,
                                    contentDescription = item.label,
                                    tint = tintColor,
                                    modifier = Modifier.size(standardIconSize)
                                )
                            } else if (item.iconDrawable != null) {
                                Icon(
                                    painter = painterResource(id = item.iconDrawable),
                                    contentDescription = item.label,
                                    tint = tintColor,
                                    modifier = Modifier.size(standardIconSize)
                                )
                            }
                        }
                    }

                    if (textSizeFloat > 1f) {
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = item.label,
                            style = MaterialTheme.typography.labelSmall.copy(
                                fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                                color = if (selected) primaryColor else unselectedColor,
                                fontSize = textSizeFloat.sp
                            ),
                            maxLines = 1
                        )
                    }
                }
            }
        }
    }
}