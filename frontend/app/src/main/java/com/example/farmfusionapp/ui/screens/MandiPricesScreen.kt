package com.example.farmfusionapp.ui.screens

import android.content.Intent
import androidx.core.net.toUri
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
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
import androidx.compose.material.icons.automirrored.rounded.KeyboardArrowRight
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.window.DialogWindowProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.AsyncImagePainter
import coil.compose.SubcomposeAsyncImage
import coil.compose.SubcomposeAsyncImageContent
import coil.request.ImageRequest
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.MarketPrice
import com.example.farmfusionapp.models.RankedProduct
import com.example.farmfusionapp.ui.components.NeoCard
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.components.NeoSectionTitle
import com.example.farmfusionapp.ui.components.PremiumButton
import com.example.farmfusionapp.utils.commodityHeroImageUrl
import com.example.farmfusionapp.viewmodel.MarketViewModel
import com.example.farmfusionapp.viewmodel.ProductViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MandiPricesScreen(
    navController: NavController,
    viewModel: MarketViewModel = viewModel(),
    productViewModel: ProductViewModel = viewModel()
) {
    val context = LocalContext.current
    var selectedCategory by remember { mutableStateOf("ALL CROPS") }
    var searchQuery by remember { mutableStateOf("") }

    val pricesState by viewModel.pricesState
    val predictionState by viewModel.predictionState

    val bestTreatment by productViewModel.bestTreatment.observeAsState(emptyList())
    val recommendedTools by productViewModel.recommendedTools.observeAsState(emptyList())
    val productLoading by productViewModel.loading.observeAsState(false)

    val categories = listOf("ALL CROPS", "GRAINS", "VEGETABLES", "PULSES", "OILSEEDS", "SPICES")

    val globalBlur = LocalGlobalBlur.current

    var showForecastDialog by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        viewModel.getMarketPrices()
        productViewModel.loadProducts(null)
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
                            "Market Prices",
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1B5E20)
                        )
                    },
                    navigationIcon = {
                        IconButton(onClick = { navController.popBackStack() }) {
                            Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", tint = Color(0xFF424242))
                        }
                    }
                )
            }
        ) { padding ->
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                // REDUCED padding to 90.dp since the nav bar is in permanent shrunk mode
                contentPadding = PaddingValues(top = 16.dp, bottom = 90.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp)
            ) {
                // Search Bar
                item {
                    Surface(
                        shape = RoundedCornerShape(24.dp),
                        color = Color.White.copy(alpha = 0.9f),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 20.dp)
                            .shadow(4.dp, RoundedCornerShape(24.dp)),
                        border = BorderStroke(1.dp, Color(0xFFEEEEEE))
                    ) {
                        TextField(
                            value = searchQuery,
                            onValueChange = { searchQuery = it },
                            placeholder = { Text("Search crops, mandis...") },
                            leadingIcon = { Icon(Icons.Rounded.Search, null, tint = Color.Gray) },
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

                // AI Insight Card
                item {
                    when (val state = predictionState) {
                        is MarketViewModel.MarketPredictionState.Success -> {
                            AiInsightCard(
                                modifier = Modifier.padding(horizontal = 20.dp),
                                title = "${state.response.commodity} Analysis",
                                body = state.response.ai_analysis ?: "",
                                onClick = {
                                    showForecastDialog = true
                                    globalBlur.value = true
                                }
                            )
                        }
                        else -> {
                            AiInsightCard(
                                modifier = Modifier.padding(horizontal = 20.dp),
                                title = "AI Price Forecast",
                                body = "Predict future prices for any crop and region with AI.",
                                onClick = {
                                    showForecastDialog = true
                                    globalBlur.value = true
                                }
                            )
                        }
                    }
                }

                // Category Tabs
                item {
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                        contentPadding = PaddingValues(horizontal = 20.dp)
                    ) {
                        items(categories) { category ->
                            val isSelected = category == selectedCategory
                            val displayCategory = if (category == "ALL CROPS") "All Crops" else category.lowercase().replaceFirstChar { it.uppercase() }

                            Surface(
                                onClick = { selectedCategory = category },
                                shape = RoundedCornerShape(50),
                                color = if (isSelected) Color(0xFF1B5E20) else Color.White,
                                border = if (!isSelected) BorderStroke(1.dp, Color(0xFFE0E0E0)) else null
                            ) {
                                Text(
                                    text = displayCategory,
                                    modifier = Modifier.padding(horizontal = 18.dp, vertical = 10.dp),
                                    style = MaterialTheme.typography.labelLarge.copy(
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        color = if (isSelected) Color.White else Color.DarkGray
                                    )
                                )
                            }
                        }
                    }
                }

                // Mandi Price List
                when (val state = pricesState) {
                    is MarketViewModel.MarketPricesState.Loading -> {
                        item { Box(Modifier.fillMaxWidth().height(100.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Color(0xFF1B5E20)) } }
                    }
                    is MarketViewModel.MarketPricesState.Success -> {
                        val filtered = state.response.data.filter {
                            (searchQuery.isEmpty() || it.commodity.contains(searchQuery, true) || it.market.contains(searchQuery, true)) &&
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
                                        "No mandi price results found. Try another crop, state or district.",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = Color.Gray,
                                        textAlign = TextAlign.Center,
                                        modifier = Modifier.padding(16.dp)
                                    )
                                }
                            }
                        } else {
                            items(filtered.take(20)) { item ->
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
                                    "Unable to load mandi prices: ${state.message}",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = Color.Red,
                                    textAlign = TextAlign.Center,
                                    modifier = Modifier.padding(16.dp)
                                )
                            }
                        }
                    }
                    else -> {}
                }

                // Ranked Products
                if (!productLoading && bestTreatment.isNotEmpty()) {
                    item {
                        Box(modifier = Modifier.padding(horizontal = 20.dp)) {
                            NeoSectionTitle("Best Treatment Products", "Top rated for your crops")
                        }
                    }
                    items(bestTreatment.take(3)) { rp ->
                        ProductRecommendationCard(
                            rp = rp,
                            modifier = Modifier.padding(horizontal = 20.dp)
                        ) {
                            val intent = Intent(Intent.ACTION_VIEW, it.toUri())
                            context.startActivity(intent)
                        }
                    }
                }
            }
        }
    }

    if (showForecastDialog) {
        ForecastDialog(
            onDismiss = {
                showForecastDialog = false
                globalBlur.value = false
            }
        ) { city, crop ->
            viewModel.predictPrices(commodity = crop, state = "India", district = city, months = 3)
            showForecastDialog = false
            globalBlur.value = false
        }
    }
}

