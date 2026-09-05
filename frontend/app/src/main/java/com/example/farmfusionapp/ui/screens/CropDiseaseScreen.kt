package com.example.farmfusionapp.ui.screens

import android.Manifest
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.OpenInNew
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.AsyncImage
import coil.compose.rememberAsyncImagePainter
import kotlinx.coroutines.launch
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.DiseaseResult
import com.example.farmfusionapp.data.model.StoreRecommendationItem
import com.example.farmfusionapp.ui.components.NeoCard
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.components.NeoSectionTitle
import com.example.farmfusionapp.ui.components.PremiumButton
import com.example.farmfusionapp.utils.*
import com.example.farmfusionapp.viewmodel.DiseaseViewModel
import java.io.File
import java.io.FileOutputStream

private val CropDashBg = Color(0xFFF9FAFB)
private val CropPrimaryDark = Color(0xFF1B5E20)
private val CropSuccessGreen = Color(0xFF059669)
private val CropErrorRed = Color(0xFFDC2626)
private val CropWarningOrange = Color(0xFFD97706)

private enum class DiseaseScreenState { IDLE, SCANNING, RESULT }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropDiseaseScreen(navController: NavController) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val diseaseViewModel: DiseaseViewModel = viewModel()
    var state by remember { mutableStateOf(DiseaseScreenState.IDLE) }
    var capturedImageUri by remember { mutableStateOf<Uri?>(null) }

    val detectState by diseaseViewModel.detectState
    val currentLang = LocalAppLanguage.current
    val strings = LocalStrings.current
    val token = remember { AuthStore.getAuthToken(context) }

    val tempFile = remember { File(context.cacheDir, "disease_scan_temp.jpg") }
    val fileProviderUri = remember { FileProvider.getUriForFile(context, "com.example.farmfusionapp.provider", tempFile) }

    val startAnalysis = {
        state = DiseaseScreenState.SCANNING
        diseaseViewModel.detectDisease(
            imageFile = tempFile,
            cropType = null,
            firebaseToken = null,
            responseLanguage = currentLang
        )
    }

    val cameraLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { success ->
        if (success) {
            capturedImageUri = fileProviderUri
            scope.launch(kotlinx.coroutines.Dispatchers.IO) {
                optimizeImageFile(tempFile)
                kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                    startAnalysis()
                }
            }
        }
    }

    val galleryLauncher = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { selectedUri ->
        if (selectedUri != null) {
            scope.launch(kotlinx.coroutines.Dispatchers.IO) {
                val success = prepareImageFromUri(context, selectedUri, tempFile)
                if (success) {
                    kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                        capturedImageUri = selectedUri
                        startAnalysis()
                    }
                }
            }
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) cameraLauncher.launch(fileProviderUri)
    }

    LaunchedEffect(detectState) {
        if (detectState is DiseaseViewModel.DiseaseDetectState.Success) {
            state = DiseaseScreenState.RESULT
        }
    }

    NeoScaffoldBackground(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                CenterAlignedTopAppBar(
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent,
                        titleContentColor = CropPrimaryDark,
                        navigationIconContentColor = Color(0xFF1A1A1A)
                    ),
                    title = { Text(strings.disease.diseaseDetection, fontWeight = FontWeight.ExtraBold) },
                    navigationIcon = {
                        IconButton(onClick = {
                            if (state == DiseaseScreenState.RESULT) {
                                state = DiseaseScreenState.IDLE
                                diseaseViewModel.resetDetectState()
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
            Box(modifier = Modifier.fillMaxSize().padding(padding)) {
                when (state) {
                    DiseaseScreenState.IDLE -> UploadPanel(
                        onCapture = { permissionLauncher.launch(Manifest.permission.CAMERA) },
                        onGallery = { galleryLauncher.launch("image/*") }
                    )
                    DiseaseScreenState.SCANNING -> ScanningPanel(
                        imageUri = capturedImageUri,
                        onCancel = {
                            diseaseViewModel.resetDetectState()
                            state = DiseaseScreenState.IDLE
                        }
                    )
                    DiseaseScreenState.RESULT -> {
                        val res = (detectState as? DiseaseViewModel.DiseaseDetectState.Success)?.response?.data
                        ResultPanel(
                            imageUri = capturedImageUri,
                            result = res,
                            onScanAgain = {
                                state = DiseaseScreenState.IDLE
                                capturedImageUri = null
                                diseaseViewModel.resetDetectState()
                            }
                        )
                    }
                }
            }

            if (detectState is DiseaseViewModel.DiseaseDetectState.Error) {
                AlertDialog(
                    onDismissRequest = { diseaseViewModel.resetDetectState(); state = DiseaseScreenState.IDLE },
                    title = { Text("Scan Failed", fontWeight = FontWeight.Bold, color = CropErrorRed) },
                    text = { Text((detectState as DiseaseViewModel.DiseaseDetectState.Error).message) },
                    confirmButton = {
                        Button(onClick = { diseaseViewModel.resetDetectState(); state = DiseaseScreenState.IDLE }) {
                            Text("Retry")
                        }
                    }
                )
            }
        }
    }
}

// ============================================
// FULLY REDESIGNED UPLOAD PANEL
// ============================================
@Composable
private fun UploadPanel(onCapture: () -> Unit, onGallery: () -> Unit) {
    val strings = LocalStrings.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp, vertical = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // 1. Hero Section with Background Illustration
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(290.dp)
        ) {
            Image(
                painter = painterResource(id = R.drawable.ill_diseased_plant),
                contentDescription = strings.disease.diseaseDetection,
                contentScale = ContentScale.Fit,
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(0.95f)
                    .align(Alignment.BottomEnd)
                    .offset(x = 45.dp, y = 10.dp)
            )

            Column(
                modifier = Modifier
                    .fillMaxWidth(0.65f)
                    .padding(top = 48.dp)
            ) {
                Text(
                    text = strings.disease.diseaseDetection,
                    style = MaterialTheme.typography.headlineMedium.copy(
                        fontWeight = FontWeight.ExtraBold,
                        color = Color(0xFF1A1A1A),
                        lineHeight = 34.sp
                    )
                )

                Spacer(modifier = Modifier.height(12.dp))

                Box(
                    modifier = Modifier
                        .size(width = 32.dp, height = 4.dp)
                        .background(CropPrimaryDark, RoundedCornerShape(2.dp))
                )

                Spacer(modifier = Modifier.height(24.dp))

                Text(
                    text = strings.disease.cameraInstructions,
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = Color(0xFF5A6B5A),
                        lineHeight = 22.sp
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 2. Tip Card
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            color = Color(0xFFF3FAF3),
            border = BorderStroke(1.dp, CropPrimaryDark)
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    shape = CircleShape,
                    color = Color(0xFFDCECC5),
                    modifier = Modifier.size(48.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = Icons.Rounded.Lightbulb,
                            contentDescription = "Tip",
                            tint = Color(0xFF4D7A1F),
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                Box(
                    modifier = Modifier
                        .width(1.dp)
                        .height(36.dp)
                        .background(Color(0xFFC8E6C9))
                )

                Spacer(modifier = Modifier.width(16.dp))

                Column {
                    Text(
                        text = strings.disease.scanPlant,
                        style = MaterialTheme.typography.titleSmall.copy(
                            fontWeight = FontWeight.Bold,
                            color = CropPrimaryDark
                        )
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = strings.disease.cameraInstructions,
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = Color(0xFF5A6B5A),
                            lineHeight = 16.sp
                        )
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // 3. Action Cards (Camera & Gallery)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 96.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Surface(
                onClick = onCapture,
                modifier = Modifier
                    .weight(1f)
                    .height(160.dp),
                shape = RoundedCornerShape(24.dp),
                color = Color.White,
                border = BorderStroke(1.dp, Color(0xFFF0F4F0)),
                shadowElevation = 1.dp
            ) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Surface(
                        shape = CircleShape,
                        color = Color(0xFFF3FAF3),
                        modifier = Modifier.size(56.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = Icons.Rounded.CameraAlt,
                                contentDescription = "Camera",
                                tint = CropPrimaryDark,
                                modifier = Modifier.size(28.dp)
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = strings.disease.takePhoto,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1A1A1A)
                        ),
                        textAlign = TextAlign.Center
                    )
                }
            }

            Surface(
                onClick = onGallery,
                modifier = Modifier
                    .weight(1f)
                    .height(160.dp),
                shape = RoundedCornerShape(24.dp),
                color = Color.White,
                border = BorderStroke(1.dp, Color(0xFFF0F4F0)),
                shadowElevation = 1.dp
            ) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Surface(
                        shape = CircleShape,
                        color = Color(0xFFF3FAF3),
                        modifier = Modifier.size(56.dp)
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = Icons.Rounded.Image,
                                contentDescription = "Gallery",
                                tint = CropPrimaryDark,
                                modifier = Modifier.size(28.dp)
                            )
                        }
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = strings.disease.uploadFromGallery,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1A1A1A)
                        ),
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
    }
}

