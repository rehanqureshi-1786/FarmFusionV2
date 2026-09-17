package com.example.farmfusionapp.ui.screens

import android.widget.Toast
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.KeyboardArrowRight
import androidx.compose.material.icons.rounded.History
import androidx.compose.material.icons.rounded.Storefront
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropSellingScreen(navController: NavController) {
    val context = LocalContext.current

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFFCFDFC))
    ) {
        // Bottom Background Illustration: ill_crop_sell_wheat_bg at 70% opacity
        Image(
            painter = painterResource(id = R.drawable.ill_crop_sell_wheat_bg),
            contentDescription = null,
            contentScale = ContentScale.FillWidth,
            alpha = 0.7f,
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
        )

        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                CenterAlignedTopAppBar(
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent
                    ),
                    title = {
                        Text(
                            text = "Sell Your Crop",
                            fontWeight = FontWeight.Bold,
                            fontSize = 20.sp,
                            color = Color(0xFF111827)
                        )
                    },
                    navigationIcon = {
                        IconButton(onClick = { navController.popBackStack() }) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Rounded.ArrowBack,
                                contentDescription = "Back",
                                tint = Color(0xFF111827)
                            )
                        }
                    }
                )
            }
        ) { padding ->
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(start = 20.dp, end = 20.dp, top = 6.dp, bottom = 110.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 1. MARKET TREND Banner Card
                item {
                    MarketTrendCard()
                }

                // 2. Section Header: Green Leaf + "What would you like to do?"
                item {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(top = 10.dp, bottom = 2.dp)
                    ) {
                        LeafHeaderIcon(modifier = Modifier.size(24.dp))
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(
                                text = "What would you like to do?",
                                style = MaterialTheme.typography.titleLarge.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF111827),
                                    fontSize = 18.5.sp
                                )
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = "Choose an option to manage your crops",
                                style = MaterialTheme.typography.bodyMedium.copy(
                                    color = Color(0xFF6B7280),
                                    fontSize = 13.5.sp
                                )
                            )
                        }
                    }
                }

                // 3. Action Cards
                // Card 1: List My Crop
                item {
                    ActionOptionCard(
                        title = "List My Crop",
                        desc = "Put your crops for sale online\nand reach more buyers",
                        avatarBg = Color(0xFFE8F5E9),
                        avatarContent = {
                            Icon(
                                imageVector = Icons.Rounded.Storefront,
                                contentDescription = null,
                                tint = Color(0xFF2E7D32),
                                modifier = Modifier.size(28.dp)
                            )
                        },
                        chevronBg = Color(0xFFF0FDF4),
                        chevronTint = Color(0xFF16A34A),
                        watermark = {
                            LeafWatermark(modifier = Modifier.size(60.dp, 44.dp))
                        },
                        onClick = {
                            navController.navigate(NavRoutes.ListMyCrop)
                        }
                    )
                }

                // Card 2: Current Prices
                item {
                    ActionOptionCard(
                        title = "Current Prices",
                        desc = "Check rates in different mandis\nacross your region",
                        avatarBg = Color(0xFFE0F2FE),
                        avatarContent = {
                            PriceBarChartIcon(
                                modifier = Modifier.size(24.dp),
                                tint = Color(0xFF0284C7)
                            )
                        },
                        chevronBg = Color(0xFFF0F9FF),
                        chevronTint = Color(0xFF0284C7),
                        watermark = {
                            PriceWaveWatermark(modifier = Modifier.size(80.dp, 36.dp))
                        },
                        onClick = {
                            navController.navigate(NavRoutes.MandiPrices)
                        }
                    )
                }

                // Card 3: My Sales
                item {
                    ActionOptionCard(
                        title = "My Sales",
                        desc = "Check the history of your\ncrops sold",
                        avatarBg = Color(0xFFF3E8FF),
                        avatarContent = {
                            Icon(
                                imageVector = Icons.Rounded.History,
                                contentDescription = null,
                                tint = Color(0xFF7C3AED),
                                modifier = Modifier.size(28.dp)
                            )
                        },
                        chevronBg = Color(0xFFFAF5FF),
                        chevronTint = Color(0xFF7C3AED),
                        watermark = {
                            InvoiceWatermark(modifier = Modifier.size(64.dp, 50.dp))
                        },
                        onClick = {
                            navController.navigate(NavRoutes.MySales)
                        }
                    )
                }
            }
        }
    }
}

