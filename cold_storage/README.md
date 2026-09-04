# 🌾 FarmFusion - Nearby Cold Storage Finder

A complete, farmer-friendly web application and backend API system for finding the nearest agricultural cold storage facilities, checking capacity, placing direct calls to managers, and navigating turn-by-turn via Google Maps.

---

## 🌟 Key Features

### 1. Three Search Options for Farmers
- **📍 Option 1: Use My Current Location**
  - Instant GPS coordinates retrieval.
  - Automatic progressive radius expansion: searches within **10 km** first → auto-expands to **25 km** or **50 km** if insufficient facilities are nearby.
  - Calculates true distance using the **Haversine formula** and sorts facilities strictly from nearest to farthest.
  - Location permission is optional, with an immediate 1-tap fallback to Manual Search if denied.
- **✏️ Option 2: Enter Location Manually**
  - Search hierarchy: `State` → `District` → `Village / Area / Landmark / PIN Code`.
  - Converts address into coordinates via **OpenStreetMap Nominatim Geocoding API** with an offline centroid database fallback.
  - Works 100% without GPS permission.
- **🏙️ Option 3: Browse by District**
  - Explore all registered cold storage facilities in any selected state & district across India.

### 2. Comprehensive Cold Storage Facility Cards
Each result card displays:
- 🏭 **Facility Name** with sample/testing indicator badge
- 📏 **Distance from Farmer** (e.g. `5.2 km away`) sorted nearest to farthest
- 📍 **Full Address** with Village/Area, District, State, and PIN code
- 🧊 **Storage Capacity** (in Metric Tonnes) & 🌡️ **Temperature Zone**
- 🌾 **Suitable Crops** (Potatoes, Onions, Garlic, Apples, Tomatoes, Dairy, Spices, etc.)
- 👤 **Manager / Contact Person** (or *"Contact information not available."*)
- ⭐ **Rating** & 🕒 **Operating Hours**
- **Action Buttons**:
  - `[ 📞 Call ]` - Direct phone dialer link (`tel:+91...`).
  - `[ 🧭 Navigate ]` - Opens Google Maps directions with origin and destination coordinates.
  - `[ ℹ️ View Details ]` - Opens a full specification sheet and capacity calculator.

### 3. Interactive Map & Detailed Drawer
- **Interactive Leaflet Map**: Custom pulsing blue marker for the farmer, green pins with distance labels for cold storages, and visual search radius circles.
- **Farmer Storage Calculator**: Input crop type and number of 50 kg bags to estimate required space in Metric Tonnes and monthly cold storage cost.
- **Multilingual Support**: Real-time language switcher supporting **English** and **हिंदी (Hindi)**.
- **Produce Crop Filters**: Quick filter chips for Potatoes, Onions, Garlic, Apples, Tomatoes, Carrots, Spices, Dairy.

---

## 🏗️ Backend REST API Endpoints

### 1. Find Nearby Cold Storage
```http
GET /cold-storages/nearby?latitude=27.1767&longitude=78.0081&radius=25&crop=Potato
```
**Response:**
```json
{
  "success": true,
  "origin": { "latitude": 27.1767, "longitude": 78.0081 },
  "searchRadiusKm": 25,
  "autoExpanded": false,
  "count": 3,
  "results": [
    {
      "id": "CS-UP-AGR-002",
      "name": "Shree Radhey Multi-Chamber Cold Storage",
      "address": "Fatehabad Road, Vill. Kundol, Post Bamrauli Katara",
      "district": "Agra",
      "state": "Uttar Pradesh",
      "latitude": 27.1350,
      "longitude": 78.1120,
      "distance_km": 11.28,
      "phone_number": "+91 88991 22334",
      "storage_capacity": "12,000 MT",
      "suitable_crops": "Potatoes (Seed & Table), Spices, Dry Fruits"
    }
  ]
}
```

### 2. Search by District
```http
GET /cold-storages/district?state=Punjab&district=Jalandhar
```

### 3. Get Facility Details
```http
GET /cold-storages/CS-UP-AGR-001
```

### 4. Get Available States & Districts
```http
GET /api/locations
```

### 5. Geocode Address / Village
```http
GET /api/geocode?state=Maharashtra&district=Nashik&address=Pimpalgaon
```

---

## 🗄️ Database Schema (`cold_storages`)

| Column Name | Type | Description |
|---|---|---|
| `id` | `TEXT PRIMARY KEY` | Unique facility identifier (e.g. `CS-UP-AGR-001`) |
| `name` | `TEXT NOT NULL` | Name of the cold storage facility |
| `address` | `TEXT NOT NULL` | Full street / highway address |
| `village_or_area`| `TEXT` | Village, industrial area, or landmark |
| `district` | `TEXT NOT NULL` | District |
| `state` | `TEXT NOT NULL` | State |
| `pincode` | `TEXT` | 6-digit postal code |
| `latitude` | `REAL NOT NULL` | GPS Latitude |
| `longitude` | `REAL NOT NULL` | GPS Longitude |
| `phone_number` | `TEXT` | Primary contact phone number |
| `alternate_phone_number` | `TEXT` | Alternate / secondary phone number |
| `contact_person`| `TEXT` | Manager or owner name |
| `email` | `TEXT` | Email address |
| `rating` | `REAL` | Facility rating (1.0 to 5.0) |
| `opening_hours` | `TEXT` | Operating schedule |
| `storage_capacity` | `TEXT` | Storage capacity in Metric Tonnes (MT) |
| `suitable_crops` | `TEXT` | Comma-separated list of suitable produce |
| `cold_storage_type`| `TEXT` | Technology type (e.g. CA, Ammonia, Deep Freeze) |
| `temperature_range`| `TEXT` | Temperature range (e.g. `0°C to 10°C`) |
| `is_sample_data` | `INTEGER` | `1` indicates testing sample data |
| `created_at` | `DATETIME` | Timestamp |

---

## 🚀 Running the Application

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Server
```bash
npm start
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

### 3. Run Automated Tests
```bash
npm test
node backend/test_e2e.js
```
