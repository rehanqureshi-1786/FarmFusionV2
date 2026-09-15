import { Api } from './api.js';
import { MapController } from './map.js';
import { translations } from './i18n.js';

// Application State
const state = {
  lang: 'en',
  currentTab: 'gps', // 'gps' | 'manual'
  farmerCoords: null, // { latitude, longitude, label, accuracy, source }
  storages: [],
  selectedStorage: null,
  locationsData: {},
  activeRadius: null, // null for auto, or number
  selectedCrop: '',
  activeView: 'split', // 'list' | 'map' | 'split'
  loading: false,
  isListening: false
};

// Initialize Application
async function initApp() {
  console.log('🌾 Initializing FarmFusion Cold Storage Finder - Rural Edition...');
  try {
    initLanguage();
    initSearchTabs();
    initViewToggles();
    initCropFilters();
    initModalListeners();
    initVoiceSearch();
    initVillageAutoSuggest();
    initQuickVillageChips();
    MapController.init();

    // Load locations for dropdowns
    await loadLocations();

    // Initial demonstration search
    initDefaultDemoSearch();
    console.log('✅ FarmFusion Cold Storage Finder initialized successfully.');
  } catch (err) {
    console.error('Initialization error:', err);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

function initLanguage() {
  const langSelect = document.getElementById('lang-select');
  if (langSelect) {
    langSelect.addEventListener('change', (e) => {
      state.lang = e.target.value;
      applyTranslations();
      renderResults();
    });
  }
  applyTranslations();
}

function applyTranslations() {
  const tDict = translations[state.lang] || translations.en;
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    if (tDict[key]) {
      el.textContent = tDict[key];
    }
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (tDict[key]) {
      el.placeholder = tDict[key];
    }
  });
}

function t(key, params = {}) {
  const dict = translations[state.lang] || translations.en;
  let str = dict[key] || key;
  for (const [k, v] of Object.entries(params)) {
    str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
  }
  return str;
}

// -------------------------------------------------------------
// Search Tabs & Form Handling
// -------------------------------------------------------------
function initSearchTabs() {
  const tabs = document.querySelectorAll('.search-tab-btn');
  tabs.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });

  // GPS Button
  const btnGps = document.getElementById('btn-gps-search');
  if (btnGps) {
    btnGps.addEventListener('click', handleGpsSearch);
  }

  // Radius chips
  const radiusChips = document.querySelectorAll('.radius-chip');
  radiusChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      radiusChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      const val = chip.getAttribute('data-radius');
      state.activeRadius = val === 'auto' ? null : parseInt(val, 10);

      // Re-trigger search if we have active coordinates
      if (state.farmerCoords) {
        executeNearbySearch(state.farmerCoords.latitude, state.farmerCoords.longitude);
      }
    });
  });

  // Manual Search Form
  const manualForm = document.getElementById('manual-search-form');
  if (manualForm) {
    manualForm.addEventListener('submit', handleManualSearch);
  }

  // Cascading dropdowns
  const manualStateSelect = document.getElementById('manual-state');
  const manualDistrictSelect = document.getElementById('manual-district');
  if (manualStateSelect && manualDistrictSelect) {
    manualStateSelect.addEventListener('change', () => {
      populateDistricts(manualStateSelect.value, manualDistrictSelect);
    });
  }
}

function switchTab(tabName) {
  state.currentTab = tabName;
  document.querySelectorAll('.search-tab-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
  });
  document.querySelectorAll('.tab-panel').forEach((panel) => {
    panel.classList.toggle('active', panel.id === `tab-${tabName}`);
  });
}

// -------------------------------------------------------------
// Locations Dropdowns
// -------------------------------------------------------------
async function loadLocations() {
  try {
    const data = await Api.getLocations();
    if (data && data.states) {
      state.locationsData = data.states;

      const manualState = document.getElementById('manual-state');
      populateStatesDropdown(manualState);

      // Default selection to Uttar Pradesh / Agra
      if (manualState && manualState.options.length > 1) {
        manualState.value = 'Uttar Pradesh';
        populateDistricts('Uttar Pradesh', document.getElementById('manual-district'));
        const manualDist = document.getElementById('manual-district');
        if (manualDist) manualDist.value = 'Agra';
      }
    }
  } catch (err) {
    console.error('Failed to load locations:', err);
  }
}

