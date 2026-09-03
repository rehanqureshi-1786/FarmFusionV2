package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.KeyboardArrowRight
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground

// Added explicit properties for padding (size), offset (position), and alpha (transparency)
data class CropServiceItem(
    val title: String,
    val subtitle: String,
    val icon: ImageVector,
    val route: String,
    val iconBgColor: Color,
    val iconTintColor: Color,
    val illustrationRes: Int,
    val imageAlpha: Float = 1.0f,
    val imagePaddingStart: Dp = 40.dp, // Tweak to change width/size
    val imagePaddingTop: Dp = 60.dp,   // Tweak to change height/size
    val imageOffsetX: Dp = 10.dp,      // Tweak to move Left/Right
    val imageOffsetY: Dp = 0.dp        // Tweak to move Up/Down
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropServicesScreen(navController: NavController) {
    val currentLang = LocalAppLanguage.current
    val services = remember(currentLang) {
        listOf(
            CropServiceItem(
                title = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("crop advice", currentLang),
                subtitle = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("crop advice sub", currentLang),
                icon = Icons.Rounded.Agriculture,
                route = NavRoutes.CropRecommendation,
                iconBgColor = Color(0xFFE8F5E9), // Used as Card Background
                iconTintColor = Color(0xFF2E7D32),
                illustrationRes = R.drawable.ill_services_crop_advice,
                imageAlpha = 0.6f,
                imagePaddingStart = 60.dp,
                imagePaddingTop = 80.dp,
                imageOffsetX = 20.dp,
                imageOffsetY = 10.dp
            ),
            CropServiceItem(
                title = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("disease info", currentLang),
                subtitle = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("disease info sub", currentLang),
                icon = Icons.Rounded.BugReport,
                route = NavRoutes.CropDisease,
                iconBgColor = Color(0xFFFFF3E0),
                iconTintColor = Color(0xFFE65100),
                illustrationRes = R.drawable.ill_services_disease_info,
                imageAlpha = 0.6f,
                imagePaddingStart = 50.dp,
                imagePaddingTop = 70.dp,
                imageOffsetX = 15.dp,
                imageOffsetY = 20.dp
            ),
            CropServiceItem(
                title = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("harvesting", currentLang),
                subtitle = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("harvesting sub", currentLang),
                icon = Icons.Rounded.ContentCut,
                route = NavRoutes.CropHarvesting,
                iconBgColor = Color(0xFFF3E5F5),
                iconTintColor = Color(0xFF6A1B9A),
                illustrationRes = R.drawable.ill_services_harvesting,
                imageAlpha = 0.6f,
                imagePaddingStart = 40.dp,
                imagePaddingTop = 60.dp,
                imageOffsetX = 15.dp,
                imageOffsetY = 20.dp
            ),
            CropServiceItem(
                title = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("selling", currentLang),
                subtitle = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("selling sub", currentLang),
                icon = Icons.Rounded.CurrencyRupee,
                route = NavRoutes.CropSelling,
                iconBgColor = Color(0xFFE0F2F1),
                iconTintColor = Color(0xFF00695C),
                illustrationRes = R.drawable.ill_services_selling,
                imageAlpha = 0.6f,
                imagePaddingStart = 10.dp,
                imagePaddingTop = 30.dp,
                imageOffsetX = 10.dp,
                imageOffsetY = 10.dp
            )
        )
    }

    Scaffold(
        containerColor = Color.Transparent,
        topBar = {
            CenterAlignedTopAppBar(
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color.Transparent,
                    titleContentColor = Color(0xFF1B4332)
                ),
                title = { Text(com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("crop services", currentLang), fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", tint = Color(0xFF1B1B1B))
                    }
                }
            )
        }
    ) { padding ->
        NeoScaffoldBackground(modifier = Modifier.fillMaxSize().background(Color(0xFFFAFCFA))) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(horizontal = 20.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {

                // 1. Premium Hero Card
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(180.dp)
                        .shadow(12.dp, RoundedCornerShape(24.dp), ambientColor = Color.Black.copy(alpha = 0.05f)),
                    shape = RoundedCornerShape(24.dp),
                    color = Color.White
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(
                                Brush.linearGradient(
                                    listOf(Color(0xFFF7FBF7), Color(0xFFEBF5EB))
                                )
                            )
                    ) {

                        // HERO ILLUSTRATION TWEAKS HERE
                        Image(
                            painter = painterResource(id = R.drawable.ill_services_hero),
                            contentDescription = null,
                            contentScale = ContentScale.Fit,
                            alignment = Alignment.BottomEnd,
                            alpha = 0.7f, // 1. Tweak Hero Transparency
                            modifier = Modifier
                                .matchParentSize()
                                .padding(start = 160.dp, top = 20.dp) // 2. Tweak Hero Size
                                .offset(x = 10.dp, y = 18.dp) // 3. Tweak Hero Position
                        )

                        // Hero Text restrained strictly to the left side
                        Column(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(24.dp)
                                .fillMaxWidth(0.55f),
                            verticalArrangement = Arrangement.Center
                        ) {
                            Text(
                                text = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("smart solutions for healthier crops", currentLang),
                                color = Color(0xFF1B4332),
                                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold),
                                lineHeight = 26.sp
                            )
                            Spacer(Modifier.height(8.dp))
                            Text(
                                text = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("crop services hero sub", currentLang),
                                color = Color(0xFF525252),
                                style = MaterialTheme.typography.bodySmall,
                                lineHeight = 16.sp
                            )
                        }
                    }
                }

                // 2. Section Title
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Rounded.Eco,
                            contentDescription = null,
                            tint = Color(0xFF66BB6A),
                            modifier = Modifier.size(22.dp)
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("available services", currentLang),
                            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B4332))
                        )
                    }
                    Text(
                        text = com.example.farmfusionapp.utils.AppLocalizer.localizeCropServicesPhrase("available services sub", currentLang),
                        style = MaterialTheme.typography.bodyMedium.copy(color = Color(0xFF616161)),
                        modifier = Modifier.padding(start = 30.dp)
                    )
                }

                // 3. Grid mapping the 4 Cards
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(bottom = 32.dp)
                ) {
                    items(services) { service ->
                        Surface(
                            onClick = { navController.navigate(service.route) },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(200.dp)
                                .shadow(8.dp, RoundedCornerShape(24.dp), ambientColor = Color.Black.copy(alpha = 0.05f), spotColor = Color.Black.copy(alpha = 0.05f)),
                            shape = RoundedCornerShape(24.dp),
                            color = service.iconBgColor // CARD IS NOW THE FAINT TINT COLOR
                        ) {
                            Box(modifier = Modifier.fillMaxSize()) {

                                // CARD ILLUSTRATION - Driven entirely by the data class properties
                                Image(
                                    painter = painterResource(id = service.illustrationRes),
                                    contentDescription = null,
                                    contentScale = ContentScale.Fit,
                                    alignment = Alignment.BottomEnd,
                                    alpha = service.imageAlpha,
                                    modifier = Modifier
                                        .matchParentSize()
                                        .padding(start = service.imagePaddingStart, top = service.imagePaddingTop)
                                        .offset(x = service.imageOffsetX, y = service.imageOffsetY)
                                )

                                // Foreground Layout
                                Column(
                                    modifier = Modifier
                                        .fillMaxSize()
                                        .padding(16.dp),
                                    verticalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Column {
                                        // Icon background changed to White to stand out against tinted card
                                        Surface(
                                            shape = CircleShape,
                                            color = Color.White,
                                            modifier = Modifier.size(40.dp)
                                        ) {
                                            Box(contentAlignment = Alignment.Center) {
                                                Icon(service.icon, null, tint = service.iconTintColor, modifier = Modifier.size(20.dp))
                                            }
                                        }
                                        Spacer(Modifier.height(12.dp))
                                        Text(
                                            text = service.title,
                                            fontWeight = FontWeight.ExtraBold,
                                            style = MaterialTheme.typography.titleMedium,
                                            color = Color(0xFF1B1B1B)
                                        )
                                        Spacer(Modifier.height(4.dp))
                                        Text(
                                            text = service.subtitle,
                                            color = Color(0xFF616161),
                                            style = MaterialTheme.typography.bodySmall,
                                            lineHeight = 14.sp
                                        )
                                    }

                                    // Bottom Left Circular Arrow
                                    Surface(
                                        shape = CircleShape,
                                        color = Color.White,
                                        shadowElevation = 2.dp,
                                        modifier = Modifier.size(32.dp)
                                    ) {
                                        Box(contentAlignment = Alignment.Center) {
                                            Icon(
                                                Icons.AutoMirrored.Rounded.KeyboardArrowRight,
                                                contentDescription = "Proceed",
                                                tint = service.iconTintColor,
                                                modifier = Modifier.size(16.dp)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}