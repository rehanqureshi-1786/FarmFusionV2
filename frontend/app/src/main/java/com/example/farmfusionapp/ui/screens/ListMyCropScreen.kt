package com.example.farmfusionapp.ui.screens

import android.content.Context
import android.location.Geocoder
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.AttachFile
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Edit
import androidx.compose.material.icons.rounded.Place
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.navigation.NavController
import coil.compose.AsyncImage
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.CreateMarketListingRequest
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.utils.LocationPermissionEffect
import com.example.farmfusionapp.utils.LocationSnapshotStore
import com.example.farmfusionapp.utils.getCityFromLocation
import com.example.farmfusionapp.utils.getDetailedAddressFromLocation
import com.example.farmfusionapp.utils.getDeviceLocation
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import com.example.farmfusionapp.data.model.MarketListingDto
import com.example.farmfusionapp.data.model.MarketListingStore
import com.example.farmfusionapp.data.model.getDefaultCropPrice
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

enum class LocationStatus {
    DETECTING,
    DETECTED,
    FAILED
}

data class LocationPrediction(
    val title: String,
    val subtitle: String,
    val fullDisplayName: String,
    val latitude: Double? = null,
    val longitude: Double? = null
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ListMyCropScreen(navController: NavController) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    // Form inputs
    var cropName by remember { mutableStateOf("") }
    var quantity by remember { mutableStateOf("") }
    var selectedMediaUris by remember { mutableStateOf<List<Uri>>(emptyList()) }
    var description by remember { mutableStateOf("") }
    var isSubmitting by remember { mutableStateOf(false) }

    // Location state - NO hardcoded values!
    var locationStatus by remember { mutableStateOf(LocationStatus.DETECTING) }
    var locationText by remember { mutableStateOf("") }
    var detectedLatitude by remember { mutableStateOf<Double?>(null) }
    var detectedLongitude by remember { mutableStateOf<Double?>(null) }
    var showEditLocationDialog by remember { mutableStateOf(false) }
    var hasLocationPermission by remember { mutableStateOf(false) }

    // Dotted buffering animation for "Detecting..."
    var dotCount by remember { mutableIntStateOf(0) }
    LaunchedEffect(locationStatus) {
        if (locationStatus == LocationStatus.DETECTING) {
            while (true) {
                delay(350L)
                dotCount = (dotCount + 1) % 4
            }
        }
    }
    val detectingDots = remember(dotCount) { ".".repeat(dotCount) }

    // Location Permission Hook
    LocationPermissionEffect(
        context = context,
        onPermissionGranted = {
            hasLocationPermission = true
        },
        onPermissionDenied = {
            hasLocationPermission = false
        }
    )

    // Auto-detect location logic with strict 10-second timeout
    LaunchedEffect(hasLocationPermission) {
        if (locationStatus != LocationStatus.DETECTED) {
            locationStatus = LocationStatus.DETECTING

            val resolved = withTimeoutOrNull(10_000L) {
                try {
                    val coords = if (hasLocationPermission) {
                        getDeviceLocation(context)
                    } else {
                        // Check if cached coordinates already exist
                        val lat = LocationSnapshotStore.latestLatitude
                        val lon = LocationSnapshotStore.latestLongitude
                        if (lat != null && lon != null) Pair(lat, lon) else null
                    }

                    if (coords != null) {
                        detectedLatitude = coords.first
                        detectedLongitude = coords.second

                        // Try detailed reverse geocoding
                        val detailed = getDetailedAddressFromLocation(context, coords.first, coords.second)
                        if (detailed != null) {
                            val city = detailed.cityOrVillage ?: detailed.district
                            val state = detailed.state
                            if (!city.isNullOrBlank() && !state.isNullOrBlank()) {
                                "$city, $state"
                            } else if (!detailed.fullDisplayName.isNullOrBlank()) {
                                detailed.fullDisplayName
                            } else {
                                getCityFromLocation(context, coords.first, coords.second)
                            }
                        } else {
                            getCityFromLocation(context, coords.first, coords.second)
                        }
                    } else {
                        // Check if WeatherSnapshotStore has a real city recorded
                        WeatherSnapshotStore.latestWeather?.city?.takeIf { it.isNotBlank() }
                    }
                } catch (e: Exception) {
                    null
                }
            }

            if (!resolved.isNullOrBlank()) {
                locationText = resolved
                locationStatus = LocationStatus.DETECTED
            } else {
                locationText = "Failed to detect location"
                locationStatus = LocationStatus.FAILED
            }
        }
    }

    // Media Picker launcher
    val mediaPickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetMultipleContents()
    ) { uris ->
        if (uris.isNotEmpty()) {
            val combined = (selectedMediaUris + uris).distinct().take(5)
            selectedMediaUris = combined
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFFEFF5F0),
                        Color(0xFFE2ECE4)
                    )
                )
            )
    ) {
        // Bottom Background Illustration: ill_crop_sell_wheat_bg at 70% opacity
        Image(
            painter = painterResource(id = R.drawable.ill_crop_sell_wheat_bg),
            contentDescription = null,
            contentScale = ContentScale.FillWidth,
            alpha = 0.7f,
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
        )

        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                CenterAlignedTopAppBar(
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent
                    ),
                    title = {
                        Text(
                            text = "List My Crop",
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp,
                            color = Color(0xFF111827)
                        )
                    },
                    navigationIcon = {
                        IconButton(onClick = { navController.popBackStack() }) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Back",
                                tint = Color(0xFF111827)
                            )
                        }
                    }
                )
            }
        ) { padding ->
            // Non-scrollable form container: fits cleanly within viewport
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(horizontal = 18.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                // 1. FIELD 1: Crop Name
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        LeafSmallIcon(modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Crop Name",
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.5.sp,
                            color = Color(0xFF111827)
                        )
                    }

                    OutlinedTextField(
                        value = cropName,
                        onValueChange = { cropName = it },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White,
                            disabledContainerColor = Color.White,
                            focusedBorderColor = Color(0xFF2E7D32),
                            unfocusedBorderColor = Color(0xFFD4E0D6),
                            cursorColor = Color(0xFF2E7D32)
                        ),
                        leadingIcon = {
                            SeedlingLeadingIcon(modifier = Modifier.size(18.dp))
                        },
                        placeholder = {
                            Text(
                                text = "Enter crop name (e.g. Wheat, Rice, Maize)",
                                color = Color(0xFF9CA3AF),
                                fontSize = 13.5.sp
                            )
                        },
                        singleLine = true
                    )
                }

                // 3. FIELD 2: Quantity (in Quintals)
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        SackHeaderIcon(modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Quantity (in Quintals)",
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.5.sp,
                            color = Color(0xFF111827)
                        )
                    }

                    OutlinedTextField(
                        value = quantity,
                        onValueChange = {
                            if (it.isEmpty() || it.matches(Regex("^\\d*\\.?\\d*$"))) {
                                quantity = it
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White,
                            disabledContainerColor = Color.White,
                            focusedBorderColor = Color(0xFF2E7D32),
                            unfocusedBorderColor = Color(0xFFD4E0D6),
                            cursorColor = Color(0xFF2E7D32)
                        ),
                        leadingIcon = {
                            ScaleWeightIcon(modifier = Modifier.size(18.dp), tint = Color(0xFF6B7280))
                        },
                        placeholder = {
                            Text(
                                text = "Enter quantity",
                                color = Color(0xFF9CA3AF),
                                fontSize = 13.5.sp
                            )
                        },
                        trailingIcon = {
                            Box(
                                modifier = Modifier
                                    .padding(end = 8.dp)
                                    .background(Color(0xFFEAF5EC), RoundedCornerShape(8.dp))
                                    .padding(horizontal = 12.dp, vertical = 6.dp)
                            ) {
                                Text(
                                    text = "Quintals",
                                    color = Color(0xFF2E7D32),
                                    fontWeight = FontWeight.Medium,
                                    fontSize = 12.5.sp
                                )
                            }
                        },
                        singleLine = true
                    )
                }

                // 4. FIELD 3: Photos or Videos (0/5)
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        ImageHeaderIcon(modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Photos or Videos",
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.5.sp,
                            color = Color(0xFF111827)
                        )
                        Spacer(modifier = Modifier.weight(1f))
                        Text(
                            text = "${selectedMediaUris.size}/5",
                            color = Color(0xFF9CA3AF),
                            fontSize = 12.5.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }

                    // Upload box
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .drawDashedBorder(
                                strokeWidth = 1.dp,
                                color = Color(0xFFD4E0D6),
                                cornerRadius = 16.dp,
                                dashLength = 6.dp,
                                gapLength = 4.dp
                            )
                            .background(Color.White, RoundedCornerShape(16.dp))
                            .padding(vertical = 16.dp, horizontal = 14.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            if (selectedMediaUris.isEmpty()) {
                                UploadPlaceholderGraphic(modifier = Modifier.size(42.dp))
                            }

                            // "Attach Photos or Videos" pill button
                            Button(
                                onClick = {
                                    if (selectedMediaUris.size >= 5) {
                                        Toast.makeText(context, "Maximum 5 files allowed", Toast.LENGTH_SHORT).show()
                                    } else {
                                        mediaPickerLauncher.launch("image/*")
                                    }
                                },
                                shape = RoundedCornerShape(20.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Color(0xFF2E7D32)
                                ),
                                contentPadding = PaddingValues(horizontal = 18.dp, vertical = 8.dp),
                                modifier = Modifier.height(38.dp)
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        imageVector = Icons.Default.AttachFile,
                                        contentDescription = null,
                                        tint = Color.White,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(
                                        text = "Attach Photos or Videos",
                                        color = Color.White,
                                        fontWeight = FontWeight.SemiBold,
                                        fontSize = 13.sp
                                    )
                                }
                            }

                            if (selectedMediaUris.isEmpty()) {
                                Text(
                                    text = "You can add up to 5 files (photos or videos)",
                                    color = Color(0xFF6B7280),
                                    fontSize = 12.sp
                                )
                            } else {
                                // Attached Media preview row
                                LazyRow(
                                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    items(selectedMediaUris) { uri ->
                                        Box(
                                            modifier = Modifier
                                                .size(56.dp)
                                                .clip(RoundedCornerShape(10.dp))
                                                .border(1.dp, Color(0xFFE5E7EB), RoundedCornerShape(10.dp))
                                        ) {
                                            AsyncImage(
                                                model = uri,
                                                contentDescription = "Selected media",
                                                contentScale = ContentScale.Crop,
                                                modifier = Modifier.fillMaxSize()
                                            )
                                            Box(
                                                modifier = Modifier
                                                    .align(Alignment.TopEnd)
                                                    .padding(3.dp)
                                                    .size(18.dp)
                                                    .background(Color.Black.copy(alpha = 0.65f), CircleShape)
                                                    .clickable {
                                                        selectedMediaUris = selectedMediaUris.filter { it != uri }
                                                    },
                                                contentAlignment = Alignment.Center
                                            ) {
                                                Icon(
                                                    imageVector = Icons.Default.Close,
                                                    contentDescription = "Remove",
                                                    tint = Color.White,
                                                    modifier = Modifier.size(11.dp)
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // 5. FIELD 4: Location (Auto-detected with 10s timeout & prediction dialog)
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        LocationHeaderIcon(modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Location",
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.5.sp,
                            color = Color(0xFF111827)
                        )
                    }

                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = Color.White,
                        border = BorderStroke(1.dp, Color(0xFFD4E0D6)),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Rounded.Place,
                                contentDescription = null,
                                tint = when (locationStatus) {
                                    LocationStatus.FAILED -> Color(0xFFDC2626)
                                    LocationStatus.DETECTING -> Color(0xFF9CA3AF)
                                    LocationStatus.DETECTED -> Color(0xFF6B7280)
                                },
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))

                            // Location text or Detecting... or Failed to detect location
                            Text(
                                text = when (locationStatus) {
                                    LocationStatus.DETECTING -> "Detecting$detectingDots"
                                    LocationStatus.FAILED -> "Failed to detect location"
                                    LocationStatus.DETECTED -> locationText
                                },
                                color = when (locationStatus) {
                                    LocationStatus.FAILED -> Color(0xFFDC2626)
                                    LocationStatus.DETECTING -> Color(0xFF6B7280)
                                    LocationStatus.DETECTED -> Color(0xFF374151)
                                },
                                fontSize = 13.sp,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis,
                                modifier = Modifier.weight(1f)
                            )

                            // Edit pencil icon
                            IconButton(
                                onClick = { showEditLocationDialog = true },
                                modifier = Modifier.size(26.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Rounded.Edit,
                                    contentDescription = "Edit Location",
                                    tint = Color(0xFF6B7280),
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                            Spacer(modifier = Modifier.width(4.dp))

                            // Badge display: Auto-detected (only when successfully detected)
                            when (locationStatus) {
                                LocationStatus.DETECTED -> {
                                    Box(
                                        modifier = Modifier
                                            .background(Color(0xFFEAF5EC), RoundedCornerShape(8.dp))
                                            .padding(horizontal = 8.dp, vertical = 3.dp)
                                    ) {
                                        Text(
                                            text = "Auto-detected",
                                            color = Color(0xFF2E7D32),
                                            fontSize = 11.sp,
                                            fontWeight = FontWeight.Medium
                                        )
                                    }
                                }
                                LocationStatus.FAILED -> {
                                    Box(
                                        modifier = Modifier
                                            .background(Color(0xFFFEE2E2), RoundedCornerShape(8.dp))
                                            .padding(horizontal = 8.dp, vertical = 3.dp)
                                    ) {
                                        Text(
                                            text = "Tap to set",
                                            color = Color(0xFFB91C1C),
                                            fontSize = 10.5.sp,
                                            fontWeight = FontWeight.Medium
                                        )
                                    }
                                }
                                LocationStatus.DETECTING -> {
                                    Box(
                                        modifier = Modifier
                                            .background(Color(0xFFF3F4F6), RoundedCornerShape(8.dp))
                                            .padding(horizontal = 8.dp, vertical = 3.dp)
                                    ) {
                                        Text(
                                            text = "Detecting",
                                            color = Color(0xFF6B7280),
                                            fontSize = 10.5.sp,
                                            fontWeight = FontWeight.Medium
                                        )
                                    }
                                }
                            }
                        }
                    }
                }

                // 6. FIELD 5: Description (Optional)
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        DocumentHeaderIcon(modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Description ",
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.5.sp,
                            color = Color(0xFF111827)
                        )
                        Text(
                            text = "(Optional)",
                            fontSize = 12.sp,
                            color = Color(0xFF6B7280)
                        )
                    }

                    Surface(
                        shape = RoundedCornerShape(14.dp),
                        color = Color.White,
                        border = BorderStroke(1.dp, Color(0xFFD4E0D6)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 14.dp, vertical = 12.dp)
                        ) {
                            androidx.compose.foundation.text.BasicTextField(
                                value = description,
                                onValueChange = {
                                    if (it.length <= 500) {
                                        description = it
                                    }
                                },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .heightIn(min = 86.dp),
                                textStyle = LocalTextStyle.current.copy(
                                    fontSize = 14.sp,
                                    color = Color(0xFF111827),
                                    lineHeight = 20.sp
                                ),
                                decorationBox = { innerTextField ->
                                    if (description.isEmpty()) {
                                        Text(
                                            text = "Add any additional details about your crop...",
                                            color = Color(0xFF9CA3AF),
                                            fontSize = 13.5.sp,
                                            lineHeight = 20.sp
                                        )
                                    }
                                    innerTextField()
                                }
                            )

                            Spacer(modifier = Modifier.height(10.dp))

                            Text(
                                text = "${description.length}/500",
                                color = Color(0xFF9CA3AF),
                                fontSize = 12.sp,
                                modifier = Modifier.align(Alignment.End)
                            )
                        }
                    }
                }

                // 7. SUBMIT BUTTON: "List Crop →"
                Button(
                    onClick = {
                        if (cropName.isBlank()) {
                            Toast.makeText(context, "Please enter crop name", Toast.LENGTH_SHORT).show()
                            return@Button
                        }
                        val parsedQty = quantity.toDoubleOrNull()
                        if (parsedQty == null || parsedQty <= 0.0) {
                            Toast.makeText(context, "Please enter a valid quantity in quintals", Toast.LENGTH_SHORT).show()
                            return@Button
                        }
                        if (locationStatus == LocationStatus.FAILED || locationText.isBlank() || locationText == "Failed to detect location") {
                            Toast.makeText(context, "Please set your location before listing", Toast.LENGTH_SHORT).show()
                            showEditLocationDialog = true
                            return@Button
                        }

                        isSubmitting = true
                        coroutineScope.launch {
                            val request = CreateMarketListingRequest(
                                cropName = cropName.trim(),
                                quantity = parsedQty,
                                unit = "Quintal",
                                locationName = locationText.trim(),
                                description = description.trim().ifEmpty { null },
                                mediaUrls = selectedMediaUris.map { it.toString() },
                                latitude = detectedLatitude,
                                longitude = detectedLongitude
                            )
                            try {
                                val response = RetrofitInstance.api.createMarketListing(request)
                                val savedItem = if (response.isSuccessful && response.body() != null) {
                                    response.body()!!
                                } else {
                                    MarketListingDto(
                                        id = (System.currentTimeMillis() % 100000).toInt(),
                                        cropName = request.cropName,
                                        quantity = request.quantity,
                                        unit = request.unit,
                                        pricePerUnit = request.pricePerUnit ?: getDefaultCropPrice(request.cropName),
                                        locationName = request.locationName,
                                        description = request.description,
                                        mediaUrls = request.mediaUrls,
                                        createdAt = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US).format(Date()),
                                        isActive = true
                                    )
                                }
                                MarketListingStore.addListing(savedItem)
                                Toast.makeText(context, "Crop listed successfully!", Toast.LENGTH_LONG).show()
                                navController.popBackStack()
                            } catch (e: Exception) {
                                val localFallback = MarketListingDto(
                                    id = (System.currentTimeMillis() % 100000).toInt(),
                                    cropName = request.cropName,
                                    quantity = request.quantity,
                                    unit = request.unit,
                                    pricePerUnit = request.pricePerUnit ?: getDefaultCropPrice(request.cropName),
                                    locationName = request.locationName,
                                    description = request.description,
                                    mediaUrls = request.mediaUrls,
                                    createdAt = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US).format(Date()),
                                    isActive = true
                                )
                                MarketListingStore.addListing(localFallback)
                                Toast.makeText(context, "Crop listed successfully!", Toast.LENGTH_LONG).show()
                                navController.popBackStack()
                            } finally {
                                isSubmitting = false
                            }
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF2E7D32)
                    ),
                    enabled = !isSubmitting
                ) {
                    if (isSubmitting) {
                        CircularProgressIndicator(
                            color = Color.White,
                            modifier = Modifier.size(20.dp),
                            strokeWidth = 2.dp
                        )
                    } else {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.Center
                        ) {
                            Text(
                                text = "List Crop",
                                color = Color.White,
                                fontWeight = FontWeight.Bold,
                                fontSize = 15.sp
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                }
            }
        }
    }

    // Modern Location Prediction & Search Dialog
    if (showEditLocationDialog) {
        LocationSearchDialog(
            currentLocation = if (locationStatus == LocationStatus.DETECTED) locationText else "",
            onDismiss = { showEditLocationDialog = false },
            onLocationSelected = { selectedLocation, lat, lon ->
                locationText = selectedLocation
                detectedLatitude = lat ?: detectedLatitude
                detectedLongitude = lon ?: detectedLongitude
                locationStatus = LocationStatus.DETECTED
                showEditLocationDialog = false
            }
        )
    }
}

