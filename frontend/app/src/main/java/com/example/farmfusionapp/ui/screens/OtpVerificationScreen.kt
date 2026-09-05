package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.GppGood
import androidx.compose.material.icons.rounded.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.utils.AuthStore
import kotlinx.coroutines.delay

// Brand Theme Colors
private val SolidGreenPrimary = Color(0xFF256F35)
private val BrandDarkGreen = Color(0xFF143B29)
private val BrandTextMuted = Color(0xFF4A6B5D)
private val TrustCardBackground = Color(0xFFEFF7EE)
private val InputBorderColor = Color(0xFFE2E8F0)
private val OtpBoxBackground = Color(0xFFF8FAFC)

@Composable
fun OtpVerificationScreen(navController: NavController) {
    val context = LocalContext.current
    val focusManager = LocalFocusManager.current

    // Retrieve the phone number saved in AuthStore or default to farmer
    val savedToken = remember { AuthStore.getAuthToken(context) ?: "farmer" }
    val rawPhone = remember(savedToken) {
        val extracted = savedToken.removePrefix("user_")
        if (extracted.all { it.isDigit() } && extracted.length == 10) {
            extracted
        } else {
            ""
        }
    }
    val displayPhone = if (rawPhone.length == 10) {
        "+91 ${rawPhone.substring(0, 5)} ${rawPhone.substring(5)}"
    } else {
        "+91 98765 43210"
    }

    var otpCode by remember { mutableStateOf("") }
    var isError by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf("") }

    // Resend countdown timer (30 seconds)
    var resendTimer by remember { mutableIntStateOf(30) }
    var canResend by remember { mutableStateOf(false) }
    var otpResentMessage by remember { mutableStateOf(false) }

    LaunchedEffect(key1 = resendTimer, key2 = canResend) {
        if (!canResend && resendTimer > 0) {
            delay(1000L)
            resendTimer -= 1
            if (resendTimer == 0) {
                canResend = true
            }
        }
    }

    LaunchedEffect(otpResentMessage) {
        if (otpResentMessage) {
            delay(3500L)
            otpResentMessage = false
        }
    }

    val onVerifyOtp: () -> Unit = {
        focusManager.clearFocus()
        // If empty, auto-fill demo OTP "1234" for convenience or allow if valid
        val finalOtp = if (otpCode.isBlank()) "1234" else otpCode
        if (finalOtp.length == 4) {
            // Persist valid login session
            val sessionToken = if (rawPhone.isNotBlank()) "user_$rawPhone" else "user_farmer"
            AuthStore.saveLoginSession(context, sessionToken)

            // Navigate to Dashboard and clear login backstack
            navController.navigate(NavRoutes.Dashboard) {
                popUpTo(NavRoutes.Login) { inclusive = true }
                launchSingleTop = true
            }
        } else {
            isError = true
            errorMessage = "Please enter complete 4-digit code"
        }
    }

    Scaffold(
        containerColor = Color.White,
        topBar = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .statusBarsPadding()
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(
                    onClick = { navController.popBackStack() },
                    modifier = Modifier
                        .size(44.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(Color(0xFFF1F5F9))
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Rounded.ArrowBack,
                        contentDescription = "Back to Login",
                        tint = BrandDarkGreen
                    )
                }
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .imePadding()
                .navigationBarsPadding()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(16.dp))

            // FarmFusion Logo Badge
            Box(
                modifier = Modifier
                    .size(64.dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(Color(0xFFE8F5E9))
                    .border(1.5.dp, Color(0xFFC8E6C9), RoundedCornerShape(18.dp)),
                contentAlignment = Alignment.Center
            ) {
                Image(
                    painter = painterResource(id = R.drawable.ic_app_logo),
                    contentDescription = "FarmFusion Logo",
                    contentScale = ContentScale.Fit,
                    modifier = Modifier.size(42.dp)
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Headline
            Text(
                text = "Verify Phone Number",
                fontSize = 26.sp,
                fontWeight = FontWeight.ExtraBold,
                color = BrandDarkGreen,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(8.dp))

            // Subtitle with phone number
            Text(
                text = "We have sent a 4-digit verification code to",
                fontSize = 14.sp,
                color = BrandTextMuted,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(4.dp))

            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Text(
                    text = displayPhone,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1F2937)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Edit",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                    color = SolidGreenPrimary,
                    modifier = Modifier
                        .clickable(
                            interactionSource = remember { MutableInteractionSource() },
                            indication = null
                        ) {
                            navController.popBackStack()
                        }
                )
            }

            Spacer(modifier = Modifier.height(36.dp))

            // 4-digit OTP Input Boxes using single underlying BasicTextField
            BasicTextField(
                value = otpCode,
                onValueChange = { input ->
                    if (input.length <= 4 && input.all { it.isDigit() }) {
                        otpCode = input
                        isError = false
                    }
                },
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Number,
                    imeAction = ImeAction.Done
                ),
                keyboardActions = KeyboardActions(
                    onDone = { focusManager.clearFocus() }
                ),
                decorationBox = {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(14.dp, Alignment.CenterHorizontally)
                    ) {
                        for (i in 0 until 4) {
                            val char = otpCode.getOrNull(i)?.toString() ?: ""
                            val isFocused = otpCode.length == i

                            val boxBorderColor = when {
                                isError -> MaterialTheme.colorScheme.error
                                isFocused -> SolidGreenPrimary
                                char.isNotEmpty() -> SolidGreenPrimary.copy(alpha = 0.6f)
                                else -> InputBorderColor
                            }

                            val boxBgColor = when {
                                isFocused -> Color.White
                                char.isNotEmpty() -> Color.White
                                else -> OtpBoxBackground
                            }

                            Box(
                                modifier = Modifier
                                    .size(width = 62.dp, height = 66.dp)
                                    .clip(RoundedCornerShape(16.dp))
                                    .background(boxBgColor)
                                    .border(
                                        width = if (isFocused) 2.dp else 1.5.dp,
                                        color = boxBorderColor,
                                        shape = RoundedCornerShape(16.dp)
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = char,
                                    fontSize = 24.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = BrandDarkGreen
                                )
                            }
                        }
                    }
                }
            )

            AnimatedVisibility(visible = isError) {
                Text(
                    text = errorMessage,
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(top = 10.dp)
                )
            }

            Spacer(modifier = Modifier.height(28.dp))

            // Resend OTP Section
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    if (!canResend) {
                        Text(
                            text = "Resend code in ",
                            fontSize = 14.sp,
                            color = Color(0xFF6B7280)
                        )
                        Text(
                            text = "${resendTimer}s",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = SolidGreenPrimary
                        )
                    } else {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.clickable {
                                resendTimer = 30
                                canResend = false
                                otpCode = ""
                                isError = false
                                otpResentMessage = true
                            }
                        ) {
                            Icon(
                                imageVector = Icons.Rounded.Refresh,
                                contentDescription = "Resend",
                                tint = SolidGreenPrimary,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = "Resend OTP",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = SolidGreenPrimary
                            )
                        }
                    }
                }

                AnimatedVisibility(
                    visible = otpResentMessage,
                    enter = fadeIn(),
                    exit = fadeOut()
                ) {
                    Row(
                        modifier = Modifier.padding(top = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            imageVector = Icons.Rounded.CheckCircle,
                            contentDescription = null,
                            tint = SolidGreenPrimary,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "OTP Resent",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = SolidGreenPrimary
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            // Primary Solid Green Button
            Button(
                onClick = onVerifyOtp,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = SolidGreenPrimary,
                    contentColor = Color.White
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "Verify OTP",
                        color = Color.White,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Icon(
                        imageVector = Icons.AutoMirrored.Rounded.ArrowForward,
                        contentDescription = null,
                        tint = Color.White,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.weight(1f, fill = false))
            Spacer(modifier = Modifier.height(48.dp))

            // Security / Trust Footer
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 20.dp),
                contentAlignment = Alignment.Center
            ) {
                Row(
                    modifier = Modifier
                        .background(TrustCardBackground, RoundedCornerShape(16.dp))
                        .padding(vertical = 10.dp, horizontal = 18.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Rounded.GppGood,
                        contentDescription = null,
                        tint = SolidGreenPrimary,
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(10.dp))
                    Column {
                        Text(
                            text = "Your data is safe with us.",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = BrandDarkGreen
                        )
                        Text(
                            text = "We never share your information.",
                            fontSize = 11.sp,
                            color = BrandTextMuted
                        )
                    }
                }
            }
        }
    }
}
