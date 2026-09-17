package com.example.farmfusionapp.ui.screens

import androidx.activity.compose.BackHandler
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.rounded.GppGood
import androidx.compose.material.icons.rounded.Phone
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
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
import com.google.firebase.auth.FirebaseAuth
import kotlinx.coroutines.delay
import java.util.Locale
import kotlin.math.cos
import kotlin.math.sin

// Brand Colors
private val SolidGreenPrimary = Color(0xFF256F35)
private val BrandDarkGreen = Color(0xFF143B29)
private val BrandTextMuted = Color(0xFF4A6B5D)
private val TrustCardBackground = Color(0xFFEFF7EE)
private val InputBorderColor = Color(0xFFE2E8F0)

// Flow steps within the unified login experience
enum class LoginStep {
    PHONE,
    OTP
}

// User Role Enum for Role-Based Dashboard Routing
enum class UserRole(
    val key: String,
    val title: String,
    val subtitle: String,
    val illustrationRes: Int
) {
    FARMER(
        key = "farmer",
        title = "Farmer",
        subtitle = "Grow. Prosper.",
        illustrationRes = R.drawable.ill_login_bust_farmer
    ),
    BUYER(
        key = "buyer",
        title = "Buyer",
        subtitle = "Buy. Support.",
        illustrationRes = R.drawable.ill_login_bust_buyer
    )
}

@Composable
fun LoginScreen(navController: NavController) {
    val context = LocalContext.current
    LoginScreenContent(
        onLoginCompleted = { phone, role ->
            AuthStore.saveLoginSession(context, "user_${phone.ifBlank { role.key }}")
            AuthStore.saveUserRole(context, role.key)
            AuthStore.saveUserPhone(context, phone)
            val dest = if (role == UserRole.BUYER) NavRoutes.BuyerDashboard else NavRoutes.Dashboard
            navController.navigate(dest) {
                popUpTo(NavRoutes.Login) { inclusive = true }
                launchSingleTop = true
            }
        }
    )
}

private data class CloudSpec(
    val baseRelX: Float,
    val baseRelY: Float,
    val widthDp: Float,
    val alpha: Float,
    val driftDistDp: Float,
    val phase: Float
)

@Composable
fun LoginScreen(
    onGetOtpClicked: (String) -> Unit
) {
    LoginScreenContent(onLoginCompleted = { phone, _ -> onGetOtpClicked(phone) })
}

@Composable
fun LoginScreen(
    onGetOtpWithRole: (String, UserRole) -> Unit
) {
    LoginScreenContent(onLoginCompleted = onGetOtpWithRole)
}

