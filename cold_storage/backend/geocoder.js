import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const locationsPath = path.join(__dirname, 'data', 'india_locations.json');
const ruralPath = path.join(__dirname, 'data', 'rural_villages.json');

const indiaLocations = JSON.parse(fs.readFileSync(locationsPath, 'utf8'));
const ruralVillages = fs.existsSync(ruralPath) ? JSON.parse(fs.readFileSync(ruralPath, 'utf8')) : {};

// Comprehensive Indian Postal 6-digit PIN Code & 3/4-digit Circle Mapping for high precision offline fallback
const pinCodeMap = {
  // Rajasthan
  '302001': { lat: 26.9196, lng: 75.8010, area: 'Jaipur GPO' },
  '302029': { lat: 26.8041, lng: 75.7482, area: 'Muhana Mandi, Jaipur' },
  '303702': { lat: 27.1724, lng: 75.7214, area: 'Chomu, Jaipur' },
  '303301': { lat: 26.8333, lng: 76.0500, area: 'Bassi, Jaipur' },
  '303007': { lat: 26.8167, lng: 75.5500, area: 'Bagru, Jaipur' },
  '303103': { lat: 27.3833, lng: 75.9667, area: 'Shahpura, Jaipur' },
  '303901': { lat: 26.6000, lng: 75.9500, area: 'Chaksu, Jaipur' },
  '303328': { lat: 26.9667, lng: 75.3833, area: 'Jobner, Jaipur' },
  '303712': { lat: 27.2333, lng: 75.6500, area: 'Govindgarh, Jaipur' },
  '303338': { lat: 27.1500, lng: 75.3667, area: 'Renwal, Jaipur' },
  '303008': { lat: 26.6833, lng: 75.2333, area: 'Dudu, Jaipur' },
  '303108': { lat: 27.7000, lng: 76.2000, area: 'Kotputli, Jaipur' },

  '342001': { lat: 26.2918, lng: 73.0168, area: 'Jodhpur City' },
  '342005': { lat: 26.2210, lng: 73.0110, area: 'Bhagat Ki Kothi, Jodhpur' },
  '342301': { lat: 27.1333, lng: 72.3667, area: 'Phalodi, Jodhpur' },
  '342303': { lat: 26.7333, lng: 72.9000, area: 'Osian, Jodhpur' },
  '342601': { lat: 26.3833, lng: 73.5333, area: 'Pipar City, Jodhpur' },
  '342602': { lat: 26.1833, lng: 73.7000, area: 'Bilara, Jodhpur' },
  '342305': { lat: 26.5333, lng: 73.0167, area: 'Mathania, Jodhpur' },

  '324005': { lat: 25.1420, lng: 75.8390, area: 'Anantpura / Bhamashah Mandi, Kota' },
  '326519': { lat: 24.6500, lng: 75.9500, area: 'Ramganj Mandi, Kota' },
  '325601': { lat: 24.9167, lng: 76.2833, area: 'Sangod, Kota' },
  '325201': { lat: 25.2667, lng: 76.1000, area: 'Digod, Kota' },
  '325004': { lat: 25.5000, lng: 76.5333, area: 'Itawa, Kota' },

  '301001': { lat: 27.5530, lng: 76.6346, area: 'Alwar City' },
  '301030': { lat: 27.5670, lng: 76.6890, area: 'MIA Industrial Area, Alwar' },
  '301411': { lat: 27.9333, lng: 76.8500, area: 'Tijara, Alwar' },
  '301405': { lat: 27.8167, lng: 76.7167, area: 'Kishangarh Bas, Alwar' },
  '301026': { lat: 27.5833, lng: 76.8167, area: 'Ramgarh, Alwar' },
  '301028': { lat: 27.8833, lng: 76.2833, area: 'Behror, Alwar' },
  '301705': { lat: 27.9833, lng: 76.3833, area: 'Neemrana, Alwar' },
  '301402': { lat: 27.6833, lng: 76.3500, area: 'Bansur, Alwar' },

  '335001': { lat: 29.9140, lng: 73.8920, area: 'Sri Ganganagar' },
  '335804': { lat: 29.3167, lng: 73.9000, area: 'Suratgarh, Sri Ganganagar' },
  '335051': { lat: 29.5333, lng: 73.4500, area: 'Raisinghnagar, Sri Ganganagar' },
  '335701': { lat: 29.1833, lng: 73.2000, area: 'Anupgarh, Sri Ganganagar' },
  '335062': { lat: 29.9833, lng: 74.0500, area: 'Sadulshahar, Sri Ganganagar' },

  '321001': { lat: 27.2152, lng: 77.5030, area: 'Bharatpur' },
  '321203': { lat: 27.4667, lng: 77.3333, area: 'Deeg, Bharatpur' },
  '321022': { lat: 27.6500, lng: 77.2667, area: 'Kaman, Bharatpur' },
  '321201': { lat: 27.3167, lng: 77.3833, area: 'Kumher, Bharatpur' },
  '321602': { lat: 27.2333, lng: 77.2000, area: 'Nadbai, Bharatpur' },
  '321401': { lat: 26.9000, lng: 77.2833, area: 'Bayana, Bharatpur' },
  '321303': { lat: 27.2080, lng: 77.4810, area: 'Sewar, Bharatpur' },

  '334001': { lat: 28.0229, lng: 73.3119, area: 'Bikaner' },
  '334803': { lat: 27.6000, lng: 73.4167, area: 'Nokha, Bikaner' },
  '331803': { lat: 28.1000, lng: 74.0167, area: 'Sri Dungargarh, Bikaner' },
  '334603': { lat: 28.5000, lng: 73.7500, area: 'Lunkaransar, Bikaner' },
  '334801': { lat: 27.8000, lng: 73.2833, area: 'Deshnoke, Bikaner' },

  // Delhi & NCR
  '110033': { lat: 28.7120, lng: 77.1720, area: 'Azadpur Mandi, Delhi' },
  '110040': { lat: 28.8527, lng: 77.0931, area: 'Narela, Delhi' },
  '110020': { lat: 28.5355, lng: 77.2711, area: 'Okhla, Delhi' },
  '110096': { lat: 28.6277, lng: 77.3271, area: 'Ghazipur Mandi, Delhi' },
  '131029': { lat: 28.9320, lng: 77.0890, area: 'Rai Food Park, Sonipat' },
  '131028': { lat: 28.8732, lng: 77.1264, area: 'Kundli, Sonipat' },
  '132001': { lat: 29.6910, lng: 76.9820, area: 'Karnal' },

  // Uttar Pradesh
  '282007': { lat: 27.2341, lng: 77.8821, area: 'Runkata, Agra' },
  '283111': { lat: 27.1350, lng: 78.1120, area: 'Kundol / Fatehabad, Agra' },
  '283126': { lat: 27.3110, lng: 78.0790, area: 'Khandauli, Agra' },
  '283125': { lat: 27.0167, lng: 78.1167, area: 'Shamshabad, Agra' },
  '283105': { lat: 27.1833, lng: 77.7667, area: 'Achhnera, Agra' },
  '283122': { lat: 27.0911, lng: 77.6611, area: 'Fatehpur Sikri, Agra' },
  '209502': { lat: 27.5500, lng: 79.3500, area: 'Kaimganj, Farrukhabad' },
  '209625': { lat: 27.3826, lng: 79.5804, area: 'Fatehgarh / Farrukhabad' },
  '209721': { lat: 27.1500, lng: 79.5200, area: 'Chhibramau, Kannauj' },
  '209725': { lat: 27.0543, lng: 79.9142, area: 'Kannauj City' },
  '204101': { lat: 27.5968, lng: 78.0519, area: 'Hathras City' },
  '204215': { lat: 27.4400, lng: 77.9900, area: 'Sadabad, Hathras' },
  '204216': { lat: 27.7000, lng: 78.0800, area: 'Sasni, Hathras' },
  '283203': { lat: 27.1592, lng: 78.3957, area: 'Firozabad' },
  '283141': { lat: 27.1000, lng: 78.6000, area: 'Shikohabad, Firozabad' },
  '281001': { lat: 27.4924, lng: 77.6737, area: 'Mathura City' },
  '281401': { lat: 27.7200, lng: 77.5000, area: 'Chhata, Mathura' },
  '281403': { lat: 27.7900, lng: 77.4300, area: 'Kosi Kalan, Mathura' },
  '221001': { lat: 25.3176, lng: 82.9739, area: 'Varanasi City' },
  '221311': { lat: 25.2600, lng: 82.8500, area: 'Raja Talab, Varanasi' },
  '273001': { lat: 26.7606, lng: 83.3732, area: 'Gorakhpur' },
  '273152': { lat: 26.8300, lng: 83.5300, area: 'Pipraich, Gorakhpur' },

  // Maharashtra
  '422001': { lat: 19.9975, lng: 73.7898, area: 'Nashik' },
  '422207': { lat: 20.1025, lng: 73.8420, area: 'Mohadi, Nashik' },
  '422209': { lat: 20.1740, lng: 73.9870, area: 'Pimpalgaon Baswant, Nashik' },
  '422306': { lat: 20.1461, lng: 74.2289, area: 'Lasalgaon, Nashik' },
  '422303': { lat: 20.0833, lng: 74.1167, area: 'Niphad, Nashik' },
  '423401': { lat: 20.0417, lng: 74.4833, area: 'Yeola, Nashik' },
  '422103': { lat: 19.8500, lng: 74.0000, area: 'Sinnar, Nashik' },
  '425001': { lat: 21.0077, lng: 75.5626, area: 'Jalgaon' },
  '425508': { lat: 21.2500, lng: 76.0300, area: 'Raver, Jalgaon' },
  '413304': { lat: 17.6700, lng: 75.3300, area: 'Pandharpur, Solapur' },
  '413307': { lat: 17.4300, lng: 75.1800, area: 'Sangola, Solapur' },
  '410505': { lat: 19.1200, lng: 73.9700, area: 'Narayangaon / Junnar, Pune' },
  '413102': { lat: 18.1500, lng: 74.5800, area: 'Baramati, Pune' },

  // Punjab
  '144001': { lat: 31.3260, lng: 75.5762, area: 'Jalandhar City' },
  '144026': { lat: 31.2590, lng: 75.5210, area: 'Lambra, Jalandhar' },
  '144040': { lat: 31.1333, lng: 75.4833, area: 'Nakodar, Jalandhar' },
  '141120': { lat: 30.8410, lng: 75.9890, area: 'Sahnewal, Ludhiana' },
  '141401': { lat: 30.7000, lng: 76.2200, area: 'Khanna, Ludhiana' },
  '152116': { lat: 30.1400, lng: 74.1900, area: 'Abohar, Fazilka' },
  '152128': { lat: 30.0800, lng: 74.0500, area: 'Khuian Sarwar, Fazilka' },

  // Gujarat
  '385535': { lat: 24.2580, lng: 72.1810, area: 'Deesa, Banaskantha' },
  '385001': { lat: 24.1724, lng: 72.4346, area: 'Palanpur, Banaskantha' },
  '384002': { lat: 23.6010, lng: 72.3920, area: 'Mehsana' },
  '383205': { lat: 23.4300, lng: 72.8600, area: 'Prantij, Sabarkantha' },
  '362150': { lat: 21.0500, lng: 70.5200, area: 'Talala (Gir), Junagadh' },

  // Himachal Pradesh & J&K
  '171201': { lat: 31.1210, lng: 77.3540, area: 'Theog, Shimla' },
  '171202': { lat: 31.1200, lng: 77.5300, area: 'Kotkhai, Shimla' },
  '171207': { lat: 31.2000, lng: 77.7500, area: 'Rohru, Shimla' },
  '193201': { lat: 34.2988, lng: 74.4709, area: 'Sopore, Baramulla' },
  '192303': { lat: 33.7200, lng: 74.8300, area: 'Shopian Town' },
  '192121': { lat: 34.0200, lng: 74.9300, area: 'Pampore, Pulwama' },

  // Madhya Pradesh
  '452015': { lat: 22.7750, lng: 75.8340, area: 'Sanwer Road, Indore' },
  '458664': { lat: 24.2300, lng: 75.0000, area: 'Piplia Mandi, Mandsaur' },
  '458001': { lat: 24.0722, lng: 75.0688, area: 'Mandsaur City' },
  '458441': { lat: 24.4740, lng: 74.8710, area: 'Neemuch City' },

  // South India
  '563101': { lat: 13.1250, lng: 78.1420, area: 'Kolar APMC Mandi' },
  '563135': { lat: 13.3400, lng: 78.2100, area: 'Srinivaspur, Kolar' },
  '522001': { lat: 16.3190, lng: 80.4580, area: 'Guntur Mirchi Yard' },
  '517325': { lat: 13.5500, lng: 78.5000, area: 'Madanapalle, Chittoor' },
  '624619': { lat: 10.4820, lng: 77.7490, area: 'Oddanchatram Daily Market, Dindigul' },
  '625516': { lat: 9.7300, lng: 77.3000, area: 'Cumbum, Theni' },
  '635109': { lat: 12.7409, lng: 77.8253, area: 'Hosur, Krishnagiri' },

  // Bihar & Bengal & North East
  '803201': { lat: 25.5120, lng: 85.3140, area: 'Fatuha, Patna' },
  '843109': { lat: 26.1900, lng: 85.3000, area: 'Kanti / Shahi Litchi Hub, Muzaffarpur' },
  '848130': { lat: 25.8600, lng: 85.6500, area: 'Tajpur, Samastipur' },
  '712409': { lat: 22.8100, lng: 88.2300, area: 'Singur, Hooghly' },
  '735210': { lat: 26.6000, lng: 89.0200, area: 'Dhupguri, Jalpaiguri' },
  '781124': { lat: 26.0500, lng: 91.4300, area: 'Chaygaon / Tihu, Kamrup Rural' }
};

