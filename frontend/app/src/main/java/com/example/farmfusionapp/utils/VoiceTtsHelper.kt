package com.example.farmfusionapp.utils

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.speech.tts.Voice
import java.util.Locale

/**
 * Configures device TTS for clearer, less "robotic" speech:
 * - Prefer Google TTS engine when installed (often better than OEM defaults).
 * - Pick the best [Voice] for the locale (quality flags + neural-style names where present).
 * - Mild prosody tuning for Indian languages.
 */
object VoiceTtsHelper {

    private const val GOOGLE_TTS_PACKAGE = "com.google.android.tts"

    fun preferredEnginePackage(context: Context): String? {
        return try {
            context.packageManager.getPackageInfo(GOOGLE_TTS_PACKAGE, 0)
            GOOGLE_TTS_PACKAGE
        } catch (_: PackageManager.NameNotFoundException) {
            null
        }
    }

    /**
     * Apply language, best matching voice, and natural prosody before [TextToSpeech.speak].
     */
    fun prepareSpeak(tts: TextToSpeech, locale: Locale) {
        when (tts.setLanguage(locale)) {
            TextToSpeech.LANG_MISSING_DATA,
            TextToSpeech.LANG_NOT_SUPPORTED -> {
                tts.setLanguage(Locale(locale.language))
            }
        }
        selectBestVoiceForLocale(tts, locale)
        // Slightly slower + neutral pitch reads more naturally than stock "phone" defaults.
        tts.setPitch(1.02f)
        tts.setSpeechRate(speechRateForLocale(locale))
    }

    private fun speechRateForLocale(locale: Locale): Float {
        return when (locale.language) {
            "hi", "mr", "gu", "pa", "te", "kn", "ta", "ml", "bn" -> 0.88f
            else -> 0.92f
        }
    }

    private fun selectBestVoiceForLocale(tts: TextToSpeech, locale: Locale) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) return
        val voices = tts.voices ?: return

        val candidates = voices.asSequence()
            .filter { v ->
                if (v.features.contains(TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED)) return@filter false
                val lang = v.locale.language
                lang.equals(locale.language, ignoreCase = true)
            }
            .toList()

        if (candidates.isEmpty()) return

        val ranked = candidates.sortedWith(
            compareByDescending<Voice> { it.qualityRank() }
                .thenByDescending { it.neuralStyleRank() }
                .thenByDescending { if (it.isNetworkConnectionRequired) 1 else 0 }
        )
        val chosen = ranked.firstOrNull() ?: return
        try {
            val result = tts.setVoice(chosen)
            if (result == TextToSpeech.ERROR) {
                tts.setLanguage(locale)
            }
        } catch (_: Exception) {
            tts.setLanguage(locale)
        }
    }

    private fun Voice.qualityRank(): Int {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) return 0
        return when (quality) {
            Voice.QUALITY_VERY_HIGH -> 4
            Voice.QUALITY_HIGH -> 3
            Voice.QUALITY_NORMAL -> 2
            Voice.QUALITY_LOW -> 1
            else -> 0
        }
    }

    /** Google on-device "neural" style voices often use "-x-" in the internal name. */
    private fun Voice.neuralStyleRank(): Int {
        val n = name.lowercase()
        return when {
            n.contains("-x-") || n.contains("wavenet") || n.contains("neural") -> 2
            n.contains("premium") || n.contains("enhanced") -> 1
            else -> 0
        }
    }

    fun speakBundle(): Bundle = Bundle().apply {
        // Route through media stream so Bluetooth / speaker path matches music (often fuller).
        putInt(TextToSpeech.Engine.KEY_PARAM_STREAM, android.media.AudioManager.STREAM_MUSIC)
    }
}
