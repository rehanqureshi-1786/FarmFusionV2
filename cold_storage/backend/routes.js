import express from 'express';
import { db } from './database.js';
import { searchNearbyWithExpansion, calculateHaversineDistance } from './haversine.js';
import { geocodeLocation, getLocationsHierarchy, searchVillages, lookupPinCode } from './geocoder.js';

const router = express.Router();

/**
 * 1. Find Nearby Cold Storage
 * GET /cold-storages/nearby or GET /api/cold-storages/nearby
 * Query Params: latitude, longitude, radius (optional), crop (optional)
 */
router.get(['/cold-storages/nearby', '/api/cold-storages/nearby'], (req, res) => {
  const { latitude, longitude, radius, crop } = req.query;

  if (!latitude || !longitude) {
    return res.status(400).json({
      error: 'Missing required parameters',
      message: 'Both latitude and longitude are required for nearby search.'
    });
  }

  const userLat = parseFloat(latitude);
  const userLng = parseFloat(longitude);

  if (isNaN(userLat) || isNaN(userLng)) {
    return res.status(400).json({
      error: 'Invalid coordinates',
      message: 'Latitude and Longitude must be valid decimal numbers.'
    });
  }

  db.all('SELECT * FROM cold_storages', [], (err, rows) => {
    if (err) {
      console.error('Database query error:', err);
      return res.status(500).json({ error: 'Database error', message: err.message });
    }

    const searchResult = searchNearbyWithExpansion(rows, userLat, userLng, radius, crop);

    return res.json({
      success: true,
      origin: {
        latitude: userLat,
        longitude: userLng
      },
      searchRadiusKm: searchResult.effectiveRadius,
      autoExpanded: searchResult.autoExpanded,
      count: searchResult.totalFound,
      results: searchResult.storages
    });
  });
});

/**
 * 2. Search by District
 * GET /cold-storages/district or GET /api/cold-storages/district
 * Query Params: state, district, crop (optional)
 */
router.get(['/cold-storages/district', '/api/cold-storages/district'], (req, res) => {
  const { state, district, crop } = req.query;

  if (!state || !district) {
    return res.status(400).json({
      error: 'Missing required parameters',
      message: 'Both state and district are required.'
    });
  }

  // Handle fuzzy matching for district names (e.g., "Jaipur" matching "Jaipur (Jaipur North & South)")
  const cleanDist = district.trim().toLowerCase();
  const cleanState = state.trim().toLowerCase();

  db.all('SELECT * FROM cold_storages', [], (err, rows) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: 'Database error', message: err.message });
    }

    let filtered = rows.filter((r) => {
      const rState = (r.state || '').toLowerCase();
      const rDist = (r.district || '').toLowerCase();

      const stateMatch = rState === cleanState || rState.includes(cleanState) || cleanState.includes(rState);
      const distMatch = rDist === cleanDist || rDist.includes(cleanDist) || cleanDist.includes(rDist);

      return stateMatch && distMatch;
    });

    if (crop && crop.trim()) {
      const term = crop.trim().toLowerCase();
      filtered = filtered.filter((r) => r.suitable_crops && r.suitable_crops.toLowerCase().includes(term));
    }

    return res.json({
      success: true,
      state: state.trim(),
      district: district.trim(),
      count: filtered.length,
      results: filtered
    });
  });
});

/**
 * 3. Get Cold Storage Details
 * GET /cold-storages/:id or GET /api/cold-storages/:id
 */
router.get(['/cold-storages/:id', '/api/cold-storages/:id'], (req, res) => {
  const { id } = req.params;

  db.get('SELECT * FROM cold_storages WHERE id = ?', [id], (err, row) => {
    if (err) {
      console.error('Database error:', err);
      return res.status(500).json({ error: 'Database error', message: err.message });
    }

    if (!row) {
      return res.status(404).json({
        error: 'Not Found',
        message: `Cold storage with ID "${id}" was not found.`
      });
    }

    return res.json({
      success: true,
      cold_storage: row
    });
  });
});

