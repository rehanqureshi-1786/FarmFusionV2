package com.example.farmfusionapp.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.ErrorOutline
import androidx.compose.material.icons.rounded.ShoppingBag
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.AsyncImage
import com.example.farmfusionapp.data.model.StoreRecommendationItem
import com.example.farmfusionapp.ui.components.EmptyState
import com.example.farmfusionapp.ui.components.NeoCard
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.components.NeoSectionTitle
import com.example.farmfusionapp.ui.components.PremiumButton
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.viewmodel.StoreViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StoreRecommendationsScreen(navController: NavController, storeViewModel: StoreViewModel = viewModel()) {
    val context = LocalContext.current
    val storeState by storeViewModel.storeState
    val token = remember { AuthStore.getAuthToken(context) }

    LaunchedEffect(Unit) {
        storeViewModel.getRecommendations(token)
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Farm Store", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        NeoScaffoldBackground(modifier = Modifier.fillMaxSize().padding(padding)) {
            when (val state = storeState) {
                is StoreViewModel.StoreState.Loading -> {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                }
                is StoreViewModel.StoreState.Error -> {
                    EmptyState(
                        title = "Oops!",
                        description = state.message,
                        icon = Icons.Rounded.ErrorOutline,
                        action = {
                            PremiumButton(text = "Retry", onClick = { storeViewModel.getRecommendations(token) })
                        }
                    )
                }
                is StoreViewModel.StoreState.Success -> {
                    if (state.items.isEmpty()) {
                        EmptyState(
                            title = "No Recommendations",
                            description = "We couldn't find any products for you right now. Check back later!",
                            icon = Icons.Rounded.ShoppingBag
                        )
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(20.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            item {
                                NeoSectionTitle(
                                    title = "Recommended for You",
                                    subtitle = "Top picks based on your farm and trends"
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                            }
                            items(state.items) { item ->
                                StoreItemCard(item) {
                                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(item.shop_url))
                                    context.startActivity(intent)
                                }
                            }
                        }
                    }
                }
                else -> {}
            }
        }
    }
}

@Composable
fun StoreItemCard(item: StoreRecommendationItem, onBuyClick: () -> Unit) {
    NeoCard(contentPadding = PaddingValues(16.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            // Product Image
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color(0xFFF5F5F5)),
                contentAlignment = Alignment.Center
            ) {
                if (!item.image_url.isNullOrBlank()) {
                    AsyncImage(
                        model = item.image_url,
                        contentDescription = item.title,
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop
                    )
                } else {
                    Icon(
                        imageVector = Icons.Rounded.ShoppingBag,
                        contentDescription = null,
                        tint = Color.LightGray,
                        modifier = Modifier.size(40.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Surface(
                    color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.5f),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = item.category.uppercase(),
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary,
                            letterSpacing = 0.5.sp
                        )
                    )
                }
                
                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = item.title,
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                
                Text(
                    text = item.subtitle,
                    style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        PremiumButton(
            text = "Buy on Amazon",
            onClick = onBuyClick,
            modifier = Modifier.height(48.dp)
        )
    }
}
