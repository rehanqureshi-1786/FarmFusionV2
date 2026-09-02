package com.example.farmfusionapp.ui.screens

import androidx.navigation.NavController
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PersonOutline
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.PhoneAndroid
import androidx.compose.material.icons.outlined.RadioButtonUnchecked
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.farmfusionapp.R
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.common.api.ApiException

// ---- Colors matched to the FarmFusion green palette used in the mock ----
private val FarmGreenDark = Color(0xFF1B5E20)
private val FarmGreenPrimary = Color(0xFF2E7D32)
private val FarmGreenLight = Color(0xFFE8F5E9)
private val FarmGreenBorder = Color(0xFFA5D6A7)
private val FarmBackground = Color(0xFFF3F8F1)
private val FarmTextGray = Color(0xFF6B7280)

enum class UserRole { FARMER, BUYER }

@Composable
fun LoginScreen(navController: NavController) {
    LoginScreen(
        onNavigateToPhoneSignUp = { navController.navigate(NavRoutes.Register) },
        onGoogleIdTokenReceived = { token -> navController.navigate(NavRoutes.Dashboard) }
    )
}

@Composable
fun LoginScreen(
    onNavigateToPhoneSignUp: () -> Unit,
    onGoogleIdTokenReceived: (String) -> Unit,
    onSignInWithPhoneClicked: () -> Unit = onNavigateToPhoneSignUp
) {
    var selectedRole by remember { mutableStateOf(UserRole.FARMER) }

    // Standard Google Sign-In launcher. Replace the web client id below
    // with the one from your Firebase project (google-services.json ->
    // "client_type": 3 entry, or Firebase Console > Authentication > Sign-in method > Google).
    val context = androidx.compose.ui.platform.LocalContext.current
    val googleSignInOptions = remember {
        GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestIdToken(context.getString(R.string.default_web_client_id))
            .requestEmail()
            .build()
    }
    val googleSignInClient = remember { GoogleSignIn.getClient(context, googleSignInOptions) }

    val googleLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val task = GoogleSignIn.getSignedInAccountFromIntent(result.data)
        try {
            val account = task.getResult(ApiException::class.java)
            account?.idToken?.let { onGoogleIdTokenReceived(it) }
        } catch (e: ApiException) {
            // Surface this via a Snackbar/Toast in your Activity if you like.
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(FarmBackground)
                .verticalScroll(rememberScrollState())
        ) {
            // ---------------- HEADER ILLUSTRATION ----------------
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(440.dp)
            ) {
                Image(
                    painter = painterResource(id = R.drawable.ill_header_bg),
                    contentDescription = null,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxSize()
                )

                Column(
                    modifier = Modifier
                        .align(Alignment.TopCenter)
                        .padding(top = 90.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        // Leaf logo mark. Swap for your own drawable if you have one.
                        Box(
                            modifier = Modifier
                                .size(56.dp)
                                .clip(RoundedCornerShape(14.dp))
                                .background(FarmGreenLight)
                                .border(1.dp, FarmGreenBorder, RoundedCornerShape(14.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.CheckCircle, // placeholder leaf icon
                                contentDescription = null,
                                tint = FarmGreenPrimary,
                                modifier = Modifier.size(30.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            text = "Farm",
                            fontSize = 30.sp,
                            fontWeight = FontWeight.Bold,
                            color = FarmGreenDark
                        )
                        Text(
                            text = "Fusion",
                            fontSize = 30.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF1F2937)
                        )
                    }
                    Spacer(modifier = Modifier.height(14.dp))
                    Text(
                        text = "Smart tools for a better harvest",
                        fontSize = 15.sp,
                        color = FarmTextGray
                    )
                }
            }

            // ---------------- MAIN CONTENT ----------------
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
            ) {

                Text(
                    text = "Are you a",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF1F2937)
                )
                Spacer(modifier = Modifier.height(10.dp))

                Row(modifier = Modifier.fillMaxWidth()) {
                    RoleCard(
                        label = "Farmer",
                        icon = Icons.Default.Person,
                        selected = selectedRole == UserRole.FARMER,
                        modifier = Modifier
                            .weight(1f)
                            .clickable { selectedRole = UserRole.FARMER }
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    RoleCard(
                        label = "Buyer",
                        icon = Icons.Default.PersonOutline,
                        selected = selectedRole == UserRole.BUYER,
                        modifier = Modifier
                            .weight(1f)
                            .clickable { selectedRole = UserRole.BUYER }
                    )
                }

                Spacer(modifier = Modifier.height(28.dp))
                DividerWithText(text = "Sign in to continue")
                Spacer(modifier = Modifier.height(18.dp))

                // ---- Google Sign-In ----
                OutlinedButton(
                    onClick = { googleLauncher.launch(googleSignInClient.signInIntent) },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp),
                    shape = RoundedCornerShape(14.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE0E0E0)),
                    colors = ButtonDefaults.outlinedButtonColors(containerColor = Color.White)
                ) {
                    Image(
                        painter = painterResource(id = R.drawable.ic_google_logo),
                        contentDescription = null,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        text = "Sign in with Google",
                        color = Color(0xFF1F2937),
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))
                DividerWithText(text = "or")
                Spacer(modifier = Modifier.height(16.dp))

                // ---- Phone Sign-In ----
                OutlinedButton(
                    onClick = onSignInWithPhoneClicked,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp),
                    shape = RoundedCornerShape(14.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE0E0E0)),
                    colors = ButtonDefaults.outlinedButtonColors(containerColor = Color.White)
                ) {
                    Icon(
                        imageVector = Icons.Default.Phone,
                        contentDescription = null,
                        tint = FarmGreenPrimary,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        text = "Sign in with phone number",
                        color = Color(0xFF1F2937),
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                // ---- "New to FarmFusion?" card ----
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Box(
                            modifier = Modifier
                                .size(56.dp)
                                .clip(CircleShape)
                                .background(FarmGreenLight),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.PhoneAndroid,
                                contentDescription = null,
                                tint = FarmGreenPrimary,
                                modifier = Modifier.size(26.dp)
                            )
                        }
                        Spacer(modifier = Modifier.height(14.dp))
                        Text(
                            text = "New to FarmFusion?",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = FarmGreenDark
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Sign up with your phone number",
                            fontSize = 14.sp,
                            color = FarmTextGray
                        )
                        Spacer(modifier = Modifier.height(18.dp))
                        OutlinedButton(
                            onClick = onNavigateToPhoneSignUp,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(52.dp),
                            shape = RoundedCornerShape(14.dp),
                            border = androidx.compose.foundation.BorderStroke(1.5.dp, FarmGreenPrimary)
                        ) {
                            Text(
                                text = "Sign up with phone number",
                                color = FarmGreenPrimary,
                                fontWeight = FontWeight.SemiBold,
                                fontSize = 15.sp
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(text = "›", color = FarmGreenPrimary, fontSize = 18.sp)
                        }
                    }
                }

                Spacer(modifier = Modifier.height(28.dp))

                // ---- Footer ----
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = null,
                        tint = FarmGreenPrimary,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Your data is safe with us.\nWe never share your information.",
                        fontSize = 12.sp,
                        color = FarmTextGray,
                        textAlign = TextAlign.Center
                    )
                }
                Spacer(modifier = Modifier.height(24.dp))
            }
        }
    }
}

