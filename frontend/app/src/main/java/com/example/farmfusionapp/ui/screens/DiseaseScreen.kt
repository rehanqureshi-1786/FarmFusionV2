package com.example.farmfusionapp.ui.screens

import android.Manifest
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.data.model.DiseaseResult
import com.example.farmfusionapp.ui.components.FarmerButton
import com.example.farmfusionapp.ui.theme.FarmColors
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.viewmodel.DiseaseViewModel
import com.example.farmfusionapp.viewmodel.DiseaseViewModel.DiseaseDetectState
import kotlinx.coroutines.delay
import java.io.File
import java.io.FileOutputStream
import java.io.IOException

// ============================================
// SCAN STATES
// ============================================
enum class ScanState {
    IDLE,
    SCANNING,
    RESULT
}

// ============================================
// MAIN DISEASE SCREEN
// ============================================
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiseaseScreen(navController: NavController) {
    val context = LocalContext.current
    val viewModel: DiseaseViewModel = viewModel()
    val detectState = viewModel.detectState.value
    
    var currentState by remember { mutableStateOf(ScanState.IDLE) }
    var capturedImageUri by remember { mutableStateOf<Uri?>(null) }
    
    val currentLang = remember { AuthStore.getLanguage(context) ?: "en" }
    val token = remember { AuthStore.getAuthToken(context) }
    val tempFile = remember { File(context.cacheDir, "disease_scan_temp.jpg") }
    val fileProviderUri = remember { FileProvider.getUriForFile(context, "com.example.farmfusionapp.provider", tempFile) }

    val startAnalysis = {
        currentState = ScanState.SCANNING
        viewModel.detectDisease(
            imageFile = tempFile,
            cropType = null,
            firebaseToken = token,
            responseLanguage = currentLang
        )
    }

    val cameraLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { success ->
        if (success) {
            // Verify file was actually written before proceeding
            if (!tempFile.exists() || tempFile.length() == 0L) {
                android.util.Log.e("DiseaseScreen", "Camera capture failed: photo file not found or empty")
                return@rememberLauncherForActivityResult
            }
            capturedImageUri = fileProviderUri
            startAnalysis()
        } else {
            android.util.Log.d("DiseaseScreen", "Camera capture cancelled by user")
        }
    }

    val galleryLauncher = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { selectedUri ->
        if (selectedUri != null) {
            try {
                copyUriToTempFile(context, selectedUri, tempFile)
                // Verify file was written successfully
                if (!tempFile.exists() || tempFile.length() == 0L) {
                    android.util.Log.e("DiseaseScreen", "Gallery file copy failed: file doesn't exist or is empty")
                    return@rememberLauncherForActivityResult
                }
                capturedImageUri = selectedUri
                startAnalysis()
            } catch (e: Exception) {
                android.util.Log.e("DiseaseScreen", "Error copying gallery file: ${e.message}", e)
            }
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) {
            cameraLauncher.launch(fileProviderUri)
        }
    }

    // Monitor detectState to transition to RESULT
    LaunchedEffect(detectState) {
        if (detectState is DiseaseDetectState.Success) {
            currentState = ScanState.RESULT
        } else if (detectState is DiseaseDetectState.Error) {
            currentState = ScanState.RESULT
        }
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            "Plant Doctor",
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.Bold
                            )
                        )
                        Text(
                            "पौधा डॉक्टर",
                            style = MaterialTheme.typography.bodyMedium.copy(
                                color = MaterialTheme.colorScheme.primary
                            )
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = {
                        when (currentState) {
                            ScanState.RESULT -> {
                                currentState = ScanState.IDLE
                                capturedImageUri = null
                                viewModel.resetDetectState()
                            }
                            else -> navController.popBackStack()
                        }
                    }) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Rounded.ArrowBack,
                            contentDescription = "Back",
                            modifier = Modifier.size(28.dp)
                        )
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background
                )
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 20.dp)
        ) {
            AnimatedContent(
                targetState = currentState,
                transitionSpec = {
                    fadeIn(animationSpec = tween(400)) togetherWith
                    fadeOut(animationSpec = tween(400))
                },
                label = "ScanTransition"
            ) { state ->
                when (state) {
                    ScanState.IDLE -> CameraCaptureStep(
                        onCameraClick = { permissionLauncher.launch(Manifest.permission.CAMERA) },
                        onGalleryClick = { galleryLauncher.launch("image/*") }
                    )
                    ScanState.SCANNING -> ScanningStep()
                    ScanState.RESULT -> {
                        when (detectState) {
                            is DiseaseDetectState.Success -> DiseaseResultStep(
                                result = detectState.response.data,
                                onReset = {
                                    currentState = ScanState.IDLE
                                    capturedImageUri = null
                                    viewModel.resetDetectState()
                                },
                                onCallExpert = { /* Call Doctor */ }
                            )
                            is DiseaseDetectState.Error -> ErrorStep(
                                error = detectState.message,
                                onReset = {
                                    currentState = ScanState.IDLE
                                    capturedImageUri = null
                                    viewModel.resetDetectState()
                                }
                            )
                            else -> ScanningStep()
                        }
                    }
                }
            }
        }
    }
}

