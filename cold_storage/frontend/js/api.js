/**
 * FarmFusion Cold Storage Finder - API Client
 */
export const Api = {
  baseUrl: '',

  /**
   * 1. Get Nearby Cold Storages
   */
  async getNearbyStorages(latitude, longitude, radius = null, crop = null) {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString()
    });

    if (radius && !isNaN(radius) && Number(radius) > 0) {
      params.append('radius', radius.toString());
    }

    if (crop && crop.trim()) {
      params.append('crop', crop.trim());
    }

    const res = await fetch(`${this.baseUrl}/cold-storages/nearby?${params.toString()}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `Failed to fetch nearby storages (${res.status})`);
    }
    return res.json();
  },

  /**
   * 2. Search Storages by District
   */
  async getStoragesByDistrict(state, district, crop = null) {
    const params = new URLSearchParams({
      state: state.trim(),
      district: district.trim()
    });

    if (crop && crop.trim()) {
      params.append('crop', crop.trim());
    }

    const res = await fetch(`${this.baseUrl}/cold-storages/district?${params.toString()}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `Failed to fetch district storages (${res.status})`);
    }
    return res.json();
  },

  /**
   * 3. Get Single Facility Details
   */
  async getStorageDetails(id) {
    const res = await fetch(`${this.baseUrl}/cold-storages/${encodeURIComponent(id)}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || `Failed to fetch storage details (${res.status})`);
    }
    return res.json();
  },

  /**
   * 4. Get Available States and Districts
   */
  async getLocations() {
    const res = await fetch(`${this.baseUrl}/api/locations`);
    if (!res.ok) {
      throw new Error('Failed to load Indian state and district directory.');
    }
    return res.json();
  },

  /**
   * 5. Geocode Address / Village
   */
  async geocode(address, district, state) {
    const params = new URLSearchParams();
    if (address) params.append('address', address.trim());
    if (district) params.append('district', district.trim());
    if (state) params.append('state', state.trim());

    const res = await fetch(`${this.baseUrl}/api/geocode?${params.toString()}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || 'Geocoding failed for the given address.');
    }
    return res.json();
  },

  /**
   * 6. Live Village, Mandi & Tehsil Auto-Suggest
   */
  async searchVillages(query, state = null, district = null) {
    const params = new URLSearchParams({ q: query.trim() });
    if (state) params.append('state', state.trim());
    if (district) params.append('district', district.trim());

    const res = await fetch(`${this.baseUrl}/api/villages?${params.toString()}`);
    if (!res.ok) return { success: false, suggestions: [] };
    return res.json();
  },

  /**
   * 7. Postal PIN Code Direct Lookup
   */
  async lookupPinCode(pin) {
    const res = await fetch(`${this.baseUrl}/api/pincode/${encodeURIComponent(pin.trim())}`);
    if (!res.ok) return { success: false };
    return res.json();
  }
};
