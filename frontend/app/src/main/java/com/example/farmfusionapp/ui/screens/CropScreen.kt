package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController

enum class CropStep {
    REPORT_CHECK,
    SOIL_INPUT,
    RESULT
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropScreen(navController: NavController) {
    var currentStep by remember { mutableStateOf(CropStep.REPORT_CHECK) }
    var hasSoilReport by remember { mutableStateOf<Boolean?>(null) }
    
    // Inputs
    var nitrogen by remember { mutableStateOf("") }
    var phosphorus by remember { mutableStateOf("") }
    var potassium by remember { mutableStateOf("") }
    var soilType by remember { mutableStateOf("Black") }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Crop Advice", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { 
                        if (currentStep == CropStep.REPORT_CHECK) navController.popBackStack()
                        else if (currentStep == CropStep.SOIL_INPUT) currentStep = CropStep.REPORT_CHECK
                        else currentStep = CropStep.SOIL_INPUT
                    }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(24.dp)
        ) {
            AnimatedContent(
                targetState = currentStep,
                transitionSpec = {
                    fadeIn() togetherWith fadeOut()
                },
                label = "StepTransition"
            ) { step ->
                when (step) {
                    CropStep.REPORT_CHECK -> {
                        CropReportCheckStep(onChoice = { hasReport: Boolean ->
                            hasSoilReport = hasReport
                            currentStep = CropStep.SOIL_INPUT
                        })
                    }
                    CropStep.SOIL_INPUT -> {
                        SoilInputStep(
                            isAdvanced = hasSoilReport == true,
                            n = nitrogen, onNChange = { nitrogen = it },
                            p = phosphorus, onPChange = { phosphorus = it },
                            k = potassium, onKChange = { potassium = it },
                            soil = soilType, onSoilChange = { soilType = it },
                            onCalculate = { currentStep = CropStep.RESULT }
                        )
                    }
                    CropStep.RESULT -> {
                        CropResultView(
                            soil = soilType,
                            isAdvanced = hasSoilReport == true,
                            onReset = { currentStep = CropStep.REPORT_CHECK }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun CropReportCheckStep(onChoice: (Boolean) -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            "Do you have a Soil Report?",
            style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
            textAlign = TextAlign.Center
        )
        Text(
            "मिट्टी की जांच रिपोर्ट है?",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier.padding(top = 4.dp, bottom = 40.dp)
        )

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            CropChoiceCard(
                text = "YES",
                subtext = "हां",
                icon = Icons.Rounded.Description,
                color = MaterialTheme.colorScheme.primaryContainer,
                modifier = Modifier.weight(1f),
                onClick = { onChoice(true) }
            )
            CropChoiceCard(
                text = "NO",
                subtext = "नहीं",
                icon = Icons.Rounded.QuestionMark,
                color = MaterialTheme.colorScheme.secondaryContainer,
                modifier = Modifier.weight(1f),
                onClick = { onChoice(false) }
            )
        }
    }
}

@Composable
fun CropChoiceCard(text: String, subtext: String, icon: ImageVector, color: Color, modifier: Modifier, onClick: () -> Unit) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.95f else 1f,
        label = "cropChoiceScale"
    )

    ElevatedCard(
        onClick = onClick,
        modifier = modifier.height(180.dp).scale(scale),
        shape = RoundedCornerShape(32.dp),
        colors = CardDefaults.elevatedCardColors(containerColor = color),
        interactionSource = interactionSource
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(icon, null, modifier = Modifier.size(48.dp))
            Spacer(modifier = Modifier.height(12.dp))
            Text(text, fontWeight = FontWeight.Black, fontSize = 24.sp)
            Text(subtext, fontSize = 18.sp)
        }
    }
}

@Composable
fun SoilInputStep(
    isAdvanced: Boolean,
    n: String, onNChange: (String) -> Unit,
    p: String, onPChange: (String) -> Unit,
    k: String, onKChange: (String) -> Unit,
    soil: String, onSoilChange: (String) -> Unit,
    onCalculate: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize()) {
        Text(
            text = if (isAdvanced) "Enter Soil Numbers" else "Select Soil Color",
            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)
        )
        Spacer(modifier = Modifier.height(24.dp))

        if (isAdvanced) {
            SoilNutrientInput("Nitrogen (N)", n, onNChange, Color(0xFFE57373))
            SoilNutrientInput("Phosphorus (P)", p, onPChange, Color(0xFF81C784))
            SoilNutrientInput("Potassium (K)", k, onKChange, Color(0xFF64B5F6))
        } else {
            val soils = listOf("Black", "Red", "Alluvial", "Sandy")
            soils.forEach { s ->
                val isSelected = soil == s
                Surface(
                    onClick = { onSoilChange(s) },
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                    shape = RoundedCornerShape(20.dp),
                    color = if (isSelected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                    border = if (isSelected) BorderStroke(2.dp, MaterialTheme.colorScheme.primary) else null
                ) {
                    Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.Landscape, null, tint = if (isSelected) MaterialTheme.colorScheme.primary else Color.Gray)
                        Spacer(modifier = Modifier.width(16.dp))
                        Text(s, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = onCalculate,
            modifier = Modifier.fillMaxWidth().height(80.dp),
            shape = RoundedCornerShape(24.dp)
        ) {
            Text("GET RECOMMENDATION", fontSize = 20.sp, fontWeight = FontWeight.Black)
        }
    }
}

@Composable
fun SoilNutrientInput(label: String, value: String, onValueChange: (String) -> Unit, color: Color) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
        shape = RoundedCornerShape(16.dp),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        leadingIcon = { Icon(Icons.Rounded.Science, null, tint = color) },
        textStyle = LocalTextStyle.current.copy(fontSize = 20.sp, fontWeight = FontWeight.Bold)
    )
}

@Composable
fun CropResultView(soil: String, isAdvanced: Boolean, onReset: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Main Crop Result
        ElevatedCard(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(40.dp),
            colors = CardDefaults.elevatedCardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
        ) {
            Column(
                modifier = Modifier.padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("BEST CROP FOR YOU", style = MaterialTheme.typography.labelLarge)
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = if (soil == "Black") "COTTON ☁️" else "WHEAT 🌾",
                    style = MaterialTheme.typography.displayMedium.copy(fontWeight = FontWeight.Black)
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Status Details
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            StatusCard("Soil Status", "Healthy ✅", modifier = Modifier.weight(1f))
            StatusCard("Water Needs", "Medium 💧", modifier = Modifier.weight(1f))
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Fertilizer Advice
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
        ) {
            Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.LocalFlorist, null, modifier = Modifier.size(32.dp))
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text("FERTILIZER TIP", fontWeight = FontWeight.Bold)
                    Text("Use 50kg Urea per acre for best growth.")
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = onReset,
            modifier = Modifier.fillMaxWidth().height(64.dp),
            shape = RoundedCornerShape(20.dp),
            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.secondary)
        ) {
            Text("TRY AGAIN", fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun StatusCard(title: String, value: String, modifier: Modifier) {
    Card(modifier = modifier, shape = RoundedCornerShape(24.dp)) {
        Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(title, style = MaterialTheme.typography.labelMedium)
            Text(value, fontWeight = FontWeight.Black, fontSize = 18.sp)
        }
    }
}
