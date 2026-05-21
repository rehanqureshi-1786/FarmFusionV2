package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.rounded.*
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.viewmodel.AuthViewModel
import com.example.farmfusionapp.utils.AffiliatePreferences
import com.example.farmfusionapp.utils.LanguagePreferences
import com.example.farmfusionapp.utils.LocaleHelper
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.components.NeoSectionTitle
import com.example.farmfusionapp.ui.components.PremiumTextField
import com.example.farmfusionapp.ui.screens.WeatherSnapshotStore

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(navController: NavController) {
    val context = LocalContext.current
    val scrollState = rememberScrollState()
    val langCode = LanguagePreferences.getSelectedLanguage(context) ?: "en"
    val langLabel = when (LocaleHelper.resourceLocaleTag(langCode)) {
        "hi" -> stringResource(R.string.profile_lang_display_hi)
        "mr" -> stringResource(R.string.profile_lang_display_mr)
        "gu" -> stringResource(R.string.profile_lang_display_gu)
        "pa" -> stringResource(R.string.profile_lang_display_pa)
        "te" -> stringResource(R.string.profile_lang_display_te)
        else -> stringResource(R.string.profile_lang_display_en)
    }

    val authViewModel: AuthViewModel = remember { AuthViewModel() }
    val userInfo = remember { authViewModel.getCurrentUserInfo() }
    val userName = userInfo.third ?: "Farmer"

    Column(modifier = Modifier.fillMaxSize()) {
        CenterAlignedTopAppBar(
            title = { Text(stringResource(R.string.profile_title), style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)) },
            navigationIcon = {
                IconButton(onClick = { navController.popBackStack() }) {
                    Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                }
            }
        )
        NeoScaffoldBackground(
            modifier = Modifier.fillMaxSize()
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(scrollState)
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(18.dp)
            ) {
                // Premium Profile Hero
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                        .shadow(12.dp, RoundedCornerShape(32.dp)),
                    shape = RoundedCornerShape(32.dp),
                    color = Color.White
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(
                                Brush.linearGradient(
                                    colors = listOf(Color(0xFF4FC3F7), Color(0xFF29B6F6), Color(0xFF039BE5))
                                )
                            )
                    ) {
                        // Background Decorative Circles
                        Box(
                            modifier = Modifier
                                .size(140.dp)
                                .align(Alignment.TopEnd)
                                .offset(x = 20.dp, y = (-20).dp)
                                .background(Color.White.copy(alpha = 0.1f), CircleShape)
                        )

                        Column(
                            modifier = Modifier.fillMaxSize().padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center
                        ) {
                            Surface(
                                modifier = Modifier.size(80.dp),
                                shape = CircleShape,
                                color = Color.White,
                                shadowElevation = 4.dp
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(
                                        Icons.Rounded.Person, 
                                        contentDescription = null, 
                                        modifier = Modifier.size(48.dp),
                                        tint = Color(0xFF0288D1)
                                    )
                                }
                            }
                            Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            text = userName, 
                            style = MaterialTheme.typography.headlineSmall.copy(
                                fontWeight = FontWeight.ExtraBold,
                                color = Color.White
                            )
                        )
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Rounded.LocationOn, 
                                contentDescription = null, 
                                modifier = Modifier.size(16.dp), 
                                tint = Color.White.copy(alpha = 0.8f)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            val displayCity = WeatherSnapshotStore.latestWeather?.city ?: "Nagpur, Maharashtra"
                            Text(
                                text = displayCity, 
                                style = MaterialTheme.typography.bodyMedium.copy(color = Color.White.copy(alpha = 0.9f))
                            )
                        }
                        }
                    }
                }

                NeoSectionTitle(
                    stringResource(R.string.profile_farm_section_title),
                    stringResource(R.string.profile_farm_section_sub)
                )

                SettingPremiumRow(
                    icon = Icons.Rounded.Language,
                    title = stringResource(R.string.profile_language),
                    subtitle = langLabel,
                    onClick = { navController.navigate(NavRoutes.LanguageSelection) }
                )
                SettingPremiumRow(
                    icon = Icons.Rounded.Notifications,
                    title = stringResource(R.string.profile_notifications),
                    subtitle = stringResource(R.string.profile_notifications_sub),
                    onClick = { }
                )
                SettingPremiumRow(
                    icon = Icons.Rounded.Mic,
                    title = stringResource(R.string.profile_voice),
                    subtitle = stringResource(R.string.profile_voice_sub),
                    onClick = { }
                )

                Spacer(modifier = Modifier.height(24.dp))

                Button(
                    onClick = {
                        authViewModel.logout(context)
                        navController.navigate(NavRoutes.Login) {
                            popUpTo(0) { inclusive = true }
                        }
                    },
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Icon(Icons.Rounded.ExitToApp, contentDescription = null)
                    Spacer(modifier = Modifier.width(12.dp))
                    Text("Logout", fontWeight = FontWeight.Bold)
                }

                Spacer(modifier = Modifier.height(40.dp))
            }
        }
    }
}

@Composable
fun SettingPremiumRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    subtitle: String,
    onClick: () -> Unit = {}
) {
    Surface(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White,
        shadowElevation = 2.dp,
        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
    ) {
        Row(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(44.dp)
                        .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), RoundedCornerShape(12.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(24.dp))
                }
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(title, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold, color = Color(0xFF1B1B1B)))
                    Text(subtitle, style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray))
                }
            }
            Icon(Icons.AutoMirrored.Rounded.ArrowForward, contentDescription = null, tint = Color.LightGray, modifier = Modifier.size(20.dp))
        }
    }
}