// ============================================
// STEP 1: CAMERA CAPTURE
// ============================================
@Composable
fun CameraCaptureStep(onCameraClick: () -> Unit, onGalleryClick: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        // Header
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .background(
                        color = MaterialTheme.colorScheme.primaryContainer,
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Rounded.Biotech,
                    contentDescription = null,
                    modifier = Modifier.size(44.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = "Point camera at the sick leaf",
                style = MaterialTheme.typography.headlineSmall.copy(
                    fontWeight = FontWeight.Bold
                ),
                textAlign = TextAlign.Center
            )

            Text(
                text = "बीमार पत्ते पर कैमरा रखें",
                style = MaterialTheme.typography.titleLarge.copy(
                    color = MaterialTheme.colorScheme.primary
                ),
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(top = 8.dp)
            )
        }

        // Camera Viewfinder
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .padding(vertical = 32.dp)
        ) {
            // Outer frame with corner markers
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .clip(RoundedCornerShape(32.dp))
                    .border(
                        width = 4.dp,
                        color = MaterialTheme.colorScheme.primary.copy(alpha = 0.3f),
                        shape = RoundedCornerShape(32.dp)
                    )
                    .background(
                        color = Color.Black.copy(alpha = 0.03f)
                    ),
                contentAlignment = Alignment.Center
            ) {
                // Corner markers
                CornerMarkers()

                // Center focus icon
                Icon(
                    imageVector = Icons.Rounded.FilterCenterFocus,
                    contentDescription = null,
                    modifier = Modifier.size(100.dp),
                    tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)
                )

                // Helper text
                Text(
                    text = "Keep leaf in frame",
                    style = MaterialTheme.typography.bodyLarge.copy(
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
                    ),
                    modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 24.dp)
                )
            }
        }

        // Capture Buttons
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.fillMaxWidth()
        ) {
            // Camera Button
            Surface(
                onClick = onCameraClick,
                modifier = Modifier.size(120.dp),
                shape = CircleShape,
                color = MaterialTheme.colorScheme.primary,
                tonalElevation = 8.dp
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.Rounded.Camera,
                        contentDescription = "Capture",
                        modifier = Modifier.size(56.dp),
                        tint = Color.White
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "Tap to Scan",
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold
                )
            )

            Text(
                text = "स्कैन करने के लिए दबाएं",
                style = MaterialTheme.typography.bodyLarge.copy(
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Gallery Button
            OutlinedButton(
                onClick = onGalleryClick,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                shape = RoundedCornerShape(16.dp)
            ) {
                Icon(
                    imageVector = Icons.Rounded.Image,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Choose from Gallery")
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Tips
        Surface(
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.secondaryContainer,
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Rounded.Lightbulb,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.secondary,
                    modifier = Modifier.size(28.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = "Tips for best results:",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold
                        )
                    )
                    Text(
                        text = "Good lighting • Clear focus • Close to leaf",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
}

@Composable
fun CornerMarkers() {
    val markerSize = 40.dp
    val strokeWidth = 4.dp
    val color = MaterialTheme.colorScheme.primary

    Box(modifier = Modifier.fillMaxSize()) {
        // Top Left
        Box(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(24.dp)
                .size(markerSize)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(strokeWidth.value / markerSize.value)
                    .fillMaxHeight()
                    .background(color)
                    .align(Alignment.TopStart)
            )
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .fillMaxHeight(strokeWidth.value / markerSize.value)
                    .background(color)
                    .align(Alignment.TopStart)
            )
        }

        // Top Right
        Box(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(24.dp)
                .size(markerSize)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(strokeWidth.value / markerSize.value)
                    .fillMaxHeight()
                    .background(color)
                    .align(Alignment.TopEnd)
            )
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .fillMaxHeight(strokeWidth.value / markerSize.value)
                    .background(color)
                    .align(Alignment.TopStart)
            )
        }

        // Bottom Left
        Box(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(24.dp)
                .size(markerSize)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(strokeWidth.value / markerSize.value)
                    .fillMaxHeight()
                    .background(color)
                    .align(Alignment.TopStart)
            )
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .fillMaxHeight(strokeWidth.value / markerSize.value)
                    .background(color)
                    .align(Alignment.BottomStart)
            )
        }

        // Bottom Right
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(24.dp)
                .size(markerSize)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(strokeWidth.value / markerSize.value)
                    .fillMaxHeight()
                    .background(color)
                    .align(Alignment.TopEnd)
            )
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .fillMaxHeight(strokeWidth.value / markerSize.value)
                    .background(color)
                    .align(Alignment.BottomStart)
            )
        }
    }
}

