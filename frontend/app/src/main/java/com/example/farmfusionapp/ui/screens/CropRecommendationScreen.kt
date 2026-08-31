package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.GenericShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.automirrored.rounded.KeyboardArrowRight
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
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
// CUSTOM SHAPES
// ============================================
val WavyRightShape = GenericShape { size, _ ->
    moveTo(0f, 0f)
    lineTo(size.width * 0.70f, 0f)
    quadraticBezierTo(
        size.width * 1.1f, size.height * 0.5f,
        size.width * 0.70f, size.height
    )
    lineTo(0f, size.height)
    close()
}

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
    val imageRes: Int,
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
            SoilTypeInfo("Black Soil", "काली मिट्टी", "Black", "काली", Color(0xFF3E2723), Icons.Rounded.Grass, R.drawable.ill_soil_black, "Rich in clay,\nretains water well"),
            SoilTypeInfo("Red Soil", "लाल मिट्टी", "Red", "लाल", Color(0xFFD32F2F), Icons.Rounded.Terrain, R.drawable.ill_soil_red, "Good for cotton\nand pulses"),
            SoilTypeInfo("Alluvial Soil", "दोमट मिट्टी", "Light Brown", "हल्का भूरा", Color(0xFF8D6E63), Icons.Rounded.Landscape, R.drawable.ill_soil_alluvial, "Very fertile, best for\nwheat and rice"),
            SoilTypeInfo("Sandy Soil", "रेतीली मिट्टी", "Yellow/Grey", "पीला/धूसर", Color(0xFFCDDC39), Icons.Rounded.Waves, R.drawable.ill_soil_sandy, "Drains quickly,\nneeds more water")
        )
    }

    // Organic Background setup
    Box(modifier = Modifier.fillMaxSize()) {
        // Light-Brown + Yellow + Green Gradient Layer
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.linearGradient(
                        colors = listOf(
                            Color(0xFFF3EBE1), // Light Brown (Top Left & Middle)
                            Color(0xFFEDF2EA), // Very light hint of Green (Top Right)
                            Color(0xFFFDF8E4)  // Yellow (Bottom)
                        ),
                        start = Offset(0f, 0f),
                        end = Offset(Float.POSITIVE_INFINITY, Float.POSITIVE_INFINITY)
                    )
                )
        )

        // Bottom Crop Illustration
        Image(
            painter = painterResource(id = R.drawable.ill_crop_bottom_bg),
            contentDescription = null,
            contentScale = ContentScale.FillWidth,
            alpha = 0.45f,
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
        )

        Scaffold(
            containerColor = Color.Transparent, // Makes scaffold transparent so gradient shows
            topBar = {
                // New Glassmorphism Header
                Column(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .statusBarsPadding()
                            .padding(horizontal = 20.dp)
                            .padding(top = 16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Frosted Glass Back Button
                        Surface(
                            onClick = {
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
                            },
                            shape = CircleShape,
                            color = Color.White.copy(alpha = 0.55f),
                            border = BorderStroke(1.dp, Color.White),
                            modifier = Modifier.size(48.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", tint = Color(0xFF1B5E20))
                            }
                        }

                        Spacer(Modifier.weight(1f))

                        Text(
                            text = stringResource(R.string.crop_advice_title),
                            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B5E20))
                        )

                        Spacer(Modifier.weight(1f))
                        Spacer(Modifier.width(48.dp)) // Added for visual symmetry against back button
                    }

                    // Frosted Glass Narrow Step Indicator Capsule
                    Surface(
                        shape = RoundedCornerShape(50.dp),
                        color = Color.White.copy(alpha = 0.55f),
                        border = BorderStroke(1.dp, Color.White),
                        modifier = Modifier
                            .align(Alignment.CenterHorizontally)
                            .padding(top = 16.dp, bottom = 8.dp)
                    ) {
                        StepIndicator(
                            currentStep = when (currentStep) {
                                RecommendationStep.SOIL_SELECTION -> 1
                                RecommendationStep.REPORT_CHECK -> 2
                                RecommendationStep.FARM_DETAILS -> 3
                                RecommendationStep.REPORT_PHOTO_INPUT, RecommendationStep.AUTO_ANALYSIS -> 4
                                RecommendationStep.RESULT -> 5
                            },
                            totalSteps = 5,
                            modifier = Modifier
                                .width(220.dp) // Made it narrow instead of full width
                                .padding(horizontal = 20.dp, vertical = 10.dp)
                        )
                    }
                }
            }
        ) { paddingValues ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(horizontal = 20.dp)
            ) {
                AnimatedContent(
                    targetState = currentStep,
                    label = "RecFlowTransition",
                    modifier = Modifier.padding(top = 16.dp)
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
    // 1. Removed: val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize(), // 2. Removed: .verticalScroll(scrollState)
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // "What is your Soil Type?" Premium Header Card
        Surface(
            shape = RoundedCornerShape(24.dp),
            color = Color(0xFFF7F5EC),
            shadowElevation = 2.dp,
            modifier = Modifier
                .fillMaxWidth()
                .height(160.dp)
        ) {
            Box(modifier = Modifier.fillMaxSize()) {
                // Background Right Illustration
                Image(
                    painter = painterResource(id = R.drawable.ill_soil_header_right),
                    contentDescription = null,
                    modifier = Modifier
                        .align(Alignment.BottomEnd)
                        .width(130.dp)
                        .fillMaxHeight(),
                    contentScale = ContentScale.Crop
                )

                // Foreground Content
                Row(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 20.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ill_soil_header_left),
                        contentDescription = null,
                        modifier = Modifier.size(76.dp)
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Text(
                            text = "What is your\nSoil Type?",
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.ExtraBold,
                                color = Color(0xFF1B5E20)
                            )
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "This helps us suggest\nthe best crops for\nyour field.",
                            style = MaterialTheme.typography.bodySmall.copy(
                                color = Color.DarkGray,
                                lineHeight = 16.sp
                            )
                        )
                    }
                }
            }
        }

        // Small Prompt Line
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        ) {
            Icon(Icons.Rounded.Eco, null, tint = Color(0xFF4CAF50), modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(8.dp))
            Text("Select the soil type that best matches your field.", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
        }

        // Fading Curved Rectangular Soil Cards
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            soils.forEach { soil ->
                val isSelected = selected == soil
                val scale by animateFloatAsState(if (isSelected) 1.02f else 1f, label = "card_scale")

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(96.dp)
                        .scale(scale)
                        .clickable(
                            interactionSource = remember { MutableInteractionSource() },
                            indication = null,
                            onClick = { onSelect(soil) }
                        )
                ) {
                    // Colored full border when selected, faint border when unselected
                    Surface(
                        shape = RoundedCornerShape(20.dp),
                        color = Color.White,
                        border = if (isSelected) BorderStroke(1.5.dp, soil.displayColor) else BorderStroke(1.dp, Color(0xFFE8E8E8)),
                        shadowElevation = if (isSelected) 4.dp else 1.dp,
                        modifier = Modifier.fillMaxSize()
                    ) {
                        Box(Modifier.fillMaxSize()) {

                            // Fading PNG Base Layer
                            Image(
                                painter = painterResource(id = soil.imageRes),
                                contentDescription = soil.name,
                                contentScale = ContentScale.Crop,
                                modifier = Modifier
                                    .fillMaxHeight()
                                    .width(130.dp)
                                    .clip(WavyRightShape)
                            )

                            // Fading Overlay to blend the curve into the white card
                            Box(modifier = Modifier
                                .fillMaxHeight()
                                .width(130.dp)
                                .background(
                                    Brush.horizontalGradient(
                                        0.45f to Color.Transparent,
                                        1.0f to Color.White
                                    )
                                )
                            )

                            // UI Layer overlaying the image
                            Row(
                                modifier = Modifier.fillMaxSize(),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Spacer(modifier = Modifier.width(105.dp))

                                // Floating Overlapped Icon
                                Box(
                                    modifier = Modifier
                                        .size(36.dp)
                                        .offset(x = (-8).dp) // Tucks the circle into the curve
                                        .background(soil.displayColor, CircleShape)
                                        .border(2.dp, Color.White, CircleShape),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(soil.icon, contentDescription = null, tint = Color.White, modifier = Modifier.size(20.dp))
                                }

                                // Text Section
                                Column(modifier = Modifier.weight(1f).offset(x = (-2).dp)) {
                                    Text(soil.name, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
                                    Surface(color = soil.displayColor, modifier = Modifier.padding(vertical = 4.dp).height(2.dp).width(16.dp)) {}
                                    Text(soil.description, style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray, fontSize = 11.sp, lineHeight = 14.sp))
                                }

                                // Simple Right Arrow
                                Surface(
                                    shape = CircleShape,
                                    color = Color(0xFFF5F5F5),
                                    modifier = Modifier.size(32.dp).padding(end = 12.dp)
                                ) {
                                    Icon(Icons.AutoMirrored.Rounded.KeyboardArrowRight, contentDescription = null, tint = Color.Gray, modifier = Modifier.padding(4.dp))
                                }
                                Spacer(Modifier.width(8.dp))
                            }
                        }
                    }
                }
            }
        }
        // 3. Removed: Spacer(Modifier.height(100.dp))
    }
}

