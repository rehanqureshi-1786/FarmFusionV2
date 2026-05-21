package com.example.farmfusionapp.viewmodel

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.farmfusionapp.data.repository.AuthRepository
import com.example.farmfusionapp.utils.AuthStore
import kotlinx.coroutines.launch
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.data.model.UserProfileResponse
import retrofit2.Response

/**
 * AuthViewModel - Manages authentication with Firebase Email/Password
 */
class AuthViewModel : ViewModel() {

    private val repo = AuthRepository()

    /**
     * Check if user is already logged in (both Firebase and local session)
     */
    fun isUserLoggedIn(context: Context): Boolean {
        return repo.isUserLoggedIn() && AuthStore.isLoggedIn(context)
    }

    /**
     * Get current user info
     */
    fun getCurrentUserInfo(): Triple<String?, String?, String?> {
        return Triple(repo.getCurrentUserId(), repo.getCurrentUserPhone(), repo.getCurrentUserName())
    }

    /**
     * Register user with name, email and password
     */
    fun registerWithEmail(context: Context, name: String, email: String, password: String, callback: (Boolean, String) -> Unit) {
        if (name.isBlank()) {
            callback(false, "Please enter your full name")
            return
        }
        if (email.isBlank() || password.length < 6) {
            callback(false, "Enter valid email and at least 6 characters password")
            return
        }
        repo.registerWithEmail(name, email, password) { success, result ->
            if (success) {
                // result is the ID token
                AuthStore.saveLoginSession(context, result)
                callback(true, "Welcome $name!")
            } else {
                callback(false, result)
            }
        }
    }

    /**
     * Login user with email and password
     */
    fun loginWithEmail(context: Context, email: String, password: String, callback: (Boolean, String) -> Unit) {
        if (email.isBlank() || password.isBlank()) {
            callback(false, "Email and password cannot be empty")
            return
        }
        repo.loginWithEmail(email, password) { success, result ->
            if (success) {
                // result is the ID token
                AuthStore.saveLoginSession(context, result)
                callback(true, "Welcome back!")
            } else {
                callback(false, result)
            }
        }
    }

    /**
     * Verify existing session with backend and sync profile
     */
    fun verifySession(context: Context, callback: (Boolean, String) -> Unit) {
        repo.fetchIdTokenAndVerify { success, result ->
            if (success) {
                val token = result // result is the ID token
                AuthStore.saveLoginSession(context, token)
                
                // Fetch profile to sync language preference
                viewModelScope.launch {
                    try {
                        val response: Response<UserProfileResponse> = RetrofitInstance.api.getUserProfile(token)
                        if (response.isSuccessful) {
                            val profile = response.body()?.profile
                            profile?.language_preference?.let { lang ->
                                val localLang = AuthStore.getLanguage(context)
                                if (lang != localLang) {
                                    AuthStore.saveLanguage(context, lang)
                                    // Trigger recreation if language changed
                                    (context as? android.app.Activity)?.recreate()
                                }
                            }
                        }
                        callback(true, "Session verified and profile synced")
                    } catch (e: Exception) {
                        // Even if profile fetch fails, we consider auth successful if token verify worked
                        callback(true, "Session verified (profile sync failed)")
                    }
                }
            } else {
                AuthStore.clearLoginSession(context)
                callback(false, result)
            }
        }
    }

    /**
     * Logout user
     */
    fun logout(context: Context) {
        repo.logout()
        AuthStore.clearLoginSession(context)
    }

    // Legacy method - kept for compatibility
    fun login(context: Context, email: String, password: String, callback: (Boolean, String) -> Unit) {
        loginWithEmail(context, email, password, callback)
    }
}
