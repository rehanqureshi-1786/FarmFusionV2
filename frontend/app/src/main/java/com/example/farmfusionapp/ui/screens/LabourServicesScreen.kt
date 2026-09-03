package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.example.farmfusionapp.R

// ---------------------------------------------------------------------------
// Colors used only on this screen
// ---------------------------------------------------------------------------
private val LabourGreen = Color(0xFF34A853)
private val LabourGreenDark = Color(0xFF1B5E20)
private val LabourBlue = Color(0xFF1565C0)
private val LabourOrange = Color(0xFFF57C00)
private val LabourPageBackground = Color(0xFFFAFCFA)
private val LabourSubtitleGray = Color(0xFF6E6E6E)
private val LabourFootnoteGray = Color(0xFF9A9A9A)

private val GreenCardBg = Color(0xFFEDF8EE)
private val GreenCardBorder = Color(0xFFCFEBD1)
private val GreenPillBg = Color(0xFFDCF0DD)

private val BlueCardBg = Color(0xFFEDF5FF)
private val BlueCardBorder = Color(0xFFC9E1FB)
private val BluePillBg = Color(0xFFD9EAFC)

data class LabourJob(
    val title: String,
    val location: String,
    val workersNeeded: String,
    val price: String,
    val date: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LabourServicesScreen(navController: NavController) {
    var showHiringForm by remember { mutableStateOf(false) }
    var showGetWork by remember { mutableStateOf(false) }

    // Shared state for demo (In real app, this would be in a ViewModel/Database)
    val jobsList = remember {
        mutableStateListOf(
            LabourJob("Wheat Harvesting", "North Farm", "5", "₹500/day", "Today"),
            LabourJob("Soil Preparation", "East Field", "2", "₹450/day", "Tomorrow"),
            LabourJob("Fertilizer Spray", "Main Orchard", "3", "₹600/day", "Monday")
        )
    }

    val onLandingScreen = !showHiringForm && !showGetWork

    Scaffold(
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Text(
                        "Labour Service",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = LabourGreen
                    )
                },
                navigationIcon = {
                    IconButton(onClick = {
                        if (showHiringForm || showGetWork) {
                            showHiringForm = false
                            showGetWork = false
                        } else {
                            navController.popBackStack()
                        }
                    }) {
                        Icon(
                            Icons.AutoMirrored.Rounded.ArrowBack,
                            contentDescription = "Back",
                            tint = Color(0xFF1B1B1B)
                        )
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color.White
                )
            )
        },
        containerColor = if (onLandingScreen) LabourPageBackground else Color(0xFFF6F8F6)
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when {
                showHiringForm -> LabourHiringForm(
                    onJobPosted = { newJob ->
                        jobsList.add(0, newJob)
                        showHiringForm = false
                        showGetWork = true // Show the list after posting
                    }
                )
                showGetWork -> GetWorkScreen(jobsList)
                else -> LabourSelectionScreen(
                    onHire = { showHiringForm = true },
                    onGetWork = { showGetWork = true }
                )
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Landing screen
// ---------------------------------------------------------------------------
@Composable
fun LabourSelectionScreen(onHire: () -> Unit, onGetWork: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(bottom = 24.dp)
    ) {
        HeroSection()

        Spacer(Modifier.height(28.dp))

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            ServiceOptionCard(
                modifier = Modifier.weight(1f),
                title = "Hire Labour",
                description = "Find skilled and reliable workers for your farm.",
                icon = Icons.Rounded.PersonAdd,
                accentColor = LabourGreenDark,
                cardBackground = GreenCardBg,
                cardBorder = GreenCardBorder,
                pillBackground = GreenPillBg,
                pillIcon = Icons.Rounded.Eco,
                pillText = "FOR FARMERS",
                onClick = onHire
            )
            ServiceOptionCard(
                modifier = Modifier.weight(1f),
                title = "Get Work",
                description = "Find nearby job opportunities and earn daily.",
                icon = Icons.Rounded.Search,
                accentColor = LabourBlue,
                cardBackground = BlueCardBg,
                cardBorder = BlueCardBorder,
                pillBackground = BluePillBg,
                pillIcon = Icons.Rounded.Groups,
                pillText = "FOR WORKERS",
                onClick = onGetWork
            )
        }

        Spacer(Modifier.height(20.dp))

        TrustBadgesSection(modifier = Modifier.padding(horizontal = 20.dp))
    }
}

