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
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
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
    UPLOAD_REPORT,
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
    val budgetUsd: String = "",
    val documentUri: android.net.Uri? = null,
    val documentBytes: ByteArray? = null,
    val documentFilename: String? = null,
    val documentMimeType: String? = null
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
    val isNoSoilSuccess by viewModel.isNoSoilReportSuccess
    val noSoilResult by viewModel.noSoilReportResult

    LaunchedEffect(isSuccess, isNoSoilSuccess) {
        if ((isSuccess || isNoSoilSuccess) && currentStep == RecommendationStep.AUTO_ANALYSIS) {
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
                                    RecommendationStep.UPLOAD_REPORT -> currentStep = RecommendationStep.REPORT_CHECK
                                    RecommendationStep.AUTO_ANALYSIS -> currentStep = if (isAdvancedMode) RecommendationStep.UPLOAD_REPORT else RecommendationStep.REPORT_CHECK
                                    RecommendationStep.RESULT -> {
                                        currentStep = RecommendationStep.SOIL_SELECTION
                                        viewModel.resetState()
                                        viewModel.resetNoSoilReportState()
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

                        val currentLang = LocalAppLanguage.current

                        Text(
                            text = AppLocalizer.localizeCropAdvicePhrase("crop advice", currentLang),
                            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B5E20))
                        )

                        Spacer(Modifier.weight(1f))
                        Spacer(Modifier.width(48.dp)) // Added for visual symmetry against back button
                    }

                    // Frosted Glass Narrow Step Indicator Capsule (4 Steps)
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
                                RecommendationStep.UPLOAD_REPORT -> 3
                                RecommendationStep.AUTO_ANALYSIS, RecommendationStep.RESULT -> 4
                            },
                            totalSteps = 4,
                            modifier = Modifier
                                .width(220.dp)
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
                        RecommendationStep.REPORT_CHECK -> CropRecommendationReportCheckStep { hasReport ->
                            isAdvancedMode = hasReport
                            if (hasReport) {
                                currentStep = RecommendationStep.UPLOAD_REPORT
                            } else {
                                // "NO, USE AUTO ANALYSIS" immediately analyzes using backend Mode B
                                currentStep = RecommendationStep.AUTO_ANALYSIS
                            }
                        }
                        RecommendationStep.UPLOAD_REPORT -> UploadSoilReportStep(
                            selectedSoil = selectedSoil?.name.orEmpty(),
                            formInputs = formInputs,
                            onInputsChange = { formInputs = it },
                            onAnalyze = {
                                currentStep = RecommendationStep.AUTO_ANALYSIS
                            }
                        )
                        RecommendationStep.AUTO_ANALYSIS -> AutoAnalysisStep(formInputs, selectedSoil?.name ?: "Black Soil", viewModel, isAdvancedMode)
                        RecommendationStep.RESULT -> {
                            val activeRecs = if (noSoilResult != null && !noSoilResult!!.recommendations.isNullOrEmpty()) {
                                noSoilResult!!.recommendations!!.map { item ->
                                    CropRecommendationItem(
                                        crop_name = item.crop_name,
                                        confidence_score = item.suitability_score,
                                        expected_yield_tons = 3.5,
                                        market_demand = item.suitability_level,
                                        estimated_profit_usd = 850.0,
                                        growing_duration_months = 4,
                                        water_requirement = item.water_requirement ?: "Medium"
                                    )
                                }
                            } else {
                                recommendations
                            }
                            val activeInsights = noSoilResult?.explanation ?: noSoilResult?.message ?: aiInsights
                            RecommendationResultStep(selectedSoil, activeRecs, activeInsights, {
                                currentStep = RecommendationStep.SOIL_SELECTION
                                viewModel.resetState()
                                viewModel.resetNoSoilReportState()
                                selectedSoil = null
                                formInputs = CropRecommendationFormInputs()
                            }, {
                                val top = activeRecs.maxByOrNull { it.confidence_score }
                                if (top != null) { AgriStoreContext.setForCrop(top.crop_name); navController.navigate(NavRoutes.ProductStore) }
                            })
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SoilSelectionStep(soils: List<SoilTypeInfo>, selected: SoilTypeInfo?, onSelect: (SoilTypeInfo) -> Unit) {
    val currentLang = LocalAppLanguage.current

    Column(
        modifier = Modifier.fillMaxSize(),
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
                            text = AppLocalizer.localizeCropAdvicePhrase("what is your soil type", currentLang),
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.ExtraBold,
                                color = Color(0xFF1B5E20)
                            )
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = AppLocalizer.localizeCropAdvicePhrase("this helps us suggest", currentLang),
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
            Text(
                text = AppLocalizer.localizeCropAdvicePhrase("select soil match", currentLang),
                style = MaterialTheme.typography.bodySmall,
                color = Color.Gray
            )
        }

        // Fading Curved Rectangular Soil Cards
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            soils.forEach { soil ->
                val isSelected = selected == soil
                val scale by animateFloatAsState(if (isSelected) 1.02f else 1f, label = "card_scale")
                val localizedSoilName = AppLocalizer.localizeSoil(soil.name, currentLang)
                val localizedSoilDesc = AppLocalizer.localizeSoilDescription(soil.description, currentLang)

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
                                contentDescription = localizedSoilName,
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
                                    Text(localizedSoilName, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
                                    Surface(color = soil.displayColor, modifier = Modifier.padding(vertical = 4.dp).height(2.dp).width(16.dp)) {}
                                    Text(localizedSoilDesc, style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray, fontSize = 11.sp, lineHeight = 14.sp))
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
    }
}

