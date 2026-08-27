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
import com.example.farmfusionapp.data.model.EnvironmentalCropRecommendation
import com.example.farmfusionapp.data.model.NoSoilReportResponse
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.ui.components.*
import com.example.farmfusionapp.utils.*
import com.example.farmfusionapp.viewmodel.CropRecommendationViewModel
import com.example.farmfusionapp.ui.screens.SoilReportVerificationStep
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import android.content.Intent
import android.net.Uri
import android.provider.MediaStore
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.result.PickVisualMediaRequest
import android.graphics.Bitmap
import androidx.compose.ui.graphics.asImageBitmap
import android.provider.MediaStore.Images.Media
import com.example.farmfusionapp.ml.SoilReportTextRecognizer
import com.example.farmfusionapp.data.soilreport.SoilReportOcrParser
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import com.example.farmfusionapp.data.soilreport.SoilReportOcrParser.ParsedSoilValues

// ============================================
// STEP DEFINITIONS
// ============================================
enum class RecommendationStep {
    SOIL_SELECTION,
    REPORT_CHECK,
    FARM_DETAILS,
    REPORT_PHOTO_INPUT,
    SOIL_REPORT_VERIFICATION,
    AUTO_ANALYSIS,
    RESULT,
    NO_SOIL_REPORT_LOADING,
    NO_SOIL_REPORT_RESULT
}

/**
 * Sub-phases of the No-Soil-Report loading flow.
 *
 * The NoSoilReportLoadingStep Composable drives this state machine:
 * permission → location → API call → (success/error).
 */
enum class NoSoilReportPhase {
    PERMISSION_CHECK,
    FETCHING_LOCATION,
    API_LOADING,
    PERMISSION_DENIED,
    LOCATION_UNAVAILABLE
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
    var noSoilReportPhase by remember { mutableStateOf(NoSoilReportPhase.PERMISSION_CHECK) }

    val isLoading by viewModel.isLoading
    val error by viewModel.error
    val recommendations by viewModel.recommendations
    val aiInsights by viewModel.aiInsights
    val isSuccess by viewModel.isSuccess

    val noSoilReportResult by viewModel.noSoilReportResult
    val isNoSoilReportLoading by viewModel.isNoSoilReportLoading
    val noSoilReportError by viewModel.noSoilReportError
    val isNoSoilReportSuccess by viewModel.isNoSoilReportSuccess

    LaunchedEffect(isSuccess) {
        if (isSuccess && currentStep == RecommendationStep.AUTO_ANALYSIS) {
            delay(500)
            currentStep = RecommendationStep.RESULT
        }
    }

    LaunchedEffect(isNoSoilReportSuccess) {
        if (isNoSoilReportSuccess && currentStep == RecommendationStep.NO_SOIL_REPORT_LOADING) {
            currentStep = RecommendationStep.NO_SOIL_REPORT_RESULT
        }
    }

