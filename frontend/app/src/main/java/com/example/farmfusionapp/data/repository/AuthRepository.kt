package com.example.farmfusionapp.data.repository

import com.google.firebase.auth.FirebaseAuth
import com.example.farmfusionapp.network.RetrofitInstance
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.google.firebase.auth.UserProfileChangeRequest

/**
 * AuthRepository using Firebase Email/Password authentication
 * After successful Firebase sign-in, fetches ID token and verifies with backend
 */
class AuthRepository {

    private val auth: FirebaseAuth = FirebaseAuth.getInstance()

    /**
     * Check if user is already logged in with Firebase
     */
    fun isUserLoggedIn(): Boolean {
        return auth.currentUser != null
    }

    /**
     * Get current user ID (or null if not logged in)
     */
    fun getCurrentUserId(): String? {
        return auth.currentUser?.uid
    }

    /**
     * Get current user phone number (may be null for email-only users)
     */
    fun getCurrentUserPhone(): String? {
        return auth.currentUser?.phoneNumber
    }

    /**
     * Get current user display name
     */
    fun getCurrentUserName(): String? {
        return auth.currentUser?.displayName
    }

    /**
     * Logout user from Firebase
     */
    fun logout() {
        auth.signOut()
    }

    /**
     * Register user with email and password, then verify token with backend
     */
    fun registerWithEmail(name: String, email: String, password: String, callback: (Boolean, String) -> Unit) {
        auth.createUserWithEmailAndPassword(email, password)
            .addOnSuccessListener { result ->
                // Set display name
                val user = result.user
                val profileUpdates = UserProfileChangeRequest.Builder()
                    .setDisplayName(name)
                    .build()
                
                user?.updateProfile(profileUpdates)?.addOnCompleteListener {
                    // Fetch ID token and call backend
                    fetchIdTokenAndVerify(callback)
                }
            }
            .addOnFailureListener {
                callback(false, it.message ?: "Registration failed")
            }
    }

    /**
     * Login user with email and password, then verify token with backend
     */
    fun loginWithEmail(email: String, password: String, callback: (Boolean, String) -> Unit) {
        auth.signInWithEmailAndPassword(email, password)
            .addOnSuccessListener {
                fetchIdTokenAndVerify(callback)
            }
            .addOnFailureListener {
                callback(false, it.message ?: "Login failed")
            }
    }

    /**
     * Fetches Firebase ID token and verifies it with the backend
     */
    fun fetchIdTokenAndVerify(callback: (Boolean, String) -> Unit) {
        val user = auth.currentUser
        if (user == null) {
            callback(false, "No authenticated user")
            return
        }

        user.getIdToken(true) // force refresh
            .addOnSuccessListener { result ->
                val idToken = result.token
                if (idToken == null) {
                    callback(false, "Failed to get ID token")
                    return@addOnSuccessListener
                }

                // Verify token with backend using Retrofit in coroutine
                CoroutineScope(Dispatchers.IO).launch {
                    try {
                        val response = RetrofitInstance.api.verifyAuthToken(idToken)
                        withContext(Dispatchers.Main) {
                            if (response.isSuccessful && response.body()?.success == true) {
                                callback(true, idToken) // Return token on success
                            } else {
                                // Try to extract backend error message
                                val backendMsg = response.body()?.message 
                                    ?: response.errorBody()?.string()?.let { 
                                        if (it.contains("\"message\":\"")) {
                                            it.substringAfter("\"message\":\"").substringBefore("\"")
                                        } else null
                                    }
                                
                                val errorMsg = when (response.code()) {
                                    401 -> backendMsg ?: "Invalid session. Please login again."
                                    else -> backendMsg ?: "Backend verification failed: ${response.code()}"
                                }
                                callback(false, errorMsg)
                            }
                        }
                    } catch (e: Exception) {
                        withContext(Dispatchers.Main) {
                            callback(false, e.message ?: "Verification request failed")
                        }
                    }
                }
            }
            .addOnFailureListener {
                callback(false, it.message ?: "Failed to retrieve ID token")
            }
    }

    // Legacy login method (kept for compatibility)
    fun login(email: String, password: String, callback: (Boolean, String) -> Unit) {
        loginWithEmail(email, password, callback)
    }
}
