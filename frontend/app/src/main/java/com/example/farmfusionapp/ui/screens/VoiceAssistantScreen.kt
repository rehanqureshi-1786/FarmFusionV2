package com.example.farmfusionapp.ui.screens

import android.Manifest
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Base64
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.Send
import androidx.compose.material.icons.automirrored.rounded.VolumeUp
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.data.model.VoiceQueryResponse
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.components.PremiumButton
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.utils.LocationSnapshotStore
import com.example.farmfusionapp.viewmodel.VoiceViewModel
import java.io.File
import java.io.FileOutputStream
import java.util.Locale

private data class ChatMessage(
    val text: String,
    val isUser: Boolean,
    val audioBase64: String? = null,
    val languageCode: String? = null,
    val ttsBadge: String? = null,
    val isNativeTts: Boolean? = null,
    val fallbackUsed: Boolean? = null
)

private data class VoiceLanguage(
    val code: String,
    val label: String,
    val nativeLabel: String,
    val locale: Locale
)

private enum class VoiceAssistantState {
    IDLE, LISTENING, PROCESSING, SPEAKING
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VoiceAssistantScreen(navController: NavController) {
    val context = LocalContext.current
    val viewModel: VoiceViewModel = viewModel()
    val voiceState by viewModel.voiceState
    val listState = rememberLazyListState()

    // 20+ Verified Indian Languages & Agrarian Regional Varieties
    val availableLanguages = remember {
        listOf(
            VoiceLanguage("hi", "Hindi", "हिन्दी (Hindi)", Locale("hi", "IN")),
            VoiceLanguage("mr", "Marathi", "मराठी (Marathi)", Locale("mr", "IN")),
            VoiceLanguage("gu", "Gujarati", "ગુજરાતી (Gujarati)", Locale("gu", "IN")),
            VoiceLanguage("pa", "Punjabi", "ਪੰਜਾਬੀ (Punjabi)", Locale("pa", "IN")),
            VoiceLanguage("te", "Telugu", "తెలుగు (Telugu)", Locale("te", "IN")),
            VoiceLanguage("bn", "Bengali", "বাংলা (Bengali)", Locale("bn", "IN")),
            VoiceLanguage("ta", "Tamil", "தமிழ் (Tamil)", Locale("ta", "IN")),
            VoiceLanguage("kn", "Kannada", "ಕನ್ನಡ (Kannada)", Locale("kn", "IN")),
            VoiceLanguage("ml", "Malayalam", "മലയാളം (Malayalam)", Locale("ml", "IN")),
            VoiceLanguage("or", "Odia", "ଓଡ଼ିଆ (Odia)", Locale("or", "IN")),
            VoiceLanguage("as", "Assamese", "অসমীয়া (Assamese)", Locale("as", "IN")),
            VoiceLanguage("mai", "Maithili", "मैथिली (Maithili)", Locale("mai", "IN")),
            VoiceLanguage("bgc", "Haryanvi", "हरियाणवी (Haryanvi)", Locale("hi", "IN")),
            VoiceLanguage("hne", "Chhattisgarhi", "छत्तीसगढ़ी (Chhattisgarhi)", Locale("hi", "IN")),
            VoiceLanguage("awa", "Awadhi", "अवधी (Awadhi)", Locale("hi", "IN")),
            VoiceLanguage("mag", "Magahi", "मगही (Magahi)", Locale("hi", "IN")),
            VoiceLanguage("gbm", "Garhwali", "गढ़वाली (Garhwali)", Locale("hi", "IN")),
            VoiceLanguage("dgo", "Dogri", "डोगरी (Dogri)", Locale("hi", "IN")),
            VoiceLanguage("ur", "Urdu", "اردو (Urdu)", Locale("ur", "IN")),
            VoiceLanguage("en", "English", "English (India)", Locale("en", "IN"))
        )
    }

    var selectedLanguage by remember {
        val preferred = AuthStore.getLanguage(context) ?: "hi"
        mutableStateOf(availableLanguages.firstOrNull { it.code == preferred } ?: availableLanguages.first())
    }
    var languageDropdownExpanded by remember { mutableStateOf(false) }

    var query by remember { mutableStateOf("") }
    var assistantState by remember { mutableStateOf(VoiceAssistantState.IDLE) }
    var ttsReady by remember { mutableStateOf(false) }
    var suggestions by remember { mutableStateOf<List<String>>(emptyList()) }
    var debugMode by remember { mutableStateOf(false) }
    var lastDebugResponse by remember { mutableStateOf<VoiceQueryResponse?>(null) }
    val chatMessages = remember { mutableStateListOf<ChatMessage>() }

    // Native Android MediaPlayer for 16 kHz 16-bit PCM WAV playback
    var activeMediaPlayer by remember { mutableStateOf<MediaPlayer?>(null) }

    // Auto-scroll to bottom
    LaunchedEffect(chatMessages.size) {
        if (chatMessages.isNotEmpty()) {
            listState.animateScrollToItem(chatMessages.size - 1)
        }
    }

    val speechRecognizer = remember {
        if (SpeechRecognizer.isRecognitionAvailable(context)) {
            SpeechRecognizer.createSpeechRecognizer(context)
        } else {
            null
        }
    }

    val androidTts = remember {
        TextToSpeech(context) { status -> ttsReady = status == TextToSpeech.SUCCESS }
    }

    fun stopAudioPlayback() {
        try {
            activeMediaPlayer?.let {
                if (it.isPlaying) it.stop()
                it.reset()
                it.release()
            }
        } catch (_: Exception) {}
        activeMediaPlayer = null
        try {
            if (ttsReady) androidTts.stop()
        } catch (_: Exception) {}
        assistantState = VoiceAssistantState.IDLE
    }

    fun playAudioFromBase64(base64Data: String, onFinished: () -> Unit) {
        stopAudioPlayback()
        try {
            val audioBytes = Base64.decode(base64Data, Base64.DEFAULT)
            val tempFile = File(context.cacheDir, "farmfusion_audio_response.wav")
            FileOutputStream(tempFile).use { it.write(audioBytes) }

            val player = MediaPlayer().apply {
                setAudioAttributes(
                    AudioAttributes.Builder()
                        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                        .setUsage(AudioAttributes.USAGE_ASSISTANCE_NAVIGATION_GUIDANCE)
                        .build()
                )
                setDataSource(tempFile.absolutePath)
                setOnPreparedListener {
                    assistantState = VoiceAssistantState.SPEAKING
                    start()
                }
                setOnCompletionListener {
                    stopAudioPlayback()
                    onFinished()
                }
                setOnErrorListener { _, _, _ ->
                    stopAudioPlayback()
                    onFinished()
                    true
                }
                prepareAsync()
            }
            activeMediaPlayer = player
        } catch (e: Exception) {
            stopAudioPlayback()
            onFinished()
        }
    }

    fun speakResponse(response: VoiceQueryResponse) {
        val audioB64 = response.audio_base64
        if (!audioB64.isNullOrBlank()) {
            // Play genuine Local Neural VITS Audio
            playAudioFromBase64(audioB64) {
                assistantState = VoiceAssistantState.IDLE
            }
        } else if (ttsReady) {
            // Fallback to Android Device TTS
            assistantState = VoiceAssistantState.SPEAKING
            val targetLocale = availableLanguages.firstOrNull { it.code == response.detected_language }?.locale
                ?: selectedLanguage.locale
            androidTts.language = targetLocale
            androidTts.speak(response.response, TextToSpeech.QUEUE_FLUSH, null, "farmfusion_voice")
        }
    }

    fun currentSpeechIntent(): Intent {
        val localeTag = when (selectedLanguage.code) {
            "hi" -> "hi-IN"
            "mr" -> "mr-IN"
            "pa" -> "pa-IN"
            "te" -> "te-IN"
            "gu" -> "gu-IN"
            "bn" -> "bn-IN"
            "ta" -> "ta-IN"
            "kn" -> "kn-IN"
            "ml" -> "ml-IN"
            "or" -> "or-IN"
            "as" -> "as-IN"
            "ur" -> "ur-IN"
            "mai" -> "mai-IN"
            else -> "en-IN"
        }
        return Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, localeTag)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, localeTag)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
        }
    }

    fun submitQuery(text: String) {
        val cleaned = text.trim()
        if (cleaned.isBlank()) return
        stopAudioPlayback()
        chatMessages.add(ChatMessage(cleaned, isUser = true))
        assistantState = VoiceAssistantState.PROCESSING
        viewModel.processVoiceQuery(
            query = cleaned,
            location = LocationSnapshotStore.latestCity,
            latitude = LocationSnapshotStore.latestLatitude,
            longitude = LocationSnapshotStore.latestLongitude,
            languageHint = selectedLanguage.code
        )
        query = ""
        suggestions = emptyList()
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            stopAudioPlayback()
            assistantState = VoiceAssistantState.LISTENING
            speechRecognizer?.startListening(currentSpeechIntent())
        } else {
            Toast.makeText(context, "Microphone permission is required", Toast.LENGTH_SHORT).show()
        }
    }

    DisposableEffect(speechRecognizer) {
        androidTts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) = Unit
            override fun onDone(utteranceId: String?) {
                assistantState = VoiceAssistantState.IDLE
            }
            override fun onError(utteranceId: String?) {
                assistantState = VoiceAssistantState.IDLE
            }
        })

        val listener = object : RecognitionListener {
            override fun onReadyForSpeech(params: android.os.Bundle?) {
                if (assistantState != VoiceAssistantState.SPEAKING) {
                    assistantState = VoiceAssistantState.LISTENING
                }
            }

            override fun onBeginningOfSpeech() {
                if (assistantState != VoiceAssistantState.SPEAKING) {
                    assistantState = VoiceAssistantState.LISTENING
                }
            }

            override fun onRmsChanged(rmsdB: Float) = Unit
            override fun onBufferReceived(buffer: ByteArray?) = Unit

            override fun onEndOfSpeech() {
                assistantState = VoiceAssistantState.PROCESSING
            }

            override fun onError(error: Int) {
                if (assistantState != VoiceAssistantState.SPEAKING) {
                    assistantState = VoiceAssistantState.IDLE
                    Toast.makeText(context, "Mic could not hear clearly. Please tap and try again.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onResults(results: android.os.Bundle?) {
                val text = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    ?.firstOrNull()
                    .orEmpty()
                if (text.isNotBlank()) submitQuery(text) else assistantState = VoiceAssistantState.IDLE
            }

            override fun onPartialResults(partialResults: android.os.Bundle?) {
                val text = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    ?.firstOrNull()
                    .orEmpty()
                if (text.isNotBlank()) query = text
            }

            override fun onEvent(eventType: Int, params: android.os.Bundle?) = Unit
        }

        speechRecognizer?.setRecognitionListener(listener)
        onDispose {
            speechRecognizer?.destroy()
            stopAudioPlayback()
            androidTts.shutdown()
        }
    }

    LaunchedEffect(voiceState) {
        when (val state = voiceState) {
            is VoiceViewModel.VoiceState.Success -> {
                val responseText = state.response.response.trim()
                lastDebugResponse = state.response

                // Compute farmer-friendly badge
                val badge = when {
                    state.response.fallback_used == true && !state.response.response_dialect.isNullOrBlank() -> {
                        "${state.response.response_dialect?.uppercase()} उत्तर • हिन्दी आवाज"
                    }
                    state.response.local_tts == true && state.response.native_tts == true -> {
                        "${selectedLanguage.label} आवाज • ऑन-डिवाइस"
                    }
                    else -> "${selectedLanguage.label} आवाज"
                }

                chatMessages.add(
                    ChatMessage(
                        text = responseText,
                        isUser = false,
                        audioBase64 = state.response.audio_base64,
                        languageCode = state.response.detected_language,
                        ttsBadge = badge,
                        isNativeTts = state.response.native_tts,
                        fallbackUsed = state.response.fallback_used
                    )
                )

                suggestions = state.response.follow_up_suggestions?.filter { it.isNotBlank() }.orEmpty()
                speakResponse(state.response)

                // Handle In-App Voice Navigation Actions
                if (state.response.action == "navigate") {
                    val dest = state.response.data?.get("destination") as? String
                    when (dest) {
                        "market_prices", "mandi" -> navController.navigate(NavRoutes.MandiPrices)
                        "weather" -> navController.navigate(NavRoutes.Weather)
                        "crop_recommendation" -> navController.navigate(NavRoutes.CropRecommendation)
                        "disease_detection", "crop_disease" -> navController.navigate(NavRoutes.CropDisease)
                        "government_schemes", "financial_services" -> navController.navigate(NavRoutes.FinancialServices)
                        "home", "dashboard" -> navController.navigate(NavRoutes.Dashboard)
                        "back" -> navController.popBackStack()
                    }
                } else if (state.response.action == "open_camera") {
                    navController.navigate(NavRoutes.CropDisease)
                }

                viewModel.resetState()
            }

            is VoiceViewModel.VoiceState.Error -> {
                val errorText = "त्रुटि: ${state.message}"
                chatMessages.add(ChatMessage(errorText, isUser = false))
                suggestions = emptyList()
                if (ttsReady) {
                    assistantState = VoiceAssistantState.SPEAKING
                    androidTts.language = selectedLanguage.locale
                    androidTts.speak(errorText, TextToSpeech.QUEUE_FLUSH, null, "farmfusion_err")
                }
                viewModel.resetState()
            }

            else -> Unit
        }
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.clickable { languageDropdownExpanded = true }
                    ) {
                        Text(
                            "Farm Assistant",
                            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
                        )
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = MaterialTheme.colorScheme.primaryContainer,
                            modifier = Modifier.padding(start = 4.dp)
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    selectedLanguage.label,
                                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                                )
                                Icon(
                                    Icons.Rounded.ArrowDropDown,
                                    contentDescription = "Select Language",
                                    modifier = Modifier.size(16.dp),
                                    tint = MaterialTheme.colorScheme.primary
                                )
                            }
                        }

                        DropdownMenu(
                            expanded = languageDropdownExpanded,
                            onDismissRequest = { languageDropdownExpanded = false }
                        ) {
                            availableLanguages.forEach { lang ->
                                DropdownMenuItem(
                                    text = { Text(lang.nativeLabel, fontWeight = if (lang.code == selectedLanguage.code) FontWeight.Bold else FontWeight.Normal) },
                                    onClick = {
                                        selectedLanguage = lang
                                        AuthStore.saveLanguage(context, lang.code)
                                        languageDropdownExpanded = false
                                        Toast.makeText(context, "Language set to ${lang.label}", Toast.LENGTH_SHORT).show()
                                    }
                                )
                            }
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { debugMode = !debugMode }) {
                        Icon(
                            Icons.Rounded.BugReport,
                            contentDescription = "Debug Mode",
                            tint = if (debugMode) MaterialTheme.colorScheme.primary else Color.Gray
                        )
                    }
                }
            )
        }
    ) { padding ->
        NeoScaffoldBackground(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Hero Area (Shown when empty chat)
                AnimatedVisibility(
                    visible = chatMessages.isEmpty(),
                    enter = expandVertically() + fadeIn(),
                    exit = shrinkVertically() + fadeOut()
                ) {
                    VoiceHero(
                        state = assistantState,
                        selectedLanguage = selectedLanguage.nativeLabel,
                        onMicClick = {
                            if (assistantState == VoiceAssistantState.SPEAKING) {
                                stopAudioPlayback()
                            } else if (assistantState == VoiceAssistantState.LISTENING) {
                                speechRecognizer?.stopListening()
                                assistantState = VoiceAssistantState.IDLE
                            } else {
                                permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                            }
                        }
                    )
                }

                // Debug Metadata Panel
                if (debugMode && lastDebugResponse != null) {
                    Surface(
                        shape = RoundedCornerShape(16.dp),
                        color = Color(0xFF1E293B),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text("🔧 VOICE DEBUG METADATA", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold, color = Color(0xFF38BDF8)))
                            Text("INTENT: ${lastDebugResponse?.intent} (conf: ${lastDebugResponse?.confidence})", style = MaterialTheme.typography.bodySmall, color = Color.White)
                            Text("ACTION: ${lastDebugResponse?.action}", style = MaterialTheme.typography.bodySmall, color = Color.White)
                            Text("LANG DETECTED: ${lastDebugResponse?.detected_language} | DIALECT: ${lastDebugResponse?.detected_dialect}", style = MaterialTheme.typography.bodySmall, color = Color.White)
                            Text("TTS PROVIDER: ${lastDebugResponse?.tts_provider} | MODEL: ${lastDebugResponse?.tts_model}", style = MaterialTheme.typography.bodySmall, color = Color(0xFF4ADE80))
                            Text("NATIVE TTS: ${lastDebugResponse?.native_tts} | LOCAL: ${lastDebugResponse?.local_tts} | HAS AUDIO: ${!lastDebugResponse?.audio_base64.isNullOrBlank()}", style = MaterialTheme.typography.bodySmall, color = Color(0xFFFDE047))
                            if (lastDebugResponse?.fallback_used == true) {
                                Text("FALLBACK: ${lastDebugResponse?.fallback_reason}", style = MaterialTheme.typography.bodySmall, color = Color(0xFFF87171))
                            }
                        }
                    }
                }

                // Chat Timeline
                LazyColumn(
                    state = listState,
                    modifier = Modifier.weight(1f),
                    contentPadding = PaddingValues(vertical = 8.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(chatMessages) { message ->
                        VoiceBubble(
                            message = message,
                            onReplayClick = {
                                if (!message.audioBase64.isNullOrBlank()) {
                                    playAudioFromBase64(message.audioBase64) {}
                                } else if (ttsReady) {
                                    assistantState = VoiceAssistantState.SPEAKING
                                    androidTts.language = selectedLanguage.locale
                                    androidTts.speak(message.text, TextToSpeech.QUEUE_FLUSH, null, "replay")
                                }
                            }
                        )
                    }

                    if (assistantState == VoiceAssistantState.PROCESSING) {
                        item {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(8.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                                    Text("समझ रहा हूँ… (Analyzing)", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                                }
                            }
                        }
                    }
                }

                // Assistant Speaking / Stop Banner
                if (assistantState == VoiceAssistantState.SPEAKING) {
                    Surface(
                        shape = RoundedCornerShape(20.dp),
                        color = MaterialTheme.colorScheme.primaryContainer,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Icon(Icons.AutoMirrored.Rounded.VolumeUp, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                                Text("बता रहा हूँ… (Speaking)", style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary))
                            }
                            Button(
                                onClick = { stopAudioPlayback() },
                                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error),
                                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Text("रोकें (Stop)", style = MaterialTheme.typography.labelSmall)
                            }
                        }
                    }
                }

                // Follow-up Suggestions
                if (suggestions.isNotEmpty() && assistantState != VoiceAssistantState.SPEAKING) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            "सुझाव (Suggested):",
                            style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold),
                            color = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.padding(start = 8.dp)
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            suggestions.take(2).forEach { suggestion ->
                                Surface(
                                    onClick = { submitQuery(suggestion) },
                                    shape = RoundedCornerShape(16.dp),
                                    color = Color.White.copy(alpha = 0.9f),
                                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)),
                                    modifier = Modifier.weight(1f)
                                ) {
                                    Text(
                                        suggestion,
                                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp),
                                        style = MaterialTheme.typography.bodySmall,
                                        textAlign = TextAlign.Center,
                                        maxLines = 2
                                    )
                                }
                            }
                        }
                    }
                }

                // Input Bar UI
                Surface(
                    shape = RoundedCornerShape(32.dp),
                    color = Color.White.copy(alpha = 0.98f),
                    modifier = Modifier
                        .fillMaxWidth()
                        .shadow(8.dp, RoundedCornerShape(32.dp)),
                    border = BorderStroke(1.dp, Color(0xFFE2E8F0))
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        TextField(
                            value = query,
                            onValueChange = { query = it },
                            modifier = Modifier.weight(1f),
                            placeholder = { Text("सवाल पूछें... (Ask question)", color = Color.Gray, fontSize = 14.sp) },
                            singleLine = true,
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = Color.Transparent,
                                unfocusedContainerColor = Color.Transparent,
                                disabledContainerColor = Color.Transparent,
                                focusedIndicatorColor = Color.Transparent,
                                unfocusedIndicatorColor = Color.Transparent,
                                cursorColor = MaterialTheme.colorScheme.primary
                            ),
                            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                            keyboardActions = KeyboardActions(onSend = { submitQuery(query) })
                        )

                        // Mic Toggle Button
                        IconButton(
                            onClick = {
                                if (assistantState == VoiceAssistantState.SPEAKING) {
                                    stopAudioPlayback()
                                } else if (assistantState == VoiceAssistantState.LISTENING) {
                                    speechRecognizer?.stopListening()
                                    assistantState = VoiceAssistantState.IDLE
                                } else {
                                    permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                                }
                            }
                        ) {
                            Icon(
                                imageVector = if (assistantState == VoiceAssistantState.LISTENING) Icons.Rounded.GraphicEq else Icons.Rounded.Mic,
                                contentDescription = "Mic",
                                tint = if (assistantState == VoiceAssistantState.LISTENING) Color.Red else MaterialTheme.colorScheme.primary
                            )
                        }

                        if (query.isNotBlank()) {
                            IconButton(onClick = { submitQuery(query) }) {
                                Icon(
                                    imageVector = Icons.AutoMirrored.Rounded.Send,
                                    contentDescription = "Send",
                                    tint = MaterialTheme.colorScheme.primary
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun VoiceHero(
    state: VoiceAssistantState,
    selectedLanguage: String,
    onMicClick: () -> Unit
) {
    val transition = rememberInfiniteTransition(label = "voice")
    val scale by transition.animateFloat(
        initialValue = 1f,
        targetValue = if (state == VoiceAssistantState.LISTENING) 1.2f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse"
    )

    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White.copy(alpha = 0.85f),
        border = BorderStroke(1.dp, Color.White.copy(alpha = 0.5f)),
        shadowElevation = 2.dp
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Box(
                    modifier = Modifier
                        .size(90.dp)
                        .scale(scale)
                        .background(
                            MaterialTheme.colorScheme.primary.copy(alpha = 0.12f),
                            CircleShape
                        )
                )

                Surface(
                    onClick = onMicClick,
                    modifier = Modifier.size(72.dp),
                    shape = CircleShape,
                    color = if (state == VoiceAssistantState.LISTENING) Color(0xFFD32F2F) else MaterialTheme.colorScheme.primaryContainer,
                    shadowElevation = 4.dp
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = if (state == VoiceAssistantState.LISTENING) Icons.Rounded.GraphicEq else Icons.Rounded.Mic,
                            contentDescription = null,
                            tint = if (state == VoiceAssistantState.LISTENING) Color.White else MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(32.dp)
                        )
                    }
                }
            }

            Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    text = when (state) {
                        VoiceAssistantState.LISTENING -> "सुन रहा हूँ… (Listening)"
                        VoiceAssistantState.PROCESSING -> "समझ रहा हूँ… (Analyzing)"
                        VoiceAssistantState.SPEAKING -> "बता रहा हूँ… (Speaking)"
                        else -> "बोलकर पूछें (Tap mic to speak)"
                    },
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
                )
                Text(
                    text = "चुनी गई भाषा: $selectedLanguage",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
            }
        }
    }
}

