package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.foundation.background
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.foundation.BorderStroke
import com.example.farmfusionapp.ui.components.*
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController

data class LabourJob(
    val title: String,
    val location: String,
    val workersNeeded: String,
    val price: String,
    val date: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LabourServicesScreen(navController: NavController) {
    var showHiringForm by remember { mutableStateOf(false) }
    var showGetWork by remember { mutableStateOf(false) }
    
    // Shared state for demo (In real app, this would be in a ViewModel/Database)
    val jobsList = remember { 
        mutableStateListOf(
            LabourJob("Wheat Harvesting", "North Farm", "5", "₹500/day", "Today"),
            LabourJob("Soil Preparation", "East Field", "2", "₹450/day", "Tomorrow"),
            LabourJob("Fertilizer Spray", "Main Orchard", "3", "₹600/day", "Monday")
        )
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Labour Service", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)) },
                navigationIcon = {
                    IconButton(onClick = { 
                        if (showHiringForm || showGetWork) {
                            showHiringForm = false
                            showGetWork = false
                        } else {
                            navController.popBackStack() 
                        }
                    }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        NeoScaffoldBackground(modifier = Modifier.fillMaxSize().padding(padding)) {
            Box(modifier = Modifier.fillMaxSize()) {
                if (!showHiringForm && !showGetWork) {
                    // Initial Selection Screen
                    LabourSelectionScreen(
                        onHire = { showHiringForm = true },
                        onGetWork = { showGetWork = true }
                    )
                } else if (showHiringForm) {
                    LabourHiringForm(
                        onJobPosted = { newJob ->
                            jobsList.add(0, newJob)
                            showHiringForm = false
                            showGetWork = true // Show the list after posting
                        }
                    )
                } else if (showGetWork) {
                    GetWorkScreen(jobsList)
                }
            }
        }
    }
}

@Composable
fun LabourSelectionScreen(onHire: () -> Unit, onGetWork: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        ModernSelectionCard(
            title = "Hire Labour",
            subtitle = "मजदूर बुलाएं",
            icon = Icons.Rounded.PersonAdd,
            gradient = listOf(Color(0xFFE8F5E9), Color(0xFFC8E6C9)),
            iconTint = Color(0xFF2E7D32),
            onClick = onHire
        )
        
        Spacer(Modifier.height(24.dp))
        
        ModernSelectionCard(
            title = "Get Work",
            subtitle = "काम ढूंढें",
            icon = Icons.Rounded.Search,
            gradient = listOf(Color(0xFFE3F2FD), Color(0xFFBBDEFB)),
            iconTint = Color(0xFF1565C0),
            onClick = onGetWork
        )
    }
}

@Composable
fun ModernSelectionCard(
    title: String,
    subtitle: String,
    icon: ImageVector,
    gradient: List<Color>,
    iconTint: Color,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(160.dp)
            .shadow(8.dp, RoundedCornerShape(32.dp)),
        shape = RoundedCornerShape(32.dp),
        color = Color.White
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Brush.linearGradient(gradient))
        ) {
            Column(
                modifier = Modifier.fillMaxSize().padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .background(Color.White.copy(alpha = 0.5f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(icon, null, modifier = Modifier.size(32.dp), tint = iconTint)
                }
                Spacer(Modifier.height(12.dp))
                Text(title, style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
                Text(subtitle, style = MaterialTheme.typography.bodyMedium.copy(color = iconTint))
            }
        }
    }
}

@Composable
fun LabourHiringForm(onJobPosted: (LabourJob) -> Unit) {
    var details by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("") }
    var count by remember { mutableStateOf("") }
    var price by remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text("Hire Workers", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
        Text("मजदूरों के लिए जानकारी भरें", color = MaterialTheme.colorScheme.primary)
        
        OutlinedTextField(
            value = details, onValueChange = { details = it },
            label = { Text("What work? (e.g. Rice Sowing)") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp)
        )

        OutlinedTextField(
            value = location, onValueChange = { location = it },
            label = { Text("Farm Location") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp)
        )

        OutlinedTextField(
            value = count, onValueChange = { count = it },
            label = { Text("How many workers needed?") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        OutlinedTextField(
            value = price, onValueChange = { price = it },
            label = { Text("Pay per day (₹)") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        Spacer(Modifier.weight(1f))

        Button(
            onClick = {
                if (details.isNotBlank() && location.isNotBlank()) {
                    onJobPosted(LabourJob(details, location, count, "₹$price/day", "Just now"))
                }
            },
            modifier = Modifier.fillMaxWidth().height(80.dp),
            shape = RoundedCornerShape(24.dp)
        ) {
            Text("POST JOB", fontWeight = FontWeight.Black, fontSize = 22.sp)
        }
    }
}

@Composable
fun GetWorkScreen(jobs: List<LabourJob>) {
    Column(modifier = Modifier.fillMaxSize().padding(20.dp)) {
        Text("Available Work Near You", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
        Text("आपके आसपास उपलब्ध काम", color = MaterialTheme.colorScheme.primary)
        Spacer(Modifier.height(16.dp))
        
        LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
            items(jobs) { job ->
                JobCard(job)
            }
        }
    }
}

@Composable
fun JobCard(job: LabourJob) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        shadowElevation = 4.dp,
        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(Icons.Rounded.Work, null, tint = MaterialTheme.colorScheme.primary)
                }
                Spacer(Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(job.title, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
                    Text(job.location, style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray))
                }
                Text(job.price, fontWeight = FontWeight.Black, color = MaterialTheme.colorScheme.primary, fontSize = 18.sp)
            }
            
            HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp, color = Color(0xFFF5F5F5))
            
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Needed: ${job.workersNeeded} Workers", style = MaterialTheme.typography.labelMedium.copy(color = Color(0xFF444444)))
                Text(job.date, style = MaterialTheme.typography.labelSmall, color = Color.LightGray)
            }
            
            Spacer(Modifier.height(16.dp))
            
            Button(
                onClick = { /* Contact Farmer */ },
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
            ) {
                Icon(Icons.Rounded.Call, null, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(8.dp))
                Text("CONTACT FARMER", fontWeight = FontWeight.Bold, fontSize = 14.sp)
            }
        }
    }
}
