package com.example.farmfusionapp.ui.screens

import android.app.Activity
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ExitToApp
import androidx.compose.material.icons.automirrored.rounded.KeyboardArrowRight
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.window.DialogWindowProvider
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.viewmodel.AuthViewModel
import com.example.farmfusionapp.utils.AppLocalizer
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.utils.LanguagePreferences
import com.example.farmfusionapp.utils.LocaleHelper
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.screens.WeatherSnapshotStore

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(navController: NavController) {
    val context = LocalContext.current
    val scrollState = rememberScrollState()
    val currentLang = LocalAppLanguage.current
    val savedDialect = AuthStore.getDialect(context)
    val activeCode = savedDialect ?: currentLang
    val langObj = remember(activeCode) { com.example.farmfusionapp.data.model.LanguageRegistry.findByCode(activeCode) }
    val langLabel = langObj?.let { "${it.nativeName} (${it.name})" } ?: "English"

    val authViewModel: AuthViewModel = remember { AuthViewModel() }
    val userInfo = remember { authViewModel.getCurrentUserInfo() }
    val rawUserName = userInfo.third
    val userName = if (!rawUserName.isNullOrBlank() && rawUserName != "Farmer") {
        rawUserName
    } else {
        AppLocalizer.localizeProfilePhrase("farmer", currentLang)
    }

    val fallbackCity = AppLocalizer.localizeProfilePhrase("location unavailable", currentLang)
    val rawCity = WeatherSnapshotStore.latestWeather?.city ?: com.example.farmfusionapp.utils.LocationSnapshotStore.latestCity
    val localizedCity = if (!rawCity.isNullOrBlank()) {
        AppLocalizer.localizeCity(rawCity, currentLang)
    } else {
        fallbackCity
    }

    // Theme Colors
    val darkGreen = Color(0xFF1E5631)
    val lightGreenBg = Color(0xFFF7FAF7)

    // Root Box to handle the background color and floating twig illustration
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(lightGreenBg)
    ) {
        // Top Right Twig Illustration
        Image(
            painter = painterResource(id = R.drawable.ill_profile_twig),
            contentDescription = null,
            contentScale = ContentScale.Fit,
            alpha = 0.85f,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .size(240.dp)
                .offset(x = 40.dp, y = (20).dp)
        )

        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                CenterAlignedTopAppBar(
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent,
                        titleContentColor = darkGreen
                    ),
                    title = {
                        Text(
                            text = AppLocalizer.localizeProfilePhrase("profile", currentLang),
                            style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)
                        )
                    },
                    navigationIcon = {
                        Surface(
                            onClick = { navController.popBackStack() },
                            shape = CircleShape,
                            color = Color.White,
                            shadowElevation = 2.dp,
                            modifier = Modifier
                                .padding(start = 16.dp)
                                .size(40.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Icon(
                                    Icons.AutoMirrored.Rounded.ArrowBack,
                                    contentDescription = "Back",
                                    tint = darkGreen,
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                        }
                    }
                )
            }
        ) { paddingValues ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(scrollState)
                    .padding(horizontal = 20.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {

                // Premium Profile Hero Card
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(220.dp)
                        .shadow(8.dp, RoundedCornerShape(24.dp), spotColor = Color.Black.copy(alpha = 0.05f)),
                    shape = RoundedCornerShape(24.dp),
                    color = Color.White
                ) {
                    Box(modifier = Modifier.fillMaxSize()) {

                        // Bottom Field Illustration
                        Image(
                            painter = painterResource(id = R.drawable.ill_profile_field),
                            contentDescription = null,
                            contentScale = ContentScale.FillWidth,
                            alignment = Alignment.BottomCenter,
                            alpha = 0.55f,
                            modifier = Modifier
                                .fillMaxWidth(1.45f)
                                .align(Alignment.BottomCenter)
                                .offset(y = 35.dp)
                        )

                        // Profile Content
                        Column(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(top = 28.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Top
                        ) {
                            Surface(
                                modifier = Modifier.size(80.dp),
                                shape = CircleShape,
                                color = darkGreen
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(
                                        Icons.Rounded.Person,
                                        contentDescription = null,
                                        modifier = Modifier.size(48.dp),
                                        tint = Color.White
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.height(12.dp))

                            Text(
                                text = userName,
                                style = MaterialTheme.typography.headlineSmall.copy(
                                    fontWeight = FontWeight.ExtraBold,
                                    color = darkGreen
                                )
                            )

                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    Icons.Rounded.LocationOn,
                                    contentDescription = null,
                                    modifier = Modifier.size(16.dp),
                                    tint = darkGreen
                                )
                                Spacer(modifier = Modifier.width(4.dp))
                                Text(
                                    text = localizedCity,
                                    style = MaterialTheme.typography.bodyMedium.copy(color = darkGreen)
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Section Title
                Column(modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = AppLocalizer.localizeProfilePhrase("farm section title", currentLang),
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = darkGreen
                        )
                    )
                    Text(
                        text = AppLocalizer.localizeProfilePhrase("farm section sub", currentLang),
                        style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray)
                    )
                }

                // Settings Rows
                SettingPremiumRow(
                    icon = Icons.Rounded.Translate,
                    title = AppLocalizer.localizeProfilePhrase("app language", currentLang),
                    subtitle = langLabel,
                    onClick = { navController.navigate(NavRoutes.LanguageSelection) }
                )
                SettingPremiumRow(
                    icon = Icons.Rounded.Notifications,
                    title = AppLocalizer.localizeProfilePhrase("notifications", currentLang),
                    subtitle = AppLocalizer.localizeProfilePhrase("notifications sub", currentLang),
                    onClick = { }
                )
                SettingPremiumRow(
                    icon = Icons.Rounded.Mic,
                    title = AppLocalizer.localizeProfilePhrase("voice assistant", currentLang),
                    subtitle = AppLocalizer.localizeProfilePhrase("voice assistant sub", currentLang),
                    onClick = { navController.navigate(NavRoutes.VoiceAssistant) }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Logout Button
                Button(
                    onClick = {
                        authViewModel.logout(context)
                        navController.navigate(NavRoutes.Login) {
                            popUpTo(navController.graph.id) { inclusive = true }
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Rounded.ExitToApp,
                        contentDescription = "Logout",
                        tint = Color.White
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = AppLocalizer.localizeProfilePhrase("logout", currentLang),
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    )
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
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        shadowElevation = 2.dp,
        border = BorderStroke(1.dp, Color(0xFFF0F5F0))
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Surface(
                    shape = CircleShape,
                    color = Color(0xFFE8F4EA),
                    modifier = Modifier.size(48.dp)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Icon(
                            icon,
                            contentDescription = null,
                            tint = Color(0xFF1E5631),
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.width(16.dp))
                Column {
                    Text(
                        title,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1B1B1B)
                        )
                    )
                    Text(
                        subtitle,
                        style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray)
                    )
                }
            }
            Icon(
                Icons.AutoMirrored.Rounded.KeyboardArrowRight,
                contentDescription = null,
                tint = Color.LightGray,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}