// ============================================
// STEP 2: SCANNING
// ============================================
@Composable
fun ScanningStep() {
    val infiniteTransition = rememberInfiniteTransition(label = "scanning")

    // Rotating scan animation
    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "rotation"
    )

    // Pulse animation
    val scale by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = EaseInOutCubic),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse"
    )

    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier.size(180.dp),
            contentAlignment = Alignment.Center
        ) {
            // Outer rotating ring
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f),
                        shape = CircleShape
                    )
            )

            // Rotating scan line
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        brush = Brush.sweepGradient(
                            colors = listOf(
                                Color.Transparent,
                                Color.Transparent,
                                MaterialTheme.colorScheme.primary.copy(alpha = 0.3f),
                                Color.Transparent
                            )
                        ),
                        shape = CircleShape
                    )
            )

            // Pulsing center
            Box(
                modifier = Modifier
                    .size(100.dp * scale)
                    .background(
                        color = MaterialTheme.colorScheme.primaryContainer,
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Rounded.Search,
                    contentDescription = null,
                    modifier = Modifier.size(48.dp),
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }

        Spacer(modifier = Modifier.height(40.dp))

        Text(
            text = "Analyzing Leaf...",
            style = MaterialTheme.typography.headlineMedium.copy(
                fontWeight = FontWeight.Bold
            )
        )

        Text(
            text = "पत्ती की जांच जारी है...",
            style = MaterialTheme.typography.titleLarge.copy(
                color = MaterialTheme.colorScheme.primary
            ),
            modifier = Modifier.padding(top = 8.dp)
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Progress indicator
        LinearProgressIndicator(
            modifier = Modifier
                .fillMaxWidth(0.6f)
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp)),
            color = MaterialTheme.colorScheme.primary,
            trackColor = MaterialTheme.colorScheme.primaryContainer
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "Checking for diseases, pests, and nutrient deficiencies",
            style = MaterialTheme.typography.bodyLarge.copy(
                color = MaterialTheme.colorScheme.onSurfaceVariant
            ),
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(horizontal = 32.dp)
        )
    }
}