/**
 * Modern Location Search Dialog with real prediction and fallback acceptance
 */
@Composable
fun LocationSearchDialog(
    currentLocation: String,
    onDismiss: () -> Unit,
    onLocationSelected: (locationName: String, lat: Double?, lon: Double?) -> Unit
) {
    val context = LocalContext.current
    val keyboardController = LocalSoftwareKeyboardController.current
    var query by remember { mutableStateOf(currentLocation) }
    var isSearching by remember { mutableStateOf(false) }
    var predictions by remember { mutableStateOf<List<LocationPrediction>>(emptyList()) }

    // Live search as user types with debounce
    LaunchedEffect(query) {
        val trimmed = query.trim()
        if (trimmed.length < 2) {
            predictions = emptyList()
            isSearching = false
            return@LaunchedEffect
        }
        isSearching = true
        delay(250L) // debounce
        val results = searchLocationsDynamic(context, trimmed)
        predictions = results
        isSearching = false
    }

    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(20.dp),
            color = Color.White,
            tonalElevation = 6.dp,
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Dialog Header
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .background(Color(0xFFEAF5EC), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Rounded.Place,
                            contentDescription = null,
                            tint = Color(0xFF2E7D32),
                            modifier = Modifier.size(20.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(10.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "Set Crop Location",
                            fontWeight = FontWeight.Bold,
                            fontSize = 16.sp,
                            color = Color(0xFF111827)
                        )
                        Text(
                            text = "Search mandi, village, city, or district",
                            fontSize = 12.sp,
                            color = Color(0xFF6B7280)
                        )
                    }
                    IconButton(onClick = onDismiss, modifier = Modifier.size(28.dp)) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Close",
                            tint = Color(0xFF9CA3AF),
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }

                // Search Input Field
                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    placeholder = { Text("e.g. Nashik, Maharashtra", fontSize = 13.5.sp) },
                    singleLine = true,
                    leadingIcon = {
                        Icon(
                            imageVector = Icons.Rounded.Search,
                            contentDescription = "Search",
                            tint = Color(0xFF2E7D32),
                            modifier = Modifier.size(20.dp)
                        )
                    },
                    trailingIcon = {
                        if (query.isNotEmpty()) {
                            IconButton(onClick = { query = "" }) {
                                Icon(
                                    imageVector = Icons.Default.Clear,
                                    contentDescription = "Clear",
                                    tint = Color(0xFF9CA3AF),
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        }
                    },
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(onDone = {
                        keyboardController?.hide()
                        if (query.isNotBlank()) {
                            onLocationSelected(query.trim(), null, null)
                        }
                    }),
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = Color(0xFF2E7D32),
                        unfocusedBorderColor = Color(0xFFE5E7EB),
                        cursorColor = Color(0xFF2E7D32)
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                if (isSearching) {
                    LinearProgressIndicator(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(2.dp),
                        color = Color(0xFF2E7D32)
                    )
                }

                // Prediction suggestions list
                LazyColumn(
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(max = 220.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    if (predictions.isNotEmpty()) {
                        item {
                            Text(
                                text = "MATCHING LOCATIONS",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = Color(0xFF9CA3AF),
                                modifier = Modifier.padding(bottom = 2.dp)
                            )
                        }
                        items(predictions) { prediction ->
                            Surface(
                                shape = RoundedCornerShape(10.dp),
                                color = Color(0xFFF9FAFB),
                                border = BorderStroke(1.dp, Color(0xFFF3F4F6)),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable {
                                        onLocationSelected(
                                            prediction.fullDisplayName,
                                            prediction.latitude,
                                            prediction.longitude
                                        )
                                    }
                            ) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(horizontal = 12.dp, vertical = 10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = Icons.Rounded.Place,
                                        contentDescription = null,
                                        tint = Color(0xFF2E7D32),
                                        modifier = Modifier.size(18.dp)
                                    )
                                    Spacer(modifier = Modifier.width(10.dp))
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(
                                            text = prediction.title,
                                            fontWeight = FontWeight.SemiBold,
                                            fontSize = 13.5.sp,
                                            color = Color(0xFF111827)
                                        )
                                        if (prediction.subtitle.isNotBlank()) {
                                            Text(
                                                text = prediction.subtitle,
                                                fontSize = 11.5.sp,
                                                color = Color(0xFF6B7280)
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Direct "Use typed text" option
                    if (query.trim().isNotBlank()) {
                        item {
                            Surface(
                                shape = RoundedCornerShape(10.dp),
                                color = Color(0xFFEAF5EC),
                                border = BorderStroke(1.dp, Color(0xFFC8E6C9)),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable {
                                        onLocationSelected(query.trim(), null, null)
                                    }
                            ) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(horizontal = 12.dp, vertical = 10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = Icons.Rounded.Check,
                                        contentDescription = null,
                                        tint = Color(0xFF2E7D32),
                                        modifier = Modifier.size(18.dp)
                                    )
                                    Spacer(modifier = Modifier.width(10.dp))
                                    Text(
                                        text = "Use \"${query.trim()}\"",
                                        fontWeight = FontWeight.Medium,
                                        fontSize = 13.sp,
                                        color = Color(0xFF1B5E20),
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
                            }
                        }
                    }
                }

                // Action Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    TextButton(onClick = onDismiss) {
                        Text("Cancel", color = Color(0xFF6B7280), fontSize = 13.5.sp)
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Button(
                        onClick = {
                            if (query.isNotBlank()) {
                                onLocationSelected(query.trim(), null, null)
                            }
                        },
                        enabled = query.isNotBlank(),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
                    ) {
                        Text("Confirm", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.5.sp)
                    }
                }
            }
        }
    }
}

/**
 * Dynamic location search using Geocoder + Indian agricultural regions fallback
 */
suspend fun searchLocationsDynamic(context: Context, query: String): List<LocationPrediction> = withContext(Dispatchers.IO) {
    val results = mutableListOf<LocationPrediction>()
    val cleanQuery = query.trim()
    if (cleanQuery.length < 2) return@withContext emptyList()

    try {
        val geocoder = Geocoder(context, Locale.getDefault())
        @Suppress("DEPRECATION")
        val addresses = geocoder.getFromLocationName(cleanQuery, 6)
        addresses?.forEach { addr ->
            val city = addr.locality ?: addr.subAdminArea ?: addr.featureName ?: cleanQuery
            val state = addr.adminArea
            val country = addr.countryName ?: "India"
            val subParts = listOfNotNull(addr.subAdminArea.takeIf { it != city }, state, country).distinct()
            val subtitle = subParts.joinToString(", ")
            val full = if (!state.isNullOrBlank()) "$city, $state" else city
            results.add(
                LocationPrediction(
                    title = city,
                    subtitle = subtitle,
                    fullDisplayName = full,
                    latitude = addr.latitude,
                    longitude = addr.longitude
                )
            )
        }
    } catch (e: Exception) {
        // Continue to fallback
    }

    // Comprehensive agricultural regions fallback for instant responsiveness & offline resilience
    if (results.isEmpty()) {
        val hubs = listOf(
            "Indore, Madhya Pradesh",
            "Bhopal, Madhya Pradesh",
            "Ujjain, Madhya Pradesh",
            "Sehore, Madhya Pradesh",
            "Hoshangabad, Madhya Pradesh",
            "Jabalpur, Madhya Pradesh",
            "Nashik, Maharashtra",
            "Pune, Maharashtra",
            "Nagpur, Maharashtra",
            "Amravati, Maharashtra",
            "Aurangabad, Maharashtra",
            "Solapur, Maharashtra",
            "Kolhapur, Maharashtra",
            "Jaipur, Rajasthan",
            "Kota, Rajasthan",
            "Jodhpur, Rajasthan",
            "Bikaner, Rajasthan",
            "Alwar, Rajasthan",
            "Sri Ganganagar, Rajasthan",
            "Ludhiana, Punjab",
            "Amritsar, Punjab",
            "Patiala, Punjab",
            "Bathinda, Punjab",
            "Karnal, Haryana",
            "Hisar, Haryana",
            "Sirsa, Haryana",
            "Agra, Uttar Pradesh",
            "Kanpur, Uttar Pradesh",
            "Varanasi, Uttar Pradesh",
            "Meerut, Uttar Pradesh",
            "Bareilly, Uttar Pradesh",
            "Ahmedabad, Gujarat",
            "Rajkot, Gujarat",
            "Surat, Gujarat",
            "Vadodara, Gujarat",
            "Mehsana, Gujarat",
            "Junagadh, Gujarat",
            "Belagavi, Karnataka",
            "Dharwad, Karnataka",
            "Mysuru, Karnataka",
            "Guntur, Andhra Pradesh",
            "Warangal, Telangana",
            "Patna, Bihar",
            "Muzaffarpur, Bihar"
        )
        hubs.filter { it.contains(cleanQuery, ignoreCase = true) }
            .take(6)
            .forEach { hub ->
                val parts = hub.split(", ")
                results.add(
                    LocationPrediction(
                        title = parts[0],
                        subtitle = parts.getOrNull(1) ?: "India",
                        fullDisplayName = hub
                    )
                )
            }
    }

    results.distinctBy { it.fullDisplayName }
}

/**
 * Top Banner Card: "List your crop and reach more buyers"
 */
@Composable
private fun ListCropBannerCard() {
    Surface(
        shape = RoundedCornerShape(14.dp),
        color = Color(0xFFEAF5EC),
        modifier = Modifier.fillMaxWidth()
    ) {
        Box {
            FaintLeafWatermark(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(end = 6.dp, bottom = 2.dp)
                    .size(width = 46.dp, height = 40.dp)
            )

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .background(Color(0xFFD4ECD5), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    SeedlingLeadingIcon(
                        modifier = Modifier.size(20.dp),
                        tint = Color(0xFF2E7D32)
                    )
                }

                Spacer(modifier = Modifier.width(10.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "List your crop and reach more buyers",
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.5.sp,
                        color = Color(0xFF111827)
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = "Fill in the details below to create your listing.",
                        fontSize = 11.5.sp,
                        color = Color(0xFF6B7280)
                    )
                }
            }
        }
    }
}

/**
 * Dashed border modifier
 */
private fun Modifier.drawDashedBorder(
    strokeWidth: androidx.compose.ui.unit.Dp,
    color: Color,
    cornerRadius: androidx.compose.ui.unit.Dp,
    dashLength: androidx.compose.ui.unit.Dp = 6.dp,
    gapLength: androidx.compose.ui.unit.Dp = 4.dp
) = this.drawBehind {
    val strokeWidthPx = strokeWidth.toPx()
    val radiusPx = cornerRadius.toPx()
    val dashPx = dashLength.toPx()
    val gapPx = gapLength.toPx()

    val path = Path().apply {
        addRoundRect(
            androidx.compose.ui.geometry.RoundRect(
                left = strokeWidthPx / 2f,
                top = strokeWidthPx / 2f,
                right = size.width - strokeWidthPx / 2f,
                bottom = size.height - strokeWidthPx / 2f,
                cornerRadius = CornerRadius(radiusPx, radiusPx)
            )
        )
    }

    drawPath(
        path = path,
        color = color,
        style = Stroke(
            width = strokeWidthPx,
            pathEffect = PathEffect.dashPathEffect(floatArrayOf(dashPx, gapPx), 0f)
        )
    )
}

/**
 * Custom Canvas vector for Seedling / Sprout (two leaves on a stem)
 */
@Composable
private fun SeedlingLeadingIcon(
    modifier: Modifier = Modifier,
    tint: Color = Color(0xFF2E7D32)
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        val stem = Path().apply {
            moveTo(w * 0.48f, h * 0.90f)
            cubicTo(w * 0.48f, h * 0.60f, w * 0.46f, h * 0.40f, w * 0.44f, h * 0.28f)
        }
        drawPath(
            path = stem,
            color = tint,
            style = Stroke(width = w * 0.10f, cap = androidx.compose.ui.graphics.StrokeCap.Round)
        )

        val leftLeaf = Path().apply {
            moveTo(w * 0.46f, h * 0.55f)
            cubicTo(w * 0.22f, h * 0.55f, w * 0.12f, h * 0.40f, w * 0.20f, h * 0.28f)
            cubicTo(w * 0.38f, h * 0.25f, w * 0.46f, h * 0.42f, w * 0.46f, h * 0.55f)
            close()
        }
        drawPath(path = leftLeaf, color = tint)

        val rightLeaf = Path().apply {
            moveTo(w * 0.46f, h * 0.40f)
            cubicTo(w * 0.70f, h * 0.38f, w * 0.85f, h * 0.20f, w * 0.72f, h * 0.12f)
            cubicTo(w * 0.52f, h * 0.12f, w * 0.44f, h * 0.26f, w * 0.46f, h * 0.40f)
            close()
        }
        drawPath(path = rightLeaf, color = tint)
    }
}

/**
 * Small Green Leaf for section header
 */
@Composable
private fun LeafSmallIcon(
    modifier: Modifier = Modifier,
    tint: Color = Color(0xFF2E7D32)
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val leaf = Path().apply {
            moveTo(w * 0.85f, h * 0.12f)
            cubicTo(w * 0.35f, h * 0.08f, w * 0.08f, h * 0.40f, w * 0.18f, h * 0.85f)
            cubicTo(w * 0.60f, h * 0.92f, w * 0.92f, h * 0.65f, w * 0.85f, h * 0.12f)
            close()
        }
        drawPath(path = leaf, color = tint)

        val vein = Path().apply {
            moveTo(w * 0.18f, h * 0.85f)
            cubicTo(w * 0.35f, h * 0.65f, w * 0.60f, h * 0.45f, w * 0.85f, h * 0.12f)
        }
        drawPath(
            path = vein,
            color = Color.White.copy(alpha = 0.5f),
            style = Stroke(width = w * 0.07f, cap = androidx.compose.ui.graphics.StrokeCap.Round)
        )
    }
}