    val soilTypes = remember {
        listOf(
            SoilTypeInfo("Sandy Soil", "बलुई मिट्टी", "Sand", "बलुई", Color(0xFFD4E157), Icons.Rounded.Waves, "Well-draining coarse texture, suitable for Bajra, Mustard & Groundnut"),
            SoilTypeInfo("Black Soil", "काली मिट्टी", "Black", "काली", Color(0xFF3E2723), Icons.Rounded.Grass, "Rich in clay, retains moisture, ideal for Cotton, Soybean & Wheat"),
            SoilTypeInfo("Red Soil", "लाल मिट्टी", "Red", "लाल", Color(0xFFD32F2F), Icons.Rounded.Terrain, "Porous, rich in iron, good for Pulses, Maize & Groundnut"),
            SoilTypeInfo("Alluvial Soil", "जलोढ़ मिट्टी", "Alluvial", "जलोढ़", Color(0xFF8D6E63), Icons.Rounded.Landscape, "Highly fertile, rich in loam/silt, ideal for Wheat, Rice & Sugarcane")
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
                            RecommendationStep.SOIL_REPORT_VERIFICATION -> currentStep = RecommendationStep.REPORT_PHOTO_INPUT
                            RecommendationStep.AUTO_ANALYSIS -> currentStep = RecommendationStep.FARM_DETAILS
                            RecommendationStep.RESULT -> {
                                currentStep = RecommendationStep.SOIL_SELECTION
                                viewModel.resetState()
                                selectedSoil = null
                                formInputs = CropRecommendationFormInputs()
                            }
                            RecommendationStep.NO_SOIL_REPORT_LOADING,
                            RecommendationStep.NO_SOIL_REPORT_RESULT -> {
                                currentStep = RecommendationStep.REPORT_CHECK
                                viewModel.resetNoSoilReportState()
                                noSoilReportPhase = NoSoilReportPhase.PERMISSION_CHECK
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
                        RecommendationStep.REPORT_PHOTO_INPUT, RecommendationStep.SOIL_REPORT_VERIFICATION -> 4
                        RecommendationStep.AUTO_ANALYSIS -> 5
                        RecommendationStep.RESULT,
                        RecommendationStep.NO_SOIL_REPORT_LOADING,
                        RecommendationStep.NO_SOIL_REPORT_RESULT -> 6
                    },
                    totalSteps = 6,
                    modifier = Modifier.padding(bottom = 24.dp)
                )

                AnimatedContent(
                    targetState = currentStep,
                    label = "RecFlowTransition",
                    modifier = Modifier.padding(top = 40.dp)
                ) { step ->
                    when (step) {
                        RecommendationStep.SOIL_SELECTION -> SoilSelectionStep(soilTypes, selectedSoil) { selectedSoil = it; currentStep = RecommendationStep.REPORT_CHECK }
                        RecommendationStep.REPORT_CHECK -> CropRecommendationReportCheckStep(
                            onChoice = { isAdvancedMode = it; currentStep = RecommendationStep.FARM_DETAILS },
                            onNoSoilReport = {
                                noSoilReportPhase = NoSoilReportPhase.PERMISSION_CHECK
                                viewModel.resetNoSoilReportState()
                                currentStep = RecommendationStep.NO_SOIL_REPORT_LOADING
                            }
                        )
                        RecommendationStep.FARM_DETAILS -> FarmDetailsStep(selectedSoil?.name.orEmpty(), formInputs, { formInputs = it }) { currentStep = if (isAdvancedMode) RecommendationStep.REPORT_PHOTO_INPUT else RecommendationStep.AUTO_ANALYSIS }
                        RecommendationStep.REPORT_PHOTO_INPUT -> PhotoInputStep(onComplete = { currentStep = RecommendationStep.SOIL_REPORT_VERIFICATION })
                        RecommendationStep.SOIL_REPORT_VERIFICATION -> SoilReportVerificationStep(
                            onConfirm = { soilValues ->
                                viewModel.setConfirmedSoilValues(soilValues)
                                currentStep = RecommendationStep.AUTO_ANALYSIS
                            },
                            onScanAgain = {
                                // Reset OCR state and go back to photo input
                                viewModel.resetOcrState()
                                currentStep = RecommendationStep.REPORT_PHOTO_INPUT
                            },
                            onCancel = {
                                currentStep = RecommendationStep.REPORT_PHOTO_INPUT
                            },
                            viewModel = viewModel
                        )
                        RecommendationStep.AUTO_ANALYSIS -> AutoAnalysisStep(formInputs, selectedSoil?.name ?: "", viewModel)
                        RecommendationStep.NO_SOIL_REPORT_LOADING -> NoSoilReportLoadingStep(
                            viewModel = viewModel,
                            selectedSoil = selectedSoil,
                            phase = noSoilReportPhase,
                            onPhaseChange = { noSoilReportPhase = it },
                            isLoading = isNoSoilReportLoading,
                            apiError = noSoilReportError,
                            onBack = { currentStep = RecommendationStep.REPORT_CHECK },
                            onReset = {
                                viewModel.resetNoSoilReportState()
                                noSoilReportPhase = NoSoilReportPhase.PERMISSION_CHECK
                            }
                        )
                        RecommendationStep.NO_SOIL_REPORT_RESULT -> NoSoilReportResultStep(
                            result = noSoilReportResult,
                            selectedSoil = selectedSoil,
                            onUploadSoilReport = {
                                isAdvancedMode = true
                                currentStep = RecommendationStep.REPORT_PHOTO_INPUT
                            },
                            onReset = {
                                currentStep = RecommendationStep.SOIL_SELECTION
                                viewModel.resetNoSoilReportState()
                                viewModel.resetState()
                                selectedSoil = null
                                formInputs = CropRecommendationFormInputs()
                                noSoilReportPhase = NoSoilReportPhase.PERMISSION_CHECK
                            }
                        )
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
fun CropRecommendationReportCheckStep(
    onChoice: (Boolean) -> Unit,
    onNoSoilReport: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
        Surface(modifier = Modifier.size(140.dp).shadow(8.dp, CircleShape), shape = CircleShape, color = Color.White, border = BorderStroke(1.dp, Color(0xFFF0F0F0))) {
            Box(contentAlignment = Alignment.Center) { Icon(Icons.Rounded.Description, null, modifier = Modifier.size(64.dp), tint = MaterialTheme.colorScheme.primary) }
        }
        Spacer(modifier = Modifier.height(32.dp))
        Text(stringResource(R.string.has_soil_health_card), style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B)), textAlign = TextAlign.Center)
        Text("क्या आपके पास मिट्टी स्वास्थ्य कार्ड है?", style = MaterialTheme.typography.bodyMedium.copy(color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold), textAlign = TextAlign.Center)
        Spacer(modifier = Modifier.height(48.dp))
        PremiumOutlinedButton(text = "I Have Soil Report", onClick = { onChoice(true) })
        Spacer(modifier = Modifier.height(16.dp))
        PremiumOutlinedButton(text = "I Don't Have Soil Report", onClick = { onNoSoilReport() })
    }
}

@Composable
fun FarmDetailsStep(selectedSoil: String, inputs: CropRecommendationFormInputs, onInputsChange: (CropRecommendationFormInputs) -> Unit, onContinue: () -> Unit) {
    val scrollState = rememberScrollState()
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val canContinue = inputs.location.isNotBlank() && inputs.farmSizeAcres.isNotBlank()

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

    // Auto-detect Village / District from GPS when the screen opens (no manual entry).
    LaunchedEffect(Unit) {
        if (inputs.location.isBlank()) autoFillFromLocation()
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
        // Farm Location — auto-detected from GPS, not manually typed.
        Surface(modifier = Modifier.fillMaxWidth().shadow(2.dp, RoundedCornerShape(16.dp)), shape = RoundedCornerShape(16.dp), color = Color(0xFFF9F9F9)) {
            Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.LocationOn, null, tint = MaterialTheme.colorScheme.primary)
                Spacer(Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text("Farm Location", style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.Bold))
                    Text(
                        text = if (inputs.location.isNotBlank()) "Automatically detected: ${inputs.location}" else "Detecting location...",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.Gray
                    )
                }
                AssistChip(
                    onClick = { autoFillFromLocation() },
                    label = { Text(stringResource(R.string.refresh_autofill)) },
                    leadingIcon = { Icon(Icons.Rounded.MyLocation, null, modifier = Modifier.size(18.dp)) }
                )
            }
        }
        PremiumTextField(inputs.farmSizeAcres, { onInputsChange(inputs.copy(farmSizeAcres = it)) }, label = stringResource(R.string.farm_size_label), leadingIcon = Icons.Rounded.SquareFoot)
        Spacer(modifier = Modifier.height(16.dp))
        PremiumButton(stringResource(R.string.continue_button), onContinue, icon = Icons.AutoMirrored.Rounded.ArrowForward, enabled = canContinue)
    }
}

