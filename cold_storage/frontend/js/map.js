let map = null;
let farmerMarker = null;
let storageMarkers = [];
let radiusCircles = [];

export const MapController = {
  /**
   * Initializes the Leaflet map in the container
   */
  init(containerId = 'map-container', initialLat = 20.5937, initialLng = 78.9629, zoom = 5) {
    if (typeof window.L === 'undefined') {
      console.warn('Leaflet map library is not loaded. Skipping map initialization.');
      return;
    }

    try {
      if (map) {
        map.remove();
        map = null;
      }

      const container = document.getElementById(containerId);
      if (!container) return;

      map = L.map(containerId, {
        zoomControl: true,
        scrollWheelZoom: true
      }).setView([initialLat, initialLng], zoom);

      // OpenStreetMap standard tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors | FarmFusion'
      }).addTo(map);

      setTimeout(() => {
        if (map) map.invalidateSize();
      }, 300);
    } catch (err) {
      console.warn('Map initialization error:', err.message);
    }
  },

  /**
   * Render farmer location and cold storages
   */
  renderResults(originCoords, storages, onSelectStorage = null, activeRadiusKm = null) {
    if (typeof window.L === 'undefined') {
      console.warn('Leaflet not loaded. Rendering list only.');
      return;
    }

    try {
      if (!map) this.init();
      if (!map) return;

      this.clearLayers();
      const bounds = L.latLngBounds();

      // 1. Plot Farmer's Pin (if available)
      if (originCoords && originCoords.latitude && originCoords.longitude) {
        const farmerIcon = L.divIcon({
          className: 'custom-farmer-pin',
          html: `
            <div class="farmer-marker-pulse"></div>
            <div class="farmer-marker-dot">📍</div>
          `,
          iconSize: [36, 36],
          iconAnchor: [18, 18]
        });

        farmerMarker = L.marker([originCoords.latitude, originCoords.longitude], {
          icon: farmerIcon,
          zIndexOffset: 1000
        })
          .addTo(map)
          .bindPopup(`
            <div class="map-popup-farmer">
              <strong>🧑‍🌾 Your Location</strong>
              <p>Lat: ${originCoords.latitude.toFixed(4)}, Lng: ${originCoords.longitude.toFixed(4)}</p>
            </div>
          `);

        bounds.extend([originCoords.latitude, originCoords.longitude]);

        // Plot search radius circle if specified
        if (activeRadiusKm) {
          const circle = L.circle([originCoords.latitude, originCoords.longitude], {
            color: '#16a34a',
            fillColor: '#22c55e',
            fillOpacity: 0.08,
            radius: activeRadiusKm * 1000,
            weight: 2,
            dashArray: '5, 5'
          }).addTo(map);
          radiusCircles.push(circle);
        }
      }

      // 2. Plot Cold Storage Pins
      if (Array.isArray(storages)) {
        storages.forEach((cs, idx) => {
          const isTop = idx === 0;
          const storageIcon = L.divIcon({
            className: 'custom-storage-pin',
            html: `
              <div class="storage-marker-badge ${isTop ? 'nearest' : ''}">
                <span class="badge-icon">🧊</span>
                ${cs.distance_km !== undefined ? `<span class="badge-dist">${cs.distance_km} km</span>` : ''}
              </div>
            `,
            iconSize: [42, 42],
            iconAnchor: [21, 21]
          });

          const latLng = [cs.latitude, cs.longitude];
          bounds.extend(latLng);

          const navUrl = originCoords
            ? `https://www.google.com/maps/dir/?api=1&origin=${originCoords.latitude},${originCoords.longitude}&destination=${cs.latitude},${cs.longitude}`
            : `https://www.google.com/maps/dir/?api=1&destination=${cs.latitude},${cs.longitude}`;

          const marker = L.marker(latLng, { icon: storageIcon })
            .addTo(map)
            .bindPopup(`
              <div class="map-popup-storage">
                <h4>${cs.name}</h4>
                <p class="popup-addr">📍 ${cs.address}, ${cs.district}</p>
                ${cs.distance_km !== undefined ? `<p class="popup-dist">📏 <strong>${cs.distance_km} km away</strong></p>` : ''}
                <p class="popup-cap">🧊 Capacity: ${cs.storage_capacity || 'N/A'}</p>
                <div class="popup-actions">
                  ${
                    cs.phone_number
                      ? `<a href="tel:${cs.phone_number.replace(/\s+/g, '')}" class="btn-popup-call">📞 Call</a>`
                      : `<span class="badge-no-contact">No Phone</span>`
                  }
                  <a href="${navUrl}" target="_blank" rel="noopener" class="btn-popup-nav">🧭 Navigate</a>
                </div>
              </div>
            `);

          marker.on('click', () => {
            if (onSelectStorage) onSelectStorage(cs.id);
          });

          storageMarkers.push(marker);
        });
      }

      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 13 });
      }
    } catch (err) {
      console.warn('Map rendering error:', err.message);
    }
  },

  clearLayers() {
    try {
      if (farmerMarker && map) {
        map.removeLayer(farmerMarker);
        farmerMarker = null;
      }
      storageMarkers.forEach((m) => map && map.removeLayer(m));
      storageMarkers = [];
      radiusCircles.forEach((c) => map && map.removeLayer(c));
      radiusCircles = [];
    } catch (err) {
      console.warn('Clear layers error:', err);
    }
  },

  invalidate() {
    try {
      if (map) {
        setTimeout(() => map.invalidateSize(), 200);
      }
    } catch (err) {
      // ignore
    }
  }
};
