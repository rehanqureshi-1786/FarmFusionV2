/**
 * High-Precision Distance & Transit Estimation Engine
 * Uses the Haversine formula and Indian rural-highway road curvature multipliers
 * to predict accurate distance and driving time for farmers.
 */

/**
 * Calculates great-circle geodesic distance using Haversine formula
 * @param {number} lat1 Latitude of origin in degrees
 * @param {number} lon1 Longitude of origin in degrees
 * @param {number} lat2 Latitude of destination in degrees
 * @param {number} lon2 Longitude of destination in degrees
 * @returns {number} Distance in kilometers
 */
export function calculateHaversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in kilometers
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  return Math.round(distance * 100) / 100;
}

function toRadians(degrees) {
  return (degrees * Math.PI) / 180;
}

/**
 * Predicts realistic road distance and driving duration for agricultural produce transport
 * In India, actual road route distance is typically ~1.20x to 1.30x the direct geodesic line.
 */
export function estimateRoadTransit(straightDistanceKm) {
  const roadMultiplier = 1.22; // Typical highway-village route multiplier
  const estimatedRoadKm = Math.round(straightDistanceKm * roadMultiplier * 10) / 10;

  // Average commercial truck/tractor speed ~40 km/h in rural/mandi corridors
  const avgSpeedKmh = 42;
  const timeMinutes = Math.max(5, Math.round((estimatedRoadKm / avgSpeedKmh) * 60));

  let timeText = `${timeMinutes} mins`;
  if (timeMinutes >= 60) {
    const hrs = Math.floor(timeMinutes / 60);
    const mins = timeMinutes % 60;
    timeText = `${hrs} hr ${mins > 0 ? `${mins} min` : ''}`;
  }

  return {
    road_distance_km: estimatedRoadKm,
    drive_time_minutes: timeMinutes,
    drive_time_text: timeText
  };
}

/**
 * Filters and sorts cold storages with progressive radius expansion & transit estimates
 */
export function searchNearbyWithExpansion(storages, userLat, userLng, requestedRadius = null, cropFilter = null) {
  // Compute distance & transit metrics for every facility
  const storagesWithMetrics = storages.map((item) => {
    const distanceKm = calculateHaversineDistance(userLat, userLng, item.latitude, item.longitude);
    const transit = estimateRoadTransit(distanceKm);

    return {
      ...item,
      distance_km: distanceKm,
      road_distance_km: transit.road_distance_km,
      drive_time_minutes: transit.drive_time_minutes,
      drive_time_text: transit.drive_time_text,
      google_maps_url: `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${item.latitude},${item.longitude}`
    };
  });

  // Filter by crop if specified
  let candidates = storagesWithMetrics;
  if (cropFilter && cropFilter.trim()) {
    const term = cropFilter.trim().toLowerCase();
    candidates = candidates.filter((item) =>
      item.suitable_crops && item.suitable_crops.toLowerCase().includes(term)
    );
  }

  // Explicit radius filter
  if (requestedRadius && !isNaN(requestedRadius) && Number(requestedRadius) > 0) {
    const targetRadius = Number(requestedRadius);
    const filtered = candidates
      .filter((item) => item.distance_km <= targetRadius)
      .sort((a, b) => a.distance_km - b.distance_km);

    return {
      storages: filtered,
      effectiveRadius: targetRadius,
      autoExpanded: false,
      totalFound: filtered.length
    };
  }

  // Progressive Expansion: 10km -> 25km -> 50km -> 100km
  const MIN_DESIRED_RESULTS = 2;
  const radiiSteps = [10, 25, 50, 100];
  let effectiveRadius = radiiSteps[0];
  let results = [];

  for (const radius of radiiSteps) {
    effectiveRadius = radius;
    results = candidates
      .filter((item) => item.distance_km <= radius)
      .sort((a, b) => a.distance_km - b.distance_km);

    if (results.length >= MIN_DESIRED_RESULTS) {
      break;
    }
  }

  if (results.length === 0) {
    results = candidates.sort((a, b) => a.distance_km - b.distance_km).slice(0, 5);
    effectiveRadius = results.length > 0 ? Math.ceil(results[results.length - 1].distance_km) : 100;
  }

  return {
    storages: results,
    effectiveRadius,
    autoExpanded: effectiveRadius > 10,
    totalFound: results.length
  };
}