@Composable
fun PhotoInputStep(
    onComplete: (ParsedSoilValues) -> Unit,
    onCancel: () -> Unit = {},
    viewModel: CropRecommendationViewModel = viewModel()
) {
    val context = LocalContext.current
    val scope = androidx.compose.runtime.rememberCoroutineScope()
    val ocrRecognizer = remember { SoilReportTextRecognizer.getInstance(context.applicationContext) }

    // State for UI
    var isProcessing by remember { mutableStateOf(false) }
    var ocrError by remember { mutableStateOf<String?>(null) }
    var previewBitmap by remember { mutableStateOf<Bitmap?>(null) }
    var parsedValues by remember { mutableStateOf<ParsedSoilValues?>(null) }
    var showImageSourceDialog by remember { mutableStateOf(false) }

    // Camera photo URI (used by the TakePicture contract)
    var photoUri by remember { mutableStateOf<Uri?>(null) }

    fun processImage(uri: Uri) {
        isProcessing = true
        ocrError = null
        parsedValues = null
        scope.launch {
            try {
                val (bitmap, parsed) = kotlinx.coroutines.withContext(Dispatchers.IO) {
                    val bmp = Media.getBitmap(context.contentResolver, uri)
                    val text = ocrRecognizer.recognizeText(bmp)
                    bmp to SoilReportOcrParser.parse(text)
                }
                previewBitmap = bitmap
                parsedValues = parsed
                // Store parsed values in ViewModel for the verification step
                viewModel.setOcrParsedValues(parsed)
            } catch (e: Exception) {
                ocrError = e.message ?: "Failed to process image"
            } finally {
                isProcessing = false
            }
        }
    }

    // Image picker launcher (photo gallery)
    val pickImageLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.PickVisualMedia(),
        onResult = { uri -> uri?.let { processImage(it) } }
    )

    // Camera launcher (TakePicture writes to photoUri)
    val takePhotoLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture(),
        onResult = { success -> if (success) photoUri?.let { processImage(it) } }
    )

    fun launchCamera() {
        val uri = context.contentResolver.insert(
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
            android.content.ContentValues().apply {
                put(MediaStore.Images.Media.DISPLAY_NAME, "soil_report_${System.currentTimeMillis()}.jpg")
                put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
            }
        )
        if (uri != null) {
            photoUri = uri
            takePhotoLauncher.launch(uri)
        }
    }

    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        if (showImageSourceDialog) {
            // Image source selection dialog
            Surface(
                modifier = Modifier.fillMaxWidth().shadow(8.dp, RoundedCornerShape(24.dp)),
                shape = RoundedCornerShape(24.dp),
                color = Color.White
            ) {
                Column(modifier = Modifier.padding(24.dp)) {
                    Text(
                        stringResource(R.string.select_image_source),
                        style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold),
                        textAlign = TextAlign.Center
                    )
                    Spacer(Modifier.height(24.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        OutlinedButton(
                            onClick = {
                                showImageSourceDialog = false
                                pickImageLauncher.launch(
                                    PickVisualMediaRequest(
                                        ActivityResultContracts.PickVisualMedia.ImageOnly
                                    )
                                )
                            },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(16.dp)
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Icon(Icons.Rounded.PhotoLibrary, contentDescription = null, modifier = Modifier.size(32.dp), tint = MaterialTheme.colorScheme.primary)
                                Text(stringResource(R.string.choose_from_gallery))
                            }
                        }
                        OutlinedButton(
                            onClick = { showImageSourceDialog = false; launchCamera() },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(16.dp)
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Icon(Icons.Rounded.CameraAlt, contentDescription = null, modifier = Modifier.size(32.dp), tint = MaterialTheme.colorScheme.primary)
                                Text(stringResource(R.string.take_photo))
                            }
                        }
                    }
                    Spacer(Modifier.height(16.dp))
                    TextButton(onClick = { showImageSourceDialog = false }) {
                        Text(stringResource(R.string.cancel))
                    }
                }
            }
        } else if (isProcessing) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                CircularProgressIndicator(modifier = Modifier.size(64.dp))
                Spacer(Modifier.height(24.dp))
                Text(stringResource(R.string.processing_image), style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
            }
        } else if (parsedValues != null) {
            // OCR complete - quick preview before verification
            Column(
                modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                previewBitmap?.let { bmp ->
                    Surface(
                        modifier = Modifier.size(200.dp).shadow(4.dp, RoundedCornerShape(32.dp)),
                        shape = RoundedCornerShape(32.dp),
                        color = Color.White,
                        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
                    ) {
                        androidx.compose.foundation.Image(
                            bitmap = bmp.asImageBitmap(),
                            contentDescription = "Soil report preview",
                            contentScale = androidx.compose.ui.layout.ContentScale.Fit,
                            modifier = Modifier.size(200.dp).clip(RoundedCornerShape(32.dp))
                        )
                    }
                    Spacer(Modifier.height(24.dp))
                }
                Text(stringResource(R.string.ocr_complete), style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
                Spacer(Modifier.height(16.dp))
                Column(modifier = Modifier.padding(horizontal = 24.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    parsedValues?.nitrogen?.let { Text("N: ${it.displayText}") }
                    parsedValues?.phosphorus?.let { Text("P: ${it.displayText}") }
                    parsedValues?.potassium?.let { Text("K: ${it.displayText}") }
                    parsedValues?.ph?.let { Text("pH: ${it.displayText}") }
                    if (!parsedValues!!.isComplete) {
                        Text(
                            stringResource(R.string.missing_values_warning, parsedValues!!.missing.joinToString(", ")),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.error
                        )
                    }
                }
                Spacer(Modifier.height(32.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedButton(
                        onClick = { parsedValues = null; previewBitmap = null },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Text(stringResource(R.string.rescan))
                    }
                    Button(
                        onClick = { parsedValues?.let { onComplete(it) } },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Text(stringResource(R.string.verify_and_continue))
                    }
                }
            }
        } else {
            // Initial state - prompt for image source
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Surface(
                    modifier = Modifier.size(200.dp).shadow(4.dp, RoundedCornerShape(32.dp)),
                    shape = RoundedCornerShape(32.dp),
                    color = Color.White,
                    border = BorderStroke(1.dp, Color(0xFFF0F0F0))
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(Icons.Rounded.AddAPhoto, null, modifier = Modifier.size(64.dp), tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.4f))
                    }
                }
                Spacer(Modifier.height(32.dp))
                Text(stringResource(R.string.scan_soil_report), style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
                Spacer(Modifier.height(16.dp))
                Text(
                    stringResource(R.string.scan_soil_report_hint),
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray,
                    textAlign = TextAlign.Center
                )
                Spacer(Modifier.height(40.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedButton(
                        onClick = {
                            pickImageLauncher.launch(
                                PickVisualMediaRequest(
                                    ActivityResultContracts.PickVisualMedia.ImageOnly
                                )
                            )
                        },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Icon(Icons.Rounded.PhotoLibrary, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(8.dp))
                        Text(stringResource(R.string.choose_from_gallery))
                    }
                    Button(
                        onClick = { launchCamera() },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Icon(Icons.Rounded.CameraAlt, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(8.dp))
                        Text(stringResource(R.string.take_photo))
                    }
                }
                ocrError?.let { err ->
                    Spacer(Modifier.height(16.dp))
                    Text(
                        stringResource(R.string.ocr_error, err),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
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
            rainfallMm = -1.0, // sentinel: backend derives rainfall from weather using coordinates
            temperatureC = formInputs.temperatureC.toDoubleOrNull() ?: 25.0,
            farmSizeAcres = formInputs.farmSizeAcres.toDoubleOrNull() ?: 1.0,
            latitude = LocationSnapshotStore.latestLatitude,
            longitude = LocationSnapshotStore.latestLongitude,
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


// ============================================
// NO SOIL REPORT FLOW COMPOSABLES
// ============================================

/**
 * Loading step for the "No Soil Report" flow.
 *
 * Drives a small state machine (NoSoilReportPhase):
 *   1. Requests location permission (if not already granted)
 *   2. Fetches device coordinates via Google Play Services
 *   3. Resolves state name from coordinates (geocoding)
 *   4. Calls the backend No-Soil-Report endpoint via the ViewModel
 *
 * Handles denied permissions and unavailable location with
 * user-friendly error messages and retry buttons.
 */
@Composable
fun NoSoilReportLoadingStep(
    viewModel: CropRecommendationViewModel,
    selectedSoil: SoilTypeInfo?,
    phase: NoSoilReportPhase,
    onPhaseChange: (NoSoilReportPhase) -> Unit,
    isLoading: Boolean,
    apiError: String?,
    onBack: () -> Unit,
    onReset: () -> Unit
) {
    val context = LocalContext.current

    // ---- Side effect: request location permission ----
    if (phase == NoSoilReportPhase.PERMISSION_CHECK) {
        LocationPermissionEffect(
            context = context,
            onPermissionGranted = { onPhaseChange(NoSoilReportPhase.FETCHING_LOCATION) },
            onPermissionDenied = { onPhaseChange(NoSoilReportPhase.PERMISSION_DENIED) }
        )
    }

    // ---- Side effect: fetch coordinates + call API ----
    if (phase == NoSoilReportPhase.FETCHING_LOCATION) {
        LaunchedEffect(Unit) {
            val location = getDeviceLocation(context)
            if (location != null) {
                val (lat, lon) = location
                val appLanguage = LanguagePreferences.getSelectedLanguage(context) ?: "en"
                val detailed = getDetailedAddressFromLocation(context, lat, lon, appLanguage)
                val state = detailed?.state ?: getRegionFromCoordinates(context, lat, lon, appLanguage)
                val locationName = detailed?.fullDisplayName
                viewModel.fetchNoSoilReportRecommendations(lat, lon, state, selectedSoil?.name, locationName)
                onPhaseChange(NoSoilReportPhase.API_LOADING)
            } else {
                onPhaseChange(NoSoilReportPhase.LOCATION_UNAVAILABLE)
            }
        }
    }

    // ---- UI rendering ----
    when (phase) {
        NoSoilReportPhase.PERMISSION_CHECK, NoSoilReportPhase.FETCHING_LOCATION ->
            NoSoilReportLoadingContent(
                title = when (phase) {
                    NoSoilReportPhase.PERMISSION_CHECK -> "Checking location permission..."
                    NoSoilReportPhase.FETCHING_LOCATION -> "Fetching your GPS location..."
                    else -> "Loading..."
                },
                subtitle = when (phase) {
                    NoSoilReportPhase.PERMISSION_CHECK -> "We need GPS permission to obtain real soil and weather data"
                    NoSoilReportPhase.FETCHING_LOCATION -> "Obtaining high-accuracy coordinates for SoilGrids & Open-Meteo"
                    else -> ""
                },
                onBack = onBack
            )

        NoSoilReportPhase.API_LOADING -> {
            if (isLoading) {
                NoSoilReportLoadingContent(
                    title = "Fetching real environmental data...",
                    subtitle = "Retrieving SoilGrids soil profile and Open-Meteo historical weather",
                    onBack = onBack
                )
            } else if (apiError != null) {
                NoSoilReportErrorContent(
                    message = apiError,
                    onRetry = {
                        onReset()
                        onPhaseChange(NoSoilReportPhase.PERMISSION_CHECK)
                    },
                    onBack = onBack
                )
            } else {
                NoSoilReportLoadingContent(
                    title = "Preparing environmental summary...",
                    subtitle = "",
                    onBack = onBack
                )
            }
        }

        NoSoilReportPhase.PERMISSION_DENIED ->
            NoSoilReportErrorContent(
                message = "Location permission is required. " +
                    "The system requires real GPS coordinates to look up environmental and soil data.",
                onRetry = { onPhaseChange(NoSoilReportPhase.PERMISSION_CHECK) },
                onBack = onBack
            )

        NoSoilReportPhase.LOCATION_UNAVAILABLE ->
            NoSoilReportErrorContent(
                message = "GPS location is currently unavailable. " +
                    "Please ensure Location/GPS is turned on in your device settings.",
                onRetry = {
                    onReset()
                    onPhaseChange(NoSoilReportPhase.PERMISSION_CHECK)
                },
                onBack = onBack
            )
    }
}

@Composable
private fun NoSoilReportLoadingContent(
    title: String,
    subtitle: String,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator(modifier = Modifier.size(64.dp))
        Spacer(modifier = Modifier.height(24.dp))
        Text(title, style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold), textAlign = TextAlign.Center)
        if (subtitle.isNotBlank()) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(subtitle, style = MaterialTheme.typography.bodyMedium, color = Color.Gray, textAlign = TextAlign.Center)
        }
        Spacer(modifier = Modifier.height(24.dp))
        PremiumOutlinedButton("Go Back", onBack, icon = Icons.AutoMirrored.Rounded.ArrowBack)
    }
}

@Composable
private fun NoSoilReportErrorContent(
    message: String,
    onRetry: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            Icons.Rounded.Warning, null,
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.error
        )
        Spacer(modifier = Modifier.height(24.dp))
        Text(message, style = MaterialTheme.typography.bodyLarge, color = Color(0xFF1B1B1B), textAlign = TextAlign.Center)
        Spacer(modifier = Modifier.height(24.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            PremiumOutlinedButton("Go Back", onBack, icon = Icons.AutoMirrored.Rounded.ArrowBack)
            PremiumButton("Retry", onRetry, icon = Icons.Rounded.Refresh)
        }
    }
}

/**
 * Real-Data-First results and guidance step for the "No Soil Report" flow.
 *
 * Displays:
 *  - Real Geocoded Location & Coordinates
 *  - Real Temperature & Humidity from Open-Meteo
 *  - Real Annual Rainfall from Open-Meteo ERA5-Land (previous complete calendar year)
 *  - Real Soil Properties from SoilGrids (pH, clay, sand, silt)
 *  - Explicit N/P/K Unavailable status
 *  - Guidance alert explaining that reliable crop recommendation requires measured N/P/K
 *  - Direct CTA to [Upload Soil Report]
 */
@Composable
fun NoSoilReportResultStep(
    result: NoSoilReportResponse?,
    selectedSoil: SoilTypeInfo?,
    onUploadSoilReport: () -> Unit,
    onReset: () -> Unit
) {
    val scrollState = rememberScrollState()
    val soil = result?.soil
    val weather = result?.weather
    val rainfall = result?.rainfall
    val recommendations = result?.recommendations ?: emptyList()
    val isRecommendationAvailable = result?.recommendation_available == true && recommendations.isNotEmpty()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // ---- Header ----
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .shadow(4.dp, RoundedCornerShape(24.dp)),
            shape = RoundedCornerShape(24.dp),
            color = Color.White
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.Analytics, null, tint = MaterialTheme.colorScheme.primary)
                    Spacer(Modifier.width(12.dp))
                    Text("Field Conditions & Suitability", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
                }
                Text(
                    "Real environmental conditions derived from your GPS coordinates",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray
                )
            }
        }

        // ---- 1. Location Card ----
        val locName = result?.location?.display_name?.takeIf { it.isNotBlank() } ?: "Detected Location"
        val latVal = result?.location?.latitude ?: 0.0
        val lonVal = result?.location?.longitude ?: 0.0
        val coordStr = String.format(java.util.Locale.US, "%.4f° N, %.4f° E", latVal, lonVal)
        RealDataCard(
            icon = Icons.Rounded.LocationOn,
            title = "Location",
            value = locName,
            source = result?.location?.source ?: "Device GPS",
            extra = "Coordinates: $coordStr"
        )

        // ---- 2. Weather Cards ----
        if (weather != null) {
            val tempField = weather.temperature
            val tempVal = tempField?.getDisplayString() ?: "Unavailable"
            val tempSource = tempField?.source ?: "Open-Meteo"
            RealDataCard(
                icon = Icons.Rounded.Thermostat,
                title = "Temperature",
                value = tempVal,
                source = tempSource,
                extra = weather.current_conditions?.let { "Conditions: $it" }
            )

            val humField = weather.humidity
            val humVal = humField?.getDisplayString() ?: "Unavailable"
            val humSource = humField?.source ?: "Open-Meteo"
            RealDataCard(
                icon = Icons.Rounded.WaterDrop,
                title = "Humidity",
                value = humVal,
                source = humSource
            )
        }

        // ---- 3. Annual Rainfall Card ----
        if (rainfall != null) {
            val rainField = rainfall.annual_rainfall
            val rainVal = rainField?.getDisplayString() ?: "Unavailable"
            val rainSource = rainField?.source ?: "Open-Meteo ERA5-Land"
            val rainPeriod = rainField?.period ?: rainfall.period ?: "2025"
            RealDataCard(
                icon = Icons.Rounded.Grain,
                title = "Annual Rainfall",
                value = rainVal,
                source = rainSource,
                extra = "Period: $rainPeriod"
            )
        }

        // ---- 4. Soil Properties Card ----
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .shadow(2.dp, RoundedCornerShape(20.dp)),
            shape = RoundedCornerShape(20.dp),
            color = Color.White,
            border = BorderStroke(1.dp, Color(0xFFF0F0F0))
        ) {
            Column(modifier = Modifier.padding(18.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Rounded.Grass, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(24.dp))
                    }
                    Spacer(Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Soil Profile", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold))
                        Text(
                            "Selected: ${soil?.farmer_selected_type ?: selectedSoil?.name ?: "Farmer Input"}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }

                HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp, color = Color(0xFFF5F5F5))

                // SoilGrids pH & texture components
                val phText = soil?.ph?.getDisplayString() ?: "Unavailable"
                val texClass = soil?.texture_class?.replace('_', ' ')?.replaceFirstChar { it.uppercase() } ?: "SoilGrids Texture"

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceAround
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Soil pH", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                        Text(phText, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF9C27B0)))
                        Text("SoilGrids (0-5cm)", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                    }
                    Box(modifier = Modifier.height(36.dp).width(1.dp).background(Color(0xFFEEEEEE)))
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Texture Class", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                        Text(texClass, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF795548)))
                        Text("SoilGrids (0-5cm)", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                    }
                }

                if (soil?.sand != null || soil?.clay != null || soil?.silt != null) {
                    val sandStr = soil.sand?.getDisplayString() ?: "--"
                    val clayStr = soil.clay?.getDisplayString() ?: "--"
                    val siltStr = soil.silt?.getDisplayString() ?: "--"
                    Spacer(Modifier.height(8.dp))
                    Text(
                        "Fractions: Sand $sandStr • Clay $clayStr • Silt $siltStr (Depth: ${soil.depth_used ?: "0-5cm"})",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth()
                    )
                }

                HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp), thickness = 0.5.dp, color = Color(0xFFF5F5F5))

                // Nutrients Status Card (N/P/K Unavailable without soil report)
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFFFFF8E1), RoundedCornerShape(12.dp))
                        .padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Rounded.Cancel, null, tint = Color(0xFFE65100), modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(8.dp))
                    Column {
                        Text(
                            "N / P / K Nutrients: Unavailable",
                            style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFFE65100))
                        )
                        Text(
                            "Plant-available Nitrogen, Phosphorus, and Potassium require a laboratory Soil Health Card.",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color(0xFF5D4037)
                        )
                    }
                }
            }
        }

        // ---- 5. Environmental Suitability Recommendations ----
        if (isRecommendationAvailable) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    "Environmental Suitability — N/P/K unavailable",
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                )
                Text(
                    "Agronomic suitability based on real location, weather, rainfall, and soil type",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
            }

            recommendations.forEach { rec ->
                EnvironmentalCropCard(rec)
            }
        }

        // ---- 6. Soil Report CTA Banner ----
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .shadow(4.dp, RoundedCornerShape(24.dp)),
            shape = RoundedCornerShape(24.dp),
            color = Color(0xFFFFFDF7),
            border = BorderStroke(1.5.dp, Color(0xFFFFB74D))
        ) {
            Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    Icons.Rounded.DocumentScanner,
                    contentDescription = null,
                    modifier = Modifier.size(44.dp),
                    tint = Color(0xFFE65100)
                )
                Spacer(Modifier.height(10.dp))
                Text(
                    "Have a Soil Health Card or laboratory report?",
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFFBF360C)),
                    textAlign = TextAlign.Center
                )
                Spacer(Modifier.height(6.dp))
                Text(
                    "Upload your soil report to run our high-accuracy N/P/K machine learning model with tailored fertilizer recommendations.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color(0xFF5D4037),
                    textAlign = TextAlign.Center
                )
                Spacer(Modifier.height(18.dp))
                PremiumButton(
                    text = "Upload Soil Report",
                    onClick = onUploadSoilReport,
                    icon = Icons.Rounded.CameraAlt,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        Spacer(Modifier.height(8.dp))
        PremiumOutlinedButton("START OVER", onReset, icon = Icons.Rounded.Refresh)
        Spacer(Modifier.height(40.dp))
    }
}

