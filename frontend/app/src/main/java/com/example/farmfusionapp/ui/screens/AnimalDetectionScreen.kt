package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R

@Composable
fun AnimalDetectionScreen(navController: NavController) {
    val scrollState = rememberScrollState()

    // Unifying background color acts as a fallback layer[cite: 7]
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF7FBF7))
    ) {
        // Background Illustration (PNG) - Now fills the entire screen edge-to-edge[cite: 7]
        Image(
            painter = painterResource(id = R.drawable.ill_animal_alert_top),
            contentDescription = "Wild Animal Alert Background",
            contentScale = ContentScale.Crop, // Crucial fix: Forces the image to cover max constraints without empty spaces[cite: 7]
            modifier = Modifier.fillMaxSize(),
        )

        // Gradient overlay blending into the screen background to anchor the bottom cards
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(Color.Transparent, Color(0xFFF7FBF7).copy(alpha = 0.9f), Color(0xFFF7FBF7)),
                        startY = 400f,
                        endY = 1200f
                    )
                )
        )

        // Main scrollable foreground container
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(scrollState)
        ) {
            TopHeaderSection(navController)
            UnderConstructionBanner()
            FeaturesCardSection()
            HowItWorksSection()

            // Buffer padding for Bottom Navigation Bar overlap
            Spacer(modifier = Modifier.height(100.dp))
        }
    }
}

@Composable
private fun TopHeaderSection(navController: NavController) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 16.dp)
    ) {
        // Transparent Top Bar Overlay
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .statusBarsPadding()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { navController.popBackStack() }) {
                Icon(
                    imageVector = Icons.AutoMirrored.Rounded.ArrowBack,
                    contentDescription = "Back",
                    tint = Color(0xFF1A1A1A)
                )
            }
            Text(
                text = "Animal Alert",
                modifier = Modifier
                    .weight(1f)
                    .offset(x = (-24).dp), // Adjusting center offset for back button
                textAlign = TextAlign.Center,
                fontWeight = FontWeight.Bold,
                fontSize = 20.sp,
                color = Color(0xFF1A1A1A)
            )
        }

        // Headline Content
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .padding(top = 16.dp),
            horizontalArrangement = Arrangement.Start,
            verticalAlignment = Alignment.Top
        ) {
            Column(modifier = Modifier.fillMaxWidth(0.8f)) {
                Text(
                    text = "Protect Your Farm,",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1A1A1A)
                )
                Text(
                    text = "Stay One Step Ahead",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = Color(0xFF2E7D32) // Deep green brand color
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Smart alerts for wild animals\nnear your crops and\nlivestock.",
                    fontSize = 15.sp,
                    color = Color.DarkGray,
                    lineHeight = 22.sp
                )
            }
        }
    }
}

@Composable
private fun UnderConstructionBanner() {
    Card(
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
            .offset(y = (-5).dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFFFF4E0)), // Light orange warning background
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Box(modifier = Modifier.fillMaxWidth()) {

            // Replicating the diagonal stripes for the construction look using Canvas
            Canvas(modifier = Modifier.fillMaxSize()) {
                val stripeColor = Color(0xFFFFE0B2).copy(alpha = 0.6f)
                val stripeWidth = 24f
                val gap = 24f
                var startX = size.width - 250f
                while (startX < size.width + 150f) {
                    drawLine(
                        color = stripeColor,
                        start = Offset(startX, 0f),
                        end = Offset(startX - size.height, size.height),
                        strokeWidth = stripeWidth
                    )
                    startX += stripeWidth + gap
                }
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Barricade/Construction Icon
                Surface(
                    shape = CircleShape,
                    color = Color.White.copy(alpha = 0.7f),
                    modifier = Modifier.size(56.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = Icons.Rounded.Construction,
                            contentDescription = "Under Construction",
                            tint = Color(0xFFF57C00),
                            modifier = Modifier.size(28.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Under Construction",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1A1A1A)
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "This feature is currently under development\nand will be available in a future update.\nStay tuned!",
                        fontSize = 12.sp,
                        color = Color.DarkGray,
                        lineHeight = 16.sp
                    )
                }
            }
        }
    }
}

