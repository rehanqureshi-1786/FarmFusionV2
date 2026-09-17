package com.example.farmfusionapp.ui.screens

import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.navigation.NavController
import com.example.farmfusionapp.data.model.MarketListingDto
import com.example.farmfusionapp.data.model.MarketListingStore
import com.example.farmfusionapp.data.model.getDefaultCropPrice
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AvailableListingsScreen(navController: NavController) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var isRefreshing by remember { mutableStateOf(false) }
    var searchQuery by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf("ALL") }
    var selectedListingForDetails by remember { mutableStateOf<MarketListingDto?>(null) }
    var backendListings by remember { mutableStateOf<List<MarketListingDto>>(emptyList()) }

    val categories = listOf("ALL", "GRAINS", "VEGETABLES", "PULSES", "FRUITS", "SPICES")

    suspend fun fetchActiveListings() {
        try {
            val response = withContext(Dispatchers.IO) {
                RetrofitInstance.api.getMarketListings(activeOnly = true)
            }
            if (response.isSuccessful && response.body() != null) {
                backendListings = response.body()!!
            }
        } catch (e: Exception) {
            // Fallback to active local store listings
        }
    }

    LaunchedEffect(Unit) {
        fetchActiveListings()
    }

    // Merge backend results with any active local store listings that aren't duplicates
    val allActiveListings = remember(backendListings, MarketListingStore.localListings) {
        val activeLocals = MarketListingStore.localListings.filter { it.isActive != false }
        val backendIds = backendListings.mapNotNull { it.id }.toSet()
        val combined = backendListings.toMutableList()
        activeLocals.forEach { local ->
            if (local.id == null || local.id !in backendIds) {
                combined.add(local)
            }
        }
        combined
    }

    val filteredListings = remember(allActiveListings, searchQuery, selectedCategory) {
        allActiveListings.filter { item ->
            val crop = item.cropName ?: ""
            val loc = item.locationName ?: ""
            val matchesSearch = searchQuery.isEmpty() ||
                    crop.contains(searchQuery, ignoreCase = true) ||
                    loc.contains(searchQuery, ignoreCase = true)
            val matchesCat = selectedCategory == "ALL" || isCropInCategory(crop, selectedCategory)
            matchesSearch && matchesCat
        }
    }

    val onNavigateBack = {
        if (!navController.popBackStack()) {
            navController.navigate(NavRoutes.BuyerDashboard) {
                popUpTo(NavRoutes.BuyerDashboard) { inclusive = false }
                launchSingleTop = true
            }
        }
    }

    BackHandler {
        onNavigateBack()
    }

    NeoScaffoldBackground(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                CenterAlignedTopAppBar(
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent,
                        scrolledContainerColor = Color.Transparent
                    ),
                    title = {
                        Text(
                            text = "Available Listings",
                            fontWeight = FontWeight.Bold,
                            fontSize = 18.sp,
                            color = Color(0xFF111827)
                        )
                    },
                    navigationIcon = {
                        IconButton(onClick = { onNavigateBack() }) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Back",
                                tint = Color(0xFF111827)
                            )
                        }
                    },
                    actions = {
                        IconButton(
                            onClick = {
                                coroutineScope.launch {
                                    isRefreshing = true
                                    fetchActiveListings()
                                    Toast.makeText(context, "Listings updated", Toast.LENGTH_SHORT).show()
                                    isRefreshing = false
                                }
                            }
                        ) {
                            if (isRefreshing) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(18.dp),
                                    strokeWidth = 2.dp,
                                    color = Color(0xFF2E7D32)
                                )
                            } else {
                                Icon(
                                    imageVector = Icons.Rounded.Refresh,
                                    contentDescription = "Refresh",
                                    tint = Color(0xFF4B5563)
                                )
                            }
                        }
                    }
                )
            }
        ) { padding ->
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(top = 8.dp, bottom = 40.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Search Bar
                item {
                    Surface(
                        shape = RoundedCornerShape(20.dp),
                        color = Color.White.copy(alpha = 0.95f),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp)
                            .shadow(
                                elevation = 8.dp,
                                shape = RoundedCornerShape(20.dp),
                                spotColor = Color.Black.copy(alpha = 0.04f),
                                ambientColor = Color.Transparent
                            )
                    ) {
                        TextField(
                            value = searchQuery,
                            onValueChange = { searchQuery = it },
                            placeholder = { Text("Search by crop name or location...") },
                            leadingIcon = { Icon(Icons.Rounded.Search, null, tint = Color.Gray) },
                            trailingIcon = {
                                if (searchQuery.isNotEmpty()) {
                                    IconButton(onClick = { searchQuery = "" }) {
                                        Icon(Icons.Rounded.Clear, contentDescription = "Clear")
                                    }
                                }
                            },
                            singleLine = true,
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = Color.Transparent,
                                unfocusedContainerColor = Color.Transparent,
                                focusedIndicatorColor = Color.Transparent,
                                unfocusedIndicatorColor = Color.Transparent
                            ),
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }

                // Category Filter Pills
                item {
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                        contentPadding = PaddingValues(horizontal = 20.dp)
                    ) {
                        items(categories) { category ->
                            val isSelected = category == selectedCategory
                            Surface(
                                onClick = { selectedCategory = category },
                                shape = RoundedCornerShape(50),
                                color = if (isSelected) Color(0xFF1B4332) else Color.White,
                                shadowElevation = if (!isSelected) 2.dp else 0.dp
                            ) {
                                Text(
                                    text = category,
                                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 9.dp),
                                    style = MaterialTheme.typography.labelMedium.copy(
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        color = if (isSelected) Color.White else Color(0xFF1B1B1B)
                                    )
                                )
                            }
                        }
                    }
                }

                // Results Summary
                item {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "${filteredListings.size} Active Crops Listed",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF4B5563)
                        )
                    }
                }

                // Empty State
                if (filteredListings.isEmpty()) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 20.dp)
                                .height(200.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Rounded.Storefront,
                                    contentDescription = null,
                                    tint = Color(0xFF9CA3AF),
                                    modifier = Modifier.size(48.dp)
                                )
                                Spacer(modifier = Modifier.height(12.dp))
                                Text(
                                    text = if (searchQuery.isNotBlank()) "No listings matching '$searchQuery'" else "No active crops listed yet",
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = Color(0xFF6B7280)
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = "Farmers' listings will appear here in real-time.",
                                    fontSize = 12.5.sp,
                                    color = Color(0xFF9CA3AF)
                                )
                            }
                        }
                    }
                } else {
                    items(filteredListings, key = { it.id ?: it.hashCode() }) { listing ->
                        BuyerCropListingCard(
                            listing = listing,
                            onClick = { selectedListingForDetails = listing },
                            onContactClick = {
                                val intent = Intent(Intent.ACTION_DIAL).apply {
                                    data = Uri.parse("tel:+918064265824")
                                }
                                try {
                                    context.startActivity(intent)
                                } catch (e: Exception) {
                                    Toast.makeText(context, "Contact: Kisan Helpline (+91 8064265824)", Toast.LENGTH_LONG).show()
                                }
                            },
                            modifier = Modifier.padding(horizontal = 20.dp)
                        )
                    }
                }
            }
        }
    }

    // Buyer Details Dialog
    selectedListingForDetails?.let { listing ->
        BuyerListingDetailsDialog(
            listing = listing,
            onDismiss = { selectedListingForDetails = null },
            onContactClick = {
                val intent = Intent(Intent.ACTION_DIAL).apply {
                    data = Uri.parse("tel:+918064265824")
                }
                try {
                    context.startActivity(intent)
                } catch (e: Exception) {
                    Toast.makeText(context, "Contact: Kisan Helpline (+91 8064265824)", Toast.LENGTH_LONG).show()
                }
            }
        )
    }
}