@Composable
fun CropRecommendationReportCheckStep(onChoice: (Boolean) -> Unit) {
    val currentLang = LocalAppLanguage.current
    val strings = LocalStrings.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 24.dp)
            .offset(y = (-28).dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // PNG Illustration (enlarged and positioned higher)
        Image(
            painter = painterResource(id = R.drawable.ill_soil_report_card),
            contentDescription = "Soil Health Card",
            modifier = Modifier
                .height(265.dp)
                .padding(bottom = 12.dp),
            contentScale = ContentScale.Fit
        )

        // Title
        Text(
            text = strings.cropAdvice.hasSoilReport,
            style = MaterialTheme.typography.titleLarge.copy(
                fontWeight = FontWeight.ExtraBold,
                color = Color(0xFF1B1B1B)
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(10.dp))

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

        Spacer(modifier = Modifier.height(10.dp))

        // Subtitle
        Text(
            text = AppLocalizer.localizeCropAdvicePhrase("soil report subtitle", currentLang),
            style = MaterialTheme.typography.bodyMedium.copy(
                color = Color.DarkGray,
                lineHeight = 20.sp
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Narrowed Capsule Buttons
        Column(
            modifier = Modifier.width(280.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // YES Button (Primary)
            PremiumButton(
                text = strings.cropAdvice.yesHaveReport,
                onClick = { onChoice(true) },
                icon = Icons.Rounded.PhotoCamera,
                shape = CircleShape,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF1B5E20),
                    contentColor = Color.White
                )
            )

            // NO Button (Secondary/Outlined)
            OutlinedButton(
                onClick = { onChoice(false) },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(54.dp),
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
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        text = strings.cropAdvice.noUseAutoAnalysis,
                        style = MaterialTheme.typography.labelLarge.copy(
                            fontWeight = FontWeight.SemiBold
                        )
                    )
                }
            }
        }
    }
}

