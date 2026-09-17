package com.example.farmfusionapp.data.model

import com.google.gson.annotations.SerializedName

data class CreateMarketListingRequest(
    @SerializedName("crop_name")
    val cropName: String,

    @SerializedName("quantity")
    val quantity: Double,

    @SerializedName("unit")
    val unit: String = "Quintal",

    @SerializedName("price_per_unit")
    val pricePerUnit: Double? = null,

    @SerializedName("image_url")
    val imageUrl: String? = null,

    @SerializedName("media_urls")
    val mediaUrls: List<String> = emptyList(),

    @SerializedName("latitude")
    val latitude: Double? = null,

    @SerializedName("longitude")
    val longitude: Double? = null,

    @SerializedName("location_name")
    val locationName: String? = null,

    @SerializedName("description")
    val description: String? = null
)

data class MarketListingDto(
    @SerializedName("id")
    val id: Int? = null,

    @SerializedName("crop_name")
    val cropName: String? = null,

    @SerializedName("quantity")
    val quantity: Double? = null,

    @SerializedName("unit")
    val unit: String? = null,

    @SerializedName("price_per_unit")
    val pricePerUnit: Double? = null,

    @SerializedName("image_url")
    val imageUrl: String? = null,

    @SerializedName("media_urls")
    val mediaUrls: List<String>? = null,

    @SerializedName("latitude")
    val latitude: Double? = null,

    @SerializedName("longitude")
    val longitude: Double? = null,

    @SerializedName("location_name")
    val locationName: String? = null,

    @SerializedName("description")
    val description: String? = null,

    @SerializedName("user_id")
    val userId: Int? = null,

    @SerializedName("is_active")
    val isActive: Boolean? = null,

    @SerializedName("created_at")
    val createdAt: String? = null
)

object MarketListingStore {
    private val _localListings = androidx.compose.runtime.mutableStateListOf<MarketListingDto>()
    val localListings: List<MarketListingDto> get() = _localListings

    fun addListing(listing: MarketListingDto) {
        _localListings.add(0, listing)
    }

    fun removeListing(id: Int) {
        _localListings.removeAll { it.id == id }
    }

    fun toggleSoldStatus(id: Int) {
        val index = _localListings.indexOfFirst { it.id == id }
        if (index != -1) {
            val current = _localListings[index]
            _localListings[index] = current.copy(isActive = !(current.isActive ?: true))
        }
    }

    fun setListings(listings: List<MarketListingDto>) {
        _localListings.clear()
        _localListings.addAll(listings)
    }
}

fun getDefaultCropPrice(cropName: String?): Double {
    val name = cropName?.lowercase() ?: ""
    return when {
        name.contains("wheat") -> 2200.0
        name.contains("rice") || name.contains("paddy") -> 2800.0
        name.contains("onion") -> 1600.0
        name.contains("maize") || name.contains("corn") -> 1900.0
        name.contains("cotton") -> 6800.0
        name.contains("soybean") || name.contains("soya") -> 4300.0
        name.contains("mustard") -> 5400.0
        name.contains("groundnut") -> 6200.0
        name.contains("potato") -> 1400.0
        name.contains("tomato") -> 1800.0
        name.contains("garlic") -> 8500.0
        name.contains("gram") || name.contains("chana") -> 5300.0
        name.contains("barley") -> 1850.0
        else -> 2100.0
    }
}
