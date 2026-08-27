package com.example.farmfusionapp.ml

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.LifecycleOwner
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.Text
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.TextRecognizer
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

/**
 * On-device OCR for soil reports using Google ML Kit Text Recognition.
 * 
 * This class handles the ML Kit text recognizer lifecycle and provides
 * a simple interface to extract raw text from soil report images.
 * 
 * Does NOT parse N/P/K/pH - only returns raw OCR text.
 * Parsing is handled by SoilReportOcrParser.
 */
class SoilReportTextRecognizer private constructor(
    private val textRecognizer: TextRecognizer
) {

    private val TAG = "SoilReportTextRecognizer"

    /**
     * Recognize text from a Bitmap image.
     * 
     * @param bitmap The soil report image as Bitmap
     * @return Raw OCR text, or empty string if no text detected
     * @throws Exception if OCR fails
     */
    suspend fun recognizeText(bitmap: Bitmap): String =
        recognizeText(InputImage.fromBitmap(bitmap, 0))

    /**
     * Recognize text from an InputImage (e.g., from camera or file URI).
     *
     * @param inputImage The soil report image as InputImage
     * @return Raw OCR text, or empty string if no text detected
     * @throws Exception if OCR fails
     */
    suspend fun recognizeText(inputImage: InputImage): String =
        suspendCancellableCoroutine { cont ->
            try {
                textRecognizer.process(inputImage)
                    .addOnSuccessListener { result -> cont.resume(result.text) }
                    .addOnFailureListener { e ->
                        Log.e(TAG, "OCR failed", e)
                        if (cont.isActive) cont.resumeWith(Result.failure(Exception("OCR processing failed: ${e.message}")))
                    }
            } catch (e: Exception) {
                Log.e(TAG, "OCR failed", e)
                if (cont.isActive) cont.resumeWith(Result.failure(Exception("OCR processing failed: ${e.message}")))
            }
        }

    /**
     * Close the text recognizer to release resources.
     * Should be called when the recognizer is no longer needed.
     */
    fun close() {
        textRecognizer.close()
    }

    companion object {
        @Volatile
        private var INSTANCE: SoilReportTextRecognizer? = null

        /**
         * Get or create a shared SoilReportTextRecognizer instance.
         * Reuses the ML Kit TextRecognizer to avoid unnecessary initialization.
         * 
         * @param context Application context
         * @return Shared SoilReportTextRecognizer instance
         */
        fun getInstance(context: Context): SoilReportTextRecognizer {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: SoilReportTextRecognizer(
                    TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
                ).also { INSTANCE = it }
            }
        }

        /**
         * Close the shared instance if it exists.
         * Should be called when the app is destroyed or OCR is no longer needed.
         */
        fun closeInstance() {
            INSTANCE?.close()
            INSTANCE = null
        }
    }
}

/**
 * Lifecycle observer to automatically close the OCR recognizer
 * when the LifecycleOwner is destroyed.
 */
class SoilReportTextRecognizerLifecycleObserver(
    private val recognizer: SoilReportTextRecognizer
) : LifecycleEventObserver {
    override fun onStateChanged(source: LifecycleOwner, event: Lifecycle.Event) {
        if (event == Lifecycle.Event.ON_DESTROY) {
            recognizer.close()
        }
    }
}