@Composable
private fun VoiceBubble(
    message: ChatMessage,
    onReplayClick: () -> Unit
) {
    val alignment = if (message.isUser) Alignment.End else Alignment.Start
    val background = if (message.isUser) MaterialTheme.colorScheme.primary else Color.White
    val contentColor = if (message.isUser) MaterialTheme.colorScheme.onPrimary else Color(0xFF1B1B1B)
    val shape = if (message.isUser) {
        RoundedCornerShape(topStart = 20.dp, topEnd = 4.dp, bottomStart = 20.dp, bottomEnd = 20.dp)
    } else {
        RoundedCornerShape(topStart = 4.dp, topEnd = 20.dp, bottomStart = 20.dp, bottomEnd = 20.dp)
    }

    Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = alignment) {
        Surface(
            shape = shape,
            color = background,
            shadowElevation = 2.dp,
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            Column(modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp)) {
                Text(
                    text = message.text,
                    style = MaterialTheme.typography.bodyMedium.copy(color = contentColor, lineHeight = 20.sp)
                )

                if (!message.isUser) {
                    Spacer(modifier = Modifier.height(6.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        if (!message.ttsBadge.isNullOrBlank()) {
                            Text(
                                text = message.ttsBadge,
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontSize = 10.sp,
                                    color = if (message.fallbackUsed == true) Color(0xFFD97706) else Color(0xFF16A34A),
                                    fontWeight = FontWeight.Medium
                                )
                            )
                        } else {
                            Spacer(modifier = Modifier.width(1.dp))
                        }

                        IconButton(
                            onClick = onReplayClick,
                            modifier = Modifier.size(24.dp)
                        ) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Rounded.VolumeUp,
                                contentDescription = "Replay Speech",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}