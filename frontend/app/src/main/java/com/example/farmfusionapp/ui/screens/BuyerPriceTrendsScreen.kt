package com.example.farmfusionapp.ui.screens

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.Clear
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.utils.AppLocalizer
import com.example.farmfusionapp.viewmodel.MarketViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BuyerPriceTrendsScreen(
    navController: NavController,
    viewModel: MarketViewModel = viewModel()
) {
    val currentLang = LocalAppLanguage.current
    var selectedCategory by remember { mutableStateOf("ALL CROPS") }
    var searchQuery by remember { mutableStateOf("") }

    val pricesState by viewModel.pricesState
    val filteredPrices = remember(pricesState, searchQuery, selectedCategory) {
        val success = pricesState as? MarketViewModel.MarketPricesState.Success
        success?.response?.data?.filter {
            (searchQuery.isEmpty() ||
                    it.commodity.contains(searchQuery, true) ||
                    it.market.contains(searchQuery, true) ||
                    it.district.contains(searchQuery, true)) &&
                    (selectedCategory == "ALL CROPS" || isCropInCategory(it.commodity, selectedCategory))
        } ?: emptyList()
    }
    val categories = listOf("ALL CROPS", "GRAINS", "VEGETABLES", "PULSES", "FRUITS", "SPICES")

    LaunchedEffect(Unit) {
        if (viewModel.pricesState.value !is MarketViewModel.MarketPricesState.Success) {
            viewModel.getMarketPrices()
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
                            text = "Price Trends",
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1A1A1A)
                        )
                    },
                    navigationIcon = {
                        IconButton(onClick = { onNavigateBack() }) {
                            Icon(
                                Icons.AutoMirrored.Rounded.ArrowBack,
                                contentDescription = "Back",
                                tint = Color(0xFF1A1A1A)
                            )
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
                verticalArrangement = Arrangement.spacedBy(16.dp)
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
                            placeholder = {
                                Text(AppLocalizer.localizeMarketPhrase("search crops placeholder", currentLang))
                            },
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
                                    text = AppLocalizer.localizeMarketPhrase(category, currentLang),
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
                        item {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(180.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                CircularProgressIndicator(color = Color(0xFF1B4332))
                            }
                        }
                    }
                    is MarketViewModel.MarketPricesState.Success -> {
                        if (filteredPrices.isEmpty()) {
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
                            items(
                                items = filteredPrices.take(40),
                                key = { "${it.market}_${it.commodity}_${it.district}_${it.arrival_date}_${it.modal_price}" }
                            ) { item ->
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
}
