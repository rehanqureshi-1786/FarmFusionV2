package com.example.farmfusionapp.ui.screens

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.view.WindowManager
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.Send
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
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

    // --- KEYBOARD FIX ---
    DisposableEffect(context) {
        val activity = context as? Activity
        val window = activity?.window
        val originalMode = window?.attributes?.softInputMode

        window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)

        onDispose {
            originalMode?.let { window.setSoftInputMode(it) }
        }
    }

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

    val allSuggestions = remember {
        listOf(
            Suggestion("Why are the leaves of my tomato plant turning yellow?", Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion("How do I treat powdery mildew on pumpkins?", Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion("What are the early signs of blight in potatoes?", Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion("Why are my apples dropping before they ripen?", Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion("How to recover crops after a mild frost?", Icons.Rounded.Eco, Color(0xFF689F38), Color(0xFFF1F8E9)),
            Suggestion("How often should I water my crops in summer?", Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion("What is the best pH level for growing wheat?", Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion("How can I improve clay soil for vegetables?", Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion("When is the best time of day to irrigate?", Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion("What cover crops fix nitrogen in the soil?", Icons.Rounded.WaterDrop, Color(0xFF0288D1), Color(0xFFE1F5FE)),
            Suggestion("What are natural ways to control aphids on plants?", Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7)),
            Suggestion("How to get rid of caterpillars on cabbage?", Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7)),
            Suggestion("Are ladybugs good for my greenhouse?", Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7)),
            Suggestion("How to protect corn from earworms?", Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7)),
            Suggestion("What is the best organic pesticide for whiteflies?", Icons.Rounded.PestControl, Color(0xFFE64A19), Color(0xFFFBE9E7))
        )
    }

    val displayedSuggestions = remember {
        val grouped = allSuggestions.groupBy { it.icon }
        listOf(
            grouped[Icons.Rounded.Eco]?.random(),
            grouped[Icons.Rounded.WaterDrop]?.random(),
            grouped[Icons.Rounded.PestControl]?.random()
        ).filterNotNull().shuffled()
    }

    var selectedLanguage by remember {
        mutableStateOf(availableLanguages.firstOrNull { it.code == savedLanguage } ?: availableLanguages.first())
    }
    var query by remember { mutableStateOf("") }
    var assistantState by remember { mutableStateOf(VoiceAssistantState.IDLE) }
    var ttsReady by remember { mutableStateOf(false) }
    val chatMessages = remember { mutableStateListOf<ChatMessage>() }

    LaunchedEffect(chatMessages.size) {
        if (chatMessages.isNotEmpty()) {
            listState.animateScrollToItem(chatMessages.size - 1)
        }
    }

    val speechRecognizer = remember {
        if (SpeechRecognizer.isRecognitionAvailable(context)) {
            SpeechRecognizer.createSpeechRecognizer(context)
        } else null
    }

    val tts = remember {
        TextToSpeech(context) { status -> ttsReady = status == TextToSpeech.SUCCESS }
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
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            assistantState = VoiceAssistantState.LISTENING
            speechRecognizer?.startListening(currentSpeechIntent())
        } else {
            Toast.makeText(context, "Microphone permission required", Toast.LENGTH_SHORT).show()
        }
    }

    DisposableEffect(speechRecognizer) {
        tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) = Unit
            override fun onDone(utteranceId: String?) { assistantState = VoiceAssistantState.IDLE }
            override fun onError(utteranceId: String?) { assistantState = VoiceAssistantState.IDLE }
        })

        val listener = object : RecognitionListener {
            override fun onReadyForSpeech(params: android.os.Bundle?) { assistantState = VoiceAssistantState.LISTENING }
            override fun onBeginningOfSpeech() { assistantState = VoiceAssistantState.LISTENING }
            override fun onRmsChanged(rmsdB: Float) = Unit
            override fun onBufferReceived(buffer: ByteArray?) = Unit
            override fun onEndOfSpeech() { assistantState = VoiceAssistantState.PROCESSING }
            override fun onError(error: Int) {
                assistantState = VoiceAssistantState.IDLE
                Toast.makeText(context, "Mic could not hear clearly. Try again.", Toast.LENGTH_SHORT).show()
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
            tts.stop()
            tts.shutdown()
        }
    }

    LaunchedEffect(voiceState) {
        when (val state = voiceState) {
            is VoiceViewModel.VoiceState.Success -> {
                val responseText = state.response.response.trim()
                chatMessages.add(ChatMessage(responseText, isUser = false))
                if (ttsReady) {
                    assistantState = VoiceAssistantState.SPEAKING
                    tts.language = availableLanguages.firstOrNull { it.code == state.response.detected_language }?.locale ?: selectedLanguage.locale
                    tts.speak(responseText, TextToSpeech.QUEUE_FLUSH, null, "farmfusion_voice")
                }
                viewModel.resetState()
            }
            is VoiceViewModel.VoiceState.Error -> {
                chatMessages.add(ChatMessage("Error: ${state.message}", isUser = false))
                assistantState = VoiceAssistantState.IDLE
                viewModel.resetState()
            }
            else -> Unit
        }
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Farm Assistant", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B5E20))) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back", tint = Color(0xFF1B1B1B))
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(containerColor = Color.Transparent)
            )
        },
        containerColor = Color(0xFFF9FBF9) // Base canvas color
    ) { padding ->
        // Box overlay structure allows the chat canvas to span full height behind the input bar
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .imePadding()
        ) {

            // Hero and Suggestions overlay (Hidden if chat started)
            AnimatedVisibility(
                visible = chatMessages.isEmpty(),
                enter = fadeIn(),
                exit = fadeOut(),
                modifier = Modifier.fillMaxSize()
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 20.dp, vertical = 8.dp)
                        .padding(bottom = 80.dp) // Keeps this content safely above the input bar
                ) {
                    VoiceHero(
                        state = assistantState,
                        modifier = Modifier.weight(1f),
                        onMicClick = {
                            if (speechRecognizer == null) {
                                Toast.makeText(context, "Speech recognition unavailable", Toast.LENGTH_SHORT).show()
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
                        onSuggestionClick = { submitQuery(it) }
                    )
                }
            }

            // Chat View (Spans full size so it scrolls seamlessly behind the bar)
            if (chatMessages.isNotEmpty()) {
                LazyColumn(
                    state = listState,
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(
                        start = 20.dp,
                        end = 20.dp,
                        top = 12.dp,
                        bottom = 96.dp // Generous bottom pad ensures the last message can be scrolled fully above the floating bar
                    ),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(chatMessages) { message -> VoiceBubble(message) }
                    if (assistantState == VoiceAssistantState.PROCESSING) {
                        item {
                            Box(modifier = Modifier.fillMaxWidth().padding(8.dp), contentAlignment = Alignment.Center) {
                                CircularProgressIndicator(modifier = Modifier.size(24.dp), strokeWidth = 2.dp, color = Color(0xFF2E7D32))
                            }
                        }
                    }
                }
            }

            // Floating Bottom Input Bar
            Surface(
                shape = RoundedCornerShape(32.dp),
                color = Color.White,
                modifier = Modifier
                    .align(Alignment.BottomCenter) // Anchors to the bottom of the Box on top of the LazyColumn
                    .fillMaxWidth()
                    .padding(start = 20.dp, end = 20.dp, bottom = 16.dp) // Fixed signature!
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
                        placeholder = { Text("Ask your farming question...", color = Color(0xFF9E9E9E), fontSize = 15.sp) },
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
                            if (assistantState == VoiceAssistantState.LISTENING) speechRecognizer?.stopListening()
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
                modifier = Modifier.fillMaxSize().padding(top = 28.dp, bottom = 24.dp, start = 24.dp, end = 24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.SpaceBetween
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
                        Text("Voice Assistant", style = MaterialTheme.typography.labelMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF2E7D32)))
                    }
                }

                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        text = buildAnnotatedString {
                            append("Ask anything\nabout ")
                            withStyle(style = SpanStyle(color = Color(0xFF2E7D32))) { append("farming") }
                        },
                        style = MaterialTheme.typography.headlineLarge.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1B1B1B),
                            fontSize = 38.sp,
                            lineHeight = 38.sp
                        ),
                        textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = "Your smart farming companion\nis ${if (state == VoiceAssistantState.LISTENING) "listening..." else "ready."}",
                        style = MaterialTheme.typography.bodyMedium.copy(
                            color = Color(0xFF616161),
                            fontSize = 15.sp
                        ),
                        textAlign = TextAlign.Center
                    )
                }

                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.size(180.dp)
                ) {
                    Canvas(modifier = Modifier.fillMaxSize()) {
                        val stroke = Stroke(width = 2.dp.toPx(), pathEffect = PathEffect.dashPathEffect(floatArrayOf(15f, 15f), 0f))
                        drawCircle(color = Color(0xFF2E7D32).copy(alpha = 0.1f), radius = size.minDimension / 2 * radarScale, style = stroke)
                        drawCircle(color = Color(0xFF2E7D32).copy(alpha = 0.2f), radius = size.minDimension / 3 * radarScale, style = stroke)

                        drawCircle(color = Color(0xFFFFCA28), radius = 6f, center = Offset(size.width * 0.8f, size.height * 0.2f))
                        drawCircle(color = Color(0xFF29B6F6), radius = 8f, center = Offset(size.width * 0.85f, size.height * 0.8f))
                        drawCircle(color = Color(0xFF81C784), radius = 6f, center = Offset(size.width * 0.15f, size.height * 0.7f))
                    }

                    Surface(
                        onClick = onMicClick,
                        modifier = Modifier.size(96.dp).shadow(12.dp, CircleShape, spotColor = Color(0xFF2E7D32).copy(alpha = 0.4f)),
                        shape = CircleShape,
                        color = Color.White,
                        border = BorderStroke(10.dp, Color(0xFFC8E6C9))
                    ) {
                        Box(contentAlignment = Alignment.Center) {
                            Icon(
                                imageVector = if (state == VoiceAssistantState.LISTENING) Icons.Rounded.GraphicEq else Icons.Rounded.Mic,
                                contentDescription = null,
                                tint = if (state == VoiceAssistantState.LISTENING) Color(0xFFD32F2F) else Color(0xFF2E7D32),
                                modifier = Modifier.size(42.dp)
                            )
                        }
                    }
                }

                Text("Tap the mic to speak", style = MaterialTheme.typography.labelSmall.copy(color = Color(0xFF757575)))
            }
        }
    }
}

@Composable
private fun SuggestionsPanel(
    suggestions: List<Suggestion>,
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
                Text("Try asking", style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B5E20)))
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
private fun VoiceBubble(message: ChatMessage) {
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
            modifier = Modifier.widthIn(max = 280.dp),
            border = if (!message.isUser) BorderStroke(1.dp, Color(0xFFEEEEEE)) else null
        ) {
            Text(
                text = message.text,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                style = MaterialTheme.typography.bodyMedium.copy(color = contentColor, lineHeight = 20.sp)
            )
        }
    }
}