@Composable
private fun LoginScreenContent(
    onLoginCompleted: (String, UserRole) -> Unit
) {
    val context = LocalContext.current
    val savedUserPhone = remember { AuthStore.getUserPhone(context) ?: "" }
    var currentStep by remember { mutableStateOf(LoginStep.PHONE) }
    var selectedRole by remember { mutableStateOf(UserRole.BUYER) }
    var phoneNumber by remember { mutableStateOf(savedUserPhone) }
    var isPhoneError by remember { mutableStateOf(false) }
    var phoneErrorCount by remember { mutableIntStateOf(0) }

    // Auto-dismiss phone warning after 5 seconds
    LaunchedEffect(phoneErrorCount) {
        if (phoneErrorCount > 0) {
            isPhoneError = true
            delay(5000L)
            isPhoneError = false
        }
    }

    // OTP states
    var otpCode by remember { mutableStateOf("") }
    var isOtpError by remember { mutableStateOf(false) }
    var otpErrorCount by remember { mutableIntStateOf(0) }
    var otpErrorMessage by remember { mutableStateOf("") }
    var resendTimer by remember { mutableIntStateOf(30) }
    var canResend by remember { mutableStateOf(false) }

    // Auto-dismiss OTP warning after 5 seconds
    LaunchedEffect(otpErrorCount) {
        if (otpErrorCount > 0) {
            isOtpError = true
            delay(5000L)
            isOtpError = false
        }
    }

    val focusManager = LocalFocusManager.current
    val density = LocalDensity.current.density

    // Smoothly go back to phone entry if back is pressed during OTP
    BackHandler(enabled = currentStep == LoginStep.OTP) {
        currentStep = LoginStep.PHONE
    }

    // Resend countdown timer
    LaunchedEffect(key1 = currentStep, key2 = resendTimer, key3 = canResend) {
        if (currentStep == LoginStep.OTP && !canResend && resendTimer > 0) {
            delay(1000L)
            resendTimer -= 1
            if (resendTimer == 0) {
                canResend = true
            }
        }
    }

    // -------------------------------------------------------------
    // ANIMATIONS: Windmill Circular Rotation & Slow Cloud Drift
    // -------------------------------------------------------------
    // 1. Windmill Continuous 360° Circular Rotation (only turbine fan rotates)
    val windmillTransition = rememberInfiniteTransition(label = "windmill_transition")
    val windmillRotation by windmillTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 6500, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "windmill_rotation"
    )

    // 2. Slow Cloud Drift Harmonic Loop (24s smooth cycle)
    val cloudTransition = rememberInfiniteTransition(label = "clouds_sky_anim")
    val cloudProgress by cloudTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 24000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "cloud_progress"
    )
    val cloudRad = cloudProgress * 2f * Math.PI.toFloat()

    val handleGetOtp: () -> Unit = {
        focusManager.clearFocus()
        val digits = phoneNumber.filter { it.isDigit() }
        if (digits.length != 10) {
            phoneErrorCount++
        } else {
            isPhoneError = false
            phoneErrorCount = 0
            AuthStore.saveUserPhone(context, digits)
            currentStep = LoginStep.OTP
            otpCode = ""
            isOtpError = false
            otpErrorCount = 0
            resendTimer = 30
            canResend = false
        }
    }

    val handleVerifyOtp: () -> Unit = {
        focusManager.clearFocus()
        val finalOtp = if (otpCode.isBlank()) "123456" else otpCode
        if (finalOtp.length == 6) {
            isOtpError = false
            otpErrorCount = 0
            val enteredDigits = phoneNumber.filter { it.isDigit() }
            val resolvedPhone = if (enteredDigits.length == 10) {
                enteredDigits
            } else {
                AuthStore.getUserPhone(context)
                    ?: try {
                        FirebaseAuth.getInstance().currentUser?.phoneNumber?.filter { it.isDigit() }?.takeLast(10)
                    } catch (e: Exception) {
                        null
                    }
                    ?: "9876543210"
            }
            AuthStore.saveUserPhone(context, resolvedPhone)
            onLoginCompleted(resolvedPhone, selectedRole)
        } else {
            otpErrorMessage = "Please enter complete 6-digit OTP"
            otpErrorCount++
        }
    }

    val handleSkip: () -> Unit = {
        focusManager.clearFocus()
        val enteredDigits = phoneNumber.filter { it.isDigit() }
        val resolvedPhone = if (enteredDigits.length == 10) {
            enteredDigits
        } else {
            AuthStore.getUserPhone(context) ?: "9876543210"
        }
        AuthStore.saveUserPhone(context, resolvedPhone)
        onLoginCompleted(resolvedPhone, selectedRole)
    }

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
    ) {
        val screenWidth = maxWidth
        // In ill_login_bg (853 x 1844), the visible illustration and its bottom wave curve end at y = 912px.
        // Ratio = 912 / 853 ≈ 1.069f. This ensures 100% of the illustration is shown while snug with the form below.
        val illustrationHeight = screenWidth * (912f / 853f)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .imePadding() // Handles the keyboard expansion
                .navigationBarsPadding()
        ) {
            // Top Background Illustration with Header & Headline overlay
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(illustrationHeight)
                    .clipToBounds()
            ) {
                // Fixed Base Layer: Landscape background
                Image(
                    painter = painterResource(id = R.drawable.ill_login_bg),
                    contentDescription = "Farm Landscape Background",
                    contentScale = ContentScale.Crop,
                    alignment = Alignment.TopCenter,
                    modifier = Modifier.fillMaxSize()
                )

                // 1. Windmill: Static tail & shaft atop tower with smoothly rotating circular turbine
                Box(
                    modifier = Modifier
                        .size(
                            width = screenWidth * (152.4f / 853f),
                            height = screenWidth * (138.9f / 853f)
                        )
                        .offset(
                            x = screenWidth * (704.3f / 853f),
                            y = screenWidth * (473.8f / 853f)
                        )
                ) {
                    // Static tail vane and horizontal shaft attached to the tower
                    Image(
                        painter = painterResource(id = R.drawable.ill_login_windmill_tail),
                        contentDescription = null,
                        contentScale = ContentScale.Fit,
                        modifier = Modifier.fillMaxSize()
                    )

                    // Rotating Turbine Fan precisely aligned with the wheel hub
                    Image(
                        painter = painterResource(id = R.drawable.ill_login_windmill_fan),
                        contentDescription = "Rotating Windmill Turbine",
                        contentScale = ContentScale.Fit,
                        modifier = Modifier
                            .size(screenWidth * (86.3f / 853f))
                            .offset(
                                x = screenWidth * (22.96f / 853f),
                                y = screenWidth * (26.24f / 853f)
                            )
                            .graphicsLayer {
                                rotationZ = windmillRotation
                                transformOrigin = TransformOrigin.Center
                            }
                    )
                }

                // 2. Soft Animated Clouds Drifting Slowly across the Sky
                Canvas(
                    modifier = Modifier.matchParentSize()
                ) {
                    val w = size.width
                    val h = size.height
                    if (w <= 0f || h <= 0f) return@Canvas

                    val clouds = listOf(
                        CloudSpec(baseRelX = 0.22f, baseRelY = 0.28f, widthDp = 80f, alpha = 0.60f, driftDistDp = 24f, phase = 0f),
                        CloudSpec(baseRelX = 0.74f, baseRelY = 0.35f, widthDp = 92f, alpha = 0.52f, driftDistDp = 28f, phase = 1.6f),
                        CloudSpec(baseRelX = 0.48f, baseRelY = 0.18f, widthDp = 64f, alpha = 0.45f, driftDistDp = 18f, phase = 3.2f)
                    )

                    for (cloud in clouds) {
                        val driftX = sin(cloudRad + cloud.phase) * (cloud.driftDistDp * density)
                        val driftY = cos(cloudRad * 2f + cloud.phase) * (4f * density)
                        val cx = w * cloud.baseRelX + driftX
                        val cy = h * cloud.baseRelY + driftY
                        val widthPx = cloud.widthDp * density
                        val hPx = widthPx * 0.36f
                        val color = Color.White.copy(alpha = cloud.alpha)

                        // Base soft rounded pill
                        drawRoundRect(
                            color = color,
                            topLeft = Offset(cx - widthPx * 0.5f, cy - hPx * 0.2f),
                            size = Size(widthPx, hPx * 0.65f),
                            cornerRadius = CornerRadius(hPx * 0.35f, hPx * 0.35f)
                        )
                        // Center dome
                        drawCircle(
                            color = color,
                            radius = hPx * 0.55f,
                            center = Offset(cx, cy - hPx * 0.16f)
                        )
                        // Left dome
                        drawCircle(
                            color = color,
                            radius = hPx * 0.42f,
                            center = Offset(cx - widthPx * 0.24f, cy - hPx * 0.04f)
                        )
                        // Right dome
                        drawCircle(
                            color = color,
                            radius = hPx * 0.38f,
                            center = Offset(cx + widthPx * 0.24f, cy + hPx * 0.02f)
                        )
                    }
                }

                // Header Content overlaying the illustration
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .statusBarsPadding()
                        .padding(horizontal = 24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Spacer(modifier = Modifier.height(8.dp))

                    // Brand Header: App Icon + Name + Tagline
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Box(
                            modifier = Modifier
                                .size(48.dp)
                                .clip(RoundedCornerShape(14.dp))
                                .background(Color(0xFFE8F5E9))
                                .border(1.5.dp, Color(0xFFC8E6C9), RoundedCornerShape(14.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Image(
                                painter = painterResource(id = R.drawable.ic_app_logo),
                                contentDescription = "FarmFusion Logo",
                                contentScale = ContentScale.Fit,
                                modifier = Modifier.size(32.dp)
                            )
                        }

                        Spacer(modifier = Modifier.width(12.dp))

                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = "Farm",
                                    fontSize = 24.sp,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = BrandDarkGreen
                                )
                                Text(
                                    text = "Fusion",
                                    fontSize = 24.sp,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = Color(0xFF22C55E) // Bright green
                                )
                            }
                            Text(
                                text = "Smart tools for a better harvest",
                                fontSize = 12.5.sp,
                                fontWeight = FontWeight.Medium,
                                color = BrandTextMuted
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(39.dp))

                    // Hero Headline (extra bold, center text)
                    Text(
                        text = "Empowering\nFarmers for a\nBrighter Tomorrow",
                        fontSize = 34.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = BrandDarkGreen,
                        lineHeight = 36.sp,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth()
                    )
                }

                // Temporary Skip Button at top right to bypass login during development
                Surface(
                    onClick = { handleSkip() },
                    shape = RoundedCornerShape(20.dp),
                    color = Color.White.copy(alpha = 0.90f),
                    border = BorderStroke(1.dp, Color(0xFFC8E6C9)),
                    shadowElevation = 2.dp,
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .statusBarsPadding()
                        .padding(top = 10.dp, end = 16.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    ) {
                        Text(
                            text = "Skip",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = SolidGreenPrimary
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(
                            imageVector = Icons.AutoMirrored.Rounded.ArrowForward,
                            contentDescription = "Skip Login",
                            tint = SolidGreenPrimary,
                            modifier = Modifier.size(14.dp)
                        )
                    }
                }
            }

            // Main Form Content - Smooth and fluid animated transition between Phone and OTP steps
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) {
                AnimatedContent(
                    targetState = currentStep,
                    transitionSpec = {
                        if (targetState == LoginStep.OTP) {
                            (slideInHorizontally(
                                animationSpec = tween(320, easing = FastOutSlowInEasing),
                                initialOffsetX = { fullWidth -> fullWidth / 4 }
                            ) + fadeIn(
                                animationSpec = tween(260)
                            )).togetherWith(
                                slideOutHorizontally(
                                    animationSpec = tween(260, easing = FastOutSlowInEasing),
                                    targetOffsetX = { fullWidth -> -fullWidth / 4 }
                                ) + fadeOut(
                                    animationSpec = tween(200)
                                )
                            )
                        } else {
                            (slideInHorizontally(
                                animationSpec = tween(320, easing = FastOutSlowInEasing),
                                initialOffsetX = { fullWidth -> -fullWidth / 4 }
                            ) + fadeIn(
                                animationSpec = tween(260)
                            )).togetherWith(
                                slideOutHorizontally(
                                    animationSpec = tween(260, easing = FastOutSlowInEasing),
                                    targetOffsetX = { fullWidth -> fullWidth / 4 }
                                ) + fadeOut(
                                    animationSpec = tween(200)
                                )
                            )
                        }
                    },
                    label = "login_step_transition",
                    modifier = Modifier.fillMaxSize()
                ) { step ->
                    when (step) {
                        LoginStep.PHONE -> {
                            Column(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(horizontal = 24.dp)
                                    .padding(top = 0.dp, bottom = 54.dp)
                            ) {
                                // "Who are you?" Section
                                Text(
                                    text = "Who are you?",
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF1E293B)
                                )

                                Spacer(modifier = Modifier.height(2.dp))

                                Text(
                                    text = "Choose the option that best describes you.",
                                    fontSize = 13.5.sp,
                                    color = Color(0xFF64748B)
                                )

                                Spacer(modifier = Modifier.height(8.dp))

                                // Role Selection Capsules: Farmer on left, Buyer on right
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                                ) {
                                    RoleCapsuleOption(
                                        role = UserRole.FARMER,
                                        isSelected = selectedRole == UserRole.FARMER,
                                        onClick = { selectedRole = UserRole.FARMER },
                                        modifier = Modifier.weight(1f)
                                    )
                                    RoleCapsuleOption(
                                        role = UserRole.BUYER,
                                        isSelected = selectedRole == UserRole.BUYER,
                                        onClick = { selectedRole = UserRole.BUYER },
                                        modifier = Modifier.weight(1f)
                                    )
                                }

                                // Clear, prominent contrast spacing between 'Who are you?' and 'Enter your phone number'
                                Spacer(modifier = Modifier.height(36.dp))

                                Text(
                                    text = "Enter your phone number",
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF1F2937)
                                )

                                Spacer(modifier = Modifier.height(2.dp))

                                Text(
                                    text = "We'll send you an OTP to continue.",
                                    fontSize = 13.5.sp,
                                    color = Color(0xFF6B7280)
                                )

                                Spacer(modifier = Modifier.height(8.dp))

                                // Phone Input Field
                                OutlinedTextField(
                                    value = phoneNumber,
                                    onValueChange = { input ->
                                        if (input.length <= 10 && input.all { it.isDigit() }) {
                                            phoneNumber = input
                                            isPhoneError = false
                                            phoneErrorCount = 0
                                        }
                                    },
                                    isError = isPhoneError,
                                    supportingText = if (isPhoneError) {
                                        {
                                            Text(
                                                text = "Please enter a valid 10-digit mobile number",
                                                color = MaterialTheme.colorScheme.error,
                                                fontSize = 12.sp
                                            )
                                        }
                                    } else null,
                                    placeholder = {
                                        Text(
                                            text = "Enter Your Phone Number",
                                            color = Color(0xFF9CA3AF),
                                            fontSize = 15.sp
                                        )
                                    },
                                    leadingIcon = {
                                        Icon(
                                            imageVector = Icons.Rounded.Phone,
                                            contentDescription = null,
                                            tint = if (isPhoneError) MaterialTheme.colorScheme.error else Color(0xFF9CA3AF),
                                            modifier = Modifier.size(20.dp)
                                        )
                                    },
                                    singleLine = true,
                                    keyboardOptions = KeyboardOptions(
                                        keyboardType = KeyboardType.Phone,
                                        imeAction = ImeAction.Done
                                    ),
                                    keyboardActions = KeyboardActions(
                                        onDone = { handleGetOtp() }
                                    ),
                                    shape = RoundedCornerShape(16.dp),
                                    colors = OutlinedTextFieldDefaults.colors(
                                        focusedContainerColor = Color.White,
                                        unfocusedContainerColor = Color.White,
                                        focusedBorderColor = SolidGreenPrimary,
                                        unfocusedBorderColor = InputBorderColor,
                                        focusedTextColor = Color(0xFF1F2937),
                                        unfocusedTextColor = Color(0xFF1F2937)
                                    ),
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .defaultMinSize(minHeight = 50.dp)
                                )

                                Spacer(modifier = Modifier.height(10.dp))

                                // Primary Button: Single colored green filled with white text
                                Button(
                                    onClick = { handleGetOtp() },
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(50.dp),
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
                                            text = "Get OTP",
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
                            }
                        }

                        LoginStep.OTP -> {
                            Column(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(horizontal = 24.dp)
                                    .padding(top = 0.dp, bottom = 54.dp)
                            ) {
                                Text(
                                    text = "Enter the OTP",
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF1E293B)
                                )

                                Spacer(modifier = Modifier.height(2.dp))

                                Text(
                                    text = "We've sent a 6-digit code to",
                                    fontSize = 13.5.sp,
                                    color = Color(0xFF6B7280)
                                )

                                Spacer(modifier = Modifier.height(2.dp))

                                Row(
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    val enteredDigits = phoneNumber.filter { it.isDigit() }
                                    val formattedPhone = remember(phoneNumber, currentStep) {
                                        if (enteredDigits.length == 10) {
                                            "+91 ${enteredDigits.substring(0, 5)} ${enteredDigits.substring(5)}"
                                        } else {
                                            val saved = AuthStore.getUserPhone(context)?.filter { it.isDigit() }
                                            if (!saved.isNullOrBlank() && saved.length == 10) {
                                                "+91 ${saved.substring(0, 5)} ${saved.substring(5)}"
                                            } else {
                                                val fbPhone = try {
                                                    FirebaseAuth.getInstance().currentUser?.phoneNumber
                                                } catch (e: Exception) {
                                                    null
                                                }
                                                if (!fbPhone.isNullOrBlank()) {
                                                    val fbDigits = fbPhone.filter { it.isDigit() }
                                                    val last10 = if (fbDigits.length >= 10) fbDigits.takeLast(10) else fbDigits
                                                    if (last10.length == 10) {
                                                        "+91 ${last10.substring(0, 5)} ${last10.substring(5)}"
                                                    } else {
                                                        fbPhone
                                                    }
                                                } else {
                                                    "+91 98765 43210"
                                                }
                                            }
                                        }
                                    }
                                    Text(
                                        text = formattedPhone,
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = SolidGreenPrimary
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = "Edit",
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = Color(0xFF64748B),
                                        modifier = Modifier.clickable {
                                            currentStep = LoginStep.PHONE
                                        }
                                    )
                                }

                                Spacer(modifier = Modifier.height(14.dp))

                                // 6-digit OTP Input Boxes
                                OtpCodeInputRow(
                                    otpCode = otpCode,
                                    onOtpChange = {
                                        otpCode = it
                                        isOtpError = false
                                        otpErrorCount = 0
                                    },
                                    isError = isOtpError,
                                    onDone = { handleVerifyOtp() }
                                )

                                if (isOtpError) {
                                    Text(
                                        text = otpErrorMessage,
                                        color = MaterialTheme.colorScheme.error,
                                        fontSize = 12.sp,
                                        modifier = Modifier.padding(top = 4.dp)
                                    )
                                }

                                Spacer(modifier = Modifier.height(14.dp))

                                // Resend Code Section
                                Column(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text(
                                        text = "Didn't receive the code?",
                                        fontSize = 13.sp,
                                        color = Color(0xFF6B7280),
                                        textAlign = TextAlign.Center
                                    )
                                    Spacer(modifier = Modifier.height(3.dp))
                                    if (!canResend) {
                                        val timerText = String.format(Locale.getDefault(), "00:%02d", resendTimer)
                                        Text(
                                            text = "Resend OTP in $timerText",
                                            fontSize = 13.5.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = SolidGreenPrimary,
                                            textAlign = TextAlign.Center
                                        )
                                    } else {
                                        Text(
                                            text = "Resend OTP",
                                            fontSize = 13.5.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = SolidGreenPrimary,
                                            textAlign = TextAlign.Center,
                                            modifier = Modifier.clickable {
                                                resendTimer = 30
                                                canResend = false
                                                otpCode = ""
                                                isOtpError = false
                                            }
                                        )
                                    }
                                }

                                Spacer(modifier = Modifier.height(16.dp))

                                // Primary Button: Verify OTP
                                Button(
                                    onClick = { handleVerifyOtp() },
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(50.dp),
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
                            }
                        }
                    }
                }

                // Security / Trust Footer - Locked at the bottom center for BOTH screens
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .align(Alignment.BottomCenter)
                        .padding(bottom = 6.dp),
                    contentAlignment = Alignment.Center
                ) {
                    SecurityTrustBadge()
                }
            }
        }
    }
}

