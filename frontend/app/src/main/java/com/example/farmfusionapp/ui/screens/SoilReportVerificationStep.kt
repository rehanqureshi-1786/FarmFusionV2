package com.example.farmfusionapp.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.Refresh
import androidx.compose.material.icons.rounded.WarningAmber
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.farmfusionapp.R
import com.example.farmfusionapp.data.soilreport.SoilReportOcrParser
import com.example.farmfusionapp.viewmodel.CropRecommendationViewModel

/**
 * Soil Report Verification step (Flow B — "I Have Soil Report").
 *
 * Displays N/P/K/pH extracted by on-device OCR, prefilled where detection
 * succeeded. Every field stays editable; editing a field marks it as
 * farmer-entered. Missing values show a warning and block confirmation.
 * No value is ever invented — missing fields must be typed by the farmer.
 */
@Composable
fun SoilReportVerificationStep(
    onConfirm: (SoilReportOcrParser.ParsedSoilValues) -> Unit,
    onScanAgain: () -> Unit,
    onCancel: () -> Unit,
    viewModel: CropRecommendationViewModel = viewModel()
) {
    val ocrValues by viewModel.ocrParsedValues

    // Editable fields prefilled with OCR results when available.
    var nitrogenText by remember(ocrValues) {
        mutableStateOf(ocrValues?.nitrogen?.value?.toString() ?: "")
    }
    var phosphorusText by remember(ocrValues) {
        mutableStateOf(ocrValues?.phosphorus?.value?.toString() ?: "")
    }
    var potassiumText by remember(ocrValues) {
        mutableStateOf(ocrValues?.potassium?.value?.toString() ?: "")
    }
    var phText by remember(ocrValues) {
        mutableStateOf(ocrValues?.ph?.value?.toString() ?: "")
    }

    // A field is OCR-sourced only while it has not been touched by the farmer.
    var nitrogenEdited by remember { mutableStateOf(false) }
    var phosphorusEdited by remember { mutableStateOf(false) }
    var potassiumEdited by remember { mutableStateOf(false) }
    var phEdited by remember { mutableStateOf(false) }

    fun sourceOf(ocr: SoilReportOcrParser.ParsedValue?, edited: Boolean): SoilReportOcrParser.Source =
        if (ocr != null && !edited) SoilReportOcrParser.Source.OCR
        else SoilReportOcrParser.Source.MANUAL

    // Validation: N/P/K > 0, pH within 0..14.
    val nitrogenError = nitrogenText.toDoubleOrNull()?.let { if (it <= 0) "Must be > 0" else null }
    val phosphorusError = phosphorusText.toDoubleOrNull()?.let { if (it <= 0) "Must be > 0" else null }
    val potassiumError = potassiumText.toDoubleOrNull()?.let { if (it <= 0) "Must be > 0" else null }
    val phError = phText.toDoubleOrNull()?.let { if (it < 0.0 || it > 14.0) "Must be 0-14" else null }

    val allValid = nitrogenText.isNotBlank() && phosphorusText.isNotBlank() &&
            potassiumText.isNotBlank() && phText.isNotBlank() &&
            nitrogenError == null && phosphorusError == null &&
            potassiumError == null && phError == null

    val missingValues = buildList {
        if (nitrogenText.isBlank()) add("N")
        if (phosphorusText.isBlank()) add("P")
        if (potassiumText.isBlank()) add("K")
        if (phText.isBlank()) add("pH")
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = stringResource(R.string.verify_soil_report_title),
            style = MaterialTheme.typography.headlineMedium.copy(fontWeight = FontWeight.Bold)
        )
        Text(
            text = stringResource(R.string.verify_soil_report_subtitle),
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        // Warning for values OCR could not detect
        if (missingValues.isNotEmpty()) {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                color = MaterialTheme.colorScheme.errorContainer,
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.error)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Rounded.WarningAmber,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.error
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        text = stringResource(
                            R.string.missing_values_warning,
                            missingValues.joinToString(", ")
                        ),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                }
            }
        }

        SoilValueInputField(
            label = stringResource(R.string.nitrogen_label),
            value = nitrogenText,
            onValueChange = { nitrogenText = it; nitrogenEdited = true },
            unit = "kg/ha",
            error = nitrogenError,
            source = sourceOf(ocrValues?.nitrogen, nitrogenEdited)
        )
        SoilValueInputField(
            label = stringResource(R.string.phosphorus_label),
            value = phosphorusText,
            onValueChange = { phosphorusText = it; phosphorusEdited = true },
            unit = "kg/ha",
            error = phosphorusError,
            source = sourceOf(ocrValues?.phosphorus, phosphorusEdited)
        )
        SoilValueInputField(
            label = stringResource(R.string.potassium_label),
            value = potassiumText,
            onValueChange = { potassiumText = it; potassiumEdited = true },
            unit = "kg/ha",
            error = potassiumError,
            source = sourceOf(ocrValues?.potassium, potassiumEdited)
        )
        SoilValueInputField(
            label = stringResource(R.string.ph_label),
            value = phText,
            onValueChange = { phText = it; phEdited = true },
            unit = "0 - 14",
            error = phError,
            source = sourceOf(ocrValues?.ph, phEdited),
            keyboardType = KeyboardType.Decimal
        )
        Spacer(Modifier.height(8.dp))


        // Action buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            OutlinedButton(
                onClick = onScanAgain,
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(16.dp)
            ) {
                Icon(Icons.Rounded.Refresh, contentDescription = null, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text(stringResource(R.string.scan_again))
            }

            Button(
                onClick = {
                    fun field(
                        text: String,
                        ocr: SoilReportOcrParser.ParsedValue?,
                        edited: Boolean,
                        defaultUnit: String?
                    ): SoilReportOcrParser.ParsedValue? {
                        val v = text.toDoubleOrNull() ?: return null
                        return SoilReportOcrParser.ParsedValue(
                            value = v,
                            unit = ocr?.unit ?: defaultUnit,
                            rawText = text,
                            source = sourceOf(ocr, edited)
                        )
                    }
                    onConfirm(
                        SoilReportOcrParser.ParsedSoilValues(
                            nitrogen = field(nitrogenText, ocrValues?.nitrogen, nitrogenEdited, "kg/ha"),
                            phosphorus = field(phosphorusText, ocrValues?.phosphorus, phosphorusEdited, "kg/ha"),
                            potassium = field(potassiumText, ocrValues?.potassium, potassiumEdited, "kg/ha"),
                            ph = field(phText, ocrValues?.ph, phEdited, null)
                        )
                    )
                },
                enabled = allValid,
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(16.dp)
            ) {
                Icon(Icons.Rounded.CheckCircle, contentDescription = null, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text(stringResource(R.string.confirm_soil_values))
            }
        }
        Spacer(Modifier.height(8.dp))

        TextButton(onClick = onCancel, modifier = Modifier.align(Alignment.CenterHorizontally)) {
            Text(stringResource(R.string.cancel), fontWeight = FontWeight.Medium)
        }
    }
}

/**
 * Individual soil value input field with an OCR / farmer-entered source chip.
 */
@Composable
fun SoilValueInputField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    unit: String,
    error: String?,
    source: SoilReportOcrParser.Source,
    keyboardType: KeyboardType = KeyboardType.Number
) {
    Column(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(label, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Medium))
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = if (source == SoilReportOcrParser.Source.OCR)
                    MaterialTheme.colorScheme.primaryContainer
                else
                    MaterialTheme.colorScheme.secondaryContainer
            ) {
                Text(
                    stringResource(
                        if (source == SoilReportOcrParser.Source.OCR)
                            R.string.extracted_from_report
                        else
                            R.string.farmer_entered
                    ),
                    style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Medium),
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        }
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
            label = { Text(unit) },
            isError = error != null
        )
        if (error != null) {
            Text(
                text = error,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(start = 12.dp)
            )
        }
    }
}
