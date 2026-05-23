package com.example.farmfusionapp.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import androidx.compose.ui.res.stringResource
import com.example.farmfusionapp.R
import com.example.farmfusionapp.ui.components.PremiumButton
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.viewmodel.AuthViewModel

@Composable
fun LoginScreen(navController: NavController) {
    // Login screen disabled for local development — navigate straight to dashboard
    LaunchedEffect(Unit) {
        navController.navigate(NavRoutes.Dashboard) {
            popUpTo(NavRoutes.Login) { inclusive = true }
        }
    }

    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        NeoScaffoldBackground {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                LoginHeader()
                Spacer(modifier = Modifier.height(24.dp))
                Text("Login disabled in dev mode.", style = MaterialTheme.typography.bodyLarge)
            }
        }
    }
}

@Composable
fun EmailLoginSection(email: String, password: String, onEmailChange: (String) -> Unit, onPasswordChange: (String) -> Unit, onLogin: () -> Unit, isLoading: Boolean) {
    Column(modifier = Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
        Surface(shape = RoundedCornerShape(24.dp), color = MaterialTheme.colorScheme.surface, tonalElevation = 4.dp, modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                OutlinedTextField(value = email, onValueChange = onEmailChange, label = { Text("Email Address") }, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp), leadingIcon = { Icon(Icons.Rounded.Email, null) }, singleLine = true)
                OutlinedTextField(value = password, onValueChange = onPasswordChange, label = { Text("Password") }, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp), leadingIcon = { Icon(Icons.Rounded.Lock, null) }, visualTransformation = PasswordVisualTransformation(), singleLine = true)
            }
        }
        Spacer(modifier = Modifier.height(24.dp))
        PremiumButton(text = "LOGIN", onClick = onLogin, icon = Icons.AutoMirrored.Rounded.ArrowForward, isLoading = isLoading, enabled = email.isNotBlank() && password.isNotBlank())
    }
}

@Composable
fun LoginHeader() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Box(modifier = Modifier.size(100.dp).background(brush = Brush.linearGradient(colors = listOf(MaterialTheme.colorScheme.primary, MaterialTheme.colorScheme.tertiary)), shape = CircleShape), contentAlignment = Alignment.Center) {
            Icon(imageVector = Icons.Rounded.Agriculture, contentDescription = null, modifier = Modifier.size(56.dp), tint = Color.White)
        }
        Spacer(modifier = Modifier.height(24.dp))
        Text(text = stringResource(R.string.welcome_to) + " Farmer!", style = MaterialTheme.typography.headlineMedium.copy(fontWeight = FontWeight.Black, color = MaterialTheme.colorScheme.primary), textAlign = TextAlign.Center)
        Text(text = "Please login with your email", style = MaterialTheme.typography.bodyLarge.copy(color = MaterialTheme.colorScheme.onSurfaceVariant), textAlign = TextAlign.Center, modifier = Modifier.padding(top = 4.dp))
    }
}

@Composable
fun TrustIndicators() {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Icon(Icons.Rounded.Security, null, modifier = Modifier.size(20.dp), tint = MaterialTheme.colorScheme.primary)
            Text("100% Secure & Trusted", style = MaterialTheme.typography.bodyMedium)
        }
    }
}