@Composable
fun AiInsightCard(modifier: Modifier = Modifier, title: String, body: String, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        modifier = modifier.shadow(6.dp, RoundedCornerShape(24.dp)),
        shape = RoundedCornerShape(24.dp),
        color = Color.White
    ) {
        Box(modifier = Modifier.fillMaxWidth().height(160.dp)) {

            Image(
                painter = painterResource(id = R.drawable.ill_ai_forecast),
                contentDescription = null,
                contentScale = ContentScale.Fit,
                alignment = Alignment.BottomEnd,
                modifier = Modifier
                    .matchParentSize()
                    .padding(start = 40.dp)
                    .offset(x = 20.dp, y = 20.dp)
            )

            Column(
                modifier = Modifier
                    .padding(24.dp)
                    .fillMaxWidth(0.65f),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = title,
                    color = Color(0xFF1B5E20),
                    fontWeight = FontWeight.ExtraBold,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = body,
                    color = Color.Gray,
                    style = MaterialTheme.typography.bodySmall,
                    lineHeight = 16.sp
                )

                Spacer(modifier = Modifier.weight(1f))

                Surface(
                    shape = CircleShape,
                    color = Color(0xFF1B5E20),
                    modifier = Modifier
                        .size(36.dp)
                        .clickable { onClick() }
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            Icons.AutoMirrored.Rounded.KeyboardArrowRight,
                            contentDescription = "Forecast Prices",
                            tint = Color.White,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun PriceCard(item: MarketPrice, modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.shadow(2.dp, RoundedCornerShape(20.dp)),
        shape = RoundedCornerShape(20.dp),
        color = Color.White
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth().padding(16.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(60.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(Color(0xFFF5F5F5)),
                contentAlignment = Alignment.Center
            ) {
                SubcomposeAsyncImage(
                    model = ImageRequest.Builder(LocalContext.current)
                        .data(commodityHeroImageUrl(item.commodity))
                        .crossfade(true)
                        .build(),
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                ) {
                    if (painter.state is AsyncImagePainter.State.Loading) {
                        CircularProgressIndicator(strokeWidth = 2.dp, color = Color(0xFF1B5E20))
                    } else if (painter.state is AsyncImagePainter.State.Error) {
                        Icon(Icons.Rounded.Grass, null, tint = Color(0xFF4CAF50))
                    } else {
                        SubcomposeAsyncImageContent()
                    }
                }
            }
            Spacer(Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.commodity,
                    fontWeight = FontWeight.ExtraBold,
                    style = MaterialTheme.typography.titleMedium,
                    color = Color(0xFF1B1B1B)
                )
                Spacer(Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Rounded.LocationOn,
                        contentDescription = null,
                        tint = Color.Gray,
                        modifier = Modifier.size(12.dp)
                    )
                    Spacer(Modifier.width(4.dp))
                    Text(
                        text = item.market,
                        color = Color.Gray,
                        style = MaterialTheme.typography.bodySmall,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "₹${item.modal_price.toInt()}",
                    fontWeight = FontWeight.Black,
                    color = Color(0xFF1B5E20),
                    fontSize = 20.sp
                )
                Text(
                    text = "per quintal",
                    color = Color.Gray,
                    style = MaterialTheme.typography.labelSmall
                )
            }
        }
    }
}

@Composable
fun ProductRecommendationCard(rp: RankedProduct, modifier: Modifier = Modifier, onBuy: (String) -> Unit) {
    Box(modifier = modifier) {
        NeoCard(contentPadding = PaddingValues(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(modifier = Modifier.size(60.dp).clip(RoundedCornerShape(12.dp)).background(Color(0xFFF5F5F5))) {
                    SubcomposeAsyncImage(
                        model = ImageRequest.Builder(LocalContext.current).data(rp.product.imageUrl).crossfade(true).build(),
                        contentDescription = null,
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop
                    ) { SubcomposeAsyncImageContent() }
                }
                Spacer(Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(rp.product.name, fontWeight = FontWeight.Bold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    Text("₹${rp.product.price}", fontWeight = FontWeight.Bold, color = Color(0xFF1B5E20))
                }
                Surface(color = Color(0xFFE8F5E9), shape = RoundedCornerShape(8.dp)) {
                    Text("${rp.matchPercentage}% Match", modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp), style = MaterialTheme.typography.labelSmall, color = Color(0xFF2E7D32), fontWeight = FontWeight.Bold)
                }
            }
            Spacer(Modifier.height(8.dp))
            PremiumButton(text = "Buy Now", onClick = { onBuy(rp.product.buyUrl) }, modifier = Modifier.height(40.dp))
        }
    }
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun ForecastDialog(onDismiss: () -> Unit, onForecast: (String, String) -> Unit) {
    var city by remember { mutableStateOf("") }
    var crop by remember { mutableStateOf("") }

    val view = LocalView.current

    LaunchedEffect(view) {
        val window = (view.parent as? DialogWindowProvider)?.window
        window?.let {
            it.clearFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND)
            it.setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        }
    }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            decorFitsSystemWindows = false
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.White.copy(alpha = 0.2f))
                .imePadding()
                .clickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    onClick = onDismiss
                ),
            contentAlignment = Alignment.Center
        ) {
            Surface(
                modifier = Modifier
                    .fillMaxWidth(0.85f)
                    .clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null,
                        onClick = {}
                    ),
                shape = RoundedCornerShape(28.dp),
                color = Color.White,
                shadowElevation = 12.dp
            ) {
                Column(
                    modifier = Modifier.padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "AI Price Forecast",
                        fontWeight = FontWeight.ExtraBold,
                        style = MaterialTheme.typography.titleLarge,
                        color = Color(0xFF1B1B1B)
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "Get AI-powered price predictions\nfor any crop in any city.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.Gray,
                        textAlign = TextAlign.Center,
                        lineHeight = 20.sp
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    OutlinedTextField(
                        value = city,
                        onValueChange = { city = it },
                        placeholder = { Text("Enter city or district", color = Color.Gray) },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF1B5E20),
                            unfocusedBorderColor = Color(0xFFEEEEEE),
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color(0xFFFAFAFA)
                        )
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    OutlinedTextField(
                        value = crop,
                        onValueChange = { crop = it },
                        placeholder = { Text("Enter crop name", color = Color.Gray) },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF1B5E20),
                            unfocusedBorderColor = Color(0xFFEEEEEE),
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color(0xFFFAFAFA)
                        )
                    )

                    Spacer(modifier = Modifier.height(28.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Button(
                            onClick = onDismiss,
                            modifier = Modifier
                                .weight(1f)
                                .height(50.dp),
                            shape = RoundedCornerShape(16.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFF5F5F5),
                                contentColor = Color(0xFF1B5E20)
                            ),
                            elevation = ButtonDefaults.buttonElevation(0.dp)
                        ) {
                            Text("Cancel", fontWeight = FontWeight.Bold)
                        }

                        Button(
                            onClick = { if (city.isNotBlank() && crop.isNotBlank()) onForecast(city, crop) },
                            modifier = Modifier
                                .weight(1f)
                                .height(50.dp),
                            shape = RoundedCornerShape(16.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFF1B5E20),
                                contentColor = Color.White
                            ),
                            elevation = ButtonDefaults.buttonElevation(2.dp)
                        ) {
                            Text("Predict", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

private fun isCropInCategory(crop: String, category: String): Boolean {
    val c = crop.lowercase()
    return when(category) {
        "GRAINS" -> listOf("wheat", "rice", "maize", "paddy", "barley").any { c.contains(it) }
        "VEGETABLES" -> listOf("potato", "tomato", "onion", "cabbage", "brinjal").any { c.contains(it) }
        "PULSES" -> listOf("soybean", "chana", "dal", "moong", "urad").any { c.contains(it) }
        "FRUITS" -> listOf("mango", "apple", "banana", "lemon", "papaya").any { c.contains(it) }
        "OILSEEDS" -> listOf("mustard", "soybean", "groundnut", "sunflower", "sesame").any { c.contains(it) }
        "SPICES" -> listOf("cumin", "jeera", "coriander", "turmeric", "chillies", "garlic").any { c.contains(it) }
        else -> true
    }
}