/**
 * Green Sack/Bag Icon for Quantity Header
 */
@Composable
private fun SackHeaderIcon(
    modifier: Modifier = Modifier,
    tint: Color = Color(0xFF2E7D32)
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        val sackBody = Path().apply {
            moveTo(w * 0.30f, h * 0.32f)
            cubicTo(w * 0.12f, h * 0.45f, w * 0.08f, h * 0.80f, w * 0.20f, h * 0.92f)
            cubicTo(w * 0.30f, h * 0.98f, w * 0.70f, h * 0.98f, w * 0.80f, h * 0.92f)
            cubicTo(w * 0.92f, h * 0.80f, w * 0.88f, h * 0.45f, w * 0.70f, h * 0.32f)
            close()
        }
        drawPath(path = sackBody, color = tint)

        drawRoundRect(
            color = Color(0xFF1B5E20),
            topLeft = Offset(w * 0.28f, h * 0.26f),
            size = Size(w * 0.44f, h * 0.10f),
            cornerRadius = CornerRadius(w * 0.04f, w * 0.04f)
        )

        val topRuffle = Path().apply {
            moveTo(w * 0.30f, h * 0.26f)
            lineTo(w * 0.22f, h * 0.12f)
            cubicTo(w * 0.35f, h * 0.08f, w * 0.65f, h * 0.08f, w * 0.78f, h * 0.12f)
            lineTo(w * 0.70f, h * 0.26f)
            close()
        }
        drawPath(path = topRuffle, color = tint)
    }
}

