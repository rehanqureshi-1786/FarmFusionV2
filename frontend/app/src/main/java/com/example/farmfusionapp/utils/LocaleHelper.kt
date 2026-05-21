package com.example.farmfusionapp.utils

import android.content.Context
import android.content.ContextWrapper
import android.content.res.Configuration
import android.os.Build
import java.util.Locale

object LocaleHelper {

    /**
     * Maps app preference codes to a locale used for `res/values-xx` resources.
     * Hinglish uses Hindi resources so the UI is fully localized where strings exist.
     */
    fun resourceLocaleTag(languageCode: String): String {
        val c = languageCode.trim().lowercase()
        return when (c) {
            "hi-en", "hinglish" -> "hi"
            else -> c.take(2).ifBlank { "en" }
        }
    }

    /** API / AI language code (hinglish → hi for model output). */
    fun apiLanguageCode(languageCode: String): String {
        val c = languageCode.trim().lowercase()
        return when (c) {
            "hi-en", "hinglish" -> "hi"
            else -> c.ifBlank { "en" }
        }
    }

    fun wrap(context: Context, languageCode: String): ContextWrapper {
        val tag = resourceLocaleTag(languageCode)
        val locale = localeForTag(tag)
        Locale.setDefault(locale)

        val config = Configuration(context.resources.configuration)
        config.setLocale(locale)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            val localized = context.createConfigurationContext(config)
            return ContextWrapper(localized)
        }
        @Suppress("DEPRECATION")
        context.resources.updateConfiguration(config, context.resources.displayMetrics)
        return ContextWrapper(context)
    }

    private fun localeForTag(tag: String): Locale {
        return when (tag) {
            "en" -> Locale("en", "IN")
            "hi" -> Locale("hi", "IN")
            "mr" -> Locale("mr", "IN")
            "gu" -> Locale("gu", "IN")
            "pa" -> Locale("pa", "IN")
            "te" -> Locale("te", "IN")
            else -> if (tag.contains("-")) Locale.forLanguageTag(tag) else Locale(tag)
        }
    }

    @Suppress("DEPRECATION")
    fun applyLocale(context: Context) {
        val tag = resourceLocaleTag(AuthStore.getLanguage(context) ?: "en")
        val locale = localeForTag(tag)
        Locale.setDefault(locale)
        val config = Configuration(context.resources.configuration)
        config.setLocale(locale)
        context.resources.updateConfiguration(config, context.resources.displayMetrics)
    }
}
