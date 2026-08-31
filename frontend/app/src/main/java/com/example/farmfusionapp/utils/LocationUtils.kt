package com.example.farmfusionapp.utils

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.Geocoder
import android.location.Location
import android.os.Looper
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.content.ContextCompat
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.coroutines.resume
import java.util.Locale

object LocationSnapshotStore {
    var latestCity by mutableStateOf<String?>(null)
    var latestLatitude by mutableStateOf<Double?>(null)
    var latestLongitude by mutableStateOf<Double?>(null)
}

/**
 * Composable for requesting location permissions at runtime
 */
@Composable
fun LocationPermissionEffect(
    context: Context,
    onPermissionGranted: () -> Unit,
    onPermissionDenied: () -> Unit
) {
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val fineLocationGranted = permissions[Manifest.permission.ACCESS_FINE_LOCATION] ?: false
        val coarseLocationGranted = permissions[Manifest.permission.ACCESS_COARSE_LOCATION] ?: false
        
        if (fineLocationGranted || coarseLocationGranted) {
            onPermissionGranted()
        } else {
            onPermissionDenied()
        }
    }
    
    LaunchedEffect(Unit) {
        val fineLocationPermission = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
        val coarseLocationPermission = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
        
        if (fineLocationPermission == PackageManager.PERMISSION_GRANTED ||
            coarseLocationPermission == PackageManager.PERMISSION_GRANTED
        ) {
            onPermissionGranted()
        } else {
            permissionLauncher.launch(
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        }
    }
}

/**
 * Get device coordinates from Google Play Services fused provider.
 * Uses last known location first for speed, then falls back to a short
 * high-accuracy update request for fresher GPS/WiFi/cellular data.
 */
@SuppressLint("MissingPermission")
suspend fun getDeviceLocation(context: Context): Pair<Double, Double>? {
    if (!hasLocationPermission(context)) return null

    return try {
        val fusedClient = LocationServices.getFusedLocationProviderClient(context)
        val lastKnownLocation = getLastKnownLocation(fusedClient)

        if (lastKnownLocation != null && isGoodEnough(lastKnownLocation)) {
            cacheCoordinates(lastKnownLocation.latitude, lastKnownLocation.longitude)
            Pair(lastKnownLocation.latitude, lastKnownLocation.longitude)
        } else {
            withTimeoutOrNull(6_000L) { requestFreshLocation(fusedClient) }?.let {
                cacheCoordinates(it.latitude, it.longitude)
                Pair(it.latitude, it.longitude)
            } ?: lastKnownLocation?.let {
                cacheCoordinates(it.latitude, it.longitude)
                Pair(it.latitude, it.longitude)
            }
        }
    } catch (e: Exception) {
        e.printStackTrace()
        null
    }
}

/**
 * Convert latitude/longitude to a city-like place name using device geocoder only.
 */
suspend fun getCityFromLocation(context: Context, latitude: Double, longitude: Double, languageCode: String? = null): String? {
    return try {
        withContext(Dispatchers.IO) {
            val locale = if (languageCode != null) Locale.forLanguageTag(languageCode) else Locale.getDefault()
            val geocoder = Geocoder(context, locale)
            @Suppress("DEPRECATION")
            val addresses = geocoder.getFromLocation(latitude, longitude, 1)
            val city = addresses
                ?.firstOrNull()
                ?.let { it.locality ?: it.subAdminArea ?: it.adminArea ?: it.featureName }

            cacheResolvedLocation(latitude, longitude, city)
            city
        }
    } catch (e: Exception) {
        e.printStackTrace()
        null
    }
}

suspend fun getRegionFromCoordinates(context: Context, latitude: Double, longitude: Double, languageCode: String? = null): String? {
    return try {
        withContext(Dispatchers.IO) {
            val locale = if (languageCode != null) Locale.forLanguageTag(languageCode) else Locale.getDefault()
            val geocoder = Geocoder(context, locale)
            @Suppress("DEPRECATION")
            val addresses = geocoder.getFromLocation(latitude, longitude, 1)
            if (!addresses.isNullOrEmpty()) {
                addresses[0].subAdminArea
                    ?: addresses[0].adminArea
                    ?: addresses[0].locality
                    ?: "India"
            } else {
                "India"
            }
        }
    } catch (e: Exception) {
        e.printStackTrace()
        "India"
    }
}

fun getCachedCityForLocation(latitude: Double, longitude: Double): String? {
    val cachedCity = LocationSnapshotStore.latestCity ?: return null
    val cachedLat = LocationSnapshotStore.latestLatitude ?: return null
    val cachedLon = LocationSnapshotStore.latestLongitude ?: return null

    val latDiff = kotlin.math.abs(cachedLat - latitude)
    val lonDiff = kotlin.math.abs(cachedLon - longitude)
    return if (latDiff < 0.05 && lonDiff < 0.05) cachedCity else null
}

private fun hasLocationPermission(context: Context): Boolean {
    val hasFine = ContextCompat.checkSelfPermission(
        context,
        Manifest.permission.ACCESS_FINE_LOCATION
    ) == PackageManager.PERMISSION_GRANTED

    val hasCoarse = ContextCompat.checkSelfPermission(
        context,
        Manifest.permission.ACCESS_COARSE_LOCATION
    ) == PackageManager.PERMISSION_GRANTED

    return hasFine || hasCoarse
}

@SuppressLint("MissingPermission")
private suspend fun getLastKnownLocation(
    fusedClient: FusedLocationProviderClient
): Location? = suspendCancellableCoroutine { continuation ->
    fusedClient.lastLocation
        .addOnSuccessListener { location ->
            if (continuation.isActive) continuation.resume(location)
        }
        .addOnFailureListener {
            if (continuation.isActive) continuation.resume(null)
        }
}

@SuppressLint("MissingPermission")
private suspend fun requestFreshLocation(
    fusedClient: FusedLocationProviderClient
): Location? = suspendCancellableCoroutine { continuation ->
    val request = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 2_000L)
        .setMinUpdateIntervalMillis(1_000L)
        .setWaitForAccurateLocation(true)
        .setMaxUpdates(1)
        .build()

    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            fusedClient.removeLocationUpdates(this)
            if (continuation.isActive) {
                continuation.resume(result.lastLocation)
            }
        }
    }

    continuation.invokeOnCancellation {
        fusedClient.removeLocationUpdates(callback)
    }

    fusedClient.requestLocationUpdates(request, callback, Looper.getMainLooper())
        .addOnFailureListener {
            fusedClient.removeLocationUpdates(callback)
            if (continuation.isActive) {
                continuation.resume(null)
            }
        }
}

private fun isGoodEnough(location: Location): Boolean {
    val ageMs = System.currentTimeMillis() - location.time
    val accuracyMeters = if (location.hasAccuracy()) location.accuracy else Float.MAX_VALUE
    return ageMs <= 120_000L && accuracyMeters <= 150f
}

private fun cacheCoordinates(latitude: Double, longitude: Double) {
    LocationSnapshotStore.latestLatitude = latitude
    LocationSnapshotStore.latestLongitude = longitude
}

private fun cacheResolvedLocation(latitude: Double, longitude: Double, city: String?) {
    if (!city.isNullOrBlank()) {
        LocationSnapshotStore.latestCity = city
    }
    cacheCoordinates(latitude, longitude)
}