/**
 * Security & Trust Footer Badge - Animated, lively, and trust-inspiring without external graphics.
 */
@Composable
private fun SecurityTrustBadge(modifier: Modifier = Modifier) {
    // Subtle breathing pulse for the security shield badge
    val infiniteTransition = rememberInfiniteTransition(label = "trust_badge_pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 0.94f,
        targetValue = 1.06f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 2200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_scale"
    )
    val glowAlpha by infiniteTransition.animateFloat(
        initialValue = 0.30f,
        targetValue = 0.75f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 2200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow_alpha"
    )

    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        color = Color(0xFFF6FBF7),
        border = BorderStroke(1.dp, Color(0xFFD4EBD7))
    ) {
        Row(
            modifier = Modifier
                .padding(horizontal = 14.dp, vertical = 7.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Animated Shield Container with glowing pulse effect
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier.size(28.dp)
            ) {
                // Soft glow halo behind shield
                Box(
                    modifier = Modifier
                        .size(26.dp)
                        .graphicsLayer {
                            scaleX = pulseScale
                            scaleY = pulseScale
                            alpha = glowAlpha
                        }
                        .background(Color(0xFFDCFCE7), CircleShape)
                )

                // Shield Icon - larger size without altering card bounds
                Icon(
                    imageVector = Icons.Rounded.GppGood,
                    contentDescription = "Data Security Verified",
                    tint = SolidGreenPrimary,
                    modifier = Modifier.size(24.dp)
                )
            }

            Spacer(modifier = Modifier.width(10.dp))

            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = "Your Data Is Safe With Us.",
                    fontSize = 11.5.sp,
                    fontWeight = FontWeight.Bold,
                    color = BrandDarkGreen,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(1.dp))

                Text(
                    text = "We never share your personal information.",
                    fontSize = 10.sp,
                    color = BrandTextMuted,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

/**
 * Role Capsule Option - Interactive pill-shaped radio container for Farmer and Buyer roles.
 */
@Composable
private fun RoleCapsuleOption(
    role: UserRole,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val backgroundColor = if (isSelected) Color(0xFFEBF8EE) else Color(0xFFF8FAFC)
    val borderColor = if (isSelected) Color(0xFF16A34A) else Color(0xFFE2E8F0)
    val borderWidth = if (isSelected) 1.5.dp else 1.dp

    Surface(
        onClick = onClick,
        modifier = modifier.height(54.dp),
        shape = RoundedCornerShape(10.dp),
        color = backgroundColor,
        border = BorderStroke(borderWidth, borderColor)
    ) {
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 10.dp, vertical = 5.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Radio Indicator
            RoleRadioIndicator(isSelected = isSelected)

            Spacer(modifier = Modifier.width(6.dp))

            // Character Bust Illustration
            Image(
                painter = painterResource(id = role.illustrationRes),
                contentDescription = role.title,
                contentScale = ContentScale.Fit,
                modifier = Modifier.size(34.dp)
            )

            Spacer(modifier = Modifier.width(6.dp))

            // Role Title & Subtitle
            Column(
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = role.title,
                    fontSize = 13.5.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1E293B),
                    maxLines = 1
                )
                Text(
                    text = role.subtitle,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Normal,
                    color = if (isSelected) Color(0xFF4A6B5D) else Color(0xFF64748B),
                    maxLines = 1
                )
            }
        }
    }
}