function populateStatesDropdown(selectElement) {
  if (!selectElement) return;
  selectElement.innerHTML = `<option value="">${t('selectState')}</option>`;
  Object.keys(state.locationsData).forEach((st) => {
    const opt = document.createElement('option');
    opt.value = st;
    opt.textContent = st;
    selectElement.appendChild(opt);
  });
}

function populateDistricts(selectedState, districtSelect, selectValue = null) {
  if (!districtSelect) return;
  districtSelect.innerHTML = `<option value="">${t('selectDistrict')}</option>`;
  if (!selectedState || !state.locationsData[selectedState]) return;

  state.locationsData[selectedState].forEach((dist) => {
    const opt = document.createElement('option');
    opt.value = dist;
    opt.textContent = dist;
    if (selectValue && dist.toLowerCase() === selectValue.toLowerCase()) {
      opt.selected = true;
    }
    districtSelect.appendChild(opt);
  });
}

// -------------------------------------------------------------
// Voice Search (Speech-to-Text for Rural Farmers)
// -------------------------------------------------------------
function initVoiceSearch() {
  const voiceBtn = document.getElementById('btn-voice-search');
  const addressInput = document.getElementById('manual-address');
  if (!voiceBtn || !addressInput) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    voiceBtn.addEventListener('click', () => {
      showError(t('voiceNotSupported'));
    });
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = state.lang === 'hi' ? 'hi-IN' : 'en-IN';

  recognition.onstart = () => {
    state.isListening = true;
    voiceBtn.classList.add('listening');
    addressInput.placeholder = t('voiceListening');
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    addressInput.value = transcript;
    addressInput.focus();

    // Trigger village auto search or direct search
    triggerVillageAutoSearch(transcript);
  };

  recognition.onerror = (event) => {
    console.warn('Speech recognition error:', event.error);
    voiceBtn.classList.remove('listening');
    state.isListening = false;
    applyTranslations();
  };

  recognition.onend = () => {
    voiceBtn.classList.remove('listening');
    state.isListening = false;
    applyTranslations();
  };

  voiceBtn.addEventListener('click', () => {
    if (state.isListening) {
      recognition.stop();
    } else {
      recognition.lang = state.lang === 'hi' ? 'hi-IN' : 'en-IN';
      recognition.start();
    }
  });
}

// -------------------------------------------------------------
// Live Village Auto-Suggest Typeahead
// -------------------------------------------------------------
let autoSuggestTimer = null;

function initVillageAutoSuggest() {
  const input = document.getElementById('manual-address');
  const dropdown = document.getElementById('village-suggestions-list');
  if (!input || !dropdown) return;

  input.addEventListener('input', () => {
    const val = input.value.trim();
    if (val.length < 2) {
      dropdown.style.display = 'none';
      return;
    }

    clearTimeout(autoSuggestTimer);
    autoSuggestTimer = setTimeout(() => {
      triggerVillageAutoSearch(val);
    }, 220);
  });

  // Close dropdown on click outside
  document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = 'none';
    }
  });
}

