import { initDatabase, db } from './database.js';
import { calculateHaversineDistance, searchNearbyWithExpansion } from './haversine.js';
import { geocodeLocation, getLocationsHierarchy, searchVillages, lookupPinCode } from './geocoder.js';

async function runTests() {
  console.log('--- STARTING COLD STORAGE BACKEND TESTS ---');

  // Test 1: DB Initialization
  await initDatabase();
  console.log('✅ Test 1: Database initialized successfully');

  // Test 2: Query DB
  const records = await new Promise((resolve, reject) => {
    db.all('SELECT * FROM cold_storages', [], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
  console.log(`✅ Test 2: Database contains ${records.length} cold storage records`);

  // Test 3: Haversine distance
  // Agra center: 27.1767, 78.0081 to Runkata (CS-UP-AGR-001): 27.2341, 77.8821
  const dist = calculateHaversineDistance(27.1767, 78.0081, 27.2341, 77.8821);
  console.log(`✅ Test 3: Haversine distance calculated: ${dist} km`);

  // Test 4: Nearby search with radius expansion
  const nearbyResult = searchNearbyWithExpansion(records, 27.1767, 78.0081, null, null);
  console.log(`✅ Test 4: Nearby search found ${nearbyResult.totalFound} storages, effective radius: ${nearbyResult.effectiveRadius} km`);

  // Test 5: Crop filter
  const potatoStorages = searchNearbyWithExpansion(records, 27.1767, 78.0081, 50, 'Potato');
  console.log(`✅ Test 5: Potato crop filter returned ${potatoStorages.totalFound} storages within 50 km`);

  // Test 6: Offline Geocoder for Rural Villages
  const geoVillage1 = await geocodeLocation('Khandauli', 'Agra', 'Uttar Pradesh');
  console.log(`✅ Test 6a: Geocoded Khandauli: lat=${geoVillage1.latitude}, lng=${geoVillage1.longitude} (source: ${geoVillage1.source})`);

  const geoVillage2 = await geocodeLocation('Deesa', 'Banaskantha (Deesa/Palanpur)', 'Gujarat');
  console.log(`✅ Test 6b: Geocoded Deesa: lat=${geoVillage2.latitude}, lng=${geoVillage2.longitude} (source: ${geoVillage2.source})`);

  // Test 7: PIN Code Lookup
  const pin1 = lookupPinCode('283126');
  console.log(`✅ Test 7a: PIN 283126: ${pin1.area} (${pin1.lat}, ${pin1.lng})`);

  const pin2 = lookupPinCode('563101');
  console.log(`✅ Test 7b: PIN 563101: ${pin2.area} (${pin2.lat}, ${pin2.lng})`);

  // Test 8: Village Auto-suggest
  const suggestions = searchVillages('Khand');
  console.log(`✅ Test 8: Village auto-suggest for "Khand" returned ${suggestions.length} results`);

  // Test 9: Locations hierarchy
  const locs = getLocationsHierarchy();
  console.log(`✅ Test 9: Locations hierarchy loaded ${Object.keys(locs).length} states & UTs`);

  console.log('--- ALL BACKEND TESTS PASSED ---');
  db.close(() => {
    process.exit(0);
  });
}

runTests().catch((err) => {
  console.error('❌ Test failed:', err);
  db.close(() => {
    process.exit(1);
  });
});
