package com.example.farmfusionapp.ui.components

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Language
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.window.DialogWindowProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.farmfusionapp.data.model.LanguageRegistry
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.utils.LocaleHelper
import com.example.farmfusionapp.viewmodel.UserViewModel
import kotlinx.coroutines.launch

data class LanguageItemUi(
    val code: String,
    val nativeName: String,
    val englishName: String,
    val initial: String,
    val avatarBg: Color,
    val avatarFg: Color
)

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun ProfileLanguageDialog(
    onDismiss: () -> Unit,
    userViewModel: UserViewModel = viewModel()
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val view = LocalView.current

    // Remove window dim so the 16.dp screen blur provides the true frosted glass backdrop
    LaunchedEffect(view) {
        val window = (view.parent as? DialogWindowProvider)?.window
        window?.let {
            it.clearFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND)
            it.setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        }
    }

    // 14 Pure Languages with their distinctive script initials and pastel color themes
    val languageList = remember {
        listOf(
            LanguageItemUi("hi", "हिंदी", "Hindi", "अ", Color(0xFFD1FAE5), Color(0xFF047857)),
            LanguageItemUi("en", "English", "English", "A", Color(0xFFE0F2FE), Color(0xFF0284C7)),
            LanguageItemUi("gu", "ગુજરાતી", "Gujarati", "અ", Color(0xFFFFEDD5), Color(0xFFC2410C)),
            LanguageItemUi("mr", "मराठी", "Marathi", "अ", Color(0xFFF3E8FF), Color(0xFF7E22CE)),
            LanguageItemUi("pa", "ਪੰਜਾਬੀ", "Punjabi", "ਅ", Color(0xFFFEF3C7), Color(0xFFB45309)),
            LanguageItemUi("bn", "বাংলা", "Bengali", "অ", Color(0xFFFFE4E6), Color(0xFFBE123C)),
            LanguageItemUi("ta", "தமிழ்", "Tamil", "அ", Color(0xFFFFEDD5), Color(0xFFEA580C)),
            LanguageItemUi("te", "తెలుగు", "Telugu", "అ", Color(0xFFE0F2FE), Color(0xFF0369A1)),
            LanguageItemUi("kn", "ಕನ್ನಡ", "Kannada", "ಅ", Color(0xFFFEF9C3), Color(0xFFA16207)),
            LanguageItemUi("ml", "മലയാളം", "Malayalam", "അ", Color(0xFFF3E8FF), Color(0xFF6D28D9)),
            LanguageItemUi("or", "ଓଡ଼ିଆ", "Odia", "ଅ", Color(0xFFFFEDD5), Color(0xFFD97706)),
            LanguageItemUi("as", "অসমীয়া", "Assamese", "অ", Color(0xFFE0F2FE), Color(0xFF2563EB)),
            LanguageItemUi("ur", "اردو", "Urdu", "ا", Color(0xFFDCFCE7), Color(0xFF15803D)),
            LanguageItemUi("mai", "मैथिली", "Maithili", "अ", Color(0xFFFFE4E6), Color(0xFFE11D48))
        )
    }

    val savedLang = remember { AuthStore.getLanguage(context) ?: "en" }
    val savedDialect = remember { AuthStore.getDialect(context) }
    var selectedCode by remember { mutableStateOf(savedDialect ?: savedLang) }
    var isSaving by remember { mutableStateOf(false) }

    // Localized Headers and Button text matching the selected language
    val headerTitle = when (selectedCode.lowercase()) {
        "en" -> "Choose App Language"
        "mr" -> "ॲपची भाषा निवडा"
        "gu" -> "એપની ભાષા પસંદ કરો"
        "pa" -> "ਐਪ ਦੀ ਭਾਸ਼ਾ ਚੁਣੋ"
        "bn" -> "অ্যাপের ভাষা নির্বাচন করুন"
        "ta" -> "பயன்பாட்டு மொழியைத் தேர்வுசெய்க"
        "te" -> "యాప్ భాషను ఎంచుకోండి"
        "kn" -> "ಆ್ಯಪ್ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ"
        "ml" -> "ആപ്പ് ഭാഷ തിരഞ്ഞെടുക്കുക"
        "or" -> "ଆପ୍ ଭାଷା ବାଛନ୍ତୁ"
        "as" -> "এপৰ ভাষা বাছক"
        "ur" -> "ایپ کی زبان منتخب کریں"
        "mai" -> "ऐप केर भाषा चुनू"
        else -> "ऐप की भाषा चुनें"
    }

    val headerSub = when (selectedCode.lowercase()) {
        "en" -> "You can change your preferred language anytime"
        "mr" -> "तुम्ही तुमची आवडती भाषा कधीही बदलू शकता"
        "gu" -> "તમે તમારી પસંદગીની ભાષા ગમે ત્યારે બદલી શકો છો"
        "pa" -> "ਤੁਸੀਂ ਕਿਸੇ ਵੀ ਸਮੇਂ ਆਪਣੀ ਪਸੰਦੀਦਾ ਭਾਸ਼ਾ ਬਦਲ ਸਕਦੇ ਹੋ"
        "bn" -> "আপনি যেকোনো সময় আপনার পছন্দের ভাষা পরিবর্তন করতে পারেন"
        "ta" -> "உங்கள் விருப்ப மொழியை எப்போது வேண்டுமானாலும் மாற்றலாம்"
        "te" -> "మీరు ఎప్పుడైనా మీకు నచ్చిన భాషను మార్చుకోవచ్చు"
        "kn" -> "ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ನೀವು ಯಾವಾಗ ಬೇಕಾದರೂ ಬದಲಾಯಿಸಬಹುದು"
        "ml" -> "നിങ്ങൾക്ക് എപ്പോൾ വേണമെങ്കിലും ഇഷ്ടമുള്ള ഭാഷ മാറ്റാം"
        "or" -> "ଆପଣ ଯେକୌଣସି ସମୟରେ ପସନ୍ଦର ଭାଷା ବଦଳାଇ ପାରିବେ"
        "as" -> "আপুনি যিকোনো সময়তে আপোনাৰ পছন্দৰ ভাষা সলনি কৰিব পাৰিব"
        "ur" -> "آپ کسی بھی وقت اپنی پسندیدہ زبان تبدیل کر سکتے ہیں"
        "mai" -> "अहाँ अपन मनपसंद भाषा कहियो बदलि सकैत छी"
        else -> "आप अपनी पसंदीदा भाषा कभी भी बदल सकते हैं"
    }

    val buttonLabel = when (selectedCode.lowercase()) {
        "en" -> "Set Language"
        "mr" -> "भाषा सेट करा"
        "gu" -> "ભાષા સેટ કરો"
        "pa" -> "ਭਾਸ਼ਾ ਸੈੱਟ ਕਰੋ"
        "bn" -> "ভাষা সেট করুন"
        "ta" -> "மொழியை அமைக்கவும்"
        "te" -> "భాషను సెట్ చేయండి"
        "kn" -> "ಭಾಷೆಯನ್ನು ಹೊಂದಿಸಿ"
        "ml" -> "ഭാഷ സജ്ജമാക്കുക"
        "or" -> "ଭାଷା ସେଟ୍ କରନ୍ତୁ"
        "as" -> "ভাষা নিৰ্ধাৰণ কৰক"
        "ur" -> "زبان منتخب کریں"
        "mai" -> "भाषा सेट करू"
        else -> "भाषा सेट करें"
    }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            decorFitsSystemWindows = false
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .clickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    onClick = onDismiss
                ),
            contentAlignment = Alignment.Center
        ) {
            // Semi-transparent frosted glass popup container
            Surface(
                modifier = Modifier
                    .fillMaxWidth(0.90f)
                    .clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null,
                        onClick = {} // Consume click inside dialog
                    ),
                shape = RoundedCornerShape(30.dp),
                color = Color(0xF2F4F7F4), // Slightly transparent frosted glass tint
                border = BorderStroke(1.dp, Color.White.copy(alpha = 0.7f)),
                shadowElevation = 16.dp
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp, vertical = 16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Top Drag Pill Handle
                    Box(
                        modifier = Modifier
                            .width(42.dp)
                            .height(4.dp)
                            .background(Color(0xFFB0B0B0), RoundedCornerShape(2.dp))
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    // Header Row with Close Button
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                            modifier = Modifier.weight(1f)
                        ) {
                            // Globe icon in light green circle
                            Surface(
                                shape = CircleShape,
                                color = Color(0xFFD1FAE5),
                                modifier = Modifier.size(46.dp)
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(
                                        imageVector = Icons.Rounded.Language,
                                        contentDescription = "Language",
                                        tint = Color(0xFF047857),
                                        modifier = Modifier.size(24.dp)
                                    )
                                }
                            }

                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = headerTitle,
                                    style = MaterialTheme.typography.titleMedium.copy(
                                        fontWeight = FontWeight.ExtraBold,
                                        fontSize = 17.sp,
                                        color = Color(0xFF1B1B1B)
                                    )
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = headerSub,
                                    style = MaterialTheme.typography.bodySmall.copy(
                                        fontSize = 11.sp,
                                        color = Color(0xFF555555),
                                        lineHeight = 14.sp
                                    )
                                )
                            }
                        }

                        // Circular Close Button (top right)
                        Surface(
                            onClick = onDismiss,
                            shape = CircleShape,
                            color = Color.White,
                            shadowElevation = 2.dp,
                            modifier = Modifier.size(34.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    imageVector = Icons.Rounded.Close,
                                    contentDescription = "Close",
                                    tint = Color(0xFF374151),
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Scrollable List showing exactly 5 language cards at once (~336.dp)
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(336.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                        contentPadding = PaddingValues(vertical = 2.dp)
                    ) {
                        items(languageList, key = { it.code }) { item ->
                            val isSelected = selectedCode.equals(item.code, ignoreCase = true)

                            // White Solid Language Card
                            Surface(
                                onClick = { selectedCode = item.code },
                                shape = RoundedCornerShape(18.dp),
                                color = Color.White,
                                border = if (isSelected) BorderStroke(1.5.dp, Color(0xFF1B5E20).copy(alpha = 0.8f)) else BorderStroke(0.5.dp, Color(0xFFE5E7EB)),
                                shadowElevation = if (isSelected) 3.dp else 1.dp,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(60.dp)
                            ) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxSize()
                                        .padding(horizontal = 14.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(14.dp)
                                    ) {
                                        // Colorful initial circle avatar
                                        Surface(
                                            shape = CircleShape,
                                            color = item.avatarBg,
                                            modifier = Modifier.size(38.dp)
                                        ) {
                                            Box(contentAlignment = Alignment.Center) {
                                                Text(
                                                    text = item.initial,
                                                    style = MaterialTheme.typography.titleMedium.copy(
                                                        fontWeight = FontWeight.ExtraBold,
                                                        color = item.avatarFg,
                                                        fontSize = 17.sp
                                                    )
                                                )
                                            }
                                        }

                                        Column {
                                            Text(
                                                text = item.nativeName,
                                                style = MaterialTheme.typography.bodyLarge.copy(
                                                    fontWeight = FontWeight.Bold,
                                                    fontSize = 15.sp,
                                                    color = Color(0xFF1F2937)
                                                )
                                            )
                                            Text(
                                                text = "(${item.englishName})",
                                                style = MaterialTheme.typography.bodySmall.copy(
                                                    fontSize = 12.sp,
                                                    color = Color(0xFF6B7280)
                                                )
                                            )
                                        }
                                    }

                                    // Radio button indicator
                                    if (isSelected) {
                                        Box(
                                            modifier = Modifier
                                                .size(22.dp)
                                                .border(2.dp, Color(0xFF1B5E20), CircleShape),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Box(
                                                modifier = Modifier
                                                    .size(10.dp)
                                                    .background(Color(0xFF1B5E20), CircleShape)
                                            )
                                        }
                                    } else {
                                        Box(
                                            modifier = Modifier
                                                .size(22.dp)
                                                .border(1.5.dp, Color(0xFF9CA3AF), CircleShape)
                                        )
                                    }
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Big Solid Green Set Language Button
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
                                    onDismiss()
                                }
                            }
                        },
                        enabled = !isSaving,
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1B5E20)),
                        shape = RoundedCornerShape(16.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(52.dp),
                        elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp, pressedElevation = 1.dp)
                    ) {
                        if (isSaving) {
                            CircularProgressIndicator(
                                color = Color.White,
                                modifier = Modifier.size(22.dp),
                                strokeWidth = 2.dp
                            )
                        } else {
                            Text(
                                text = buttonLabel,
                                style = MaterialTheme.typography.titleMedium.copy(
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 16.sp,
                                    color = Color.White
                                )
                            )
                        }
                    }
                }
            }
        }
    }
}
