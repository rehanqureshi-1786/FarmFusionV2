package com.example.farmfusionapp.utils

import android.content.Context

/**
 * Delegating to AuthStore to maintain consistency
 */
object LanguagePreferences {
    fun getSelectedLanguage(context: Context): String? {
        return AuthStore.getLanguage(context)
    }

    fun saveSelectedLanguage(context: Context, languageCode: String) {
        AuthStore.saveLanguage(context, languageCode)
    }
}