// 2-digit Circle prefix fallback for any 6-digit Indian PIN code
const pinCirclePrefixes = {
  '11': { state: 'Delhi NCR', lat: 28.6139, lng: 77.2090 },
  '12': { state: 'Haryana', lat: 29.0588, lng: 76.0856 },
  '13': { state: 'Haryana', lat: 29.9695, lng: 76.8783 },
  '14': { state: 'Punjab', lat: 31.1471, lng: 75.3412 },
  '15': { state: 'Punjab', lat: 30.2110, lng: 74.9455 },
  '16': { state: 'Chandigarh & Punjab', lat: 30.7333, lng: 76.7794 },
  '17': { state: 'Himachal Pradesh', lat: 31.1048, lng: 77.1734 },
  '18': { state: 'Jammu and Kashmir', lat: 32.7266, lng: 74.8570 },
  '19': { state: 'Jammu and Kashmir', lat: 34.0837, lng: 74.7973 },
  '20': { state: 'Uttar Pradesh', lat: 27.8974, lng: 78.0880 },
  '21': { state: 'Uttar Pradesh', lat: 26.4499, lng: 80.3319 },
  '22': { state: 'Uttar Pradesh', lat: 26.8467, lng: 80.9462 },
  '23': { state: 'Uttar Pradesh', lat: 25.3176, lng: 82.9739 },
  '24': { state: 'Uttarakhand & UP', lat: 30.3165, lng: 78.0322 },
  '25': { state: 'Uttar Pradesh', lat: 28.9845, lng: 77.7064 },
  '26': { state: 'Uttar Pradesh', lat: 28.3670, lng: 79.4304 },
  '27': { state: 'Uttar Pradesh', lat: 26.7606, lng: 83.3732 },
  '28': { state: 'Uttar Pradesh', lat: 27.1767, lng: 78.0081 },
  '30': { state: 'Rajasthan', lat: 26.9124, lng: 75.7873 },
  '31': { state: 'Rajasthan', lat: 24.5854, lng: 73.7125 },
  '32': { state: 'Rajasthan', lat: 25.2138, lng: 75.8648 },
  '33': { state: 'Rajasthan', lat: 28.0229, lng: 73.3119 },
  '34': { state: 'Rajasthan', lat: 26.2389, lng: 73.0243 },
  '36': { state: 'Gujarat', lat: 22.3039, lng: 70.8022 },
  '37': { state: 'Gujarat', lat: 23.2420, lng: 69.6669 },
  '38': { state: 'Gujarat', lat: 23.0225, lng: 72.5714 },
  '39': { state: 'Gujarat', lat: 21.1702, lng: 72.8311 },
  '40': { state: 'Maharashtra & Goa', lat: 18.9220, lng: 72.8347 },
  '41': { state: 'Maharashtra', lat: 18.5204, lng: 73.8567 },
  '42': { state: 'Maharashtra', lat: 19.9975, lng: 73.7898 },
  '43': { state: 'Maharashtra', lat: 19.8762, lng: 75.3433 },
  '44': { state: 'Maharashtra', lat: 21.1458, lng: 79.0882 },
  '45': { state: 'Madhya Pradesh', lat: 22.7196, lng: 75.8577 },
  '46': { state: 'Madhya Pradesh', lat: 23.2599, lng: 77.4126 },
  '47': { state: 'Madhya Pradesh', lat: 26.2183, lng: 78.1828 },
  '48': { state: 'Madhya Pradesh', lat: 23.1815, lng: 79.9864 },
  '49': { state: 'Chhattisgarh', lat: 21.2514, lng: 81.6296 },
  '50': { state: 'Telangana', lat: 17.3850, lng: 78.4867 },
  '51': { state: 'Andhra Pradesh', lat: 14.6819, lng: 77.6006 },
  '52': { state: 'Andhra Pradesh', lat: 16.3067, lng: 80.4365 },
  '53': { state: 'Andhra Pradesh', lat: 17.6868, lng: 83.2185 },
  '56': { state: 'Karnataka', lat: 12.9716, lng: 77.5946 },
  '57': { state: 'Karnataka', lat: 13.3161, lng: 75.7720 },
  '58': { state: 'Karnataka', lat: 15.4589, lng: 75.0078 },
  '59': { state: 'Karnataka', lat: 15.8497, lng: 74.4977 },
  '60': { state: 'Tamil Nadu', lat: 13.0827, lng: 80.2707 },
  '61': { state: 'Tamil Nadu', lat: 10.7905, lng: 78.7047 },
  '62': { state: 'Tamil Nadu', lat: 9.9252, lng: 78.1198 },
  '63': { state: 'Tamil Nadu', lat: 11.6643, lng: 78.1460 },
  '64': { state: 'Tamil Nadu', lat: 11.0168, lng: 76.9558 },
  '67': { state: 'Kerala', lat: 11.2588, lng: 75.7804 },
  '68': { state: 'Kerala', lat: 9.9816, lng: 76.2999 },
  '69': { state: 'Kerala', lat: 8.5241, lng: 76.9366 },
  '70': { state: 'West Bengal', lat: 22.5726, lng: 88.3639 },
  '71': { state: 'West Bengal', lat: 22.9038, lng: 88.3968 },
  '72': { state: 'West Bengal', lat: 22.4257, lng: 87.3199 },
  '73': { state: 'West Bengal', lat: 26.5405, lng: 88.7194 },
  '74': { state: 'West Bengal', lat: 23.4710, lng: 88.5565 },
  '75': { state: 'Odisha', lat: 20.2961, lng: 85.8245 },
  '76': { state: 'Odisha', lat: 19.3150, lng: 84.7941 },
  '77': { state: 'Odisha', lat: 21.4669, lng: 83.9812 },
  '78': { state: 'Assam & NE', lat: 26.1445, lng: 91.7362 },
  '79': { state: 'Northeast States', lat: 25.5788, lng: 91.8933 },
  '80': { state: 'Bihar', lat: 25.5941, lng: 85.1376 },
  '81': { state: 'Bihar & Jharkhand', lat: 25.2425, lng: 86.9842 },
  '82': { state: 'Bihar & Jharkhand', lat: 23.7957, lng: 86.4304 },
  '83': { state: 'Jharkhand', lat: 23.3441, lng: 85.3096 },
  '84': { state: 'Bihar', lat: 26.1226, lng: 85.3906 },
  '85': { state: 'Bihar', lat: 25.7771, lng: 87.4753 }
};