@Composable
private fun HeroSection() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
            .padding(top = 20.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "Find Trusted Help,",
                fontSize = 26.sp,
                lineHeight = 32.sp,
                fontWeight = FontWeight.ExtraBold,
                color = Color(0xFF1B1B1B)
            )
            Text(
                text = "Get Work Done.",
                fontSize = 26.sp,
                lineHeight = 32.sp,
                fontWeight = FontWeight.ExtraBold,
                color = LabourGreen
            )

            Spacer(Modifier.height(10.dp))

            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .width(22.dp)
                        .height(3.dp)
                        .background(LabourGreen, RoundedCornerShape(50))
                )
                Spacer(Modifier.width(5.dp))
                Box(
                    modifier = Modifier
                        .size(4.dp)
                        .background(LabourGreen, CircleShape)
                )
            }

            Spacer(Modifier.height(10.dp))

            Text(
                text = "Hire skilled labour or find daily work quickly and easily.",
                fontSize = 14.sp,
                lineHeight = 20.sp,
                color = LabourSubtitleGray
            )
        }

        Spacer(Modifier.width(12.dp))

        Box(
            modifier = Modifier
                .weight(0.85f)
                .aspectRatio(0.95f),
            contentAlignment = Alignment.Center
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize(0.9f)
                    .background(
                        color = Color(0xFFF2F3F6),
                        shape = RoundedCornerShape(
                            topStart = 60.dp,
                            topEnd = 30.dp,
                            bottomStart = 30.dp,
                            bottomEnd = 60.dp
                        )
                    )
            )
            Image(
                painter = painterResource(id = R.drawable.ill_labour_help), // Adjust resource if needed
                contentDescription = "Farmer and employer shaking hands",
                modifier = Modifier.fillMaxSize(0.88f),
                contentScale = ContentScale.Fit
            )
        }
    }
}

@Composable
private fun ServiceOptionCard(
    modifier: Modifier = Modifier,
    title: String,
    description: String,
    icon: ImageVector,
    accentColor: Color,
    cardBackground: Color,
    cardBorder: Color,
    pillBackground: Color,
    pillIcon: ImageVector,
    pillText: String,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(24.dp),
        color = cardBackground,
        border = BorderStroke(1.dp, cardBorder)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.Start
        ) {
            Box(
                modifier = Modifier
                    .size(46.dp)
                    .background(Color.White, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    icon,
                    contentDescription = null,
                    tint = accentColor,
                    modifier = Modifier.size(24.dp)
                )
            }

            Spacer(Modifier.height(12.dp))

            Text(
                text = title,
                fontSize = 18.sp,
                fontWeight = FontWeight.ExtraBold,
                color = accentColor
            )

            Spacer(Modifier.height(5.dp))

            Box(
                modifier = Modifier
                    .width(20.dp)
                    .height(3.dp)
                    .background(accentColor, RoundedCornerShape(50))
            )

            Spacer(Modifier.height(8.dp))

            Text(
                text = description,
                fontSize = 12.5.sp,
                lineHeight = 16.sp,
                color = LabourSubtitleGray
            )

            Spacer(Modifier.height(14.dp))

            Row(
                modifier = Modifier
                    .background(pillBackground, RoundedCornerShape(50))
                    .padding(horizontal = 12.dp, vertical = 7.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    pillIcon,
                    contentDescription = null,
                    tint = accentColor,
                    modifier = Modifier.size(14.dp)
                )
                Spacer(Modifier.width(6.dp))
                Text(
                    text = pillText,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.4.sp,
                    color = accentColor
                )
            }
        }
    }
}

@Composable
private fun TrustBadgesSection(modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        border = BorderStroke(1.dp, Color(0xFFEFEFEF))
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 18.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            TrustBadgeItem(
                modifier = Modifier.weight(1f),
                icon = Icons.Rounded.VerifiedUser,
                iconColor = LabourGreen,
                title = "Verified Workers",
                description = "Safe & secure connections"
            )
            TrustBadgeItem(
                modifier = Modifier.weight(1f),
                icon = Icons.Rounded.LocationOn,
                iconColor = LabourOrange,
                title = "Local Opportunities",
                description = "Jobs and workers near you"
            )
            TrustBadgeItem(
                modifier = Modifier.weight(1f),
                icon = Icons.Rounded.Lock,
                iconColor = LabourBlue,
                title = "Secure Payments",
                description = "Trusted and protected"
            )
        }
    }
}

@Composable
private fun TrustBadgeItem(
    modifier: Modifier = Modifier,
    icon: ImageVector,
    iconColor: Color,
    title: String,
    description: String
) {
    Column(modifier = modifier) {
        Icon(
            icon,
            contentDescription = null,
            tint = iconColor,
            modifier = Modifier.size(18.dp)
        )
        Spacer(Modifier.height(6.dp))
        Text(
            text = title,
            fontSize = 12.sp,
            lineHeight = 14.sp,
            fontWeight = FontWeight.Bold,
            color = iconColor
        )
        Spacer(Modifier.height(2.dp))
        Text(
            text = description,
            fontSize = 10.5.sp,
            lineHeight = 13.sp,
            color = LabourFootnoteGray
        )
    }
}

