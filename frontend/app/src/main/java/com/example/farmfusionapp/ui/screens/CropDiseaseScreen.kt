package com.example.farmfusionapp.ui.screens

import android.Manifest
import android.content.Context
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.rememberAsyncImagePainter
import com.example.farmfusionapp.data.model.DiseaseResult
import com.example.farmfusionapp.utils.*
import com.example.farmfusionapp.viewmodel.DiseaseViewModel
import java.io.File
import java.io.FileOutputStream

// Premium Color Tokens
private val CropDashBg = Color(0xFFF9FAFB)
private val CropCardBg = Color(0xFFFFFFFF)
private val CropPrimaryDark = Color(0xFF1B5E20)
private val CropSuccessGreen = Color(0xFF059669)
private val CropErrorRed = Color(0xFFDC2626)
private val CropWarningOrange = Color(0xFFD97706)
private val CropTextMain = Color(0xFF111827)
private val CropTextSub = Color(0xFF6B7280)

private enum class DiseaseScreenState { IDLE, SCANNING, RESULT }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropDiseaseScreen(navController: NavController) {
    val context = LocalContext.current
    val diseaseViewModel: DiseaseViewModel = viewModel()
    var state by remember { mutableStateOf(DiseaseScreenState.IDLE) }
    var capturedImageUri by remember { mutableStateOf<Uri?>(null) }

    val tempFile = remember { File(context.cacheDir, "camera_image_temp.jpg") }
    val uri = remember { FileProvider.getUriForFile(context, "com.example.farmfusionapp.provider", tempFile) }

    val cameraLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { success ->
        if (success) {
            capturedImageUri = uri
            state = DiseaseScreenState.SCANNING
            diseaseViewModel.detectDisease(imageFile = tempFile, cropType = null)
        }
    }

    val galleryLauncher = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { selectedUri ->
        if (selectedUri != null) {
            copyUriToTempFile(context, selectedUri, tempFile)
            capturedImageUri = selectedUri
            state = DiseaseScreenState.SCANNING
            diseaseViewModel.detectDisease(imageFile = tempFile, cropType = null)
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) cameraLauncher.launch(uri)
    }

    val detectState by diseaseViewModel.detectState

    LaunchedEffect(detectState) {
        if (detectState is DiseaseViewModel.DiseaseDetectState.Success) {
            state = DiseaseScreenState.RESULT
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        CenterAlignedTopAppBar(
            title = { Text("AI Plant Scan", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.ExtraBold, color = CropPrimaryDark)) },
            navigationIcon = {
                IconButton(onClick = {
                    if (state == DiseaseScreenState.RESULT) {
                        state = DiseaseScreenState.IDLE
                        diseaseViewModel.resetDetectState()
                    } else {
                        navController.popBackStack()
                    }
                }) {
                    Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", tint = CropTextMain)
                }
            },
            colors = TopAppBarDefaults.centerAlignedTopAppBarColors(containerColor = CropDashBg)
        )
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(18.dp)
        ) {
            when (state) {
                DiseaseScreenState.IDLE -> UploadPanel(
                    onCapture = { permissionLauncher.launch(Manifest.permission.CAMERA) },
                    onGallery = { galleryLauncher.launch("image/*") }
                )
                DiseaseScreenState.SCANNING -> ScanningPanel(imageUri = capturedImageUri)
                DiseaseScreenState.RESULT -> {
                    val response = (detectState as? DiseaseViewModel.DiseaseDetectState.Success)?.response
                    ResultPanel(
                        imageUri = capturedImageUri,
                        result = response?.data,
                        onScanAgain = {
                            state = DiseaseScreenState.IDLE
                            capturedImageUri = null
                            diseaseViewModel.resetDetectState()
                        },
                        onShopForTreatment = {
                            AgriStoreContext.setForDisease(
                                response?.data?.disease_name.orEmpty(),
                                response?.data?.crop_type
                            )
                            navController.navigate(NavRoutes.ProductStore)
                        }
                    )
                }
            }
        }

