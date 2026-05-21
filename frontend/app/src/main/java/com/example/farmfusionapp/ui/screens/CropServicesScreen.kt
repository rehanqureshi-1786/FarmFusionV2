package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.components.NeoCard
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.components.NeoSectionTitle

data class CropServiceItem(
    val title: String,
    val hindiTitle: String,
    val icon: ImageVector,
    val route: String,
    val color: Color
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropServicesScreen(navController: NavController) {
    val services = remember {
        listOf(
            CropServiceItem("Crop Advice", "फसल सलाह", Icons.Rounded.Agriculture, NavRoutes.CropRecommendation, Color(0xFFE8F5E9)),
            CropServiceItem("Sowing Help", "बुवाई सहायता", Icons.Rounded.Grass, NavRoutes.CropSowing, Color(0xFFFFF3E0)),
            CropServiceItem("Monitoring", "निगरानी", Icons.Rounded.Speed, NavRoutes.CropMonitoring, Color(0xFFE1F5FE)),
            CropServiceItem("Disease Info", "बीमारी की जानकारी", Icons.Rounded.BugReport, NavRoutes.CropDisease, Color(0xFFFFEBEE)),
            CropServiceItem("Harvesting", "कटाई", Icons.Rounded.ContentCut, NavRoutes.CropHarvesting, Color(0xFFF3E5F5)),
            CropServiceItem("Selling", "बेचना", Icons.Rounded.Sell, NavRoutes.CropSelling, Color(0xFFE0F2F1))
        )
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Crop Services", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        NeoScaffoldBackground(modifier = Modifier.fillMaxSize().padding(padding)) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {
                // Premium Hero Card
                Surface(
                    modifier = Modifier.fillMaxWidth().height(160.dp).shadow(12.dp, RoundedCornerShape(32.dp)),
                    shape = RoundedCornerShape(32.dp),
                    color = Color.White
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize().background(
                            Brush.linearGradient(listOf(Color(0xFF66BB6A), Color(0xFF43A047), Color(0xFF2E7D32)))
                        )
                    ) {
                        Icon(
                            Icons.Rounded.Spa, null,
                            modifier = Modifier.size(140.dp).align(Alignment.BottomEnd).offset(x = 20.dp, y = 20.dp),
                            tint = Color.White.copy(alpha = 0.1f)
                        )
                        Column(
                            modifier = Modifier.fillMaxSize().padding(24.dp),
                            verticalArrangement = Arrangement.Center
                        ) {
                            Text("Complete Crop Care", color = Color.White, style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
                            Text("बीज से बिक्री तक - हम आपके साथ हैं", color = Color.White.copy(alpha = 0.9f), style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }

                NeoSectionTitle("Available Services", "Explore AI-powered field assistance")

                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    modifier = Modifier.fillMaxSize()
                ) {
                    items(services) { service ->
                        NeoCard(
                            onClick = { navController.navigate(service.route) },
                            contentPadding = PaddingValues(16.dp)
                        ) {
                            Box(
                                modifier = Modifier.size(56.dp).background(service.color, CircleShape),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(service.icon, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(28.dp))
                            }
                            Column {
                                Text(service.title, fontWeight = FontWeight.ExtraBold, style = MaterialTheme.typography.titleMedium)
                                Text(service.hindiTitle, color = Color.Gray, style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                }
            }
        }
    }
}