@Composable
fun CropRecommendationReportCheckStep(onChoice: (Boolean) -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // PNG Illustration
        Image(
            painter = painterResource(id = R.drawable.ill_soil_report_card),
            contentDescription = "Soil Health Card",
            modifier = Modifier
                .height(240.dp)
                .padding(bottom = 24.dp),
            contentScale = ContentScale.Fit
        )

        // Title
        Text(
            text = "Do you have a Soil Health Card?",
            style = MaterialTheme.typography.titleLarge.copy(
                fontWeight = FontWeight.ExtraBold,
                color = Color(0xFF1B1B1B)
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Tiny Leaf Divider
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.width(160.dp)
        ) {
            HorizontalDivider(modifier = Modifier.weight(1f), color = Color(0xFFE0E0E0))
            Icon(
                imageVector = Icons.Rounded.Eco,
                contentDescription = null,
                tint = Color(0xFF4CAF50),
                modifier = Modifier
                    .padding(horizontal = 8.dp)
                    .size(16.dp)
            )
            HorizontalDivider(modifier = Modifier.weight(1f), color = Color(0xFFE0E0E0))
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Subtitle
        Text(
            text = "A Soil Health Card helps us understand your\nsoil better and give you accurate crop advice.",
            style = MaterialTheme.typography.bodyMedium.copy(
                color = Color.DarkGray,
                lineHeight = 22.sp
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(40.dp))

        // Narrowed Capsule Buttons
        Column(
            modifier = Modifier.width(280.dp), // Explicitly constrains width for the buttons
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // YES Button (Primary)
            PremiumButton(
                text = "YES, I HAVE REPORT",
                onClick = { onChoice(true) },
                icon = Icons.Rounded.PhotoCamera,
                shape = CircleShape,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF1B5E20), // Dark Green
                    contentColor = Color.White
                )
            )

            // NO Button (Secondary/Outlined)
            OutlinedButton(
                onClick = { onChoice(false) },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp), // Matching PremiumButton fixed height
                shape = CircleShape,
                border = BorderStroke(1.dp, Color(0xFF1B5E20)),
                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = Color(0xFF1B5E20),
                    containerColor = Color.Transparent
                )
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.Rounded.AutoAwesome,
                        contentDescription = null,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "NO, USE AUTO ANALYSIS",
                        style = MaterialTheme.typography.labelLarge.copy(
                            fontWeight = FontWeight.SemiBold
                        )
                    )
                }
            }
        }
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
        Spacer(modifier = Modifier.height(100.dp))
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
        Spacer(Modifier.height(100.dp))
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