/**
 * Modern crop card designed specifically for buyers.
 */
@Composable
private fun BuyerCropListingCard(
    listing: MarketListingDto,
    onClick: () -> Unit,
    onContactClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val cropName = listing.cropName ?: "Crop"
    val unit = listing.unit ?: "Quintal"
    val price = listing.pricePerUnit ?: getDefaultCropPrice(cropName)
    val formattedDate = remember(listing.createdAt) {
        formatListingDate(listing.createdAt)
    }

    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFF1F3F5)),
        modifier = modifier
            .fillMaxWidth()
            .shadow(
                elevation = 4.dp,
                shape = RoundedCornerShape(20.dp),
                spotColor = Color.Black.copy(alpha = 0.06f),
                ambientColor = Color.Black.copy(alpha = 0.02f)
            )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Crop Thumbnail
            Box(
                modifier = Modifier
                    .size(76.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(Color(0xFFF4F6F4))
            ) {
                CropThumbnailGraphic(
                    cropName = cropName,
                    mediaUrls = listing.mediaUrls
                )
            }

            Spacer(modifier = Modifier.width(14.dp))

            // Information Column
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = cropName,
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        color = Color(0xFF111827),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f)
                    )

                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = Color(0xFFE8F5E9)
                    ) {
                        Text(
                            text = "${listing.quantity?.toInt() ?: 0} $unit",
                            fontSize = 11.5.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1B5E20),
                            modifier = Modifier.padding(horizontal = 7.dp, vertical = 3.dp)
                        )
                    }
                }

                // Price
                Row(verticalAlignment = Alignment.Bottom) {
                    Text(
                        text = "₹${price.toInt()}",
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 16.sp,
                        color = Color(0xFF166534)
                    )
                    Text(
                        text = " / $unit",
                        fontSize = 11.5.sp,
                        color = Color(0xFF6B7280),
                        fontWeight = FontWeight.Medium
                    )
                }

                // Location & Date
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Rounded.LocationOn,
                        contentDescription = null,
                        tint = Color(0xFF9CA3AF),
                        modifier = Modifier.size(13.dp)
                    )
                    Text(
                        text = listing.locationName ?: "Rajasthan, India",
                        fontSize = 11.5.sp,
                        color = Color(0xFF6B7280),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f)
                    )

                    Text(
                        text = formattedDate,
                        fontSize = 10.5.sp,
                        color = Color(0xFF9CA3AF)
                    )
                }
            }
        }
    }
}

