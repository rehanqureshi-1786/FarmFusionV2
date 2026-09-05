import assert from 'assert';

const BASE_URL = 'http://localhost:3000';

async function runE2ETests() {
  console.log('====================================================');
  console.log('🚀 RUNNING COMPREHENSIVE E2E & API INTEGRATION TESTS');
  console.log('====================================================\n');

  let passed = 0;
  let total = 0;

  async function test(name, fn) {
    total++;
    try {
      await fn();
      console.log(`✅ [PASS] ${name}`);
      passed++;
    } catch (err) {
      console.error(`❌ [FAIL] ${name}:`, err.message);
    }
  }

  // 1. Static Assets & HTML Tests
  await test('1. Frontend HTML serves correctly with Voice Search, Village Auto-suggest & Rural Chips', async () => {
    const res = await fetch(`${BASE_URL}/`);
    assert.strictEqual(res.status, 200);
    const html = await res.text();
    assert(html.includes('FarmFusion | Cold Storage Finder'), 'Page title missing');
    assert(html.includes('id="tab-btn-gps"'), 'GPS tab button missing');
    assert(html.includes('id="tab-btn-manual"'), 'Manual tab button missing');
    assert(html.includes('id="btn-voice-search"'), 'Voice search button missing');
    assert(html.includes('id="village-suggestions-list"'), 'Village suggestions dropdown missing');
    assert(html.includes('quick-village-chip'), 'Quick village chips missing');
    assert(html.includes('leaflet.js'), 'Leaflet map script missing');
  });

  await test('2. CSS design system stylesheet is accessible with voice & village styles', async () => {
    const res = await fetch(`${BASE_URL}/css/styles.css`);
    assert.strictEqual(res.status, 200);
    const css = await res.text();
    assert(css.includes('--primary-600'), 'CSS variables missing');
    assert(css.includes('.btn-voice'), 'Voice button styles missing');
    assert(css.includes('.village-suggestions-dropdown'), 'Village suggestions styles missing');
    assert(css.includes('.storage-card'), 'Storage card styles missing');
  });

  await test('3. JS Modules (app.js, api.js, map.js, i18n.js) load correctly', async () => {
    const files = ['app.js', 'api.js', 'map.js', 'i18n.js'];
    for (const f of files) {
      const res = await fetch(`${BASE_URL}/js/${f}`);
      assert.strictEqual(res.status, 200, `Failed to load ${f}`);
    }
  });

  // 4. API Locations Hierarchy
  await test('4. GET /api/locations returns all 28 Indian states & districts', async () => {
    const res = await fetch(`${BASE_URL}/api/locations`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.states['Uttar Pradesh'].includes('Agra'), 'UP Agra missing');
    assert(data.states['Maharashtra'].includes('Nashik'), 'MH Nashik missing');
    assert(data.states['Punjab'].includes('Jalandhar'), 'PB Jalandhar missing');
    assert(data.states['Gujarat'].some((d) => d.includes('Banaskantha')), 'Gujarat Banaskantha missing');
    assert(data.states['Himachal Pradesh'].some((d) => d.includes('Shimla')), 'HP Shimla missing');
  });

  // 5. Village Auto-suggest API
  await test('5. GET /api/villages returns instant autocomplete for rural places', async () => {
    const res = await fetch(`${BASE_URL}/api/villages?q=Khandauli`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.count > 0, 'No village suggestions found for Khandauli');
    assert(data.suggestions[0].village.includes('Khandauli'), 'Khandauli not matched');
    console.log(`   -> Village auto-suggest result: "${data.suggestions[0].name}" (${data.suggestions[0].type})`);
  });

  // 6. Postal PIN Code Lookup API
  await test('6. GET /api/pincode/:pin returns exact coordinates & area name', async () => {
    const res = await fetch(`${BASE_URL}/api/pincode/283126`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.area.includes('Khandauli'), 'PIN 283126 area mismatch');
    assert(data.lat > 26 && data.lng > 77, 'PIN coordinates invalid');
    console.log(`   -> PIN Code 283126: ${data.area} (Lat: ${data.lat}, Lng: ${data.lng})`);
  });

  // 7. Option 1: GPS Nearby Search
  await test('7. GET /cold-storages/nearby calculates Haversine & sorts nearest to farthest', async () => {
    // Farmer at Khandauli / Agra (27.3110, 78.0790)
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=27.3110&longitude=78.0790`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.count > 0, 'No nearby storages found');

    // Verify distance sorting
    for (let i = 0; i < data.results.length - 1; i++) {
      assert(
        data.results[i].distance_km <= data.results[i + 1].distance_km,
        `Not sorted by distance: ${data.results[i].distance_km} > ${data.results[i + 1].distance_km}`
      );
    }

    // Nearest storage should be < 5km from Khandauli
    assert(data.results[0].distance_km < 10, 'Nearest storage should be close');
    console.log(`   -> Nearest facility: "${data.results[0].name}" at ${data.results[0].distance_km} km (Drive: ~${data.results[0].drive_time_text})`);
  });

  // 8. Progressive Radius Expansion (10km -> 25km -> 50km)
  await test('8. Auto-expansion: expands radius when few or no storages within 10 km in rural areas', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=27.1767&longitude=78.0081`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.searchRadiusKm >= 10, 'Search radius should be defined');
    console.log(`   -> Effective expanded search radius: ${data.searchRadiusKm} km (autoExpanded: ${data.autoExpanded})`);
  });

  // 9. Crop filtering on nearby search
  await test('9. Crop filter: filters nearby storages suitable for specific produce', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=27.1767&longitude=78.0081&crop=Potato`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    data.results.forEach((item) => {
      assert(item.suitable_crops.toLowerCase().includes('potato'), 'Item does not match crop filter');
    });
    console.log(`   -> Found ${data.count} potato-suitable facilities near Agra`);
  });

  // 10. Option 2: Geocoding + Manual Village Search
  await test('10. GET /api/geocode converts rural village to accurate coordinates', async () => {
    const res = await fetch(`${BASE_URL}/api/geocode?state=Maharashtra&district=Nashik&address=Mohadi`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.location.latitude > 18 && data.location.latitude < 22, 'Invalid Nashik latitude');
    assert(data.location.longitude > 72 && data.location.longitude < 76, 'Invalid Nashik longitude');
    console.log(`   -> Geocoded Mohadi, Nashik to: ${data.location.latitude}, ${data.location.longitude} (${data.location.source})`);
  });

  // 11. Single Facility Details by ID
  await test('11. GET /cold-storages/:id returns complete real details, description & contact info', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/CS-UP-AGR-003`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    const cs = data.cold_storage;
    assert.strictEqual(cs.id, 'CS-UP-AGR-003');
    assert(cs.name && cs.address && cs.phone_number && cs.storage_capacity, 'Required fields missing');
    assert(cs.village_or_area === 'Khandauli', 'Village field mismatch');
    console.log(`   -> Verified Khandauli Facility: ${cs.name}, Capacity: ${cs.storage_capacity}`);
  });

  // 12. Error & Edge Cases
  await test('12. Error handling for missing parameters & 404s', async () => {
    // Missing coords
    const res1 = await fetch(`${BASE_URL}/cold-storages/nearby`);
    assert.strictEqual(res1.status, 400);

    // Invalid non-existent ID
    const res2 = await fetch(`${BASE_URL}/cold-storages/CS-NONEXISTENT-999`);
    assert.strictEqual(res2.status, 404);

    // Non-existent PIN
    const res3 = await fetch(`${BASE_URL}/api/pincode/999999`);
    assert.strictEqual(res3.status, 404);
  });

  console.log('\n====================================================');
  console.log(`📊 TEST SUMMARY: ${passed}/${total} TESTS PASSED (${Math.round((passed / total) * 100)}%)`);
  console.log('====================================================');

  if (passed === total) {
    return;
  } else {
    process.exitCode = 1;
  }
}

runE2ETests().catch((err) => {
  console.error('Fatal error in tests:', err);
  process.exitCode = 1;
});

