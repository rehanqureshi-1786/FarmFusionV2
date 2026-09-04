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

    val savedLang = remember { AuthStore.getLanguage(context) ?: "en" }
    val savedDialect = remember { AuthStore.getDialect(context) }
    var selectedCode by remember { mutableStateOf(savedDialect ?: savedLang) }
    var isSaving by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFFAFAFA)) // Clean off-white background
            .statusBarsPadding()
            .padding(top = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // --- Header Section ---
        Icon(
            imageVector = Icons.Rounded.Language,
            contentDescription = "Globe Icon",
            tint = Color(0xFF2E7D32),
            modifier = Modifier.size(42.dp)
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Select your Language",
            style = MaterialTheme.typography.headlineMedium.copy(
                fontWeight = FontWeight.ExtraBold,
                color = Color(0xFF1B3B22)
            )
        )

        Spacer(modifier = Modifier.height(8.dp))

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.AutoMirrored.Rounded.VolumeUp,
                contentDescription = "Audio Instructions",
                tint = Color(0xFF4CAF50),
                modifier = Modifier.size(20.dp)
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = "Select the languages you're comfortable with",
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = Color(0xFF6B7B6B)
                )
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        // --- Grid Section ---
        LazyVerticalGrid(
            columns = GridCells.Fixed(2),
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            contentPadding = PaddingValues(horizontal = 20.dp, vertical = 8.dp),
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

        // --- Bottom Sticky Button ---
        Surface(
            modifier = Modifier.fillMaxWidth(),
            color = Color.Transparent,
            shadowElevation = 0.dp
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp, vertical = 24.dp)
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
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp)
                ) {
                    if (isSaving) {
                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp), strokeWidth = 2.dp)
                    } else {
                        Row(
                            horizontalArrangement = Arrangement.Center,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Continue", fontWeight = FontWeight.Bold, fontSize = 16.sp, color = Color.White)
                            Spacer(modifier = Modifier.width(8.dp))
                            Icon(Icons.AutoMirrored.Rounded.ArrowForward, contentDescription = "Continue", tint = Color.White)
                        }
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