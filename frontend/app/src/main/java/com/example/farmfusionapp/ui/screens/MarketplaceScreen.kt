package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Eco
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R

data class StoreProduct(
    val id: Int,
    val category: String,
    val title: String,
    val description: String,
    val tags: List<String>,
    val imageRes: Int,
    val searchQuery: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MarketplaceScreen(navController: NavController) {

    val products = remember {
        listOf(
            StoreProduct(
                id = 1,
                category = "FERTILIZER",
                title = "Organic NPK Fertilizer",
                description = "Balanced nutrition for field crops",
                tags = listOf("Improves growth", "Boosts yield"),
                imageRes = R.drawable.img_npk_fertilizer,
                searchQuery = "Organic NPK Fertilizer for agriculture field crops plant growth"
            ),
            StoreProduct(
                id = 2,
                category = "SEEDS",
                title = "Certified Wheat Seeds",
                description = "High-yield varieties",
                tags = listOf("Better germination", "Disease resistant"),
                imageRes = R.drawable.img_wheat_seeds,
                searchQuery = "High yield certified wheat seeds for farming agriculture"
            ),
            StoreProduct(
                id = 3,
                category = "CROP CARE",
                title = "Neem Oil Spray",
                description = "Organic pest care",
                tags = listOf("Natural protection", "Safe for crops"),
                imageRes = R.drawable.img_neem_spray,
                searchQuery = "Organic Neem Oil Spray for plant pests agriculture farming"
            ),
            StoreProduct(
                id = 4,
                category = "TOOLS",
                title = "Garden Hand Tools Set",
                description = "Durable tools for every gardener",
                tags = listOf("Ergonomic design", "Long lasting"),
                imageRes = R.drawable.img_garden_tools,
                searchQuery = "Heavy duty ergonomic garden hand tools set farming agriculture"
            )
        )
    }

    Scaffold(
        containerColor = Color(0xFFFAFAFA),
        topBar = {
            CenterAlignedTopAppBar(
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color.Transparent,
                    scrolledContainerColor = Color.Transparent
                ),
                title = {
                    Text(
                        text = "Farm Store",
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1B5E20)
                    )
                },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", tint = Color(0xFF1A1A1A))
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {

            item {
                Column(modifier = Modifier.padding(bottom = 8.dp)) {
                    Text(
                        text = "Recently Bought Items",
                        style = MaterialTheme.typography.headlineSmall.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF112A1F)
                        )
                    )
                    Box(
                        modifier = Modifier
                            .padding(top = 4.dp, bottom = 8.dp)
                            .size(width = 32.dp, height = 3.dp)
                            .background(Color(0xFF2E7D32), RoundedCornerShape(50))
                    )
                    Text(
                        text = "Your go-to essentials, all in one place",
                        style = MaterialTheme.typography.bodyMedium.copy(
                            color = Color(0xFF616161)
                        )
                    )
                }
            }

            items(products) { product ->
                PremiumProductCard(product = product)
            }

            item { Spacer(modifier = Modifier.height(24.dp)) }
        }
    }
}

@Composable
fun PremiumProductCard(product: StoreProduct) {
    val context = LocalContext.current

    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(
                elevation = 12.dp,
                shape = RoundedCornerShape(24.dp),
                spotColor = Color.Black.copy(alpha = 0.04f),
                ambientColor = Color.Black.copy(alpha = 0.02f)
            ),
        shape = RoundedCornerShape(24.dp),
        color = Color.White
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {

            Image(
                painter = painterResource(id = product.imageRes),
                contentDescription = product.title,
                contentScale = ContentScale.Fit,
                modifier = Modifier
                    .size(110.dp)
                    .padding(end = 16.dp)
            )

            Column(
                modifier = Modifier.weight(1f)
            ) {
                // Heart icon removed from this Row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Start,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Surface(
                        shape = RoundedCornerShape(8.dp),
                        color = Color(0xFFE8F5E9)
                    ) {
                        Text(
                            text = product.category,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            style = MaterialTheme.typography.labelSmall.copy(
                                fontWeight = FontWeight.ExtraBold,
                                color = Color(0xFF2E7D32),
                                letterSpacing = 0.5.sp,
                                fontSize = 9.sp
                            )
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                Text(
                    text = product.title,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1B1B1B)
                    ),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = product.description,
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = Color(0xFF757575)
                    ),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                Spacer(modifier = Modifier.height(10.dp))

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(
                        imageVector = Icons.Rounded.Eco,
                        contentDescription = null,
                        tint = Color(0xFF2E7D32),
                        modifier = Modifier.size(12.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = product.tags.getOrNull(0) ?: "",
                        style = MaterialTheme.typography.labelSmall.copy(
                            color = Color(0xFF616161),
                            fontSize = 11.sp
                        )
                    )

                    Text(
                        text = "   |   ",
                        style = MaterialTheme.typography.labelSmall.copy(
                            color = Color(0xFFE0E0E0),
                            fontSize = 10.sp
                        )
                    )

                    Text(
                        text = product.tags.getOrNull(1) ?: "",
                        style = MaterialTheme.typography.labelSmall.copy(
                            color = Color(0xFF616161),
                            fontSize = 11.sp
                        )
                    )
                }

                Spacer(modifier = Modifier.height(14.dp))

                Surface(
                    onClick = {
                        // Using the standard product title for accurate search results
                        val query = android.net.Uri.encode(product.title)
                        val amazonUrl = "https://www.amazon.in/s?k=$query"

                        // Fired using a basic intent without aggressive flags so the
                        // Android OS manages the backstack naturally.
                        val intent = android.content.Intent(
                            android.content.Intent.ACTION_VIEW,
                            android.net.Uri.parse(amazonUrl)
                        )
                        context.startActivity(intent)
                    },
                    shape = RoundedCornerShape(24.dp),
                    border = BorderStroke(1.dp, Color(0xFFEEEEEE)),
                    color = Color.White
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center,
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Image(
                            painter = painterResource(id = R.drawable.ic_amazon_logo),
                            contentDescription = "Amazon",
                            modifier = Modifier.height(16.dp).width(50.dp),
                            contentScale = ContentScale.Fit
                        )

                        Spacer(modifier = Modifier.width(8.dp))

                        Text(
                            text = "Buy on Amazon",
                            style = MaterialTheme.typography.labelMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1B1B1B)
                            )
                        )

                        Spacer(modifier = Modifier.width(4.dp))

                        Icon(
                            imageVector = Icons.Rounded.ChevronRight,
                            contentDescription = null,
                            tint = Color(0xFF1B1B1B),
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }
        }
    }
}