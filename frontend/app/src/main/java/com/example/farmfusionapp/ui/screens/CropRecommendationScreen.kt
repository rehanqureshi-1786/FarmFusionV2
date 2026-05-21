package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.CropRecommendationItem
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.ui.components.*
import com.example.farmfusionapp.utils.*
import com.example.farmfusionapp.viewmodel.CropRecommendationViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// ============================================
// STEP DEFINITIONS
// ============================================
enum class RecommendationStep {
    SOIL_SELECTION,
    REPORT_CHECK,
    FARM_DETAILS,
    REPORT_PHOTO_INPUT,
    AUTO_ANALYSIS,
    RESULT
}

data class SoilTypeInfo(
    val name: String,
    val hindiName: String,
    val colorName: String,
    val colorHindi: String,
    val displayColor: Color,
    val icon: ImageVector,
    val description: String
)

data class CropRecommendationFormInputs(
    val location: String = "",
    val rainfallMm: String = "",
    val temperatureC: String = "",
    val farmSizeAcres: String = "",
    val budgetUsd: String = ""
)

// ============================================
// MAIN SCREEN
// ============================================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropRecommendationScreen(
    navController: NavController,
    viewModel: CropRecommendationViewModel = viewModel()
) {
    var currentStep by remember { mutableStateOf(RecommendationStep.SOIL_SELECTION) }
    var selectedSoil by remember { mutableStateOf<SoilTypeInfo?>(null) }
    var isAdvancedMode by remember { mutableStateOf(false) }
    var formInputs by remember { mutableStateOf(CropRecommendationFormInputs()) }

    val isLoading by viewModel.isLoading
    val error by viewModel.error
    val recommendations by viewModel.recommendations
    val aiInsights by viewModel.aiInsights
    val isSuccess by viewModel.isSuccess

    LaunchedEffect(isSuccess) {
        if (isSuccess && currentStep == RecommendationStep.AUTO_ANALYSIS) {
            delay(500)
            currentStep = RecommendationStep.RESULT
        }
    }

    val soilTypes = remember {
        listOf(
            SoilTypeInfo("Black Soil", "काली मिट्टी", "Black", "काली", Color(0xFF3E2723), Icons.Rounded.Grass, "Rich in clay, retains water well"),
            SoilTypeInfo("Red Soil", "लाल मिट्टी", "Red", "लाल", Color(0xFFD32F2F), Icons.Rounded.Terrain, "Good for cotton and pulses"),
            SoilTypeInfo("Alluvial Soil", "दोमट मिट्टी", "Light Brown", "हल्का भूरा", Color(0xFF8D6E63), Icons.Rounded.Landscape, "Very fertile, best for wheat and rice"),
            SoilTypeInfo("Sandy Soil", "रेतीली मिट्टी", "Yellow/Grey", "पीला/धूसर", Color(0xFFD4E157), Icons.Rounded.Waves, "Drains quickly, needs more water")
        )
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(stringResource(R.string.crop_advice_title), style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
                        Text("फसल सलाह", style = MaterialTheme.typography.bodyMedium.copy(color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold))
                    }
                },
                navigationIcon = {
                    IconButton(onClick = {
                        when (currentStep) {
                            RecommendationStep.SOIL_SELECTION -> navController.popBackStack()
                            RecommendationStep.REPORT_CHECK -> currentStep = RecommendationStep.SOIL_SELECTION
                            RecommendationStep.FARM_DETAILS -> currentStep = RecommendationStep.REPORT_CHECK
                            RecommendationStep.REPORT_PHOTO_INPUT -> currentStep = RecommendationStep.FARM_DETAILS
                            RecommendationStep.AUTO_ANALYSIS -> currentStep = RecommendationStep.FARM_DETAILS
                            RecommendationStep.RESULT -> {
                                currentStep = RecommendationStep.SOIL_SELECTION
                                viewModel.resetState()
                                selectedSoil = null
                                formInputs = CropRecommendationFormInputs()
                            }
                        }
                    }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", modifier = Modifier.size(28.dp))
                    }
                }
            )
        }
    ) { paddingValues ->
        NeoScaffoldBackground(modifier = Modifier.fillMaxSize().padding(paddingValues)) {
            Box(modifier = Modifier.fillMaxSize().padding(horizontal = 20.dp, vertical = 16.dp)) {
                StepIndicator(
                    currentStep = when (currentStep) {
                        RecommendationStep.SOIL_SELECTION -> 1
                        RecommendationStep.REPORT_CHECK -> 2
                        RecommendationStep.FARM_DETAILS -> 3
                        RecommendationStep.REPORT_PHOTO_INPUT, RecommendationStep.AUTO_ANALYSIS -> 4
                        RecommendationStep.RESULT -> 5
                    },
                    totalSteps = 5,
                    modifier = Modifier.padding(bottom = 24.dp)
                )

                AnimatedContent(
                    targetState = currentStep,
                    label = "RecFlowTransition",
                    modifier = Modifier.padding(top = 40.dp)
                ) { step ->
                    when (step) {
                        RecommendationStep.SOIL_SELECTION -> SoilSelectionStep(soilTypes, selectedSoil) { selectedSoil = it; currentStep = RecommendationStep.REPORT_CHECK }
                        RecommendationStep.REPORT_CHECK -> CropRecommendationReportCheckStep { isAdvancedMode = it; currentStep = RecommendationStep.FARM_DETAILS }
                        RecommendationStep.FARM_DETAILS -> FarmDetailsStep(selectedSoil?.name.orEmpty(), formInputs, { formInputs = it }) { currentStep = if (isAdvancedMode) RecommendationStep.REPORT_PHOTO_INPUT else RecommendationStep.AUTO_ANALYSIS }
                        RecommendationStep.REPORT_PHOTO_INPUT -> PhotoInputStep { currentStep = RecommendationStep.AUTO_ANALYSIS }
                        RecommendationStep.AUTO_ANALYSIS -> AutoAnalysisStep(formInputs, selectedSoil?.name ?: "", viewModel)
                        RecommendationStep.RESULT -> RecommendationResultStep(selectedSoil, recommendations, aiInsights, { currentStep = RecommendationStep.SOIL_SELECTION; viewModel.resetState(); selectedSoil = null; formInputs = CropRecommendationFormInputs() }, {
                            val top = recommendations.maxByOrNull { it.confidence_score }
                            if (top != null) { AgriStoreContext.setForCrop(top.crop_name); navController.navigate(NavRoutes.ProductStore) }
                        })
                    }
                }
            }
        }
    }
}