async function triggerVillageAutoSearch(query) {
  const dropdown = document.getElementById('village-suggestions-list');
  const input = document.getElementById('manual-address');
  const stateVal = document.getElementById('manual-state')?.value || '';
  const distVal = document.getElementById('manual-district')?.value || '';

  if (!dropdown || !input) return;

  try {
    const res = await Api.searchVillages(query, stateVal, distVal);
    if (res.success && res.suggestions && res.suggestions.length > 0) {
      dropdown.innerHTML = res.suggestions
        .map(
          (s) => `
        <div class="suggestion-item" data-village="${escapeHtml(s.village || s.name)}" data-district="${escapeHtml(s.district || '')}" data-state="${escapeHtml(s.state || '')}" data-lat="${s.latitude}" data-lng="${s.longitude}">
          <div class="suggestion-item-main">
            <span class="suggestion-name">📍 ${escapeHtml(s.village || s.name)}</span>
            <span class="suggestion-sub">${escapeHtml(s.district ? `${s.district}, ${s.state}` : s.name)}</span>
          </div>
          <span class="suggestion-badge">${escapeHtml(s.type || 'Village')}</span>
        </div>
      `
        )
        .join('');

      dropdown.style.display = 'flex';

      dropdown.querySelectorAll('.suggestion-item').forEach((item) => {
        item.addEventListener('click', () => {
          const vName = item.getAttribute('data-village');
          const dName = item.getAttribute('data-district');
          const sName = item.getAttribute('data-state');
          const lat = parseFloat(item.getAttribute('data-lat'));
          const lng = parseFloat(item.getAttribute('data-lng'));

          input.value = vName;
          dropdown.style.display = 'none';

          // Sync state & district dropdowns if available
          if (sName) {
            const stSelect = document.getElementById('manual-state');
            if (stSelect) {
              stSelect.value = sName;
              populateDistricts(sName, document.getElementById('manual-district'), dName);
            }
          }

          state.farmerCoords = {
            latitude: lat,
            longitude: lng,
            label: `${vName}${dName ? `, ${dName}` : ''}`,
            source: 'Rural Gram Panchayat / Village Engine',
            accuracy: '🌾 Exact Village Centroid'
          };

          executeNearbySearch(lat, lng);
        });
      });
    } else {
      dropdown.style.display = 'none';
    }
  } catch (err) {
    console.warn('Auto-suggest error:', err);
  }
}

// -------------------------------------------------------------
// Quick Rural Mandi / Village Chips
// -------------------------------------------------------------
function initQuickVillageChips() {
  const chips = document.querySelectorAll('.quick-village-chip');
  const input = document.getElementById('manual-address');
  const stSelect = document.getElementById('manual-state');
  const distSelect = document.getElementById('manual-district');

  chips.forEach((chip) => {
    chip.addEventListener('click', async () => {
      const vName = chip.getAttribute('data-village');
      const dName = chip.getAttribute('data-district');
      const sName = chip.getAttribute('data-state');

      if (input) input.value = vName;

      if (sName && stSelect) {
        stSelect.value = sName;
        populateDistricts(sName, distSelect, dName);
      }

      setLoading(true);
      try {
        const geoRes = await Api.geocode(vName, dName, sName);
        const loc = geoRes.location;

        state.farmerCoords = {
          latitude: loc.latitude,
          longitude: loc.longitude,
          label: `${vName}, ${dName}`,
          source: loc.source,
          accuracy: loc.accuracy || 'Exact Village'
        };

        await executeNearbySearch(loc.latitude, loc.longitude);
      } catch (err) {
        showError(err.message || t('errGeocodeFail'));
      } finally {
        setLoading(false);
      }
    });
  });
}

// -------------------------------------------------------------
// Search Handlers
// -------------------------------------------------------------

/**
 * OPTION 1: Use My Current Location
 */
function handleGpsSearch() {
  clearError();
  const btn = document.getElementById('btn-gps-search');
  const originalHTML = btn.innerHTML;

  if (!navigator.geolocation) {
    showError(t('errGpsUnavailable'));
    return;
  }

  btn.innerHTML = `<span>⏳ ${t('locating')}</span>`;
  btn.disabled = true;

  navigator.geolocation.getCurrentPosition(
    (position) => {
      btn.innerHTML = originalHTML;
      btn.disabled = false;

      const lat = position.coords.latitude;
      const lng = position.coords.longitude;

      state.farmerCoords = {
        latitude: lat,
        longitude: lng,
        label: 'My Current Location',
        accuracy: 'GPS High Precision',
        source: 'Device Geolocation'
      };

      executeNearbySearch(lat, lng);
    },
    (err) => {
      btn.innerHTML = originalHTML;
      btn.disabled = false;

      console.warn('Geolocation error:', err);
      let errorMsg = t('errGpsUnavailable');
      if (err.code === err.PERMISSION_DENIED) {
        errorMsg = t('errGpsDenied');
      }

      showError(errorMsg, true);
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 60000
    }
  );
}

/**
 * OPTION 2: Enter Location / Village Manually
 */
