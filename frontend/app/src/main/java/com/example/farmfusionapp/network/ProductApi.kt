package com.example.farmfusionapp.network

import com.example.farmfusionapp.models.Product
import retrofit2.http.GET

interface ProductApi {
    // Backend store products endpoint
    @GET("api/v1/store/products")
    suspend fun getProducts(): List<StoreProductDto>
}

data class StoreProductDto(
    val name: String,
    val category: String,
    val price: Double,
    val currency: String = "INR",
    val stock_quantity: Double,
    val unit: String,
    val image_url: String? = null,
    val description: String? = null
)