@Composable
fun SoilSelectionStep(soils: List<SoilTypeInfo>, selected: SoilTypeInfo?, onSelect: (SoilTypeInfo) -> Unit) {
    val scrollState = rememberScrollState()
    Column(modifier = Modifier.fillMaxSize().verticalScroll(scrollState)) {
        Surface(modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp).shadow(4.dp, RoundedCornerShape(24.dp)), shape = RoundedCornerShape(24.dp), color = Color.White, border = BorderStroke(1.dp, Color(0xFFF0F0F0))) {
            Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(modifier = Modifier.size(52.dp).background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), CircleShape), contentAlignment = Alignment.Center) {
                    Icon(Icons.Rounded.Grass, null, modifier = Modifier.size(32.dp), tint = MaterialTheme.colorScheme.primary)
                }
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(stringResource(R.string.soil_type_selection_title), style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
                    Text("मिट्टी का प्रकार चुनें", style = MaterialTheme.typography.bodyMedium.copy(color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold))
                }
            }
        }
        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
            soils.forEach { soil ->
                val isSelected = selected == soil
                Surface(onClick = { onSelect(soil) }, modifier = Modifier.fillMaxWidth().shadow(if(isSelected) 8.dp else 2.dp, RoundedCornerShape(24.dp)), shape = RoundedCornerShape(24.dp), color = Color.White, border = BorderStroke(if (isSelected) 2.dp else 1.dp, if (isSelected) MaterialTheme.colorScheme.primary else Color(0xFFF0F0F0))) {
                    Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(modifier = Modifier.size(64.dp).clip(CircleShape).background(soil.displayColor).border(2.dp, Color.White, CircleShape), contentAlignment = Alignment.Center) {
                            Icon(soil.icon, null, modifier = Modifier.size(32.dp), tint = Color.White)
                        }
                        Spacer(modifier = Modifier.width(16.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(soil.name, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
                            Text(soil.description, style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray))
                        }
                        if (isSelected) Icon(Icons.Rounded.CheckCircle, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(24.dp))
                    }
                }
            }
        }
    }
}