@Composable
private fun RoleCard(
    label: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    selected: Boolean,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .height(76.dp)
            .clip(RoundedCornerShape(14.dp))
            .background(if (selected) FarmGreenLight else Color.White)
            .border(
                width = 1.5.dp,
                color = if (selected) FarmGreenPrimary else Color(0xFFE5E7EB),
                shape = RoundedCornerShape(14.dp)
            )
            .padding(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxSize(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(38.dp)
                    .clip(CircleShape)
                    .background(if (selected) Color.White else Color(0xFFF3F4F6)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = if (selected) FarmGreenPrimary else Color(0xFF9CA3AF),
                    modifier = Modifier.size(20.dp)
                )
            }
            Spacer(modifier = Modifier.width(10.dp))
            Text(
                text = label,
                fontWeight = FontWeight.SemiBold,
                color = if (selected) FarmGreenDark else Color(0xFF374151),
                fontSize = 15.sp
            )
        }

        // Selection indicator (top-right dot/circle)
        Box(modifier = Modifier.fillMaxSize()) {
            Icon(
                imageVector = if (selected) Icons.Default.CheckCircle else Icons.Outlined.RadioButtonUnchecked,
                contentDescription = null,
                tint = if (selected) FarmGreenPrimary else Color(0xFFD1D5DB),
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .size(18.dp)
            )
        }
    }
}

@Composable
private fun DividerWithText(text: String) {
    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
        HorizontalDivider(modifier = Modifier.weight(1f), color = Color(0xFFE5E7EB))
        Text(
            text = text,
            color = FarmTextGray,
            fontSize = 13.sp,
            modifier = Modifier.padding(horizontal = 12.dp)
        )
        HorizontalDivider(modifier = Modifier.weight(1f), color = Color(0xFFE5E7EB))
    }
}