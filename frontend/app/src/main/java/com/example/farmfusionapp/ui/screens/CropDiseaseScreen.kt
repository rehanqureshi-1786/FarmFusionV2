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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.AsyncImage
import coil.compose.rememberAsyncImagePainter
import kotlinx.coroutines.launch
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
    val currentLang = remember { AuthStore.getLanguage(context) ?: "en" }
    val token = remember { AuthStore.getAuthToken(context) }

    val tempFile = remember { File(context.cacheDir, "disease_scan_temp.jpg") }
    val fileProviderUri = remember { FileProvider.getUriForFile(context, "com.example.farmfusionapp.provider", tempFile) }

    val startAnalysis = {
        state = DiseaseScreenState.SCANNING
        diseaseViewModel.detectDisease(
            imageFile = tempFile,
            cropType = null,
            firebaseToken = token,
            responseLanguage = currentLang
        )
    }

    val cameraLauncher = rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { success ->
        if (success) {
            capturedImageUri = fileProviderUri
            startAnalysis()
        }
    }

    val galleryLauncher = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { selectedUri ->
        if (selectedUri != null) {
            scope.launch(kotlinx.coroutines.Dispatchers.IO) {
                try {
                    val success = copyUriToTempFile(context, selectedUri, tempFile)
                    if (success) {
                        kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                            capturedImageUri = selectedUri
                            startAnalysis()
                        }
                    }
                } catch (e: Exception) {
                    android.util.Log.e("CropDisease", "Error copying file: ${e.message}")
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

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Plant Doctor AI", fontWeight = FontWeight.ExtraBold, color = CropPrimaryDark) },
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
        NeoScaffoldBackground(modifier = Modifier.fillMaxSize().padding(padding)) {
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

@Composable
private fun UploadPanel(onCapture: () -> Unit, onGallery: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        NeoCard {
            Column(modifier = Modifier.padding(8.dp)) {
                Box(modifier = Modifier.size(56.dp).background(Color(0xFFE8F5E9), CircleShape), contentAlignment = Alignment.Center) {
                    Icon(Icons.Rounded.AutoAwesome, null, tint = CropPrimaryDark)
                }
                Spacer(Modifier.height(16.dp))
                Text("Scan Your Crop", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
                Text("Identify pests and diseases instantly with AI biology analysis.", color = Color.Gray)
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Surface(
                onClick = onCapture,
                modifier = Modifier.weight(1f).height(120.dp),
                shape = RoundedCornerShape(24.dp),
                color = Color.White,
                border = BorderStroke(2.dp, CropPrimaryDark),
                shadowElevation = 2.dp
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                    Icon(Icons.Rounded.CameraAlt, null, tint = CropPrimaryDark, modifier = Modifier.size(32.dp))
                    Spacer(Modifier.height(8.dp))
                    Text("Camera", fontWeight = FontWeight.Bold)
                }
            }
            Surface(
                onClick = onGallery,
                modifier = Modifier.weight(1f).height(120.dp),
                shape = RoundedCornerShape(24.dp),
                color = Color.White,
                border = BorderStroke(1.dp, Color(0xFFEEEEEE)),
                shadowElevation = 2.dp
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                    Icon(Icons.Rounded.PhotoLibrary, null, tint = Color.Gray, modifier = Modifier.size(32.dp))
                    Spacer(Modifier.height(8.dp))
                    Text("Gallery", fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
private fun ScanningPanel(imageUri: Uri?, onCancel: () -> Unit) {
    Column(modifier = Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Surface(shape = RoundedCornerShape(32.dp), modifier = Modifier.size(280.dp).shadow(20.dp)) {
            Box {
                if (imageUri != null) Image(painter = rememberAsyncImagePainter(imageUri), contentDescription = null, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxSize())
                Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.4f)))
                CircularProgressIndicator(color = Color.White, modifier = Modifier.align(Alignment.Center).size(60.dp), strokeWidth = 4.dp)
            }
        }
        Spacer(Modifier.height(32.dp))
        Text("AI is analyzing...", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
        Text("Checking leaf patterns and cell damage.", color = Color.Gray)
        Spacer(Modifier.height(24.dp))
        TextButton(onClick = onCancel) { Text("Cancel Upload", color = CropErrorRed) }
    }
}

@Composable
private fun ResultPanel(imageUri: Uri?, result: DiseaseResult?, onScanAgain: () -> Unit) {
    val scrollState = rememberScrollState()
    val context = LocalContext.current

    if (result == null || result.ai_analyzed == false) {
        Column(Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
            Icon(Icons.Rounded.SentimentDissatisfied, null, modifier = Modifier.size(80.dp), tint = Color.Gray)
            Text("Analysis Failed", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
            Text(result?.invalid_image_reason ?: "The AI could not identify a clear plant in this image.", textAlign = TextAlign.Center, color = Color.Gray)
            Spacer(Modifier.height(24.dp))
            PremiumButton(text = "Try Again", onClick = onScanAgain)
        }
        return
    }

    val diseaseName = result.disease_name ?: "Unknown Disease"
    val severity = result.severity ?: "unknown"
    val description = result.description ?: ""
    val treatmentSuggestions = result.treatment_suggestions ?: emptyList()
    val preventionTips = result.prevention_tips ?: emptyList()

    Column(modifier = Modifier.fillMaxSize().verticalScroll(scrollState).padding(20.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Surface(shape = RoundedCornerShape(28.dp), modifier = Modifier.fillMaxWidth().height(200.dp).shadow(8.dp)) {
            Box {
                if (imageUri != null) Image(painter = rememberAsyncImagePainter(imageUri), contentDescription = null, contentScale = ContentScale.Crop, modifier = Modifier.fillMaxSize())
                Surface(color = CropErrorRed, shape = RoundedCornerShape(12.dp), modifier = Modifier.padding(16.dp).align(Alignment.TopEnd)) {
                    Text("DISEASED", modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp), color = Color.White, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        NeoCard {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = diseaseName,
                        style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Black, color = Color(0xFF1B1B1B))
                    )
                }

                val sevColor = when (severity.lowercase()) {
                    "low" -> CropSuccessGreen
                    "moderate" -> CropWarningOrange
                    else -> CropErrorRed
                }
                Surface(color = sevColor.copy(alpha = 0.1f), border = BorderStroke(1.dp, sevColor), shape = RoundedCornerShape(8.dp)) {
                    Text(severity.uppercase(), modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp), color = sevColor, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }

                var expanded by remember { mutableStateOf(false) }
                Text(
                    text = description,
                    maxLines = if (expanded) Int.MAX_VALUE else 3,
                    overflow = TextOverflow.Ellipsis,
                    style = MaterialTheme.typography.bodyMedium.copy(lineHeight = 20.sp),
                    modifier = Modifier.clickable { expanded = !expanded }
                )
                Text(if (expanded) "Show Less" else "Read More", color = CropPrimaryDark, fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
        }

        NeoSectionTitle("Recommended Care", "Scientific steps for recovery")
        NeoCard {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Treatment Steps", fontWeight = FontWeight.Bold, color = CropPrimaryDark)
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

                Text("Prevention Tips", fontWeight = FontWeight.Bold, color = CropPrimaryDark)
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

        if (!result.store_recommendations.isNullOrEmpty()) {
            NeoSectionTitle("Buy Treatment", "Amazon affiliate picks for $diseaseName")
            LazyRow(horizontalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 12.dp)) {
                items(result.store_recommendations) { item ->
                    StoreMiniCard(item) {
                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(item.shop_url))
                        context.startActivity(intent)
                    }
                }
            }
        }

        PremiumButton(text = "Scan Another Plant", onClick = onScanAgain, icon = Icons.Rounded.Refresh)
        Spacer(Modifier.height(40.dp))
    }
}

@Composable
fun StoreMiniCard(item: StoreRecommendationItem, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        modifier = Modifier.width(160.dp).shadow(4.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        color = Color.White
    ) {
        Column {
            Box(Modifier.fillMaxWidth().height(100.dp).background(Color(0xFFF5F5F5))) {
                AsyncImage(model = item.image_url, contentDescription = null, modifier = Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
            }
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(item.title, fontWeight = FontWeight.Bold, maxLines = 1, overflow = TextOverflow.Ellipsis, fontSize = 13.sp)
                Text(item.subtitle, color = Color.Gray, fontSize = 11.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Buy Now", fontWeight = FontWeight.ExtraBold, color = CropPrimaryDark, fontSize = 12.sp)
                    Spacer(Modifier.width(4.dp))
                    Icon(Icons.AutoMirrored.Rounded.OpenInNew, null, modifier = Modifier.size(12.dp), tint = CropPrimaryDark)
                }
            }
        }
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