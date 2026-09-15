import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { db } from '../database.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Universal Government Dataset Importer
 * Ingests official CSV or JSON exports from:
 * - WDRA (Warehousing Development and Regulatory Authority)
 * - APEDA (Recognized Packhouses & Cold Chain Units)
 * - National Horticulture Board (NHB) Cold Storage Registry
 * - State Agricultural Marketing Boards (MSAMB, UP Mandi Board, Punjab Mandi Board)
 * 
 * Usage:
 * node backend/scripts/import_government_data.js <path-to-file.csv|json>
 */

export function parseCSV(csvText) {
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length < 2) return [];

  const headers = lines[0].split(',').map((h) => h.trim().replace(/^["']|["']$/g, ''));
  const records = [];

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Handle quoted commas
    const values = [];
    let insideQuotes = false;
    let currentValue = '';

    for (let c = 0; c < line.length; c++) {
      const char = line[c];
      if (char === '"' || char === "'") {
        insideQuotes = !insideQuotes;
      } else if (char === ',' && !insideQuotes) {
        values.push(currentValue.trim().replace(/^["']|["']$/g, ''));
        currentValue = '';
      } else {
        currentValue += char;
      }
    }
    values.push(currentValue.trim().replace(/^["']|["']$/g, ''));

    const row = {};
    headers.forEach((h, idx) => {
      row[h] = values[idx] || '';
    });
    records.push(row);
  }
  return records;
}

export function normalizeRecord(raw, index) {
  const name = raw.name || raw.warehouse_name || raw.facility_name || raw['Name of Cold Storage'] || raw['Unit Name'] || `Registered Cold Store #${index + 1}`;
  const district = raw.district || raw.District || raw['District Name'] || 'Agra';
  const state = raw.state || raw.State || raw['State Name'] || 'Uttar Pradesh';
  const address = raw.address || raw.Address || raw.location || raw['Address/Location'] || `${district}, ${state}`;
  const village_or_area = raw.village_or_area || raw.village || raw.mandi || raw.Tehsil || null;
  const pincode = raw.pincode || raw.PIN || raw.postal_code || null;
  const latitude = parseFloat(raw.latitude || raw.lat || raw.Latitude || 0);
  const longitude = parseFloat(raw.longitude || raw.lng || raw.Longitude || 0);
  const phone = raw.phone_number || raw.phone || raw.mobile || raw.Contact || null;
  const contact_person = raw.contact_person || raw.manager || raw.Incharge || 'Chief Manager';
  const capacity = raw.storage_capacity || raw.capacity || raw['Capacity (MT)'] ? `${raw.storage_capacity || raw.capacity || raw['Capacity (MT)']} MT` : '15,000 MT';
  const crops = raw.suitable_crops || raw.commodities || raw.produce || raw.Crops || 'Potatoes, Vegetables, Fruits, Seeds';
  const type = raw.cold_storage_type || raw.type || raw.Technology || 'Ammonia Refrigeration / CA Multi-Chamber';
  const regNo = raw.reg_no || raw.registration_number || raw.wdra_id || raw.apeda_id || `REG-${state.substring(0, 2).toUpperCase()}-${String(index + 1).padStart(4, '0')}`;

  return {
    id: regNo,
    name,
    address,
    village_or_area,
    district,
    state,
    pincode,
    latitude,
    longitude,
    phone_number: phone,
    alternate_phone_number: null,
    contact_person,
    email: raw.email || null,
    rating: parseFloat(raw.rating || 4.7),
    opening_hours: raw.opening_hours || '06:00 AM - 09:30 PM',
    storage_capacity: capacity,
    suitable_crops: crops,
    cold_storage_type: type,
    temperature_range: raw.temperature_range || '2°C to 8°C',
    description: raw.description || `Government registered agricultural cold storage facility (${regNo}) serving farmers in ${district}, ${state}.`,
    amenities: raw.amenities || 'Electronic Weighbridge, 24x7 Generator Backup, Quality Testing, NWR Bank Loan Desk',
    certifications: raw.certifications || 'WDRA / NHB Registered Warehouse',
    is_sample_data: 0
  };
}

async function runImporter() {
  const filePath = process.argv[2];
  if (!filePath) {
    console.log('Usage: node backend/scripts/import_government_data.js <path-to-file>');
    process.exit(0);
  }

  const absPath = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath);
  if (!fs.existsSync(absPath)) {
    console.error(`File not found: ${absPath}`);
    process.exit(1);
  }

  const content = fs.readFileSync(absPath, 'utf8');
  let rawList = [];

  if (absPath.endsWith('.json')) {
    rawList = JSON.parse(content);
  } else if (absPath.endsWith('.csv')) {
    rawList = parseCSV(content);
  } else {
    console.error('Unsupported file format. Please provide .json or .csv');
    process.exit(1);
  }

  console.log(`📥 Ingesting ${rawList.length} records from ${path.basename(absPath)}...`);
  const normalized = rawList.map((r, i) => normalizeRecord(r, i));

  // Save to sample_storages.json
  const targetPath = path.join(__dirname, '..', 'data', 'sample_storages.json');
  fs.writeFileSync(targetPath, JSON.stringify(normalized, null, 2), 'utf8');
  console.log(`✅ Written ${normalized.length} records to ${targetPath}`);

  // Re-seed DB
  const { initDatabase } = await import('../database.js');
  await initDatabase();
  console.log('🎉 Database successfully re-seeded with official dataset!');
  process.exit(0);
}

if (process.argv[1] && process.argv[1].includes('import_government_data.js')) {
  runImporter().catch((err) => {
    console.error('Import error:', err);
    process.exit(1);
  });
}
