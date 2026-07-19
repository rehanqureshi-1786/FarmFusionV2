package com.example.farmfusionapp.ui.screens

import android.Manifest
import android.content.Intent
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
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
import java.util.Locale

private data class ChatMessage(
    val text: String,
    val isUser: Boolean
)

private data class VoiceLanguage(
    val code: String,
    val label: String,
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
    val savedLanguage = remember { AuthStore.getLanguage(context) ?: "en" }
    val listState = rememberLazyListState()

    val availableLanguages = remember {
        listOf(
            VoiceLanguage("en", "English", Locale("en", "IN")),
            VoiceLanguage("hi", "हिन्दी", Locale("hi", "IN")),
            VoiceLanguage("mr", "मराठी", Locale("mr", "IN")),
            VoiceLanguage("pa", "ਪੰਜਾਬੀ", Locale("pa", "IN")),
            VoiceLanguage("te", "తెలుగు", Locale("te", "IN"))
        )
    }

    var selectedLanguage by remember {
        mutableStateOf(availableLanguages.firstOrNull { it.code == savedLanguage } ?: availableLanguages.first())
    }
    var query by remember { mutableStateOf("") }
    var assistantState by remember { mutableStateOf(VoiceAssistantState.IDLE) }
    var pendingRoute by remember { mutableStateOf<(() -> Unit)?>(null) }
    var ttsReady by remember { mutableStateOf(false) }
    var suggestions by remember { mutableStateOf<List<String>>(emptyList()) }
    val chatMessages = remember { mutableStateListOf<ChatMessage>() }

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

    val tts = remember {
        TextToSpeech(context) { status -> ttsReady = status == TextToSpeech.SUCCESS }
    }

    fun currentSpeechIntent(): Intent {
        val localeTag = when (selectedLanguage.code) {
            "hi" -> "hi-IN"
            "mr" -> "mr-IN"
            "pa" -> "pa-IN"
            "te" -> "te-IN"
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

    fun resolvedSpeakLocale(code: String): Locale {
        return availableLanguages.firstOrNull { it.code == code }?.locale ?: selectedLanguage.locale
    }

    fun speak(text: String, languageCode: String) {
        if (!ttsReady) return

        assistantState = VoiceAssistantState.SPEAKING
        tts.language = resolvedSpeakLocale(languageCode)
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "farmfusion_voice")
    }

    fun submitQuery(text: String) {
        val cleaned = text.trim()
        if (cleaned.isBlank()) return
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
            assistantState = VoiceAssistantState.LISTENING
            speechRecognizer?.startListening(currentSpeechIntent())
        } else {
            Toast.makeText(context, "Microphone permission is required", Toast.LENGTH_SHORT).show()
        }
    }

    DisposableEffect(speechRecognizer) {
        tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
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
                assistantState = VoiceAssistantState.LISTENING
            }

            override fun onBeginningOfSpeech() {
                assistantState = VoiceAssistantState.LISTENING
            }

            override fun onRmsChanged(rmsdB: Float) = Unit
            override fun onBufferReceived(buffer: ByteArray?) = Unit

            override fun onEndOfSpeech() {
                assistantState = VoiceAssistantState.PROCESSING
            }

            override fun onError(error: Int) {
                assistantState = VoiceAssistantState.IDLE
                Toast.makeText(context, "Mic could not hear clearly. Try again.", Toast.LENGTH_SHORT).show()
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
            tts.stop()
            tts.shutdown()
        }
    }

    LaunchedEffect(voiceState) {
        when (val state = voiceState) {
            is VoiceViewModel.VoiceState.Success -> {
                val responseText = state.response.response.trim()
                chatMessages.add(ChatMessage(responseText, isUser = false))
                suggestions = state.response.follow_up_suggestions?.filter { it.isNotBlank() }.orEmpty()
                speak(responseText, state.response.detected_language)
                viewModel.resetState()
            }

            is VoiceViewModel.VoiceState.Error -> {
                val errorText = "Error: ${state.message}"
                chatMessages.add(ChatMessage(errorText, isUser = false))
                suggestions = emptyList()
                speak(errorText, selectedLanguage.code)
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
                        "Farm Assistant",
                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)
                    )
                },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
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
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Only show Hero if no messages yet
                AnimatedVisibility(
                    visible = chatMessages.isEmpty(),
                    enter = expandVertically() + fadeIn(),
                    exit = shrinkVertically() + fadeOut()
                ) {
                    VoiceHero(
                        state = assistantState,
                        selectedLanguage = selectedLanguage.label,
                        onMicClick = {
                            if (speechRecognizer == null) {
                                Toast.makeText(context, "Speech recognition not available", Toast.LENGTH_SHORT).show()
                            } else if (assistantState == VoiceAssistantState.LISTENING) {
                                speechRecognizer.stopListening()
                                assistantState = VoiceAssistantState.IDLE
                            } else {
                                permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                            }
                        }
                    )
                }

                LazyColumn(
                    state = listState,
                    modifier = Modifier.weight(1f),
                    contentPadding = PaddingValues(vertical = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(chatMessages) { message ->
                        VoiceBubble(message)
                    }

                    if (assistantState == VoiceAssistantState.PROCESSING) {
                        item {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(8.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                CircularProgressIndicator(modifier = Modifier.size(24.dp), strokeWidth = 2.dp)
                            }
                        }
                    }
                }

                if (suggestions.isNotEmpty()) {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            "Suggested for you:",
                            style = MaterialTheme.typography.labelMedium,
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
                                    color = Color.White.copy(alpha = 0.8f),
                                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)),
                                    modifier = Modifier.weight(1f)
                                ) {
                                    Text(
                                        suggestion,
                                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                                        style = MaterialTheme.typography.bodySmall,
                                        textAlign = TextAlign.Center,
                                        maxLines = 2
                                    )
                                }
                            }
                        }
                    }
                }

                // Premium Search Bar UI
                Surface(
                    shape = RoundedCornerShape(32.dp),
                    color = Color.White.copy(alpha = 0.95f),
                    modifier = Modifier
                        .fillMaxWidth()
                        .shadow(10.dp, RoundedCornerShape(32.dp)),
                    border = BorderStroke(1.dp, Color(0xFFF0F0F0))
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Rounded.Search,
                            contentDescription = null,
                            tint = Color.Gray,
                            modifier = Modifier.size(20.dp)
                        )
                        TextField(
                            value = query,
                            onValueChange = { query = it },
                            modifier = Modifier.weight(1f),
                            placeholder = { Text("Ask your farming question...", color = Color.Gray) },
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

                        IconButton(
                            onClick = {
                                if (assistantState == VoiceAssistantState.LISTENING) {
                                    speechRecognizer?.stopListening()
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
        shape = RoundedCornerShape(28.dp),
        color = Color.White.copy(alpha = 0.6f),
        border = BorderStroke(1.dp, Color.White.copy(alpha = 0.5f))
    ) {
        Column(
            modifier = Modifier.padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Box(
                    modifier = Modifier
                        .size(100.dp)
                        .scale(scale)
                        .background(
                            MaterialTheme.colorScheme.primary.copy(alpha = 0.1f),
                            CircleShape
                        )
                )

                Surface(
                    onClick = onMicClick,
                    modifier = Modifier.size(80.dp),
                    shape = CircleShape,
                    color = if (state == VoiceAssistantState.LISTENING) Color(0xFFD32F2F) else MaterialTheme.colorScheme.primaryContainer,
                    shadowElevation = 4.dp
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            imageVector = if (state == VoiceAssistantState.LISTENING) Icons.Rounded.GraphicEq else Icons.Rounded.Mic,
                            contentDescription = null,
                            tint = if (state == VoiceAssistantState.LISTENING) Color.White else MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(36.dp)
                        )
                    }
                }
            }

            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = when (state) {
                        VoiceAssistantState.LISTENING -> "Listening..."
                        VoiceAssistantState.PROCESSING -> "Analyzing..."
                        VoiceAssistantState.SPEAKING -> "FarmFusion is speaking"
                        else -> "Ask anything about farming"
                    },
                    style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)
                )
                Text(
                    text = "Current language: $selectedLanguage",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
            }
        }
    }
}

@Composable
private fun VoiceBubble(message: ChatMessage) {
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
            modifier = Modifier.widthIn(max = 280.dp)
        ) {
            Text(
                text = message.text,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                style = MaterialTheme.typography.bodyMedium.copy(color = contentColor, lineHeight = 20.sp)
            )
        }
    }
}