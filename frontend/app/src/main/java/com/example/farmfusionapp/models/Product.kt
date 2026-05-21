package com.example.farmfusionapp.models

data class Product(
    val name: String,
    val imageUrl: String,
    val price: Double,
    val rating: Double,
    val reviewCount: Int,
    val buyUrl: String,
    val category: String,
    val availability: Boolean,
    val popularityScore: Double,
    val relevanceScore: Double
)

data class RankedProduct(
    val product: Product,
    val score: Double,
    val reasons: List<String>
) {
    val matchPercentage: Int
        get() = (product.relevanceScore * 100).toInt()
}
