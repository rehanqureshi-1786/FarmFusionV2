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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ArrowForward
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.Language
import androidx.compose.material.icons.rounded.RadioButtonUnchecked
import androidx.compose.material.icons.rounded.VolumeUp
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
import com.example.farmfusionapp.ui.components.PremiumButton
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.viewmodel.UserViewModel

data class AppLanguage(
    val code: String,
    val nativeName: String,
    val englishName: String,
    val illustration: Int,
    val baseColor: Color
)

@Composable
fun LanguageSelectionScreen(
    navController: NavController,
    userViewModel: UserViewModel = viewModel()
) {
    val context = LocalContext.current

    val languages = remember {
        listOf(
            AppLanguage("hi", "हिंदी", "Hindi", R.drawable.ill_lang_hi, Color(0xFF81C784)),
            AppLanguage("en", "English", "English", R.drawable.ill_lang_en, Color(0xFF4CAF50)),
            AppLanguage("ta", "தமிழ்", "Tamil", R.drawable.ill_lang_ta, Color(0xFFFFB74D)),
            AppLanguage("te", "తెలుగు", "Telugu", R.drawable.ill_lang_te, Color(0xFF64B5F6)),
            AppLanguage("gu", "ગુજરાતી", "Gujarati", R.drawable.ill_lang_gu, Color(0xFF4FC3F7)),
            AppLanguage("bn", "বাংলা", "Bangla", R.drawable.ill_lang_bn, Color(0xFFF06292)),
            AppLanguage("mr", "मराठी", "Marathi", R.drawable.ill_lang_mr, Color(0xFFAED581)),
            AppLanguage("kn", "ಕನ್ನಡ", "Kannada", R.drawable.ill_lang_kn, Color(0xFFFFD54F))
        )
    }

    val currentCode = remember { AuthStore.getLanguage(context) ?: "en" }
    var selectedLanguage by remember {
        mutableStateOf(languages.find { it.code == currentCode } ?: languages[1])
    }

    var isSaving by remember { mutableStateOf(false) }

    val navigateForward = {
        isSaving = false
        navController.navigate(NavRoutes.Splash) {
            popUpTo(NavRoutes.LanguageSelection) { inclusive = true }
        }
        (context as? Activity)?.recreate()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFFAFAFA))
            .statusBarsPadding()
            .padding(top = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // --- Header Section ---
        Icon(
            imageVector = Icons.Rounded.Language,
            contentDescription = "Globe Icon",
            tint = Color(0xFF2E7D32),
            modifier = Modifier.size(36.dp)
        )

        Spacer(modifier = Modifier.height(12.dp))

        Text(
            text = "Choose Your Language",
            style = MaterialTheme.typography.headlineMedium.copy(
                fontWeight = FontWeight.ExtraBold,
                color = Color(0xFF1B3B22),
                fontSize = 24.sp
            )
        )

        Spacer(modifier = Modifier.height(6.dp))

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Rounded.VolumeUp,
                contentDescription = "Audio Instructions",
                tint = Color(0xFF4CAF50),
                modifier = Modifier.size(18.dp)
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                text = "Select the languages you're comfortable with",
                style = MaterialTheme.typography.bodyMedium.copy(
                    color = Color(0xFF6B7B6B),
                    fontSize = 13.sp
                )
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        // --- Fluid Weighted Grid Section ---
        Column(
            modifier = Modifier
                .weight(1f) // Consumes all middle space perfectly
                .fillMaxWidth()
                .padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            val chunkedLanguages = languages.chunked(2)
            chunkedLanguages.forEach { rowLanguages ->
                Row(
                    modifier = Modifier
                        .weight(1f) // Divides vertical space equally across all 4 rows
                        .fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    rowLanguages.forEach { language ->
                        LanguageGridCard(
                            modifier = Modifier.weight(1f), // Halves the width perfectly
                            language = language,
                            isSelected = selectedLanguage == language,
                            onClick = { selectedLanguage = language }
                        )
                    }
                }
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
                    .padding(horizontal = 24.dp, vertical = 24.dp) // Restored nice padding
            ) {
                PremiumButton(
                    text = "Continue",
                    icon = Icons.Rounded.ArrowForward,
                    isLoading = isSaving,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF2E7D32),
                        contentColor = Color.White
                    ),
                    onClick = {
                        isSaving = true
                        AuthStore.saveLanguage(context, selectedLanguage.code)

                        val token = AuthStore.getAuthToken(context)
                        if (token != null) {
                            userViewModel.updateLanguage(token, selectedLanguage.code) { _, _ ->
                                navigateForward()
                            }
                        } else {
                            navigateForward()
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun LanguageGridCard(
    modifier: Modifier = Modifier,
    language: AppLanguage,
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
        targetValue = if (isSelected) language.baseColor.copy(alpha = 0.25f) else language.baseColor.copy(alpha = 0.08f),
        animationSpec = tween(durationMillis = 300),
        label = "CardBackgroundColor"
    )

    val borderColor = if (isSelected) language.baseColor.copy(alpha = 0.6f) else Color.Transparent

    Surface(
        modifier = modifier
            .fillMaxSize() // Removed aspectRatio so it organically fills the given flex weight
            .clickable(
                interactionSource = interactionSource,
                indication = null,
                onClick = onClick
            ),
        shape = RoundedCornerShape(20.dp),
        color = animatedBgColor,
        border = BorderStroke(1.dp, borderColor)
    ) {
        Box(modifier = Modifier.fillMaxSize()) {

            // Background Illustration (Right Aligned, Scaled down initially)
            Image(
                painter = painterResource(id = language.illustration),
                contentDescription = null,
                contentScale = ContentScale.Fit,
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .fillMaxWidth(0.6f)
                    .fillMaxHeight(0.7f)
                    .padding(end = 8.dp, bottom = 4.dp)
                    .graphicsLayer {
                        // Transforms scale originating from the bottom right so it doesn't clip out of the card
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
                    .padding(12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                // Language Names
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = language.nativeName,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1B1B1B),
                            fontSize = 15.sp
                        )
                    )
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = language.englishName,
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Medium,
                            color = Color(0xFF757575)
                        )
                    )
                }

                // Radio Button Indicator
                Icon(
                    imageVector = if (isSelected) Icons.Rounded.CheckCircle else Icons.Rounded.RadioButtonUnchecked,
                    contentDescription = if (isSelected) "Selected" else "Unselected",
                    tint = if (isSelected) Color(0xFF2E7D32) else Color(0xFF9E9E9E),
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}