/**
 * 1. Market Trend Card matching the reference design.
 * Features: Soft pastel green background, Market Trend label, bold text with highlighted 5% and rising arrow,
 * and vector-drawn ascending bars with trend curve and wheat stalk.
 */
@Composable
private fun MarketTrendCard() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(
                elevation = 2.dp,
                shape = RoundedCornerShape(22.dp),
                spotColor = Color(0xFF1B5E20).copy(alpha = 0.06f),
                ambientColor = Color.Black.copy(alpha = 0.02f)
            ),
        shape = RoundedCornerShape(22.dp),
        color = Color(0xFFEDF7ED),
        border = BorderStroke(1.dp, Color(0xFFE1EFE1))
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(start = 18.dp, end = 14.dp, top = 18.dp, bottom = 18.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "MARKET TREND",
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontWeight = FontWeight.ExtraBold,
                        color = Color(0xFF5A9E6F),
                        letterSpacing = 0.7.sp,
                        fontSize = 11.sp
                    )
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = buildAnnotatedString {
                        append("Wheat prices expected\nto rise by ")
                        withStyle(SpanStyle(color = Color(0xFF16A34A), fontWeight = FontWeight.Bold)) {
                            append("5% next week! ↗")
                        }
                    },
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF111827),
                        fontSize = 15.sp,
                        lineHeight = 21.sp
                    )
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "A good time to plan your sale.",
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = Color(0xFF6B7280),
                        fontSize = 12.5.sp
                    )
                )
            }

            Spacer(modifier = Modifier.width(8.dp))

            // Right illustration: ascending bars + upward curved arrow + wheat stalk
            MarketTrendGraphic(
                modifier = Modifier.size(width = 86.dp, height = 74.dp)
            )
        }
    }
}

/**
 * Custom Canvas vector graphic for the Market Trend Card:
 * - 4 ascending bars in light sage green
 * - Curved rising green arrow arching over the bars
 * - Golden wheat ear / stalk on the right
 */
@Composable
private fun MarketTrendGraphic(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        // 1. Four ascending bars in soft pastel sage green
        val barColor = Color(0xFFC2E0C6)
        val barWidth = w * 0.085f
        val radius = barWidth / 2f

        // Bar 1 (Shortest)
        drawRoundRect(
            color = barColor,
            topLeft = Offset(w * 0.02f, h * 0.70f),
            size = Size(barWidth, h * 0.30f),
            cornerRadius = CornerRadius(radius, radius)
        )
        // Bar 2
        drawRoundRect(
            color = barColor,
            topLeft = Offset(w * 0.16f, h * 0.52f),
            size = Size(barWidth, h * 0.48f),
            cornerRadius = CornerRadius(radius, radius)
        )
        // Bar 3
        drawRoundRect(
            color = barColor,
            topLeft = Offset(w * 0.30f, h * 0.38f),
            size = Size(barWidth, h * 0.62f),
            cornerRadius = CornerRadius(radius, radius)
        )
        // Bar 4 (Tallest)
        drawRoundRect(
            color = barColor,
            topLeft = Offset(w * 0.44f, h * 0.22f),
            size = Size(barWidth, h * 0.78f),
            cornerRadius = CornerRadius(radius, radius)
        )

        // 2. Upward arching green trend line + arrow
        val arrowColor = Color(0xFF2E7D32)
        val trendPath = Path().apply {
            moveTo(w * 0.06f, h * 0.66f)
            cubicTo(
                w * 0.22f, h * 0.58f,
                w * 0.38f, h * 0.34f,
                w * 0.58f, h * 0.08f
            )
        }
        drawPath(
            path = trendPath,
            color = arrowColor,
            style = Stroke(width = 2.4.dp.toPx(), cap = StrokeCap.Round)
        )

        // Arrow head pointing towards top-right
        val tipX = w * 0.58f
        val tipY = h * 0.08f
        val arrowHead = Path().apply {
            moveTo(tipX - w * 0.11f, tipY + h * 0.03f)
            lineTo(tipX, tipY)
            lineTo(tipX - w * 0.03f, tipY + h * 0.11f)
        }
        drawPath(
            path = arrowHead,
            color = arrowColor,
            style = Stroke(width = 2.4.dp.toPx(), cap = StrokeCap.Round)
        )

        // 3. Stylized Golden Wheat Stalk on the right
        val wheatColor = Color(0xFFE2A458)
        val stemX = w * 0.72f
        // Wheat main central stem
        drawLine(
            color = wheatColor,
            start = Offset(stemX, h * 0.14f),
            end = Offset(stemX, h * 0.85f),
            strokeWidth = 1.6.dp.toPx(),
            cap = StrokeCap.Round
        )

        // Alternating wheat grains (tilted oval grains)
        val grainWidth = w * 0.07f
        val grainHeight = h * 0.11f
        val grainPositions = listOf(
            Offset(stemX - w * 0.07f, h * 0.20f) to -25f,
            Offset(stemX + w * 0.02f, h * 0.24f) to 25f,
            Offset(stemX - w * 0.07f, h * 0.34f) to -25f,
            Offset(stemX + w * 0.02f, h * 0.38f) to 25f,
            Offset(stemX - w * 0.07f, h * 0.48f) to -25f,
            Offset(stemX + w * 0.02f, h * 0.52f) to 25f
        )

        for ((pos, _) in grainPositions) {
            drawRoundRect(
                color = wheatColor,
                topLeft = pos,
                size = Size(grainWidth, grainHeight),
                cornerRadius = CornerRadius(grainWidth / 2f, grainHeight / 2f)
            )
        }

        // Top terminal grain
        drawRoundRect(
            color = wheatColor,
            topLeft = Offset(stemX - grainWidth / 2f, h * 0.10f),
            size = Size(grainWidth, grainHeight),
            cornerRadius = CornerRadius(grainWidth / 2f, grainHeight / 2f)
        )
    }
}