// ============================================
// UPLOAD SOIL REPORT STEP (MATCHING DESIGN)
// ============================================
@Composable
fun UploadSoilReportStep(
    selectedSoil: String,
    formInputs: CropRecommendationFormInputs,
    onInputsChange: (CropRecommendationFormInputs) -> Unit,
    onAnalyze: () -> Unit
) {
    val context = LocalContext.current
    val currentLang = LocalAppLanguage.current
    val scrollState = rememberScrollState()

    var locationDisplay by remember { mutableStateOf(formInputs.location.ifBlank { LocationSnapshotStore.latestCity ?: "Detecting..." }) }
    var rainfallDisplay by remember { mutableStateOf(formInputs.rainfallMm.ifBlank { "" }) }
    var tempDisplay by remember {
        mutableStateOf(
            formInputs.temperatureC.ifBlank {
                WeatherSnapshotStore.latestWeather?.let { "${it.temperature}.0" } ?: ""
            }
        )
    }

    var documentName by remember { mutableStateOf(formInputs.documentFilename) }
    var documentBytes by remember { mutableStateOf(formInputs.documentBytes) }
    var documentMime by remember { mutableStateOf(formInputs.documentMimeType) }

    val hasValidDocument = documentBytes != null && documentBytes!!.isNotEmpty() && documentName != null && (
        documentName!!.endsWith(".pdf", ignoreCase = true) ||
        documentName!!.endsWith(".jpg", ignoreCase = true) ||
        documentName!!.endsWith(".jpeg", ignoreCase = true) ||
        documentName!!.endsWith(".png", ignoreCase = true) ||
        (documentMime != null && (
            documentMime!!.contains("pdf", ignoreCase = true) ||
            documentMime!!.contains("jpeg", ignoreCase = true) ||
            documentMime!!.contains("jpg", ignoreCase = true) ||
            documentMime!!.contains("png", ignoreCase = true)
        ))
    )

    // File picker launcher for images and PDFs
    val filePickerLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.activity.result.contract.ActivityResultContracts.OpenDocument()
    ) { uri: android.net.Uri? ->
        if (uri != null) {
            try {
                val contentResolver = context.contentResolver
                val mime = contentResolver.getType(uri) ?: "application/pdf"
                var name = "Soil_Health_Card.pdf"
                contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                    if (cursor.moveToFirst()) {
                        val nameIndex = cursor.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                        if (nameIndex != -1) {
                            cursor.getString(nameIndex)?.let { name = it }
                        }
                    }
                }
                val bytes = contentResolver.openInputStream(uri)?.use { it.readBytes() }
                if (bytes != null) {
                    documentName = name
                    documentBytes = bytes
                    documentMime = mime
                    onInputsChange(
                        formInputs.copy(
                            documentUri = uri,
                            documentBytes = bytes,
                            documentFilename = name,
                            documentMimeType = mime
                        )
                    )
                }
            } catch (e: Exception) {
                // handle error gracefully
            }
        }
    }

    // Auto-fetch location & weather on load
    LaunchedEffect(Unit) {
        val location = getDeviceLocation(context)
        val lat = location?.first ?: LocationSnapshotStore.latestLatitude ?: 26.9124
        val lon = location?.second ?: LocationSnapshotStore.latestLongitude ?: 75.7873
        val appLang = LanguagePreferences.getSelectedLanguage(context) ?: "en"

        val city = getCityFromLocation(context, lat, lon, appLang)
        if (!city.isNullOrBlank()) {
            locationDisplay = city
            LocationSnapshotStore.latestCity = city
        } else if (!LocationSnapshotStore.latestCity.isNullOrBlank()) {
            locationDisplay = LocationSnapshotStore.latestCity!!
        } else {
            locationDisplay = "Jaipur, Rajasthan"
        }

        // Live weather query
        val weatherRes = runCatching { RetrofitInstance.farmFusionApi.getCurrentWeather(lat, lon) }.getOrNull()
        val weatherData = weatherRes?.body()?.data
        if (weatherData != null) {
            tempDisplay = String.format(java.util.Locale.US, "%.1f", weatherData.temperature_c)
        } else if (WeatherSnapshotStore.latestWeather != null) {
            tempDisplay = "${WeatherSnapshotStore.latestWeather!!.temperature}.0"
        } else {
            tempDisplay = "27.4"
        }

        // Fetch real ERA-5 historical annual rainfall from backend
        val rainfallRes = runCatching { RetrofitInstance.farmFusionApi.getAnnualRainfall(lat, lon) }.getOrNull()
        val rainVal = rainfallRes?.body()?.data?.let { it.annual_rainfall_mm ?: it.total_rainfall_mm }
        if (rainVal != null && rainVal > 0) {
            rainfallDisplay = String.format(java.util.Locale.US, "%.0f", rainVal)
        } else {
            val estRainfall = when {
                lat in 24.0..30.5 && lon in 70.0..78.5 -> 612.0  // NW / Rajasthan
                lat in 8.0..18.0 && lon in 74.0..78.0 -> 950.0   // South
                lat in 20.0..28.0 && lon in 80.0..89.0 -> 1150.0 // East / Gangetic
                else -> 750.0
            }
            rainfallDisplay = estRainfall.toInt().toString()
        }

        onInputsChange(
            formInputs.copy(
                location = locationDisplay,
                rainfallMm = rainfallDisplay,
                temperatureC = tempDisplay,
                farmSizeAcres = formInputs.farmSizeAcres.ifBlank { "1.0" }
            )
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(bottom = 16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        // Title & Description Header
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(
                text = "Upload Your Soil Health Card",
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.ExtraBold,
                    color = Color(0xFF1B1B1B),
                    fontSize = 21.sp
                )
            )
            Text(
                text = "Upload your soil report to get crop recommendations based on your soil condition.",
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = Color.Gray,
                    lineHeight = 18.sp,
                    fontSize = 13.sp
                )
            )
        }

        // ========================================
        // DASHED UPLOAD CARD
        // ========================================
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .drawBehind {
                    val stroke = Stroke(
                        width = 1.5.dp.toPx(),
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(14f, 10f), 0f)
                    )
                    drawRoundRect(
                        color = Color(0xFF81C784),
                        cornerRadius = CornerRadius(20.dp.toPx(), 20.dp.toPx()),
                        style = stroke
                    )
                }
                .clip(RoundedCornerShape(20.dp))
                .background(Color(0xFFFAFCF9))
                .padding(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Soil Card Illustration (Enlarged for better prominence)
                Image(
                    painter = painterResource(id = R.drawable.ill_soil_report_card),
                    contentDescription = "Soil Report Illustration",
                    modifier = Modifier
                        .size(116.dp)
                        .padding(end = 10.dp),
                    contentScale = ContentScale.Fit
                )

                // Right Content Info & Upload Action
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = "Upload Soil Report",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1B1B1B),
                            fontSize = 15.sp
                        )
                    )
                    Text(
                        text = "JPG, JPEG, PNG or PDF",
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = Color.Gray,
                            fontSize = 12.sp
                        )
                    )
                    Text(
                        text = "Maximum file size: 10 MB",
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = Color.Gray,
                            fontSize = 11.5.sp
                        )
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    if (documentName == null) {
                        // Upload Document Button
                        OutlinedButton(
                            onClick = {
                                filePickerLauncher.launch(
                                    arrayOf(
                                        "image/jpeg",
                                        "image/png",
                                        "image/jpg",
                                        "application/pdf",
                                        "image/*"
                                    )
                                )
                            },
                            shape = RoundedCornerShape(20.dp),
                            border = BorderStroke(1.dp, Color(0xFF1B5E20)),
                            colors = ButtonDefaults.outlinedButtonColors(
                                containerColor = Color.Transparent,
                                contentColor = Color(0xFF1B5E20)
                            ),
                            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp),
                            modifier = Modifier.height(36.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Rounded.FileUpload,
                                contentDescription = null,
                                modifier = Modifier.size(18.dp),
                                tint = Color(0xFF1B5E20)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "UPLOAD DOCUMENT",
                                style = MaterialTheme.typography.labelMedium.copy(
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 11.sp,
                                    letterSpacing = 0.5.sp
                                )
                            )
                        }
                    } else {
                        // Picked State Badge + Change Button
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier
                                .clip(RoundedCornerShape(12.dp))
                                .background(Color(0xFFE8F5E9))
                                .clickable {
                                    filePickerLauncher.launch(
                                        arrayOf(
                                            "image/jpeg",
                                            "image/png",
                                            "image/jpg",
                                            "application/pdf",
                                            "image/*"
                                        )
                                    )
                                }
                                .padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Rounded.CheckCircle,
                                contentDescription = null,
                                tint = Color(0xFF2E7D32),
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = documentName ?: "File Selected",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF1B5E20),
                                    fontSize = 11.sp
                                ),
                                maxLines = 1
                            )
                        }
                    }
                }
            }
        }

        // Helper Note under card
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(horizontal = 4.dp)
        ) {
            Icon(
                imageVector = Icons.Rounded.Description,
                contentDescription = null,
                tint = Color(0xFF4CAF50),
                modifier = Modifier.size(15.dp)
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = "You can upload a photo of your Soil Health Card or a PDF report.",
                style = MaterialTheme.typography.bodySmall.copy(
                    color = Color(0xFF616161),
                    fontSize = 11.5.sp
                )
            )
        }

        // ========================================
        // 3 AUTO-FETCHED CARDS ROW
        // ========================================
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(
                text = "Auto-fetched Details",
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1B1B1B),
                    fontSize = 15.sp
                )
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                // Card 1: Village / District
                AutoFetchedItemCard(
                    icon = Icons.Rounded.LocationOn,
                    label = "Village / District",
                    value = locationDisplay.ifBlank { "Detecting..." },
                    modifier = Modifier.weight(1f)
                )

                // Card 2: Annual Rainfall
                AutoFetchedItemCard(
                    icon = Icons.Rounded.WaterDrop,
                    label = "Annual Rainfall",
                    value = if (rainfallDisplay.isNotBlank()) "$rainfallDisplay mm" else "Calculating...",
                    modifier = Modifier.weight(1f)
                )

                // Card 3: Avg. Temperature
                AutoFetchedItemCard(
                    icon = Icons.Rounded.Thermostat,
                    label = "Avg. Temperature",
                    value = if (tempDisplay.isNotBlank()) "$tempDisplay °C" else "Fetching...",
                    modifier = Modifier.weight(1f)
                )
            }
        }

        Spacer(modifier = Modifier.height(4.dp))

        // Document upload requirement message if document not picked yet
        if (!hasValidDocument) {
            Text(
                text = "Please upload your Soil Health Card (PDF, JPG, or PNG) to continue.",
                style = MaterialTheme.typography.bodySmall.copy(
                    color = Color(0xFFE65100),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium
                ),
                modifier = Modifier.padding(horizontal = 4.dp)
            )
        }

        // ========================================
        // ANALYZE & GET CROP ADVICE BUTTON
        // ========================================
        Button(
            onClick = {
                if (hasValidDocument) {
                    onInputsChange(
                        formInputs.copy(
                            location = locationDisplay,
                            rainfallMm = rainfallDisplay,
                            temperatureC = tempDisplay,
                            farmSizeAcres = formInputs.farmSizeAcres.ifBlank { "1.0" },
                            documentBytes = documentBytes,
                            documentFilename = documentName,
                            documentMimeType = documentMime
                        )
                    )
                    onAnalyze()
                }
            },
            enabled = hasValidDocument,
            shape = RoundedCornerShape(28.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF1B5E20),
                contentColor = Color.White,
                disabledContainerColor = Color(0xFFA5D6A7),
                disabledContentColor = Color.White.copy(alpha = 0.8f)
            ),
            modifier = Modifier
                .fillMaxWidth()
                .height(54.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Text(
                    text = "ANALYZE & GET CROP ADVICE",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = Color.White,
                        fontSize = 15.sp,
                        letterSpacing = 0.5.sp
                    )
                )
                Spacer(modifier = Modifier.width(8.dp))
                Icon(
                    imageVector = Icons.AutoMirrored.Rounded.ArrowForward,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(20.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(40.dp))
    }
}