/**
 * 4. Get Available States and Districts
 * GET /api/locations
 */
router.get(['/locations', '/api/locations'], (req, res) => {
  try {
    const locations = getLocationsHierarchy();
    res.json({
      success: true,
      states: locations
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to retrieve locations', message: err.message });
  }
});

/**
 * 5. Geocode Manual Location / Village
 * GET /api/geocode
 * Query Params: address, district, state
 */
router.get(['/geocode', '/api/geocode'], async (req, res) => {
  const { address, district, state } = req.query;

  if (!state && !district && !address) {
    return res.status(400).json({
      error: 'Missing parameters',
      message: 'Please provide at least a state, district, or address/village/pincode.'
    });
  }

  try {
    const geo = await geocodeLocation(address, district, state);
    res.json({
      success: true,
      location: geo
    });
  } catch (err) {
    res.status(500).json({
      error: 'Geocoding failed',
      message: err.message
    });
  }
});

/**
 * 6. Rural Village, Mandi & Tehsil Auto-Suggest
 * GET /api/villages
 * Query Params: q (search term), state (optional), district (optional)
 */
router.get(['/villages', '/api/villages'], (req, res) => {
  const { q, query, state, district } = req.query;
  const searchTerm = (q || query || '').trim();

  try {
    const suggestions = searchVillages(searchTerm, state, district);
    res.json({
      success: true,
      count: suggestions.length,
      suggestions
    });
  } catch (err) {
    res.status(500).json({
      error: 'Village lookup failed',
      message: err.message
    });
  }
});

/**
 * 7. Postal PIN Code Lookup
 * GET /api/pincode/:pin
 */
router.get(['/pincode/:pin', '/api/pincode/:pin'], (req, res) => {
  const { pin } = req.params;
  const result = lookupPinCode(pin);

  if (result.success) {
    res.json(result);
  } else {
    res.status(404).json({
      error: 'PIN Not Found',
      message: `No coordinate record found for PIN ${pin}.`
    });
  }
});

/**
 * 8. Import Official Government Dataset (JSON/CSV records)
 * POST /api/cold-storages/import
 */
router.post(['/cold-storages/import', '/api/cold-storages/import'], async (req, res) => {

  const records = req.body;
  if (!Array.isArray(records) || records.length === 0) {
    return res.status(400).json({
      error: 'Invalid Payload',
      message: 'Expected an array of cold storage records to import.'
    });
  }

  const stmt = db.prepare(`
    INSERT OR REPLACE INTO cold_storages (
      id, name, address, village_or_area, district, state, pincode,
      latitude, longitude, phone_number, alternate_phone_number,
      contact_person, email, rating, opening_hours, storage_capacity,
      suitable_crops, cold_storage_type, temperature_range,
      description, amenities, certifications, is_sample_data
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  db.serialize(() => {
    records.forEach((item, index) => {
      stmt.run([
        item.id || `REG-${(item.state || 'IN').substring(0, 2).toUpperCase()}-${String(index + 1).padStart(4, '0')}`,
        item.name,
        item.address || `${item.district}, ${item.state}`,
        item.village_or_area || null,
        item.district,
        item.state,
        item.pincode || null,
        parseFloat(item.latitude || 0),
        parseFloat(item.longitude || 0),
        item.phone_number || null,
        item.alternate_phone_number || null,
        item.contact_person || 'Chief Manager',
        item.email || null,
        parseFloat(item.rating || 4.7),
        item.opening_hours || '06:00 AM - 09:30 PM',
        item.storage_capacity || null,
        item.suitable_crops || null,
        item.cold_storage_type || null,
        item.temperature_range || null,
        item.description || null,
        item.amenities || null,
        item.certifications || 'WDRA / NHB Registered',
        item.is_sample_data ?? 0
      ]);
    });

    stmt.finalize((err) => {
      if (err) {
        return res.status(500).json({ error: 'Import failed', message: err.message });
      }
      res.json({
        success: true,
        message: `Successfully imported ${records.length} registered cold storage records.`,
        importedCount: records.length
      });
    });
  });
});

export default router;

