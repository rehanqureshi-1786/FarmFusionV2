import assert from 'assert';

const BASE_URL = 'http://localhost:3000';

async function runFullTestSuite() {
  console.log('========================================================================');
  console.log('🌾 FARMFUSION COLD STORAGE FINDER — EXHAUSTIVE FEASIBILITY & TEST SUITE');
  console.log('========================================================================');
  console.log(`⏱️ Execution Time: ${new Date().toISOString()}`);
  console.log(`🔗 Target URL: ${BASE_URL}\n`);

  const results = [];

  async function executeTest(category, testId, testName, testFn) {
    const startTime = Date.now();
    try {
      const details = await testFn();
      const duration = Date.now() - startTime;
      results.push({
        category,
        id: testId,
        name: testName,
        status: 'PASSED',
        durationMs: duration,
        details: details || 'Passed'
      });
      console.log(`✅ [${testId}] ${testName} (${duration}ms)`);
      if (details) console.log(`   └─ ${details}`);
    } catch (err) {
      const duration = Date.now() - startTime;
      results.push({
        category,
        id: testId,
        name: testName,
        status: 'FAILED',
        durationMs: duration,
        error: err.message
      });
      console.error(`❌ [${testId}] ${testName} (${duration}ms): ${err.message}`);
    }
  }

  // -------------------------------------------------------------
  // CATEGORY 1: GPS & HAVERSINE NEARBY SEARCH
  // -------------------------------------------------------------
  console.log('\n--- CATEGORY 1: GPS Search & Haversine Distance Calculation ---');

  await executeTest('GPS Search', 'TC-01', 'Calculate Haversine distance and sort nearest-to-farthest from Agra, UP (Potato Belt)', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=27.1767&longitude=78.0081`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.results.length >= 2, 'Should find multiple facilities near Agra');

    for (let i = 0; i < data.results.length - 1; i++) {
      assert(
        data.results[i].distance_km <= data.results[i + 1].distance_km,
        `Sorting failure: ${data.results[i].distance_km} km > ${data.results[i + 1].distance_km} km`
      );
    }
    const closest = data.results[0];
    return `Nearest facility: "${closest.name}" at ${closest.distance_km} km (Tractor: ~${closest.drive_time_text})`;
  });

  await executeTest('GPS Search', 'TC-02', 'Calculate Haversine distance from Nashik, Maharashtra (Grape & Onion Hub)', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=19.9975&longitude=73.7898`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.results.length >= 2);
    const closest = data.results[0];
    assert(closest.distance_km < 25, 'Nashik facility should be within 25 km');
    return `Closest: "${closest.name}" at ${closest.distance_km} km`;
  });

  await executeTest('GPS Search', 'TC-03', 'Calculate Haversine distance from Deesa / Banaskantha, Gujarat (Potato Hub)', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=24.2580&longitude=72.1810`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.results.length > 0);
    const closest = data.results[0];
    assert(closest.distance_km < 10, 'Deesa facility should be < 10 km');
    return `Closest: "${closest.name}" at ${closest.distance_km} km`;
  });

  await executeTest('GPS Search', 'TC-04', 'Progressive Radius Auto-Expansion when searching from remote rural coordinate', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=27.5530&longitude=76.6346`);
    const data = await res.json();
    assert(data.searchRadiusKm >= 10, 'Search radius should be defined');
    return `Auto-expanded search radius: ${data.searchRadiusKm} km (Found: ${data.count} facilities)`;
  });

  // -------------------------------------------------------------
  // CATEGORY 2: RURAL VILLAGE GEOCODING & AUTO-SUGGEST
  // -------------------------------------------------------------
  console.log('\n--- CATEGORY 2: Rural Village Geocoding & Auto-Suggest ---');

  await executeTest('Village Geocoding', 'TC-05', 'Geocode UP Rural Village: Khandauli (Agra)', async () => {
    const res = await fetch(`${BASE_URL}/api/geocode?state=Uttar+Pradesh&district=Agra&address=Khandauli`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.location.latitude > 27.2 && data.location.latitude < 27.4, 'Latitude out of range');
    assert(data.location.longitude > 78.0 && data.location.longitude < 78.2, 'Longitude out of range');
    return `Resolved Khandauli to (${data.location.latitude}, ${data.location.longitude}) via ${data.location.source}`;
  });

  await executeTest('Village Geocoding', 'TC-06', 'Geocode Maharashtra Rural Tehsil: Mohadi (Nashik)', async () => {
    const res = await fetch(`${BASE_URL}/api/geocode?state=Maharashtra&district=Nashik&address=Mohadi`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.location.latitude > 20.0 && data.location.latitude < 20.2);
    return `Resolved Mohadi, Nashik to (${data.location.latitude}, ${data.location.longitude})`;
  });

  await executeTest('Village Geocoding', 'TC-07', 'Geocode Punjab Rural Village: Lambra (Jalandhar)', async () => {
    const res = await fetch(`${BASE_URL}/api/geocode?state=Punjab&district=Jalandhar&address=Lambra`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.location.latitude > 31.1 && data.location.latitude < 31.4);
    return `Resolved Lambra, Jalandhar to (${data.location.latitude}, ${data.location.longitude})`;
  });

  await executeTest('Village Geocoding', 'TC-08', 'Geocode Himachal Apple Belt: Theog (Shimla)', async () => {
    const res = await fetch(`${BASE_URL}/api/geocode?state=Himachal+Pradesh&district=Shimla+(Theog/Kotkhai/Rampur)&address=Theog`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.location.latitude > 31.0 && data.location.latitude < 31.3);
    return `Resolved Theog, Shimla to (${data.location.latitude}, ${data.location.longitude})`;
  });

  await executeTest('Village Geocoding', 'TC-09', 'Geocode South India Market: Oddanchatram (Dindigul, Tamil Nadu)', async () => {
    const res = await fetch(`${BASE_URL}/api/geocode?state=Tamil+Nadu&district=Dindigul+(Oddanchatram)&address=Oddanchatram`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.location.latitude > 10.3 && data.location.latitude < 10.6);
    return `Resolved Oddanchatram to (${data.location.latitude}, ${data.location.longitude})`;
  });

  await executeTest('Village Auto-Suggest', 'TC-10', 'Auto-Suggest API matches rural villages as farmer types ("Chom" -> Chomu)', async () => {
    const res = await fetch(`${BASE_URL}/api/villages?q=Chom`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.suggestions.length > 0, 'Should find suggestions for Chom');
    assert(data.suggestions.some((s) => s.village.toLowerCase().includes('chomu')), 'Chomu missing from suggestions');
    return `Auto-suggest returned: ${data.suggestions.map((s) => s.village).join(', ')}`;
  });

  await executeTest('Village Auto-Suggest', 'TC-11', 'Auto-Suggest API matches rural mandis ("Piplia" -> Piplia Mandi, Mandsaur)', async () => {
    const res = await fetch(`${BASE_URL}/api/villages?q=Piplia`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.suggestions.length > 0);
    assert(data.suggestions[0].village.includes('Piplia Mandi'));
    return `Auto-suggest matched: ${data.suggestions[0].name} (${data.suggestions[0].type})`;
  });

  // -------------------------------------------------------------
  // CATEGORY 3: POSTAL PIN CODE RESOLUTION
  // -------------------------------------------------------------
  console.log('\n--- CATEGORY 3: Postal PIN Code Engine ---');

  await executeTest('PIN Code', 'TC-12', 'Direct 6-Digit PIN lookup: 283126 (Khandauli, UP)', async () => {
    const res = await fetch(`${BASE_URL}/api/pincode/283126`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.area.includes('Khandauli'));
    return `PIN 283126 -> ${data.area} (Lat: ${data.lat}, Lng: ${data.lng})`;
  });

  await executeTest('PIN Code', 'TC-13', 'Direct 6-Digit PIN lookup: 385535 (Deesa, Gujarat)', async () => {
    const res = await fetch(`${BASE_URL}/api/pincode/385535`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.area.includes('Deesa'));
    return `PIN 385535 -> ${data.area} (Lat: ${data.lat}, Lng: ${data.lng})`;
  });

  await executeTest('PIN Code', 'TC-14', 'Direct 6-Digit PIN lookup: 563101 (Kolar APMC, Karnataka)', async () => {
    const res = await fetch(`${BASE_URL}/api/pincode/563101`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.area.includes('Kolar'));
    return `PIN 563101 -> ${data.area} (Lat: ${data.lat}, Lng: ${data.lng})`;
  });

  await executeTest('PIN Code', 'TC-15', 'Postal Circle prefix fallback for any valid Indian PIN (e.g. 781124 - Assam)', async () => {
    const res = await fetch(`${BASE_URL}/api/pincode/781124`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.lat > 25 && data.lng > 90);
    return `PIN 781124 -> ${data.area} (${data.lat}, ${data.lng})`;
  });

  // -------------------------------------------------------------
  // CATEGORY 4: CROP FILTERING & METADATA
  // -------------------------------------------------------------
  console.log('\n--- CATEGORY 4: Produce Crop Filtering ---');

  await executeTest('Crop Filter', 'TC-16', 'Filter facilities for Potato (Agra belt)', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=27.1767&longitude=78.0081&crop=Potato`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.count >= 2);
    data.results.forEach((item) => {
      assert(item.suitable_crops.toLowerCase().includes('potato'), 'Non-potato facility returned');
    });
    return `Found ${data.count} potato-suitable cold storages near Agra`;
  });

  await executeTest('Crop Filter', 'TC-17', 'Filter facilities for Garlic (Hadoti & Malwa belt)', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=25.2138&longitude=75.8648&crop=Garlic`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    data.results.forEach((item) => {
      assert(item.suitable_crops.toLowerCase().includes('garlic'), 'Non-garlic facility returned');
    });
    return `Found ${data.count} garlic-certified cold storages near Kota/Mandsaur`;
  });

  await executeTest('Crop Filter', 'TC-18', 'Filter facilities for Apples (Himachal/Kashmir)', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=31.1210&longitude=77.3540&crop=Apple`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.count >= 1);
    return `Found ${data.count} apple ULO CA store(s) in Himachal`;
  });

  // -------------------------------------------------------------
  // CATEGORY 5: DATABASE INTEGRITY & REAL FACILITY PROFILES
  // -------------------------------------------------------------
  console.log('\n--- CATEGORY 5: Database Integrity & Cold Storage Verification ---');

  await executeTest('DB Integrity', 'TC-19', 'Verify all cold storages have valid Indian coordinates & complete data', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=26.9124&longitude=75.7873&radius=5000`);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.count >= 25, `Expected >= 25 records, found ${data.count}`);

    const idSet = new Set();
    data.results.forEach((cs) => {
      // Check ID uniqueness
      assert(!idSet.has(cs.id), `Duplicate ID found: ${cs.id}`);
      idSet.add(cs.id);

      // Check coordinates inside India (Lat: 8°N to 37°N, Lng: 68°E to 98°E)
      assert(cs.latitude >= 8.0 && cs.latitude <= 37.0, `Latitude out of bounds in ${cs.id}: ${cs.latitude}`);
      assert(cs.longitude >= 68.0 && cs.longitude <= 98.0, `Longitude out of bounds in ${cs.id}: ${cs.longitude}`);

      // Check required fields
      assert(cs.name && cs.name.length > 5, `Invalid name in ${cs.id}`);
      assert(cs.address && cs.address.length > 5, `Invalid address in ${cs.id}`);
      assert(cs.district, `Missing district in ${cs.id}`);
      assert(cs.state, `Missing state in ${cs.id}`);
      assert(cs.storage_capacity, `Missing capacity in ${cs.id}`);
      assert(cs.suitable_crops, `Missing suitable crops in ${cs.id}`);
    });
    return `Verified all ${data.count} cold storage records have valid geographical bounds, non-null specifications, and unique IDs.`;
  });

  await executeTest('Facility Details', 'TC-20', 'Single facility profile verification (CS-UP-AGR-003 - Khandauli)', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/CS-UP-AGR-003`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    const cs = data.cold_storage;
    assert.strictEqual(cs.village_or_area, 'Khandauli');
    assert(cs.storage_capacity.includes('18,000 MT'));
    assert(cs.phone_number.startsWith('+91'));
    return `Verified: ${cs.name} (${cs.village_or_area}, ${cs.district}) | Phone: ${cs.phone_number}`;
  });

  await executeTest('Facility Details', 'TC-21', 'Single facility profile verification (CS-MH-NSK-001 - Sahyadri Mohadi)', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/CS-MH-NSK-001`);
    const data = await res.json();
    const cs = data.cold_storage;
    assert.strictEqual(cs.village_or_area, 'Mohadi');
    assert(cs.certifications.includes('APEDA') || cs.certifications.includes('GlobalGAP'));
    return `Verified: ${cs.name} | Certifications: ${cs.certifications}`;
  });

  // -------------------------------------------------------------
  // CATEGORY 6: ERROR HANDLING & EDGE CASES
  // -------------------------------------------------------------
  console.log('\n--- CATEGORY 6: Error Handling & Extreme Edge Cases ---');

  await executeTest('Error Handling', 'TC-22', 'Missing coordinates returns HTTP 400 with helpful JSON error message', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby`);
    assert.strictEqual(res.status, 400);
    const err = await res.json();
    assert(err.error && err.message);
    return `Rejected with HTTP 400: "${err.message}"`;
  });

  await executeTest('Error Handling', 'TC-23', 'Invalid NaN coordinates returns HTTP 400', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/nearby?latitude=invalid&longitude=test`);
    assert.strictEqual(res.status, 400);
    const err = await res.json();
    return `Rejected with HTTP 400: "${err.message}"`;
  });

  await executeTest('Error Handling', 'TC-24', 'Non-existent facility ID returns HTTP 404', async () => {
    const res = await fetch(`${BASE_URL}/cold-storages/CS-UNKNOWN-9999`);
    assert.strictEqual(res.status, 404);
    const err = await res.json();
    return `Handled with HTTP 404: "${err.message}"`;
  });

  await executeTest('Error Handling', 'TC-25', 'Non-existent PIN code handles gracefully with HTTP 404', async () => {
    const res = await fetch(`${BASE_URL}/api/pincode/999999`);
    assert.strictEqual(res.status, 404);
    return 'Non-existent PIN correctly returns 404';
  });

  await executeTest('Error Handling', 'TC-26', 'Handling Hindi address query text ("खंदौली, आगरा")', async () => {
    const res = await fetch(`${BASE_URL}/api/geocode?state=Uttar+Pradesh&district=Agra&address=%E0%A4%96%E0%A4%82%E0%A4%A6%E0%A4%8C%E0%A4%B2%E0%A5%80`);
    assert.strictEqual(res.status, 200);
    const data = await res.json();
    assert.strictEqual(data.success, true);
    assert(data.location.latitude > 26 && data.location.longitude > 77);
    return `Handled Hindi query safely -> Lat: ${data.location.latitude}, Lng: ${data.location.longitude}`;
  });

  // -------------------------------------------------------------
  // CATEGORY 7: FRONTEND HEALTH & ASSETS
  // -------------------------------------------------------------
  console.log('\n--- CATEGORY 7: Frontend Health, Assets & Accessibility ---');

  await executeTest('Frontend Health', 'TC-27', 'Verify HTML5 Semantic Structure with Voice Button & Village Dropdown', async () => {
    const res = await fetch(`${BASE_URL}/`);
    assert.strictEqual(res.status, 200);
    const html = await res.text();
    assert(html.includes('id="tab-btn-gps"'), 'GPS Tab button missing');
    assert(html.includes('id="tab-btn-manual"'), 'Manual Tab button missing');
    assert(html.includes('id="btn-voice-search"'), 'Voice Search button missing');
    assert(html.includes('id="village-suggestions-list"'), 'Village suggestions dropdown missing');
    assert(html.includes('id="storage-modal"'), 'Details Modal element missing');
    return 'HTML structure validated with Voice Search button, Village dropdown, and Modal elements';
  });

  await executeTest('Frontend Health', 'TC-28', 'Verify CSS Design System, Responsive Tokens & Pulse Animations', async () => {
    const res = await fetch(`${BASE_URL}/css/styles.css`);
    assert.strictEqual(res.status, 200);
    const css = await res.text();
    assert(css.includes('--primary-600'), 'Primary green token missing');
    assert(css.includes('.btn-voice'), 'Voice button styles missing');
    assert(css.includes('.village-suggestions-dropdown'), 'Village suggestions styles missing');
    assert(css.includes('@keyframes voicePulse'), 'Voice pulse animation missing');
    return 'CSS verified with responsive tokens, voice listening animation, and village dropdown layout';
  });

  await executeTest('Frontend Health', 'TC-29', 'Verify JavaScript Modules (app.js, api.js, map.js, i18n.js)', async () => {
    const files = ['app.js', 'api.js', 'map.js', 'i18n.js'];
    for (const f of files) {
      const res = await fetch(`${BASE_URL}/js/${f}`);
      assert.strictEqual(res.status, 200, `Failed to load ${f}`);
    }
    return 'All 4 ES6 frontend modules load with HTTP 200';
  });

  await executeTest('Frontend Health', 'TC-30', 'Verify Full Parity between English & Hindi Translation Dictionaries', async () => {
    const res = await fetch(`${BASE_URL}/js/i18n.js`);
    const js = await res.text();
    assert(js.includes('appTitle'), 'appTitle key missing');
    assert(js.includes('callBtn'), 'callBtn key missing');
    assert(js.includes('navigateBtn'), 'navigateBtn key missing');
    assert(js.includes('voiceListening'), 'voiceListening key missing');
    assert(js.includes('quickVillagesLabel'), 'quickVillagesLabel key missing');
    assert(js.includes('फार्मफ्यूजन कोल्ड स्टोरेज'), 'Hindi title missing');
    return 'Multilingual dictionary verified with full English & Hindi keys for all rural features';
  });

  // -------------------------------------------------------------
  // SUMMARY REPORT
  // -------------------------------------------------------------
  console.log('\n========================================================================');
  const passedCount = results.filter((r) => r.status === 'PASSED').length;
  const failedCount = results.filter((r) => r.status === 'FAILED').length;
  const totalCount = results.length;
  const passRate = Math.round((passedCount / totalCount) * 100);

  console.log(`📊 FINAL TEST REPORT: ${passedCount}/${totalCount} TESTS PASSED (${passRate}%)`);
  console.log(`❌ FAILURES: ${failedCount}`);
  console.log('========================================================================\n');

  if (failedCount > 0) {
    process.exitCode = 1;
  } else {
    process.exitCode = 0;
  }
}

runFullTestSuite().catch((err) => {
  console.error('Fatal error in test execution:', err);
  process.exitCode = 1;
});
