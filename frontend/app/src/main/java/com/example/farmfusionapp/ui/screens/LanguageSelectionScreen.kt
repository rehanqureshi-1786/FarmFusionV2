package com.example.farmfusionapp.ui.screens

import android.app.Activity
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.automirrored.rounded.VolumeUp
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.LanguageRegistry
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.utils.LocaleHelper
import com.example.farmfusionapp.viewmodel.UserViewModel
import kotlinx.coroutines.launch

import androidx.compose.ui.draw.shadow
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalDensity
import dev.chrisbanes.haze.HazeState
import dev.chrisbanes.haze.HazeStyle
import dev.chrisbanes.haze.haze
import dev.chrisbanes.haze.hazeChild

data class AppLanguageUi(
    val code: String,
    val nativeName: String,
    val englishName: String,
    val illustration: Int,
    val baseColor: Color
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LanguageSelectionScreen(
    navController: NavController,
    userViewModel: UserViewModel = viewModel()
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val density = LocalDensity.current

    val hazeState = remember { HazeState() }
    var headerHeightDp by remember { mutableStateOf(210.dp) }

    // 14 requested languages with targeted custom colors and distinct illustrations
    val uiLanguages = remember {
        listOf(
            AppLanguageUi("hi", "हिंदी", "Hindi", R.drawable.ill_lang_hi, Color(0xFF4CAF50)), // Green
            AppLanguageUi("en", "English", "English", R.drawable.ill_lang_en, Color(0xFF4CAF50)), // Green
            AppLanguageUi("gu", "ગુજરાતી", "Gujarati", R.drawable.ill_lang_gu, Color(0xFF2196F3)), // Blue
            AppLanguageUi("mr", "मराठी", "Marathi", R.drawable.ill_lang_mr, Color(0xFF4CAF50)), // Green
            AppLanguageUi("pa", "ਪੰਜਾਬੀ", "Punjabi", R.drawable.ill_lang_pa, Color(0xFFFFB300)), // Golden Yellow/Orange
            AppLanguageUi("bn", "বাংলা", "Bengali", R.drawable.ill_lang_bn, Color(0xFFE91E63)), // Reddish Pink
            AppLanguageUi("ta", "தமிழ்", "Tamil", R.drawable.ill_lang_ta, Color(0xFFFF6D00)), // Dark Orange
            AppLanguageUi("te", "తెలుగు", "Telugu", R.drawable.ill_lang_te, Color(0xFF2196F3)), // Blue
            AppLanguageUi("kn", "ಕನ್ನಡ", "Kannada", R.drawable.ill_lang_kn, Color(0xFFFFC107)), // Yellow
            AppLanguageUi("ml", "മലയാളം", "Malayalam", R.drawable.ill_lang_ml, Color(0xFF9C27B0)), // Purple
            AppLanguageUi("or", "ଓଡ଼ିଆ", "Odia", R.drawable.ill_lang_or, Color(0xFFFF9800)), // Orange
            AppLanguageUi("as", "অসমীয়া", "Assamese", R.drawable.ill_lang_as, Color(0xFF2196F3)), // Blue
            AppLanguageUi("ur", "اردو", "Urdu", R.drawable.ill_lang_ur, Color(0xFF4CAF50)), // Green
            AppLanguageUi("mai", "मैथिली", "Maithili", R.drawable.ill_lang_mai, Color(0xFFF44336)) // Red
        )
    }

    // 14-language title map for bilingual header (selected language bigger + English smaller)
    val localizedTitles = remember {
        mapOf(
            "en" to "Select your Language",
            "hi" to "अपनी भाषा चुनें",
            "mr" to "आपली भाषा निवडा",
            "gu" to "તમારી ભાષા પસંદ કરો",
            "pa" to "ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ",
            "bn" to "আপনার ভাষা নির্বাচন করুন",
            "ta" to "உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்",
            "te" to "మీ భాషను ఎంచుకోండి",
            "kn" to "ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
            "ml" to "നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക",
            "or" to "ଆପଣଙ୍କର ଭାଷା ଚୟନ କରନ୍ତୁ",
            "od" to "ଆପଣଙ୍କର ଭାଷା ଚୟନ କରନ୍ତୁ",
            "as" to "আপোনাৰ ভাষা বাছনি কৰক",
            "ur" to "अपनी زبان منتخب کریں",
            "mai" to "अपन भाषा चुनू"
        )
    }

    // 14-language audio guidance prompt
    val audioInstructions = remember {
        mapOf(
            "en" to "Select the languages you're comfortable with",
            "hi" to "जिस भाषा में आप सहज हों, उसे चुनें",
            "mr" to "ज्या भाषेत तुम्हाला सोपे वाटते ती निवडा",
            "gu" to "તમે જેમાં સરળતા અનુભવો તે ભાષા પસંદ કરો",
            "pa" to "ਜਿਸ ਭਾਸ਼ਾ ਵਿੱਚ ਤੁਸੀਂ ਸਹਿਜ ਹੋ, ਉਸਨੂੰ ਚੁਣੋ",
            "bn" to "যে ভাষায় আপনি স্বাচ্ছন্দ্যবোধ করেন তা বেছে নিন",
            "ta" to "நீங்கள் விரும்பும் மொழியைத் தேர்ந்தெடுக்கவும்",
            "te" to "మీకు అనుకూలమైన భాషను ఎంచుకోండి",
            "kn" to "ನಿಮಗೆ ಅನುಕೂಲಕರವಾದ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
            "ml" to "നിങ്ങൾക്ക് സൗകര്യಪ್ರദമായ ഭാഷ തിരഞ്ഞെടുക്കുക",
            "or" to "ଆପଣ ଯେଉଁ ଭାଷାରେ ସହଜ, ତାହା ବାଛନ୍ତୁ",
            "od" to "ଆପଣ ଯେଉଁ ଭାଷାରେ ସହଜ, ତାହା ବାଛନ୍ତୁ",
            "as" to "আপুনি যিটো ভাষাত স্বাচ্ছন্দ্যবোধ কৰে বাছক",
            "ur" to "جس زبان میں آپ کو سہولت ہو، اسے منتخب کریں",
            "mai" to "जाहि भाषा मे अहाँ सहज होइ, से चुनू"
        )
    }

    // 14-language continue button labels
    val continueButtons = remember {
        mapOf(
            "en" to "Continue",
            "hi" to "आगे बढ़ें",
            "mr" to "पुढे जा",
            "gu" to "આગળ વધો",
            "pa" to "ਅੱਗੇ ਵਧੋ",
            "bn" to "এগিয়ে যান",
            "ta" to "தொடரவும்",
            "te" to "కొనసాగించండి",
            "kn" to "ಮುಂದುವರಿಯಿರಿ",
            "ml" to "തുടരുക",
            "or" to "ଆଗକୁ ବଢ଼ନ୍ତୁ",
            "od" to "ଆଗକୁ ବଢ଼ନ୍ତୁ",
            "as" to "আগবাঢ়ক",
            "ur" to "آگے بڑھیں",
            "mai" to "आगे बढ़ू"
        )
    }

    val savedLang = remember { AuthStore.getLanguage(context) ?: "en" }
    val savedDialect = remember { AuthStore.getDialect(context) }
    var selectedCode by remember { mutableStateOf(savedDialect ?: savedLang) }
    var isSaving by remember { mutableStateOf(false) }

    val isEnglish = selectedCode.equals("en", ignoreCase = true)
    val currentTitle = localizedTitles[selectedCode.lowercase()] ?: "अपनी भाषा चुनें"
    val currentAudioPrompt = audioInstructions[selectedCode.lowercase()] ?: "Select the languages you're comfortable with"
    val currentContinue = continueButtons[selectedCode.lowercase()] ?: "Continue"

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
    ) {
        // --- Continuous Grid Canvas (Cards scroll behind header and button) ---
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            modifier = Modifier
                .fillMaxSize()
                .haze(state = hazeState),
            contentPadding = PaddingValues(
                top = headerHeightDp + 12.dp,
                bottom = 104.dp,
                start = 20.dp,
                end = 20.dp
            ),
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(uiLanguages) { language ->
                LanguageGridCard(
                    language = language,
                    isSelected = selectedCode.equals(language.code, ignoreCase = true),
                    onClick = { selectedCode = language.code }
                )
            }
        }

        // --- Top Frosted Glass Header (iOS Style) ---
        Surface(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .fillMaxWidth()
                .onGloballyPositioned { coordinates ->
                    val measured = with(density) { coordinates.size.height.toDp() }
                    if (measured > 0.dp && measured != headerHeightDp) {
                        headerHeightDp = measured
                    }
                }
                .shadow(
                    elevation = 2.dp,
                    shape = RoundedCornerShape(bottomStart = 28.dp, bottomEnd = 28.dp),
                    spotColor = Color.Black.copy(alpha = 0.03f),
                    ambientColor = Color.Transparent
                )
                .hazeChild(
                    state = hazeState,
                    shape = RoundedCornerShape(bottomStart = 28.dp, bottomEnd = 28.dp),
                    style = HazeStyle(
                        tint = Color.White.copy(alpha = 0.45f),
                        blurRadius = 20.dp
                    )
                ),
            shape = RoundedCornerShape(bottomStart = 28.dp, bottomEnd = 28.dp),
            color = Color.Transparent,
            border = BorderStroke(1.dp, Color.White.copy(alpha = 0.60f)),
            tonalElevation = 0.dp
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .statusBarsPadding()
                    .padding(top = 16.dp, bottom = 18.dp, start = 20.dp, end = 20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    imageVector = Icons.Rounded.Language,
                    contentDescription = "Globe Icon",
                    tint = Color(0xFF2E7D32),
                    modifier = Modifier.size(40.dp)
                )

                Spacer(modifier = Modifier.height(10.dp))

                if (isEnglish) {
                    Text(
                        text = "Select your Language",
                        style = MaterialTheme.typography.headlineMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1B3B22),
                            fontSize = 24.sp
                        )
                    )
                    Spacer(modifier = Modifier.height(3.dp))
                    Text(
                        text = "Choose the language for the whole app",
                        style = MaterialTheme.typography.bodyMedium.copy(
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF5A6E5D),
                            fontSize = 14.sp
                        )
                    )
                } else {
                    // Bigger heading in the selected language
                    Text(
                        text = currentTitle,
                        style = MaterialTheme.typography.headlineMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1B3B22),
                            fontSize = 25.sp
                        )
                    )
                    Spacer(modifier = Modifier.height(3.dp))
                    // Smaller heading right under it in English
                    Text(
                        text = "Select your Language",
                        style = MaterialTheme.typography.bodyMedium.copy(
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF5A6E5D),
                            fontSize = 14.sp
                        )
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Rounded.VolumeUp,
                        contentDescription = "Audio Instructions",
                        tint = Color(0xFF4CAF50),
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = currentAudioPrompt,
                        style = MaterialTheme.typography.bodyMedium.copy(
                            color = Color(0xFF6B7B6B),
                            fontSize = 13.sp
                        )
                    )
                }
            }
        }

        // --- Bottom Floating Continue Button (Cards go behind it, no opaque canvas) ---
        Box(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .navigationBarsPadding()
                .padding(horizontal = 24.dp, vertical = 20.dp)
        ) {
            Button(
                onClick = {
                    val chosen = LanguageRegistry.findByCode(selectedCode) ?: LanguageRegistry.scheduledLanguages.first()
                    val primaryLang = if (chosen.isDialect) (chosen.parentLanguage ?: "hi") else chosen.code
                    val dialect = if (chosen.isDialect) chosen.code else null

                    isSaving = true
                    AuthStore.saveLanguageAndDialect(context, primaryLang, dialect)
                    LocaleHelper.applyLocale(context)
                    LocaleHelper.wrap(context, primaryLang)

                    coroutineScope.launch {
                        try {
                            val token = AuthStore.getAuthToken(context)
                            if (!token.isNullOrBlank()) {
                                userViewModel.updateLanguage(token, chosen.code) { _, _ -> }
                            }
                        } catch (_: Exception) {}
                        finally {
                            isSaving = false
                            if (navController.previousBackStackEntry != null) {
                                navController.popBackStack()
                            } else {
                                navController.navigate(NavRoutes.Dashboard) {
                                    popUpTo(navController.graph.id) {
                                        inclusive = true
                                    }
                                    launchSingleTop = true
                                }
                            }
                        }
                    }
                },
                enabled = !isSaving,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)),
                elevation = ButtonDefaults.buttonElevation(
                    defaultElevation = 6.dp,
                    pressedElevation = 2.dp
                ),
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                if (isSaving) {
                    CircularProgressIndicator(
                        color = Color.White,
                        modifier = Modifier.size(24.dp),
                        strokeWidth = 2.dp
                    )
                } else {
                    Row(
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = currentContinue,
                            fontWeight = FontWeight.Bold,
                            fontSize = 17.sp,
                            color = Color.White
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Icon(
                            imageVector = Icons.AutoMirrored.Rounded.ArrowForward,
                            contentDescription = "Continue",
                            tint = Color.White,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun LanguageGridCard(
    language: AppLanguageUi,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }

    // Fluid animations for selection state
    val targetScale = if (isSelected) 1.15f else 1.0f
    val animatedScale by animateFloatAsState(
        targetValue = targetScale,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessLow),
        label = "IllustrationScale"
    )

    val targetOpacity = if (isSelected) 0.8f else 0.5f
    val animatedOpacity by animateFloatAsState(
        targetValue = targetOpacity,
        animationSpec = tween(durationMillis = 300),
        label = "IllustrationOpacity"
    )

    val animatedBgColor by animateColorAsState(
        targetValue = if (isSelected) language.baseColor.copy(alpha = 0.20f) else language.baseColor.copy(alpha = 0.05f),
        animationSpec = tween(durationMillis = 300),
        label = "CardBackgroundColor"
    )

    val borderColor = if (isSelected) language.baseColor.copy(alpha = 0.8f) else Color.Transparent

    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1.05f) // Slightly reduced height
            .clickable(
                interactionSource = interactionSource,
                indication = null,
                onClick = onClick
            ),
        shape = RoundedCornerShape(20.dp),
        color = animatedBgColor,
        border = BorderStroke(1.5.dp, borderColor)
    ) {
        Box(modifier = Modifier.fillMaxSize()) {

            // Background Illustration (Restored to original size, touching bottom & right edges)
            Image(
                painter = painterResource(id = language.illustration),
                contentDescription = null,
                alignment = Alignment.BottomEnd,
                contentScale = ContentScale.Fit,
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .fillMaxWidth(0.65f)
                    .fillMaxHeight(0.75f)
                    .graphicsLayer {
                        transformOrigin = TransformOrigin(1f, 1f)
                        scaleX = animatedScale
                        scaleY = animatedScale
                        alpha = animatedOpacity
                    }
            )

            // Top Content Layout
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                // Language Names
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = language.nativeName,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1B1B1B)
                        )
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = language.englishName,
                        style = MaterialTheme.typography.labelMedium.copy(
                            fontWeight = FontWeight.Medium,
                            color = Color(0xFF757575)
                        )
                    )
                }

                // Color-Matched Radio Button Indicator
                Icon(
                    imageVector = if (isSelected) Icons.Rounded.CheckCircle else Icons.Rounded.RadioButtonUnchecked,
                    contentDescription = if (isSelected) "Selected" else "Unselected",
                    tint = if (isSelected) language.baseColor else Color(0xFF9E9E9E),
                    modifier = Modifier.size(24.dp)
                )
            }
        }
    }
}