async function handleManualSearch(e) {
  e.preventDefault();
  clearError();

  const stateVal = document.getElementById('manual-state').value;
  const districtVal = document.getElementById('manual-district').value;
  const addressVal = document.getElementById('manual-address').value;

  if (!stateVal && !districtVal && !addressVal) {
    showError(t('errMissingInputs'));
    return;
  }

  setLoading(true);
  try {
    const geoRes = await Api.geocode(addressVal, districtVal, stateVal);
    const loc = geoRes.location;

    state.farmerCoords = {
      latitude: loc.latitude,
      longitude: loc.longitude,
      label: addressVal ? `${addressVal}${districtVal ? `, ${districtVal}` : ''}` : `${districtVal}, ${stateVal}`,
      source: loc.source,
      accuracy: loc.accuracy || 'Regional'
    };

    await executeNearbySearch(loc.latitude, loc.longitude);
  } catch (err) {
    showError(err.message || t('errGeocodeFail'));
  } finally {
    setLoading(false);
  }
}

/**
 * Executes nearby search API and updates map + UI
 */
async function executeNearbySearch(lat, lng) {
  setLoading(true);
  clearError();

  try {
    const data = await Api.getNearbyStorages(lat, lng, state.activeRadius, state.selectedCrop);

    state.storages = data.results || [];
    const radius = data.searchRadiusKm;
    const autoExpanded = data.autoExpanded;

    renderResults({
      title: state.farmerCoords?.label || `${lat.toFixed(3)}, ${lng.toFixed(3)}`,
      count: state.storages.length,
      radius,
      autoExpanded
    });

    MapController.renderResults(
      state.farmerCoords,
      state.storages,
      (id) => openStorageModal(id),
      radius
    );
  } catch (err) {
    showError(err.message || t('errNetwork'));
  } finally {
    setLoading(false);
  }
}

function initDefaultDemoSearch() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        state.farmerCoords = {
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          label: 'Your Current Location',
          accuracy: 'GPS',
          source: 'Live GPS'
        };
        executeNearbySearch(pos.coords.latitude, pos.coords.longitude);
      },
      () => {
        // Default to Agra / Khandauli potato belt
        state.farmerCoords = {
          latitude: 27.1767,
          longitude: 78.0081,
          label: 'Agra, Uttar Pradesh (Rural Agri Belt)',
          accuracy: 'District Hub',
          source: 'Regional Center'
        };
        executeNearbySearch(27.1767, 78.0081);
      },
      { timeout: 3500 }
    );
  } else {
    state.farmerCoords = {
      latitude: 27.1767,
      longitude: 78.0081,
      label: 'Agra, Uttar Pradesh',
      accuracy: 'District Hub',
      source: 'Regional Center'
    };
    executeNearbySearch(27.1767, 78.0081);
  }
}

// -------------------------------------------------------------
// Render Results List & Cards
// -------------------------------------------------------------
function renderResults(meta = {}) {
  const container = document.getElementById('storages-list');
  const countBadge = document.getElementById('results-count-badge');
  const noticeBox = document.getElementById('search-notice-box');
  const sourceBadge = document.getElementById('location-source-badge');

  if (!container) return;

  if (countBadge) {
    countBadge.textContent = t('resultsCount', { count: state.storages.length });
  }

  // Location accuracy source badge
  if (sourceBadge && state.farmerCoords && state.farmerCoords.accuracy) {
    sourceBadge.textContent = `📍 ${state.farmerCoords.accuracy}`;
    sourceBadge.style.display = 'inline-block';
  } else if (sourceBadge) {
    sourceBadge.style.display = 'none';
  }

  // Expansion alert
  if (noticeBox) {
    if (meta.autoExpanded && meta.radius) {
      noticeBox.innerHTML = `
        <div class="expansion-alert">
          <span class="alert-icon">ℹ️</span>
          <span>${t('autoExpandedNotice', { radius: meta.radius })}</span>
        </div>
      `;
      noticeBox.style.display = 'block';
    } else {
      noticeBox.innerHTML = '';
      noticeBox.style.display = 'none';
    }
  }

  // Empty State
  if (state.storages.length === 0) {
    container.innerHTML = `
      <div class="empty-state-card">
        <div class="empty-icon">🧊</div>
        <h3>${t('noResultsTitle')}</h3>
        <p>${t('noResultsDesc')}</p>
        <div class="empty-actions">
          <button class="btn btn-primary" id="btn-expand-empty">${t('btnExpandRadius')}</button>
        </div>
      </div>
    `;

    document.getElementById('btn-expand-empty')?.addEventListener('click', () => {
      state.activeRadius = 100;
      if (state.farmerCoords) {
        executeNearbySearch(state.farmerCoords.latitude, state.farmerCoords.longitude);
      }
    });

    return;
  }

  // Render Storage Cards
  container.innerHTML = state.storages
    .map((cs, idx) => createStorageCardHTML(cs, idx))
    .join('');

  // Attach card detail buttons
  state.storages.forEach((cs) => {
    const cardEl = document.getElementById(`storage-card-${cs.id}`);
    if (cardEl) {
      cardEl.querySelector('.btn-view-details')?.addEventListener('click', () => {
        openStorageModal(cs.id);
      });
    }
  });
}

