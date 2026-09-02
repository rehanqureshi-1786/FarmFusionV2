package com.example.farmfusionapp.ui.screens

import android.app.Activity
import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.model.AppLanguage
import com.example.farmfusionapp.data.model.LanguageRegistry
import com.example.farmfusionapp.network.RetrofitInstance
import com.example.farmfusionapp.ui.components.NeoScaffoldBackground
import com.example.farmfusionapp.ui.components.PremiumButton
import com.example.farmfusionapp.utils.AuthStore
import com.example.farmfusionapp.utils.LocaleHelper
import com.example.farmfusionapp.viewmodel.UserViewModel
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LanguageSelectionScreen(
    navController: NavController,
    userViewModel: UserViewModel = viewModel()
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var searchQuery by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf("ALL") } // ALL, SCHEDULED, DIALECTS

    val savedLang = remember { AuthStore.getLanguage(context) ?: "en" }
    val savedDialect = remember { AuthStore.getDialect(context) }
    var selectedCode by remember { mutableStateOf(savedDialect ?: savedLang) }
    var isSaving by remember { mutableStateOf(false) }

    val allLanguages = LanguageRegistry.allLanguages

    val filteredLanguages = allLanguages.filter { lang ->
        val matchesCategory = when (selectedCategory) {
            "SCHEDULED" -> !lang.isDialect
            "DIALECTS" -> lang.isDialect
            else -> true
        }
        val matchesSearch = searchQuery.isBlank() ||
                lang.name.contains(searchQuery, ignoreCase = true) ||
                lang.nativeName.contains(searchQuery, ignoreCase = true) ||
                lang.code.contains(searchQuery, ignoreCase = true) ||
                lang.regions.any { it.contains(searchQuery, ignoreCase = true) }
        matchesCategory && matchesSearch
    }

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Select Language / भाषा चुनें", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        NeoScaffoldBackground(modifier = Modifier.fillMaxSize().padding(padding)) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Search Bar
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = Color.White,
                    shadowElevation = 2.dp,
                    border = BorderStroke(1.dp, Color(0xFFE5E7EB)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    TextField(
                        value = searchQuery,
                        onValueChange = { searchQuery = it },
                        placeholder = { Text("Search language or dialect (e.g. Marwari, Gujarati, हिन्दी)...", fontSize = 13.sp) },
                        leadingIcon = { Icon(Icons.Rounded.Search, null, tint = Color.Gray) },
                        trailingIcon = {
                            if (searchQuery.isNotEmpty()) {
                                IconButton(onClick = { searchQuery = "" }) {
                                    Icon(Icons.Rounded.Clear, contentDescription = "Clear")
                                }
                            }
                        },
                        singleLine = true,
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent
                        ),
                        modifier = Modifier.fillMaxWidth()
                    )
                }

                // Category Filter Chips
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(
                        selected = selectedCategory == "ALL",
                        onClick = { selectedCategory = "ALL" },
                        label = { Text("All (${allLanguages.size})", fontSize = 12.sp) }
                    )
                    FilterChip(
                        selected = selectedCategory == "SCHEDULED",
                        onClick = { selectedCategory = "SCHEDULED" },
                        label = { Text("Primary (${LanguageRegistry.scheduledLanguages.size})", fontSize = 12.sp) }
                    )
                    FilterChip(
                        selected = selectedCategory == "DIALECTS",
                        onClick = { selectedCategory = "DIALECTS" },
                        label = { Text("Regional & Dialects (${LanguageRegistry.regionalDialects.size})", fontSize = 12.sp) }
                    )
                }

                // Languages List
                LazyColumn(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    contentPadding = PaddingValues(bottom = 8.dp)
                ) {
                    items(filteredLanguages, key = { it.code }) { lang ->
                        val isSelected = selectedCode.equals(lang.code, ignoreCase = true)
                        Surface(
                            onClick = { selectedCode = lang.code },
                            shape = RoundedCornerShape(16.dp),
                            color = if (isSelected) Color(0xFFECFDF5) else Color.White,
                            border = BorderStroke(
                                width = if (isSelected) 2.dp else 1.dp,
                                color = if (isSelected) MaterialTheme.colorScheme.primary else Color(0xFFE5E7EB)
                            ),
                            shadowElevation = if (isSelected) 4.dp else 1.dp,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(14.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                        Text(
                                            text = lang.nativeName,
                                            style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
                                        )
                                        Text(
                                            text = "• ${lang.name}",
                                            style = MaterialTheme.typography.bodyMedium.copy(color = Color.Gray)
                                        )
                                    }

                                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                        // Type badge
                                        Surface(
                                            shape = RoundedCornerShape(6.dp),
                                            color = if (lang.isDialect) Color(0xFFFEF3C7) else Color(0xFFDBEAFE)
                                        ) {
                                            Text(
                                                text = if (lang.isDialect) "Dialect of ${lang.parentLanguage?.uppercase() ?: "HI"}" else "Primary",
                                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                                                style = MaterialTheme.typography.labelSmall.copy(
                                                    fontSize = 10.sp,
                                                    fontWeight = FontWeight.SemiBold,
                                                    color = if (lang.isDialect) Color(0xFF92400E) else Color(0xFF1E40AF)
                                                )
                                            )
                                        }

                                        // Capability badge
                                        Text(
                                            text = lang.capabilityLabel,
                                            style = MaterialTheme.typography.labelSmall.copy(
                                                fontSize = 10.sp,
                                                color = if (lang.supportTier == 1) Color(0xFF047857) else Color(0xFF6B7280),
                                                fontWeight = FontWeight.Medium
                                            )
                                        )
                                    }
                                }

                                if (isSelected) {
                                    Surface(shape = CircleShape, color = MaterialTheme.colorScheme.primary, modifier = Modifier.size(24.dp)) {
                                        Box(contentAlignment = Alignment.Center) {
                                            Icon(Icons.Rounded.Check, contentDescription = "Selected", tint = Color.White, modifier = Modifier.size(16.dp))
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Confirm / Apply Button
                Button(
                    onClick = {
                        val chosen = LanguageRegistry.findByCode(selectedCode) ?: LanguageRegistry.scheduledLanguages.first()
                        val primaryLang = if (chosen.isDialect) (chosen.parentLanguage ?: "hi") else chosen.code
                        val dialect = if (chosen.isDialect) chosen.code else null

                        isSaving = true
                        AuthStore.saveLanguageAndDialect(context, primaryLang, dialect)
                        LocaleHelper.wrap(context, primaryLang)

                        coroutineScope.launch {
                            try {
                                val token = AuthStore.getAuthToken(context)
                                if (!token.isNullOrBlank()) {
                                    userViewModel.updateLanguage(token, chosen.code) { _, _ -> }
                                }
                            } catch (_: Exception) {}
                            finally {
                                isSaving = false
                                // NOTE: popBackStack() did nothing because this is the first
                                // screen shown — there's no prior screen to pop back to.
                                // Navigate to home explicitly instead, and clear this screen
                                // (and anything before it) off the back stack so the user
                                // can't press "back" and land here again.
                                navController.navigate("home") {
                                    popUpTo(0) { inclusive = true }
                                    launchSingleTop = true
                                }
                            }
                        }
                    },
                    enabled = !isSaving,
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary),
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(52.dp)
                ) {
                    if (isSaving) {
                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                    } else {
                        val chosenName = LanguageRegistry.findByCode(selectedCode)?.displayTitle ?: "Selected Language"
                        Text("Apply $chosenName", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    }
                }
            }
        }
    }
}