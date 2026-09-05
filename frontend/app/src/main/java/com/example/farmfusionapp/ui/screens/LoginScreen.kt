package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.rounded.GppGood
import androidx.compose.material.icons.rounded.Phone
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

// Brand Colors
private val SolidGreenPrimary = Color(0xFF256F35)
private val BrandDarkGreen = Color(0xFF143B29)
private val BrandTextMuted = Color(0xFF4A6B5D)
private val TrustCardBackground = Color(0xFFEFF7EE)
private val InputBorderColor = Color(0xFFE2E8F0)

@Composable
fun LoginScreen(navController: NavController) {
    val context = LocalContext.current
    LoginScreenContent(
        onGetOtpClicked = { phone ->
            AuthStore.saveLoginSession(context, "user_${phone.ifBlank { "farmer" }}")
            // Navigates securely to the OTP Screen!
            navController.navigate(NavRoutes.OtpVerification)
        }
    )
}

@Composable
fun LoginScreen(
    onGetOtpClicked: (String) -> Unit
) {
    LoginScreenContent(onGetOtpClicked = onGetOtpClicked)
}

@Composable
private fun LoginScreenContent(
    onGetOtpClicked: (String) -> Unit
) {
    var phoneNumber by remember { mutableStateOf("") }
    var isPhoneError by remember { mutableStateOf(false) }
    val focusManager = LocalFocusManager.current

    val handleGetOtp = {
        focusManager.clearFocus()
        if (phoneNumber.isNotEmpty() && phoneNumber.length < 10) {
            isPhoneError = true
        } else {
            isPhoneError = false
            onGetOtpClicked(phoneNumber)
        }
    }

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
    ) {
        val screenWidth = maxWidth
        // In ill_login_bg (853 x 1844), the visible illustration and its bottom curve end at y = 939px.
        // Ratio = 939 / 853 ≈ 1.101f. This ensures 100% of the illustration and strong curve are shown.
        val illustrationHeight = screenWidth * (939f / 853f)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .imePadding() // Handles the keyboard expansion
                .navigationBarsPadding()
                .verticalScroll(rememberScrollState())
        ) {
            // Top Background Illustration with Header & Headline overlay
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(illustrationHeight)
            ) {
                Image(
                    painter = painterResource(id = R.drawable.ill_login_bg),
                    contentDescription = "Farm Landscape Background",
                    contentScale = ContentScale.Crop,
                    alignment = Alignment.TopCenter,
                    modifier = Modifier.fillMaxSize()
                )

                // Header Content overlaying the illustration
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .statusBarsPadding()
                        .padding(horizontal = 24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Spacer(modifier = Modifier.height(24.dp))

                    // Brand Header: App Icon + Name + Tagline
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Box(
                            modifier = Modifier
                                .size(52.dp)
                                .clip(RoundedCornerShape(14.dp))
                                .background(Color(0xFFE8F5E9))
                                .border(1.5.dp, Color(0xFFC8E6C9), RoundedCornerShape(14.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Image(
                                painter = painterResource(id = R.drawable.ic_app_logo),
                                contentDescription = "FarmFusion Logo",
                                contentScale = ContentScale.Fit,
                                modifier = Modifier.size(34.dp)
                            )
                        }

                        Spacer(modifier = Modifier.width(14.dp))

                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = "Farm",
                                    fontSize = 26.sp,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = BrandDarkGreen
                                )
                                Text(
                                    text = "Fusion",
                                    fontSize = 26.sp,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = Color(0xFF22C55E) // Bright green
                                )
                            }
                            Text(
                                text = "Smart tools for a better harvest",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Medium,
                                color = BrandTextMuted
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(32.dp))

                    // Hero Headline (semi-bold, same layout and position)
                    Text(
                        text = "Empowering\nFarmers for a\nBrighter Tomorrow",
                        fontSize = 30.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = BrandDarkGreen,
                        lineHeight = 38.sp,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            // Main Form Content - starts immediately right below the illustration curve
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
                    .padding(top = 16.dp, bottom = 24.dp)
            ) {
                Text(
                    text = "Enter your phone number",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1F2937)
                )

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = "We'll send you an OTP to continue",
                    fontSize = 14.sp,
                    color = Color(0xFF6B7280)
                )

                Spacer(modifier = Modifier.height(18.dp))

                // Phone Input Field
                OutlinedTextField(
                    value = phoneNumber,
                    onValueChange = { input ->
                        if (input.length <= 10 && input.all { it.isDigit() }) {
                            phoneNumber = input
                            isPhoneError = false
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
                        .defaultMinSize(minHeight = 56.dp)
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Primary Button: Single colored green filled with white text
                Button(
                    onClick = handleGetOtp,
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
}