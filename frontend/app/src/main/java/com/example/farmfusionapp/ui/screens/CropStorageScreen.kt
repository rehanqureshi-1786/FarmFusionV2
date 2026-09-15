package com.example.farmfusionapp.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.data.model.ColdStorageItem
import com.example.farmfusionapp.utils.LocationSnapshotStore
import com.example.farmfusionapp.utils.getDeviceLocation
import com.example.farmfusionapp.viewmodel.ColdStorageUiState
import com.example.farmfusionapp.viewmodel.ColdStorageViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CropStorageScreen(
    navController: NavController,
    viewModel: ColdStorageViewModel = viewModel()
) {
    val context = LocalContext.current
    val focusManager = LocalFocusManager.current

    val uiState by viewModel.uiState
    val currentCrop by viewModel.selectedCrop
    val searchQuery by viewModel.searchQuery
    val selectedRadius by viewModel.selectedRadius
    val activeSearchedArea by viewModel.activeSearchedArea

    val radiusOptions = listOf(10.0, 25.0, 50.0, 100.0)

    val cropFilters = listOf(
        null to "All Produce",
        "Potato" to "🥔 Potato (आलू)",
        "Onion" to "🧅 Onion (प्याज)",
        "Garlic" to "🧄 Garlic (लहसुन)",
        "Carrot" to "🥕 Carrot (गाजर)",
        "Fruits" to "🍎 Fruits (फल)",
        "Vegetables" to "🥦 Vegetables (सब्जियां)",
        "Spices" to "🌶️ Spices (मसाले)"
    )

    // Initial Load: Fetch facilities according to the user's current GPS location
    LaunchedEffect(Unit) {
        val location = getDeviceLocation(context)
        val lat = location?.first ?: LocationSnapshotStore.latestLatitude ?: 26.9124
        val lon = location?.second ?: LocationSnapshotStore.latestLongitude ?: 75.7873
        viewModel.initUserLocation(lat, lon)
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF8FAFC))
    ) {
        // Gradient Header Background
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(260.dp)
                .background(
                    Brush.verticalGradient(
                        listOf(
                            Color(0xFFE0F2FE),
                            Color(0xFFE8F5E9),
                            Color(0xFFF8FAFC)
                        )
                    )
                )
        )

        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                CenterAlignedTopAppBar(
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent,
                        titleContentColor = Color(0xFF0F172A)
                    ),
                    title = {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                text = "Crop Storage (शीतगृह)",
                                fontWeight = FontWeight.Bold,
                                fontSize = 18.sp,
                                color = Color(0xFF0F172A)
                            )
                            Text(
                                text = "Cold Chain & Preservation Hubs",
                                fontSize = 12.sp,
                                color = Color(0xFF64748B)
                            )
                        }
                    },
                    navigationIcon = {
                        Surface(
                            onClick = { navController.popBackStack() },
                            shape = CircleShape,
                            color = Color.White,
                            shadowElevation = 2.dp,
                            modifier = Modifier
                                .padding(start = 16.dp)
                                .size(40.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    imageVector = Icons.AutoMirrored.Rounded.ArrowBack,
                                    contentDescription = "Back",
                                    tint = Color(0xFF1E293B),
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                        }
                    }
                )
            }
        ) { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                // ========================================
                // SEARCH BAR WITH DEDICATED SEARCH BUTTON
                // ========================================
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = Color.White,
                    shadowElevation = 3.dp,
                    border = BorderStroke(1.dp, Color(0xFFE2E8F0)),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 6.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Rounded.Search,
                            contentDescription = "Search",
                            tint = Color(0xFF0284C7),
                            modifier = Modifier.padding(start = 6.dp)
                        )

                        TextField(
                            value = searchQuery,
                            onValueChange = { viewModel.onSearchQueryChanged(it) },
                            placeholder = {
                                Text(
                                    "Search city, district, town, or PIN...",
                                    fontSize = 13.5.sp,
                                    color = Color(0xFF94A3B8)
                                )
                            },
                            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                            keyboardActions = KeyboardActions(
                                onSearch = {
                                    focusManager.clearFocus()
                                    viewModel.submitSearch(searchQuery)
                                }
                            ),
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = Color.Transparent,
                                unfocusedContainerColor = Color.Transparent,
                                focusedIndicatorColor = Color.Transparent,
                                unfocusedIndicatorColor = Color.Transparent
                            ),
                            singleLine = true,
                            modifier = Modifier.weight(1f)
                        )

                        if (searchQuery.isNotBlank()) {
                            IconButton(
                                onClick = {
                                    focusManager.clearFocus()
                                    viewModel.clearSearch()
                                },
                                modifier = Modifier.size(36.dp)
                            ) {
                                Icon(
                                    Icons.Rounded.Clear,
                                    contentDescription = "Clear",
                                    tint = Color(0xFF64748B),
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }

                        // Prominent Search Button
                        Button(
                            onClick = {
                                focusManager.clearFocus()
                                viewModel.submitSearch(searchQuery)
                            },
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF0284C7)),
                            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp),
                            modifier = Modifier.height(38.dp)
                        ) {
                            Text(
                                text = "Search",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        }
                    }
                }

                // ========================================
                // ACTIVE SEARCHED AREA BANNER
                // ========================================
                if (!activeSearchedArea.isNullOrBlank()) {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = Color(0xFFE0F2FE),
                        border = BorderStroke(1.dp, Color(0xFFBAE6FD)),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 4.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.weight(1f)
                            ) {
                                Icon(
                                    imageVector = Icons.Rounded.LocationOn,
                                    contentDescription = null,
                                    tint = Color(0xFF0369A1),
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Column {
                                    Text(
                                        text = "Showing Facilities in:",
                                        fontSize = 11.sp,
                                        color = Color(0xFF0369A1)
                                    )
                                    Text(
                                        text = activeSearchedArea!!,
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = Color(0xFF0C4A6E),
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
                            }

                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = Color.White,
                                border = BorderStroke(1.dp, Color(0xFF7DD3FC)),
                                modifier = Modifier.clickable {
                                    focusManager.clearFocus()
                                    viewModel.clearSearch()
                                }
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                ) {
                                    Icon(
                                        imageVector = Icons.Rounded.MyLocation,
                                        contentDescription = null,
                                        tint = Color(0xFF0284C7),
                                        modifier = Modifier.size(14.dp)
                                    )
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = "My Location",
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = Color(0xFF0284C7)
                                    )
                                }
                            }
                        }
                    }
                }

                // ========================================
                // RADIUS / DISTANCE FILTER ROW (10km, 25km, 50km, 100km)
                // ========================================
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 4.dp)
                ) {
                    Icon(
                        imageVector = Icons.Rounded.NearMe,
                        contentDescription = null,
                        tint = Color(0xFF475569),
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Radius:",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF475569)
                    )
                    Spacer(modifier = Modifier.width(8.dp))

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        radiusOptions.forEach { rad ->
                            val isSelected = selectedRadius == rad
                            Surface(
                                shape = RoundedCornerShape(16.dp),
                                color = if (isSelected) Color(0xFF0F172A) else Color.White,
                                border = BorderStroke(
                                    1.dp,
                                    if (isSelected) Color(0xFF0F172A) else Color(0xFFCBD5E1)
                                ),
                                shadowElevation = if (isSelected) 2.dp else 0.dp,
                                modifier = Modifier
                                    .weight(1f)
                                    .height(32.dp)
                                    .clickable {
                                        viewModel.selectRadius(rad)
                                    }
                            ) {
                                Box(
                                    contentAlignment = Alignment.Center,
                                    modifier = Modifier.fillMaxSize()
                                ) {
                                    Text(
                                        text = "${rad.toInt()} km",
                                        fontSize = 12.sp,
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        color = if (isSelected) Color.White else Color(0xFF334155)
                                    )
                                }
                            }
                        }
                    }
                }

                // ========================================
                // CROP FILTER CHIPS ROW
                // ========================================
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp, vertical = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    cropFilters.forEach { (cropKey, label) ->
                        val isSelected = currentCrop == cropKey
                        Surface(
                            shape = RoundedCornerShape(18.dp),
                            color = if (isSelected) Color(0xFF0284C7) else Color.White,
                            border = if (!isSelected) BorderStroke(1.dp, Color(0xFFCBD5E1)) else null,
                            shadowElevation = if (isSelected) 1.5.dp else 0.dp,
                            modifier = Modifier.clickable {
                                viewModel.selectCrop(cropKey)
                            }
                        ) {
                            Text(
                                text = label,
                                fontSize = 12.5.sp,
                                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
                                color = if (isSelected) Color.White else Color(0xFF334155),
                                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                            )
                        }
                    }
                }

                // ========================================
                // RESULTS & STATE HANDLING
                // ========================================
                when (val state = uiState) {
                    is ColdStorageUiState.Loading -> {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(32.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                CircularProgressIndicator(color = Color(0xFF0284C7))
                                Spacer(modifier = Modifier.height(16.dp))
                                Text(
                                    text = if (!activeSearchedArea.isNullOrBlank()) {
                                        "Searching facilities in ${activeSearchedArea}..."
                                    } else {
                                        "Finding nearest facilities to your location..."
                                    },
                                    fontSize = 14.sp,
                                    color = Color(0xFF64748B)
                                )
                            }
                        }
                    }

                    is ColdStorageUiState.Error -> {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(32.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                Icon(
                                    Icons.Rounded.CloudOff,
                                    contentDescription = "Error",
                                    tint = Color(0xFFEF4444),
                                    modifier = Modifier.size(48.dp)
                                )
                                Spacer(modifier = Modifier.height(12.dp))
                                Text(
                                    text = state.message,
                                    fontSize = 14.sp,
                                    color = Color(0xFF64748B),
                                    textAlign = TextAlign.Center
                                )
                                Spacer(modifier = Modifier.height(16.dp))
                                Button(
                                    onClick = { viewModel.loadStorages() },
                                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF0284C7))
                                ) {
                                    Text("Retry Search")
                                }
                            }
                        }
                    }

                    is ColdStorageUiState.Success -> {
                        if (state.items.isEmpty()) {
                            Box(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(32.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Icon(
                                        Icons.Rounded.Warehouse,
                                        contentDescription = "No Storage",
                                        tint = Color(0xFF94A3B8),
                                        modifier = Modifier.size(56.dp)
                                    )
                                    Spacer(modifier = Modifier.height(12.dp))
                                    Text(
                                        text = if (!state.searchedArea.isNullOrBlank()) {
                                            "No facilities found within ${selectedRadius.toInt()} km of ${state.searchedArea}."
                                        } else {
                                            "No facilities found within ${selectedRadius.toInt()} km of your location."
                                        },
                                        fontSize = 14.5.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = Color(0xFF334155),
                                        textAlign = TextAlign.Center
                                    )
                                    Spacer(modifier = Modifier.height(6.dp))
                                    Text(
                                        text = "Try expanding your search radius to find nearby preservation hubs:",
                                        fontSize = 13.sp,
                                        color = Color(0xFF64748B),
                                        textAlign = TextAlign.Center
                                    )
                                    Spacer(modifier = Modifier.height(16.dp))

                                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                        if (selectedRadius < 50.0) {
                                            OutlinedButton(
                                                onClick = { viewModel.selectRadius(50.0) },
                                                colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF0284C7))
                                            ) {
                                                Text("Expand to 50 km")
                                            }
                                        }
                                        if (selectedRadius < 100.0) {
                                            Button(
                                                onClick = { viewModel.selectRadius(100.0) },
                                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF0284C7))
                                            ) {
                                                Text("Expand to 100 km")
                                            }
                                        }
                                    }

                                    if (!activeSearchedArea.isNullOrBlank()) {
                                        Spacer(modifier = Modifier.height(12.dp))
                                        TextButton(onClick = { viewModel.clearSearch() }) {
                                            Icon(Icons.Rounded.MyLocation, contentDescription = null, modifier = Modifier.size(16.dp))
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Text("Return to My Location")
                                        }
                                    }
                                }
                            }
                        } else {
                            LazyColumn(
                                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                                verticalArrangement = Arrangement.spacedBy(14.dp),
                                modifier = Modifier.fillMaxSize()
                            ) {
                                item {
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(horizontal = 4.dp, vertical = 2.dp)
                                    ) {
                                        Text(
                                            text = if (!state.searchedArea.isNullOrBlank()) {
                                                "${state.items.size} Facilities in ${state.searchedArea} (within ${state.searchRadiusKm.toInt()} km)"
                                            } else {
                                                "${state.items.size} Facilities Nearby (within ${state.searchRadiusKm.toInt()} km)"
                                            },
                                            fontSize = 13.5.sp,
                                            fontWeight = FontWeight.SemiBold,
                                            color = Color(0xFF475569)
                                        )
                                    }
                                }

                                items(state.items, key = { it.id }) { storage ->
                                    EnhancedColdStorageCard(
                                        storage = storage,
                                        searchedArea = state.searchedArea,
                                        onCallClick = {
                                            val phone = storage.phoneNumber ?: storage.alternatePhoneNumber
                                            if (!phone.isNullOrBlank()) {
                                                val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:${phone.trim()}"))
                                                context.startActivity(intent)
                                            }
                                        },
                                        onDirectionsClick = {
                                            val gmaps = storage.googleMapsUrl
                                            if (!gmaps.isNullOrBlank()) {
                                                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(gmaps))
                                                context.startActivity(intent)
                                            } else if (storage.latitude != 0.0 && storage.longitude != 0.0) {
                                                val uri = Uri.parse("geo:${storage.latitude},${storage.longitude}?q=${storage.latitude},${storage.longitude}(${Uri.encode(storage.name)})")
                                                context.startActivity(Intent(Intent.ACTION_VIEW, uri))
                                            }
                                        }
                                    )
                                }

                                item {
                                    Spacer(modifier = Modifier.height(24.dp))
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun EnhancedColdStorageCard(
    storage: ColdStorageItem,
    searchedArea: String?,
    onCallClick: () -> Unit,
    onDirectionsClick: () -> Unit
) {
    Surface(
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        shadowElevation = 2.dp,
        border = BorderStroke(1.dp, Color(0xFFF1F5F9)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Header: Name & Rating
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = storage.name,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF0F172A),
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                    Spacer(modifier = Modifier.height(3.dp))
                    Text(
                        text = storage.address,
                        fontSize = 13.sp,
                        color = Color(0xFF64748B),
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                    Text(
                        text = "${storage.district}, ${storage.state}${if (!storage.pincode.isNullOrBlank()) " - ${storage.pincode}" else ""}",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF0284C7)
                    )
                }

                // Rating Badge
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = Color(0xFFFEF3C7),
                    modifier = Modifier.padding(start = 8.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(horizontal = 7.dp, vertical = 4.dp)
                    ) {
                        Icon(
                            Icons.Rounded.Star,
                            contentDescription = null,
                            tint = Color(0xFFD97706),
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(3.dp))
                        Text(
                            text = String.format(java.util.Locale.US, "%.1f", storage.rating),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF92400E)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Metadata Badges Row: Distance, Drive Time, Capacity
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Distance Badge
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = Color(0xFFEFF6FF)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Icon(
                            Icons.Rounded.LocationOn,
                            contentDescription = null,
                            tint = Color(0xFF2563EB),
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = if (storage.userDistanceKm != null && !searchedArea.isNullOrBlank()) {
                                "${storage.distanceKm} km from ${searchedArea.split(',')[0]} (${storage.userDistanceKm.toInt()} km away)"
                            } else {
                                "${storage.distanceKm} km away"
                            },
                            fontSize = 11.5.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF1D4ED8)
                        )
                    }
                }

                // Drive Time
                if (!storage.driveTimeText.isNullOrBlank()) {
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = Color(0xFFF1F5F9)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Icon(
                                Icons.Rounded.DirectionsCar,
                                contentDescription = null,
                                tint = Color(0xFF475569),
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = storage.driveTimeText,
                                fontSize = 11.5.sp,
                                color = Color(0xFF334155)
                            )
                        }
                    }
                }

                // Capacity
                if (!storage.storageCapacity.isNullOrBlank()) {
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = Color(0xFFECFDF5)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Icon(
                                Icons.Rounded.Inventory2,
                                contentDescription = null,
                                tint = Color(0xFF059669),
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = storage.storageCapacity,
                                fontSize = 11.5.sp,
                                fontWeight = FontWeight.Medium,
                                color = Color(0xFF065F46)
                            )
                        }
                    }
                }

                // Temperature
                if (!storage.temperatureRange.isNullOrBlank()) {
                    Surface(
                        shape = RoundedCornerShape(10.dp),
                        color = Color(0xFFF0FDF4)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Icon(
                                Icons.Rounded.AcUnit,
                                contentDescription = null,
                                tint = Color(0xFF16A34A),
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = storage.temperatureRange,
                                fontSize = 11.5.sp,
                                color = Color(0xFF166534)
                            )
                        }
                    }
                }
            }

            // Suitable Crops Tag
            if (!storage.suitableCrops.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(10.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = "Suitable Crops: ",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF475569)
                    )
                    Text(
                        text = storage.suitableCrops,
                        fontSize = 12.sp,
                        color = Color(0xFF0F172A),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }

            // Description / Amenities if present
            if (!storage.description.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = storage.description,
                    fontSize = 12.sp,
                    color = Color(0xFF64748B),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
            }

            HorizontalDivider(
                modifier = Modifier.padding(vertical = 12.dp),
                thickness = 0.8.dp,
                color = Color(0xFFF1F5F9)
            )

            // Action Buttons: Call & Directions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                // Call Button
                OutlinedButton(
                    onClick = onCallClick,
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = Color(0xFF16A34A)
                    ),
                    border = BorderStroke(1.dp, Color(0xFF86EFAC)),
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        Icons.Rounded.Call,
                        contentDescription = "Call",
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Call Facility",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                // Directions Button
                Button(
                    onClick = onDirectionsClick,
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF0284C7)
                    ),
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        Icons.Rounded.Navigation,
                        contentDescription = "Directions",
                        tint = Color.White,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Directions",
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color.White
                    )
                }
            }
        }
    }
}