function createStorageCardHTML(cs, index) {
  const hasPhone = Boolean(cs.phone_number);
  const cleanPhone = hasPhone ? cs.phone_number.replace(/\s+/g, '') : '';
  const cropsList = cs.suitable_crops
    ? cs.suitable_crops.split(',').map((c) => `<span class="crop-tag">${c.trim()}</span>`).join('')
    : '';

  // Google Maps Direction URL
  let navUrl = `https://www.google.com/maps/dir/?api=1&destination=${cs.latitude},${cs.longitude}`;
  if (state.farmerCoords && state.farmerCoords.latitude && state.farmerCoords.longitude) {
    navUrl = `https://www.google.com/maps/dir/?api=1&origin=${state.farmerCoords.latitude},${state.farmerCoords.longitude}&destination=${cs.latitude},${cs.longitude}`;
  }

  const isNearest = index === 0 && cs.distance_km !== undefined;

  return `
    <div class="storage-card ${isNearest ? 'card-highlight-nearest' : ''}" id="storage-card-${cs.id}">
      <div class="card-header">
        <div class="card-title-group">
          <div class="card-badges">
            <span class="verified-badge">✓ ${t('verifiedBadge')}</span>
            ${isNearest ? '<span class="nearest-badge">⭐ NEAREST (सबसे पास)</span>' : ''}
            ${cs.rating ? `<span class="rating-badge">★ ${cs.rating}</span>` : ''}
          </div>
          <h3 class="storage-name">${escapeHtml(cs.name)}</h3>
          <p class="storage-address">📍 ${escapeHtml(cs.address)}${cs.village_or_area ? `, ${escapeHtml(cs.village_or_area)}` : ''}, ${escapeHtml(cs.district)}, ${escapeHtml(cs.state)} ${cs.pincode ? ` - ${cs.pincode}` : ''}</p>
        </div>

        ${
          cs.distance_km !== undefined
            ? `
          <div class="card-distance-box">
            <span class="dist-num">${cs.distance_km}</span>
            <span class="dist-unit">km</span>
            <span class="dist-lbl">${t('distanceAway')}</span>
            ${cs.drive_time_text ? `<span class="dist-drive">🚜 ~${cs.drive_time_text}</span>` : ''}
          </div>
        `
            : ''
        }
      </div>

      <div class="card-body">
        ${
          cs.description
            ? `<p class="card-description-snippet">${escapeHtml(cs.description.substring(0, 160))}...</p>`
            : ''
        }

        <div class="card-specs-grid">
          <div class="spec-item">
            <span class="spec-icon">🧊</span>
            <div>
              <span class="spec-lbl">${t('capacity')}</span>
              <strong class="spec-val">${escapeHtml(cs.storage_capacity || 'N/A')}</strong>
            </div>
          </div>

          <div class="spec-item">
            <span class="spec-icon">👤</span>
            <div>
              <span class="spec-lbl">${t('manager')}</span>
              <strong class="spec-val">${escapeHtml(cs.contact_person || t('contactNotAvailable'))}</strong>
            </div>
          </div>
        </div>

        ${
          cropsList
            ? `
          <div class="card-crops">
            <div class="crop-tags-container">${cropsList}</div>
          </div>
        `
            : ''
        }
      </div>

      <!-- Large Farmer Actions -->
      <div class="card-actions">
        ${
          hasPhone
            ? `<a href="tel:${cleanPhone}" class="btn btn-call" title="Call Cold Storage Facility">
                <span class="btn-icon">📞</span>
                <span>${t('callBtn')}</span>
               </a>`
            : `<button class="btn btn-disabled" disabled>
                <span class="btn-icon">📞</span>
                <span>Phone N/A</span>
               </button>`
        }

        <a href="${navUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-navigate" title="Open Google Maps Directions">
          <span class="btn-icon">🧭</span>
          <span>${t('navigateBtn')}</span>
        </a>

        <button class="btn btn-details btn-view-details" data-id="${cs.id}" title="View Complete Facility Specifications">
          <span>${t('detailsBtn')}</span>
        </button>
      </div>
    </div>
  `;
}