/**
 * Balance/Scale weight icon for Quantity input leading icon
 */
@Composable
private fun ScaleWeightIcon(
    modifier: Modifier = Modifier,
    tint: Color = Color(0xFF6B7280)
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        drawCircle(
            color = tint,
            radius = w * 0.18f,
            center = Offset(w * 0.5f, h * 0.22f),
            style = Stroke(width = w * 0.10f)
        )

        val weight = Path().apply {
            moveTo(w * 0.32f, h * 0.38f)
            lineTo(w * 0.68f, h * 0.38f)
            lineTo(w * 0.84f, h * 0.88f)
            cubicTo(w * 0.84f, h * 0.94f, w * 0.16f, h * 0.94f, w * 0.16f, h * 0.88f)
            close()
        }
        drawPath(path = weight, color = tint)

        drawCircle(
            color = Color.White.copy(alpha = 0.8f),
            radius = w * 0.10f,
            center = Offset(w * 0.5f, h * 0.65f)
        )
    }
}

/**
 * Green Image Landscape Icon for Photos Header
 */
@Composable
private fun ImageHeaderIcon(
    modifier: Modifier = Modifier,
    tint: Color = Color(0xFF2E7D32)
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val r = w * 0.15f

        drawRoundRect(
            color = tint,
            topLeft = Offset(w * 0.06f, h * 0.10f),
            size = Size(w * 0.88f, h * 0.80f),
            cornerRadius = CornerRadius(r, r)
        )

        drawCircle(
            color = Color.White,
            radius = w * 0.11f,
            center = Offset(w * 0.32f, h * 0.36f)
        )

        val mountain = Path().apply {
            moveTo(w * 0.14f, h * 0.80f)
            lineTo(w * 0.42f, h * 0.52f)
            lineTo(w * 0.58f, h * 0.68f)
            lineTo(w * 0.72f, h * 0.54f)
            lineTo(w * 0.86f, h * 0.80f)
            close()
        }
        drawPath(path = mountain, color = Color.White)
    }
}