// ============================================
// STEP 3: DISEASE RESULT
// ============================================
@Composable
fun DiseaseResultStep(
    result: DiseaseResult?,
    onReset: () -> Unit,
    onCallExpert: () -> Unit
) {
    val scrollState = rememberScrollState()
    val context = LocalContext.current

    if (result == null) {
        return
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(scrollState),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Disease detected indicator
        Box(
            modifier = Modifier
                .size(100.dp)
                .background(
                    color = FarmColors.Error.copy(alpha = 0.2f),
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .background(
                        color = FarmColors.Error,
                        shape = CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Rounded.Warning,
                    contentDescription = null,
                    modifier = Modifier.size(44.dp),
                    tint = Color.White
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Disease Detected",
            style = MaterialTheme.typography.titleLarge.copy(
                fontWeight = FontWeight.Bold,
                color = FarmColors.Error
            )
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Image Preview
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .height(220.dp),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                // Placeholder for actual image
                Icon(
                    imageVector = Icons.Rounded.Eco,
                    contentDescription = null,
                    modifier = Modifier.size(100.dp),
                    tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.3f)
                )

                // Disease indicator badge
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(16.dp)
                        .background(
                            color = FarmColors.Error,
                            shape = RoundedCornerShape(12.dp)
                        )
                        .padding(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = "DISEASED",
                        style = MaterialTheme.typography.labelLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Disease Details Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(28.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.errorContainer
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(24.dp)
            ) {
                Text(
                    text = "IDENTIFIED DISEASE",
                    style = MaterialTheme.typography.labelLarge.copy(
                        color = MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.7f)
                    )
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = result?.disease_name?.takeIf { it.isNotBlank() } ?: "Unknown Disease",
                    style = MaterialTheme.typography.headlineMedium.copy(
                        fontWeight = FontWeight.Black,
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                )

                Spacer(modifier = Modifier.height(16.dp))

                HorizontalDivider(
                    color = MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.2f)
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Confidence Tier Badge
                val tier = result?.confidence_tier?.lowercase() ?: "unclear"
                val tierColor = when (tier) {
                    "high" -> FarmColors.Success
                    "medium" -> FarmColors.Warning
                    else -> FarmColors.Error
                }
                val tierLabel = when (tier) {
                    "high" -> "CONFIDENT DIAGNOSIS (${((result?.confidence ?: 0.0) * 100).toInt()}%)"
                    "medium" -> "POSSIBLE DIAGNOSIS (${((result?.confidence ?: 0.0) * 100).toInt()}%) — CONFIRM WITH EXPERT"
                    "low" -> "LOW CONFIDENCE (${((result?.confidence ?: 0.0) * 100).toInt()}%)"
                    else -> "UNCERTAIN IMAGE QUALITY"
                }

                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = tierColor
                ) {
                    Text(
                        text = tierLabel,
                        style = MaterialTheme.typography.labelLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        ),
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp)
                    )
                }

                if (!result?.scientific_name.isNullOrBlank() && result?.scientific_name != "N/A" && result?.scientific_name != "NOT_AVAILABLE") {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Pathogen: ${result.scientific_name}",
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.8f),
                            fontWeight = FontWeight.Medium
                        )
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Symptoms Card
        if (!result?.symptoms.isNullOrEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(
                    modifier = Modifier.padding(24.dp)
                ) {
                    Text(
                        text = "Key Symptoms / लक्षण",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold
                        )
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    result.symptoms.forEach { symptom ->
                        Row(modifier = Modifier.padding(vertical = 4.dp), verticalAlignment = Alignment.Top) {
                            Text("• ", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                            Text(text = symptom, style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }
            }
            Spacer(modifier = Modifier.height(20.dp))
        }

        // Description
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp)
            ) {
                Text(
                    text = "Description",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold
                    )
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = result?.description ?: "No description available",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Treatment Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(28.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .background(
                                color = MaterialTheme.colorScheme.primary,
                                shape = CircleShape
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Rounded.Medication,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "Treatment / इलाज",
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Treatment suggestions
                if (!result.treatment_suggestions.isNullOrEmpty()) {
                    result.treatment_suggestions.forEachIndexed { index, treatment ->
                        TreatmentStep(
                            number = index + 1,
                            text = treatment,
                            hindiText = ""
                        )
                    }
                } else {
                    Text(
                        text = "Consult a farming expert for detailed treatment plan",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Prevention Tips
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.tertiaryContainer
            )
        ) {
            Row(
                modifier = Modifier.padding(20.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Rounded.HealthAndSafety,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.tertiary,
                    modifier = Modifier.size(32.dp)
                )
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(
                        text = "Prevention",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold
                        )
                    )
                    Text(
                        text = if (!result.prevention_tips.isNullOrEmpty())
                            result.prevention_tips[0]
                        else
                            "Follow recommended farming practices",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }

        // Recommended Products Card (Amazon Affiliate)
        if (!result.store_recommendations.isNullOrEmpty()) {
            Spacer(modifier = Modifier.height(20.dp))
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.6f)
                )
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Rounded.ShoppingCart,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.secondary,
                            modifier = Modifier.size(28.dp)
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            text = "Recommended Products / अनुशंसित उत्पाद",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onSecondaryContainer
                            )
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    result.store_recommendations.forEach { item ->
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 6.dp),
                            shape = RoundedCornerShape(16.dp),
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surface
                            )
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(14.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = item.title,
                                        style = MaterialTheme.typography.bodyLarge.copy(
                                            fontWeight = FontWeight.Bold
                                        )
                                    )
                                    if (item.subtitle.isNotBlank()) {
                                        Text(
                                            text = item.subtitle,
                                            style = MaterialTheme.typography.bodySmall.copy(
                                                color = MaterialTheme.colorScheme.onSurfaceVariant
                                            )
                                        )
                                    }
                                }
                                Spacer(modifier = Modifier.width(8.dp))
                                Button(
                                    onClick = {
                                        try {
                                            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(item.shop_url))
                                            context.startActivity(intent)
                                        } catch (e: Exception) {
                                            android.util.Log.e("DiseaseScreen", "Error opening shop URL: ${e.message}")
                                        }
                                    },
                                    shape = RoundedCornerShape(12.dp),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = MaterialTheme.colorScheme.primary
                                    ),
                                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                                ) {
                                    Text("Buy", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                                }
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Action Buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedButton(
                onClick = onReset,
                modifier = Modifier
                    .weight(1f)
                    .height(64.dp),
                shape = RoundedCornerShape(20.dp)
            ) {
                Icon(Icons.Rounded.Refresh, null, modifier = Modifier.size(24.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "SCAN AGAIN",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold
                    )
                )
            }

            Button(
                onClick = onCallExpert,
                modifier = Modifier
                    .weight(1f)
                    .height(64.dp),
                shape = RoundedCornerShape(20.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = FarmColors.Success
                )
            ) {
                Icon(Icons.Rounded.Call, null, modifier = Modifier.size(24.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "CALL EXPERT",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(80.dp))
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
private fun copyUriToTempFile(context: Context, uri: Uri, targetFile: File) {
    try {
        // Delete old file if it exists
        if (targetFile.exists()) {
            targetFile.delete()
        }
        
        // Open input stream and copy
        context.contentResolver.openInputStream(uri)?.use { input ->
            FileOutputStream(targetFile).use { output ->
                val buffer = ByteArray(8192)
                var bytesRead: Int
                while (input.read(buffer).also { bytesRead = it } != -1) {
                    output.write(buffer, 0, bytesRead)
                }
                // Ensure all data is written to disk
                output.flush()
            }
        } ?: throw IOException("Failed to open input stream for URI: $uri")
        
        // Verify file was written
        if (!targetFile.exists() || targetFile.length() == 0L) {
            throw IOException("File copy resulted in empty or missing file")
        }
        
        android.util.Log.d("DiseaseScreen", "Successfully copied file to ${targetFile.absolutePath} (${targetFile.length()} bytes)")
    } catch (e: Exception) {
        android.util.Log.e("DiseaseScreen", "Error copying file: ${e.message}", e)
        throw e
    }
}

@Composable
fun ErrorStep(error: String, onReset: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 20.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = Icons.Rounded.ErrorOutline,
            contentDescription = null,
            modifier = Modifier.size(100.dp),
            tint = FarmColors.Error
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Error",
            style = MaterialTheme.typography.headlineSmall.copy(
                fontWeight = FontWeight.Bold,
                color = FarmColors.Error
            )
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = error,
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(
            onClick = onReset,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            shape = RoundedCornerShape(20.dp)
        ) {
            Text("Try Again")
        }
    }
}

@Composable
fun TreatmentStep(number: Int, text: String, hindiText: String) {
    Row(
        modifier = Modifier.padding(vertical = 8.dp),
        verticalAlignment = Alignment.Top
    ) {
        Box(
            modifier = Modifier
                .size(32.dp)
                .background(
                    color = MaterialTheme.colorScheme.primary,
                    shape = CircleShape
                ),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = number.toString(),
                style = MaterialTheme.typography.titleMedium.copy(
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            )
        }
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Text(
                text = text,
                style = MaterialTheme.typography.bodyLarge.copy(
                    fontWeight = FontWeight.Medium
                )
            )
            Text(
                text = hindiText,
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            )
        }
    }
}
