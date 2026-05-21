package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController

enum class AlertSeverity {
    EMERGENCY, // Red
    WARNING,   // Yellow
    INFO       // Green
}

enum class AlertType {
    WEATHER,
    PEST,
    IRRIGATION
}

data class FarmAlert(
    val id: Int,
    val title: String,
    val description: String,
    val type: AlertType,
    val severity: AlertSeverity,
    val time: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AlertsScreen(navController: NavController) {
    val alerts = listOf(
        FarmAlert(
            1, "Heavy Rain Warning", "Storm expected tonight. Move harvested crops to shed.",
            AlertType.WEATHER, AlertSeverity.EMERGENCY, "2 mins ago"
        ),
        FarmAlert(
            2, "Pest Alert: Locusts", "Locust swarms reported in nearby villages. Check your fields.",
            AlertType.PEST, AlertSeverity.WARNING, "1 hour ago"
        ),
        FarmAlert(
            3, "Time to Water", "Soil moisture is low. Start drip irrigation now.",
            AlertType.IRRIGATION, AlertSeverity.INFO, "3 hours ago"
        ),
        FarmAlert(
            4, "High Heat Tomorrow", "Temp will reach 42°C. Avoid working between 12-4 PM.",
            AlertType.WEATHER, AlertSeverity.WARNING, "5 hours ago"
        )
    )

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Alerts", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(alerts) { alert ->
                AlertCard(alert)
            }
        }
    }
}

@Composable
fun AlertCard(alert: FarmAlert) {
    val containerColor = when (alert.severity) {
        AlertSeverity.EMERGENCY -> MaterialTheme.colorScheme.errorContainer
        AlertSeverity.WARNING -> Color(0xFFFFF9C4) // Light Yellow
        AlertSeverity.INFO -> Color(0xFFC8E6C9)    // Light Green
    }

    val contentColor = when (alert.severity) {
        AlertSeverity.EMERGENCY -> MaterialTheme.colorScheme.onErrorContainer
        AlertSeverity.WARNING -> Color(0xFFF57F17) // Deep Orange/Yellow
        AlertSeverity.INFO -> Color(0xFF2E7D32)    // Dark Green
    }

    val icon = when (alert.type) {
        AlertType.WEATHER -> Icons.Rounded.Thunderstorm
        AlertType.PEST -> Icons.Rounded.BugReport
        AlertType.IRRIGATION -> Icons.Rounded.WaterDrop
    }

    ElevatedCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.elevatedCardColors(containerColor = containerColor)
    ) {
        Row(
            modifier = Modifier
                .padding(20.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.Top
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .padding(top = 4.dp),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(32.dp),
                    tint = contentColor
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = alert.title,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = contentColor
                        )
                    )
                }
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Text(
                    text = alert.description,
                    style = MaterialTheme.typography.bodyLarge,
                    color = contentColor.copy(alpha = 0.8f)
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = alert.time,
                    style = MaterialTheme.typography.labelMedium,
                    color = contentColor.copy(alpha = 0.6f)
                )
            }
        }
    }
}
