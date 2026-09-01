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
    val displayCity = WeatherSnapshotStore.latestWeather?.city ?: "Nagpur, Maharashtra"

    // Theme Colors
    val darkGreen = Color(0xFF1E5631)
    val lightGreenBg = Color(0xFFF7FAF7)

    // Dialog & Global Blur States
    var showLanguageDialog by remember { mutableStateOf(false) }
    val globalBlur = LocalGlobalBlur.current

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
                            stringResource(R.string.profile_title),
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
                                    text = displayCity,
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
                        stringResource(R.string.profile_farm_section_title),
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = FontWeight.Bold,
                            color = darkGreen
                        )
                    )
                    Text(
                        stringResource(R.string.profile_farm_section_sub),
                        style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray)
                    )
                }

                // Settings Rows
                SettingPremiumRow(
                    icon = Icons.Rounded.Language,
                    title = stringResource(R.string.profile_language),
                    subtitle = langLabel,
                    onClick = { showLanguageDialog = true }
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
                    onClick = { navController.navigate(NavRoutes.VoiceAssistant) }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Logout Button
                Button(
                    onClick = {
                        authViewModel.logout(context)
                        navController.navigate(NavRoutes.Login) {
                            popUpTo(0) { inclusive = true }
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Icon(Icons.Rounded.ExitToApp, contentDescription = null, tint = Color.White)
                    Spacer(modifier = Modifier.width(12.dp))
                    Text("Logout", fontWeight = FontWeight.Bold, color = Color.White)
                }

                Spacer(modifier = Modifier.height(40.dp))
            }
        }
    }

    // Modal Language Selection Popup
    if (showLanguageDialog) {

        // This guarantees the blur triggers when the dialog appears,
        // and ALWAYS clears when the dialog leaves the screen.
        DisposableEffect(Unit) {
            globalBlur.value = true
            onDispose {
                globalBlur.value = false
            }
        }

        LanguageSelectionDialog(
            currentLanguageCode = langCode,
            onDismiss = { showLanguageDialog = false },
            onSave = { selectedCode ->
                showLanguageDialog = false
                AuthStore.saveLanguage(context, selectedCode)
                (context as? Activity)?.recreate()
            }
        )
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

@Composable
fun LanguageSelectionDialog(
    currentLanguageCode: String,
    onDismiss: () -> Unit,
    onSave: (String) -> Unit
) {
    val languages = listOf(
        "en" to "English / English",
        "hi" to "Hindi / हिंदी",
        "ta" to "Tamil / தமிழ்",
        "te" to "Telugu / తెలుగు",
        "kn" to "Kannada / ಕನ್ನಡ",
        "mr" to "Marathi / मराठी",
        "gu" to "Gujarati / ગુજરાતી",
        "bn" to "Bengali / বাংলা"
    )

    var selected by remember { mutableStateOf(currentLanguageCode) }
    val view = LocalView.current

    // Clears the default heavy Compose shadow/dim so our custom overlay shines through
    LaunchedEffect(view) {
        val window = (view.parent as? DialogWindowProvider)?.window
        window?.let {
            it.clearFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND)
        }
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
                .background(Color.Black.copy(alpha = 0.25f)) // Slight dim background
                .clickable(
                    interactionSource = remember { MutableInteractionSource() },
                    indication = null,
                    onClick = onDismiss
                ),
            contentAlignment = Alignment.Center
        ) {
            Surface(
                modifier = Modifier
                    .fillMaxWidth(0.85f)
                    .clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null,
                        onClick = {} // Consume clicks to prevent dismissing when clicking the card
                    ),
                shape = RoundedCornerShape(24.dp),
                color = Color.White,
                shadowElevation = 12.dp
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    // Header
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Choose Language",
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1B1B1B)
                            )
                        )
                        IconButton(
                            onClick = onDismiss,
                            modifier = Modifier
                                .size(36.dp)
                                .background(Color(0xFFF5F5F5), CircleShape)
                        ) {
                            Icon(Icons.Rounded.Close, contentDescription = "Close", tint = Color.Gray, modifier = Modifier.size(20.dp))
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Language List
                    LazyColumn(
                        modifier = Modifier.heightIn(max = 400.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(languages) { (code, name) ->
                            val isSelected = selected == code
                            Surface(
                                onClick = { selected = code },
                                shape = RoundedCornerShape(12.dp),
                                color = Color.White,
                                border = BorderStroke(
                                    width = 1.dp,
                                    color = if (isSelected) Color(0xFF2E7D32) else Color(0xFFEEEEEE)
                                )
                            ) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(horizontal = 16.dp, vertical = 14.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = if (isSelected) Icons.Rounded.RadioButtonChecked else Icons.Rounded.RadioButtonUnchecked,
                                        contentDescription = null,
                                        tint = if (isSelected) Color(0xFF2E7D32) else Color.Gray,
                                        modifier = Modifier.size(22.dp)
                                    )
                                    Spacer(modifier = Modifier.width(12.dp))
                                    Text(
                                        text = name,
                                        style = MaterialTheme.typography.bodyLarge.copy(
                                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                            color = Color(0xFF1B1B1B)
                                        )
                                    )
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    // Action Button
                    Button(
                        onClick = { onSave(selected) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(50.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text("Done", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    }
                }
            }
        }
    }
}