/**
 * Concentric custom radio circle matching the exact design specification.
 */
@Composable
private fun RoleRadioIndicator(
    isSelected: Boolean,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .size(19.dp)
            .border(
                width = if (isSelected) 2.dp else 1.5.dp,
                color = if (isSelected) Color(0xFF16A34A) else Color(0xFF94A3B8),
                shape = CircleShape
            ),
        contentAlignment = Alignment.Center
    ) {
        if (isSelected) {
            Box(
                modifier = Modifier
                    .size(8.5.dp)
                    .background(Color(0xFF16A34A), CircleShape)
            )
        }
    }
}

/**
 * 6-Digit OTP Box Row - Matches Image 2 reference with responsive rounded square boxes,
 * en-dash placeholders when empty, and smooth focus indicator highlighting.
 */
@Composable
private fun OtpCodeInputRow(
    otpCode: String,
    onOtpChange: (String) -> Unit,
    isError: Boolean,
    modifier: Modifier = Modifier,
    onDone: () -> Unit
) {
    BasicTextField(
        value = otpCode,
        onValueChange = { input ->
            if (input.length <= 6 && input.all { it.isDigit() }) {
                onOtpChange(input)
                if (input.length == 6) {
                    onDone()
                }
            }
        },
        keyboardOptions = KeyboardOptions(
            keyboardType = KeyboardType.Number,
            imeAction = ImeAction.Done
        ),
        keyboardActions = KeyboardActions(
            onDone = { onDone() }
        ),
        modifier = modifier.fillMaxWidth(),
        decorationBox = {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                for (i in 0 until 6) {
                    val char = otpCode.getOrNull(i)?.toString() ?: ""
                    val isCurrent = otpCode.length == i || (otpCode.length == 6 && i == 5)
                    val isFilled = char.isNotEmpty()

                    val borderColor = when {
                        isError -> MaterialTheme.colorScheme.error
                        isCurrent -> SolidGreenPrimary
                        isFilled -> SolidGreenPrimary.copy(alpha = 0.5f)
                        else -> InputBorderColor
                    }

                    val borderWidth = if (isCurrent) 1.5.dp else 1.dp
                    val bgBoxColor = if (isCurrent) Color(0xFFF0FDF4) else Color(0xFFF8FAFC)

                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .height(52.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(bgBoxColor)
                            .border(borderWidth, borderColor, RoundedCornerShape(12.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        if (isFilled) {
                            Text(
                                text = char,
                                fontSize = 20.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1E293B),
                                textAlign = TextAlign.Center
                            )
                        } else {
                            Text(
                                text = "—",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Normal,
                                color = Color(0xFF94A3B8),
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                }
            }
        }
    )
}