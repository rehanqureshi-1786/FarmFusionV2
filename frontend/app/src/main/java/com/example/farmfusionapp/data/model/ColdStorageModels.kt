package com.example.farmfusionapp.data.model

import com.google.gson.annotations.SerializedName

data class ColdStorageResponse(
    @SerializedName("success") val success: Boolean = false,
    @SerializedName("count") val count: Int = 0,
    @SerializedName("searchRadiusKm") val searchRadiusKm: Double = 50.0,
    @SerializedName("autoExpanded") val autoExpanded: Boolean = false,
    @SerializedName("searchedArea") val searchedArea: String? = null,
    @SerializedName("results") val results: List<ColdStorageItem> = emptyList()
)

data class ColdStorageItem(
    @SerializedName("id") val id: String = "",
    @SerializedName("name") val name: String = "",
    @SerializedName("address") val address: String = "",
    @SerializedName("village_or_area") val villageOrArea: String? = null,
    @SerializedName("district") val district: String = "",
    @SerializedName("state") val state: String = "",
    @SerializedName("pincode") val pincode: String? = null,
    @SerializedName("latitude") val latitude: Double = 0.0,
    @SerializedName("longitude") val longitude: Double = 0.0,
    @SerializedName("phone_number") val phoneNumber: String? = null,
    @SerializedName("alternate_phone_number") val alternatePhoneNumber: String? = null,
    @SerializedName("contact_person") val contactPerson: String? = null,
    @SerializedName("email") val email: String? = null,
    @SerializedName("rating") val rating: Double = 4.5,
    @SerializedName("opening_hours") val openingHours: String? = null,
    @SerializedName("storage_capacity") val storageCapacity: String? = null,
    @SerializedName("suitable_crops") val suitableCrops: String? = null,
    @SerializedName("cold_storage_type") val coldStorageType: String? = null,
    @SerializedName("temperature_range") val temperatureRange: String? = null,
    @SerializedName("description") val description: String? = null,
    @SerializedName("amenities") val amenities: String? = null,
    @SerializedName("certifications") val certifications: String? = null,
    @SerializedName("distance_km") val distanceKm: Double = 0.0,
    @SerializedName("user_distance_km") val userDistanceKm: Double? = null,
    @SerializedName("searched_area") val searchedArea: String? = null,
    @SerializedName("road_distance_km") val roadDistanceKm: Double = 0.0,
    @SerializedName("drive_time_text") val driveTimeText: String? = null,
    @SerializedName("google_maps_url") val googleMapsUrl: String? = null
)