/**
 * Sanitizes rural address text by stripping common administrative prefixes & noise
 */
function cleanRuralSearchTerm(term) {
  if (!term) return '';
  let clean = term.trim();
  // Remove common Indian rural qualifiers
  clean = clean.replace(/\b(vill|village|gram|panchayat|gram panchayat|gp|tehsil|tahsil|taluk|taluka|block|mandi|krishi mandi|subzi mandi|post|p\.o\.|po|district|dist|road|bypas|bypass|nh-\d+|sh-\d+|khurd|kalan|basti|dhani|wadi|palli|gaon|gaonwada)\b/gi, ' ');
  // Remove punctuation
  clean = clean.replace(/[,\.\-\_\/\\#]/g, ' ');
  // Collapse spaces
  clean = clean.replace(/\s+/g, ' ').trim();
  return clean;
}

/**
 * Intelligent Rural & Urban Precision Geocoder.
 * Handles:
 * 1. 6-digit Indian Postal PIN codes (Exact + Postal Circle Fallback).
 * 2. Dedicated Rural Tehsils, Blocks, Mandis & Gram Panchayat Dictionary.
 * 3. OpenStreetMap Nominatim with structured village queries.
 * 4. District & State fallback centroids.
 */
export async function geocodeLocation(address, district, state) {
  const addrClean = (address || '').trim();
  const distClean = (district || '').trim();
  const stateClean = (state || '').trim();

  // 1. PIN Code Direct Lookup
  const pinMatch = addrClean.match(/\b([1-9][0-9]{5})\b/);
  if (pinMatch) {
    const pin = pinMatch[1];
    if (pinCodeMap[pin]) {
      const p = pinCodeMap[pin];
      return {
        latitude: p.lat,
        longitude: p.lng,
        displayName: `${p.area} (PIN: ${pin}), ${distClean || ''}, ${stateClean || ''}, India`,
        source: 'High-Precision Indian Postal PIN Database',
        accuracy: 'Exact PIN Centroid'
      };
    }

    // 2-digit PIN prefix circle fallback
    const prefix2 = pin.substring(0, 2);
    if (pinCirclePrefixes[prefix2]) {
      const circ = pinCirclePrefixes[prefix2];
      return {
        latitude: circ.lat,
        longitude: circ.lng,
        displayName: `Postal Division ${pin} (${circ.state}), India`,
        source: 'Indian Postal Circle Engine',
        accuracy: 'PIN Postal Division Centroid'
      };
    }
  }

  // 2. Rural Villages / Tehsils Dictionary Check
  const searchWord = cleanRuralSearchTerm(addrClean).toLowerCase();

  if (searchWord && stateClean && ruralVillages[stateClean]) {
    const stateRural = ruralVillages[stateClean];

    // Check under selected district first
    if (distClean && stateRural[distClean]) {
      const districtVillages = stateRural[distClean];
      for (const [villageName, coords] of Object.entries(districtVillages)) {
        const vClean = cleanRuralSearchTerm(villageName).toLowerCase();
        if (searchWord === vClean || searchWord.includes(vClean) || vClean.includes(searchWord)) {
          return {
            latitude: coords.lat,
            longitude: coords.lng,
            displayName: `${villageName} (${coords.type || 'Gram Panchayat / Tehsil'}), ${distClean}, ${stateClean}, India`,
            source: 'Rural Gram Panchayat & Tehsil Engine',
            accuracy: 'Exact Village Centroid'
          };
        }
      }
    }

    // Check across all districts of the state
    for (const [dName, villages] of Object.entries(stateRural)) {
      for (const [vName, coords] of Object.entries(villages)) {
        const vClean = cleanRuralSearchTerm(vName).toLowerCase();
        if (searchWord === vClean || searchWord.includes(vClean) || vClean.includes(searchWord)) {
          return {
            latitude: coords.lat,
            longitude: coords.lng,
            displayName: `${vName} (${coords.type || 'Gram Panchayat / Tehsil'}), ${dName}, ${stateClean}, India`,
            source: 'Rural Gram Panchayat & Tehsil Engine',
            accuracy: 'Exact Village Centroid'
          };
        }
      }
    }
  }

  // Check all states in rural dictionary if no state specified or not found yet
  if (searchWord) {
    for (const [sName, districts] of Object.entries(ruralVillages)) {
      for (const [dName, villages] of Object.entries(districts)) {
        for (const [vName, coords] of Object.entries(villages)) {
          const vClean = cleanRuralSearchTerm(vName).toLowerCase();
          if (searchWord === vClean || searchWord.includes(vClean)) {
            return {
              latitude: coords.lat,
              longitude: coords.lng,
              displayName: `${vName} (${coords.type || 'Gram Panchayat / Tehsil'}), ${dName}, ${sName}, India`,
              source: 'Rural Gram Panchayat & Tehsil Engine',
              accuracy: 'Exact Village Centroid'
            };
          }
        }
      }
    }
  }

  // 3. Online Structured Nominatim Search
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);

    const queryParts = [];
    if (addrClean) queryParts.push(addrClean);
    if (distClean) queryParts.push(distClean);
    if (stateClean) queryParts.push(stateClean);
    queryParts.push('India');

    const fullQuery = queryParts.join(', ');
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
      fullQuery
    )}&limit=1&countrycodes=in&addressdetails=1`;

    const response = await fetch(url, {
      headers: {
        'User-Agent': 'FarmFusionRuralColdChain/2.0 (agri-rural-app)'
      },
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      if (Array.isArray(data) && data.length > 0) {
        const item = data[0];
        return {
          latitude: parseFloat(item.lat),
          longitude: parseFloat(item.lon),
          displayName: item.display_name,
          source: 'OpenStreetMap High-Precision Geocoding API',
          accuracy: item.importance > 0.4 ? 'Exact Landmark/Village' : 'Regional'
        };
      }
    }
  } catch (err) {
    console.warn(`Online geocoding timeout for rural query "${addrClean}":`, err.message);
  }

  // 4. District & State Fallback
  if (stateClean && indiaLocations[stateClean]) {
    const stateDistricts = indiaLocations[stateClean];
    if (distClean && stateDistricts[distClean]) {
      const coords = stateDistricts[distClean];
      return {
        latitude: coords.lat,
        longitude: coords.lng,
        displayName: `${addrClean ? `${addrClean}, ` : ''}${distClean}, ${stateClean}, India (District Centroid)`,
        source: 'District Centroid Fallback',
        accuracy: 'District Hub'
      };
    }
  }

  // 5. Default Central Fallback
  return {
    latitude: 26.9124,
    longitude: 75.7873,
    displayName: 'Jaipur, Rajasthan, India',
    source: 'Regional Center Fallback',
    accuracy: 'Approximate'
  };
}

/**
 * Live Village, Tehsil & Mandi Auto-Suggest Search
 */
export function searchVillages(query, filterState = null, filterDistrict = null) {
  if (!query || query.trim().length < 2) return [];

  const q = cleanRuralSearchTerm(query).toLowerCase();
  const results = [];

  // 1. Match from PIN code database if numbers
  if (/^\d{2,6}$/.test(query.trim())) {
    const pinTerm = query.trim();
    for (const [pin, info] of Object.entries(pinCodeMap)) {
      if (pin.startsWith(pinTerm)) {
        results.push({
          name: `${info.area} (PIN: ${pin})`,
          village: info.area,
          type: 'Postal PIN Code',
          district: '',
          state: '',
          pincode: pin,
          latitude: info.lat,
          longitude: info.lng
        });
        if (results.length >= 10) return results;
      }
    }
  }

  // 2. Match from Rural Villages Dictionary
  for (const [state, districts] of Object.entries(ruralVillages)) {
    if (filterState && filterState.trim() && state.toLowerCase() !== filterState.trim().toLowerCase()) {
      continue;
    }

    for (const [district, villages] of Object.entries(districts)) {
      if (filterDistrict && filterDistrict.trim() && district.toLowerCase() !== filterDistrict.trim().toLowerCase()) {
        continue;
      }

      for (const [villageName, data] of Object.entries(villages)) {
        const vClean = cleanRuralSearchTerm(villageName).toLowerCase();
        if (vClean.includes(q) || villageName.toLowerCase().includes(q)) {
          results.push({
            name: `${villageName}, ${district}, ${state}`,
            village: villageName,
            type: data.type || 'Gram Panchayat / Tehsil',
            district,
            state,
            latitude: data.lat,
            longitude: data.lng
          });

          if (results.length >= 15) return results;
        }
      }
    }
  }

  return results;
}

/**
 * Resolves a 6-digit PIN code
 */
export function lookupPinCode(pin) {
  const cleanPin = (pin || '').trim();
  if (pinCodeMap[cleanPin]) {
    return {
      success: true,
      pin: cleanPin,
      ...pinCodeMap[cleanPin]
    };
  }

  const prefix2 = cleanPin.substring(0, 2);
  if (pinCirclePrefixes[prefix2]) {
    const circ = pinCirclePrefixes[prefix2];
    return {
      success: true,
      pin: cleanPin,
      area: `Postal Circle ${cleanPin}`,
      state: circ.state,
      lat: circ.lat,
      lng: circ.lng
    };
  }

  return { success: false };
}

export function getLocationsHierarchy() {
  const result = {};
  for (const [state, districts] of Object.entries(indiaLocations)) {
    result[state] = Object.keys(districts);
  }
  return result;
}