@Composable
private fun FeaturesCardSection() {
    Card(
        shape = RoundedCornerShape(24.dp),
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 24.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            FeatureIconItem(
                icon = Icons.Rounded.CenterFocusStrong,
                title = "AI Detection",
                desc = "Smart sensors\ndetect wild\nanimals"
            )
            FeatureIconItem(
                icon = Icons.Rounded.NotificationsActive,
                title = "Instant Alerts",
                desc = "Get notified\nin real-time\n"
            )
            FeatureIconItem(
                icon = Icons.Rounded.LocationOn,
                title = "Location Based",
                desc = "Alerts for your\nfarm area\n"
            )
            FeatureIconItem(
                icon = Icons.Rounded.Security,
                title = "Stay Protected",
                desc = "Take action\nand protect\nyour farm"
            )
        }
    }
}

@Composable
private fun FeatureIconItem(icon: ImageVector, title: String, desc: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.width(78.dp)
    ) {
        Surface(
            shape = CircleShape,
            color = Color(0xFFE8F5E9), // Light green tint
            modifier = Modifier.size(46.dp)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = Color(0xFF2E7D32),
                    modifier = Modifier.size(22.dp)
                )
            }
        }
        Spacer(modifier = Modifier.height(12.dp))
        Text(
            text = title,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF2E7D32),
            textAlign = TextAlign.Center,
            lineHeight = 14.sp
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            text = desc,
            fontSize = 10.sp,
            color = Color.Gray,
            textAlign = TextAlign.Center,
            lineHeight = 14.sp
        )
    }
}

@Composable
private fun HowItWorksSection() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 16.dp)
    ) {
        Text(
            text = "How it works",
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF2E7D32),
            modifier = Modifier.padding(bottom = 12.dp, start = 4.dp)
        )

        Card(
            shape = RoundedCornerShape(24.dp),
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Box(
                modifier = Modifier.fillMaxWidth()
            ) {
                // Timeline Steps (Left Side)
                Column(
                    modifier = Modifier
                        .fillMaxWidth(0.65f) // Restrict width so it doesn't overlap the sensor
                        .padding(start = 20.dp, top = 20.dp, bottom = 20.dp, end = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(0.dp)
                ) {
                    StepItem(
                        icon = Icons.Rounded.CenterFocusStrong,
                        title = "Detect",
                        desc = "Sensors detect wild animals\nnear your crops or livestock."
                    )
                    StepItem(
                        icon = Icons.Rounded.NotificationsActive,
                        title = "Alert",
                        desc = "You receive an instant notification\nwith details and location."
                    )
                    StepItem(
                        icon = Icons.Rounded.Security,
                        title = "Act",
                        desc = "Take necessary action and\nkeep your farm safe.",
                        isLast = true
                    )
                }

                // Sensor Illustration (Right Side)
                Image(
                    painter = painterResource(id = R.drawable.ill_animal_alert_sensor),
                    contentDescription = "Sensor System Mounted",
                    contentScale = ContentScale.Fit,
                    alignment = Alignment.BottomEnd,
                    modifier = Modifier
                        .matchParentSize()
                        .padding(start = 20.dp)
                        .offset(y = 15.dp)
                )
            }
        }
    }
}

@Composable
private fun StepItem(icon: ImageVector, title: String, desc: String, isLast: Boolean = false) {
    Row(modifier = Modifier.height(IntrinsicSize.Min)) {
        // Icon and Dashed Connector Column
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.width(36.dp)
        ) {
            Surface(
                shape = CircleShape,
                color = Color(0xFFE8F5E9),
                modifier = Modifier.size(36.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = Color(0xFF2E7D32),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
            if (!isLast) {
                Canvas(
                    modifier = Modifier
                        .width(2.dp)
                        .weight(1f)
                        .padding(vertical = 4.dp)
                ) {
                    drawLine(
                        color = Color(0xFFC8E6C9),
                        start = Offset(0f, 0f),
                        end = Offset(0f, size.height),
                        strokeWidth = 4f,
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(12f, 12f), 0f)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.width(16.dp))

        // Content Column
        Column(
            modifier = Modifier.padding(bottom = if (isLast) 0.dp else 24.dp)
        ) {
            Text(
                text = title,
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF1A1A1A)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = desc,
                fontSize = 12.sp,
                color = Color.Gray,
                lineHeight = 16.sp
            )
        }
    }
}