@Composable
private fun RealDataCard(
    icon: ImageVector,
    title: String,
    value: String,
    source: String,
    extra: String? = null
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(2.dp, RoundedCornerShape(18.dp)),
        shape = RoundedCornerShape(18.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(icon, null, modifier = Modifier.size(24.dp), tint = MaterialTheme.colorScheme.primary)
            }
            Spacer(Modifier.width(14.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.labelMedium, color = Color.Gray)
                Text(value, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B1B1B)))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Source: $source", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.SemiBold)
                    if (!extra.isNullOrBlank()) {
                        Text(" • $extra", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                    }
                }
            }
        }
    }
}

@Composable
private fun EnvironmentalCropCard(rec: EnvironmentalCropRecommendation) {
    val badgeColor = when (rec.suitability_level) {
        "Highly Suitable" -> Color(0xFF2E7D32)
        "Suitable" -> Color(0xFF1565C0)
        else -> Color(0xFFE65100)
    }
    val badgeBg = when (rec.suitability_level) {
        "Highly Suitable" -> Color(0xFFE8F5E9)
        "Suitable" -> Color(0xFFE3F2FD)
        else -> Color(0xFFFFF3E0)
    }

    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(3.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        rec.crop_name,
                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = Color(0xFF1B1B1B))
                    )
                    if (!rec.hindi_name.isNullOrBlank()) {
                        Text(
                            rec.hindi_name,
                            style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray, fontWeight = FontWeight.Medium)
                        )
                    }
                }
                Surface(
                    color = badgeBg,
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(
                        rec.suitability_level,
                        color = badgeColor,
                        style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                    )
                }
            }

            if (!rec.water_requirement.isNullOrBlank()) {
                Spacer(Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.WaterDrop, null, modifier = Modifier.size(16.dp), tint = Color(0xFF1976D2))
                    Spacer(Modifier.width(6.dp))
                    Text(
                        "Water requirement: ${rec.water_requirement}",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF555555)
                    )
                }
            }

            val factors = rec.contributing_factors
            if (!factors.isNullOrEmpty()) {
                HorizontalDivider(modifier = Modifier.padding(vertical = 10.dp), thickness = 0.5.dp, color = Color(0xFFF5F5F5))
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Contributing Environmental Factors:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = Color(0xFF2E7D32)))
                    for (factor in factors) {
                        Row(verticalAlignment = Alignment.Top) {
                            Text("• ", color = Color(0xFF2E7D32), style = MaterialTheme.typography.bodySmall)
                            Text(factor, style = MaterialTheme.typography.bodySmall, color = Color(0xFF333333))
                        }
                    }
                }
            }

            val notes = rec.management_notes
            if (!notes.isNullOrEmpty()) {
                Spacer(Modifier.height(6.dp))
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Agronomic Management Notes:", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = Color(0xFFE65100)))
                    for (note in notes) {
                        Row(verticalAlignment = Alignment.Top) {
                            Text("• ", color = Color(0xFFE65100), style = MaterialTheme.typography.bodySmall)
                            Text(note, style = MaterialTheme.typography.bodySmall, color = Color(0xFF555555))
                        }
                    }
                }
            }
        }
    }
}

