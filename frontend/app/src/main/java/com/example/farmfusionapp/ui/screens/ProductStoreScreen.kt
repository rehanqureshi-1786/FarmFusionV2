package com.example.farmfusionapp.ui.screens

import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.OpenInNew
import androidx.compose.material.icons.rounded.ShoppingBag
import androidx.compose.material.icons.rounded.Star
import androidx.compose.material.icons.rounded.StarBorder
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.livedata.observeAsState
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
import androidx.core.net.toUri
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import coil.compose.AsyncImagePainter
import coil.compose.SubcomposeAsyncImage
import coil.compose.SubcomposeAsyncImageContent
import coil.request.ImageRequest
import com.example.farmfusionapp.models.RankedProduct
import com.example.farmfusionapp.utils.AffiliatePreferences
import com.example.farmfusionapp.utils.AgriStoreContext
import com.example.farmfusionapp.viewmodel.ProductViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductStoreScreen(
    navController: NavController,
    productViewModel: ProductViewModel = viewModel()
) {
    val context = LocalContext.current
    val params = AgriStoreContext.current

    val bestTreatment by productViewModel.bestTreatment.observeAsState(initial = emptyList<RankedProduct>())
    val recommendedTools by productViewModel.recommendedTools.observeAsState(initial = emptyList<RankedProduct>())
    val alternativeProducts by productViewModel.alternativeProducts.observeAsState(initial = emptyList<RankedProduct>())
    val loading by productViewModel.loading.observeAsState(initial = false)

    val openShopUrl: (String) -> Unit = { url ->
        val affiliateUrl = AffiliatePreferences.buildAffiliateUrl(url, AffiliatePreferences.getAssociateTag(context))
        val intent = Intent(Intent.ACTION_VIEW, affiliateUrl.toUri())
        context.startActivity(intent)
    }

    LaunchedEffect(params.diseaseName) {
        productViewModel.loadProducts(params.diseaseName)
    }

    val subtitle = when (params.source) {
        "crop" -> params.crop?.let { "Best match crop: $it. Ranked recommendations." }
            ?: "Crop-based picks."
        "disease" -> buildString {
            params.diseaseName?.let { append("Diagnosis: $it. ") }
            append("Ranked treatments.")
        }
        else -> "Popular farming inputs. Ranked for you."
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Agri Store", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp)
        ) {
            Text(
                text = subtitle,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(vertical = 8.dp)
            )

            if (loading) {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    contentPadding = PaddingValues(bottom = 24.dp)
                ) {
                    if (bestTreatment.isNotEmpty()) {
                        item {
                            Text(
                                "Best Treatment Products",
                                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold, letterSpacing = (-0.5).sp),
                                modifier = Modifier.padding(vertical = 8.dp)
                            )
                        }
                        items(items = bestTreatment.take(3)) { rp ->
                            StoreRecommendationCard(
                                rankedProduct = rp,
                                onOpenShop = openShopUrl
                            )
                        }
                    }

                    if (recommendedTools.isNotEmpty()) {
                        item {
                            Text(
                                "Recommended Farming Tools",
                                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold, letterSpacing = (-0.5).sp),
                                modifier = Modifier.padding(vertical = 8.dp)
                            )
                        }
                        items(items = recommendedTools.take(3)) { rp ->
                            StoreRecommendationCard(
                                rankedProduct = rp,
                                onOpenShop = openShopUrl
                            )
                        }
                    }

                    if (alternativeProducts.isNotEmpty()) {
                        item {
                            Text(
                                "Alternative Products",
                                style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold, letterSpacing = (-0.5).sp),
                                modifier = Modifier.padding(vertical = 8.dp)
                            )
                        }
                        items(items = alternativeProducts) { rp ->
                            StoreRecommendationCard(
                                rankedProduct = rp,
                                onOpenShop = openShopUrl
                            )
                        }
                    }

                    if (bestTreatment.isEmpty() && recommendedTools.isEmpty() && alternativeProducts.isEmpty()) {
                        item {
                            Text("No recommendations right now.", modifier = Modifier.padding(16.dp))
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun StoreRecommendationCard(
    rankedProduct: RankedProduct,
    onOpenShop: (String) -> Unit
) {
    val context = LocalContext.current
    val product = rankedProduct.product
    ElevatedCard(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(Color(0xFFE8F5E9)),
                    contentAlignment = Alignment.Center
                ) {
                    val url = product.imageUrl
                    if (url.isNotBlank()) {
                        SubcomposeAsyncImage(
                            model = ImageRequest.Builder(context)
                                .data(url)
                                .crossfade(true)
                                .build(),
                            contentDescription = product.name,
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Crop
                        ) {
                            when (painter.state) {
                                is AsyncImagePainter.State.Loading -> {
                                    CircularProgressIndicator(
                                        modifier = Modifier.size(28.dp),
                                        strokeWidth = 2.dp
                                    )
                                }
                                is AsyncImagePainter.State.Error,
                                is AsyncImagePainter.State.Empty -> {
                                    Icon(
                                        Icons.Rounded.ShoppingBag,
                                        contentDescription = null,
                                        tint = Color(0xFF1B5E20).copy(alpha = 0.5f),
                                        modifier = Modifier.size(36.dp)
                                    )
                                }
                                else -> SubcomposeAsyncImageContent()
                            }
                        }
                    } else {
                        Icon(
                            Icons.Rounded.ShoppingBag,
                            contentDescription = null,
                            tint = Color(0xFF1B5E20).copy(alpha = 0.5f),
                            modifier = Modifier.size(36.dp)
                        )
                    }
                }
                Spacer(Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        product.name,
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold),
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                    Text(
                        product.category,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = "₹${product.price}",
                        style = MaterialTheme.typography.titleSmall.copy(fontWeight = FontWeight.Bold),
                        color = MaterialTheme.colorScheme.primary
                    )
                    
                    // Star rating
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        repeat(5) { index ->
                            val active = index < product.rating.toInt()
                            Icon(
                                imageVector = if (active) Icons.Rounded.Star else Icons.Rounded.StarBorder,
                                contentDescription = null,
                                modifier = Modifier.size(14.dp),
                                tint = if (active) Color(0xFFFFD700) else Color.Gray
                            )
                        }
                        Spacer(Modifier.width(4.dp))
                        Text(
                            text = "(${product.reviewCount})",
                            style = MaterialTheme.typography.labelSmall,
                            color = Color.Gray
                        )
                    }
                }
                
                // Match percentage badge
                Surface(
                    color = MaterialTheme.colorScheme.tertiaryContainer,
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = "${rankedProduct.matchPercentage}%",
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                        style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                        color = MaterialTheme.colorScheme.onTertiaryContainer
                    )
                }
            }
            
            // Why recommended section
            if (rankedProduct.reasons.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "Why recommended:",
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold)
                )
                rankedProduct.reasons.take(3).forEach { reason ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(modifier = Modifier.size(4.dp).background(MaterialTheme.colorScheme.primary, CircleShape))
                        Spacer(Modifier.width(6.dp))
                        Text(
                            text = reason,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            
            Spacer(Modifier.height(12.dp))
            Button(
                onClick = { onOpenShop(product.buyUrl) },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.AutoMirrored.Rounded.OpenInNew, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(8.dp))
                Text("Buy Now")
            }
        }
    }
}