/**
 * Clean Action Option Card matching the reference screen:
 * - Rounded white surface with subtle shadow
 * - Circular tinted avatar container on left
 * - Multi-line title & subtitle
 * - Circular chevron on right
 * - Decorative pastel watermark at bottom-right corner
 */
@Composable
private fun ActionOptionCard(
    title: String,
    desc: String,
    avatarBg: Color,
    avatarContent: @Composable () -> Unit,
    chevronBg: Color,
    chevronTint: Color,
    watermark: @Composable () -> Unit,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .shadow(
                elevation = 2.dp,
                shape = RoundedCornerShape(22.dp),
                spotColor = Color.Black.copy(alpha = 0.05f),
                ambientColor = Color.Black.copy(alpha = 0.02f)
            ),
        shape = RoundedCornerShape(22.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFF1F5F9))
    ) {
        Box(modifier = Modifier.fillMaxWidth()) {
            // Subtle watermark illustration at bottom-right
            Box(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(end = 6.dp, bottom = 4.dp)
            ) {
                watermark()
            }

            // Foreground Content
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 18.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Circular Avatar
                Surface(
                    shape = CircleShape,
                    color = avatarBg,
                    modifier = Modifier.size(54.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        avatarContent()
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                // Titles
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF111827),
                            fontSize = 16.sp
                        )
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = desc,
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = Color(0xFF6B7280),
                            fontSize = 12.5.sp,
                            lineHeight = 16.sp
                        )
                    )
                }

                Spacer(modifier = Modifier.width(10.dp))

                // Circular Chevron Button
                Surface(
                    shape = CircleShape,
                    color = chevronBg,
                    modifier = Modifier.size(32.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Rounded.KeyboardArrowRight,
                            contentDescription = null,
                            tint = chevronTint,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }
        }
    }
}

/**
 * Green leaf icon for the "What would you like to do?" section header.
 */
@Composable
private fun LeafHeaderIcon(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val leaf = Path().apply {
            moveTo(w * 0.90f, h * 0.10f)
            cubicTo(w * 0.35f, h * 0.05f, w * 0.05f, h * 0.40f, w * 0.15f, h * 0.88f)
            cubicTo(w * 0.60f, h * 0.95f, w * 0.95f, h * 0.65f, w * 0.90f, h * 0.10f)
            close()
        }
        drawPath(path = leaf, color = Color(0xFF2E7D32))

        // Center vein
        drawLine(
            color = Color.White.copy(alpha = 0.75f),
            start = Offset(w * 0.22f, h * 0.82f),
            end = Offset(w * 0.82f, h * 0.22f),
            strokeWidth = 1.3.dp.toPx(),
            cap = StrokeCap.Round
        )
    }
}

/**
 * 3-Bar Chart Icon for Current Prices avatar
 */