@Composable
fun CropRecommendationReportCheckStep(onChoice: (Boolean) -> Unit) {
    Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
        Surface(modifier = Modifier.size(140.dp).shadow(8.dp, CircleShape), shape = CircleShape, color = Color.White, border = BorderStroke(1.dp, Color(0xFFF0F0F0))) {
            Box(contentAlignment = Alignment.Center) { Icon(Icons.Rounded.Description, null, modifier = Modifier.size(64.dp), tint = MaterialTheme.colorScheme.primary) }
        }
        Spacer(modifier = Modifier.height(32.dp))
        Text(stringResource(R.string.has_soil_health_card), style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)), textAlign = TextAlign.Center)
        Text("क्या आपके पास मिट्टी स्वास्थ्य कार्ड है?", style = MaterialTheme.typography.bodyMedium.copy(color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold), textAlign = TextAlign.Center)
        Spacer(modifier = Modifier.height(48.dp))
        PremiumButton(stringResource(R.string.yes_have_report), { onChoice(true) }, icon = Icons.Rounded.PhotoCamera)
        Spacer(modifier = Modifier.height(16.dp))
        PremiumOutlinedButton(stringResource(R.string.no_use_auto_analysis), { onChoice(false) }, icon = Icons.Rounded.AutoAwesome)
    }
}

@Composable
fun FarmDetailsStep(selectedSoil: String, inputs: CropRecommendationFormInputs, onInputsChange: (CropRecommendationFormInputs) -> Unit, onContinue: () -> Unit) {
    val scrollState = rememberScrollState()
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val canContinue = inputs.location.isNotBlank() && inputs.farmSizeAcres.isNotBlank() && inputs.rainfallMm.isNotBlank() && inputs.temperatureC.isNotBlank()

    fun autoFillFromLocation() {
        scope.launch {
            val location = getDeviceLocation(context) ?: return@launch
            val (lat, lon) = location
            var next = inputs
            val appLanguage = LanguagePreferences.getSelectedLanguage(context) ?: "en"
            getCityFromLocation(context, lat, lon, appLanguage)?.let { if(next.location.isBlank()) next = next.copy(location = it) }
            runCatching { RetrofitInstance.farmFusionApi.getCurrentWeather(lat, lon) }.getOrNull()?.body()?.data?.let { if(next.temperatureC.isBlank()) next = next.copy(temperatureC = it.temperature_c.toInt().toString()) }
            onInputsChange(next)
        }
    }

    Column(modifier = Modifier.fillMaxSize().verticalScroll(scrollState), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text(stringResource(R.string.basic_details_title), style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
        Surface(modifier = Modifier.fillMaxWidth().shadow(2.dp, RoundedCornerShape(16.dp)), shape = RoundedCornerShape(16.dp), color = Color(0xFFF9F9F9)) {
            Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.Grass, null, tint = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.width(12.dp))
                Column {
                    Text(stringResource(R.string.soil_type_selected), style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.Bold))
                    Text(selectedSoil.ifBlank { "Select soil in previous step" }, style = MaterialTheme.typography.titleMedium)
                }
            }
        }
        PremiumTextField(inputs.location, { onInputsChange(inputs.copy(location = it)) }, label = stringResource(R.string.village_district_label), leadingIcon = Icons.Rounded.LocationOn)
        PremiumTextField(inputs.farmSizeAcres, { onInputsChange(inputs.copy(farmSizeAcres = it)) }, label = stringResource(R.string.farm_size_label), leadingIcon = Icons.Rounded.SquareFoot)
        PremiumTextField(inputs.rainfallMm, { onInputsChange(inputs.copy(rainfallMm = it)) }, label = stringResource(R.string.annual_rainfall_label), leadingIcon = Icons.Rounded.WaterDrop)
        PremiumTextField(inputs.temperatureC, { onInputsChange(inputs.copy(temperatureC = it)) }, label = stringResource(R.string.avg_temp_label), leadingIcon = Icons.Rounded.Thermostat)
        
        AssistChip(onClick = { autoFillFromLocation() }, label = { Text(stringResource(R.string.refresh_autofill)) }, leadingIcon = { Icon(Icons.Rounded.MyLocation, null, modifier = Modifier.size(18.dp)) })
        Spacer(modifier = Modifier.height(16.dp))
        PremiumButton(stringResource(R.string.continue_button), onContinue, icon = Icons.AutoMirrored.Rounded.ArrowForward, enabled = canContinue)
    }
}

@Composable
fun PhotoInputStep(onComplete: () -> Unit) {
    Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
        Surface(modifier = Modifier.size(200.dp).shadow(4.dp, RoundedCornerShape(32.dp)), shape = RoundedCornerShape(32.dp), color = Color.White, border = BorderStroke(1.dp, Color(0xFFF0F0F0))) {
            Box(contentAlignment = Alignment.Center) { Icon(Icons.Rounded.AddAPhoto, null, modifier = Modifier.size(64.dp), tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)) }
        }
        Spacer(Modifier.height(32.dp))
        Text(stringResource(R.string.scan_soil_report), style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
        Spacer(Modifier.height(40.dp))
        PremiumButton(stringResource(R.string.take_photo), onComplete, icon = Icons.Rounded.Camera)
    }
}

