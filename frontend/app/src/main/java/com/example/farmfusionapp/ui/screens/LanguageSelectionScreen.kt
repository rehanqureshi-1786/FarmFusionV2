package com.example.farmfusionapp.ui.screens

import android.app.Activity
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Agriculture
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Language
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.components.PremiumButton
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.viewmodel.UserViewModel

data class Language(
    val name: String,
    val localName: String,
    val greeting: String,
    val code: String,
    val color: Color
)

@Composable
fun LanguageSelectionScreen(
    navController: NavController,
    userViewModel: UserViewModel = viewModel()
) {
    val context = LocalContext.current
    val englishLabel = stringResource(R.string.lang_local_english)
    val hindiLabel = stringResource(R.string.lang_local_hindi)

    val languages = remember(englishLabel, hindiLabel) {
        listOf(
            Language(englishLabel, "English", "Hello", "en", Color(0xFFE3F2FD)),
            Language(hindiLabel, "हिन्दी", "नमस्ते", "hi", Color(0xFFFFF3E0)),
            Language("Hinglish", "Hinglish", "Kya haal hai", "hi-en", Color(0xFFF3E5F5)),
            Language("Marathi", "मराठी", "नमस्कार", "mr", Color(0xFFE8F5E9)),
            Language("Punjabi", "ਪੰਜਾਬੀ", "Sat Sri Akal", "pa", Color(0xFFFBE9E7)),
            Language("Telugu", "తెలుగు", "నమస్కారం", "te", Color(0xFFE0F2F1))
        )
    }

    var selectedLanguageCode by remember { 
        mutableStateOf(AuthStore.getLanguage(context) ?: "en") 
    }
    var isSaving by remember { mutableStateOf(false) }

    NeoScaffoldBackground {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            Spacer(modifier = Modifier.height(40.dp))

            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.fillMaxWidth()
            ) {
                Surface(
                    modifier = Modifier.size(80.dp).shadow(12.dp, CircleShape),
                    shape = CircleShape,
                    color = Color.White
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(
                                brush = Brush.linearGradient(
                                    listOf(Color(0xFF2C7B46), Color(0xFF7BB45A))
                                )
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Rounded.Agriculture,
                            contentDescription = null,
                            modifier = Modifier.size(44.dp),
                            tint = Color.White
                        )
                    }
                }

                Spacer(modifier = Modifier.height(20.dp))

                Text(
                    text = stringResource(R.string.choose_app_language),
                    style = MaterialTheme.typography.headlineSmall.copy(
                        fontWeight = FontWeight.ExtraBold,
                        color = Color(0xFF1B1B1B)
                    ),
                    textAlign = TextAlign.Center
                )
                Text(
                    text = stringResource(R.string.select_lang_desc),
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = Color.Gray
                    ),
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 12.dp)
                )
            }

            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                horizontalArrangement = Arrangement.spacedBy(14.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
                modifier = Modifier.weight(1f),
                contentPadding = PaddingValues(bottom = 16.dp)
            ) {
                items(languages) { language ->
                    val isSelected = selectedLanguageCode == language.code
                    Surface(
                        onClick = { selectedLanguageCode = language.code },
                        shape = RoundedCornerShape(24.dp),
                        color = if (isSelected) Color.White else Color.White.copy(alpha = 0.6f),
                        modifier = Modifier
                            .fillMaxWidth()
                            .shadow(if (isSelected) 8.dp else 2.dp, RoundedCornerShape(24.dp)),
                        border = BorderStroke(
                            width = if (isSelected) 2.dp else 1.dp,
                            color = if (isSelected) MaterialTheme.colorScheme.primary else Color(0xFFEEEEEE)
                        )
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(
                                    Brush.verticalGradient(
                                        listOf(
                                            if (isSelected) language.color.copy(alpha = 0.4f) else Color.Transparent,
                                            Color.White
                                        )
                                    )
                                )
                                .padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(36.dp)
                                        .background(
                                            if (isSelected) MaterialTheme.colorScheme.primary.copy(alpha = 0.1f) 
                                            else Color(0xFFF5F5F5), 
                                            CircleShape
                                        ),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = if (isSelected) Icons.Rounded.Check else Icons.Rounded.Language,
                                        contentDescription = null,
                                        modifier = Modifier.size(18.dp),
                                        tint = if (isSelected) MaterialTheme.colorScheme.primary else Color.Gray
                                    )
                                }
                            }
                            
                            Column {
                                Text(
                                    text = language.localName,
                                    style = MaterialTheme.typography.titleMedium.copy(
                                        fontWeight = FontWeight.ExtraBold,
                                        color = if (isSelected) MaterialTheme.colorScheme.primary else Color(0xFF1B1B1B)
                                    )
                                )
                                Text(
                                    text = language.name,
                                    style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray)
                                )
                            }
                        }
                    }
                }
            }

            PremiumButton(
                text = "SAVE CHANGES / सुरक्षित करें",
                onClick = {
                    isSaving = true
                    AuthStore.saveLanguage(context, selectedLanguageCode)
                    
                    val token = AuthStore.getAuthToken(context)
                    if (token != null) {
                        userViewModel.updateLanguage(token, selectedLanguageCode) { _, _ ->
                            isSaving = false
                            // Recreate to apply locale, NavHost will then start at Splash
                            (context as? Activity)?.recreate()
                        }
                    } else {
                        isSaving = false
                        // If not logged in, just go to Splash -> Login
                        (context as? Activity)?.recreate()
                    }
                },
                isLoading = isSaving,
                modifier = Modifier.fillMaxWidth().height(56.dp)
            )
            
            Spacer(modifier = Modifier.height(10.dp))
        }
    }
}
