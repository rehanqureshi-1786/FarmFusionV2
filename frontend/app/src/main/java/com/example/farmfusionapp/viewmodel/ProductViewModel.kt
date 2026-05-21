package com.example.farmfusionapp.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.models.RankedProduct
import com.example.farmfusionapp.repository.ProductRepository
import com.example.farmfusionapp.service.ProductRankingService
import kotlinx.coroutines.launch

class ProductViewModel(
    private val repository: ProductRepository = ProductRepository.create()
) : ViewModel() {

    private val _bestTreatment = MutableLiveData<List<RankedProduct>>(emptyList())
    val bestTreatment: LiveData<List<RankedProduct>> = _bestTreatment

    private val _recommendedTools = MutableLiveData<List<RankedProduct>>(emptyList())
    val recommendedTools: LiveData<List<RankedProduct>> = _recommendedTools

    private val _alternativeProducts = MutableLiveData<List<RankedProduct>>(emptyList())
    val alternativeProducts: LiveData<List<RankedProduct>> = _alternativeProducts

    private val _loading = MutableLiveData(false)
    val loading: LiveData<Boolean> = _loading

    fun loadProducts(detectedDisease: String?) {
        _loading.value = true
        viewModelScope.launch {
            try {
                val result = repository.getRankedProducts(detectedDisease)
                _bestTreatment.value = result.bestTreatment
                _recommendedTools.value = result.recommendedTools
                _alternativeProducts.value = result.alternativeProducts
            } catch (t: Throwable) {
                // swallow here — UI should observe empty lists and present errors elsewhere
                _bestTreatment.value = emptyList()
                _recommendedTools.value = emptyList()
                _alternativeProducts.value = emptyList()
            } finally {
                _loading.value = false
            }
        }
    }
}
