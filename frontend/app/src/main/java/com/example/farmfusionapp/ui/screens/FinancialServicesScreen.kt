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
import androidx.navigation.NavController

data class FinancialService(
    val title: String,
    val desc: String,
    val icon: ImageVector,
    val color: Color
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FinancialServicesScreen(navController: NavController) {
    val services = listOf(
        FinancialService("Kisan Loans", "Apply for low-interest farming loans", Icons.Rounded.AccountBalance, Color(0xFFE8F5E9)),
        FinancialService("Crop Insurance", "Protect your farm from natural disasters", Icons.Rounded.Shield, Color(0xFFE1F5FE)),
        // Fixed deprecated icon reference
        FinancialService("Govt Schemes", "View latest PM-Kisan and other schemes", Icons.Rounded.AccountBalanceWallet, Color(0xFFFFF3E0)),
        FinancialService("Banking Help", "Connect with your nearest bank branch", Icons.Rounded.SupportAgent, Color(0xFFF3E5F5))
    )

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Financial Services", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp)) {
            Text(
                "Money & Banking Support",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(bottom = 24.dp)
            )

            LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                items(services) { service ->
                    FinanceCard(service)
                }
            }
        }
    }
}

@Composable
fun FinanceCard(service: FinancialService) {
    ElevatedCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.elevatedCardColors(containerColor = service.color)
    ) {
        Row(
            modifier = Modifier.padding(24.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = Color.White.copy(alpha = 0.6f),
                modifier = Modifier.size(56.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(service.icon, null, modifier = Modifier.size(32.dp), tint = MaterialTheme.colorScheme.primary)
                }
            }
            Spacer(Modifier.width(16.dp))
            Column {
                Text(service.title, style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
                Text(service.desc, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}
