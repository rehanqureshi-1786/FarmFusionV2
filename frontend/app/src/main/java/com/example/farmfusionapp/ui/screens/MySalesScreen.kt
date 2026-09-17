package com.example.farmfusionapp.ui.screens

import android.widget.Toast
import androidx.compose.animation.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.MoreVert
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
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.navigation.NavController
import coil.compose.AsyncImage
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.MarketListingDto
import com.example.farmfusionapp.data.model.MarketListingStore
import com.example.farmfusionapp.data.model.getDefaultCropPrice
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MySalesScreen(navController: NavController) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var isRefreshing by remember { mutableStateOf(false) }
    var selectedListingForDetails by remember { mutableStateOf<MarketListingDto?>(null) }
    var listingToDelete by remember { mutableStateOf<MarketListingDto?>(null) }

    // Read reactive local listings from MarketListingStore
    val listings = MarketListingStore.localListings

    // Fetch latest listings from PostgreSQL backend on launch
    LaunchedEffect(Unit) {
        try {
            val response = withContext(Dispatchers.IO) {
                RetrofitInstance.api.getMarketListings()
            }
            if (response.isSuccessful && response.body() != null) {
                val serverListings = response.body()!!
                MarketListingStore.setListings(serverListings)
            }
        } catch (e: Exception) {
            // Offline or backend unavailable: local store keeps working seamlessly
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFFCFDFC))
    ) {
        // Bottom Background Illustration: Sack of grains and leaves
        Image(
            painter = painterResource(id = R.drawable.ill_crop_bottom_bg),
            contentDescription = null,
            contentScale = ContentScale.FillWidth,
            alpha = 0.95f,
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
                            text = "My Sales",
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
                    },
                    actions = {
                        IconButton(
                            onClick = {
                                coroutineScope.launch {
                                    isRefreshing = true
                                    try {
                                        val res = withContext(Dispatchers.IO) {
                                            RetrofitInstance.api.getMarketListings()
                                        }
                                        if (res.isSuccessful && res.body() != null) {
                                            MarketListingStore.setListings(res.body()!!)
                                            Toast.makeText(context, "Sales updated", Toast.LENGTH_SHORT).show()
                                        }
                                    } catch (e: Exception) {
                                        Toast.makeText(context, "Up to date", Toast.LENGTH_SHORT).show()
                                    } finally {
                                        isRefreshing = false
                                    }
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
            },
            floatingActionButton = {
                FloatingActionButton(
                    onClick = { navController.navigate(NavRoutes.ListMyCrop) },
                    containerColor = Color(0xFF2E7D32),
                    contentColor = Color.White,
                    shape = CircleShape,
                    elevation = FloatingActionButtonDefaults.elevation(6.dp),
                    modifier = Modifier.padding(bottom = 16.dp, end = 8.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Add,
                        contentDescription = "List My Crop",
                        modifier = Modifier.size(26.dp)
                    )
                }
            }
        ) { padding ->
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 4.dp, bottom = 120.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Section Header
                item {
                    Column(modifier = Modifier.padding(bottom = 6.dp)) {
                        Text(
                            text = "Track Your Sales",
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 24.sp,
                            color = Color(0xFF111827)
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Manage your listed crops and check their status.",
                            fontSize = 13.5.sp,
                            color = Color(0xFF6B7280)
                        )
                    }
                }

                // Crop Listing Cards
                if (listings.isEmpty()) {
                    item {
                        EmptySalesState(onListCropClick = { navController.navigate(NavRoutes.ListMyCrop) })
                    }
                } else {
                    items(listings, key = { it.id ?: it.hashCode() }) { listing ->
                        SaleCropCard(
                            listing = listing,
                            onClick = { selectedListingForDetails = listing },
                            onMarkSold = {
                                listing.id?.let { id ->
                                    MarketListingStore.toggleSoldStatus(id)
                                    coroutineScope.launch {
                                        try {
                                            val newActive = !(listing.isActive ?: true)
                                            withContext(Dispatchers.IO) {
                                                RetrofitInstance.api.updateMarketListingStatus(id, newActive)
                                            }
                                        } catch (e: Exception) {
                                            // Handled locally
                                        }
                                    }
                                    val statusMsg = if (listing.isActive == false) "Marked as active" else "Marked as sold"
                                    Toast.makeText(context, statusMsg, Toast.LENGTH_SHORT).show()
                                }
                            },
                            onDelete = {
                                listingToDelete = listing
                            }
                        )
                    }
                }
            }
        }
    }

    // Delete Confirmation Dialog
    listingToDelete?.let { listing ->
        AlertDialog(
            onDismissRequest = { listingToDelete = null },
            title = { Text(text = "Delete Listing?", fontWeight = FontWeight.Bold, color = Color(0xFF111827)) },
            text = { Text(text = "Are you sure you want to remove ${listing.cropName} from your listed sales?") },
            confirmButton = {
                TextButton(
                    onClick = {
                        listing.id?.let { id ->
                            MarketListingStore.removeListing(id)
                            coroutineScope.launch {
                                try {
                                    withContext(Dispatchers.IO) {
                                        RetrofitInstance.api.deleteMarketListing(id)
                                    }
                                } catch (e: Exception) {
                                    // Removed locally
                                }
                            }
                            Toast.makeText(context, "Listing deleted", Toast.LENGTH_SHORT).show()
                        }
                        listingToDelete = null
                    }
                ) {
                    Text(text = "Delete", color = Color(0xFFDC2626), fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { listingToDelete = null }) {
                    Text(text = "Cancel", color = Color(0xFF6B7280))
                }
            }
        )
    }

    // Details Dialog
    selectedListingForDetails?.let { listing ->
        ListingDetailsDialog(
            listing = listing,
            onDismiss = { selectedListingForDetails = null }
        )
    }
}

/**
 * Individual Crop Sale Card matching the design from the reference screenshot.
 */
@Composable
private fun SaleCropCard(
    listing: MarketListingDto,
    onClick: () -> Unit,
    onMarkSold: () -> Unit,
    onDelete: () -> Unit
) {
    var menuExpanded by remember { mutableStateOf(false) }

    val formattedDate = remember(listing.createdAt) {
        formatListingDate(listing.createdAt)
    }

    val price = listing.pricePerUnit ?: getDefaultCropPrice(listing.cropName)
    val isSold = listing.isActive == false

    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(18.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFF1F3F5)),
        modifier = Modifier
            .fillMaxWidth()
            .shadow(
                elevation = 2.dp,
                shape = RoundedCornerShape(18.dp),
                spotColor = Color.Black.copy(alpha = 0.05f),
                ambientColor = Color.Black.copy(alpha = 0.02f)
            )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 1. Left: Crop Thumbnail (72.dp x 72.dp)
            Box(
                modifier = Modifier
                    .size(72.dp)
                    .clip(RoundedCornerShape(14.dp))
                    .background(Color(0xFFF4F6F4))
            ) {
                CropThumbnailGraphic(
                    cropName = listing.cropName ?: "Crop",
                    mediaUrls = listing.mediaUrls
                )

                if (isSold) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(Color.Black.copy(alpha = 0.45f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = Color(0xFFDC2626)
                        ) {
                            Text(
                                text = "SOLD",
                                color = Color.White,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.ExtraBold,
                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 1.dp)
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.width(14.dp))

            // 2. Middle: Crop Details (Title, Quantity, Location, Date)
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(3.dp)
            ) {
                Text(
                    text = listing.cropName ?: "Unknown Crop",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    color = Color(0xFF111827),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                val qtyText = if (listing.quantity != null) {
                    val formatted = if (listing.quantity % 1.0 == 0.0) listing.quantity.toInt().toString() else listing.quantity.toString()
                    "$formatted ${listing.unit ?: "Quintals"}"
                } else {
                    "Quantity not set"
                }

                Text(
                    text = qtyText,
                    fontSize = 13.sp,
                    color = Color(0xFF6B7280),
                    fontWeight = FontWeight.Medium
                )

                // Location with pin icon
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Rounded.Place,
                        contentDescription = null,
                        tint = Color(0xFF9CA3AF),
                        modifier = Modifier.size(13.5.dp)
                    )
                    Spacer(modifier = Modifier.width(3.dp))
                    Text(
                        text = listing.locationName?.ifBlank { "Location not specified" } ?: "Location not specified",
                        fontSize = 12.sp,
                        color = Color(0xFF6B7280),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                // Date with calendar icon
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Rounded.CalendarToday,
                        contentDescription = null,
                        tint = Color(0xFF9CA3AF),
                        modifier = Modifier.size(12.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Listed on $formattedDate",
                        fontSize = 11.5.sp,
                        color = Color(0xFF6B7280),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }

            // 3. Right: 3-dots Menu + Price per Quintal
            Column(
                horizontalAlignment = Alignment.End,
                verticalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.height(72.dp)
            ) {
                // 3-dots Menu Button
                Box {
                    IconButton(
                        onClick = { menuExpanded = true },
                        modifier = Modifier.size(24.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.MoreVert,
                            contentDescription = "Options",
                            tint = Color(0xFF9CA3AF),
                            modifier = Modifier.size(18.dp)
                        )
                    }

                    DropdownMenu(
                        expanded = menuExpanded,
                        onDismissRequest = { menuExpanded = false },
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        DropdownMenuItem(
                            text = { Text(if (isSold) "Mark as Active" else "Mark as Sold") },
                            leadingIcon = {
                                Icon(
                                    imageVector = if (isSold) Icons.Rounded.Refresh else Icons.Rounded.CheckCircle,
                                    contentDescription = null,
                                    tint = if (isSold) Color(0xFF2E7D32) else Color(0xFF16A34A),
                                    modifier = Modifier.size(18.dp)
                                )
                            },
                            onClick = {
                                menuExpanded = false
                                onMarkSold()
                            }
                        )

                        DropdownMenuItem(
                            text = { Text("View Details") },
                            leadingIcon = {
                                Icon(
                                    imageVector = Icons.Rounded.Info,
                                    contentDescription = null,
                                    tint = Color(0xFF3B82F6),
                                    modifier = Modifier.size(18.dp)
                                )
                            },
                            onClick = {
                                menuExpanded = false
                                onClick()
                            }
                        )

                        HorizontalDivider(modifier = Modifier.padding(vertical = 4.dp))

                        DropdownMenuItem(
                            text = { Text("Delete Listing", color = Color(0xFFDC2626)) },
                            leadingIcon = {
                                Icon(
                                    imageVector = Icons.Rounded.Delete,
                                    contentDescription = null,
                                    tint = Color(0xFFDC2626),
                                    modifier = Modifier.size(18.dp)
                                )
                            },
                            onClick = {
                                menuExpanded = false
                                onDelete()
                            }
                        )
                    }
                }

                // Price
                Column(horizontalAlignment = Alignment.End) {
                    val priceStr = "₹" + String.format(Locale.US, "%,.0f", price)
                    Text(
                        text = priceStr,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 16.sp,
                        color = Color(0xFF15803D)
                    )
                    Text(
                        text = "per ${listing.unit ?: "Quintal"}",
                        fontSize = 10.5.sp,
                        color = Color(0xFF6B7280),
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

/**
 * Renders the crop thumbnail:
 * If user uploaded photos, displays the first one using Coil AsyncImage.
 * Otherwise, renders an authentic photo or graphic matching the reference.
 */
@Composable
internal fun CropThumbnailGraphic(
    cropName: String,
    mediaUrls: List<String>?
) {
    if (!mediaUrls.isNullOrEmpty()) {
        AsyncImage(
            model = mediaUrls.first(),
            contentDescription = cropName,
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize()
        )
        return
    }

    val lower = cropName.lowercase()
    when {
        lower.contains("wheat") -> {
            // Wheat Photo / Visual
            Image(
                painter = painterResource(id = R.drawable.img_wheat_seeds),
                contentDescription = cropName,
                contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize()
            )
        }
        lower.contains("rice") || lower.contains("paddy") -> {
            // Rice bowl visual
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        Brush.radialGradient(
                            colors = listOf(Color(0xFFFFFBEB), Color(0xFFE8E0D2))
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Rounded.Grain,
                    contentDescription = null,
                    tint = Color(0xFFB45309),
                    modifier = Modifier.size(36.dp)
                )
            }
        }
        lower.contains("onion") -> {
            // Soft graphic illustration matching the 3rd card in reference:
            // Light mint background with seedling and warm sun!
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color(0xFFE8F5E9)),
                contentAlignment = Alignment.Center
            ) {
                // Sun in top right
                Box(
                    modifier = Modifier
                        .size(16.dp)
                        .offset(x = 14.dp, y = (-14).dp)
                        .background(Color(0xFFFDE68A), CircleShape)
                )
                // Sprouting plant in center
                Icon(
                    imageVector = Icons.Rounded.Eco,
                    contentDescription = null,
                    tint = Color(0xFF2E7D32),
                    modifier = Modifier.size(36.dp)
                )
            }
        }
        lower.contains("maize") || lower.contains("corn") -> {
            // Yellow maize visual
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(Color(0xFFFEF3C7), Color(0xFFFDE047))
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Rounded.Grass,
                    contentDescription = null,
                    tint = Color(0xFFCA8A04),
                    modifier = Modifier.size(36.dp)
                )
            }
        }
        else -> {
            // Clean organic fallback avatar
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color(0xFFEAF5EC)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Rounded.Spa,
                    contentDescription = null,
                    tint = Color(0xFF2E7D32),
                    modifier = Modifier.size(32.dp)
                )
            }
        }
    }
}