@Composable
fun AutoFetchedItemCard(
    icon: ImageVector,
    label: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFEBEBEB)),
        shadowElevation = 0.5.dp,
        modifier = modifier.height(130.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(vertical = 10.dp, horizontal = 6.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Icon in Light-Green Circle
            Surface(
                shape = CircleShape,
                color = Color(0xFFE8F5E9),
                modifier = Modifier.size(34.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = Color(0xFF2E7D32),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }

            // Title & Value
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(2.dp)
            ) {
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelSmall.copy(
                        color = Color(0xFF757575),
                        fontWeight = FontWeight.Medium,
                        fontSize = 10.sp
                    ),
                    textAlign = TextAlign.Center,
                    maxLines = 1
                )
                Text(
                    text = value,
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = Color(0xFF1B1B1B),
                        fontWeight = FontWeight.Bold,
                        fontSize = 11.5.sp
                    ),
                    textAlign = TextAlign.Center,
                    maxLines = 2
                )
            }

            // "AUTO" Badge Pill
            Surface(
                shape = RoundedCornerShape(6.dp),
                color = Color(0xFFE8F5E9)
            ) {
                Text(
                    text = "AUTO",
                    style = MaterialTheme.typography.labelSmall.copy(
                        color = Color(0xFF2E7D32),
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 9.sp,
                        letterSpacing = 0.5.sp
                    ),
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                )
            }
        }
    }
}

