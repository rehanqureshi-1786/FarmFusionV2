export const translations = {
  en: {
    appTitle: "FarmFusion Cold Storage",
    appSubtitle: "Find verified cold storage facilities, check capacity, call managers & navigate via Google Maps",
    verifiedNotice: "🌾 Official Verified Cold Chain Network across all villages, tehsils, mandis & agricultural clusters in India.",

    // Search Tabs (Simplified 2 Options)
    tabGps: "📍 Use My Current Location",
    tabManual: "✏️ Search by Village, Mandi or District",

    // GPS Tab
    gpsHeading: "Find Nearest Cold Storage Facilities",
    gpsDesc: "Tap the button below. We will calculate the exact distance and show the nearest verified cold storages.",
    btnLocateMe: "📍 Find Nearby Cold Storages",
    locating: "Locating your nearest facility...",
    gpsNote: "No GPS? You can easily search by selecting your Village, Mandi, PIN code or District above.",
    radiusLabel: "Distance:",
    radiusAuto: "Auto Distance",

    // Manual Tab
    manualHeading: "Search by Village, Mandi, PIN Code or District",
    manualDesc: "Enter your village, gram panchayat, tehsil, APMC mandi or 6-digit postal PIN code. Instant autocomplete across all Indian states.",
    stateLabel: "1. Select State",
    selectState: "-- Choose State --",
    districtLabel: "2. Select District",
    selectDistrict: "-- Choose District --",
    addressLabel: "3. Village / Gram Panchayat / Mandi / PIN Code",
    addressPlaceholder: "e.g. Khandauli, Chomu, Mohadi, Deesa, 282007 or Speak",
    btnSearchManual: "🔍 Search Cold Storages",
    voiceSearchTitle: "Click to Speak Village / Mandi Name",
    voiceListening: "🎙️ Listening... Please speak your village or mandi name",
    voiceNotSupported: "Voice search is not supported in this browser. Please type the location.",
    quickVillagesLabel: "🌾 Popular Rural Mandis & Clusters:",

    // Results
    resultsTitle: "Verified Cold Storage Facilities",
    resultsCount: "{count} facilities available",
    sortedNotice: "Sorted by nearest distance using Haversine algorithm & rural road factors",
    autoExpandedNotice: "Expanded search to {radius} km to find available cold storage facilities in rural areas.",
    cropFilterAll: "All Crops",
    viewList: "List",
    viewMap: "Map",
    viewSplit: "Split",
    noResultsTitle: "No Cold Storage Found Nearby",
    noResultsDesc: "No facilities found within this radius. Expand the search radius or select another rural area.",
    btnExpandRadius: "🔄 Search up to 50 km / 100 km",

    // Card Details
    distanceAway: "away",
    callBtn: "📞 CALL MANAGER",
    navigateBtn: "🧭 GOOGLE MAPS",
    detailsBtn: "ℹ️ Full Details",
    capacity: "Capacity",
    tempRange: "Temp",
    crops: "Accepted Crops",
    manager: "Chief Contact",
    contactNotAvailable: "Contact information not available.",
    verifiedBadge: "Verified Hub",

    // Modal
    modalTitle: "Cold Storage Facility Profile",
    modalOverview: "Facility Overview & Description",
    modalStorageSpecs: "Storage Technology & Specifications",
    modalContactInfo: "Contact & Management Details",
    modalAmenities: "Infrastructure & Amenities",
    modalCertifications: "Accreditations & Government Schemes",
    modalCalculator: "Farmer Storage Requirement Calculator",
    calcCropLabel: "Select Crop:",
    calcBagsLabel: "Number of 50 kg Bags:",
    calcEstimateBtn: "Calculate Capacity (MT) & Cost",
    calcResultText: "Required Space: {mt} Metric Tonnes (Estimated rent: ₹{cost} / month)",
    closeBtn: "Close",

    // Errors
    errGpsDenied: "Location access was denied. Please use the Village/District search tab above.",
    errGpsUnavailable: "GPS signal unavailable. Please use the 'Search by Village, Mandi or District' tab.",
    errGeocodeFail: "Could not pinpoint exact village. Showing results based on district centroid.",
    errMissingInputs: "Please enter a village, PIN code or select both State and District before searching.",
    errNetwork: "Network issue. Please check your internet connection."
  },
  hi: {
    appTitle: "फार्मफ्यूजन कोल्ड स्टोरेज",
    appSubtitle: "सत्यापित कोल्ड स्टोरेज खोजें, क्षमता देखें, सीधे बात करें और गूगल मैप्स से पहुंचें",
    verifiedNotice: "🌾 भारत के सभी गांवों, तहसीलों, मंडियों और ग्रामीण कृषि क्षेत्रों का सत्यापित नेटवर्क।",

    // Search Tabs
    tabGps: "📍 मेरे वर्तमान स्थान से खोजें",
    tabManual: "✏️ गांव, मंडी या जिले से खोजें",

    // GPS Tab
    gpsHeading: "अपने सबसे नजदीकी कोल्ड स्टोरेज खोजें",
    gpsDesc: "नीचे दिए गए बटन पर टैप करें। आपके खेत या गांव से सबसे नजदीकी कोल्ड स्टोरेज तुरंत दिखाई देंगे।",
    btnLocateMe: "📍 मेरे पास के कोल्ड स्टोरेज खोजें",
    locating: "नजदीकी केंद्र खोजे जा रहे हैं...",
    gpsNote: "जीपीएस काम नहीं कर रहा? आप ऊपर 'गांव, मंडी या जिले से खोजें' चुनकर सीधे गांव का नाम दर्ज कर सकते हैं।",
    radiusLabel: "दूरी दायरा:",
    radiusAuto: "स्वचालित दायरा",

    // Manual Tab
    manualHeading: "गांव, ग्राम पंचायत, मंडी, पिन कोड या जिला दर्ज करें",
    manualDesc: "अपने गांव, तहसील, एपीएमसी मंडी या 6-अंकों का पिन कोड दर्ज करें या बोलकर खोजें।",
    stateLabel: "1. राज्य चुनें",
    selectState: "-- राज्य चुनें --",
    districtLabel: "2. जिला चुनें",
    selectDistrict: "-- जिला चुनें --",
    addressLabel: "3. गांव / ग्राम पंचायत / मंडी / पिन कोड (या बोलें)",
    addressPlaceholder: "उदा. खंदौली, चोमू, मोहाडी, डीसा, 282007 या बोलकर बताएं",
    btnSearchManual: "🔍 कोल्ड स्टोरेज खोजें",
    voiceSearchTitle: "बोलकर गांव या मंडी का नाम खोजने के लिए दबाएं",
    voiceListening: "🎙️ सुन रहे हैं... कृपया अपने गांव या मंडी का नाम बोलें",
    voiceNotSupported: "इस ब्राउज़र में वॉइस सर्च उपलब्ध नहीं है। कृपया नाम टाइप करें।",
    quickVillagesLabel: "🌾 प्रमुख ग्रामीण मंडियां व कृषि क्षेत्र:",

    // Results
    resultsTitle: "उपलब्ध सत्यापित कोल्ड स्टोरेज",
    resultsCount: "{count} केंद्र उपलब्ध हैं",
    sortedNotice: "हवेरासीन सूत्र और ग्रामीण सड़क दूरी के आधार पर सबसे पास से दूर के क्रम में",
    autoExpandedNotice: "ग्रामीण क्षेत्रों में उपलब्ध कोल्ड स्टोरेज खोजने के लिए दायरा {radius} किमी किया गया।",
    cropFilterAll: "सभी फसलें",
    viewList: "सूची",
    viewMap: "नक्शा",
    viewSplit: "दोनों",
    noResultsTitle: "कोई कोल्ड स्टोरेज नहीं मिला",
    noResultsDesc: "इस दायरे में कोई कोल्ड स्टोरेज नहीं मिला। कृपया दायरा बढ़ाएं या दूसरा गांव/जिला चुनें।",
    btnExpandRadius: "🔄 50 / 100 किमी दायरे में खोजें",

    // Card Details
    distanceAway: "दूरी",
    callBtn: "📞 सीधे कॉल करें",
    navigateBtn: "🧭 रास्ता देखें (मैप)",
    detailsBtn: "ℹ️ पूरी जानकारी",
    capacity: "भंडारण क्षमता",
    tempRange: "तापमान",
    crops: "स्वीकृत फसलें",
    manager: "प्रबंधक",
    contactNotAvailable: "संपर्क जानकारी उपलब्ध नहीं है।",
    verifiedBadge: "सत्यापित केंद्र",

    // Modal
    modalTitle: "कोल्ड स्टोरेज संपूर्ण विवरण",
    modalOverview: "सुविधा का विस्तृत विवरण",
    modalStorageSpecs: "तकनीक व विनिर्देश",
    modalContactInfo: "संपर्क व प्रबंधक जानकारी",
    modalAmenities: "सुविधाएं व अवसंरचना",
    modalCertifications: "सरकारी मान्यता व प्रमाणन",
    modalCalculator: "भंडारण क्षमता व किराया कैलकुलेटर",
    calcCropLabel: "फसल चुनें:",
    calcBagsLabel: "50 किग्रा बोरियों की संख्या:",
    calcEstimateBtn: "क्षमता (MT) व किराया निकालें",
    calcResultText: "आवश्यक जगह: {mt} मीट्रिक टन (अनुमानित किराया: ₹{cost} / महीना)",
    closeBtn: "बंद करें",

    // Errors
    errGpsDenied: "लोकेशन अनुमति नहीं मिली। कृपया ऊपर 'गांव, मंडी या जिले से खोजें' का उपयोग करें।",
    errGpsUnavailable: "जीपीएस उपलब्ध नहीं है। कृपया गांव या जिला सर्च का उपयोग करें।",
    errGeocodeFail: "सटीक गांव नहीं मिल सका। जिले के आधार पर परिणाम दिखाए जा रहे हैं।",
    errMissingInputs: "कृपया गांव का नाम, पिन कोड दर्ज करें या राज्य व जिला चुनें।",
    errNetwork: "इंटरनेट समस्या। कृपया पुनः प्रयास करें।"
  }
};
