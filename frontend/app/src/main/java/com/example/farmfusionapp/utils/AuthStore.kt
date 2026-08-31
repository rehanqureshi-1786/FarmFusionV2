package com.example.farmfusionapp.utils

import android.content.Context

/**
 * AuthStore - Manages persistent authentication state & global language settings using SharedPreferences
 */
object AuthStore {
    private const val PREFS_NAME = "farmfusion_auth_prefs"
    private const val KEY_IS_LOGGED_IN = "is_logged_in"
    private const val KEY_AUTH_TOKEN = "auth_token"
    private const val KEY_LANGUAGE = "selected_language"
    private const val KEY_DIALECT = "selected_dialect"

    /**
     * Save login state and token
     */
    fun saveLoginSession(context: Context, token: String?) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        with(prefs.edit()) {
            putBoolean(KEY_IS_LOGGED_IN, true)
            putString(KEY_AUTH_TOKEN, token)
            apply()
        }
    }

    /**
     * Save selected language and optional dialect
     */
    fun saveLanguage(context: Context, languageCode: String) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_LANGUAGE, languageCode)
            .commit()
    }

    fun saveLanguageAndDialect(context: Context, languageCode: String, dialectCode: String?) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_LANGUAGE, languageCode)
            .putString(KEY_DIALECT, dialectCode)
            .commit()
    }

    /**
     * Get saved language (default "en" or "hi")
     */
    fun getLanguage(context: Context): String? {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getString(KEY_LANGUAGE, null)
    }

    /**
     * Get saved dialect if any
     */
    fun getDialect(context: Context): String? {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getString(KEY_DIALECT, null)
    }

    /**
     * Clear login state
     */
    fun clearLoginSession(context: Context) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        with(prefs.edit()) {
            clear()
            apply()
        }
    }

    /**
     * Check if user is logged in
     */
    fun isLoggedIn(context: Context): Boolean {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getBoolean(KEY_IS_LOGGED_IN, false)
    }

    /**
     * Get saved auth token
     */
    fun getAuthToken(context: Context): String? {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getString(KEY_AUTH_TOKEN, null)
    }
}