@Composable
fun AutoAnalysisStep(
    formInputs: CropRecommendationFormInputs,
    soilType: String,
    viewModel: CropRecommendationViewModel,
    isAdvancedMode: Boolean
) {
    val context = LocalContext.current
    val currentLang = LocalAppLanguage.current
    val isLoading by viewModel.isLoading
    val isNoSoilLoading by viewModel.isNoSoilReportLoading
    val error by viewModel.error
    val noSoilError by viewModel.noSoilReportError

    LaunchedEffect(Unit) {
        val lang = LocaleHelper.apiLanguageCode(LanguagePreferences.getSelectedLanguage(context) ?: "en")
        val location = getDeviceLocation(context)
        val lat = location?.first
        val lon = location?.second
        val city = if (lat != null && lon != null) getCityFromLocation(context, lat, lon, lang) else null
        val resolvedLocation = formInputs.location.ifBlank { city ?: LocationSnapshotStore.latestCity ?: "India" }

        if (!isAdvancedMode) {
            // Mode B: "No Soil Report / Auto Analysis" flow
            viewModel.fetchNoSoilReportRecommendations(
                latitude = lat ?: 20.5937,
                longitude = lon ?: 78.9629,
                state = null,
                soilType = soilType,
                locationName = resolvedLocation
            )
        } else {
            // Mode A: "I Have a Soil Report" flow
            val docBytes = formInputs.documentBytes
            if (docBytes != null && docBytes.isNotEmpty()) {
                viewModel.fetchRecommendationsFromDocument(
                    documentBytes = docBytes,
                    filename = formInputs.documentFilename ?: "soil_report.pdf",
                    mimeType = formInputs.documentMimeType ?: "application/pdf",
                    farmSizeAcres = formInputs.farmSizeAcres.toDoubleOrNull() ?: 1.0,
                    location = resolvedLocation,
                    latitude = lat,
                    longitude = lon,
                    soilType = soilType,
                    rainfallMm = formInputs.rainfallMm.toDoubleOrNull() ?: 612.0,
                    temperatureC = formInputs.temperatureC.toDoubleOrNull() ?: 27.4,
                    preferredLanguage = lang
                )
            } else {
                viewModel.fetchRecommendations(
                    location = resolvedLocation,
                    soilType = soilType,
                    rainfallMm = formInputs.rainfallMm.toDoubleOrNull() ?: 612.0,
                    temperatureC = formInputs.temperatureC.toDoubleOrNull() ?: 27.4,
                    farmSizeAcres = formInputs.farmSizeAcres.toDoubleOrNull() ?: 1.0,
                    latitude = lat,
                    longitude = lon,
                    preferredLanguage = lang
                )
            }
        }
    }

    val activeError = error ?: noSoilError

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        if (activeError != null) {
            Icon(Icons.Rounded.ErrorOutline, null, tint = MaterialTheme.colorScheme.error, modifier = Modifier.size(56.dp))
            Spacer(Modifier.height(16.dp))
            Text(activeError!!, color = MaterialTheme.colorScheme.error, textAlign = TextAlign.Center)
        } else {
            CircularProgressIndicator(modifier = Modifier.size(64.dp), color = Color(0xFF1B5E20))
            Spacer(Modifier.height(24.dp))
            Text(
                text = AppLocalizer.localizeCropAdvicePhrase("ai analyzing", currentLang),
                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B5E20)),
                textAlign = TextAlign.Center
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = AppLocalizer.localizeCropAdvicePhrase("fetching weather characteristics", currentLang),
                style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray),
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
fun RecommendationResultStep(soil: SoilTypeInfo?, recommendations: List<CropRecommendationItem>, aiInsights: String, onReset: () -> Unit, onOpenAgriStore: () -> Unit) {
    val scrollState = rememberScrollState()
    val currentLang = LocalAppLanguage.current

    Column(modifier = Modifier.fillMaxSize().verticalScroll(scrollState), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Surface(modifier = Modifier.fillMaxWidth().shadow(4.dp, RoundedCornerShape(24.dp)), shape = RoundedCornerShape(24.dp), color = Color.White) {
            Column(modifier = Modifier.padding(20.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.AutoAwesome, null, tint = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.width(12.dp))
                    Text(
                        text = AppLocalizer.localizeCropAdvicePhrase("ai best recommendations", currentLang),
                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)
                    )
                }
                Text(
                    text = AppLocalizer.localizeCropAdvicePhrase("based on your soil", currentLang),
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray
                )
            }
        }
        if (aiInsights.isNotEmpty()) GlassPanel { Row { Text("💡", fontSize = 24.sp); Spacer(Modifier.width(12.dp)); Text(aiInsights, style = MaterialTheme.typography.bodyLarge) } }
        recommendations.forEach { CropResultCard(it) }
        PremiumButton(
            text = AppLocalizer.localizeCropAdvicePhrase("shop seeds", currentLang),
            onClick = onOpenAgriStore,
            icon = Icons.Rounded.ShoppingBag
        )
        PremiumOutlinedButton(
            text = AppLocalizer.localizeCropAdvicePhrase("start over", currentLang),
            onClick = onReset,
            icon = Icons.Rounded.Refresh
        )
        Spacer(Modifier.height(100.dp))
    }
}

