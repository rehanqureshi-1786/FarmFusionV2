package com.example.farmfusionapp.ui.screens

import android.Manifest
import android.content.Intent
import android.media.AudioAttributes
import android.media.MediaPlayer
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
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.Send
import androidx.compose.material.icons.automirrored.rounded.VolumeUp
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.VoiceQueryResponse
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.utils.AppLocalizer
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.utils.LocationSnapshotStore
import com.example.farmfusionapp.viewmodel.VoiceViewModel
import kotlinx.coroutines.delay
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

private data class Suggestion(
    val text: String,
    val icon: ImageVector,
    val iconTint: Color,
    val bgTint: Color
)

private enum class VoiceAssistantState {
    IDLE, LISTENING, PROCESSING, SPEAKING
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VoiceAssistantScreen(navController: NavController) {
    val context = LocalContext.current
    val currentAppLang = LocalAppLanguage.current
    val viewModel: VoiceViewModel = viewModel()
    val voiceState by viewModel.voiceState
    val listState = rememberLazyListState()

    val availableLanguages = remember {
        com.example.farmfusionapp.data.model.LanguageRegistry.allLanguages.map { lang ->
            VoiceLanguage(
                code = lang.code,
                label = lang.name,
                nativeLabel = lang.displayTitle,
                locale = lang.getLocale()
            )
        }
    }

    val selectedLanguage = remember(currentAppLang) {
        val preferredDialect = AuthStore.getDialect(context)
        val preferredLang = AuthStore.getLanguage(context) ?: currentAppLang
        val activeCode = preferredDialect ?: preferredLang
        availableLanguages.firstOrNull { it.code == activeCode } ?: availableLanguages.first()
    }

    val activeLangCode = selectedLanguage.code

    val allSuggestions = remember(activeLangCode) {
        listOf(
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg tomato yellow", activeLangCode), Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg mildew pumpkin", activeLangCode), Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg potato blight", activeLangCode), Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg frost recover", activeLangCode), Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg summer water", activeLangCode), Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg wheat ph", activeLangCode), Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg clay soil", activeLangCode), Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg nitrogen cover", activeLangCode), Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg aphids natural", activeLangCode), Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg cabbage worm", activeLangCode), Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg corn protect", activeLangCode), Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7)),
            Suggestion(AppLocalizer.localizeVoiceAssistantPhrase("sugg organic whiteflies", activeLangCode), Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7))
        )
    }

    val displayedSuggestions = remember(allSuggestions) {
        val grouped = allSuggestions.groupBy { it.icon }
        listOf(
            grouped[Icons.Rounded.Eco]?.random(),
            grouped[Icons.Rounded.WaterDrop]?.random(),
            grouped[Icons.Rounded.PestControl]?.random()
        ).filterNotNull().shuffled().take(2)
    }

    var query by remember { mutableStateOf("") }
    var assistantState by remember { mutableStateOf(VoiceAssistantState.IDLE) }
    var ttsReady by remember { mutableStateOf(false) }
    var suggestions by remember { mutableStateOf<List<String>>(emptyList()) }
    val chatMessages = remember { mutableStateListOf<ChatMessage>() }

    var activeMediaPlayer by remember { mutableStateOf<MediaPlayer?>(null) }

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
            playAudioFromBase64(audioB64) {
                assistantState = VoiceAssistantState.IDLE
            }
        } else if (ttsReady) {
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
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            stopAudioPlayback()
            assistantState = VoiceAssistantState.LISTENING
            speechRecognizer?.startListening(currentSpeechIntent())
        } else {
            Toast.makeText(
                context,
                AppLocalizer.localizeVoiceAssistantPhrase("mic permission required", activeLangCode),
                Toast.LENGTH_SHORT
            ).show()
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
                if (assistantState != VoiceAssistantState.SPEAKING) assistantState = VoiceAssistantState.LISTENING
            }
            override fun onBeginningOfSpeech() {
                if (assistantState != VoiceAssistantState.SPEAKING) assistantState = VoiceAssistantState.LISTENING
            }
            override fun onRmsChanged(rmsdB: Float) = Unit
            override fun onBufferReceived(buffer: ByteArray?) = Unit
            override fun onEndOfSpeech() { assistantState = VoiceAssistantState.PROCESSING }
            override fun onError(error: Int) {
                if (assistantState != VoiceAssistantState.SPEAKING) {
                    assistantState = VoiceAssistantState.IDLE
                    Toast.makeText(
                        context,
                        AppLocalizer.localizeVoiceAssistantPhrase("mic hear clearly error", activeLangCode),
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
            override fun onResults(results: android.os.Bundle?) {
                val text = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull().orEmpty()
                if (text.isNotBlank()) submitQuery(text) else assistantState = VoiceAssistantState.IDLE
            }
            override fun onPartialResults(partialResults: android.os.Bundle?) {
                val text = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull().orEmpty()
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
                val voiceBadgeTemplate = AppLocalizer.localizeVoiceAssistantPhrase("voice badge", activeLangCode)
                val voiceBadgeText = String.format(voiceBadgeTemplate, selectedLanguage.nativeLabel)

                val badge = when {
                    state.response.fallback_used == true && !state.response.response_dialect.isNullOrBlank() -> {
                        "${state.response.response_dialect?.uppercase()} • $voiceBadgeText"
                    }
                    state.response.local_tts == true && state.response.native_tts == true -> {
                        "$voiceBadgeText • AI"
                    }
                    else -> voiceBadgeText
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

                suggestions = state.response.follow_up_suggestions?.filter { it.isNotBlank() }?.take(2).orEmpty()
                speakResponse(state.response)

                if (state.response.action == "navigate") {
                    val dest = state.response.data?.get("destination") as? String
                    when (dest) {
                        "market_prices", "mandi" -> navController.navigate("mandi_prices")
                        "weather" -> navController.navigate("weather")
                        "crop_recommendation" -> navController.navigate("crop_recommendation")
                        "disease_detection", "crop_disease" -> navController.navigate("crop_disease")
                        "government_schemes", "financial_services" -> navController.navigate("financial_services")
                        "home", "dashboard" -> navController.navigate("dashboard")
                        "back" -> navController.popBackStack()
                    }
                } else if (state.response.action == "open_camera") {
                    navController.navigate("crop_disease")
                }

                viewModel.resetState()
            }
            is VoiceViewModel.VoiceState.Error -> {
                val errPrefix = AppLocalizer.localizeVoiceAssistantPhrase("error prefix", activeLangCode)
                val errorText = "$errPrefix${state.message}"
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
                    Text(
                        text = AppLocalizer.localizeVoiceAssistantPhrase("farm assistant", activeLangCode),
                        style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B5E20))
                    )
                },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", tint = Color(0xFF1B1B1B))
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(containerColor = Color.Transparent)
            )
        },
        containerColor = Color(0xFFF9FBF9)
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .imePadding()
        ) {
            AnimatedVisibility(
                visible = chatMessages.isEmpty(),
                enter = fadeIn(),
                exit = fadeOut(),
                modifier = Modifier.fillMaxSize()
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(14.dp),
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp, vertical = 6.dp)
                        .padding(bottom = 90.dp)
                ) {
                    VoiceHero(
                        state = assistantState,
                        langCode = activeLangCode,
                        modifier = Modifier.fillMaxWidth(),
                        onMicClick = {
                            if (speechRecognizer == null) {
                                Toast.makeText(
                                    context,
                                    AppLocalizer.localizeVoiceAssistantPhrase("speech unavailable", activeLangCode),
                                    Toast.LENGTH_SHORT
                                ).show()
                            } else if (assistantState == VoiceAssistantState.SPEAKING) {
                                stopAudioPlayback()
                            } else if (assistantState == VoiceAssistantState.LISTENING) {
                                speechRecognizer.stopListening()
                                assistantState = VoiceAssistantState.IDLE
                            } else {
                                permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                            }
                        }
                    )

                    SuggestionsPanel(
                        suggestions = displayedSuggestions,
                        langCode = activeLangCode,
                        onSuggestionClick = { submitQuery(it) }
                    )
                }
            }

            if (chatMessages.isNotEmpty()) {
                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(
                        start = 20.dp,
                        end = 20.dp,
                        top = 12.dp,
                        bottom = 120.dp
                    ),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
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
                            Box(modifier = Modifier.fillMaxWidth().padding(8.dp), contentAlignment = Alignment.Center) {
                                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp, color = Color(0xFF2E7D32))
                                    Text(
                                        text = AppLocalizer.localizeVoiceAssistantPhrase("analyzing", activeLangCode),
                                        style = MaterialTheme.typography.bodySmall,
                                        color = Color.Gray
                                    )
                                }
                            }
                        }
                    }

                    if (assistantState == VoiceAssistantState.SPEAKING) {
                        item {
                            Surface(
                                shape = RoundedCornerShape(20.dp),
                                color = Color(0xFFE8F5E9),
                                border = BorderStroke(1.dp, Color(0xFFC8E6C9)),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                        Icon(Icons.AutoMirrored.Rounded.VolumeUp, contentDescription = null, tint = Color(0xFF2E7D32))
                                        Text(
                                            text = AppLocalizer.localizeVoiceAssistantPhrase("speaking", activeLangCode),
                                            style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF2E7D32))
                                        )
                                    }
                                    Button(
                                        onClick = { stopAudioPlayback() },
                                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F)),
                                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                                        shape = RoundedCornerShape(12.dp),
                                        modifier = Modifier.height(32.dp)
                                    ) {
                                        Text(
                                            text = AppLocalizer.localizeVoiceAssistantPhrase("stop", activeLangCode),
                                            style = MaterialTheme.typography.labelSmall
                                        )
                                    }
                                }
                            }
                        }
                    }

                    if (suggestions.isNotEmpty() && assistantState != VoiceAssistantState.SPEAKING) {
                        item {
                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(
                                    text = AppLocalizer.localizeVoiceAssistantPhrase("suggested label", activeLangCode),
                                    style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold),
                                    color = Color(0xFF2E7D32),
                                    modifier = Modifier.padding(start = 8.dp)
                                )
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    suggestions.take(2).forEach { suggestion ->
                                        Surface(
                                            onClick = { submitQuery(suggestion) },
                                            shape = RoundedCornerShape(16.dp),
                                            color = Color.White,
                                            border = BorderStroke(1.dp, Color(0xFFC8E6C9)),
                                            modifier = Modifier.weight(1f)
                                        ) {
                                            Text(suggestion, modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp), style = MaterialTheme.typography.bodySmall, textAlign = TextAlign.Center, maxLines = 2)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Surface(
                shape = RoundedCornerShape(32.dp),
                color = Color.White,
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .padding(start = 20.dp, end = 20.dp, bottom = 16.dp)
                    .shadow(12.dp, RoundedCornerShape(32.dp), spotColor = Color(0xFF2E7D32).copy(alpha = 0.1f)),
                border = BorderStroke(1.dp, Color(0xFFF0F5F0))
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(imageVector = Icons.Rounded.Search, contentDescription = null, tint = Color(0xFF9E9E9E), modifier = Modifier.size(22.dp))

                    TextField(
                        value = query,
                        onValueChange = { query = it },
                        modifier = Modifier.weight(1f),
                        placeholder = {
                            Text(
                                text = AppLocalizer.localizeVoiceAssistantPhrase("ask farming question placeholder", activeLangCode),
                                color = Color(0xFF9E9E9E),
                                fontSize = 15.sp
                            )
                        },
                        singleLine = true,
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent,
                            cursorColor = Color(0xFF2E7D32)
                        ),
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                        keyboardActions = KeyboardActions(onSend = { submitQuery(query) })
                    )

                    IconButton(
                        onClick = {
                            if (assistantState == VoiceAssistantState.SPEAKING) stopAudioPlayback()
                            else if (assistantState == VoiceAssistantState.LISTENING) speechRecognizer?.stopListening()
                            else permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                        }
                    ) {
                        Icon(
                            imageVector = if (assistantState == VoiceAssistantState.LISTENING) Icons.Rounded.GraphicEq else Icons.Rounded.Mic,
                            contentDescription = "Mic",
                            tint = if (assistantState == VoiceAssistantState.LISTENING) Color(0xFFD32F2F) else Color(0xFF2E7D32)
                        )
                    }

                    if (query.isNotBlank()) {
                        IconButton(onClick = { submitQuery(query) }) {
                            Icon(Icons.AutoMirrored.Rounded.Send, contentDescription = "Send", tint = Color(0xFF2E7D32))
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
    langCode: String,
    modifier: Modifier = Modifier,
    onMicClick: () -> Unit
) {
    val transition = rememberInfiniteTransition(label = "radar")
    val radarScale by transition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1500, easing = LinearOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "radarScale"
    )

    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(32.dp),
        color = Color(0xFFF0F7F0),
        shadowElevation = 0.dp
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            Image(
                painter = painterResource(id = R.drawable.ill_voice_background),
                contentDescription = null,
                contentScale = ContentScale.Crop,
                alpha = 0.8f,
                modifier = Modifier.fillMaxSize().align(Alignment.BottomCenter)
            )

            Column(
                modifier = Modifier.fillMaxWidth().padding(top = 20.dp, bottom = 18.dp, start = 20.dp, end = 20.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = Color.White.copy(alpha = 0.55f),
                    border = BorderStroke(1.dp, Color.White.copy(alpha = 0.8f))
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp)
                    ) {
                        Icon(Icons.Rounded.GraphicEq, contentDescription = null, tint = Color(0xFF388E3C), modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = AppLocalizer.localizeVoiceAssistantPhrase("voice assistant", langCode),
                            style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF2E7D32))
                        )
                    }
                }

                val askPrefix = AppLocalizer.localizeVoiceAssistantPhrase("ask anything about", langCode)
                val farmingWord = AppLocalizer.localizeVoiceAssistantPhrase("farming word", langCode)
                val companionSubtitle = if (state == VoiceAssistantState.LISTENING) {
                    AppLocalizer.localizeVoiceAssistantPhrase("smart companion listening", langCode)
                } else {
                    AppLocalizer.localizeVoiceAssistantPhrase("smart companion ready", langCode)
                }

                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = buildAnnotatedString {
                            append(askPrefix)
                            withStyle(style = SpanStyle(color = Color(0xFF2E7D32))) { append(farmingWord) }
                        },
                        style = MaterialTheme.typography.headlineLarge.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1B1B1B),
                            fontSize = 26.sp,
                            lineHeight = 30.sp
                        ),
                        textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = companionSubtitle,
                        style = MaterialTheme.typography.bodyMedium.copy(
                            color = Color(0xFF616161),
                            fontSize = 13.5.sp,
                            lineHeight = 17.sp
                        ),
                        textAlign = TextAlign.Center
                    )
                }

                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.size(145.dp)
                ) {
                    Canvas(modifier = Modifier.fillMaxSize()) {
                        val stroke = Stroke(width = 2.dp.toPx(), pathEffect = PathEffect.dashPathEffect(floatArrayOf(15f, 15f), 0f))
                        drawCircle(color = Color(0xFF2E7D32).copy(alpha = 0.1f), radius = size.minDimension / 2 * radarScale, style = stroke)
                        drawCircle(color = Color(0xFF2E7D32).copy(alpha = 0.2f), radius = size.minDimension / 3 * radarScale, style = stroke)

                        drawCircle(color = Color(0xFFFFCA28), radius = 5f, center = Offset(size.width * 0.8f, size.height * 0.2f))
                        drawCircle(color = Color(0xFF29B6F6), radius = 7f, center = Offset(size.width * 0.85f, size.height * 0.8f))
                        drawCircle(color = Color(0xFF81C784), radius = 5f, center = Offset(size.width * 0.15f, size.height * 0.7f))
                    }

                    Surface(
                        onClick = onMicClick,
                        modifier = Modifier.size(80.dp).shadow(10.dp, CircleShape, spotColor = Color(0xFF2E7D32).copy(alpha = 0.4f)),
                        shape = CircleShape,
                        color = Color.White,
                        border = BorderStroke(8.dp, Color(0xFFC8E6C9))
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = if (state == VoiceAssistantState.LISTENING) Icons.Rounded.GraphicEq else Icons.Rounded.Mic,
                                contentDescription = null,
                                tint = if (state == VoiceAssistantState.LISTENING) Color(0xFFD32F2F) else Color(0xFF2E7D32),
                                modifier = Modifier.size(36.dp)
                            )
                        }
                    }
                }

                Text(
                    text = AppLocalizer.localizeVoiceAssistantPhrase("tap mic to speak", langCode),
                    style = MaterialTheme.typography.labelSmall.copy(color = Color(0xFF757575))
                )
            }
        }
    }
}