/**
 * Formats ISO date string to "12 Sep 2025" style.
 */
internal fun formatListingDate(isoDate: String?): String {
    if (isoDate.isNullOrBlank()) {
        return SimpleDateFormat("dd MMM yyyy", Locale.US).format(Date())
    }
    return try {
        val parser = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
        val date = parser.parse(isoDate)
        if (date != null) {
            val formatter = SimpleDateFormat("dd MMM yyyy", Locale.US)
            formatter.format(date)
        } else {
            isoDate.substring(0, 10.coerceAtMost(isoDate.length))
        }
    } catch (e: Exception) {
        try {
            val simple = SimpleDateFormat("yyyy-MM-dd", Locale.US)
            val date = simple.parse(isoDate)
            if (date != null) {
                SimpleDateFormat("dd MMM yyyy", Locale.US).format(date)
            } else {
                SimpleDateFormat("dd MMM yyyy", Locale.US).format(Date())
            }
        } catch (ex: Exception) {
            SimpleDateFormat("dd MMM yyyy", Locale.US).format(Date())
        }
    }
}

/**
 * Full Listing Details Modal Dialog.
 */
@Composable
private fun ListingDetailsDialog(
    listing: MarketListingDto,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(24.dp),
            color = Color.White,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Header with Close
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = listing.cropName ?: "Crop",
                            fontWeight = FontWeight.Bold,
                            fontSize = 20.sp,
                            color = Color(0xFF111827)
                        )
                        Text(
                            text = if (listing.isActive == false) "Status: Sold" else "Status: Active on Marketplace",
                            fontSize = 12.sp,
                            color = if (listing.isActive == false) Color(0xFFDC2626) else Color(0xFF16A34A),
                            fontWeight = FontWeight.SemiBold
                        )
                    }

                    IconButton(onClick = onDismiss) {
                        Icon(
                            imageVector = Icons.Rounded.Close,
                            contentDescription = "Close",
                            tint = Color(0xFF6B7280)
                        )
                    }
                }

                // Media Gallery (if photos attached)
                if (!listing.mediaUrls.isNullOrEmpty()) {
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        items(listing.mediaUrls) { url ->
                            Box(
                                modifier = Modifier
                                    .size(90.dp)
                                    .clip(RoundedCornerShape(12.dp))
                                    .border(1.dp, Color(0xFFE5E7EB), RoundedCornerShape(12.dp))
                            ) {
                                AsyncImage(
                                    model = url,
                                    contentDescription = null,
                                    contentScale = ContentScale.Crop,
                                    modifier = Modifier.fillMaxSize()
                                )
                            }
                        }
                    }
                }

                HorizontalDivider(color = Color(0xFFF3F4F6))

                // Metadata Rows
                DetailRow(
                    icon = Icons.Rounded.Scale,
                    label = "Quantity",
                    value = "${listing.quantity ?: 0.0} ${listing.unit ?: "Quintals"}"
                )

                val price = listing.pricePerUnit ?: getDefaultCropPrice(listing.cropName)
                DetailRow(
                    icon = Icons.Rounded.CurrencyRupee,
                    label = "Expected Rate",
                    value = "₹" + String.format(Locale.US, "%,.0f", price) + " / Quintal"
                )

                DetailRow(
                    icon = Icons.Rounded.Place,
                    label = "Location",
                    value = listing.locationName?.ifBlank { "Location not specified" } ?: "Location not specified"
                )

                DetailRow(
                    icon = Icons.Rounded.CalendarMonth,
                    label = "Listed Date",
                    value = formatListingDate(listing.createdAt)
                )

                // Description
                if (!listing.description.isNullOrBlank()) {
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(
                            text = "Description",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF374151)
                        )
                        Text(
                            text = listing.description,
                            fontSize = 13.sp,
                            color = Color(0xFF4B5563),
                            lineHeight = 18.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.height(4.dp))

                Button(
                    onClick = onDismiss,
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(text = "Close", fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
private fun DetailRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    value: String
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier.fillMaxWidth()
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = Color(0xFF2E7D32),
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = "$label: ",
            fontSize = 13.sp,
            color = Color(0xFF6B7280),
            fontWeight = FontWeight.Medium
        )
        Text(
            text = value,
            fontSize = 13.5.sp,
            color = Color(0xFF111827),
            fontWeight = FontWeight.SemiBold
        )
    }
}

@Composable
private fun EmptySalesState(onListCropClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 40.dp, horizontal = 20.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Box(
            modifier = Modifier
                .size(72.dp)
                .background(Color(0xFFE8F5E9), CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Rounded.Inventory2,
                contentDescription = null,
                tint = Color(0xFF2E7D32),
                modifier = Modifier.size(36.dp)
            )
        }

        Text(
            text = "No Crops Listed Yet",
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp,
            color = Color(0xFF111827)
        )

        Text(
            text = "List your crops to reach buyers directly and keep track of all your sales here.",
            fontSize = 13.sp,
            color = Color(0xFF6B7280),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )

        Spacer(modifier = Modifier.height(6.dp))

        Button(
            onClick = onListCropClick,
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
        ) {
            Text(text = "List Your First Crop", fontWeight = FontWeight.Bold)
        }
    }
}
