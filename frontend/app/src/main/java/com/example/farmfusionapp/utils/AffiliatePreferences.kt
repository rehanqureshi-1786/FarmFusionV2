package com.example.farmfusionapp.utils

import android.content.Context
import android.net.Uri

object AffiliatePreferences {
    private const val PREFS_NAME = "farmfusion_prefs"
    private const val KEY_AMAZON_ASSOCIATE_TAG = "amazon_associate_tag"
    private const val DEFAULT_ASSOCIATE_TAG = "farmfusionsto-21"

    fun getAssociateTag(context: Context): String {
        return DEFAULT_ASSOCIATE_TAG
    }

    fun saveAssociateTag(context: Context, tag: String) {
        val value = tag.trim().takeIf { it.isNotBlank() }
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE).edit()
        if (value != null) {
            prefs.putString(KEY_AMAZON_ASSOCIATE_TAG, value)
        } else {
            prefs.remove(KEY_AMAZON_ASSOCIATE_TAG)
        }
        prefs.apply()
    }

    fun buildAffiliateUrl(url: String, tag: String?): String {
        if (tag.isNullOrBlank()) return url
        val uri = Uri.parse(url)
        val host = uri.host ?: return url
        if (!host.contains("amazon.")) return url
        if (uri.getQueryParameter("tag") != null) return url
        return uri.buildUpon()
            .appendQueryParameter("tag", tag.trim())
            .build()
            .toString()
    }
}