@Composable
fun CropResultCard(crop: CropRecommendationItem) {
    val currentLang = LocalAppLanguage.current
    val localizedCropName = AppLocalizer.localizeCrop(crop.crop_name, currentLang)

    Surface(modifier = Modifier.fillMaxWidth().shadow(4.dp, RoundedCornerShape(24.dp)), shape = RoundedCornerShape(24.dp), color = Color.White, border = BorderStroke(1.dp, Color(0xFFF0F0F0))) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Column {
                    Text(localizedCropName, style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)))
                    Surface(color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), shape = RoundedCornerShape(8.dp)) {
                        Text(
                            text = "${AppLocalizer.localizeCropAdvicePhrase("match", currentLang)}: ${(crop.confidence_score * 100).toInt()}%",
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                        )
                    }
                }
                Surface(color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), shape = CircleShape, modifier = Modifier.size(52.dp)) {
                    Box(contentAlignment = Alignment.Center) { Icon(Icons.Rounded.Agriculture, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(28.dp)) }
                }
            }
            HorizontalDivider(modifier = Modifier.padding(vertical = 16.dp), thickness = 0.5.dp, color = Color(0xFFF5F5F5))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                ResultDetailItem(
                    icon = Icons.Rounded.TrendingUp,
                    label = AppLocalizer.localizeCropAdvicePhrase("profit", currentLang),
                    value = AppLocalizer.localizeSeverity("High", currentLang),
                    modifier = Modifier.weight(1f)
                )
                Box(modifier = Modifier.height(32.dp).width(1.dp).background(Color(0xFFF0F0F0)))
                ResultDetailItem(
                    icon = Icons.Rounded.Schedule,
                    label = AppLocalizer.localizeCropAdvicePhrase("duration", currentLang),
                    value = AppLocalizer.localizeDuration(crop.growing_duration_months, currentLang),
                    modifier = Modifier.weight(1f)
                )
                Box(modifier = Modifier.height(32.dp).width(1.dp).background(Color(0xFFF0F0F0)))
                ResultDetailItem(
                    icon = Icons.Rounded.WaterDrop,
                    label = AppLocalizer.localizeCropAdvicePhrase("water", currentLang),
                    value = AppLocalizer.localizeSeverity(crop.water_requirement, currentLang),
                    modifier = Modifier.weight(1f)
                )
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