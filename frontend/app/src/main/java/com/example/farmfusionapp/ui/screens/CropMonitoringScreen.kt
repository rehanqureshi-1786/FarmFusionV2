package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController

data class Reminder(val id: Int, val title: String, val time: String, val icon: androidx.compose.ui.graphics.vector.ImageVector)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropMonitoringScreen(navController: NavController) {
    val reminders = listOf(
        Reminder(1, "Morning Irrigation", "06:00 AM", Icons.Rounded.WaterDrop),
        Reminder(2, "Fertilizer Check", "09:30 AM", Icons.Rounded.Agriculture),
        Reminder(3, "Soil Moisture Check", "04:00 PM", Icons.Rounded.Speed)
    )

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Crop Monitoring", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { /* Add Reminder */ },
                containerColor = MaterialTheme.colorScheme.primaryContainer
            ) {
                Icon(Icons.Rounded.Add, contentDescription = "Add")
            }
        }
    ) { paddingValues ->
        Column(modifier = Modifier.padding(paddingValues).padding(20.dp)) {
            // Live Status Card
            ElevatedCard(
                modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
                shape = RoundedCornerShape(32.dp),
                colors = CardDefaults.elevatedCardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer)
            ) {
                Row(modifier = Modifier.padding(24.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Current Field Status", style = MaterialTheme.typography.labelLarge)
                        Text("Soil Moisture: 45%", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Black))
                        Text("Status: Healthy ✅", style = MaterialTheme.typography.bodyMedium)
                    }
                    Icon(Icons.Rounded.Thermostat, null, modifier = Modifier.size(64.dp), tint = MaterialTheme.colorScheme.onTertiaryContainer)
                }
            }

            Text("Scheduled Reminders", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
            Spacer(modifier = Modifier.height(16.dp))

            LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                items(reminders) { reminder ->
                    ReminderItem(reminder)
                }
            }
        }
    }
}

@Composable
fun ReminderItem(reminder: Reminder) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(reminder.icon, null, modifier = Modifier.size(32.dp), tint = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(reminder.title, fontWeight = FontWeight.Bold)
                Text(reminder.time, style = MaterialTheme.typography.bodySmall)
            }
            Switch(checked = true, onCheckedChange = {})
        }
    }
}
