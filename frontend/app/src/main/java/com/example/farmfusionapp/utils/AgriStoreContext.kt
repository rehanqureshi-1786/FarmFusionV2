package com.example.farmfusionapp.utils

/**
 * Holds the last user intent when opening Agri Store (browse vs crop vs disease).
 * Set before [com.example.farmfusionapp.ui.screens.NavRoutes.ProductStore] navigation.
 */
data class AgriStoreParams(
    val source: String = "browse",
    val crop: String? = null,
    val diseaseName: String? = null,
    val cropHint: String? = null
)

object AgriStoreContext {
    var current: AgriStoreParams = AgriStoreParams()
        private set

    fun setBrowse() {
        current = AgriStoreParams()
    }

    fun setForCrop(cropName: String) {
        val c = cropName.trim()
        current = AgriStoreParams(source = "crop", crop = c.ifEmpty { null })
    }

    fun setForDisease(diseaseName: String, cropHint: String?) {
        val d = diseaseName.trim()
        val h = cropHint?.trim()?.ifEmpty { null }
        current = AgriStoreParams(
            source = "disease",
            diseaseName = d.ifEmpty { null },
            cropHint = h
        )
    }
}