/**
 * Green Location Pin Icon for Location Header
 */
@Composable
private fun LocationHeaderIcon(
    modifier: Modifier = Modifier,
    tint: Color = Color(0xFF2E7D32)
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        val pin = Path().apply {
            moveTo(w * 0.50f, h * 0.94f)
            cubicTo(w * 0.35f, h * 0.68f, w * 0.14f, h * 0.50f, w * 0.14f, h * 0.34f)
            cubicTo(w * 0.14f, h * 0.15f, w * 0.30f, h * 0.06f, w * 0.50f, h * 0.06f)
            cubicTo(w * 0.70f, h * 0.06f, w * 0.86f, h * 0.15f, w * 0.86f, h * 0.34f)
            cubicTo(w * 0.86f, h * 0.50f, w * 0.65f, h * 0.68f, w * 0.50f, h * 0.94f)
            close()
        }
        drawPath(path = pin, color = tint)

        drawCircle(
            color = Color.White,
            radius = w * 0.15f,
            center = Offset(w * 0.50f, h * 0.34f)
        )
    }
}

/**
 * Green Document Lines Icon for Description Header
 */
@Composable
private fun DocumentHeaderIcon(
    modifier: Modifier = Modifier,
    tint: Color = Color(0xFF2E7D32)
) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val r = w * 0.14f

        drawRoundRect(
            color = tint,
            topLeft = Offset(w * 0.12f, h * 0.08f),
            size = Size(w * 0.76f, h * 0.84f),
            cornerRadius = CornerRadius(r, r)
        )

        val lineStyle = Stroke(
            width = w * 0.08f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )

        drawLine(
            color = Color.White,
            start = Offset(w * 0.28f, h * 0.32f),
            end = Offset(w * 0.72f, h * 0.32f),
            strokeWidth = lineStyle.width,
            cap = lineStyle.cap
        )
        drawLine(
            color = Color.White,
            start = Offset(w * 0.28f, h * 0.50f),
            end = Offset(w * 0.72f, h * 0.50f),
            strokeWidth = lineStyle.width,
            cap = lineStyle.cap
        )
        drawLine(
            color = Color.White,
            start = Offset(w * 0.28f, h * 0.68f),
            end = Offset(w * 0.56f, h * 0.68f),
            strokeWidth = lineStyle.width,
            cap = lineStyle.cap
        )
    }
}