// ---------------------------------------------------------------------------
// Hiring form
// ---------------------------------------------------------------------------
@Composable
fun LabourHiringForm(onJobPosted: (LabourJob) -> Unit) {
    var details by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("") }
    var count by remember { mutableStateOf("") }
    var price by remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text("Hire Workers", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold))
        Text("मजदूरों के लिए जानकारी भरें", color = LabourGreen)

        OutlinedTextField(
            value = details, onValueChange = { details = it },
            label = { Text("What work? (e.g. Rice Sowing)") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp)
        )

        OutlinedTextField(
            value = location, onValueChange = { location = it },
            label = { Text("Farm Location") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp)
        )

        OutlinedTextField(
            value = count, onValueChange = { count = it },
            label = { Text("How many workers needed?") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        OutlinedTextField(
            value = price, onValueChange = { price = it },
            label = { Text("Pay per day (₹)") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )

        Spacer(Modifier.weight(1f))

        Button(
            onClick = {
                if (details.isNotBlank() && location.isNotBlank()) {
                    onJobPosted(LabourJob(details, location, count, "₹$price/day", "Just now"))
                }
            },
            modifier = Modifier.fillMaxWidth().height(80.dp),
            shape = RoundedCornerShape(24.dp),
            colors = ButtonDefaults.buttonColors(containerColor = LabourGreenDark)
        ) {
            Text("POST JOB", fontWeight = FontWeight.Black, fontSize = 22.sp, color = Color.White)
        }
    }
}

// ---------------------------------------------------------------------------
// Work List Design
// ---------------------------------------------------------------------------
@Composable
fun GetWorkScreen(jobs: List<LabourJob>) {
    Column(modifier = Modifier.fillMaxSize()) {
        Text(
            text = "Available Work Near You",
            style = MaterialTheme.typography.titleLarge.copy(
                fontWeight = FontWeight.Bold,
                color = Color(0xFF1B1B1B)
            ),
            // FIXED: Fully explicit arguments
            modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 20.dp)
        )

        Row(
            verticalAlignment = Alignment.CenterVertically,
            // FIXED: Fully explicit arguments
            modifier = Modifier.padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 4.dp)
        ) {
            Box(
                modifier = Modifier
                    .width(28.dp)
                    .height(4.dp)
                    .background(LabourGreen, RoundedCornerShape(2.dp))
            )
            Spacer(modifier = Modifier.width(4.dp))
            Box(
                modifier = Modifier
                    .size(4.dp)
                    .background(LabourGreen, CircleShape)
            )
        }

        Text(
            text = "आपके आस-पास उपलब्ध काम",
            color = LabourGreen,
            fontWeight = FontWeight.Medium,
            fontSize = 14.sp,
            modifier = Modifier.padding(horizontal = 20.dp) // Only horizontal is fine!
        )

        Spacer(Modifier.height(20.dp))

        LazyColumn(
            // FIXED: Fully explicit arguments
            contentPadding = PaddingValues(start = 20.dp, end = 20.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            modifier = Modifier.fillMaxSize()
        ) {
            items(jobs) { job ->
                JobCard(job)
            }
        }
    }
}

@Composable
fun JobCard(job: LabourJob) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        color = Color.White,
        shadowElevation = 2.dp,
        border = BorderStroke(1.dp, Color(0xFFF0F0F0))
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .background(GreenCardBg, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Rounded.Work,
                        contentDescription = null,
                        tint = LabourGreenDark
                    )
                }
                Spacer(Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = job.title,
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFF1B1B1B)
                        )
                    )
                    Text(
                        text = job.location,
                        style = MaterialTheme.typography.bodySmall.copy(color = Color.Gray)
                    )
                }
                Text(
                    text = job.price,
                    fontWeight = FontWeight.Black,
                    color = LabourGreenDark,
                    fontSize = 17.sp
                )
            }

            HorizontalDivider(
                modifier = Modifier.padding(vertical = 16.dp),
                thickness = 1.dp,
                color = Color(0xFFF5F5F5)
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Rounded.People,
                        contentDescription = null,
                        tint = LabourGreen,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        text = "Needed: ${job.workersNeeded} Workers",
                        style = MaterialTheme.typography.labelMedium.copy(color = Color(0xFF444444))
                    )
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Rounded.CalendarToday,
                        contentDescription = null,
                        tint = LabourGreen,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(Modifier.width(6.dp))
                    Text(
                        text = job.date,
                        style = MaterialTheme.typography.labelMedium.copy(color = Color(0xFF444444))
                    )
                }
            }

            Spacer(Modifier.height(16.dp))

            OutlinedButton(
                onClick = { /* Contact Farmer */ },
                modifier = Modifier.fillMaxWidth().height(48.dp),
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, LabourGreen),
                colors = ButtonDefaults.outlinedButtonColors(
                    containerColor = Color.White,
                    contentColor = LabourGreen
                )
            ) {
                Icon(
                    imageVector = Icons.Rounded.Call,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = "Contact Farmer",
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 14.sp
                )
            }
        }
    }
}