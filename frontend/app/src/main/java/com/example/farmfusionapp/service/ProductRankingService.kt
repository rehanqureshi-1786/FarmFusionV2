package com.example.farmfusionapp.service

import com.example.farmfusionapp.models.Product
import com.example.farmfusionapp.models.RankedProduct
import kotlin.math.ln

class ProductRankingService {

    data class RankingResult(
        val bestTreatment: List<RankedProduct>,
        val recommendedTools: List<RankedProduct>,
        val alternativeProducts: List<RankedProduct>
    )

    fun rankProducts(products: List<Product>, detectedDisease: String?): RankingResult {
        if (products.isEmpty()) return RankingResult(emptyList(), emptyList(), emptyList())

        val maxReview = products.maxOfOrNull { it.reviewCount }?.toDouble() ?: 1.0
        val minPrice = products.minOfOrNull { it.price } ?: 0.0
        val maxPrice = products.maxOfOrNull { it.price } ?: minPrice.coerceAtLeast(1.0)

        fun reviewNormalized(count: Int): Double {
            if (maxReview <= 0.0) return 0.0
            // use a log scale to reduce skew from very large counts
            return ln(1.0 + count) / ln(1.0 + maxReview)
        }

        fun priceScore(price: Double): Double {
            // Higher score for relatively cheaper products (0..1)
            if (maxPrice - minPrice <= 0.0) return 0.5
            return 1.0 - ((price - minPrice) / (maxPrice - minPrice)).coerceIn(0.0, 1.0)
        }

        fun computeScore(p: Product): Double {
            val relevance = p.relevanceScore.coerceIn(0.0, 1.0)
            val rating = (p.rating / 5.0).coerceIn(0.0, 1.0)
            val reviewNorm = reviewNormalized(p.reviewCount)
            val popularity = p.popularityScore.coerceIn(0.0, 1.0)
            val price = priceScore(p.price)

            return (relevance * 0.35) +
                    (rating * 0.25) +
                    (reviewNorm * 0.15) +
                    (popularity * 0.15) +
                    (price * 0.10)
        }

        fun buildReasons(p: Product, score: Double): List<String> {
            val reasons = mutableListOf<String>()
            if (!detectedDisease.isNullOrBlank() && p.relevanceScore >= 0.25) {
                reasons += "Effective against $detectedDisease"
            }
            if (p.rating >= 4.0) reasons += "High farmer ratings"
            if (p.popularityScore >= 0.6) reasons += "Frequently purchased"
            if (p.availability) reasons += "In stock"
            val ps = priceScore(p.price)
            if (ps >= 0.7) reasons += "Cost-effective compared to alternatives"
            if (p.reviewCount >= 1000) reasons += "Large number of reviews"
            if (reasons.isEmpty()) reasons += "Recommended based on combined signals"
            return reasons
        }

        val scored = products.map { p ->
            val s = computeScore(p)
            RankedProduct(p, s, buildReasons(p, s))
        }.sortedByDescending { it.score }

        // Category helpers (case-insensitive contains)
        val treatmentKeywords = listOf("medicine", "fungicide", "pesticide", "herbicide", "insecticide")
        val toolKeywords = listOf("tool", "implement", "equipment", "tractor", "sprayer")

        val bestTreatment = scored.filter { rp ->
            val cat = rp.product.category.lowercase()
            treatmentKeywords.any { cat.contains(it) } || (rp.product.relevanceScore >= 0.5)
        }.take(3)

        val recommendedTools = scored.filter { rp ->
            val cat = rp.product.category.lowercase()
            toolKeywords.any { cat.contains(it) }
        }.take(3)

        val excluded = (bestTreatment + recommendedTools).map { it.product.name }.toSet()

        val alternative = scored.filter { rp -> !excluded.contains(rp.product.name) }

        return RankingResult(bestTreatment, recommendedTools, alternative)
    }
}