@Composable
private fun ScanningPanel(imageUri: Uri?, onCancel: () -> Unit) {
    val strings = LocalStrings.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(64.dp))

        Text(
            text = strings.disease.analyzingSymptoms,
            style = MaterialTheme.typography.headlineMedium.copy(
                fontWeight = FontWeight.ExtraBold,
                fontSize = 28.sp,
                color = CropPrimaryDark
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(12.dp))

        Text(
            text = strings.disease.scanningLeaf,
            style = MaterialTheme.typography.bodyMedium.copy(
                color = Color(0xFF5A6B5A),
                lineHeight = 22.sp
            ),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Isolated Background Box
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier.fillMaxWidth()
        ) {
            Image(
                painter = painterResource(id = R.drawable.bg_faint_leaves),
                contentDescription = strings.disease.scanningLeaf,
                contentScale = ContentScale.Fit,
                modifier = Modifier.fillMaxWidth(0.95f)
            )

            Surface(
                shape = RoundedCornerShape(32.dp),
                color = Color.White,
                shadowElevation = 8.dp,
                modifier = Modifier.size(240.dp)
            ) {
                Box(modifier = Modifier.padding(4.dp).fillMaxSize()) {
                    if (imageUri != null) {
                        Image(
                            painter = rememberAsyncImagePainter(imageUri),
                            contentDescription = strings.disease.scanningLeaf,
                            contentScale = ContentScale.Crop,
                            modifier = Modifier
                                .fillMaxSize()
                                .clip(RoundedCornerShape(28.dp))
                        )
                    } else {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(Color(0xFFF5F5F5), RoundedCornerShape(28.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(color = CropPrimaryDark)
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        // Deep Scanning Capsule
        Surface(
            shape = RoundedCornerShape(20.dp),
            color = Color(0xFFF3FAF3),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Surface(
                    shape = CircleShape,
                    color = Color(0xFFE8F5E9),
                    modifier = Modifier.size(48.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = Icons.Rounded.Eco,
                            contentDescription = "Scanning",
                            tint = CropPrimaryDark,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.width(16.dp))

                Column {
                    Text(
                        text = strings.disease.analyzingSymptoms,
                        style = MaterialTheme.typography.titleSmall.copy(
                            fontWeight = FontWeight.Bold,
                            color = CropPrimaryDark
                        )
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = strings.disease.scanningLeaf,
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = Color(0xFF5A6B5A),
                            lineHeight = 16.sp
                        )
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        LinearProgressIndicator(
            modifier = Modifier
                .width(160.dp)
                .height(6.dp)
                .clip(CircleShape),
            color = CropPrimaryDark,
            trackColor = Color(0xFFE8F5E9)
        )

        Spacer(modifier = Modifier.height(40.dp))

        Surface(
            onClick = onCancel,
            shape = RoundedCornerShape(16.dp),
            color = CropErrorRed,
            modifier = Modifier.height(48.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
                modifier = Modifier.padding(horizontal = 24.dp)
            ) {
                Icon(
                    imageVector = Icons.Rounded.Cancel,
                    contentDescription = strings.common.cancel,
                    tint = Color.White,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = strings.common.cancel,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = Color.White,
                        fontSize = 15.sp
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(32.dp))
    }
}

@Composable
private fun ResultPanel(imageUri: Uri?, result: DiseaseResult?, onScanAgain: () -> Unit) {
    val scrollState = rememberScrollState()
    val context = LocalContext.current

    val currentLang = LocalAppLanguage.current
    val strings = LocalStrings.current

    if (result == null || result.ai_analyzed == false) {
        Column(Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
            Icon(Icons.Rounded.SentimentDissatisfied, null, modifier = Modifier.size(80.dp), tint = Color.Gray)
            Text(strings.disease.diagnosisResult, style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
            Text(result?.invalid_image_reason ?: "The AI could not identify a clear plant in this image.", textAlign = TextAlign.Center, color = Color.Gray)
            Spacer(Modifier.height(24.dp))
            PremiumButton(text = strings.disease.scanAnotherPlant, onClick = onScanAgain)
        }
        return
    }

    // ============================================
    // DEDICATED NO PLANT DETECTED VIEW
    // ============================================
    val isNoPlant = result.is_plant_image == false ||
            result.can_analyze == false ||
            result.diagnosis_status.equals("no_plant", ignoreCase = true) ||
            result.disease_name.equals("No Plant Detected", ignoreCase = true)

    if (isNoPlant) {
        val noPlantTitle = AppLocalizer.localizeDisease("No Plant Detected", currentLang).ifBlank { "No Plant Detected" }
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(scrollState)
                .padding(vertical = 20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Image with NO PLANT warning badge
            Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                Surface(
                    shape = RoundedCornerShape(28.dp),
                    modifier = Modifier.fillMaxWidth().height(200.dp).shadow(8.dp)
                ) {
                    Box {
                        if (imageUri != null) {
                            Image(
                                painter = rememberAsyncImagePainter(imageUri),
                                contentDescription = null,
                                contentScale = ContentScale.Crop,
                                modifier = Modifier.fillMaxSize()
                            )
                        }
                        Surface(
                            color = CropWarningOrange,
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.padding(16.dp).align(Alignment.TopEnd)
                        ) {
                            Text(
                                text = "NO PLANT",
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                                color = Color.White,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }

            // Main No Plant Detected Card
            Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                NeoCard {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = noPlantTitle,
                                style = MaterialTheme.typography.headlineSmall.copy(
                                    fontWeight = FontWeight.Black,
                                    color = Color(0xFF1B1B1B)
                                )
                            )
                        }

                        Surface(
                            color = CropWarningOrange.copy(alpha = 0.12f),
                            border = BorderStroke(1.dp, CropWarningOrange),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text(
                                text = "NOT A PLANT",
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                                color = CropWarningOrange,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Text(
                            text = result.description?.takeIf { it.isNotBlank() }
                                ?: "No crop leaf, plant, or agricultural foliage was detected in this image. The disease detection system only analyzes plants and crops.\n\nPlease point your camera directly at a plant leaf, stem, or fruit in good lighting.",
                            style = MaterialTheme.typography.bodyMedium.copy(
                                lineHeight = 20.sp,
                                color = Color.DarkGray
                            )
                        )
                    }
                }
            }

            // Photo Guidelines Card
            Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                NeoCard {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text(
                            text = "Photo Guidelines for Best Diagnosis",
                            fontWeight = FontWeight.Bold,
                            color = CropPrimaryDark
                        )
                        Row(verticalAlignment = Alignment.Top) {
                            Icon(
                                Icons.Rounded.CheckCircle,
                                contentDescription = null,
                                tint = CropPrimaryDark,
                                modifier = Modifier.size(16.dp).padding(top = 2.dp)
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(
                                text = "Point camera directly at the affected crop leaf, stem, or fruit",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                        Row(verticalAlignment = Alignment.Top) {
                            Icon(
                                Icons.Rounded.CheckCircle,
                                contentDescription = null,
                                tint = CropPrimaryDark,
                                modifier = Modifier.size(16.dp).padding(top = 2.dp)
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(
                                text = "Ensure the plant is in focus with natural, even lighting",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                        Row(verticalAlignment = Alignment.Top) {
                            Icon(
                                Icons.Rounded.Cancel,
                                contentDescription = null,
                                tint = CropErrorRed,
                                modifier = Modifier.size(16.dp).padding(top = 2.dp)
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(
                                text = "Avoid photographing electronic devices, indoor surfaces, or general objects",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                    }
                }
            }

            // Scan Another Plant Button
            Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                PremiumButton(
                    text = strings.disease.scanAnotherPlant,
                    onClick = onScanAgain,
                    icon = Icons.Rounded.Refresh
                )
            }
            Spacer(Modifier.height(40.dp))
        }
        return
    }

    val rawDiseaseName = result.disease_name ?: "Unknown Disease"
    val isHealthy = result.diagnosis_status.equals("healthy", ignoreCase = true) ||
            rawDiseaseName.contains("healthy", ignoreCase = true)
    val isDiseased = !isHealthy

    val baseDiseaseName = if (isHealthy && (rawDiseaseName.equals("healthy", ignoreCase = true) || rawDiseaseName.isBlank())) {
        "Healthy Plant"
    } else {
        rawDiseaseName.replace("_", " ").split(" ").joinToString(" ") { word ->
            word.replaceFirstChar { if (it.isLowerCase()) it.titlecase(java.util.Locale.ROOT) else it.toString() }
        }
    }
    val diseaseName = AppLocalizer.localizeDisease(baseDiseaseName, currentLang)

    val rawStatusText = if (isDiseased) "DISEASED" else "HEALTHY"
    val statusText = AppLocalizer.localizeSeverity(rawStatusText, currentLang)
    val statusBgColor = if (isDiseased) CropErrorRed else Color(0xFF2E7D32)

    val severity = result.severity ?: if (isHealthy) "No Threat" else "High"
    val rawThreatText = when {
        isHealthy -> "NO THREAT"
        severity.equals("none", ignoreCase = true) -> "NO THREAT"
        else -> severity.uppercase()
    }
    val threatText = AppLocalizer.localizeSeverity(rawThreatText, currentLang)
    val sevColor = when (rawThreatText.lowercase()) {
        "no threat", "none", "healthy", "low" -> Color(0xFF2E7D32)
        "moderate", "medium" -> CropWarningOrange
        else -> CropErrorRed
    }

    val description = AppLocalizer.localizeDiseaseAdvice(result.description, currentLang)
    val treatmentSuggestions = (result.treatment_suggestions ?: emptyList()).map { AppLocalizer.localizeDiseaseAdvice(it, currentLang) }
    val preventionTips = (result.prevention_tips ?: emptyList()).map { AppLocalizer.localizeDiseaseAdvice(it, currentLang) }

    val treatmentPicks = remember(result.store_recommendations) {
        result.store_recommendations?.filterNot { item ->
            val t = item.title.lowercase()
            t.contains("knapsack") || t.contains("pesticide spraying") || t.contains("ppe safety") || t.contains("sprayer")
        } ?: emptyList()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(vertical = 20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
            Surface(shape = RoundedCornerShape(28.dp), modifier = Modifier.fillMaxWidth().height(200.dp).shadow(8.dp)) {
                Box {
                    if (imageUri != null) Image(painter = rememberAsyncImagePainter(imageUri), contentDescription = null, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxSize())
                    Surface(color = statusBgColor, shape = RoundedCornerShape(12.dp), modifier = Modifier.padding(16.dp).align(Alignment.TopEnd)) {
                        Text(statusText, modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp), color = Color.White, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
            NeoCard {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                        Text(
                            text = diseaseName,
                            style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Black, color = Color(0xFF1B1B1B))
                        )
                    }

                    Surface(color = sevColor.copy(alpha = 0.12f), border = BorderStroke(1.dp, sevColor), shape = RoundedCornerShape(8.dp)) {
                        Text(threatText, modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp), color = sevColor, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }

                    if (description.isNotBlank()) {
                        Text(
                            text = description,
                            style = MaterialTheme.typography.bodyMedium.copy(lineHeight = 20.sp, color = Color.DarkGray)
                        )
                    }
                }
            }
        }

        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
            NeoSectionTitle(strings.disease.recommendedCare, strings.disease.treatmentSteps)
        }

        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
            NeoCard {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(strings.disease.treatmentSteps, fontWeight = FontWeight.Bold, color = CropPrimaryDark)
                    if (treatmentSuggestions.isEmpty()) {
                        Text("No treatment steps available.", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                    } else {
                        treatmentSuggestions.forEach { tip ->
                            Row(verticalAlignment = Alignment.Top) {
                                Icon(Icons.Rounded.CheckCircle, null, tint = CropPrimaryDark, modifier = Modifier.size(16.dp).padding(top = 2.dp))
                                Spacer(Modifier.width(8.dp))
                                Text(tip, style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }

                    HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

                    Text(strings.disease.preventionTips, fontWeight = FontWeight.Bold, color = CropPrimaryDark)
                    if (preventionTips.isEmpty()) {
                        Text("No prevention tips available.", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                    } else {
                        preventionTips.forEach { tip ->
                            Row(verticalAlignment = Alignment.Top) {
                                Icon(Icons.Rounded.Shield, null, tint = CropWarningOrange, modifier = Modifier.size(16.dp).padding(top = 2.dp))
                                Spacer(Modifier.width(8.dp))
                                Text(tip, style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                }
            }
        }

        if (treatmentPicks.isNotEmpty()) {
            Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                NeoSectionTitle(strings.disease.buyTreatment, diseaseName)
            }
            LazyRow(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(start = 20.dp, end = 20.dp, bottom = 12.dp)
            ) {
                items(treatmentPicks) { item ->
                    StoreMiniCard(item) {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(item.shop_url))
                        context.startActivity(intent)
                    }
                }
            }
        }

        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
            PremiumButton(text = strings.disease.scanAnotherPlant, onClick = onScanAgain, icon = Icons.Rounded.Refresh)
        }
        Spacer(Modifier.height(40.dp))
    }
}

@Composable
fun StoreMiniCard(item: StoreRecommendationItem, onClick: () -> Unit) {
    val strings = LocalStrings.current
    val currentLang = LocalAppLanguage.current
    val localizedTitle = AppLocalizer.localizeDiseaseAdvice(item.title, currentLang)
    val localizedSubtitle = AppLocalizer.localizeDiseaseAdvice(item.subtitle, currentLang)

    Surface(
        onClick = onClick,
        modifier = Modifier
            .width(160.dp)
            .shadow(
                elevation = 1.dp,
                shape = RoundedCornerShape(16.dp),
                spotColor = Color(0x12000000),
                ambientColor = Color(0x08000000)
            ),
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, Color(0xFFE8ECEF)),
        color = Color.White
    ) {
        Column {
            Box(
                Modifier
                    .fillMaxWidth()
                    .height(104.dp)
                    .background(Color(0xFFF8F9FA))
            ) {
                AsyncImage(
                    model = item.image_url,
                    contentDescription = localizedTitle,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
            }
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    text = localizedTitle,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    fontSize = 13.sp,
                    color = Color(0xFF1E293B)
                )
                Text(
                    text = localizedSubtitle,
                    color = Color(0xFF64748B),
                    fontSize = 11.sp,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(Modifier.height(2.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = strings.store.buyOnAmazon,
                        fontWeight = FontWeight.SemiBold,
                        color = CropPrimaryDark,
                        fontSize = 12.sp
                    )
                    Spacer(Modifier.width(4.dp))
                    Icon(
                        Icons.AutoMirrored.Rounded.OpenInNew,
                        contentDescription = null,
                        modifier = Modifier.size(12.dp),
                        tint = CropPrimaryDark
                    )
                }
            }
        }
    }
}

private fun optimizeImageFile(file: File, maxDimension: Int = 1280, quality: Int = 82) {
    try {
        if (!file.exists() || file.length() == 0L) return
        val boundsOptions = android.graphics.BitmapFactory.Options().apply {
            inJustDecodeBounds = true
        }
        android.graphics.BitmapFactory.decodeFile(file.absolutePath, boundsOptions)
        val origW = boundsOptions.outWidth
        val origH = boundsOptions.outHeight
        if (origW <= 0 || origH <= 0) return

        var sampleSize = 1
        while ((origW / sampleSize) > maxDimension * 2 || (origH / sampleSize) > maxDimension * 2) {
            sampleSize *= 2
        }

        val decodeOptions = android.graphics.BitmapFactory.Options().apply {
            inSampleSize = sampleSize
        }
        val bitmap = android.graphics.BitmapFactory.decodeFile(file.absolutePath, decodeOptions) ?: return

        val scale = minOf(1.0f, maxDimension.toFloat() / maxOf(bitmap.width, bitmap.height).toFloat())
        val finalBitmap = if (scale < 1.0f) {
            val destW = (bitmap.width * scale).toInt()
            val destH = (bitmap.height * scale).toInt()
            android.graphics.Bitmap.createScaledBitmap(bitmap, destW, destH, true).also {
                if (it != bitmap) bitmap.recycle()
            }
        } else {
            bitmap
        }

        FileOutputStream(file).use { out ->
            finalBitmap.compress(android.graphics.Bitmap.CompressFormat.JPEG, quality, out)
        }
        finalBitmap.recycle()
        android.util.Log.d("CropDisease", "Optimized camera image size: ${file.length()} bytes")
    } catch (e: Exception) {
        android.util.Log.e("CropDisease", "Image optimization failed, using original", e)
    }
}

private fun prepareImageFromUri(context: Context, uri: Uri, targetFile: File, maxDimension: Int = 1280, quality: Int = 82): Boolean {
    return try {
        val boundsOptions = android.graphics.BitmapFactory.Options().apply {
            inJustDecodeBounds = true
        }
        context.contentResolver.openInputStream(uri)?.use { stream ->
            android.graphics.BitmapFactory.decodeStream(stream, null, boundsOptions)
        }
        val origW = boundsOptions.outWidth
        val origH = boundsOptions.outHeight

        var sampleSize = 1
        if (origW > 0 && origH > 0) {
            while ((origW / sampleSize) > maxDimension * 2 || (origH / sampleSize) > maxDimension * 2) {
                sampleSize *= 2
            }
        }

        val decodeOptions = android.graphics.BitmapFactory.Options().apply {
            inSampleSize = sampleSize
        }
        val bitmap = context.contentResolver.openInputStream(uri)?.use { stream ->
            android.graphics.BitmapFactory.decodeStream(stream, null, decodeOptions)
        } ?: return copyUriToTempFile(context, uri, targetFile)

        val scale = minOf(1.0f, maxDimension.toFloat() / maxOf(bitmap.width, bitmap.height).toFloat())
        val finalBitmap = if (scale < 1.0f) {
            val destW = (bitmap.width * scale).toInt()
            val destH = (bitmap.height * scale).toInt()
            android.graphics.Bitmap.createScaledBitmap(bitmap, destW, destH, true).also {
                if (it != bitmap) bitmap.recycle()
            }
        } else {
            bitmap
        }

        FileOutputStream(targetFile).use { out ->
            finalBitmap.compress(android.graphics.Bitmap.CompressFormat.JPEG, quality, out)
        }
        finalBitmap.recycle()
        android.util.Log.d("CropDisease", "Optimized gallery image saved: ${targetFile.length()} bytes")
        true
    } catch (e: Exception) {
        android.util.Log.e("CropDisease", "Optimized load failed, fallback to raw copy", e)
        copyUriToTempFile(context, uri, targetFile)
    }
}

private fun copyUriToTempFile(context: Context, uri: Uri, targetFile: File): Boolean {
    return try {
        context.contentResolver.openInputStream(uri)?.use { input ->
            FileOutputStream(targetFile).use { output ->
                input.copyTo(output)
            }
        }
        true
    } catch (e: Exception) {
        android.util.Log.e("CropDisease", "Copy error", e)
        false
    }
}