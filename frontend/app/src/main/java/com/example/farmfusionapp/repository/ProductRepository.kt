package com.example.farmfusionapp.repository

import com.example.farmfusionapp.network.ApiConfig
import com.example.farmfusionapp.network.ProductApi
import com.example.farmfusionapp.service.ProductRankingService
import com.example.farmfusionapp.models.Product
import com.example.farmfusionapp.models.RankedProduct
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class ProductRepository(
    private val api: ProductApi,
    private val rankingService: ProductRankingService
) {

    private fun mapStoreProduct(dto: com.example.farmfusionapp.network.StoreProductDto): Product {
        return Product(
            name = dto.name,
            imageUrl = dto.image_url.orEmpty(),
            price = dto.price,
            rating = 4.2,
            reviewCount = 150,
            buyUrl = "https://www.amazon.in/s?k=${dto.name.replace(" ", "+")}",
            category = dto.category,
            availability = dto.stock_quantity > 0,
            popularityScore = 0.68,
            relevanceScore = if (dto.category.lowercase().contains("pesticide") || dto.category.lowercase().contains("fertilizer")) 0.7 else 0.55
        )
    }

    suspend fun getRankedProducts(detectedDisease: String?) : ProductRankingService.RankingResult {
        val dtos = api.getProducts()
        val products = dtos.map { dto -> mapStoreProduct(dto) }
        return rankingService.rankProducts(products, detectedDisease)
    }

    companion object {
        fun create(): ProductRepository {
            val retrofit = Retrofit.Builder()
                .baseUrl(ApiConfig.BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            val api = retrofit.create(ProductApi::class.java)
            val ranking = ProductRankingService()
            return ProductRepository(api, ranking)
        }
    }
}