@Composable
fun AutoAnalysisStep(formInputs: CropRecommendationFormInputs, soilType: String, viewModel: CropRecommendationViewModel) {
    val context = LocalContext.current
    LaunchedEffect(Unit) {
        val lang = LocaleHelper.apiLanguageCode(LanguagePreferences.getSelectedLanguage(context) ?: "en")
        viewModel.fetchRecommendations(
            location = formInputs.location,
            soilType = soilType,
            rainfallMm = formInputs.rainfallMm.toDoubleOrNull() ?: 1000.0,
            temperatureC = formInputs.temperatureC.toDoubleOrNull() ?: 25.0,
            farmSizeAcres = formInputs.farmSizeAcres.toDoubleOrNull() ?: 1.0,
            preferredLanguage = lang
        )
    }
    Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
        CircularProgressIndicator(modifier = Modifier.size(64.dp))
        Spacer(Modifier.height(24.dp))
        Text("AI is analyzing...", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
    }
}

@Composable
fun RecommendationResultStep(soil: SoilTypeInfo?, recommendations: List<CropRecommendationItem>, aiInsights: String, onReset: () -> Unit, onOpenAgriStore: () -> Unit) {
    val scrollState = rememberScrollState()
    Column(modifier = Modifier.fillMaxSize().verticalScroll(scrollState), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Surface(modifier = Modifier.fillMaxWidth().shadow(4.dp, RoundedCornerShape(24.dp)), shape = RoundedCornerShape(24.dp), color = Color.White) {
            Column(modifier = Modifier.padding(20.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.AutoAwesome, null, tint = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.width(12.dp))
                    Text("AI Best Recommendations", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
                }
                Text("Based on your ${soil?.name ?: "Field"} and location", style = MaterialTheme.typography.bodyMedium, color = Color.Gray)
            }
        }
        if (aiInsights.isNotEmpty()) GlassPanel { Row { Text("💡", fontSize = 24.sp); Spacer(Modifier.width(12.dp)); Text(aiInsights, style = MaterialTheme.typography.bodyLarge) } }
        recommendations.forEach { CropResultCard(it) }
        PremiumButton("Shop seeds & inputs", onOpenAgriStore, icon = Icons.Rounded.ShoppingBag)
        PremiumOutlinedButton("START OVER", onReset, icon = Icons.Rounded.Refresh)
        Spacer(Modifier.height(40.dp))
    }
}

@Composable
fun CropResultCard(crop: CropRecommendationItem) {
    Surface(modifier = Modifier.fillMaxWidth().shadow(4.dp, RoundedCornerShape(24.dp)), shape = RoundedCornerShape(24.dp), color = Color.White, border = BorderStroke(1.dp, Color(0xFFF0F0F0))) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Column {
                    Text(crop.crop_name, style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
                    Surface(color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), shape = RoundedCornerShape(8.dp)) {
                        Text("Match: ${(crop.confidence_score * 100).toInt()}%", modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp), style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary))
                    }
                }
                Surface(color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), shape = CircleShape, modifier = Modifier.size(52.dp)) {
                    Box(contentAlignment = Alignment.Center) { Icon(Icons.Rounded.Agriculture, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(28.dp)) }
                }
            }
            HorizontalDivider(modifier = Modifier.padding(vertical = 16.dp), thickness = 0.5.dp, color = Color(0xFFF5F5F5))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                ResultDetailItem(Icons.Rounded.TrendingUp, "Profit", "High", Modifier.weight(1f))
                Box(modifier = Modifier.height(32.dp).width(1.dp).background(Color(0xFFF0F0F0)))
                ResultDetailItem(Icons.Rounded.Schedule, "Duration", "${crop.growing_duration_months} Mon", Modifier.weight(1f))
                Box(modifier = Modifier.height(32.dp).width(1.dp).background(Color(0xFFF0F0F0)))
                ResultDetailItem(Icons.Rounded.WaterDrop, "Water", crop.water_requirement, Modifier.weight(1f))
            }
        }
    }
}

@Composable
fun ResultDetailItem(icon: ImageVector, label: String, value: String, modifier: Modifier = Modifier) {
    Column(modifier = modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        Icon(icon, null, modifier = Modifier.size(20.dp), tint = MaterialTheme.colorScheme.primary)
        Text(label, style = MaterialTheme.typography.labelMedium)
        Text(value, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold))
    }
}