/**
 * Rich details dialog for a buyer inspecting a farmer's crop listing.
 */
@Composable
private fun BuyerListingDetailsDialog(
    listing: MarketListingDto,
    onDismiss: () -> Unit,
    onContactClick: () -> Unit
) {
    val cropName = listing.cropName ?: "Crop"
    val unit = listing.unit ?: "Quintal"
    val price = listing.pricePerUnit ?: getDefaultCropPrice(cropName)
    val qty = listing.quantity ?: 1.0
    val totalEst = (qty * price).toInt()

    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(24.dp),
            color = Color.White,
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp)
                .shadow(24.dp, RoundedCornerShape(24.dp))
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(22.dp)
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Crop Details",
                        fontWeight = FontWeight.Bold,
                        fontSize = 18.sp,
                        color = Color(0xFF111827)
                    )
                    IconButton(onClick = onDismiss, modifier = Modifier.size(28.dp)) {
                        Icon(Icons.Rounded.Close, contentDescription = "Close", tint = Color.Gray)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Crop Image Preview
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(150.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(Color(0xFFF3F4F6))
                ) {
                    CropThumbnailGraphic(
                        cropName = cropName,
                        mediaUrls = listing.mediaUrls
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Crop Name & Total
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = cropName,
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 20.sp,
                            color = Color(0xFF111827)
                        )
                        Text(
                            text = "Listed by verified farmer",
                            fontSize = 12.sp,
                            color = Color(0xFF16A34A),
                            fontWeight = FontWeight.Medium
                        )
                    }

                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "₹$totalEst",
                            fontWeight = FontWeight.Black,
                            fontSize = 20.sp,
                            color = Color(0xFF166534)
                        )
                        Text(
                            text = "Est. Total",
                            fontSize = 11.sp,
                            color = Color(0xFF6B7280)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(14.dp))

                // Key Info Chips Row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = Color(0xFFF3F4F6),
                        modifier = Modifier.weight(1f)
                    ) {
                        Column(modifier = Modifier.padding(10.dp)) {
                            Text(text = "Available", fontSize = 10.sp, color = Color(0xFF6B7280))
                            Text(text = "${qty.toInt()} $unit", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = Color(0xFF111827))
                        }
                    }

                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = Color(0xFFF3F4F6),
                        modifier = Modifier.weight(1f)
                    ) {
                        Column(modifier = Modifier.padding(10.dp)) {
                            Text(text = "Rate", fontSize = 10.sp, color = Color(0xFF6B7280))
                            Text(text = "₹${price.toInt()} / $unit", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = Color(0xFF111827))
                        }
                    }

                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = Color(0xFFF3F4F6),
                        modifier = Modifier.weight(1f)
                    ) {
                        Column(modifier = Modifier.padding(10.dp)) {
                            Text(text = "Location", fontSize = 10.sp, color = Color(0xFF6B7280))
                            Text(
                                text = listing.locationName ?: "Rajasthan",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF111827),
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }
                }

                if (!listing.description.isNullOrBlank()) {
                    Spacer(modifier = Modifier.height(14.dp))
                    Text(text = "Farmer's Note", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = Color(0xFF374151))
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = listing.description,
                        fontSize = 13.sp,
                        color = Color(0xFF4B5563),
                        lineHeight = 18.sp
                    )
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Contact Farmer CTA Button
                Button(
                    onClick = {
                        onDismiss()
                        onContactClick()
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    shape = RoundedCornerShape(14.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF166534),
                        contentColor = Color.White
                    )
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Icon(Icons.Rounded.Call, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Contact Seller / Farmer",
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                    }
                }
            }
        }
    }
}