        if (detectState is DiseaseViewModel.DiseaseDetectState.Error) {
            val errorMessage = (detectState as DiseaseViewModel.DiseaseDetectState.Error).message
            AlertDialog(
                containerColor = CropCardBg,
                onDismissRequest = {
                    diseaseViewModel.resetDetectState()
                    state = DiseaseScreenState.IDLE
                },
                title = { Text("Scanner Error", color = CropErrorRed, fontWeight = FontWeight.Bold) },
                text = { Text(errorMessage, color = CropTextMain) },
                confirmButton = {
                    Button(
                        onClick = {
                            diseaseViewModel.resetDetectState()
                            state = DiseaseScreenState.IDLE
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = CropPrimaryDark)
                    ) { Text("Try Again") }
                }
            )
        }
    }
}

@Composable
private fun UploadPanel(onCapture: () -> Unit, onGallery: () -> Unit) {
    Column(modifier = Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(24.dp)) {
        Surface(shape = RoundedCornerShape(24.dp), color = CropCardBg, shadowElevation = 4.dp, modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(24.dp)) {
                Box(modifier = Modifier.size(56.dp).background(Color(0xFFE8F5E9), CircleShape), contentAlignment = Alignment.Center) {
                    Icon(Icons.Rounded.EnergySavingsLeaf, null, tint = CropPrimaryDark, modifier = Modifier.size(28.dp))
                }
                Spacer(modifier = Modifier.height(16.dp))
                Text("Detect crop diseases instantly with AI", fontSize = 22.sp, fontWeight = FontWeight.ExtraBold, color = CropTextMain, lineHeight = 28.sp)
                Spacer(modifier = Modifier.height(12.dp))
                Text("Take a clear picture of a leaf or plant showing signs of illness. Our AI will analyze patterns to give you an immediate diagnosis.", fontSize = 14.sp, color = CropTextSub, lineHeight = 22.sp)
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Surface(shape = RoundedCornerShape(20.dp), color = CropCardBg, shadowElevation = 2.dp, border = BorderStroke(2.dp, CropPrimaryDark), modifier = Modifier.weight(1f).clickable { onCapture() }) {
                Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(Icons.Rounded.CameraAlt, null, tint = CropPrimaryDark, modifier = Modifier.size(32.dp))
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Take Photo", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = CropPrimaryDark)
                }
            }
            Surface(shape = RoundedCornerShape(20.dp), color = CropDashBg, border = BorderStroke(1.dp, Color(0xFFD1D5DB)), modifier = Modifier.weight(1f).clickable { onGallery() }) {
                Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(Icons.Rounded.PhotoLibrary, null, tint = CropTextSub, modifier = Modifier.size(32.dp))
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Gallery", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = CropTextSub)
                }
            }
        }
    }
}

@Composable
private fun ScanningPanel(imageUri: Uri?) {
    Column(modifier = Modifier.padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Surface(shape = RoundedCornerShape(24.dp), shadowElevation = 12.dp, modifier = Modifier.fillMaxWidth().height(400.dp)) {
            Box {
                if (imageUri != null) Image(painter = rememberAsyncImagePainter(imageUri), contentDescription = "Scanning", contentScale = ContentScale.Crop, modifier = Modifier.fillMaxSize())
                Box(modifier = Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f)))
                Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                    CircularProgressIndicator(color = Color.White, strokeWidth = 4.dp, modifier = Modifier.size(64.dp))
                    Spacer(modifier = Modifier.height(24.dp))
                    Text("Analyzing biology...", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color.White)
                }
            }
        }
    }
}

