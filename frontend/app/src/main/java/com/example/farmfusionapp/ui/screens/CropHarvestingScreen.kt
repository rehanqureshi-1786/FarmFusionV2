package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.Groups
import androidx.compose.material.icons.rounded.KeyboardArrowRight
import androidx.compose.material.icons.rounded.Warehouse
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
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
fun CropHarvestingScreen(navController: NavController) {
    val currentLang = LocalAppLanguage.current
    Box(modifier = Modifier.fillMaxSize().background(Color(0xFFFAFCFA))) {

        // iOS-Level Premium Gradient
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(450.dp)
                .background(
                    Brush.verticalGradient(
                        0.0f to Color(0xFFF4EBE1),
                        0.35f to Color(0xFFE8F4EA),
                        0.7f to Color(0xFFE1F1FA),
                        1.0f to Color(0xFFFAFCFA)
                    )
                )
        )

        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                CenterAlignedTopAppBar(
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent,
                        titleContentColor = Color(0xFF1E5631)
                    ),
                    title = { Text(com.example.farmfusionapp.utils.AppLocalizer.localizeHarvestingPhrase("harvesting help", currentLang), fontWeight = FontWeight.Bold) },
                    navigationIcon = {
                        Surface(
                            onClick = { navController.popBackStack() },
                            shape = CircleShape,
                            color = Color.White,
                            shadowElevation = 2.dp,
                            modifier = Modifier.padding(start = 16.dp).size(40.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    Icons.AutoMirrored.Rounded.ArrowBack,
                                    contentDescription = "Back",
                                    tint = Color(0xFF1E5631),
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                        }
                    }
                )
            }
        ) { padding ->
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 32.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp)
            ) {

                // 1. Hero Header Section
                item {
                    HarvestHeroSection(currentLang)
                }

                // 2. Find Labour Card
                item {
                    PremiumHarvestCard(
                        title = com.example.farmfusionapp.utils.AppLocalizer.localizeHarvestingPhrase("find labour", currentLang),
                        subtitle = com.example.farmfusionapp.utils.AppLocalizer.localizeHarvestingPhrase("find labour sub", currentLang),
                        icon = Icons.Rounded.Groups,
                        cardColor = Color(0xFFE6F4EA),
                        iconBgColor = Color(0xFFD3EADD),
                        iconTintColor = Color(0xFF2E7D32),
                        illustration = R.drawable.ill_find_labour,
                        onClick = {
                            navController.navigate(NavRoutes.LabourServices)
                        }
                    )
                }

                // 3. Crop Storage Card
                item {
                    PremiumHarvestCard(
                        title = com.example.farmfusionapp.utils.AppLocalizer.localizeHarvestingPhrase("crop storage", currentLang),
                        subtitle = com.example.farmfusionapp.utils.AppLocalizer.localizeHarvestingPhrase("nearby cold storage sub", currentLang),
                        icon = Icons.Rounded.Warehouse,
                        cardColor = Color(0xFFE3F2FD),
                        iconBgColor = Color(0xFFCBE6FA),
                        iconTintColor = Color(0xFF1565C0),
                        illustration = R.drawable.ill_cold_storage,
                        onClick = {
                            // TODO: Add Crop Storage route when ready
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun HarvestHeroSection(currentLang: String = "en") {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(240.dp) // Slightly taller to accommodate the larger farmer illustration
    ) {
        // Hero Background Illustration (Scaled up and flush with right edge)
        Image(
            painter = painterResource(id = R.drawable.ill_harvest_hero),
            contentDescription = "Farmer Harvesting",
            contentScale = ContentScale.Fit,
            alignment = Alignment.BottomEnd,
            modifier = Modifier
                .matchParentSize()
                .padding(start = 70.dp) // Reduced padding to make the image much larger
                .offset(x = 20.dp, y = 10.dp) // Pushed perfectly to the right edge and bottom baseline
        )

        // Hero Typography (Shifted right away from the screen edge)
        Column(
            modifier = Modifier
                .align(Alignment.CenterStart)
                .padding(start = 12.dp, bottom = 20.dp) // Shifted 12.dp to the right
                .fillMaxWidth(0.6f)
        ) {
            Text(
                text = com.example.farmfusionapp.utils.AppLocalizer.localizeHarvestingPhrase("get the right help harvest with ease", currentLang),
                style = MaterialTheme.typography.headlineMedium.copy(
                    fontWeight = FontWeight.ExtraBold,
                    color = Color(0xFF2A2A2A)
                ),
                lineHeight = 34.sp
            )
            Spacer(modifier = Modifier.height(14.dp))
            Text(
                text = com.example.farmfusionapp.utils.AppLocalizer.localizeHarvestingPhrase("harvesting hero sub", currentLang),
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = Color(0xFF616161),
                    lineHeight = 20.sp
                )
            )
        }
    }
}

@Composable
fun PremiumHarvestCard(
    title: String,
    subtitle: String,
    icon: ImageVector,
    cardColor: Color,
    iconBgColor: Color,
    iconTintColor: Color,
    illustration: Int,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(160.dp)
            .shadow(
                elevation = 16.dp,
                shape = RoundedCornerShape(24.dp),
                spotColor = Color(0xFF000000).copy(alpha = 0.12f),
                ambientColor = Color(0xFF000000).copy(alpha = 0.04f)
            ),
        shape = RoundedCornerShape(24.dp),
        color = cardColor
    ) {
        Box(modifier = Modifier.fillMaxSize()) {

            // Bottom Right Illustration
            Image(
                painter = painterResource(id = illustration),
                contentDescription = null,
                contentScale = ContentScale.Fit,
                alignment = Alignment.BottomEnd,
                modifier = Modifier
                    .matchParentSize()
                    .padding(start = 70.dp)
                    .offset(y = 18.dp)
            )

            // Foreground Layout
            Row(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(20.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                // Left Side: Supersized Icon + Text
                Row(
                    modifier = Modifier.weight(1f),
                    horizontalArrangement = Arrangement.spacedBy(18.dp), // Slightly more breathing room for larger icon
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Supersized Circular Themed Icon
                    Surface(
                        shape = CircleShape,
                        color = iconBgColor,
                        modifier = Modifier.size(72.dp) // Increased significantly from 60.dp
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                icon,
                                contentDescription = null,
                                tint = iconTintColor,
                                modifier = Modifier.size(36.dp) // Increased from 30.dp
                            )
                        }
                    }

                    // Card Copy
                    Column {
                        Text(
                            text = title,
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.ExtraBold,
                                color = Color(0xFF1B1B1B)
                            )
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = subtitle,
                            style = MaterialTheme.typography.bodyMedium.copy(
                                color = Color(0xFF525252),
                                lineHeight = 18.sp
                            )
                        )
                    }
                }

                // Right Side: Forward Arrow
                Surface(
                    shape = CircleShape,
                    color = Color.White.copy(alpha = 0.9f),
                    shadowElevation = 2.dp,
                    modifier = Modifier.size(28.dp).align(Alignment.CenterVertically)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            Icons.Rounded.KeyboardArrowRight,
                            contentDescription = "Proceed",
                            tint = Color(0xFF1B1B1B),
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }
        }
    }
}