// -------------------------------------------------------------
// Crop Filters & View Toggles
// -------------------------------------------------------------
function initCropFilters() {
  const cropChips = document.querySelectorAll('.crop-chip');
  cropChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      cropChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');

      const crop = chip.getAttribute('data-crop') || '';
      state.selectedCrop = crop;

      if (state.farmerCoords) {
        executeNearbySearch(state.farmerCoords.latitude, state.farmerCoords.longitude);
      }
    });
  });
}

function initViewToggles() {
  const viewBtns = document.querySelectorAll('.view-toggle-btn');
  const layoutContainer = document.querySelector('.results-layout');

  viewBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      viewBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');

      const view = btn.getAttribute('data-view');
      state.activeView = view;

      if (layoutContainer) {
        layoutContainer.className = `results-layout view-${view}`;
      }
      MapController.invalidate();
    });
  });
}

// -------------------------------------------------------------
// Modal & Calculator
// -------------------------------------------------------------
function initModalListeners() {
  const modal = document.getElementById('storage-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const backdrop = document.getElementById('modal-backdrop');

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', closeModal);
}

async function openStorageModal(id) {
  const modal = document.getElementById('storage-modal');
  const modalBody = document.getElementById('modal-dynamic-content');
  if (!modal || !modalBody) return;

  setModalLoading(true);
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';

  try {
    const res = await Api.getStorageDetails(id);
    const cs = res.cold_storage;
    state.selectedStorage = cs;

    let navUrl = `https://www.google.com/maps/dir/?api=1&destination=${cs.latitude},${cs.longitude}`;
    if (state.farmerCoords) {
      navUrl = `https://www.google.com/maps/dir/?api=1&origin=${state.farmerCoords.latitude},${state.farmerCoords.longitude}&destination=${cs.latitude},${cs.longitude}`;
    }

    const cleanPhone = cs.phone_number ? cs.phone_number.replace(/\s+/g, '') : '';
    const shareText = encodeURIComponent(`*${cs.name}*\n📍 ${cs.address}, ${cs.district}\n📞 Phone: ${cs.phone_number || 'N/A'}\n🧊 Capacity: ${cs.storage_capacity || 'N/A'}`);

    modalBody.innerHTML = `
      <div class="modal-facility-hero">
        <div class="modal-hero-tags">
          <span class="verified-badge">✓ ${t('verifiedBadge')}</span>
          ${cs.rating ? `<span class="rating-badge">★ ${cs.rating} Rating</span>` : ''}
        </div>
        <h2 class="modal-facility-title">${escapeHtml(cs.name)}</h2>
        <p class="modal-facility-address">📍 ${escapeHtml(cs.address)}${cs.village_or_area ? `, ${escapeHtml(cs.village_or_area)}` : ''}, ${escapeHtml(cs.district)}, ${escapeHtml(cs.state)} ${cs.pincode ? ` - ${cs.pincode}` : ''}</p>

        <div class="modal-cta-bar">
          ${
            cleanPhone
              ? `<a href="tel:${cleanPhone}" class="btn btn-call btn-modal-cta">
                  <span class="btn-icon">📞</span>
                  <span>${t('callBtn')} (${cs.phone_number})</span>
                 </a>`
              : ''
          }
          <a href="${navUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-navigate btn-modal-cta">
            <span class="btn-icon">🧭</span>
            <span>${t('navigateBtn')}</span>
          </a>
          <a href="https://api.whatsapp.com/send?text=${shareText}" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp btn-modal-cta">
            <span>💬 WhatsApp Share</span>
          </a>
        </div>
      </div>

      <div class="modal-sections">
        ${
          cs.description
            ? `
          <div class="modal-section">
            <h3 class="modal-sec-title">🌾 ${t('modalOverview')}</h3>
            <p class="modal-desc-text">${escapeHtml(cs.description)}</p>
          </div>
        `
            : ''
        }

        <div class="modal-section">
          <h3 class="modal-sec-title">🧊 ${t('modalStorageSpecs')}</h3>
          <div class="modal-specs-table">
            <div class="modal-spec-row">
              <span class="modal-spec-key">Storage Capacity:</span>
              <strong class="modal-spec-val">${escapeHtml(cs.storage_capacity || 'N/A')}</strong>
            </div>
            <div class="modal-spec-row">
              <span class="modal-spec-key">Technology Type:</span>
              <strong class="modal-spec-val">${escapeHtml(cs.cold_storage_type || 'Ammonia Refrigeration')}</strong>
            </div>
            <div class="modal-spec-row">
              <span class="modal-spec-key">Temperature Range:</span>
              <strong class="modal-spec-val">${escapeHtml(cs.temperature_range || '0°C to 10°C')}</strong>
            </div>
            <div class="modal-spec-row">
              <span class="modal-spec-key">Suitable Produce:</span>
              <strong class="modal-spec-val">${escapeHtml(cs.suitable_crops || 'All Agricultural Crops')}</strong>
            </div>
          </div>
        </div>

        <div class="modal-section">
          <h3 class="modal-sec-title">👤 ${t('modalContactInfo')}</h3>
          <div class="modal-specs-table">
            <div class="modal-spec-row">
              <span class="modal-spec-key">Chief Manager / In-Charge:</span>
              <strong class="modal-spec-val">${escapeHtml(cs.contact_person || t('contactNotAvailable'))}</strong>
            </div>
            <div class="modal-spec-row">
              <span class="modal-spec-key">Primary Phone:</span>
              <strong class="modal-spec-val">${escapeHtml(cs.phone_number || 'N/A')}</strong>
            </div>
            ${
              cs.alternate_phone_number
                ? `
              <div class="modal-spec-row">
                <span class="modal-spec-key">Alternate Phone:</span>
                <strong class="modal-spec-val">${escapeHtml(cs.alternate_phone_number)}</strong>
              </div>
            `
                : ''
            }
            ${
              cs.email
                ? `
              <div class="modal-spec-row">
                <span class="modal-spec-key">Email:</span>
                <strong class="modal-spec-val">${escapeHtml(cs.email)}</strong>
              </div>
            `
                : ''
            }
            <div class="modal-spec-row">
              <span class="modal-spec-key">Gate / Receiving Hours:</span>
              <strong class="modal-spec-val">${escapeHtml(cs.opening_hours || '06:00 AM - 09:00 PM')}</strong>
            </div>
          </div>
        </div>

        ${
          cs.amenities
            ? `
          <div class="modal-section">
            <h3 class="modal-sec-title">🏢 ${t('modalAmenities')}</h3>
            <p class="modal-desc-text">${escapeHtml(cs.amenities)}</p>
          </div>
        `
            : ''
        }

        ${
          cs.certifications
            ? `
          <div class="modal-section">
            <h3 class="modal-sec-title">📜 ${t('modalCertifications')}</h3>
            <p class="modal-desc-text">${escapeHtml(cs.certifications)}</p>
          </div>
        `
            : ''
        }

        <!-- Farmer Calculator -->
        <div class="modal-section calculator-card">
          <h3 class="modal-sec-title">🧮 ${t('modalCalculator')}</h3>
          <p class="calc-sub">Estimate how many Metric Tonnes (MT) of cold storage space and monthly rent you need for your harvest.</p>

          <div class="calc-form">
            <div class="calc-field">
              <label for="calc-crop">${t('calcCropLabel')}</label>
              <select id="calc-crop" class="calc-select">
                <option value="potato">🥔 Potato (आलू) - ₹40/bag/mo</option>
                <option value="onion">🧅 Onion (प्याज) - ₹45/bag/mo</option>
                <option value="garlic">🧄 Garlic (लहसुन) - ₹55/bag/mo</option>
                <option value="apple">🍎 Apple (सेब) - ₹75/crate/mo</option>
                <option value="vegetable">🥦 Vegetables (सब्जी) - ₹50/crate/mo</option>
                <option value="spices">🌶️ Spices (मसाले) - ₹60/bag/mo</option>
              </select>
            </div>

            <div class="calc-field">
              <label for="calc-bags">${t('calcBagsLabel')}</label>
              <input type="number" id="calc-bags" class="calc-input" value="200" min="1" max="100000">
            </div>

            <button type="button" class="btn btn-primary" id="btn-run-calc">${t('calcEstimateBtn')}</button>

            <div id="calc-result" class="calc-result-box" style="display: none;"></div>
          </div>
        </div>
      </div>
    `;

    // Hook calculator
    document.getElementById('btn-run-calc')?.addEventListener('click', runStorageCalculator);
  } catch (err) {
    modalBody.innerHTML = `<p class="error-msg">Failed to load details: ${escapeHtml(err.message)}</p>`;
  } finally {
    setModalLoading(false);
  }
}

function runStorageCalculator() {
  const cropSelect = document.getElementById('calc-crop');
  const bagsInput = document.getElementById('calc-bags');
  const resultBox = document.getElementById('calc-result');

  if (!cropSelect || !bagsInput || !resultBox) return;

  const crop = cropSelect.value;
  const count = parseInt(bagsInput.value, 10) || 0;

  if (count <= 0) {
    resultBox.textContent = 'Please enter a valid bag/crate count.';
    resultBox.style.display = 'block';
    return;
  }

  // 1 Bag = 50 kg -> 20 bags = 1 MT (Metric Tonne)
  const metricTonnes = (count * 50) / 1000;

  const rates = {
    potato: 40,
    onion: 45,
    garlic: 55,
    apple: 75,
    vegetable: 50,
    spices: 60
  };

  const costPerUnit = rates[crop] || 45;
  const totalCost = count * costPerUnit;

  resultBox.innerHTML = `
    <strong>📊 Storage Requirement Estimate:</strong><br>
    <span>${t('calcResultText', { mt: metricTonnes.toFixed(2), cost: totalCost.toLocaleString('en-IN') })}</span>
  `;
  resultBox.style.display = 'block';
}

function closeModal() {
  const modal = document.getElementById('storage-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

function setModalLoading(isLoading) {
  const modalBody = document.getElementById('modal-dynamic-content');
  if (modalBody && isLoading) {
    modalBody.innerHTML = `
      <div class="modal-loading-box">
        <div class="spinner"></div>
        <p>Loading full facility specifications & contacts...</p>
      </div>
    `;
  }
}

// -------------------------------------------------------------
// UI Utilities
// -------------------------------------------------------------
function setLoading(isLoading) {
  state.loading = isLoading;
  const loader = document.getElementById('global-loader');
  if (loader) {
    loader.style.display = isLoading ? 'flex' : 'none';
  }
}

function showError(message, isGpsFallback = false) {
  const box = document.getElementById('global-error-box');
  if (!box) return;

  box.innerHTML = `
    <div class="error-alert">
      <span class="alert-icon">⚠️</span>
      <div class="alert-text">
        <strong>Notice:</strong> ${escapeHtml(message)}
        ${
          isGpsFallback
            ? `<div class="alert-action">
                <button class="btn btn-sm btn-outline" id="btn-fallback-manual">✏️ Search by Village / District</button>
               </div>`
            : ''
        }
      </div>
    </div>
  `;
  box.style.display = 'block';

  document.getElementById('btn-fallback-manual')?.addEventListener('click', () => {
    switchTab('manual');
    box.style.display = 'none';
  });
}

function clearError() {
  const box = document.getElementById('global-error-box');
  if (box) {
    box.style.display = 'none';
    box.innerHTML = '';
  }
}

function escapeHtml(unsafe) {
  if (typeof unsafe !== 'string') return unsafe;
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