@Composable
private fun ResultPanel(imageUri: Uri?, result: DiseaseResult?, onScanAgain: () -> Unit, onShopForTreatment: () -> Unit) {
    val invalid = result?.is_plant_image == false || result?.can_analyze == false
    val healthy = result?.disease_name?.contains("Healthy", ignoreCase = true) == true
    Column(modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp, vertical = 12.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(bottom = 24.dp)) {
            Surface(shape = RoundedCornerShape(12.dp), color = CropDashBg, modifier = Modifier.size(72.dp).border(1.dp, Color(0xFFE5E7EB), RoundedCornerShape(12.dp))) {
                if(imageUri != null) Image(painter = rememberAsyncImagePainter(imageUri), contentDescription = null, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxSize())
            }
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text("SCAN SUCCESSFUL", fontSize = 10.sp, fontWeight = FontWeight.ExtraBold, color = CropTextSub, letterSpacing = 1.sp)
                Text("Diagnosis Ready", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = CropTextMain)
            }
        }
        Surface(shape = RoundedCornerShape(24.dp), color = CropCardBg, shadowElevation = 6.dp, modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(24.dp)) {
                when {
                    invalid -> {
                        Icon(Icons.Rounded.Error, null, tint = CropWarningOrange, modifier = Modifier.size(48.dp))
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Not a valid plant", fontSize = 22.sp, fontWeight = FontWeight.ExtraBold, color = CropTextMain)
                        Text(result?.invalid_image_reason ?: "We could not identify a clear leaf. Please retry with better lighting.", fontSize = 15.sp, color = CropTextSub, lineHeight = 22.sp)
                    }
                    healthy -> {
                        Icon(Icons.Rounded.CheckCircle, null, tint = CropSuccessGreen, modifier = Modifier.size(48.dp))
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Crop looks healthy!", fontSize = 22.sp, fontWeight = FontWeight.ExtraBold, color = CropSuccessGreen)
                    }
                    else -> {
                        Surface(color = CropErrorRed.copy(alpha = 0.1f), shape = CircleShape) {
                            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)) {
                                Icon(Icons.Rounded.WarningAmber, null, tint = CropErrorRed, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("DISEASE DETECTED", fontSize = 11.sp, fontWeight = FontWeight.ExtraBold, color = CropErrorRed)
                            }
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(result?.disease_name ?: "Unknown Pathogen", fontSize = 24.sp, fontWeight = FontWeight.Black, color = CropTextMain)
                        Text(result?.description ?: "No description provided.", fontSize = 15.sp, color = CropTextSub, lineHeight = 22.sp)
                        if (!result?.treatment_suggestions.isNullOrEmpty()) {
                            Spacer(modifier = Modifier.height(24.dp)); HorizontalDivider(); Spacer(modifier = Modifier.height(16.dp))
                            Text("Recommended Treatment", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = CropPrimaryDark)
                            result?.treatment_suggestions?.forEach { tip ->
                                Row(modifier = Modifier.padding(vertical = 4.dp), verticalAlignment = Alignment.Top) {
                                    Icon(Icons.Rounded.PlayArrow, null, tint = CropPrimaryDark, modifier = Modifier.size(14.dp).padding(top = 4.dp))
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(tip, fontSize = 14.sp, color = CropTextMain, lineHeight = 20.sp)
                                }
                            }
                        }
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(32.dp))
        if (!invalid && !healthy) {
            OutlinedButton(onClick = onShopForTreatment, modifier = Modifier.fillMaxWidth().height(52.dp), shape = RoundedCornerShape(16.dp), colors = ButtonDefaults.outlinedButtonColors(contentColor = CropPrimaryDark), border = BorderStroke(1.5.dp, CropPrimaryDark)) {
                Icon(Icons.Rounded.Storefront, null, modifier = Modifier.size(20.dp)); Spacer(Modifier.width(8.dp)); Text("Find treatment & supplies", fontSize = 15.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(12.dp))
        }
        Button(onClick = onScanAgain, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = CropPrimaryDark), shape = RoundedCornerShape(16.dp)) {
            Text("Scan Another Plant", fontSize = 16.sp, fontWeight = FontWeight.Bold)
        }
        Spacer(modifier = Modifier.height(40.dp))
    }
}

private fun copyUriToTempFile(context: Context, uri: Uri, targetFile: File) {
    context.contentResolver.openInputStream(uri)?.use { input ->
        FileOutputStream(targetFile).use { output ->
            input.copyTo(output)
        }
    }
}
