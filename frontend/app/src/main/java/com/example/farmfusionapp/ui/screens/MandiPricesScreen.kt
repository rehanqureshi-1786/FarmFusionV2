package com.example.farmfusionapp.ui.screens

import android.content.Intent
import androidx.core.net.toUri
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
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
    
    val categories = listOf("ALL CROPS", "GRAINS", "VEGETABLES", "PULSES", "FRUITS", "SPICES")

    // Forecast Selection State
    var showForecastDialog by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        viewModel.getMarketPrices()
        productViewModel.loadProducts(null)
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Mandi Prices", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        NeoScaffoldBackground(modifier = Modifier.fillMaxSize().padding(padding)) {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(20.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp)
            ) {
                // Search Bar
                item {
                    Surface(
                        shape = RoundedCornerShape(24.dp),
                        color = Color.White.copy(alpha = 0.9f),
                        modifier = Modifier.fillMaxWidth().shadow(4.dp, RoundedCornerShape(24.dp)),
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
                                title = "${state.response.commodity} Analysis",
                                body = state.response.ai_analysis ?: "",
                                onClick = { showForecastDialog = true }
                            )
                        }
                        else -> {
                            AiInsightCard(
                                title = "AI Price Forecast",
                                body = "Tap to predict future prices for any crop and region.",
                                onClick = { showForecastDialog = true }
                            )
                        }
                    }
                }

                // Category Tabs
                item {
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        items(categories) { category ->
                            val isSelected = category == selectedCategory
                            Surface(
                                onClick = { selectedCategory = category },
                                shape = RoundedCornerShape(16.dp),
                                color = if (isSelected) MaterialTheme.colorScheme.primary else Color.White,
                                border = if (!isSelected) BorderStroke(1.dp, Color(0xFFEEEEEE)) else null
                            ) {
                                Text(
                                    text = category,
                                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                                    style = MaterialTheme.typography.labelLarge.copy(
                                        fontWeight = FontWeight.Bold,
                                        color = if (isSelected) Color.White else Color.Black
                                    )
                                )
                            }
                        }
                    }
                }

                // Mandi Price List
                when (val state = pricesState) {
                    is MarketViewModel.MarketPricesState.Loading -> {
                        item { Box(Modifier.fillMaxWidth().height(100.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator() } }
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
                                        .height(140.dp)
                                        .padding(top = 20.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        "No mandi price results found. Try another crop, state or district.",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = Color.Gray,
                                        textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                        modifier = Modifier.padding(16.dp)
                                    )
                                }
                            }
                        } else {
                            items(filtered.take(20)) { item ->
                                PriceCard(item)
                            }
                        }
                    }
                    is MarketViewModel.MarketPricesState.Error -> {
                        item {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(140.dp)
                                    .padding(top = 20.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    "Unable to load mandi prices: ${state.message}",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = Color.Red,
                                    textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                    modifier = Modifier.padding(16.dp)
                                )
                            }
                        }
                    }
                    else -> {}
                }

                // Ranked Products
                if (!productLoading && bestTreatment.isNotEmpty()) {
                    item { NeoSectionTitle("Best Treatment Products", "Top rated for your crops") }
                    items(bestTreatment.take(3)) { rp ->
                        ProductRecommendationCard(rp) {
                            val intent = Intent(Intent.ACTION_VIEW, it.toUri())
                            context.startActivity(intent)
                        }
                    }
                }
            }
        }
    }

    if (showForecastDialog) {
        ForecastDialog(onDismiss = { showForecastDialog = false }) { city, crop ->
            viewModel.predictPrices(commodity = crop, state = "India", district = city, months = 3)
            showForecastDialog = false
        }
    }
}

@Composable
fun AiInsightCard(title: String, body: String, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().shadow(8.dp, RoundedCornerShape(24.dp)),
        shape = RoundedCornerShape(24.dp),
        color = Color(0xFF1B5E20)
    ) {
        Box(modifier = Modifier.background(Brush.linearGradient(listOf(Color(0xFF2E7D32), Color(0xFF1B5E20))))) {
            Icon(Icons.Rounded.AutoAwesome, null, modifier = Modifier.size(120.dp).align(Alignment.BottomEnd).offset(20.dp, 20.dp), tint = Color.White.copy(alpha = 0.1f))
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.Rounded.AutoGraph, null, tint = Color(0xFFFFD54F), modifier = Modifier.size(20.dp))
                    Text(title, color = Color.White, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                }
                Text(
                    text = body, 
                    color = Color.White.copy(alpha = 0.9f), 
                    style = MaterialTheme.typography.bodySmall,
                    lineHeight = 18.sp
                )
            }
        }
    }
}

@Composable
fun PriceCard(item: MarketPrice) {
    NeoCard(contentPadding = PaddingValues(12.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
            Box(modifier = Modifier.size(48.dp).clip(RoundedCornerShape(12.dp)).background(Color(0xFFF0F4F0)), contentAlignment = Alignment.Center) {
                SubcomposeAsyncImage(
                    model = ImageRequest.Builder(LocalContext.current).data(commodityHeroImageUrl(item.commodity)).crossfade(true).build(),
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                ) {
                    if (painter.state is AsyncImagePainter.State.Loading) {
                        CircularProgressIndicator(strokeWidth = 2.dp)
                    } else if (painter.state is AsyncImagePainter.State.Error) {
                        Icon(Icons.Rounded.Grass, null, tint = Color(0xFF4CAF50))
                    } else {
                        SubcomposeAsyncImageContent()
                    }
                }
            }
            Spacer(Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(item.commodity, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                Text(item.market, color = Color.Gray, style = MaterialTheme.typography.bodySmall)
            }
            Column(horizontalAlignment = Alignment.End) {
                Text("₹${item.modal_price.toInt()}", fontWeight = FontWeight.Black, color = Color(0xFF1B5E20), fontSize = 18.sp)
                Text("per quintal", color = Color.Gray, style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}

@Composable
fun ProductRecommendationCard(rp: RankedProduct, onBuy: (String) -> Unit) {
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

@Composable
fun ForecastDialog(onDismiss: () -> Unit, onForecast: (String, String) -> Unit) {
    var city by remember { mutableStateOf("") }
    var crop by remember { mutableStateOf("") }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("AI Price Forecast", fontWeight = FontWeight.Bold) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(value = city, onValueChange = { city = it }, label = { Text("City/District") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = crop, onValueChange = { crop = it }, label = { Text("Crop Name") }, modifier = Modifier.fillMaxWidth())
            }
        },
        confirmButton = { TextButton(onClick = { if (city.isNotBlank() && crop.isNotBlank()) onForecast(city, crop) }) { Text("Predict") } },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } }
    )
}

private fun isCropInCategory(crop: String, category: String): Boolean {
    val c = crop.lowercase()
    return when(category) {
        "GRAINS" -> listOf("wheat", "rice", "maize", "paddy", "barley").any { c.contains(it) }
        "VEGETABLES" -> listOf("potato", "tomato", "onion", "cabbage", "brinjal").any { c.contains(it) }
        "PULSES" -> listOf("soybean", "chana", "dal", "moong", "urad").any { c.contains(it) }
        "FRUITS" -> listOf("mango", "apple", "banana", "lemon", "papaya").any { c.contains(it) }
        "SPICES" -> listOf("cumin", "jeera", "coriander", "turmeric", "chillies", "garlic").any { c.contains(it) }
        else -> true
    }
}