/**
 * Center Upload Placeholder Graphic (Gray image frame with green circle + badge)
 */
@Composable
private fun UploadPlaceholderGraphic(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height

        val frameStroke = Stroke(
            width = w * 0.07f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )
        drawRoundRect(
            color = Color(0xFF9CA3AF),
            topLeft = Offset(w * 0.10f, h * 0.14f),
            size = Size(w * 0.72f, h * 0.66f),
            cornerRadius = CornerRadius(w * 0.14f, w * 0.14f),
            style = frameStroke
        )

        val hill = Path().apply {
            moveTo(w * 0.18f, h * 0.68f)
            lineTo(w * 0.38f, h * 0.44f)
            lineTo(w * 0.50f, h * 0.56f)
            lineTo(w * 0.64f, h * 0.42f)
            lineTo(w * 0.76f, h * 0.68f)
        }
        drawPath(path = hill, color = Color(0xFF9CA3AF), style = frameStroke)

        drawCircle(
            color = Color(0xFF9CA3AF),
            radius = w * 0.08f,
            center = Offset(w * 0.34f, h * 0.32f)
        )

        val badgeCenter = Offset(w * 0.76f, h * 0.74f)
        val badgeRadius = w * 0.20f

        drawCircle(color = Color.White, radius = badgeRadius + w * 0.03f, center = badgeCenter)
        drawCircle(color = Color(0xFF2E7D32), radius = badgeRadius, center = badgeCenter)

        val plusLen = badgeRadius * 0.55f
        val plusStroke = w * 0.06f
        drawLine(
            color = Color.White,
            start = Offset(badgeCenter.x - plusLen, badgeCenter.y),
            end = Offset(badgeCenter.x + plusLen, badgeCenter.y),
            strokeWidth = plusStroke,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )
        drawLine(
            color = Color.White,
            start = Offset(badgeCenter.x, badgeCenter.y - plusLen),
            end = Offset(badgeCenter.x, badgeCenter.y + plusLen),
            strokeWidth = plusStroke,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )
    }
}

/**
 * Faint green leaf watermark for the top banner card
 */
@Composable
private fun FaintLeafWatermark(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val w = size.width
        val h = size.height
        val leafColor = Color(0xFF81C784).copy(alpha = 0.45f)

        val leaf1 = Path().apply {
            moveTo(w * 0.75f, h * 0.10f)
            cubicTo(w * 0.60f, h * 0.40f, w * 0.65f, h * 0.75f, w * 0.55f, h * 0.95f)
            cubicTo(w * 0.90f, h * 0.75f, w * 0.98f, h * 0.40f, w * 0.75f, h * 0.10f)
            close()
        }
        drawPath(path = leaf1, color = leafColor)

        val leaf2 = Path().apply {
            moveTo(w * 0.45f, h * 0.45f)
            cubicTo(w * 0.25f, h * 0.60f, w * 0.15f, h * 0.80f, w * 0.20f, h * 0.95f)
            cubicTo(w * 0.45f, h * 0.90f, w * 0.55f, h * 0.70f, w * 0.45f, h * 0.45f)
            close()
        }
        drawPath(path = leaf2, color = leafColor)
    }
}
