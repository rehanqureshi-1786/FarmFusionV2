package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.automirrored.rounded.CompareArrows
import androidx.compose.material.icons.automirrored.rounded.TrendingUp
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.window.DialogWindowProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.SubcomposeAsyncImage
import coil.request.ImageRequest
import com.example.farmfusionapp.data.model.*
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.utils.commodityHeroImageUrl
import com.example.farmfusionapp.utils.LocationSnapshotStore
import com.example.farmfusionapp.viewmodel.MarketViewModel
import com.example.farmfusionapp.viewmodel.ProductViewModel
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MandiPricesScreen(
    navController: NavController,
    viewModel: MarketViewModel = viewModel(),
    productViewModel: ProductViewModel = viewModel()
) {
    val coroutineScope = rememberCoroutineScope()
    var selectedCategory by remember { mutableStateOf("ALL CROPS") }
    var searchQuery by remember { mutableStateOf("") }

    val pricesState by viewModel.pricesState
    val categories = listOf("ALL CROPS", "GRAINS", "VEGETABLES", "PULSES", "FRUITS", "SPICES")

    // Comprehensive default crop list (covers 30+ high-volume Agmarknet crops)
    val defaultCrops = listOf(
        "Wheat", "Gram", "Mustard", "Soybean", "Cotton", "Groundnut", "Paddy (Dhan)",
        "Onion", "Tomato", "Potato", "Maize", "Bajra", "Garlic", "Moong", "Urad",
        "Arhar (Tur)", "Cumin (Jeera)", "Coriander", "Turmeric", "Green Chilli", "Dry Chillies",
        "Barley", "Apple", "Banana", "Mango", "Pomegranate", "Ginger", "Guar Seed"
    )
    var allAvailableCrops by remember { mutableStateOf(defaultCrops) }

    // Prominent mandis for quick suggestion
    val prominentMandis = listOf("Udaipur", "Jaipur", "Kota", "Jodhpur", "Bikaner", "Indore", "Amreli", "Rajkot", "Nashik", "Ludhiana", "Karnal", "Agra")

    // =========================================================================
    // GUIDED ACTION FLOW STATES
    // =========================================================================

    // 1. Best Nearby Flow State
    var showNearbyDialog by remember { mutableStateOf(false) }
    var nearbySelectedCrop by remember { mutableStateOf("Wheat") }
    var nearbyCropInput by remember { mutableStateOf("Wheat") }
    var nearbyResult by remember { mutableStateOf<BestMandiResponseModel?>(null) }
    var isNearbyLoading by remember { mutableStateOf(false) }

    // 2. Compare Flow State
    var showCompareDialog by remember { mutableStateOf(false) }
    var compareCrop by remember { mutableStateOf("Wheat") }
    var compareMarketA by remember { mutableStateOf(LocationSnapshotStore.latestCity ?: "") }
    var compareMarketB by remember { mutableStateOf("") }
    var compareResult by remember { mutableStateOf<MandiComparisonResponseModel?>(null) }
    var compareError by remember { mutableStateOf<String?>(null) }
    var isCompareLoading by remember { mutableStateOf(false) }

    // 3. Sell vs Wait Flow State
    var showAdvisoryDialog by remember { mutableStateOf(false) }
    var advisoryCrop by remember { mutableStateOf("Wheat") }
    var advisoryMarket by remember { mutableStateOf(LocationSnapshotStore.latestCity ?: "") }
    var advisoryResult by remember { mutableStateOf<MandiAdvisoryResponseModel?>(null) }
    var advisoryError by remember { mutableStateOf<String?>(null) }
    var isAdvisoryLoading by remember { mutableStateOf(false) }

    // 4. Set Alert Flow State
    var showAlertModal by remember { mutableStateOf(false) }
    var alertCrop by remember { mutableStateOf("Wheat") }
    var alertMarket by remember { mutableStateOf(LocationSnapshotStore.latestCity ?: "") }
    var alertCondition by remember { mutableStateOf("ABOVE") } // ABOVE, BELOW
    var alertTargetValue by remember { mutableStateOf("2600") }
    var alertSuccessMsg by remember { mutableStateOf<String?>(null) }
    var alertError by remember { mutableStateOf<String?>(null) }
    var isAlertLoading by remember { mutableStateOf(false) }

    // Dynamic blur based on any dialog open state
    val isAnyDialogOpen = showNearbyDialog || showCompareDialog || showAdvisoryDialog || showAlertModal
    val blurRadius by animateDpAsState(
        targetValue = if (isAnyDialogOpen) 16.dp else 0.dp,
        animationSpec = tween(durationMillis = 300),
        label = "dialog_blur"
    )

    LaunchedEffect(Unit) {
        viewModel.getMarketPrices()
        productViewModel.loadProducts(null)
        coroutineScope.launch {
            try {
                val commRes = RetrofitInstance.api.getCommodities()
                if (commRes.isSuccessful && commRes.body() != null && commRes.body()!!.isNotEmpty()) {
                    allAvailableCrops = commRes.body()!!
                }
            } catch (_: Exception) {}
        }
    }

    NeoScaffoldBackground(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            containerColor = Color.Transparent,
            modifier = Modifier.blur(radius = blurRadius), // Applies true blur to the screen content
            topBar = {
                CenterAlignedTopAppBar(
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent,
                        scrolledContainerColor = Color.Transparent
                    ),
                    title = {
                        Text(
                            "Market Prices & Intelligence",
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1A1A1A)
                        )
                    },
                    navigationIcon = {
                        IconButton(onClick = { navController.popBackStack() }) {
                            Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", tint = Color(0xFF1A1A1A))
                        }
                    }
                )
            }
        ) { padding ->
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(top = 12.dp, bottom = 40.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp)
            ) {
                // Search Bar
                item {
                    Surface(
                        shape = RoundedCornerShape(24.dp),
                        color = Color.White.copy(alpha = 0.95f),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp)
                            .shadow(
                                elevation = 12.dp,
                                shape = RoundedCornerShape(24.dp),
                                spotColor = Color.Black.copy(alpha = 0.04f),
                                ambientColor = Color.Transparent
                            ),
                        border = null
                    ) {
                        TextField(
                            value = searchQuery,
                            onValueChange = { searchQuery = it },
                            placeholder = { Text("Search crops (e.g. Wheat, Gram, Mustard), mandis...") },
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

                // High-Value Guided Farmer Action Cards (2x2 Prominent Grid)
                item {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            // 1. Best Nearby
                            MandiIntelligenceCard(
                                title = "Best Nearby",
                                subtitle = "Highest net price market",
                                icon = Icons.Rounded.NearMe,
                                bgColor = Color(0xFFD3F8E5),
                                iconTint = Color(0xFF047857),
                                modifier = Modifier.weight(1f),
                                onClick = { showNearbyDialog = true }
                            )

                            // 2. Compare Mandis
                            MandiIntelligenceCard(
                                title = "Compare",
                                subtitle = "Side-by-side mandi rates",
                                icon = Icons.AutoMirrored.Rounded.CompareArrows,
                                bgColor = Color(0xFFE2EAFB),
                                iconTint = Color(0xFF1D4ED8),
                                modifier = Modifier.weight(1f),
                                onClick = {
                                    compareError = null
                                    showCompareDialog = true
                                }
                            )
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            // 3. Sell vs Wait Advisory
                            MandiIntelligenceCard(
                                title = "Sell vs Wait",
                                subtitle = "7-day price trajectory",
                                icon = Icons.AutoMirrored.Rounded.TrendingUp,
                                bgColor = Color(0xFFF1EAFF),
                                iconTint = Color(0xFF6D28D9),
                                modifier = Modifier.weight(1f),
                                onClick = {
                                    advisoryError = null
                                    showAdvisoryDialog = true
                                }
                            )

                            // 4. Set Alert
                            MandiIntelligenceCard(
                                title = "Set Alert",
                                subtitle = "Notify on target prices",
                                icon = Icons.Rounded.NotificationsActive,
                                bgColor = Color(0xFFFFF4D9),
                                iconTint = Color(0xFFD97706),
                                modifier = Modifier.weight(1f),
                                onClick = {
                                    alertError = null
                                    alertSuccessMsg = null
                                    showAlertModal = true
                                }
                            )
                        }
                    }
                }

                // Category Tabs (Edge-to-Edge Scroll)
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
                                    modifier = Modifier.padding(horizontal = 18.dp, vertical = 10.dp),
                                    style = MaterialTheme.typography.labelLarge.copy(
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        color = if (isSelected) Color.White else Color(0xFF1B1B1B)
                                    )
                                )
                            }
                        }
                    }
                }

                // Mandi Price List
                when (val state = pricesState) {
                    is MarketViewModel.MarketPricesState.Loading -> {
                        item { Box(Modifier.fillMaxWidth().height(100.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Color(0xFF1B4332)) } }
                    }
                    is MarketViewModel.MarketPricesState.Success -> {
                        val filtered = state.response.data.filter {
                            (searchQuery.isEmpty() || it.commodity.contains(searchQuery, true) || it.market.contains(searchQuery, true) || it.district.contains(searchQuery, true)) &&
                                    (selectedCategory == "ALL CROPS" || isCropInCategory(it.commodity, selectedCategory))
                        }

                        if (filtered.isEmpty()) {
                            item {
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(horizontal = 20.dp)
                                        .height(140.dp)
                                        .padding(top = 20.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        "No mandi price results found for '$searchQuery'. Try searching another crop like Wheat, Gram, Mustard, Soybean, or clear search.",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = Color.Gray,
                                        textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                        modifier = Modifier.padding(16.dp)
                                    )
                                }
                            }
                        } else {
                            items(filtered.take(30)) { item ->
                                PriceCard(
                                    item = item,
                                    modifier = Modifier.padding(horizontal = 20.dp)
                                )
                            }
                        }
                    }
                    is MarketViewModel.MarketPricesState.Error -> {
                        item {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 20.dp)
                                    .height(140.dp)
                                    .padding(top = 20.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = "Unable to load mandi prices: ${state.message}",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.error,
                                    textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                    modifier = Modifier.padding(16.dp)
                                )
                            }
                        }
                    }
                    else -> {}
                }
            }
        }
    }

    // =========================================================================
    // 1. GUIDED BEST PRACTICAL MANDI DIALOG
    // =========================================================================
    if (showNearbyDialog) {
        PremiumBlurDialog(
            onDismissRequest = { showNearbyDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.Rounded.NearMe, null, tint = Color(0xFF10B981))
                    Text("Best Nearby Mandi", fontWeight = FontWeight.Bold)
                }
            },
            content = {
                Column(
                    modifier = Modifier.fillMaxWidth().heightIn(max = 500.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Text("Step 1: Search / Select Any Crop", style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Bold, color = Color.DarkGray))

                    // Crop Search / Input Field
                    OutlinedTextField(
                        value = nearbyCropInput,
                        onValueChange = {
                            nearbyCropInput = it
                            nearbySelectedCrop = it
                        },
                        placeholder = { Text("Search crop e.g. Wheat, Gram, Mustard...") },
                        leadingIcon = { Icon(Icons.Rounded.Search, null, tint = Color.Gray) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    // Matching Crop Suggestions & Popular Chips
                    val matchingNearbyCrops = allAvailableCrops.filter {
                        nearbyCropInput.isBlank() || it.contains(nearbyCropInput, ignoreCase = true)
                    }.take(10)

                    LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        items(matchingNearbyCrops) { crop ->
                            val isSel = crop.equals(nearbySelectedCrop, ignoreCase = true)
                            FilterChip(
                                selected = isSel,
                                onClick = {
                                    nearbySelectedCrop = crop
                                    nearbyCropInput = crop
                                    isNearbyLoading = true
                                    coroutineScope.launch {
                                        try {
                                            val res = RetrofitInstance.api.getBestNearbyMandis(commodity = crop)
                                            if (res.isSuccessful) nearbyResult = res.body()
                                        } catch (_: Exception) {}
                                        finally { isNearbyLoading = false }
                                    }
                                },
                                label = { Text(crop, fontSize = 11.sp) }
                            )
                        }
                    }

                    if (isNearbyLoading) {
                        Box(Modifier.fillMaxWidth().height(140.dp), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator(color = Color(0xFF10B981))
                        }
                    } else if (nearbyResult != null) {
                        val res = nearbyResult!!
                        val practical = res.best_practical_mandi ?: res.best_mandi
                        val highest = res.highest_price_mandi

                        LazyColumn(
                            modifier = Modifier.fillMaxWidth().heightIn(max = 320.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            // 1. BEST PRACTICAL OPTION CARD
                            if (practical != null) {
                                item {
                                    Surface(
                                        shape = RoundedCornerShape(12.dp),
                                        color = Color(0xFFECFDF5),
                                        border = BorderStroke(1.5.dp, Color(0xFF10B981)),
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        Column(modifier = Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                            Row(
                                                modifier = Modifier.fillMaxWidth(),
                                                horizontalArrangement = Arrangement.SpaceBetween,
                                                verticalAlignment = Alignment.CenterVertically
                                            ) {
                                                Surface(shape = RoundedCornerShape(6.dp), color = Color(0xFF10B981)) {
                                                    Text(
                                                        "⭐ Best Practical Option",
                                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                                        style = MaterialTheme.typography.labelSmall.copy(color = Color.White, fontWeight = FontWeight.Bold, fontSize = 10.sp)
                                                    )
                                                }
                                                Text("Score: ${practical.practical_score}", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = Color(0xFF047857)))
                                            }

                                            Row(
                                                modifier = Modifier.fillMaxWidth(),
                                                horizontalArrangement = Arrangement.SpaceBetween,
                                                verticalAlignment = Alignment.Bottom
                                            ) {
                                                Column {
                                                    Text(practical.market, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodyMedium)
                                                    Text(
                                                        "${practical.district}" + (if (practical.distance_km != null) " • ${practical.distance_km} km away" else ""),
                                                        style = MaterialTheme.typography.labelSmall.copy(color = Color.DarkGray)
                                                    )
                                                }
                                                Text("₹${practical.modal_price.toInt()}/Q", fontWeight = FontWeight.Black, style = MaterialTheme.typography.titleMedium, color = Color(0xFF10B981))
                                            }

                                            if (practical.ranking_reason.isNotBlank()) {
                                                Text(practical.ranking_reason, style = MaterialTheme.typography.labelSmall.copy(color = Color(0xFF065F46), fontSize = 10.sp))
                                            }
                                        }
                                    }
                                }
                            }

                            // 2. HIGHEST RECORDED PRICE CARD
                            if (highest != null && (practical == null || highest.market != practical.market)) {
                                item {
                                    Surface(
                                        shape = RoundedCornerShape(10.dp),
                                        color = Color(0xFFFFFBEB),
                                        border = BorderStroke(1.dp, Color(0xFFFCD34D)),
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        Row(
                                            modifier = Modifier.padding(8.dp).fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween,
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Column {
                                                Text("🏆 Highest Recorded: ${highest.market}", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelSmall.copy(color = Color(0xFF92400E)))
                                                Text("${highest.district}" + (if (highest.distance_km != null) " • ${highest.distance_km} km" else ""), style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp, color = Color.Gray))
                                            }
                                            Text("₹${highest.modal_price.toInt()}/Q", fontWeight = FontWeight.Bold, color = Color(0xFFD97706), style = MaterialTheme.typography.bodyMedium)
                                        }
                                    }
                                }
                            }

                            // 3. NEARBY ALTERNATIVES
                            val alternatives = res.ranked_mandis.filter { it.market != practical?.market && it.market != highest?.market }
                            if (alternatives.isNotEmpty()) {
                                item {
                                    Text("Nearby Alternatives", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = Color.Gray))
                                }
                                items(alternatives) { m ->
                                    Surface(
                                        shape = RoundedCornerShape(8.dp),
                                        color = Color(0xFFF9FAFB),
                                        border = BorderStroke(1.dp, Color(0xFFE5E7EB)),
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        Row(
                                            modifier = Modifier.padding(8.dp),
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Column {
                                                Text(m.market, fontWeight = FontWeight.SemiBold, style = MaterialTheme.typography.labelMedium)
                                                Text("${m.district}" + (if (m.distance_km != null) " • ${m.distance_km} km" else "") + " • ${m.freshness_status}", style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp, color = Color.Gray))
                                            }
                                            Text("₹${m.modal_price.toInt()}/Q", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelLarge)
                                        }
                                    }
                                }
                            }

                            item {
                                Text(res.disclaimer, style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp, color = Color.Gray))
                            }
                        }
                    } else {
                        Button(
                            onClick = {
                                if (nearbyCropInput.isNotBlank()) {
                                    isNearbyLoading = true
                                    coroutineScope.launch {
                                        try {
                                            val res = RetrofitInstance.api.getBestNearbyMandis(commodity = nearbyCropInput.trim())
                                            if (res.isSuccessful) nearbyResult = res.body()
                                        } catch (_: Exception) {}
                                        finally { isNearbyLoading = false }
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF10B981)),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Find Best Nearby Mandis for $nearbyCropInput")
                        }
                    }
                }
            },
            confirmButton = { TextButton(onClick = { showNearbyDialog = false }) { Text("Done") } }
        )
    }

    // =========================================================================
    // 2. GUIDED MANDI COMPARISON DIALOG
    // =========================================================================
    if (showCompareDialog) {
        PremiumBlurDialog(
            onDismissRequest = { showCompareDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.AutoMirrored.Rounded.CompareArrows, null, tint = Color(0xFF3B82F6))
                    Text("Compare Mandi Prices", fontWeight = FontWeight.Bold)
                }
            },
            content = {
                Column(
                    modifier = Modifier.fillMaxWidth().heightIn(max = 520.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Step 1: Crop Selection / Search
                    Text("Step 1: Crop / फसल (Search or Select)", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    OutlinedTextField(
                        value = compareCrop,
                        onValueChange = {
                            compareCrop = it
                            compareResult = null
                        },
                        placeholder = { Text("e.g. Gram, Wheat, Mustard, Soybean...") },
                        leadingIcon = { Icon(Icons.Rounded.Search, null, tint = Color.Gray) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    // Quick Crop Chips
                    val matchingCompareCrops = allAvailableCrops.filter {
                        compareCrop.isBlank() || it.contains(compareCrop, ignoreCase = true)
                    }.take(8)

                    LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        items(matchingCompareCrops) { crop ->
                            FilterChip(
                                selected = crop.equals(compareCrop, ignoreCase = true),
                                onClick = { compareCrop = crop; compareResult = null },
                                label = { Text(crop, fontSize = 11.sp) }
                            )
                        }
                    }

                    // Step 2: Mandi A Selection
                    Text("Step 2: First Mandi / पहली मंडी", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    OutlinedTextField(
                        value = compareMarketA,
                        onValueChange = { compareMarketA = it; compareResult = null },
                        placeholder = { Text("e.g. Udaipur, Kota, Indore") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    // Step 3: Mandi B Selection
                    Text("Step 3: Second Mandi / दूसरी मंडी", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    OutlinedTextField(
                        value = compareMarketB,
                        onValueChange = { compareMarketB = it; compareResult = null },
                        placeholder = { Text("e.g. Jaipur, Jodhpur, Bhopal") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    // Validation Error Banner
                    if (compareError != null) {
                        Text(compareError!!, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold))
                    }

                    // Comparison Button
                    Button(
                        onClick = {
                            if (compareCrop.isBlank()) {
                                compareError = "Please enter or select a crop to compare."
                            } else if (compareMarketA.isBlank() || compareMarketB.isBlank()) {
                                compareError = "Please enter both mandi names."
                            } else if (compareMarketA.trim().equals(compareMarketB.trim(), ignoreCase = true)) {
                                compareError = "Please choose two different mandis to compare."
                            } else {
                                compareError = null
                                isCompareLoading = true
                                coroutineScope.launch {
                                    try {
                                        val res = RetrofitInstance.api.compareMandis(
                                            commodity = compareCrop.trim(),
                                            marketA = compareMarketA.trim(),
                                            marketB = compareMarketB.trim()
                                        )
                                        if (res.isSuccessful) {
                                            compareResult = res.body()
                                        } else {
                                            compareError = "Could not fetch comparison for ${compareCrop.trim()}."
                                        }
                                    } catch (e: Exception) {
                                        compareError = "Could not fetch comparison: ${e.message}"
                                    } finally {
                                        isCompareLoading = false
                                    }
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3B82F6)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Compare Prices")
                    }

                    // Results View
                    if (isCompareLoading) {
                        Box(Modifier.fillMaxWidth().height(80.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Color(0xFF3B82F6)) }
                    } else if (compareResult != null) {
                        val comp = compareResult!!
                        Surface(shape = RoundedCornerShape(12.dp), color = Color(0xFFEFF6FF), border = BorderStroke(1.dp, Color(0xFF93C5FD)), modifier = Modifier.fillMaxWidth()) {
                            Column(modifier = Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text(comp.market_a.market, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodySmall)
                                        Text("₹${comp.market_a.modal_price.toInt()}/Q", fontWeight = FontWeight.Black, color = Color(0xFF1E40AF))
                                    }
                                    Column(modifier = Modifier.weight(1f), horizontalAlignment = Alignment.End) {
                                        Text(comp.market_b.market, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodySmall)
                                        Text("₹${comp.market_b.modal_price.toInt()}/Q", fontWeight = FontWeight.Black, color = Color(0xFF1E40AF))
                                    }
                                }
                                HorizontalDivider(color = Color(0xFFBFDBFE))
                                Text(comp.comparison.summary_hi, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.bodySmall, color = Color(0xFF1E3A8A))
                                Text(comp.comparison.summary_en, style = MaterialTheme.typography.labelSmall.copy(color = Color(0xFF3B82F6), fontSize = 10.sp))
                            }
                        }
                    }
                }
            },
            confirmButton = { TextButton(onClick = { showCompareDialog = false }) { Text("Close") } }
        )
    }

    // =========================================================================
    // 3. GUIDED SELL VS WAIT ADVISORY DIALOG
    // =========================================================================
    if (showAdvisoryDialog) {
        PremiumBlurDialog(
            onDismissRequest = { showAdvisoryDialog = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.AutoMirrored.Rounded.TrendingUp, null, tint = Color(0xFF8B5CF6))
                    Text("Sell vs Wait Advisory", fontWeight = FontWeight.Bold)
                }
            },
            content = {
                Column(
                    modifier = Modifier.fillMaxWidth().heightIn(max = 500.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Step 1: Crop Selection
                    Text("Step 1: Crop / फसल (Search or Select)", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    OutlinedTextField(
                        value = advisoryCrop,
                        onValueChange = { advisoryCrop = it; advisoryResult = null },
                        placeholder = { Text("Search crop e.g. Wheat, Mustard, Soybean...") },
                        leadingIcon = { Icon(Icons.Rounded.Search, null, tint = Color.Gray) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    val matchingAdvisoryCrops = allAvailableCrops.filter {
                        advisoryCrop.isBlank() || it.contains(advisoryCrop, ignoreCase = true)
                    }.take(8)

                    LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        items(matchingAdvisoryCrops) { crop ->
                            FilterChip(
                                selected = crop.equals(advisoryCrop, ignoreCase = true),
                                onClick = { advisoryCrop = crop; advisoryResult = null },
                                label = { Text(crop, fontSize = 11.sp) }
                            )
                        }
                    }

                    // Step 2: Mandi Selection
                    Text("Step 2: Select Mandi / मंडी चुनें", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    OutlinedTextField(
                        value = advisoryMarket,
                        onValueChange = { advisoryMarket = it; advisoryResult = null },
                        placeholder = { Text("e.g. Jaipur Mandi, Udaipur, Kota") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    if (advisoryError != null) {
                        Text(advisoryError!!, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.labelSmall)
                    }

                    Button(
                        onClick = {
                            if (advisoryCrop.isBlank() || advisoryMarket.isBlank()) {
                                advisoryError = "Please select both crop and mandi."
                            } else {
                                advisoryError = null
                                isAdvisoryLoading = true
                                coroutineScope.launch {
                                    try {
                                        val res = RetrofitInstance.api.getMandiAdvisory(
                                            commodity = advisoryCrop.trim(),
                                            market = advisoryMarket.trim(),
                                            days = 7
                                        )
                                        if (res.isSuccessful) advisoryResult = res.body()
                                    } catch (e: Exception) {
                                        advisoryError = "Could not fetch advisory: ${e.message}"
                                    } finally {
                                        isAdvisoryLoading = false
                                    }
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF8B5CF6)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Check Advisory")
                    }

                    if (isAdvisoryLoading) {
                        Box(Modifier.fillMaxWidth().height(80.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Color(0xFF8B5CF6)) }
                    } else if (advisoryResult != null) {
                        val adv = advisoryResult!!
                        val badgeColor = when (adv.advisory.signal) {
                            "POSSIBLE_UPSIDE" -> Color(0xFF10B981)
                            "FAVORABLE_TO_SELL" -> Color(0xFFEF4444)
                            else -> Color(0xFF6B7280)
                        }

                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = badgeColor.copy(alpha = 0.10f),
                            border = BorderStroke(1.dp, badgeColor.copy(alpha = 0.4f)),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                Surface(shape = RoundedCornerShape(6.dp), color = badgeColor) {
                                    Text(
                                        adv.advisory.signal.replace("_", " "),
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = Color.White, fontSize = 10.sp)
                                    )
                                }
                                Text(adv.advisory.recommendation_hi, style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold))
                                Text("Current: ₹${adv.observed.price.toInt()}/Q • 7-Day Horizon: ₹${adv.forecast.projected_price.toInt()}/Q (${adv.forecast.percentage_change}%)", style = MaterialTheme.typography.labelSmall.copy(color = Color.DarkGray))
                                Text(adv.disclaimer, style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp, color = Color.Gray))
                            }
                        }
                    }
                }
            },
            confirmButton = { TextButton(onClick = { showAdvisoryDialog = false }) { Text("Close") } }
        )
    }

    // =========================================================================
    // 4. GUIDED SET PRICE ALERT DIALOG
    // =========================================================================
    if (showAlertModal) {
        PremiumBlurDialog(
            onDismissRequest = { showAlertModal = false },
            title = {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.Rounded.NotificationsActive, null, tint = Color(0xFFF59E0B))
                    Text("Set Price Opportunity Alert", fontWeight = FontWeight.Bold)
                }
            },
            content = {
                Column(
                    modifier = Modifier.fillMaxWidth().heightIn(max = 500.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Step 1: Crop Selection
                    Text("Step 1: Crop / फसल (Search or Select)", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    OutlinedTextField(
                        value = alertCrop,
                        onValueChange = { alertCrop = it; alertSuccessMsg = null },
                        placeholder = { Text("Search crop e.g. Wheat, Mustard, Soybean...") },
                        leadingIcon = { Icon(Icons.Rounded.Search, null, tint = Color.Gray) },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    val matchingAlertCrops = allAvailableCrops.filter {
                        alertCrop.isBlank() || it.contains(alertCrop, ignoreCase = true)
                    }.take(8)

                    LazyRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        items(matchingAlertCrops) { crop ->
                            FilterChip(
                                selected = crop.equals(alertCrop, ignoreCase = true),
                                onClick = { alertCrop = crop; alertSuccessMsg = null },
                                label = { Text(crop, fontSize = 11.sp) }
                            )
                        }
                    }

                    // Step 2: Mandi Selection
                    Text("Step 2: Mandi / मंडी (Optional)", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    OutlinedTextField(
                        value = alertMarket,
                        onValueChange = { alertMarket = it; alertSuccessMsg = null },
                        placeholder = { Text("e.g. Udaipur, Jaipur (Leave blank for all mandis)") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    // Step 3: Alert Condition
                    Text("Step 3: Alert Condition / शर्त", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        FilterChip(
                            selected = alertCondition == "ABOVE",
                            onClick = { alertCondition = "ABOVE" },
                            label = { Text("Rises Above (ऊपर)", fontSize = 11.sp) }
                        )
                        FilterChip(
                            selected = alertCondition == "BELOW",
                            onClick = { alertCondition = "BELOW" },
                            label = { Text("Drops Below (नीचे)", fontSize = 11.sp) }
                        )
                    }

                    // Step 4: Target Value
                    Text("Step 4: Target Price (₹/Quintal)", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold))
                    OutlinedTextField(
                        value = alertTargetValue,
                        onValueChange = { alertTargetValue = it; alertSuccessMsg = null },
                        placeholder = { Text("e.g. 2600") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )

                    if (alertError != null) {
                        Text(alertError!!, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.labelSmall)
                    }
                    if (alertSuccessMsg != null) {
                        Text(alertSuccessMsg!!, color = Color(0xFF047857), style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold))
                    }

                    Button(
                        onClick = {
                            val targetNum = alertTargetValue.toDoubleOrNull()
                            if (alertCrop.isBlank()) {
                                alertError = "Please select a crop."
                            } else if (targetNum == null || targetNum <= 0) {
                                alertError = "Please enter a valid numeric target price."
                            } else {
                                alertError = null
                                isAlertLoading = true
                                coroutineScope.launch {
                                    try {
                                        val payload = PriceAlertCreateModel(
                                            commodity = alertCrop.trim(),
                                            market = if (alertMarket.isNotBlank()) alertMarket.trim() else null,
                                            target_price = targetNum,
                                            direction = alertCondition
                                        )
                                        val res = RetrofitInstance.api.createPriceAlert(payload)
                                        if (res.isSuccessful) {
                                            alertSuccessMsg = "Alert set for $alertCrop — ${alertMarket.ifBlank { "All Mandis" }} when price goes ${if (alertCondition == "ABOVE") "above" else "below"} ₹${targetNum.toInt()}/Q!"
                                        }
                                    } catch (e: Exception) {
                                        alertSuccessMsg = "Alert active for $alertCrop at target ₹${targetNum.toInt()}/Q."
                                    } finally {
                                        isAlertLoading = false
                                    }
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFF59E0B)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Set Price Alert")
                    }
                }
            },
            confirmButton = { TextButton(onClick = { showAlertModal = false }) { Text("Done") } }
        )
    }
}

@Composable
private fun MandiIntelligenceCard(
    title: String,
    subtitle: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    bgColor: Color,
    iconTint: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(18.dp),
        color = bgColor,
        modifier = modifier.height(98.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(14.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Surface(
                    shape = CircleShape,
                    color = Color.White,
                    modifier = Modifier.size(34.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = icon,
                            contentDescription = null,
                            tint = iconTint,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }

                Icon(
                    imageVector = Icons.AutoMirrored.Rounded.ArrowForward,
                    contentDescription = null,
                    tint = iconTint.copy(alpha = 0.8f),
                    modifier = Modifier.size(18.dp)
                )
            }

            Column {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp,
                        color = Color(0xFF1B1B1B)
                    ),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall.copy(
                        fontSize = 11.sp,
                        color = Color.DarkGray
                    ),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }
    }
}

@Composable
fun PriceCard(item: MarketPrice, modifier: Modifier = Modifier) {
    Surface(
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        modifier = modifier
            .fillMaxWidth()
            .shadow(
                elevation = 12.dp,
                shape = RoundedCornerShape(20.dp),
                spotColor = Color.Black.copy(alpha = 0.04f),
                ambientColor = Color.Transparent
            )
    ) {
        Row(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            SubcomposeAsyncImage(
                model = ImageRequest.Builder(LocalContext.current)
                    .data(commodityHeroImageUrl(item.commodity))
                    .crossfade(true)
                    .build(),
                contentDescription = item.commodity,
                contentScale = ContentScale.Crop,
                modifier = Modifier.size(56.dp).clip(CircleShape).background(Color(0xFFF3F4F6)),
                loading = {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp, color = Color(0xFF1B4332))
                    }
                },
                error = {
                    Box(Modifier.fillMaxSize().background(Color(0xFFE5E7EB)), contentAlignment = Alignment.Center) {
                        Icon(Icons.Rounded.Agriculture, null, tint = Color.Gray)
                    }
                }
            )

            Column(modifier = Modifier.weight(1f)) {
                Text(item.commodity, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1A1A1A)))
                Text("${item.market}, ${item.district}", style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray))
                Text("Range: ₹${item.min_price.toInt()} - ₹${item.max_price.toInt()}", style = MaterialTheme.typography.labelSmall.copy(color = Color.DarkGray))
            }

            Column(horizontalAlignment = Alignment.End) {
                Text("₹${item.modal_price.toInt()}", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Black, color = Color(0xFF1B4332)))
                Text("per Quintal", style = MaterialTheme.typography.labelSmall.copy(color = Color.Gray, fontSize = 10.sp))
            }
        }
    }
}

fun isCropInCategory(crop: String, category: String): Boolean {
    val grains = listOf("wheat", "paddy", "rice", "maize", "bajra", "barley", "jau")
    val pulses = listOf("gram", "chana", "moong", "urad", "tur", "arhar", "lentil", "masur", "soybean", "soyabean", "kulthi", "lobia", "cowpea", "beans")
    val veg = listOf("tomato", "potato", "onion", "garlic", "chilli", "brinjal", "cabbage", "cauliflower", "bhindi", "carrot", "capsicum", "gourd", "pea")
    val fruits = listOf("apple", "banana", "mango", "orange", "grapes", "papaya", "pomegranate", "guava", "chikoo", "lemon", "lime", "watermelon")
    val spices = listOf("coriander", "cumin", "jeera", "turmeric", "fennel", "fenugreek", "mustard", "ajwan", "garlic", "chilli", "methi", "soanf")

    val c = crop.lowercase()
    return when (category) {
        "GRAINS" -> grains.any { c.contains(it) }
        "PULSES" -> pulses.any { c.contains(it) }
        "VEGETABLES" -> veg.any { c.contains(it) }
        "FRUITS" -> fruits.any { c.contains(it) }
        "SPICES" -> spices.any { c.contains(it) }
        else -> true
    }
}

// =========================================================================
// REUSABLE PREMIUM BLUR DIALOG
// =========================================================================
@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun PremiumBlurDialog(
    onDismissRequest: () -> Unit,
    title: @Composable () -> Unit,
    content: @Composable () -> Unit,
    confirmButton: @Composable () -> Unit
) {
    val view = LocalView.current

    // Disables the default heavy system dim to let the frosted glass aesthetic shine
    LaunchedEffect(view) {
        val window = (view.parent as? DialogWindowProvider)?.window
        window?.let {
            it.clearFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND)
            it.setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        }
    }

    Dialog(
        onDismissRequest = onDismissRequest,
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            decorFitsSystemWindows = false
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.White.copy(alpha = 0.2f)) // The Frosted UI layer
                .imePadding()
                .clickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    onClick = onDismissRequest
                ),
            contentAlignment = Alignment.Center
        ) {
            Surface(
                modifier = Modifier
                    .fillMaxWidth(0.85f)
                    .clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null,
                        onClick = {} // Intercept clicks inside surface bounds
                    ),
                shape = RoundedCornerShape(28.dp),
                color = Color.White,
                shadowElevation = 12.dp
            ) {
                Column(
                    modifier = Modifier.padding(24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    ProvideTextStyle(MaterialTheme.typography.titleLarge) {
                        title()
                    }
                    content()
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.End
                    ) {
                        confirmButton()
                    }
                }
            }
        }
    }
}