@Composable
private fun SuggestionsPanel(
    suggestions: List<Suggestion>,
    langCode: String,
    modifier: Modifier = Modifier,
    onSuggestionClick: (String) -> Unit
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        shadowElevation = 0.dp,
        border = BorderStroke(1.dp, Color(0xFFF0F5F0))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(bottom = 12.dp)) {
                Icon(Icons.Rounded.AutoAwesome, contentDescription = null, tint = Color(0xFF2E7D32), modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = AppLocalizer.localizeVoiceAssistantPhrase("try asking", langCode),
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B5E20))
                )
            }

            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                suggestions.forEachIndexed { index, suggestion ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable(onClick = { onSuggestionClick(suggestion.text) }),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = suggestion.bgTint,
                            modifier = Modifier.size(36.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(suggestion.icon, contentDescription = null, tint = suggestion.iconTint, modifier = Modifier.size(18.dp))
                            }
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = suggestion.text,
                            style = MaterialTheme.typography.bodyMedium.copy(
                                color = Color(0xFF424242),
                                lineHeight = 18.sp,
                                fontSize = 13.sp
                            ),
                            modifier = Modifier.weight(1f)
                        )
                    }
                    if (index < suggestions.lastIndex) {
                        HorizontalDivider(color = Color(0xFFF5F5F5), thickness = 1.dp)
                    }
                }
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
    val background = if (message.isUser) Color(0xFF2E7D32) else Color.White
    val contentColor = if (message.isUser) Color.White else Color(0xFF1B1B1B)
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
            modifier = Modifier.widthIn(max = 300.dp),
            border = if (!message.isUser) BorderStroke(1.dp, Color(0xFFEEEEEE)) else null
        ) {
            Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)) {
                Text(
                    text = message.text,
                    style = MaterialTheme.typography.bodyMedium.copy(color = contentColor, lineHeight = 20.sp)
                )

                if (!message.isUser) {
                    Spacer(modifier = Modifier.height(8.dp))
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
                                imageVector = Icons.Rounded.VolumeUp,
                                contentDescription = "Replay Speech",
                                tint = Color(0xFF2E7D32),
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}