package com.example.farmfusionapp.ui.screens

import androidx.activity.compose.BackHandler
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ExitToApp
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.components.ProfileLanguageDialog
import com.example.farmfusionapp.utils.AppLocalizer
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.viewmodel.AuthViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BuyerProfileScreen(navController: NavController) {
    val context = LocalContext.current
    val scrollState = rememberScrollState()
    val currentLang = LocalAppLanguage.current
    var showLanguageDialog by remember { mutableStateOf(false) }
    val globalBlur = LocalGlobalBlur.current

    LaunchedEffect(showLanguageDialog) {
        globalBlur.value = showLanguageDialog
    }
    DisposableEffect(Unit) {
        onDispose {
            globalBlur.value = false
        }
    }

    val savedDialect = AuthStore.getDialect(context)
    val activeCode = savedDialect ?: currentLang
    val langObj = remember(activeCode) { com.example.farmfusionapp.data.model.LanguageRegistry.findByCode(activeCode) }
    val langLabel = langObj?.let { "${it.nativeName} (${it.name})" } ?: "English"

    val authViewModel: AuthViewModel = remember { AuthViewModel() }
    val userInfo = remember { authViewModel.getCurrentUserInfo() }
    val rawUserName = userInfo.third
    val savedPhone = remember { AuthStore.getUserPhone(context) }
    val userName = if (!rawUserName.isNullOrBlank() && !rawUserName.equals("Farmer", ignoreCase = true) && !rawUserName.equals("Buyer", ignoreCase = true)) {
        rawUserName
    } else if (!savedPhone.isNullOrBlank()) {
        "+91 ${savedPhone.takeLast(10)}"
    } else {
        "Buyer"
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

    val onNavigateBackToHome = {
        if (!navController.popBackStack(NavRoutes.BuyerDashboard, inclusive = false)) {
            navController.navigate(NavRoutes.BuyerDashboard) {
                popUpTo(NavRoutes.BuyerDashboard) { inclusive = false }
                launchSingleTop = true
            }
        }
    }

    BackHandler {
        onNavigateBackToHome()
    }

    // Root Box with background color and floating twig illustration
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(lightGreenBg)
    ) {
        // Wind Sway Animation for Top-Right Leaf Illustration
        val leafInfiniteTransition = rememberInfiniteTransition(label = "BuyerLeafWindSway")
        val leafSwayAngle by leafInfiniteTransition.animateFloat(
            initialValue = 0.5f,
            targetValue = -9.0f,
            animationSpec = infiniteRepeatable(
                animation = tween(durationMillis = 1350, easing = FastOutSlowInEasing),
                repeatMode = RepeatMode.Reverse
            ),
            label = "buyerLeafSwayAngle"
        )

        // Top Right Leaf Illustration
        Image(
            painter = painterResource(id = R.drawable.ill_profile_twig),
            contentDescription = null,
            contentScale = ContentScale.Fit,
            alpha = 0.85f,
            modifier = Modifier
                .align(Alignment.TopEnd)
                .size(240.dp)
                .offset(x = 40.dp, y = 20.dp)
                .graphicsLayer {
                    transformOrigin = TransformOrigin(0.85f, 0.20f)
                    rotationZ = leafSwayAngle
                }
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
                            onClick = { onNavigateBackToHome() },
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

                // Premium Buyer Profile Hero Card
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(230.dp)
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
                                .padding(top = 22.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Top
                        ) {
                            Surface(
                                modifier = Modifier.size(76.dp),
                                shape = CircleShape,
                                color = darkGreen
                            ) {
                                Box(contentAlignment = Alignment.Center) {
                                    Icon(
                                        Icons.Rounded.Person,
                                        contentDescription = null,
                                        modifier = Modifier.size(46.dp),
                                        tint = Color.White
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.height(10.dp))

                            Text(
                                text = userName,
                                style = MaterialTheme.typography.headlineSmall.copy(
                                    fontWeight = FontWeight.ExtraBold,
                                    color = darkGreen
                                )
                            )

                            Spacer(modifier = Modifier.height(4.dp))

                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.Center
                            ) {
                                Surface(
                                    shape = RoundedCornerShape(12.dp),
                                    color = Color(0xFFE8F5E9),
                                    border = BorderStroke(1.dp, Color(0xFFC8E6C9))
                                ) {
                                    Text(
                                        text = "Verified Buyer",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = darkGreen,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                                    )
                                }

                                Spacer(modifier = Modifier.width(8.dp))

                                Icon(
                                    Icons.Rounded.LocationOn,
                                    contentDescription = null,
                                    modifier = Modifier.size(15.dp),
                                    tint = darkGreen
                                )
                                Spacer(modifier = Modifier.width(2.dp))
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
                        text = "Account & Preferences",
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = darkGreen
                        )
                    )
                    Text(
                        text = "Manage language, notifications, and AI assistant",
                        style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray)
                    )
                }

                // Settings Rows
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    SettingPremiumRow(
                        icon = Icons.Rounded.Translate,
                        title = AppLocalizer.localizeProfilePhrase("app language", currentLang),
                        subtitle = langLabel,
                        onClick = { showLanguageDialog = true }
                    )
                    SettingPremiumRow(
                        icon = Icons.Rounded.Notifications,
                        title = AppLocalizer.localizeProfilePhrase("notifications", currentLang),
                        subtitle = "Price alerts, order updates & announcements",
                        onClick = { }
                    )
                    SettingPremiumRow(
                        icon = Icons.Rounded.Mic,
                        title = AppLocalizer.localizeProfilePhrase("voice assistant", currentLang),
                        subtitle = "Multilingual AI buying & trade queries",
                        onClick = { navController.navigate(NavRoutes.VoiceAssistant) }
                    )
                }

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

        if (showLanguageDialog) {
            ProfileLanguageDialog(
                onDismiss = { showLanguageDialog = false }
            )
        }
    }
}