@Composable
private fun PriceBarChartIcon(modifier: Modifier = Modifier, tint: Color = Color(0xFF0284C7)) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val barW = w * 0.22f
        val r = barW / 2f

        // Bar 1 (Left - Medium)
        drawRoundRect(
            color = tint,
            topLeft = Offset(w * 0.08f, h * 0.45f),
            size = Size(barW, h * 0.55f),
            cornerRadius = CornerRadius(r, r)
        )
        // Bar 2 (Center - Tallest)
        drawRoundRect(
            color = tint,
            topLeft = Offset(w * 0.39f, h * 0.15f),
            size = Size(barW, h * 0.85f),
            cornerRadius = CornerRadius(r, r)
        )
        // Bar 3 (Right - Medium-Low)
        drawRoundRect(
            color = tint,
            topLeft = Offset(w * 0.70f, h * 0.35f),
            size = Size(barW, h * 0.65f),
            cornerRadius = CornerRadius(r, r)
        )
    }
}

/**
 * Bottom-right watermark for "List My Crop" card (two pastel green leaves)
 */
@Composable
private fun LeafWatermark(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val watermarkColor = Color(0xFFC8E6C9).copy(alpha = 0.75f)

        // Left leaf
        val leaf1 = Path().apply {
            moveTo(w * 0.45f, h * 0.95f)
            cubicTo(w * 0.15f, h * 0.85f, 0f, h * 0.55f, 0f, h * 0.35f)
            cubicTo(w * 0.25f, h * 0.35f, w * 0.45f, h * 0.65f, w * 0.45f, h * 0.95f)
            close()
        }
        drawPath(leaf1, color = watermarkColor)

        // Right leaf
        val leaf2 = Path().apply {
            moveTo(w * 0.45f, h * 0.95f)
            cubicTo(w * 0.55f, h * 0.55f, w * 0.80f, h * 0.20f, w * 0.98f, 0f)
            cubicTo(w * 0.98f, h * 0.45f, w * 0.75f, h * 0.85f, w * 0.45f, h * 0.95f)
            close()
        }
        drawPath(leaf2, color = watermarkColor)
    }
}

/**
 * Bottom-right watermark for "Current Prices" card (pastel blue wave line with crest dot)
 */
@Composable
private fun PriceWaveWatermark(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val waveColor = Color(0xFF90CAF9).copy(alpha = 0.65f)

        val path = Path().apply {
            moveTo(0f, h * 0.85f)
            cubicTo(
                w * 0.25f, h * 0.85f,
                w * 0.40f, h * 0.50f,
                w * 0.55f, h * 0.55f
            )
            cubicTo(
                w * 0.70f, h * 0.60f,
                w * 0.80f, h * 0.25f,
                w * 0.92f, h * 0.25f
            )
            cubicTo(
                w * 0.96f, h * 0.25f,
                w * 0.98f, h * 0.40f,
                w, h * 0.50f
            )
        }
        drawPath(
            path = path,
            color = waveColor,
            style = Stroke(width = 1.6.dp.toPx(), cap = StrokeCap.Round)
        )

        // Small circle at crest
        drawCircle(
            color = waveColor,
            radius = 2.4.dp.toPx(),
            center = Offset(w * 0.92f, h * 0.25f)
        )
    }
}

/**
 * Bottom-right watermark for "My Sales" card (pastel lavender invoice sheet + leaf)
 */
@Composable
private fun InvoiceWatermark(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val docColor = Color(0xFFE1BEE7).copy(alpha = 0.55f)

        // Rounded document sheet
        val sheetW = w * 0.58f
        val sheetH = h * 0.85f
        drawRoundRect(
            color = docColor,
            topLeft = Offset(0f, h * 0.15f),
            size = Size(sheetW, sheetH),
            cornerRadius = CornerRadius(6.dp.toPx(), 6.dp.toPx())
        )
        // Two document lines
        drawLine(
            color = Color.White.copy(alpha = 0.85f),
            start = Offset(sheetW * 0.18f, h * 0.42f),
            end = Offset(sheetW * 0.82f, h * 0.42f),
            strokeWidth = 2.dp.toPx(),
            cap = StrokeCap.Round
        )
        drawLine(
            color = Color.White.copy(alpha = 0.85f),
            start = Offset(sheetW * 0.18f, h * 0.62f),
            end = Offset(sheetW * 0.60f, h * 0.62f),
            strokeWidth = 2.dp.toPx(),
            cap = StrokeCap.Round
        )

        // Small leaf beside document
        val leaf = Path().apply {
            moveTo(sheetW + w * 0.05f, h * 0.95f)
            cubicTo(sheetW + w * 0.08f, h * 0.65f, w * 0.88f, h * 0.50f, w, h * 0.45f)
            cubicTo(w * 0.95f, h * 0.75f, sheetW + w * 0.25f, h * 0.95f, sheetW + w * 0.05f, h * 0.95f)
            close()
        }
        drawPath(leaf, color = docColor)
    }
}