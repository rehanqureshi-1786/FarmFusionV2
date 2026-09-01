package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropHarvestingScreen(navController: NavController) {
    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Harvesting Help", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(modifier = Modifier.fillMaxSize().padding(padding).padding(20.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            item {
                HarvestActionCard("Find Labour", "Hire workers for harvesting", Icons.Rounded.Groups, Color(0xFFE8F5E9)) {
                    navController.navigate(NavRoutes.LabourServices)
                }
            }
            item {
                HarvestActionCard("Nearby Cold Storage", "Save your crop from rotting", Icons.Rounded.AcUnit, Color(0xFFE1F5FE)) {
                    /* Cold Storage functionality */
                }
            }
            item {
                HarvestActionCard("Equipment Rental", "Rent tractors or harvesters", Icons.Rounded.Agriculture, Color(0xFFFFF3E0)) {
                    /* Equipment Rental functionality */
                }
            }
        }
    }
}

@Composable
fun HarvestActionCard(title: String, desc: String, icon: ImageVector, color: Color, onClick: () -> Unit) {
    ElevatedCard(onClick = onClick, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(24.dp), colors = CardDefaults.elevatedCardColors(containerColor = color)) {
        Row(modifier = Modifier.padding(24.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(icon, null, modifier = Modifier.size(48.dp), tint = MaterialTheme.colorScheme.primary)
            Spacer(Modifier.width(16.dp))
            Column {
                Text(title, style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
                Text(desc, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}
