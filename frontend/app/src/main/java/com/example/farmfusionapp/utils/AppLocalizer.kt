package com.example.farmfusionapp.utils

/**
 * AppLocalizer - Universal Localization & Transliteration Engine
 * Covers Cities/Locations, Weather Conditions, Crops/Commodities, Diseases (all 38 classes),
 * Animals, Severities, Units, Days/Months, and ICAR Diagnostic Bullet Points across 14 languages:
 * en, hi, gu, mr, pa, bn, ta, te, kn, ml, or/od, as, ur, mai.
 */
object AppLocalizer {

    // ==========================================
    // 1. INDIAN CITIES & LOCATIONS (14 LANGUAGES)
    // ==========================================
    private val CITY_TRANSLATIONS = mapOf(
        "bengaluru" to mapOf(
            "en" to "Bengaluru", "hi" to "बेंगलुरु", "gu" to "બેંગલુરુ", "mr" to "बंगळुरू",
            "pa" to "ਬੈਂਗਲੁਰੂ", "bn" to "বেঙ্গালুরু", "ta" to "பெங்களூரு", "te" to "బెంగళూరు",
            "kn" to "ಬೆಂಗಳೂರು", "ml" to "ബെംഗളൂരു", "or" to "ବେଙ୍ଗାଲୁରୁ", "od" to "ବେଙ୍ଗାଲୁରୁ",
            "as" to "বেংগালুৰু", "ur" to "بنگلور", "mai" to "बेंगलुरु"
        ),
        "bangalore" to mapOf(
            "en" to "Bengaluru", "hi" to "बेंगलुरु", "gu" to "બેંગલુરુ", "mr" to "बंगळुरू",
            "pa" to "ਬੈਂਗਲੁਰੂ", "bn" to "বেঙ্গালুরু", "ta" to "பெங்களூரு", "te" to "బెంగళూరు",
            "kn" to "ಬೆಂಗಳೂರು", "ml" to "ബെംഗളൂരു", "or" to "ବେଙ୍ଗାଲୁରୁ", "od" to "ବେଙ୍ଗାଲୁରୁ",
            "as" to "বেংগালুৰু", "ur" to "بنگلور", "mai" to "बेंगलुरु"
        ),
        "mumbai" to mapOf(
            "en" to "Mumbai", "hi" to "मुंबई", "gu" to "મુંબઈ", "mr" to "मुंबई",
            "pa" to "ਮੁੰਬਈ", "bn" to "মুম্বই", "ta" to "மும்பை", "te" to "ముంబై",
            "kn" to "ಮುಂಬೈ", "ml" to "മുംബൈ", "or" to "ମୁମ୍ବାଇ", "od" to "ମୁମ୍ବାଇ",
            "as" to "মুম্বাই", "ur" to "ممبئی", "mai" to "मुम्बई"
        ),
        "delhi" to mapOf(
            "en" to "Delhi", "hi" to "दिल्ली", "gu" to "દિલ્હી", "mr" to "दिल्ली",
            "pa" to "ਦਿੱਲੀ", "bn" to "দিল্লি", "ta" to "தில்லி", "te" to "ఢిల్లీ",
            "kn" to "ದೆಹಲಿ", "ml" to "ഡൽഹി", "or" to "ଦିଲ୍ଲୀ", "od" to "ଦିଲ୍ଲୀ",
            "as" to "দিল্লী", "ur" to "دہلی", "mai" to "दिल्ली"
        ),
        "new delhi" to mapOf(
            "en" to "New Delhi", "hi" to "नई दिल्ली", "gu" to "નવી દિલ્હી", "mr" to "नवी दिल्ली",
            "pa" to "ਨਵੀਂ ਦਿੱਲੀ", "bn" to "নতুন দিল্লি", "ta" to "புது தில்லி", "te" to "న్యూ ఢిల్లీ",
            "kn" to "ನವದೆಹಲಿ", "ml" to "ന്യൂഡൽഹി", "or" to "ନୂଆଦିଲ୍ଲୀ", "od" to "ନୂଆଦିଲ୍ଲୀ",
            "as" to "নতুন দিল্লী", "ur" to "نئی دہلی", "mai" to "नव दिल्ली"
        ),
        "hyderabad" to mapOf(
            "en" to "Hyderabad", "hi" to "हैदराबाद", "gu" to "હૈદરાબાદ", "mr" to "हैदराबाद",
            "pa" to "ਹੈਦਰਾਬਾਦ", "bn" to "হায়দরাবাদ", "ta" to "ஹைதராபாத்", "te" to "హైదరాబాద్",
            "kn" to "ಹೈದರಾಬಾದ್", "ml" to "ഹൈദരാബാദ്", "or" to "ହାଇଦ୍ରାବାଦ", "od" to "ହାଇଦ୍ରାବାଦ",
            "as" to "হায়দৰাবাদ", "ur" to "حیدرآباد", "mai" to "हैदराबाद"
        ),
        "chennai" to mapOf(
            "en" to "Chennai", "hi" to "चेन्नई", "gu" to "ચેન્નઈ", "mr" to "चेन्नई",
            "pa" to "ਚੇਨਈ", "bn" to "চেন্নাই", "ta" to "சென்னை", "te" to "చెన్నై",
            "kn" to "ಚೆನ್ನೈ", "ml" to "ചെന്നൈ", "or" to "ଚେନ୍ନାଇ", "od" to "ଚେନ୍ନାଇ",
            "as" to "চেন্নাই", "ur" to "چنئی", "mai" to "चेन्नई"
        ),
        "kolkata" to mapOf(
            "en" to "Kolkata", "hi" to "कोलकाता", "gu" to "કોલકાતા", "mr" to "कोलकाता",
            "pa" to "ਕੋਲਕਾਤਾ", "bn" to "কলকাতা", "ta" to "கொல்கத்தா", "te" to "కోల్‌కతా",
            "kn" to "ಕೋಲ್ಕತ್ತಾ", "ml" to "കൊൽക്കത്ത", "or" to "କୋଲକାତା", "od" to "କୋଲକାତା",
            "as" to "কলকাতা", "ur" to "کولکتہ", "mai" to "कोलकाता"
        ),
        "pune" to mapOf(
            "en" to "Pune", "hi" to "पुणे", "gu" to "પુણે", "mr" to "पुणे",
            "pa" to "ਪੁਣੇ", "bn" to "পুনে", "ta" to "புனே", "te" to "పూణే",
            "kn" to "ಪುಣೆ", "ml" to "പൂനെ", "or" to "ପୁଣେ", "od" to "ପୁଣେ",
            "as" to "পুনে", "ur" to "پونے", "mai" to "पुणे"
        ),
        "ahmedabad" to mapOf(
            "en" to "Ahmedabad", "hi" to "अहमदाबाद", "gu" to "અમદાવાદ", "mr" to "अहमदाबाद",
            "pa" to "ਅਹਿਮਦਾਬਾਦ", "bn" to "আহমেদাবাদ", "ta" to "அகமதாபாத்", "te" to "అహ్మదాబాద్",
            "kn" to "ಅಹಮದಾಬಾದ್", "ml" to "അഹമ്മദാബാദ്", "or" to "ଅହମ୍ମଦାବାଦ", "od" to "ଅହମ୍ମଦାବାଦ",
            "as" to "আহমেদাবাদ", "ur" to "احمد آباد", "mai" to "अहमदाबाद"
        ),
        "jaipur" to mapOf(
            "en" to "Jaipur", "hi" to "जयपुर", "gu" to "જયપુર", "mr" to "जयपूर",
            "pa" to "ਜੈਪੁਰ", "bn" to "জয়পুর", "ta" to "ஜெய்ப்பூர்", "te" to "జైపూర్",
            "kn" to "ಜೈಪುರ", "ml" to "ജയ്പൂർ", "or" to "ଜୟପୁର", "od" to "ଜୟପୁର",
            "as" to "জয়পুৰ", "ur" to "جے پور", "mai" to "जयपुर"
        ),
        "lucknow" to mapOf(
            "en" to "Lucknow", "hi" to "लखनऊ", "gu" to "લખનૌ", "mr" to "लखनौ",
            "pa" to "ਲਖਨਊ", "bn" to "লখনউ", "ta" to "லக்னோ", "te" to "లక్నో",
            "kn" to "ಲಕ್ನೋ", "ml" to "ലഖ്‌നൗ", "or" to "ଲକ୍ଷ୍ନୌ", "od" to "ଲକ୍ଷ୍ନୌ",
            "as" to "লখনৌ", "ur" to "لکھنؤ", "mai" to "लखनऊ"
        ),
        "patna" to mapOf(
            "en" to "Patna", "hi" to "पटना", "gu" to "પટના", "mr" to "पाटणा",
            "pa" to "ਪਟਨਾ", "bn" to "পাটना", "ta" to "பாட்னா", "te" to "పాట్నా",
            "kn" to "ಪಾಟ್ನಾ", "ml" to "പട്ന", "or" to "ପାଟନା", "od" to "ପାଟନା",
            "as" to "পাটনা", "ur" to "پٹنہ", "mai" to "पटना"
        ),
        "chandigarh" to mapOf(
            "en" to "Chandigarh", "hi" to "चंडीगढ़", "gu" to "ચંદીગઢ", "mr" to "चंदिगढ",
            "pa" to "ਚੰਡੀਗੜ੍ਹ", "bn" to "চণ্ডীগড়", "ta" to "சண்டிகர்", "te" to "చండీగఢ్",
            "kn" to "ಚಂಡೀಗಢ", "ml" to "ചണ്ഡീഗഡ്", "or" to "ଚଣ୍ଡିଗଡ଼", "od" to "ଚଣ୍ଡିଗଡ଼",
            "as" to "চণ্ডীগড়", "ur" to "چنڈی گڑھ", "mai" to "चंडीगढ़"
        ),
        "bhopal" to mapOf(
            "en" to "Bhopal", "hi" to "भोपाल", "gu" to "ભોપાલ", "mr" to "भोपाळ",
            "pa" to "ਭੋਪਾਲ", "bn" to "ভোপাল", "ta" to "போபால்", "te" to "భోపాల్",
            "kn" to "ಭೋಪಾಲ್", "ml" to "ഭോപ്പാൽ", "or" to "ଭୋପାଲ", "od" to "ଭୋପାଲ",
            "as" to "ভোপাল", "ur" to "بھوپال", "mai" to "भोपाल"
        ),
        "indore" to mapOf(
            "en" to "Indore", "hi" to "इंदौर", "gu" to "ઇન્દોર", "mr" to "इंदूर",
            "pa" to "ਇੰਦੌਰ", "bn" to "ইন্দোর", "ta" to "இந்தூர்", "te" to "ఇండోర్",
            "kn" to "ಇಂದೋರ್", "ml" to "ഇൻഡോർ", "or" to "ଇନ୍ଦୋର", "od" to "ଇନ୍ଦୋର",
            "as" to "ইন্দোৰ", "ur" to "اندور", "mai" to "इन्दौर"
        ),
        "nagpur" to mapOf(
            "en" to "Nagpur", "hi" to "नागपुर", "gu" to "નાગપુર", "mr" to "नागपूर",
            "pa" to "ਨਾਗਪੁਰ", "bn" to "নাਗপুর", "ta" to "நாக்பூர்", "te" to "నాగ్‌పూర్",
            "kn" to "ನಾಗಪುರ", "ml" to "നാഗ്പൂർ", "or" to "ନାଗପୁର", "od" to "ନାଗପୁର",
            "as" to "নাগপুৰ", "ur" to "ناگپور", "mai" to "नागपुर"
        ),
        "surat" to mapOf(
            "en" to "Surat", "hi" to "सूरत", "gu" to "સુરત", "mr" to "सुरत",
            "pa" to "ਸੂਰਤ", "bn" to "সুরাত", "ta" to "சூரத்", "te" to "సూరత్",
            "kn" to "ಸೂರತ್", "ml" to "സൂററ്റ്", "or" to "ସୁରଟ", "od" to "ସୁରଟ",
            "as" to "চুৰাট", "ur" to "سورت", "mai" to "सूरत"
        ),
        "varanasi" to mapOf(
            "en" to "Varanasi", "hi" to "वाराणसी", "gu" to "વારાણસી", "mr" to "वाराणसी",
            "pa" to "ਵਾਰਾਣਸੀ", "bn" to "বারাণসী", "ta" to "வாரணாசி", "te" to "వారణాసి",
            "kn" to "ವಾರಣಾಸಿ", "ml" to "വാരാണസി", "or" to "ବାରାଣସୀ", "od" to "ବାରାଣସୀ",
            "as" to "বাৰাণসী", "ur" to "وارانسی", "mai" to "वाराणसी"
        ),
        "ludhiana" to mapOf(
            "en" to "Ludhiana", "hi" to "लुधियाना", "gu" to "લુધિયાણા", "mr" to "लुधियाना",
            "pa" to "ਲੁਧਿਆਣਾ", "bn" to "লুধিয়ানা", "ta" to "லூதியானா", "te" to "లూథియానా",
            "kn" to "ಲುಧಿಯಾನ", "ml" to "ലുധിയാന", "or" to "ଲୁଧିଆନା", "od" to "ଲୁଧିଆନା",
            "as" to "লুধিয়ানা", "ur" to "لدھیانہ", "mai" to "लुधियाना"
        ),
        "amritsar" to mapOf(
            "en" to "Amritsar", "hi" to "अमृतसर", "gu" to "અમૃતસર", "mr" to "अमृतसर",
            "pa" to "ਅੰਮ੍ਰਿਤਸਰ", "bn" to "অমৃতসর", "ta" to "அமிர்தசரஸ்", "te" to "అమృత్‌సర్",
            "kn" to "ಅಮೃತಸರ", "ml" to "അമൃത്സർ", "or" to "ଅମୃତସର", "od" to "ଅମୃତସର",
            "as" to "অমৃতসৰ", "ur" to "امرتسر", "mai" to "अमृतसर"
        ),
        "guwahati" to mapOf(
            "en" to "Guwahati", "hi" to "गुवाहाटी", "gu" to "ગુવાહાટી", "mr" to "ગુવાહાટી",
            "pa" to "ਗੁਵਾਹਾਟੀ", "bn" to "গুয়াহাটি", "ta" to "குவஹாத்தி", "te" to "గౌహతి",
            "kn" to "ಗುವಾಹಟಿ", "ml" to "ഗുവാഹത്തി", "or" to "ଗୁଆହାଟୀ", "od" to "ଗୁଆହାଟୀ",
            "as" to "গুৱাহাটী", "ur" to "گوہاٹی", "mai" to "गुवाहाटी"
        ),
        "bhubaneswar" to mapOf(
            "en" to "Bhubaneswar", "hi" to "भुवनेश्वर", "gu" to "ભુવનેશ્વર", "mr" to "भुवनेश्वर",
            "pa" to "ਭੁਵਨੇਸ਼ਵਰ", "bn" to "ভুবনেশ্বর", "ta" to "புவனேஸ்வர்", "te" to "భువనేశ్వర్",
            "kn" to "ಭುವನೇಶ್ವರ", "ml" to "ഭുവനേശ്വർ", "or" to "ଭୁବନେଶ୍ୱର", "od" to "ଭୁବନେଶ୍ୱର",
            "as" to "ভুৱনেশ্বৰ", "ur" to "بھوبنیشور", "mai" to "भुवनेश्वर"
        ),
        "ranchi" to mapOf(
            "en" to "Ranchi", "hi" to "रांची", "gu" to "રાંચી", "mr" to "रांची",
            "pa" to "ਰਾਂਚੀ", "bn" to "রাঁচি", "ta" to "ராஞ்சி", "te" to "రాంచీ",
            "kn" to "ರಾಂಚಿ", "ml" to "റാഞ്ചി", "or" to "ରାଞ୍ଚି", "od" to "ରାଞ୍ଚି",
            "as" to "ৰাঁচী", "ur" to "رانچی", "mai" to "राँची"
        ),
        "kochi" to mapOf(
            "en" to "Kochi", "hi" to "कोच्चि", "gu" to "કોચી", "mr" to "कोची",
            "pa" to "ਕੋਚੀ", "bn" to "কোচি", "ta" to "கொச்சி", "te" to "కొచ్చి",
            "kn" to "ಕೊಚ್ಚಿ", "ml" to "കൊച്ചി", "or" to "କୋଚି", "od" to "କୋଚି",
            "as" to "কোচি", "ur" to "کوچی", "mai" to "कोच्चि"
        ),
        "thiruvananthapuram" to mapOf(
            "en" to "Thiruvananthapuram", "hi" to "तिरुवनंतपुरम", "gu" to "તિરુવનંતપુરમ", "mr" to "तिरुवनंतपुरम",
            "pa" to "ਤਿਰੂਵਨੰਤਪੁਰਮ", "bn" to "তিরুবনন্তপুরম", "ta" to "திருவனந்தபுரம்", "te" to "తిరువనంతపురం",
            "kn" to "ತಿರುವನಂತಪುರಂ", "ml" to "തിരുവനന്തപുരം", "or" to "ତିରୁବନନ୍ତପୁରମ", "od" to "ତିରୁବନନ୍ତପୁରମ",
            "as" to "তিৰুৱনন্তপুৰম", "ur" to "تروواننت پورم", "mai" to "तिरुवनंतपुरम"
        ),
        "india" to mapOf(
            "en" to "India", "hi" to "भारत", "gu" to "ભારત", "mr" to "भारत",
            "pa" to "ਭਾਰਤ", "bn" to "ভারত", "ta" to "இந்தியா", "te" to "భారతదేశం",
            "kn" to "ಭಾರತ", "ml" to "ഇന്ത്യ", "or" to "ଭାରତ", "od" to "ଭାରତ",
            "as" to "ভাৰত", "ur" to "بھارت", "mai" to "भारत"
        )
    )

    // ==========================================
    // 2. WEATHER CONDITIONS (14 LANGUAGES)
    // ==========================================
    private val WEATHER_CONDITIONS = mapOf(
        "clear sky" to mapOf("en" to "Clear Sky", "hi" to "साफ आसमान", "gu" to "ચોખ્ખું આકાશ", "mr" to "निरभ्र आकाश", "pa" to "ਸਾਫ਼ ਅਸਮਾਨ", "bn" to "পরিষ্কার আকাশ", "ta" to "தெளிவான வானம்", "te" to "స్పష్టమైన ఆకాశం", "kn" to "ಸ್ವಚ್ಛ ಆಕಾಶ", "ml" to "തെളിഞ്ഞ ആകാശം", "or" to "ପରିଷ୍କାର ଆକାଶ", "as" to "পৰিষ্কাৰ আকাশ", "ur" to "صاف آسمان", "mai" to "साफ अकास"),
        "sunny" to mapOf("en" to "Sunny", "hi" to "धूपदार", "gu" to "તડકો", "mr" to "सूर्यप्रकाश", "pa" to "ਧੁੱਪ", "bn" to "রৌদ্রোজ্জ্বল", "ta" to "வெயில்", "te" to "ఎండగా ఉంది", "kn" to "ಬಿಸಿಲು", "ml" to "വെയിൽ", "or" to "ଖରାଟିଆ", "as" to "ৰৌদ্ৰোজ্জ্বল", "ur" to "دھوپ", "mai" to "घाम"),
        "mainly clear" to mapOf("en" to "Mainly Clear", "hi" to "मुख्यतः साफ", "gu" to "મોટે ભાગે ચોખ્ખું", "mr" to "मुख्यतः निरभ्र", "pa" to "ਮੁੱਖ ਤੌਰ 'ਤੇ ਸਾਫ਼", "bn" to "বেশিরভাগ সময় পরিষ্কার", "ta" to "பெரும்பாலும் தெளிவானது", "te" to "ఎక్కువగా స్పష్టం", "kn" to "ಹೆಚ್ಚಾಗಿ ಸ್ವಚ್ಛ", "ml" to "മിക്കവാറും തെളിഞ്ഞത്", "or" to "ମୁଖ୍ୟତଃ ପରିଷ୍କାର", "as" to "প্ৰধানকৈ পৰিষ্কাৰ", "ur" to "زیادہ تر صاف", "mai" to "मुख्यतः साफ"),
        "partly cloudy" to mapOf("en" to "Partly Cloudy", "hi" to "आंशिक बादल", "gu" to "અંશતઃ વાદળછાયું", "mr" to "अंशतः ढगाळ", "pa" to "ਅੰਸ਼ਕ ਤੌਰ 'ਤੇ ਬੱਦਲਵਾਈ", "bn" to "আংশিক মেঘলা", "ta" to "பகுதி மேகமூட்டம்", "te" to "పాక్షికంగా మేఘావృతం", "kn" to "ಭಾಗಶಃ ಮೋಡ", "ml" to "ഭാഗികമായി മേഘാവൃതമായ", "or" to "ଆଂଶିକ ମେଘୁଆ", "as" to "আংশিক ডাৱৰীয়া", "ur" to "جزوی طور پر ابر آلود", "mai" to "आंशिक बादल"),
        "overcast" to mapOf("en" to "Overcast", "hi" to "घने बादल", "gu" to "વાદળછાયું", "mr" to "पूर्ण ढगाळ", "pa" to "ਘਣੇ ਬੱਦਲ", "bn" to "মেঘলা আকাশ", "ta" to "முழு மேகமூட்டம்", "te" to "పూర్తిగా మేఘావృతం", "kn" to "ತುಂಬಾ ಮೋಡ", "ml" to "കാർമേഘം", "or" to "ପୂରା ମେଘୁଆ", "as" to "ডাৱৰীয়া", "ur" to "گھٹا چھائی ہوئی", "mai" to "घने बादल"),
        "fog" to mapOf("en" to "Fog", "hi" to "कोहरा", "gu" to "ધુમ્મસ", "mr" to "धुके", "pa" to "ਧੁੰਦ", "bn" to "কুয়াশা", "ta" to "மூடுபனி", "te" to "పొగమంచు", "kn" to "ದಟ್ಟ ಮಂಜು", "ml" to "മൂടൽമഞ്ഞ്", "or" to "କୁହୁଡ଼ି", "as" to "কুঁৱলী", "ur" to "کہر", "mai" to "कुहासा"),
        "light rain" to mapOf("en" to "Light Rain", "hi" to "हल्की बारिश", "gu" to "હળવો વરસાદ", "mr" to "हलका पाऊस", "pa" to "ਹਲਕੀ ਬਾਰਿਸ਼", "bn" to "হালকা বৃষ্টি", "ta" to "லேசான மழை", "te" to "తేలికపాటి వర్షం", "kn" to "ಹಗುರ ಮಳೆ", "ml" to "നേരിയ മഴ", "or" to "ହାଲୁକା ବର୍ଷା", "as" to "পাতলীয়া বৰষুণ", "ur" to "ہلکی بارش", "mai" to "हलुक वर्षा"),
        "moderate rain" to mapOf("en" to "Moderate Rain", "hi" to "मध्यम बारिश", "gu" to "મધ્યમ વરસાદ", "mr" to "मध्यम पाऊस", "pa" to "ਦਰਮਿਆਨੀ ਬਾਰਿਸ਼", "bn" to "মাঝারি বৃষ্টি", "ta" to "மிதமான மழை", "te" to "మితమైన వర్షం", "kn" to "ಮಧ್ಯಮ ಮಳೆ", "ml" to "മിതമായ മഴ", "or" to "ମଧ୍ୟମ ବର୍ଷା", "as" to "মজলীয়া বৰষুণ", "ur" to "معتدل بارش", "mai" to "मध्यम वर्षा"),
        "heavy rain" to mapOf("en" to "Heavy Rain", "hi" to "भारी बारिश", "gu" to "ભારે વરસાદ", "mr" to "मुसळधार पाऊस", "pa" to "ਭਾਰੀ ਬਾਰਿਸ਼", "bn" to "ভারী বৃষ্টি", "ta" to "கனமழை", "te" to "భారీ వర్షం", "kn" to "ಭಾರೀ ಮಳೆ", "ml" to "കനത്ത മഴ", "or" to "ପ୍ରବଳ ବର୍ଷା", "as" to "প্ৰবল বৰষুণ", "ur" to "شدید بارش", "mai" to "भारी वर्षा"),
        "thunderstorm" to mapOf("en" to "Thunderstorm", "hi" to "गरज के साथ बारिश", "gu" to "ગાજવીજ સાથે વરસાદ", "mr" to "वादळी पाऊस", "pa" to "ਤੂਫਾਨ ਅਤੇ ਬਾਰਿਸ਼", "bn" to "বজ্রবিদ্যুৎসহ ঝড়বৃষ্টি", "ta" to "இடி மின்னலுடன் கூடிய மழை", "te" to "ఉరుములతో కూడిన వర్షం", "kn" to "ಗುಡುಗು ಸಹಿತ ಮಳೆ", "ml" to "ഇടിമിന്നലോടുകൂടിയ മഴ", "or" to "ଘଡ଼ଘଡ଼ି ସହ ବର୍ଷା", "as" to "বজ্ৰপাত আৰু ধুমুহা", "ur" to "گرج چمک کے ساتھ بارش", "mai" to "ठनका आ वर्षा")
    )

    // ==========================================
    // 3. CROPS & MANDI COMMODITIES (14 LANGUAGES)
    // ==========================================
    private val CROPS = mapOf(
        "wheat" to mapOf("en" to "Wheat", "hi" to "गेहूं", "gu" to "ઘઉં", "mr" to "गहू", "pa" to "ਕਣਕ", "bn" to "গম", "ta" to "கோதுமை", "te" to "గోధుమలు", "kn" to "ಗೋಧಿ", "ml" to "ഗോതമ്പ്", "or" to "ଗହମ", "as" to "গম", "ur" to "گندم", "mai" to "गेहूँ"),
        "rice" to mapOf("en" to "Rice / Paddy", "hi" to "धान / चावल", "gu" to "ડાંગર / ચોખા", "mr" to "भात / तांदूळ", "pa" to "ਝੋਨਾ / ਚੌਲ", "bn" to "ধান / চাল", "ta" to "நெல் / அரிசி", "te" to "వరి / బియ్యం", "kn" to "ಭತ್ತ / ಅಕ್ಕಿ", "ml" to "നെല്ല് / അരി", "or" to "ଧାନ / ଚାଉଳ", "as" to "ধান / চাউল", "ur" to "دھان / چاول", "mai" to "धान / चाउर"),
        "paddy" to mapOf("en" to "Paddy", "hi" to "धान", "gu" to "ડાંગર", "mr" to "भात", "pa" to "ਝੋਨਾ", "bn" to "ধান", "ta" to "நெல்", "te" to "వరి", "kn" to "ಭತ್ತ", "ml" to "നെല്ല്", "or" to "ଧାନ", "as" to "ধান", "ur" to "دھان", "mai" to "धान"),
        "cotton" to mapOf("en" to "Cotton", "hi" to "कपास", "gu" to "કપાસ", "mr" to "कापूस", "pa" to "ਕਪਾਹ", "bn" to "তুলা", "ta" to "பருத்தி", "te" to "ప్రత్తి", "kn" to "ಹತ್ತಿ", "ml" to "പരുത്തി", "or" to "କପା", "as" to "কপাহ", "ur" to "کپاس", "mai" to "कपास"),
        "maize" to mapOf("en" to "Maize / Corn", "hi" to "मक्का", "gu" to "મકાઈ", "mr" to "मका", "pa" to "ਮੱਕੀ", "bn" to "ভুট্টা", "ta" to "மக்காச்சோளம்", "te" to "మొక్కజొన్న", "kn" to "ಮೆಕ್ಕೆಜೋಳ", "ml" to "ചോളം", "or" to "ମକା", "as" to "মাকৈ", "ur" to "مکئی", "mai" to "मकई"),
        "corn" to mapOf("en" to "Corn / Maize", "hi" to "मक्का", "gu" to "મકાઈ", "mr" to "मका", "pa" to "ਮੱਕੀ", "bn" to "ভুট্টা", "ta" to "மக்காச்சோளம்", "te" to "మొక్కజొన్న", "kn" to "ಮೆಕ್ಕೆಜೋಳ", "ml" to "ചോളം", "or" to "ମକା", "as" to "মাকৈ", "ur" to "مکئی", "mai" to "मकई"),
        "groundnut" to mapOf("en" to "Groundnut", "hi" to "मूंगफली", "gu" to "મગફળી", "mr" to "भुईमूग", "pa" to "ਮੂੰਗਫਲੀ", "bn" to "চিনাবাদাম", "ta" to "வேர்க்கடலை", "te" to "వేరుశనగ", "kn" to "ಕಡಲೆಕಾಯಿ", "ml" to "നിലക്കടല", "or" to "ଚିନାବାଦାମ", "as" to "বাদাম", "ur" to "مونگ پھلی", "mai" to "बादाम"),
        "mustard" to mapOf("en" to "Mustard", "hi" to "सरसों", "gu" to "રાયડો / સરસવ", "mr" to "मोहरी", "pa" to "ਸਰ੍ਹੋਂ", "bn" to "সরিষা", "ta" to "கடுகு", "te" to "ఆవాలు", "kn" to "ಸಾಸಿವೆ", "ml" to "കടുക്", "or" to "ସୋରିଷ", "as" to "সৰিয়হ", "ur" to "سرسوں", "mai" to "तोरी / सरिसो"),
        "soyabean" to mapOf("en" to "Soyabean", "hi" to "सोयाबीन", "gu" to "સોયાબીન", "mr" to "सोयाबीन", "pa" to "ਸੋਇਆਬੀਨ", "bn" to "সয়াবিন", "ta" to "சோயாபீன்", "te" to "సోయాబీన్", "kn" to "ಸೋಯಾಬೀನ್", "ml" to "സോയാബീൻ", "or" to "ସୋୟାବିନ୍", "as" to "চয়াবিন", "ur" to "سویا بین", "mai" to "सोयाबीन"),
        "sugarcane" to mapOf("en" to "Sugarcane", "hi" to "गन्ना", "gu" to "શેરડી", "mr" to "ऊस", "pa" to "ਗੰਨਾ", "bn" to "আখ", "ta" to "கரும்பு", "te" to "చెరకు", "kn" to "ಕಬ್ಬು", "ml" to "കരിമ്പ്", "or" to "ଆଖୁ", "as" to "কুঁহিয়াৰ", "ur" to "گنا", "mai" to "ऊख / केतारी"),
        "tomato" to mapOf("en" to "Tomato", "hi" to "टमाटर", "gu" to "ટામેટા", "mr" to "टोमॅटो", "pa" to "ਟਮਾਟਰ", "bn" to "টমেটো", "ta" to "தக்காளி", "te" to "టమోటా", "kn" to "ಟೊಮ್ಯಾಟೊ", "ml" to "തക്കാളി", "or" to "ଟମାଟୋ", "as" to "টমেটো", "ur" to "ٹماٹر", "mai" to "टमाटर"),
        "potato" to mapOf("en" to "Potato", "hi" to "आलू", "gu" to "બટાકા", "mr" to "बटाटा", "pa" to "ਆਲੂ", "bn" to "আলু", "ta" to "உருளைக்கிழங்கு", "te" to "బంగాళాదుంప", "kn" to "ಆಲೂಗಡ್ಡೆ", "ml" to "ഉരുളക്കിഴങ്ങ്", "or" to "ଆଳୁ", "as" to "আলু", "ur" to "آلو", "mai" to "आलू"),
        "onion" to mapOf("en" to "Onion", "hi" to "प्याज", "gu" to "ડુંગળી", "mr" to "कांदा", "pa" to "ਪਿਆਜ਼", "bn" to "পেঁয়াজ", "ta" to "வெங்காயம்", "te" to "ఉల్లిపాయ", "kn" to "ಈರುಳ್ಳಿ", "ml" to "സവാള", "or" to "ପିଆଜ", "as" to "পিয়াঁজ", "ur" to "پیاز", "mai" to "पियाज"),
        "pepper bell" to mapOf("en" to "Bell Pepper / Capsicum", "hi" to "शिमला मिर्च", "gu" to "કેપ્સિકમ / સિમલા મરચાં", "mr" to "ढोबळी मिरची (शिमला मिरची)", "pa" to "ਸ਼ਿਮਲਾ ਮਿਰਚ", "bn" to "ক্যাপসিকাম / মিষ্টি মরিচ", "ta" to "குடைமிளகாய்", "te" to "క్యాప్సికం / బెంగళూరు మిరప", "kn" to "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ (ಕ್ಯಾಪ್ಸಿಕಂ)", "ml" to "ക്യാപ്സിക്കം", "or" to "ଶିମଲା ଲଙ୍କା", "as" to "কেপচিকাম / ক্যাপচিকাম", "ur" to "شملہ مرچ", "mai" to "शिमला मिर्च"),
        "bell pepper" to mapOf("en" to "Bell Pepper / Capsicum", "hi" to "शिमला मिर्च", "gu" to "કેપ્સિકમ / સિમલા મરચાં", "mr" to "ढोबळी मिरची (शिमला मिरची)", "pa" to "ਸ਼ਿਮਲਾ ਮਿਰਚ", "bn" to "ক্যাপসিকাম / মিষ্টি মরিচ", "ta" to "குடைமிளகாய்", "te" to "క్యాప్సికం / బెంగళూరు మిరప", "kn" to "ದಪ್ಪ ಮೆಣಸಿನಕಾಯಿ (ಕ್ಯಾಪ್ಸಿಕಂ)", "ml" to "ക്യാപ്സിക്കം", "or" to "ଶିମଲା ଲଙ୍କା", "as" to "কেপচিকাম / ক্যাপচিকাম", "ur" to "شملہ مرچ", "mai" to "शिमला मिर्च"),
        "apple" to mapOf("en" to "Apple", "hi" to "सेब", "gu" to "સફરજન", "mr" to "सफरचंद", "pa" to "ਸੇਬ", "bn" to "আপেল", "ta" to "ஆப்பிள்", "te" to "ஆపిల్", "kn" to "ಸೇಬು", "ml" to "ആപ്പിൾ", "or" to "ସେଓ", "as" to "আপেল", "ur" to "سیب", "mai" to "सेब"),
        "grape" to mapOf("en" to "Grape", "hi" to "अंगूर", "gu" to "દ્રાક્ષ", "mr" to "द्राक्षे", "pa" to "ਅੰਗੂਰ", "bn" to "আঙ্গুর", "ta" to "திராட்சை", "te" to "ద్రాక్ష", "kn" to "ದ್ರಾಕ್ಷಿ", "ml" to "മുന്തിരി", "or" to "ଅଙ୍ଗୁର", "as" to "আঙুৰ", "ur" to "انگور", "mai" to "अंगूर"),
        "orange" to mapOf("en" to "Orange / Citrus", "hi" to "संतरा / नींबू", "gu" to "સંતરાં / મોસંબી", "mr" to "संत्री / मोसंबी", "pa" to "ਸੰਤਰਾ", "bn" to "কমলালেবু", "ta" to "ஆரஞ்சு", "te" to "నారింజ", "kn" to "ಕಿತ್ತಳೆ", "ml" to "ഓറഞ്ച്", "or" to "କମଳା", "as" to "কমলা", "ur" to "سنترا", "mai" to "संतरा"),
        "peach" to mapOf("en" to "Peach", "hi" to "आड़ू", "gu" to "પીચ / આડુ", "mr" to "पीच / आडू", "pa" to "ਆੜੂ", "bn" to "পীচ ফল", "ta" to "பீச்", "te" to "పీచ్", "kn" to "ಪೀಚ್", "ml" to "പീച്ച്", "or" to "ପିଚ୍", "as" to "পীচ", "ur" to "آڑو", "mai" to "आडू"),
        "strawberry" to mapOf("en" to "Strawberry", "hi" to "स्ट्रॉबेरी", "gu" to "સ્ટ્રોબેરી", "mr" to "स्ट्रॉबेरी", "pa" to "ਸਟ੍ਰਾਬੇਰੀ", "bn" to "স্ট্রবেরি", "ta" to "ஸ்ட்ராபெரி", "te" to "స్ట్రాబెర్రీ", "kn" to "ಸ್ಟ್ರಾಬೆರಿ", "ml" to "സ്ട്രോബെറി", "or" to "ଷ୍ଟ୍ରବେରୀ", "as" to "ষ্ট্ৰবেৰী", "ur" to "اسٹرابیری", "mai" to "स्ट्रॉबेरी"),
        "chickpea" to mapOf("en" to "Chickpea / Gram", "hi" to "चना", "gu" to "ચણા", "mr" to "हरभरा / चणा", "pa" to "ਛੋਲੇ / ਚਣਾ", "bn" to "ছোলা", "ta" to "கொண்டைக்கடலை", "te" to "శనగలు", "kn" to "ಕಡಲೆ", "ml" to "കടല", "or" to "ବୁଟ / ଚଣା", "as" to "বুট / বুটমাহ", "ur" to "چنا", "mai" to "चना"),
        "kidneybeans" to mapOf("en" to "Kidney Beans / Rajma", "hi" to "राजमा", "gu" to "રાજમા", "mr" to "राजमा", "pa" to "ਰਾਜਮਾਂਹ", "bn" to "রাজমা", "ta" to "ராஜ்மா", "te" to "రాజ్మా", "kn" to "ರಾಜ್ಮಾ", "ml" to "രാജ്മ", "or" to "ରାଜମା", "as" to "ৰাজমাহ", "ur" to "راجمہ", "mai" to "राजमा"),
        "pigeonpeas" to mapOf("en" to "Pigeon Peas / Arhar", "hi" to "अरहर / तुअर", "gu" to "તુવેર", "mr" to "तूर", "pa" to "ਅਰਹਰ / ਤੂਰ", "bn" to "অড়হর", "ta" to "துவரை", "te" to "కందులు", "kn" to "ತೊಗರಿ", "ml" to "തുവര", "or" to "ହରଡ଼", "as" to "অৰহৰ", "ur" to "ارہر کی دال", "mai" to "रहरी / अरहर"),
        "mothbeans" to mapOf("en" to "Moth Beans", "hi" to "मोठ", "gu" to "મઠ", "mr" to "मटकी", "pa" to "ਮੋਠ", "bn" to "মঠ কলাই", "ta" to "நரிப்பயறு", "te" to "బొబ్బర్లు / మోత్", "kn" to "ಮಡಿಕೆ ಕಾಳು", "ml" to "മോത്ത് ബീൻസ്", "or" to "କାନି ମୁଗ", "as" to "মথ মাহ", "ur" to "موٹھ", "mai" to "मोठ"),
        "mungbean" to mapOf("en" to "Mung Bean / Green Gram", "hi" to "मूंग", "gu" to "મગ", "mr" to "मूग", "pa" to "ਮੂੰਗੀ", "bn" to "মুগ ডাল", "ta" to "பாசிப்பயறு", "te" to "పెసలు", "kn" to "ಹೆಸರು ಕಾಳು", "ml" to "ചെറുപയർ", "or" to "ମୁଗ", "as" to "মগু মাহ", "ur" to "مونگ", "mai" to "मूंग"),
        "blackgram" to mapOf("en" to "Black Gram / Urad", "hi" to "उड़द", "gu" to "અડદ", "mr" to "उडीद", "pa" to "ਮਾਂਹ / ਉੜਦ", "bn" to "মাষকলাই / কলাই", "ta" to "உளுந்து", "te" to "మినుములు", "kn" to "ಉದ್ದು", "ml" to "ഉഴുന്ന്", "or" to "ବିରି", "as" to "মাটি মাহ", "ur" to "ماش کی دال", "mai" to "उड़िद / कलाई"),
        "lentil" to mapOf("en" to "Lentil / Masoor", "hi" to "मसूर", "gu" to "મસૂર", "mr" to "मसूर", "pa" to "ਮਸਰ", "bn" to "মসুর ডাল", "ta" to "மைசூர் பருப்பு", "te" to "మసూర్ పప్పు", "kn" to "ಮಸೂರ", "ml" to "മസൂർ പരിപ്പ്", "or" to "ମସୁର", "as" to "মচুৰ মাহ", "ur" to "مسور", "mai" to "मंसूर / मसूर"),
        "pomegranate" to mapOf("en" to "Pomegranate", "hi" to "अनार", "gu" to "દાડમ", "mr" to "डाळिंब", "pa" to "ਅਨਾਰ", "bn" to "ডালিম / বেদানা", "ta" to "மாதுளை", "te" to "దానిమ్మ", "kn" to "ದಾಳಿಂಬೆ", "ml" to "മാതളനാരങ്ങ", "or" to "ଡାଳିମ୍ବ", "as" to "ডালিম", "ur" to "انار", "mai" to "अनार / बेदाना"),
        "banana" to mapOf("en" to "Banana", "hi" to "केला", "gu" to "કેળાં", "mr" to "केळी", "pa" to "ਕੇਲਾ", "bn" to "কলা", "ta" to "வாழை", "te" to "అరటి", "kn" to "ಬಾಳೆಹಣ್ಣು", "ml" to "വാഴ", "or" to "କଦଳୀ", "as" to "কল", "ur" to "کیلا", "mai" to "केरा"),
        "mango" to mapOf("en" to "Mango", "hi" to "आम", "gu" to "કેરી", "mr" to "आंबा", "pa" to "ਅੰਬ", "bn" to "আম", "ta" to "மாம்பழம்", "te" to "మామిడి", "kn" to "ಮಾವು", "ml" to "മാങ്ങ", "or" to "ଆମ୍ବ", "as" to "আম", "ur" to "آم", "mai" to "आम"),
        "grapes" to mapOf("en" to "Grapes", "hi" to "अंगूर", "gu" to "દ્રાક્ષ", "mr" to "द्राक्षे", "pa" to "ਅੰਗੂਰ", "bn" to "আঙ্গুর", "ta" to "திராட்சை", "te" to "ద్రాక్ష", "kn" to "ದ್ರಾಕ್ಷಿ", "ml" to "മുന്തിരി", "or" to "ଅଙ୍ଗୁର", "as" to "আঙুৰ", "ur" to "انگور", "mai" to "अंगूर"),
        "watermelon" to mapOf("en" to "Watermelon", "hi" to "तरबूज", "gu" to "તરબૂચ", "mr" to "कलिंगड / टरबूज", "pa" to "ਤਰਬੂਜ਼", "bn" to "তরমুজ", "ta" to "தர்பூசணி", "te" to "పుచ్చకాయ", "kn" to "ಕಲ್ಲಂಗಡಿ", "ml" to "തണ്ണിമത്തൻ", "or" to "ତରଭୁଜ", "as" to "তৰমুজ", "ur" to "تربوز", "mai" to "तरबूज"),
        "muskmelon" to mapOf("en" to "Muskmelon", "hi" to "खरबूजा", "gu" to "ટેટી / શક્કરટેટી", "mr" to "खरबूज", "pa" to "ਖਰਬੂਜ਼ਾ", "bn" to "ফুটি / খরমুজ", "ta" to "முலாம் பழம்", "te" to "కర్బూజ", "kn" to "ಖರಬೂಜ", "ml" to "തയ്ക്കുമ്പളം", "or" to "ଖରଭୁଜ", "as" to "খাৰমুজা", "ur" to "خربوزہ", "mai" to "खरबूजा"),
        "papaya" to mapOf("en" to "Papaya", "hi" to "पपीता", "gu" to "પપૈયું", "mr" to "पपई", "pa" to "ਪਪੀਤਾ", "bn" to "পেঁপে", "ta" to "பப்பாளி", "te" to "బొప్పాయి", "kn" to "ಪಪ್ಪಾಯಿ", "ml" to "പപ്പായ", "or" to "ଅମୃତଭଣ୍ଡା", "as" to "অমিতা", "ur" to "پپیتا", "mai" to "पपीता"),
        "coconut" to mapOf("en" to "Coconut", "hi" to "नारियल", "gu" to "નાળિયેર", "mr" to "नारळ", "pa" to "ਨਾਰੀਅਲ", "bn" to "নারকেল", "ta" to "தேங்காய்", "te" to "కొబ్బరి", "kn" to "ತೆಂಗಿನಕಾಯಿ", "ml" to "തേങ്ങ / നാളികേരം", "or" to "ନଡ଼ିଆ", "as" to "নাৰিকল", "ur" to "ناریل", "mai" to "नारियर"),
        "jute" to mapOf("en" to "Jute", "hi" to "जूट / पटसन", "gu" to "શણ", "mr" to "ताग", "pa" to "ਪਟਸਨ / ਜੂਟ", "bn" to "পাট", "ta" to "சணல்", "te" to "జనపనార", "kn" to "ಸೆಣಬು", "ml" to "ചണം", "or" to "ଝୋଟ", "as" to "মৰাপাট", "ur" to "پٹ سن", "mai" to "पटुआ / जूट"),
        "coffee" to mapOf("en" to "Coffee", "hi" to "कॉफी", "gu" to "કોફી", "mr" to "कॉफी", "pa" to "ਕੌਫੀ", "bn" to "কফি", "ta" to "காபி", "te" to "కాఫీ", "kn" to "ಕಾಫಿ", "ml" to "കാപ്പി", "or" to "କଫି", "as" to "কফি", "ur" to "کافی", "mai" to "कॉफी")
    )

    // ==========================================
    // 4. PLANT DISEASES - ALL 38 CLASSES (14 LANGUAGES)
    // ==========================================
    private val DISEASES = mapOf(
        "healthy plant" to mapOf("en" to "Healthy Plant", "hi" to "स्वस्थ पौधा", "gu" to "સ્વસ્થ છોડ", "mr" to "निरोगी रोप", "pa" to "ਸਿਹਤਮੰਦ ਪੌਦਾ", "bn" to "সুস্থ উদ্ভিদ", "ta" to "ஆரோக்கியமான தாவரம்", "te" to "ఆరోగ్యకరమైన మొక్క", "kn" to "ಆರೋಗ್ಯಕರ ಸಸ್ಯ", "ml" to "ആരോഗ്യമുള്ള ചെടി", "or" to "ସୁସ୍ଥ ଗଛ", "as" to "সুস্থ উদ্ভিদ", "ur" to "صحت مند پودا", "mai" to "स्वस्थ गाछ"),
        "healthy" to mapOf("en" to "Healthy Plant", "hi" to "स्वस्थ पौधा", "gu" to "સ્વસ્થ છોડ", "mr" to "निरोगी रोप", "pa" to "ਸਿਹਤਮੰਦ ਪੌਦਾ", "bn" to "সুস্থ উদ্ভিদ", "ta" to "ஆரோக்கியமான தாவரம்", "te" to "ఆరోగ్యకరమైన మొక్క", "kn" to "ಆರೋಗ್ಯಕರ ಸಸ್ಯ", "ml" to "ആരോഗ്യമുള്ള ചെടി", "or" to "ସୁସ୍ଥ ଗଛ", "as" to "সুস্থ উদ্ভিদ", "ur" to "صحت مند پودا", "mai" to "स्वस्थ गाछ"),
        
        "bacterial spot" to mapOf(
            "en" to "Bacterial Spot",
            "hi" to "जीवाणु धब्बा रोग (बैक्टीरियल स्पॉट)",
            "gu" to "જીવાણુજન્ય ટપકાંનો રોગ",
            "mr" to "जिवाणूजन्य ठिपके रोग (बॅक्टेरियल स्पॉट)",
            "pa" to "ਜੀਵਾਣੂ ਧੱਬਾ ਰੋਗ",
            "bn" to "ব্যাকটেরিয়াল স্পট রোগ",
            "ta" to "பாக்டீரியா புள்ளி நோய்",
            "te" to "బ్యాక్టీరియా మచ్చ తెగులు",
            "kn" to "ಬ್ಯಾಕ್ಟೀರಿಯಾ ಕಲೆ ರೋಗ",
            "ml" to "ബാക്ടീരിയൽ പൊട്ടുരോഗം",
            "or" to "ଜୀବାଣୁ ଦାଗ ରୋଗ",
            "as" to "বেক্টেৰিয়াজনিত দাগ ৰোগ",
            "ur" to "بیکٹیریل داغ (بیکٹیریل سپاٹ)",
            "mai" to "जीवाणु धब्बा रोग"
        ),
        "early blight" to mapOf(
            "en" to "Early Blight",
            "hi" to "अगेती झुलसा रोग (अल्टरनेरिया)",
            "gu" to "આગોતરો સુકારો",
            "mr" to "लवकर येणारा करपा (अगेती करपा)",
            "pa" to "ਅਗੇਤਾ ਝੁਲਸ ਰੋਗ",
            "bn" to "আগাম ধসা রোগ",
            "ta" to "முன் பருவ கருகல் நோய்",
            "te" to "ముందస్తు తెగులు",
            "kn" to "ಮುಂಚಿನ ಕರಕಲು ರೋಗ",
            "ml" to "ആദ്യകാല കരിച്ചിൽ",
            "or" to "ଅଗାତିଆ ଝାଉଁଳା ରୋଗ",
            "as" to "আগতীয়া পাত শুকোৱা ৰোগ",
            "ur" to "پیشگی جھلسائو",
            "mai" to "अगेती झुलसा"
        ),
        "late blight" to mapOf(
            "en" to "Late Blight",
            "hi" to "पछेती झुलसा रोग (फाइटोफ्थोरा)",
            "gu" to "પાછોતરો સુકારો",
            "mr" to "उशिरा येणारा करपा (पछेती करपा)",
            "pa" to "ਪਛੇਤਾ ਝੁਲਸ ਰੋਗ",
            "bn" to "নাবী ধসা রোগ",
            "ta" to "பின் பருவ கருகல் நோய்",
            "te" to "లేట్ బ్లైట్ తెగులు",
            "kn" to "ತಡವಾದ ಕರಕಲು ರೋಗ",
            "ml" to "പിൽക്കാല കരിച്ചിൽ",
            "or" to "ପଛୁଆ ଝାଉଁଳା ରୋଗ",
            "as" to "পাছতীয়া পাত শুকোৱা ৰୋଗ",
            "ur" to "پچھتائی جھلسائو",
            "mai" to "पछेती झुलसा"
        ),
        "powdery mildew" to mapOf(
            "en" to "Powdery Mildew",
            "hi" to "चूर्णिल आसिता (सफेद फफूंद)",
            "gu" to "ભૂરી રોગ / સફેદ ફૂગ",
            "mr" to "भुरी रोग (पांढरी बुरशी)",
            "pa" to "ਚਿੱਟੀ ਉੱਲੀ ਰੋਗ",
            "bn" to "পাউডারি মিলডিউ (সাদা ছত্রাক)",
            "ta" to "சாம்பல் நோய்",
            "te" to "బూడిద తెగులు",
            "kn" to "ಬೂದಿ ರೋಗ",
            "ml" to "ചാരപ്പൂപ്പ് രോഗം",
            "or" to "ଧଳା ଫିମ୍ପି ରୋଗ",
            "as" to "পাউডাৰী মিলডিউ",
            "ur" to "سفید پھپھوندی",
            "mai" to "सफेद फफूंद"
        ),
        "leaf rust" to mapOf(
            "en" to "Leaf Rust",
            "hi" to "पत्ती का रतुआ रोग (रस्ट)",
            "gu" to "પાનનો ગેરુ રોગ",
            "mr" to "पानावरील तांबेरा रोग",
            "pa" to "ਪੱਤਿਆਂ ਦਾ ਕੁੰਗੀ ਰੋਗ",
            "bn" to "পাতার মরিচা রোগ",
            "ta" to "இலை துரு நோய்",
            "te" to "ఆకు తుప్పు తెగులు",
            "kn" to "ಎಲೆ ತುಕ್ಕು ರೋಗ",
            "ml" to "ഇല തുരുമ്പ് രോഗം",
            "or" to "ପତ୍ର କଳଙ୍କି ରୋଗ",
            "as" to "পাতৰ মামৰ ৰোগ",
            "ur" to "پتوں کا زنگ",
            "mai" to "पत्ता के गेरुआ"
        ),
        "apple scab" to mapOf(
            "en" to "Apple Scab",
            "hi" to "सेब का स्कैब रोग",
            "gu" to "સફરજનનો સ્કેબ રોગ",
            "mr" to "सफरचंदाचा खवडे रोग (स्कॅब)",
            "pa" to "ਸੇਬ ਦਾ ਸਕੈਬ ਰੋਗ",
            "bn" to "আপেলের স্ক্যাব রোগ",
            "ta" to "ஆப்பிள் ஸ்கேப் நோய்",
            "te" to "ஆపిల్ స్కాబ్ తెగులు",
            "kn" to "ಸೇಬಿನ ಸ್ಕ್ಯಾಬ್ ರೋಗ",
            "ml" to "ആപ്പിൾ സ്കാബ് രോഗം",
            "or" to "ସେଓ ସ୍କାବ୍ ରୋଗ",
            "as" to "আপেলৰ স্কেব ৰোগ",
            "ur" to "سیب کا خارش زدہ مرض",
            "mai" to "सेबक स्कैब रोग"
        ),
        "black rot" to mapOf(
            "en" to "Black Rot",
            "hi" to "काली सड़न (ब्लैक रॉट)",
            "gu" to "કાળો સડો",
            "mr" to "काळी कूज (ब्लॅक रॉट)",
            "pa" to "ਕਾਲੀ ਸੜਨ ਰੋਗ",
            "bn" to "কালো পচন রোগ",
            "ta" to "கருப்பு அழுகல் நோய்",
            "te" to "నల్ల కుళ్లు తెగులు",
            "kn" to "ಕಪ್ಪು ಕೊಳೆತ ರೋಗ",
            "ml" to "കറുത്ത ചീയൽ രോഗം",
            "or" to "କଳା ପଚା ରୋଗ",
            "as" to "কলা পচন ৰোগ",
            "ur" to "سیاہ سڑن",
            "mai" to "करिया सड़न रोग"
        ),
        "cedar apple rust" to mapOf(
            "en" to "Cedar Apple Rust",
            "hi" to "देवदार-सेब रतुआ",
            "gu" to "સીડર એપલ રસ્ટ",
            "mr" to "सिडार ॲपल रस्ट (तांबेरा)",
            "pa" to "ਸਿਡਾਰ ਐਪਲ ਰਸਟ",
            "bn" to "সিডার আপেল মরিচা",
            "ta" to "சீடார் ஆப்பிள் துரு நோய்",
            "te" to "సెడార్ ஆపిల్ తుప్పు తెగులు",
            "kn" to "ಸಿಡಾರ್ ಸೇಬು ತುಕ್ಕು ರೋಗ",
            "ml" to "സീഡാർ ആപ്പിൾ തുരുമ്പ് രോഗം",
            "or" to "ସିଡାର୍ ସେଓ କଳଙ୍କି ରୋଗ",
            "as" to "চিডাৰ আপেল মামৰ ৰোগ",
            "ur" to "سیب کا زنگال",
            "mai" to "देवदार सेब गेरुआ"
        ),
        "cercospora leaf spot" to mapOf(
            "en" to "Cercospora / Gray Leaf Spot",
            "hi" to "सर्कोस्पोरा / धूसर पत्ती धब्बा",
            "gu" to "ગ્રે લીફ સ્પોટ / પાનનાં ટપકાં",
            "mr" to "पानावरील करपा व करडे ठिपके",
            "pa" to "ਸਰਕੋਸਪੋਰਾ ਪੱਤਾ ਧੱਬਾ ਰੋਗ",
            "bn" to "ধূসর পাতার দাগ রোগ",
            "ta" to "சாம்பல் நிற இலை புள்ளி நோய்",
            "te" to "బూడిద రంగు ఆకు మచ్చ తెగులు",
            "kn" to "ಬೂದು ಎಲೆ ಕಲೆ ರೋಗ",
            "ml" to "ചാര ഇലപ്പുള്ളി രോഗം",
            "or" to "ପାଉଁଶିଆ ପତ୍ର ଦାଗ ରୋଗ",
            "as" to "ধূসৰ পাতৰ দাগ ৰোগ",
            "ur" to "پتوں کے خاکستری دھبے",
            "mai" to "धूसर पत्ता धब्बा रोग"
        ),
        "gray leaf spot" to mapOf(
            "en" to "Cercospora / Gray Leaf Spot",
            "hi" to "सर्कोस्पोरा / धूसर पत्ती धब्बा",
            "gu" to "ગ્રે લીફ સ્પોટ / પાનનાં ટપકાં",
            "mr" to "पानावरील करपा व करडे ठिपके",
            "pa" to "ਸਰਕੋਸਪੋਰਾ ਪੱਤਾ ਧੱਬਾ ਰੋਗ",
            "bn" to "ধূসর পাতার দাগ রোগ",
            "ta" to "சாம்பல் நிற இலை புள்ளி நோய்",
            "te" to "బూడిద రంగు ఆకు మచ్చ తెగులు",
            "kn" to "ಬೂದು ಎಲೆ ಕಲೆ ರೋಗ",
            "ml" to "ചാര ഇലപ്പുള്ളಿ രോഗം",
            "or" to "ପାଉଁଶିଆ ପତ୍ର ଦାଗ ରୋଗ",
            "as" to "ধূসৰ পাতৰ দাগ ৰোগ",
            "ur" to "پتوں کے خاکستری دھبے",
            "mai" to "धूसर पत्ता धब्बा रोग"
        ),
        "common rust" to mapOf(
            "en" to "Common Rust",
            "hi" to "सामान्य रतुआ रोग",
            "gu" to "સામાન્ય ગેરુ રોગ",
            "mr" to "साधारण तांबेरा रोग",
            "pa" to "ਆਮ ਕੁੰਗੀ ਰੋਗ",
            "bn" to "সাধারণ মরিচা রোগ",
            "ta" to "துரு நோய்",
            "te" to "సాధారణ తుప్పు తెగులు",
            "kn" to "ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ",
            "ml" to "സാധാരണ തുരുമ്പ് രോഗം",
            "or" to "ସାଧାରଣ କଳଙ୍କି ରୋଗ",
            "as" to "সাধাৰণ মামৰ ৰোগ",
            "ur" to "عام زنگ",
            "mai" to "सामान्य गेरुआ रोग"
        ),
        "northern leaf blight" to mapOf(
            "en" to "Northern Leaf Blight",
            "hi" to "उत्तरी पत्ती झुलसा",
            "gu" to "પાનનો મોટો સુકારો",
            "mr" to "नॉर्दर्न लीफ ब्लाइट (पर्ण करपा)",
            "pa" to "ਉੱਤਰੀ ਪੱਤਾ ਝੁਲਸ ਰੋਗ",
            "bn" to "উত্তুরে পাতা ধসা রোগ",
            "ta" to "இலை கருகல் நோய்",
            "te" to "నార్తర్న్ ఆకు తెగులు",
            "kn" to "ಉತ್ತರ ಎಲೆ ಕರಕಲು ರೋಗ",
            "ml" to "ഇല കരിച്ചിൽ രോഗം",
            "or" to "ଉତ୍ତର ପତ୍ର ଝାଉଁଳା ରୋଗ",
            "as" to "উত্তৰীয়া পাত শুকোৱা ৰোগ",
            "ur" to "شمالی پتوں کا جھلسائو",
            "mai" to "उत्तरी पत्ता झुलसा"
        ),
        "esca" to mapOf(
            "en" to "Esca (Black Measles)",
            "hi" to "एस्का (अंगूर का काला दाना रोग)",
            "gu" to "એસ્કા (દ્રાક્ષનો રોગ)",
            "mr" to "एस्का (द्राक्षावरील काळे ठिपके)",
            "pa" to "ਏਸਕਾ ਰੋਗ",
            "bn" to "এস্কা রোগ",
            "ta" to "எஸ்கா நோய்",
            "te" to "ఎస్కా తెగులు",
            "kn" to "ಎಸ್ಕಾ ರೋಗ",
            "ml" to "എസ്ക രോഗം",
            "or" to "ଏସ୍କା ରୋଗ",
            "as" to "এস্কা ৰোগ",
            "ur" to "انگور کا اسکا مرض",
            "mai" to "एस्का रोग"
        ),
        "citrus greening" to mapOf(
            "en" to "Citrus Greening (HLB)",
            "hi" to "सिट्रस ग्रीनिंग (हुआंगलोंगबिंग)",
            "gu" to "સિટ્રસ ગ્રીનીંગ રોગ",
            "mr" to "सिट्रस ग्रीनिंग (लिंबूवर्गीय पिवळेपणा)",
            "pa" to "ਨਿੰਬੂ ਜਾਤੀ ਗ੍ਰੀਨਿੰਗ ਰੋਗ",
            "bn" to "লেবুর গ্রিনিং রোগ",
            "ta" to "சிட்ரஸ் கிரீனிங் நோய்",
            "te" to "సిట్రస్ గ్రీనింగ్ తెగులు",
            "kn" to "ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗ",
            "ml" to "സിട്രസ് ഗ്രീനിംഗ് രോഗം",
            "or" to "ଲେମ୍ବୁ ଜାତୀୟ ଗ୍ରୀନିଂ ରୋଗ",
            "as" to "নেমুৰ গ্ৰীনিং ৰোগ",
            "ur" to "سٹرس گریننگ",
            "mai" to "सिट्रस ग्रीनिंग रोग"
        ),
        "haunglongbing" to mapOf(
            "en" to "Citrus Greening (HLB)",
            "hi" to "सिट्रस ग्रीनिंग (हुआंगलोंगबिंग)",
            "gu" to "સિટ્રસ ગ્રીનીંગ રોગ",
            "mr" to "सिट्रस ग्रीनिंग (लिंबूवर्गीय पिवळेपणा)",
            "pa" to "ਨਿੰਬੂ ਜਾਤੀ ਗ੍ਰੀਨਿੰਗ ਰੋਗ",
            "bn" to "লেবুর গ্রিনিং রোগ",
            "ta" to "சிட்ரஸ் கிரீனிங் நோய்",
            "te" to "సిట్రస్ గ్రీనింగ్ తెగులు",
            "kn" to "ಸಿಟ್ರಸ್ ಗ್ರೀನಿಂಗ್ ರೋಗ",
            "ml" to "സിട്രസ് ഗ്രീനിംഗ് രോഗം",
            "or" to "ଲେମ୍ବୁ ଜାତୀୟ ଗ୍ରୀନିଂ ରୋଗ",
            "as" to "নেমুৰ গ্ৰীনিং ৰোগ",
            "ur" to "سٹرس گریننگ",
            "mai" to "सिट्रस ग्रीनिंग रोग"
        ),
        "leaf scorch" to mapOf(
            "en" to "Leaf Scorch",
            "hi" to "पत्ती झुलसन (लीफ स्कॉर्च)",
            "gu" to "પાન બળી જવાનો રોગ",
            "mr" to "पाने करपणे (लीफ स्कॉर्च)",
            "pa" to "ਪੱਤਾ ਝੁਲਸਣਾ",
            "bn" to "পাতা পোড়া রোগ",
            "ta" to "இலை கருகல்",
            "te" to "ఆకు మాడిపోవు తెగులు",
            "kn" to "ಎಲೆ ಸುಟ್ಟ ರೋಗ",
            "ml" to "ഇല കരിച്ചിൽ",
            "or" to "ପତ୍ର ପୋଡ଼ିବା ରୋଗ",
            "as" to "পাত পোৰা ৰোগ",
            "ur" to "پتوں کا جلنا",
            "mai" to "पत्ता झुलसइब"
        ),
        "leaf mold" to mapOf(
            "en" to "Leaf Mold",
            "hi" to "पत्ती की फफूंद (लीफ मोल्ड)",
            "gu" to "પાનની ફૂગ (લીફ મોલ્ડ)",
            "mr" to "पानावरील बुरशी (लीफ मोल्ड)",
            "pa" to "ਪੱਤੇ ਦੀ ਉੱਲੀ",
            "bn" to "পাতার ছত্রাক রোগ",
            "ta" to "இலை பூஞ்சை நோய்",
            "te" to "ఆకు బూజు తెగులు",
            "kn" to "ಎಲೆ ಬೂಷ್ಟು ರೋಗ",
            "ml" to "ഇല പൂപ്പൽ രോഗം",
            "or" to "ପତ୍ର ଫିମ୍ପି ରୋଗ",
            "as" to "পাতৰ ভেঁকুৰ ৰোগ",
            "ur" to "پتوں کی پھپھوندی",
            "mai" to "पत्ता के फफूंदी"
        ),
        "septoria leaf spot" to mapOf(
            "en" to "Septoria Leaf Spot",
            "hi" to "सेप्टोरिया पत्ती धब्बा",
            "gu" to "સેપ્ટોરિયા પાનનાં ટપકાં",
            "mr" to "सेप्टोरिया पानांवरील ठिपके",
            "pa" to "ਸੈਪਟੋਰੀਆ ਪੱਤਾ ਧੱਬਾ",
            "bn" to "সেপ্টোরিয়া পাতার দাগ",
            "ta" to "செப்டோரியா இலை புள்ளி நோய்",
            "te" to "సెప్టోరియా ఆకు మచ్చ తెగులు",
            "kn" to "ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಕಲೆ ರೋಗ",
            "ml" to "സെപ്റ്റോറിയ ഇലപ്പുള്ളി രോഗം",
            "or" to "ସେପ୍ଟୋରିଆ ପତ୍ର ଦାଗ",
            "as" to "চেপ্টোৰিয়া পাতৰ দাগ",
            "ur" to "سیپٹوریا کے داغ",
            "mai" to "सेप्टोरिया पत्ता धब्बा"
        ),
        "spider mites" to mapOf(
            "en" to "Two-Spotted Spider Mites",
            "hi" to "लाल मकड़ी / माइट्स का प्रकोप",
            "gu" to "લાલ કથીરી / સ્પાઈડર માઈટ્સ",
            "mr" to "लाल कोळी किडींचा प्रादुर्भाव",
            "pa" to "ਲਾਲ ਮਕੌੜਾ / ਮਾਈਟਸ",
            "bn" to "লাল মাকড়সার আক্রমণ",
            "ta" to "செம்பேன் / சிலந்தி பூச்சி தாக்குதல்",
            "te" to "ఎర్ర నల్లి / స్పైడర్ మైట్స్",
            "kn" to "ಕೆಂಪು ನುಸಿ ಕೀಟ ಬಾಧೆ",
            "ml" to "മണ്ഡരി / ചിലന്തി ശല്യം",
            "or" to "ଲାଲ୍ ବୁଢ଼ିଆଣୀ କୀଟ",
            "as" to "ৰঙা মকৰা পোকৰ আক্ৰমণ",
            "ur" to "سرخ مکڑی کے کیڑے",
            "mai" to "लाल मकड़ी केर प्रकोप"
        ),
        "target spot" to mapOf(
            "en" to "Target Spot",
            "hi" to "टारगेट स्पॉट (गोल धब्बा रोग)",
            "gu" to "ટાર્ગેટ સ્પોટ રોગ",
            "mr" to "टार्गेट स्पॉट (चकतीसारखे ठिपके)",
            "pa" to "ਟਾਰਗੇਟ ਸਪਾਟ ਰੋਗ",
            "bn" to "টার্গেট স্পট রোগ",
            "ta" to "டார்கெட் ஸ்பாட் நோய்",
            "te" to "టార్గెట్ స్పాట్ తెగులు",
            "kn" to "ಟಾರ್ಗೆಟ್ ಸ್ಪಾಟ್ ರೋಗ",
            "ml" to "ടാർഗെറ്റ് സ്പോട്ട് രോഗം",
            "or" to "ଟାର୍ଗେଟ୍ ଦାଗ ରୋଗ",
            "as" to "টাৰ্গেট দাগ ৰোগ",
            "ur" to "ہدف نما داغ",
            "mai" to "टारगेट स्पॉट रोग"
        ),
        "tomato yellow leaf curl virus" to mapOf(
            "en" to "Tomato Yellow Leaf Curl Virus",
            "hi" to "टमाटर पीली पत्ती मरोड़िया वायरस",
            "gu" to "ટામેટા પીળી પાન વળવાનો વાયરસ",
            "mr" to "टोमॅटो पर्णगुच्छ / पिवळा चुरडा-मुरडा",
            "pa" to "ਪੀਲਾ ਪੱਤਾ ਮਰੋੜ ਵਿਸ਼ਾਣੂ",
            "bn" to "পাতা কোঁকড়ানো হলুদ ভাইরাস",
            "ta" to "இலை சுருட்டு வைரஸ் நோய்",
            "te" to "ఆకు ముడత వైరస్ తెగులు",
            "kn" to "ಎಲೆ ಮುದುರು ವೈರಸ್ ರೋಗ",
            "ml" to "ഇലച്ചുരുൾ വൈറസ് രോഗം",
            "or" to "ହଳଦିଆ ପତ୍ର ମୋଡ଼ା ଭୂତାଣୁ",
            "as" to "পাত কোঁচোৱা ভাইৰাছ ৰোগ",
            "ur" to "پتے مڑنے کا زرد وائرس",
            "mai" to "पीला पत्ता मरोड़िया वायरस"
        ),
        "tomato mosaic virus" to mapOf(
            "en" to "Tomato Mosaic Virus",
            "hi" to "मोजेक वायरस (चित्तीदार रोग)",
            "gu" to "મોઝેક વાયરસ",
            "mr" to "मोझॅक विषाणू (पिवळे चट्टे)",
            "pa" to "ਮੋਜ਼ੇਕ ਵਿਸ਼ਾਣੂ ਰੋਗ",
            "bn" to "মোজাইক ভাইরাস রোগ",
            "ta" to "மொசைக் வைரஸ் நோய்",
            "te" to "మొజాయిక్ వైరస్ తెగులు",
            "kn" to "ಮೊಸಾಯಿಕ್ ವೈರಸ್ ರೋಗ",
            "ml" to "മൊസൈക് വൈറസ് രോഗം",
            "or" to "ମୋଜାଇକ୍ ଭୂତାଣୁ ରୋଗ",
            "as" to "ম'জাইক ভাইৰাছ ৰোগ",
            "ur" to "موزیک وائرس",
            "mai" to "मोजेक वायरस रोग"
        ),
        "mosaic virus" to mapOf(
            "en" to "Mosaic Virus",
            "hi" to "मोजेक वायरस (चित्तीदार रोग)",
            "gu" to "મોઝેક વાયરસ",
            "mr" to "मोझॅक विषाणू (पिवळे चट्टे)",
            "pa" to "ਮੋਜ਼ੇਕ ਵਿਸ਼ਾਣੂ ਰੋਗ",
            "bn" to "মোজাইক ভাইরাস রোগ",
            "ta" to "மொசைக் வைரஸ் நோய்",
            "te" to "మొజాయిక్ వైరస్ తెగులు",
            "kn" to "ಮೊಸಾಯಿಕ್ ವೈರಸ್ ರೋಗ",
            "ml" to "മൊസൈക് വൈറസ് രോഗം",
            "or" to "ମୋଜାଇକ୍ ଭୂତାଣୁ ରୋଗ",
            "as" to "ম'জাইক ভাইৰাছ ৰোগ",
            "ur" to "موزیک وائرس",
            "mai" to "मोजेक वायरस रोग"
        )
    )

    // ==========================================
    // 5. WILDLIFE & LIVESTOCK (14 LANGUAGES)
    // ==========================================
    private val ANIMALS = mapOf(
        "wild boar" to mapOf("en" to "Wild Boar", "hi" to "जंगली सूअर", "gu" to "જંગલી ભૂંડ", "mr" to "रानडुक्कर", "pa" to "ਜੰਗਲੀ ਸੂਰ", "bn" to "বুনো শুয়োর", "ta" to "காட்டுப் பன்றி", "te" to "అడవి పంది", "kn" to "ಕಾಡು ಹಂದಿ", "ml" to "കാട്ടുപന്നി", "or" to "ବଣୁଆ ଘୁଷୁରି", "as" to "বনৰীয়া গাহৰি", "ur" to "جنگلی سور", "mai" to "जंगली सूअर"),
        "nilgai" to mapOf("en" to "Nilgai", "hi" to "नीलगाय / घोड़परास", "gu" to "નીલગાય / રોજ", "mr" to "नीलगाय", "pa" to "ਨੀਲਗਾਂ", "bn" to "নীলগাই", "ta" to "நீல மான் (நீல்காய்)", "te" to "నీలుగాయి", "kn" to "ನೀಲಗಾಯಿ", "ml" to "നീൽഗായ്", "or" to "ନୀଳଗାଈ", "as" to "নীলগাই", "ur" to "نیل گائے", "mai" to "घ घोड़परास"),
        "elephant" to mapOf("en" to "Elephant", "hi" to "हाथी", "gu" to "હાથી", "mr" to "हत्ती", "pa" to "ਹਾਥੀ", "bn" to "হাতি", "ta" to "யானை", "te" to "ఏనుగు", "kn" to "ಆನೆ", "ml" to "ആന", "or" to "ହାତୀ", "as" to "হাতী", "ur" to "ہاتھی", "mai" to "हाथी"),
        "monkey" to mapOf("en" to "Monkey", "hi" to "बंदर", "gu" to "વાંદરો", "mr" to "माकड", "pa" to "ਬਾਂਦਰ", "bn" to "বানর", "ta" to "குரங்கு", "te" to "కోతి", "kn" to "ಕೋತಿ", "ml" to "കുരങ്ങ്", "or" to "ମାଙ୍କଡ଼", "as" to "বান্দৰ", "ur" to "بندر", "mai" to "बानर"),
        "deer" to mapOf("en" to "Deer", "hi" to "हिरण", "gu" to "હરણ", "mr" to "हरिण", "pa" to "ਹਿਰਨ", "bn" to "হরিণ", "ta" to "மான்", "te" to "జింక", "kn" to "ಜಿಂಕೆ", "ml" to "മാൻ", "or" to "ହରିଣ", "as" to "হৰিণা", "ur" to "ہرن", "mai" to "हरिण"),
        "cow" to mapOf("en" to "Cow", "hi" to "गाय", "gu" to "ગાય", "mr" to "गाय", "pa" to "ਗਾਂ", "bn" to "গরু", "ta" to "பசு", "te" to "ఆవు", "kn" to "ಹಸು", "ml" to "പശു", "or" to "ଗାଈ", "as" to "গৰু", "ur" to "گائے", "mai" to "गाय"),
        "bull" to mapOf("en" to "Bull", "hi" to "बैल / सांड", "gu" to "બળદ / આખલો", "mr" to "बैल", "pa" to "ਬਲਦ", "bn" to "ষাঁড়", "ta" to "காளை", "te" to "ఎద్దు", "kn" to "ಎತ್ತು", "ml" to "കാള", "or" to "ବଳଦ", "as" to "বলध", "ur" to "بیل", "mai" to "बैल")
    )

    // ==========================================
    // 6. SEVERITIES & STATUS BADGES (14 LANGUAGES)
    // ==========================================
    private val SEVERITIES = mapOf(
        "critical" to mapOf("en" to "CRITICAL", "hi" to "गंभीर", "gu" to "ગંભીર", "mr" to "अतिगंभीर", "pa" to "ਨਾਜ਼ੁਕ", "bn" to "মারাত্মক", "ta" to "மிகத் தீவிரம்", "te" to "తీవ్రమైనది", "kn" to "ಅಪಾಯಕಾರಿ", "ml" to "ഗുരുതരം", "or" to "ଅତି ଗୁରୁତର", "as" to "অতি সংকটজনক", "ur" to "انتہائی شدید", "mai" to "अति गंभीर"),
        "high" to mapOf("en" to "HIGH", "hi" to "उच्च", "gu" to "ઊંચું", "mr" to "जास्त", "pa" to "ਉੱਚ", "bn" to "উচ্চ", "ta" to "அதிகம்", "te" to "ఎక్కువ", "kn" to "ಹೆಚ್ಚು", "ml" to "ഉയർന്ന", "or" to "ଉଚ୍ଚ", "as" to "উচ্চ", "ur" to "زیادہ", "mai" to "उच्च"),
        "moderate" to mapOf("en" to "MODERATE", "hi" to "मध्यम", "gu" to "મધ્યમ", "mr" to "मध्यम", "pa" to "ਦਰਮਿਆਨਾ", "bn" to "মাঝারি", "ta" to "மிதமான", "te" to "మితమైన", "kn" to "ಮಧ್ಯಮ", "ml" to "മിതമായ", "or" to "ମଧ୍ୟମ", "as" to "মজলীয়া", "ur" to "معتدل", "mai" to "मध्यम"),
        "low" to mapOf("en" to "LOW", "hi" to "कम", "gu" to "ઓછું", "mr" to "कमी", "pa" to "ਘੱਟ", "bn" to "কম", "ta" to "குறைவு", "te" to "తక్కువ", "kn" to "ಕಡಿಮೆ", "ml" to "കുറഞ്ഞ", "or" to "କମ୍", "as" to "কম", "ur" to "کم", "mai" to "कम"),
        "no threat" to mapOf("en" to "NO THREAT", "hi" to "कोई खतरा नहीं", "gu" to "કોઈ જોખમ નથી", "mr" to "धोका नाही", "pa" to "ਕੋਈ ਖਤਰਾ ਨਹੀਂ", "bn" to "কোনো ঝুঁকি নেই", "ta" to "அபாயம் இல்லை", "te" to "ప్రమాదం లేదు", "kn" to "ಅಪಾಯವಿಲ್ಲ", "ml" to "ഭീഷണിയില്ല", "or" to "ବିପଦ ନାହିଁ", "as" to "কোনো বিপদ নাই", "ur" to "کوئی خطرہ نہیں", "mai" to "कुनो खतरा नहि"),
        "none" to mapOf("en" to "NO THREAT", "hi" to "कोई खतरा नहीं", "gu" to "કોઈ જોખમ નથી", "mr" to "धोका नाही", "pa" to "ਕੋਈ ਖਤਰਾ ਨਹੀਂ", "bn" to "কোনো ঝুঁকি নেই", "ta" to "அபாயம் இல்லை", "te" to "ప్రమాదం లేదు", "kn" to "ಅಪಾಯವಿಲ್ಲ", "ml" to "ഭീഷണിയില്ല", "or" to "ବିପଦ ନାହିଁ", "as" to "কোনো বিপদ নাই", "ur" to "کوئی خطرہ नहीं", "mai" to "कुनो खतरा नहि"),
        "healthy" to mapOf("en" to "HEALTHY", "hi" to "स्वस्थ", "gu" to "સ્વસ્થ", "mr" to "निरोगी", "pa" to "ਸਿਹਤਮੰਦ", "bn" to "সুস্থ", "ta" to "ஆரோக்கியமானது", "te" to "ఆరోగ్యకరమైనది", "kn" to "ಆರೋಗ್ಯಕರ", "ml" to "ആരോഗ്യമുള്ളത്", "or" to "ସୁସ୍ଥ", "as" to "সুস্থ", "ur" to "صحت مند", "mai" to "स्वस्थ"),
        "diseased" to mapOf("en" to "DISEASED", "hi" to "रोगग्रस्त", "gu" to "રોગગ્રસ્ત", "mr" to "रोगग्रस्त", "pa" to "ਬਿਮਾਰੀ ਵਾਲਾ", "bn" to "রোগাক্রান্ত", "ta" to "நோயுற்றது", "te" to "వ్యాధిగ్రస్తం", "kn" to "ರೋಗಗ್ರಸ್ತ", "ml" to "രോഗബാധിതമായ", "or" to "ରୋଗାକ୍ରାନ୍ତ", "as" to "ৰোগাক্ৰান্ত", "ur" to "بیمار", "mai" to "रोगग्रस्त")
    )

    // ==========================================
    // 7. TIME & GENERAL TERMS (14 LANGUAGES)
    // ==========================================
    private val TIME_TERMS = mapOf(
        "today" to mapOf("en" to "Today", "hi" to "आज", "gu" to "આજે", "mr" to "आज", "pa" to "ਅੱਜ", "bn" to "আজ", "ta" to "இன்று", "te" to "ఈ రోజు", "kn" to "ಇಂದು", "ml" to "ഇന്ന്", "or" to "ଆଜି", "as" to "আজি", "ur" to "آج", "mai" to "आइज"),
        "tomorrow" to mapOf("en" to "Tomorrow", "hi" to "कल", "gu" to "આવતીકાલે", "mr" to "उद्या", "pa" to "ਭਲਕੇ", "bn" to "আগামীকাল", "ta" to "நாளை", "te" to "రేపు", "kn" to "ನಾಳೆ", "ml" to "ನಾಳೆ", "or" to "ଆସନ୍ତାକାଲି", "as" to "কাইলৈ", "ur" to "کل", "mai" to "कालि"),
        "yesterday" to mapOf("en" to "Yesterday", "hi" to "बीता कल", "gu" to "ગઈકાલે", "mr" to "काल", "pa" to "ਕੱਲ੍ਹ", "bn" to "গতকাল", "ta" to "நேற்று", "te" to "ನಿನ್ನ", "kn" to "ನಿನ್ನೆ", "ml" to "ഇന്നലെ", "or" to "ଗତକାଲି", "as" to "যোৱাকালী", "ur" to "گزشتہ کل", "mai" to "काल")
    )

    // ==========================================
    // 8. DYNAMIC AGRICULTURAL SENTENCE & ADVICE LOCALIZERS
    // ==========================================
    private val ADVICE_PATTERNS = listOf(
        // 1. Prevention: Foliage wet
        Pair("foliage is wet", mapOf(
            "en" to "Avoid working in fields when foliage is wet to prevent spreading pathogens",
            "hi" to "पत्तियां गीली होने पर खेत में काम करने से बचें ताकि रोग न फैले",
            "gu" to "પાંદડાં ભીનાં હોય ત્યારે ખેતરમાં કામ કરવાનું ટાળો જેથી રોગ ન ફેલાય",
            "mr" to "पाने ओली असताना शेतात काम करणे टाळा जेणेकरून रोगाचा प्रसार होणार नाही",
            "pa" to "ਪੱਤੇ ਗਿੱਲੇ ਹੋਣ 'ਤੇ ਖੇਤ ਵਿੱਚ ਕੰਮ ਕਰਨ ਤੋਂ ਬਚੋ ਤਾਂ ਜੋ ਬਿਮਾਰੀ ਨਾ ਫੈਲੇ",
            "bn" to "পাতা ভেজা থাকা অবস্থায় জমিতে কাজ করা পরিহার করুন যাতে রোগ না ছড়ায়",
            "ta" to "இலைகள் ஈரமாக இருக்கும் போது வயலில் வேலை செய்வதைத் தவிர்க்கவும்",
            "te" to "ఆకులు తడిగా ఉన్నప్పుడు పొలంలో పని చేయవద్దు",
            "kn" to "ಎಲೆಗಳು ತೇವವಾಗಿರುವಾಗ ಹೊಲದಲ್ಲಿ ಕೆಲಸ ಮಾಡುವುದನ್ನು ತಪ್ಪಿಸಿ",
            "ml" to "ഇലകൾ നനഞ്ഞിരിക്കുമ്പോൾ തോട്ടത്തിൽ ജോലി ചെയ്യുന്നത് ഒഴിവാക്കുക",
            "or" to "ପତ୍ର ଓଦା ଥିବା ସମୟରେ କ୍ଷେତରେ କାମ କରିବା ବନ୍ଦ କରନ୍ତୁ",
            "as" to "পাত তিতা হৈ থকা অৱস্থাত পথাৰত কাম কৰাৰ পৰা বিৰত থাকক",
            "ur" to "پتے گیلے ہونے پر کھیت میں کام کرنے سے گریز کریں",
            "mai" to "पत्ता भीजल रहला पर खेत मे काज करय सं बचू जाहि सं बीमारी नहि फैलय"
        )),

        // 2. Biological: Bacillus subtilis / Pseudomonas fluorescens
        Pair("bacillus subtilis", mapOf(
            "en" to "Biological: Foliar spray of Bacillus subtilis or Pseudomonas fluorescens @ 5 g/L",
            "hi" to "जैविक नियंत्रण: बैसिलस सबटिलिस या स्यूडोमोनास फ्लोरोसेंस (5 ग्राम/लीटर) का पत्तियों पर छिड़काव करें",
            "gu" to "જૈવિક નિયંત્રણ: બેસિલસ સબટિલિસ અથવા સ્યુડોમોનાસ ફ્લોરોસેન્સ (5 ગ્રામ/લિટર) નો પાન પર છંટકાવ કરો",
            "mr" to "जैविक उपाय: बॅसिलस सबटिलिस किंवा स्यूडोमोनास फ्लोरोसन्स (५ ग्रॅम/लिटर) ची पानांवर फवारणी करा",
            "pa" to "ਜੈਵਿਕ ਰੋਕਥਾਮ: ਬੈਸੀਲਸ ਸਬਟਿਲਿਸ ਜਾਂ ਸੂਡੋਮੋਨਾਸ ਫਲੋਰੋਸੈਂਸ (5 ਗ੍ਰਾਮ/ਲੀਟਰ) ਦਾ ਛਿੜਕਾਅ ਕਰੋ",
            "bn" to "জৈব নিয়ন্ত্রণ: ব্যাসিলাস সাবটিলিস বা সিউডোমোনাস ফ্লুরোসেন্স (৫ গ্রাম/লিটার) পাতায় স্প্রে করুন",
            "ta" to "இயற்கை கட்டுப்பாடு: பேசிலஸ் சப்டிலிஸ் அல்லது சூடோமோனாஸ் (5 கிராம்/லிட்டர்) இலைகளில் தெளிக்கவும்",
            "te" to "జీవ నియంత్రణ: బాసిల్లస్ సబ్టిలిస్ లేదా సూడోమోనాస్ (5 గ్రా/లీ) ఆకులపై పిచికారీ చేయండి",
            "kn" to "ಜೈವಿಕ ನಿಯಂತ್ರಣ: ಬ್ಯಾಸಿಲಸ್ ಸಬ್ಟಿಲಿಸ್ ಅಥವಾ ಸ್ಯೂಡೋಮೊನಾಸ್ (5 ಗ್ರಾಂ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ",
            "ml" to "ജൈവ നിയന്ത്രണം: ബാസിലസ് സബ്റ്റിലിസ് അല്ലെങ്കിൽ സ്യൂഡോമോണസ് (5 ഗ്രാം/ലിറ്റർ) തളിക്കുക",
            "or" to "ଜୈବିକ ନିୟନ୍ତ୍ରଣ: ବ୍ୟାସିଲସ୍ ସବଟିଲିସ୍ କିମ୍ବା ସୁଡୋମୋନାସ୍ (୫ ଗ୍ରାମ୍/ଲିଟର) ସ୍ପ୍ରେ କରନ୍ତୁ",
            "as" to "জৈৱিক নিয়ন্ত্ৰণ: বেচিলেচ চাবটিলিচ বা চিউড'ম'নাচ (৫ গ্ৰাম/লিটাৰ) পাতত ছটিওৱক",
            "ur" to "حیاتیاتی کنٹرول: باسیلس سبٹیلس یا سیوڈوموناس فلوروسینس (5 گرام فی لیٹر) کا سپرے کریں",
            "mai" to "जैविक नियंत्रण: बैसिलस सबटिलिस वा स्यूडोमोनास (5 ग्राम/लीटर) केर छिड़काव करू"
        )),

        // 3. Chemical: Copper Oxychloride + Streptocycline
        Pair("copper oxychloride", mapOf(
            "en" to "Chemical: Foliar spray of Copper Oxychloride 50% WP @ 2.5 g/L PLUS Streptocycline @ 0.1 g/L every 7-10 days",
            "hi" to "रासायनिक उपाय: कॉपर ऑक्सीक्लोराइड 50% WP (2.5 ग्राम/लीटर) + स्ट्रेप्टोसाइक्लिन (0.1 ग्राम/लीटर) का 7-10 दिनों के अंतराल पर छिड़काव करें",
            "gu" to "રાસાયણિક ઉપાય: કોપર ઓક્સિક્લોરાઇડ 50% WP (2.5 ગ્રામ/લિટર) + સ્ટ્રેપ્ટોસાયક્લિન (0.1 ગ્રામ/લિટર) નો 7-10 દિવસના અંતરે છંટકાવ કરો",
            "mr" to "रासायनिक उपाय: कॉपर ऑक्सिक्लोराईड 50% WP (२.५ ग्रॅम/लिटर) + स्ट्रेप्टोसायक्लिन (०.१ ग्रॅम/लिटर) ची ७-१० दिवसांच्या अंतराने फवारणी करा",
            "pa" to "ਰਸਾਇਣਕ ਰੋਕਥਾਮ: ਕਾਪਰ ਆਕਸੀਕਲੋਰਾਈਡ (2.5 ਗ੍ਰਾਮ/ਲੀਟਰ) + ਸਟ੍ਰੈਪਟੋਸਾਈਕਲਿਨ (0.1 ਗ੍ਰਾਮ/ਲੀਟਰ) ਦਾ 7-10 ਦਿਨਾਂ ਬਾਅਦ ਛਿੜਕਾਅ ਕਰੋ",
            "bn" to "রাসায়নিক নিয়ন্ত্রণ: কপার অক্সিক্লোরাইড ৫০% WP (২.৫ গ্রাম/লিটার) + স্ট্রেপ্টোসাইক্লিন (০.১ গ্রাম/লিটার) ৭-১০ দিন পর পর স্প্রে করুন",
            "ta" to "வேதியியல் கட்டுப்பாடு: காப்பர் ஆக்ஸிகுளோரைடு (2.5 கிராம்/லிட்டர்) + ஸ்ட்ரெப்டோசைக்ளின் (0.1 கிராம்/லிட்டர்) 7-10 நாட்களுக்கு ஒருமுறை தெளிக்கவும்",
            "te" to "రసాయన నియంత్రణ: కాపర్ ఆక్సిక్లోరైడ్ (2.5 గ్రా/లీ) + స్ట్రెప్టోసైక్లిన్ (0.1 గ్రా/లీ) 7-10 రోజుల వ్యవధిలో పిచికారీ చేయండి",
            "kn" to "ರಾಸಾಯನಿಕ ನಿಯಂತ್ರಣ: ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (2.5 ಗ್ರಾಂ/ಲೀಟರ್) + ಸ್ಟ್ರೆಪ್ಟೋಸೈಕ್ಲಿನ್ (0.1 ಗ್ರಾಂ/ಲೀಟರ್) 7-10 ದಿನಗಳಿಗೊಮ್ಮೆ ಸಿಂಪಡಿಸಿ",
            "ml" to "രാസ നിയന്ത്രണം: കോപ്പർ ഓക്സിക്ലോറൈഡ് (2.5 ഗ്രാം/ലിറ്റർ) + സ്ട്രെപ്റ്റോസൈക്ലിൻ (0.1 ഗ്രാം/ലിറ്റർ) 7-10 ദിവസത്തിൽ തളിക്കുക",
            "or" to "ରାସାୟନିକ ନିୟନ୍ତ୍ରଣ: କପର୍ ଅକ୍ସିକ୍ଲୋରାଇଡ୍ (୨.୫ ଗ୍ରାମ୍/ଲିଟର) + ଷ୍ଟ୍ରେପ୍ଟୋସାଇକ୍ଲିନ୍ (୦.୧ ଗ୍ରାମ୍/ଲିଟର) ୭-୧୦ ଦିନରେ ସ୍ପ୍ରେ କରନ୍ତୁ",
            "as" to "ৰাসায়নিক নিয়ন্ত্ৰণ: কপাৰ অক্সিক্ল'ৰাইড (২.৫ গ্ৰাম/লিটাৰ) + ষ্ট্ৰেপ্ট'চাইক্লিন (০.১ গ্ৰাম/লিটাৰ) ৭-১০ দিনৰ ব্যৱধানত ছটিওৱক",
            "ur" to "کیمیائی کنٹرول: کاپر آکسی کلورائڈ (2.5 گرام/لیٹر) + اسٹریپٹوسائکلین (0.1 گرام/لیٹر) کا ہر 7-10 دن بعد سپرے کریں",
            "mai" to "रासायनिक नियंत्रण: कॉपर ऑक्सीक्लोराइड (2.5 ग्राम/लीटर) + स्ट्रेप्टोसाइक्लिन (0.1 ग्राम/लीटर) केर छिड़काव करू"
        )),

        // 4. Cultural: Drip irrigation instead of overhead sprinklers
        Pair("drip irrigation", mapOf(
            "en" to "Cultural: Drip irrigation instead of overhead sprinklers to keep foliage dry",
            "hi" to "कृषि पद्धतियां: पत्तियों को सूखा रखने के लिए फव्वारे की जगह ड्रिप (टपक) सिंचाई प्रणाली अपनाएं",
            "gu" to "કૃષિ પદ્ધતિ: પાંદડાં સૂકાં રાખવા માટે સ્પ્રિંકલરને બદલે ટપક સિંચાઈ પદ્ધતિ અપનાવો",
            "mr" to "मशागत पद्धती: पाने कोरडी राहण्यासाठी तुषार सिंचनाऐवजी ठिबक सिंचन पद्धतीचा वापर करा",
            "pa" to "ਖੇਤੀ ਤਰੀਕੇ: ਪੱਤਿਆਂ ਨੂੰ ਸੁੱਕਾ ਰੱਖਣ ਲਈ ਫੁਹਾਰਾ ਸਿੰਚਾਈ ਦੀ ਥਾਂ ਤੁਪਕਾ ਸਿੰਚਾਈ ਅਪਣਾਓ",
            "bn" to "কৃষি পদ্ধতি: পাতা শুকনো রাখতে ওভারহেড স্প্রিংকলারের বদলে ড্রিপ সেচ ব্যবহার করুন",
            "ta" to "பயிர் மேலாண்மை: இலைகள் ஈரமாகாமல் இருக்க தெளிப்பு நீர்ப்பாசனத்திற்கு பதிலாக சொட்டு நீர் பாசனம் பயன்படுத்தவும்",
            "te" to "సాగు పద్ధతులు: ఆకులు తడవకుండా ఉండటానికి స్ప్రింక్లర్లకు బదులుగా డ్రిప్ ఇరిగేషన్ వాడండి",
            "kn" to "ಕೃಷಿ ಪದ್ಧತಿ: ಎಲೆಗಳು ತೇವವಾಗುವುದನ್ನು ತಪ್ಪಿಸಲು ತುಂತುರು ನೀರಾವರಿ ಬದಲು ಹನಿ ನೀರಾವರಿ ಬಳಸಿ",
            "ml" to "കാർഷിക രീതികൾ: ഇലകൾ നനയാതിരിക്കാൻ തുള്ളി നന രീതി ഉപയോഗിക്കുക",
            "or" to "କୃଷି ପଦ୍ଧତି: ପତ୍ର ଶୁଖିଲା ରଖିବା ପାଇଁ ସ୍ପ୍ରିଙ୍କଲର ବଦଳରେ ବିନ୍ଦୁ ଜଳସେଚନ ବ୍ୟବହାର କରନ୍ତୁ",
            "as" to "কৃষি পদ্ধতি: পাত শুকান ৰাখিবলৈ স্প্ৰিংকলাৰৰ সলনি টোপাল জলসিঞ্চন ব্যৱহাৰ কৰক",
            "ur" to "زرعی طریقے: پتوں کو خشک رکھنے کے لیے فوارے کے بجائے ڈرپ اریگیشن استعمال کریں",
            "mai" to "कृषि पद्धति: पत्ता केँ सूखल रखबाक लेल फव्वाराक बदला ड्रिप सिंचाई करू"
        )),

        // 5. Prevention: Certified disease-free seeds or hot water treated seeds
        Pair("certified disease-free seeds", mapOf(
            "en" to "Use certified disease-free seeds or hot water treated seeds (50°C for 25 minutes)",
            "hi" to "प्रमाणित रोग-मुक्त बीज का उपयोग करें या बीजों को गर्म पानी (50°C पर 25 मिनट) से उपचारित करें",
            "gu" to "પ્રમાણિત રોગમુક્ત બિયારણ વાપરો અથવા ગરમ પાણી (50°C પર 25 મિનિટ) થી બીજ માવજત કરો",
            "mr" to "प्रमाणित रोगमुक्त बियाणे वापरा किंवा बियाण्यांवर गरम पाण्याची प्रक्रिया (५०°C वर २५ मिनिटे) करा",
            "pa" to "ਪ੍ਰਮਾਣਿਤ ਬਿਮਾਰੀ-ਮੁਕਤ ਬੀਜ ਵਰਤੋ ਜਾਂ ਗਰਮ ਪਾਣੀ (50°C 'ਤੇ 25 ਮਿੰਟ) ਨਾਲ ਬੀਜ ਸੋਧ ਕਰੋ",
            "bn" to "রোগমুক্ত প্রত্যায়িত বীজ ব্যবহার করুন বা গরম পানিতে (৫০°C তাপমাত্রায় ২৫ মিনিট) শোধন করুন",
            "ta" to "சான்றளிக்கப்பட்ட நோய் தாக்காத விதைகளைப் பயன்படுத்தவும் அல்லது சுடுநீர் (50°C இல் 25 நிமிடங்கள்) நேர்த்தி செய்யவும்",
            "te" to "ధృవీకరించబడిన నాణ్యమైన విత్తనాలను వాడండి లేదా వేడి నీటితో (50°C వద్ద 25 నిమిషాలు) విత్తన శుద్ధి చేయండి",
            "kn" to "ಪ್ರಮಾಣೀಕೃತ ರೋಗರಹಿತ ಬೀಜಗಳನ್ನು ಬಳಸಿ ಅಥವಾ ಬಿಸಿನೀರಿನಲ್ಲಿ (50°C ನಲ್ಲಿ 25 ನಿಮಿಷ) ಬೀಜೋಪಚಾರ ಮಾಡಿ",
            "ml" to "രോഗബാധയില്ലാത്ത സാക്ഷ്യപ്പെടുത്തിയ വിത്തുകൾ ഉപയോഗിക്കുക അല്ലെങ്കിൽ ചൂടുവെള്ളത്തിൽ (50°C ൽ 25 മിനിറ്റ്) സംസ്കരിക്കുക",
            "or" to "ପ୍ରମାଣିତ ରୋଗମୁକ୍ତ ବିହନ ବ୍ୟବହାର କରନ୍ତୁ କିମ୍ବା ଉଷୁମ ପାଣିରେ (୫୦°C ରେ ୨୫ ମିନିଟ୍) ବିଶୋଧନ କରନ୍ତୁ",
            "as" to "প্ৰমাণিত ৰোগমুক্ত বীজ ব্যৱহাৰ কৰক বা গৰম পানীত (৫০°C ত ২৫ মিনিট) শোধন কৰক",
            "ur" to "تصدیق شدہ بیماری سے پاک بیج استعمال کریں یا بیجوں کو گرم پانی (50 ڈگری سینٹی گریڈ پر 25 منٹ) سے ٹریٹ کریں",
            "mai" to "प्रमाणित रोग-मुक्त बीयाक प्रयोग करू वा गर्म पानि (50°C पर 25 मिनट) सं बीजोपचार करू"
        )),

        // 6. Prevention: 2-year crop rotation
        Pair("crop rotation", mapOf(
            "en" to "Practice 2-year crop rotation avoiding tomato, pepper, eggplant, and potato",
            "hi" to "टमाटर, मिर्च, बैंगन और आलू से बचते हुए 2 वर्षीय फसल चक्र (क्रॉप रोटेशन) अपनाएं",
            "gu" to "ટામેટા, મરચાં, રીંગણ અને બટાકા ટાળીને 2 વર્ષનું પાક ચક્ર અપનાવો",
            "mr" to "टोमॅटो, मिरची, वांगी आणि बटाटा पिके टाळून २ वर्षांचे पीक फेरपालट करा",
            "pa" to "ਟਮਾਟਰ, ਮਿਰਚ, ਬੈਂਗਣ ਅਤੇ ਆਲੂ ਤੋਂ ਬਚ ਕੇ 2 ਸਾਲਾਂ ਦਾ ਫਸਲੀ ਚੱਕਰ ਅਪਣਾਓ",
            "bn" to "টমেটো, মরিচ, বেগুন ও আলু পরিহার করে ২ বছরের ফসল আবর্তন পদ্ধতি অনুসরণ করুন",
            "ta" to "தக்காளி, மிளகாய், கத்தரி மற்றும் உருளைக்கிழங்கு தவிர்த்து 2 ஆண்டு பயிர் சுழற்சி முறையை கடைபிடிக்கவும்",
            "te" to "టమోటా, మిరప, వంగ మరియు బంగాళాదుంప కాకుండా 2 సంవత్సరాల పంట మార్పిడి చేయండి",
            "kn" to "ಟೊಮೆಟೊ, ಮೆಣಸಿನಕಾಯಿ, ಬದನೆ ಮತ್ತು ಆಲೂಗಡ್ಡೆ ಬೆಳೆಗಳನ್ನು ಹೊರತುಪಡಿಸಿ 2 ವರ್ಷಗಳ ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ",
            "ml" to "തക്കാളി, മുളക്, വഴുതന, ഉരുളക്കിഴങ്ങ് എന്നിവ ഒഴിവാക്കി 2 വർഷത്തെ വിള പരിക്രമം നടത്തുക",
            "or" to "ଟମାଟୋ, ଲଙ୍କା, ବାଇଗଣ ଏବଂ ଆଳୁ ଫସଲ ବଦଳାଇ ୨ ବର୍ଷର ଫସଲ ଚକ୍ର ଆପଣାନ୍ତୁ",
            "as" to "টমেটো, জলকীয়া, বেঙেনা আৰু আলু পৰিহাৰ কৰি ২ বছৰীয়া শস্য আৱৰ্তন কৰক",
            "ur" to "ٹماٹر، مرچ، بینگن اور آلو سے بچتے ہوئے 2 سالہ فصلوں کے ہیر پھیر پر عمل کریں",
            "mai" to "टमाटर, मिर्च, भंटा आ आलू सं बचैत 2 बरखक फसल चक्र अपनाउ"
        )),

        // 7. Biological: Beneficial predator insects
        Pair("maintain beneficial predator insects", mapOf(
            "en" to "Biological: Maintain beneficial predator insects (ladybugs, predatory mites) by avoiding broad-spectrum insecticides",
            "hi" to "जैविक नियंत्रण: कीटनाशकों का कम उपयोग कर लाभकारी कीटों (लेडीबग्स आदि) को सुरक्षित रखें",
            "gu" to "જૈવિક નિયંત્રણ: બ્રોડ-સ્પેક્ટ્રમ જંતુનાશકો ટાળીને ઉપયોગી પરભક્ષી કીટકોનું રક્ષણ કરો",
            "mr" to "जैविक नियंत्रण: मित्र कीटकांचे (उदा. लेडीबग्स) रक्षण करण्यासाठी अति कीटकनाशके टाळा",
            "pa" to "ਜੈਵਿਕ ਰੋਕਥਾਮ: ਕੀਟਨਾਸ਼ਕਾਂ ਤੋਂ ਬਚ ਕੇ ਮਿੱਤਰ ਕੀੜਿਆਂ ਦੀ ਰੱਖਿਆ ਕਰੋ",
            "bn" to "জৈব নিয়ন্ত্রণ: উপকারী পোকা মাকড়ের সুরক্ষায় অতিরিক্ত কীটনাশক পরিহার করুন",
            "ta" to "இயற்கை கட்டுப்பாடு: நன்மை செய்யும் பூச்சிகளை பாதுகாக்க பூச்சிக்கொல்லிகளை குறைக்கவும்",
            "te" to "జీవ నియంత్రణ: ఉపయోగకరమైన కీటకాలను రక్షించడానికి రసాయన మందులను తగ్గించండి",
            "kn" to "ಜೈವಿಕ ನಿಯಂತ್ರಣ: ಉಪಯುಕ್ತ ಕೀಟಗಳನ್ನು ರಕ್ಷಿಸಲು ಕೀಟನಾಶಕಗಳನ್ನು ಮಿತವಾಗಿ ಬಳಸಿ",
            "ml" to "ജൈവ നിയന്ത്രണം: ഉപകാരികളായ പ്രാണികളെ സംരക്ഷിക്കാൻ കീടനാശിനികൾ ഒഴിവാക്കുക",
            "or" to "ଜୈବିକ ନିୟନ୍ତ୍ରଣ: ଉପକାରୀ କୀଟ ମାନଙ୍କୁ ସୁରକ୍ଷା ଦେବା ପାଇଁ ଅତ୍ୟଧିକ କୀଟନାଶକ ବ୍ୟବହାର ବନ୍ଦ କରନ୍ତୁ",
            "as" to "জৈৱিক নিয়ন্ত্ৰণ: উপকাৰী কীট-পতংগ ৰক্ষা কৰিবলৈ অতিৰিক্ত কীটনাশক পৰিহাৰ কৰক",
            "ur" to "حیاتیاتی کنٹرول: مفید کیڑوں کے تحفظ کے لیے غیر ضروری کیڑے مار ادویات سے پرہیز کریں",
            "mai" to "जैविक नियंत्रण: कीटनाशक के कम प्रयोग कऽ लाभकारी कीट सभ केँ सुरक्षित राखू"
        )),

        // 8. Cultural: Weed clearing around tree basins
        Pair("weed clearing around tree basins", mapOf(
            "en" to "Cultural: Weed clearing around tree basins and annual winter pruning",
            "hi" to "कृषि पद्धतियां: तनों के चारों ओर खरपतवार हटाएं और नियमित कटाई-छंटाई करें",
            "gu" to "કૃષિ પદ્ધતિ: થડની આસપાસથી નીંદણ દૂર કરો અને નિયમિત કાપણી કરો",
            "mr" to "मशागत पद्धती: झाडाभोवतीचे तण काढून टाका आणि नियमित छाटणी करा",
            "pa" to "ਖੇਤੀ ਤਰੀਕੇ: ਬੂਟਿਆਂ ਦੇ ਆਲੇ-ਦੁਆਲੇ ਤੋਂ ਨਦੀਨ ਸਾਫ਼ ਕਰੋ ਅਤੇ ਛਾਂਟੀ ਕਰੋ",
            "bn" to "কৃষি পদ্ধতি: গাছের গোড়ার আগাছা পরিষ্কার করুন এবং সঠিক ছাঁটাই করুন",
            "ta" to "பயிர் மேலாண்மை: மரங்களைச் சுற்றியுள்ள களைகளை அகற்றி கவாத்து செய்யவும்",
            "te" to "సాగు పద్ధతులు: చెట్ల చుట్టూ కలుపు తీసివేసి సక్రమంగా కత్తిరింపులు చేయండి",
            "kn" to "ಕೃಷಿ ಪದ್ಧತಿ: ಗಿಡಗಳ ಸುತ್ತ ಕಳೆ ತೆಗೆದು ಸಕಾಲಿಕ ಕತ್ತರಿಕೆ ಮಾಡಿ",
            "ml" to "കാർഷിക രീതികൾ: ചെടികൾക്ക് ചുറ്റുമുള്ള കളകൾ നീക്കം ചെയ്യുകയും വെട്ടിപ്പരുക്കുകയും ചെയ്യുക",
            "or" to "କୃଷି ପଦ୍ଧତି: ଗଛ ମୂଳରୁ ଘାସ ସଫା କରନ୍ତୁ ଏବଂ ନିୟମିତ ଡାଳ କାଟନ୍ତୁ",
            "as" to "কৃষি পদ্ধতি: গছৰ গুৰিৰ অপতৃণ পৰিষ্কাৰ কৰক আৰু নিয়মীয়া ডাল কাটি দিয়ক",
            "ur" to "زرعی طریقے: پودوں کے ارد گرد سے گھاس پھوس صاف کریں اور باقاعدہ کٹائی کریں",
            "mai" to "कृषि पद्धति: गाछक जड़ि लग सं घास-पात हटाउ आ कटाई-छंटाई करू"
        )),

        // 9. Balanced N-P-K
        Pair("balanced n-p-k", mapOf(
            "en" to "Continue balanced N-P-K and micronutrient (Boron, Zinc, Calcium) fertilization based on annual soil tests",
            "hi" to "मृदा परीक्षण के अनुसार संतुलित N-P-K और सूक्ष्म पोषक तत्व (बोरॉन, जिंक, कैल्शियम) दें",
            "gu" to "જમીન ચકાસણી મુજબ સંતુલિત N-P-K અને સૂક્ષ્મ પોષક તત્વો (બોરોન, ઝિંક, કેલ્શિયમ) આપો",
            "mr" to "माती परीक्षणानुसार संतुलित N-P-K आणि सूक्ष्म अन्नद्रव्ये (बोरॉन, झिंक, कॅल्शियम) द्या",
            "pa" to "ਮਿੱਟੀ ਪਰਖ ਅਨੁਸਾਰ ਸੰਤੁਲਿਤ N-P-K ਅਤੇ ਸੂਖਮ ਤੱਤ (ਬੋਰੋਨ, ਜ਼ਿੰਕ, ਕੈਲਸ਼ੀਅਮ) ਪਾਓ",
            "bn" to "মাটি পরীক্ষা অনুযায়ী সুষম N-P-K এবং অণুখাদ্য (বোরন, জিঙ্ক, ক্যালসিয়াম) প্রয়োগ করুন",
            "ta" to "மண் பரிசோதனைப்படி சமச்சீர் N-P-K மற்றும் நுண்ணூட்டச்சத்துக்களை (போரான், ஜிங்க், கால்சியம்) இடவும்",
            "te" to "నేల పరీక్షల ఆధారంగా సమతుల్య N-P-K మరియు సూక్ష్మ పోషకాలను అందించండి",
            "kn" to "ಮಣ್ಣು ಪರೀಕ್ಷೆಯ ಪ್ರಕಾರ ಸಮತೋಲಿತ N-P-K ಮತ್ತು ಲಘು ಪೋಷಕಾಂಶಗಳನ್ನು ಒದಗಿಸಿ",
            "ml" to "മണ്ണ് പരിശോധന പ്രകാരം സമീകൃത N-P-K വളങ്ങളും സൂക്ഷ്മ മൂലകങ്ങളും നൽകുക",
            "or" to "ମାଟି ପରୀକ୍ଷା ଅନୁସାରେ ସନ୍ତୁଳିତ N-P-K ଏବଂ ଅଣୁ ପୋଷକ ତତ୍ତ୍ୱ ପ୍ରୟୋଗ କରନ୍ତୁ",
            "as" to "মাটি পৰীক্ষাৰ ভিত্তিত সুষম N-P-K আৰু অণুপোষক দ্ৰব্য প্ৰয়ੋগ কৰক",
            "ur" to "مٹی کے ٹیسٹ کے مطابق متوازن N-P-K اور غذائی اجزاء استعمال کریں",
            "mai" to "माटिक जाँचक अनुसार संतुलित N-P-K आ सूक्ष्म पोषक तत्व दियौ"
        )),

        // 10. Pruning and drip irrigation
        Pair("pruning and drip irrigation", mapOf(
            "en" to "Maintain regular pruning and drip irrigation schedules",
            "hi" to "नियमित कटाई-छंटाई और ड्रिप सिंचाई का उचित कार्यक्रम बनाए रखें",
            "gu" to "નિયમિત કાપણી અને ટપક સિંચાઈનું યોગ્ય સમયપત્રક જાળવો",
            "mr" to "नियमित छाटणी आणि ठिबक सिंचनाचे योग्य नियोजन ठेवा",
            "pa" to "ਨਿਯਮਤ ਛਾਂਟੀ ਅਤੇ ਤੁਪਕਾ ਸਿੰਚਾਈ ਦਾ ਸਹੀ ਸਮਾਂ-ਸਾਰਣੀ ਰੱਖੋ",
            "bn" to "নিয়মিত ছাঁটাই এবং ড্রিপ সেচ ব্যবস্থা বজায় রাখুন",
            "ta" to "முறையான கவாத்து மற்றும் சொட்டு நீர் பாசன அட்டவணையை பராமரிக்கவும்",
            "te" to "క్రమం తప్పకుండా కత్తిరింపులు మరియు డ్రిప్ ఇరిగేషన్ విధానాన్ని కొనసాగించండి",
            "kn" to "ನಿಯಮಿತ ಕತ್ತರಿಕೆ ಮತ್ತು ಹನಿ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಅನುಸರಿಸಿ",
            "ml" to "കൃത്യമായ വെട്ടിപ്പരുക്കലും തുള്ളി നനയും ഉറപ്പാക്കുക",
            "or" to "ନିୟମିତ ଡାଳ କଟା ଏବଂ ବିନ୍ଦୁ ଜଳସେଚନ କାର୍ଯ୍ୟକ୍ରମ ବଜାୟ ରଖନ୍ତୁ",
            "as" to "নিয়মীয়া ডাল কটা আৰু টোপাল জলসিঞ্চন ব্যৱস্থা বৰ্তাই ৰাখক",
            "ur" to "باقاعدہ کٹائی اور ڈرپ اریگیشن کے شیڈول پر عمل کریں",
            "mai" to "नियमित कटाई आ ड्रिप सिंचाई केर समय-सारिणी बना कऽ राखू"
        )),

        // 11. Store: Recommended active ingredient
        Pair("recommended active ingredient", mapOf(
            "en" to "Recommended active ingredient for disease control",
            "hi" to "रोग नियंत्रण के लिए अनुशंसित सक्रिय घटक",
            "mr" to "रोग नियंत्रणासाठी शिफारस केलेले प्रभावी घटक",
            "gu" to "રોગ નિયંત્રણ માટે ભલામણ કરેલ સક્રિય ઘટક",
            "pa" to "ਬਿਮਾਰੀ ਕੰਟਰੋਲ ਲਈ ਸਿਫਾਰਸ਼ ਕੀਤਾ ਤੱਤ",
            "bn" to "রোগ নিয়ন্ত্রণের জন্য প্রস্তাবিত সক্রিয় উপাদান",
            "ta" to "நோய் கட்டுப்பாட்டுக்கு பரிந்துரைக்கப்பட்ட மருந்து",
            "te" to "తెగులు నివారణకు సిఫార్సు చేయబడిన మందు",
            "kn" to "ರೋಗ ನಿಯಂತ್ರಣಕ್ಕಾಗಿ ಶಿಫಾರಸು ಮಾಡಿದ ಘಟಕ",
            "ml" to "രോഗനിയന്ത്രണത്തിന് ശുപാർശ ചെയ്ത മരുന്ന്",
            "or" to "ରୋଗ ନିୟନ୍ତ୍ରଣ ପାଇଁ ସୁପାରିଶ କରାଯାଇଥିବା ଔଷଧ",
            "as" to "ৰোগ নিয়ন্ত্ৰণৰ বাবে অনুমোদন কৰা দ্ৰব্য",
            "ur" to "بیماری کے تدارک کے لیے تجویز کردہ جزو",
            "mai" to "रोग नियंत्रणक लेल अनुशंसित सक्रिय घटक"
        )),

        // 12. Store: Antibacterial agricultural formulation
        Pair("antibacterial agricultural", mapOf(
            "en" to "Antibacterial agricultural bactericide formulation",
            "hi" to "जीवाणुरोधी कृषि सूत्रीकरण (बैक्टीरीसाइड)",
            "mr" to "जिवाणूनाशक कृषी औषध",
            "gu" to "જીવાણુનાશક કૃષિ દવા",
            "pa" to "ਜੀਵਾਣੂਨਾਸ਼ਕ ਖੇਤੀਬਾੜੀ ਦਵਾਈ",
            "bn" to "ব্যাকটেরিয়ানাশক কৃষি ওষুধ",
            "ta" to "பாக்டீரியா எதிர்ப்பு வேளாண் மருந்து",
            "te" to "బ్యాక్టీరియా నివారిణి వ్యవసాయ మందు",
            "kn" to "ಬ್ಯಾಕ್ಟೀರಿಯಾ ನಿವಾರಕ ಕೃಷಿ ಔಷಧ",
            "ml" to "ബാക്ടീരിയ നാശിനി കാർഷിക മരുന്ന്",
            "or" to "ଜୀବାଣୁନାଶକ କୃଷି ଔଷଧ",
            "as" to "বেক্টেৰিয়ানাশক কৃষি ঔষধ",
            "ur" to "بیکٹیریل زرعی دوا",
            "mai" to "जीवाणुरोधी कृषि दवाई"
        )),

        // 13. Store: Systemic fungicide
        Pair("systemic fungicide", mapOf(
            "en" to "Effective systemic fungicide formulation",
            "hi" to "प्रभावी प्रणालीगत कवकनाशी (फंगीसाइड)",
            "mr" to "प्रभावी आंतरप्रवाही बुरशीनाशक",
            "gu" to "અસરકારક પ્રણાલીગત ફૂગનાશક",
            "pa" to "ਅਸਰਦਾਰ ਉੱਲੀਨਾਸ਼ਕ ਦਵਾਈ",
            "bn" to "কার্যকর ছত্রাকনাশক ওষুধ",
            "ta" to "செயல்திறன் மிக்க பூஞ்சைக் கொல்லி",
            "te" to "సమర్థవంతమైన శిలీంధ్ర సంహారిణి",
            "kn" to "ಪರಿಣಾಮಕಾರಿ ಶಿಲೀಂಧ್ರನಾಶಕ",
            "ml" to "ഫലപ്രദമായ കുമിൾനാശിനി",
            "or" to "ପ୍ରଭାବଶାଳୀ କବକନାଶକ",
            "as" to "কাৰ্যকৰী ভেঁকুৰনাশক",
            "ur" to "مؤثر پھپھوندی کش دوا",
            "mai" to "प्रभावी कवकनाशी दवाई"
        ))
    )

    // ==========================================
    // PUBLIC LOCALIZATION API
    // ==========================================

    fun localizeDiseaseAdvice(text: String?, langCode: String): String {
        if (text.isNullOrBlank()) return ""
        if (langCode == "en") return text

        val normalized = text.lowercase().trim()

        // 1. Dynamic sentence pattern: "Pathology pattern matching {disease} in {crop}."
        if (normalized.contains("pathology pattern matching") || normalized.contains("symptoms and management profile")) {
            val isHealthy = normalized.contains("healthy")
            val crop = when {
                normalized.contains("pepper bell") || normalized.contains("bell pepper") -> localizeCrop("pepper bell", langCode)
                normalized.contains("tomato") -> localizeCrop("tomato", langCode)
                normalized.contains("potato") -> localizeCrop("potato", langCode)
                normalized.contains("cotton") -> localizeCrop("cotton", langCode)
                normalized.contains("wheat") -> localizeCrop("wheat", langCode)
                normalized.contains("rice") || normalized.contains("paddy") -> localizeCrop("rice", langCode)
                normalized.contains("apple") -> localizeCrop("apple", langCode)
                normalized.contains("grape") -> localizeCrop("grape", langCode)
                normalized.contains("orange") -> localizeCrop("orange", langCode)
                normalized.contains("corn") || normalized.contains("maize") -> localizeCrop("maize", langCode)
                else -> when (langCode) {
                    "hi" -> "फसल"
                    "mr" -> "पीक"
                    "gu" -> "પાક"
                    "pa" -> "ਫਸਲ"
                    "bn" -> "ফসল"
                    "ta" -> "பயிர்"
                    "te" -> "పంట"
                    "kn" -> "ಬೆಳೆ"
                    "ml" -> "വിള"
                    "or" -> "ଫସଲ"
                    "as" -> "শস্য"
                    "ur" -> "فصل"
                    "mai" -> "फसल"
                    else -> "फसल"
                }
            }

            return when (langCode) {
                "hi" -> if (isHealthy) "$crop में स्वस्थ पौधे की पुष्टि हुई है।" else "$crop में रोग के लक्षण पाए गए हैं।"
                "gu" -> if (isHealthy) "$crop માં સ્વસ્થ છોડની પુષ્ટિ થઈ છે." else "$crop માં રોગના લક્ષણો મળ્યા છે."
                "mr" -> if (isHealthy) "$crop मध्ये निरोगी रोपाची खात्री झाली आहे." else "$crop मध्ये रोगाचे लक्षणे आढळली आहेत."
                "pa" -> if (isHealthy) "$crop ਵਿੱਚ ਸਿਹਤਮੰਦ ਬੂਟੇ ਦੀ ਪੁਸ਼ਟੀ ਹੋਈ ਹੈ।" else "$crop ਵਿੱਚ ਬਿਮਾਰੀ ਦੇ ਲੱਛਣ ਮਿਲੇ ਹਨ।"
                "bn" -> if (isHealthy) "$crop এ সুস্থ উদ্ভিদের লক্ষণ পাওয়া গেছে।" else "$crop এ রোগের লক্ষণ পাওয়া গেছে।"
                "ta" -> if (isHealthy) "$crop பயிரில் ஆரோக்கியமான தாவரம் உறுதி செய்யப்பட்டது." else "$crop பயிரில் நோய் அறிகுறிகள் காணப்படுகின்றன."
                "te" -> if (isHealthy) "$crop లో ఆరోగ్యకరమైన మొక్కగా నిర్ధారించబడింది." else "$crop లో వ్యాధి లక్షణాలు గుర్తించబడ్డాయి."
                "kn" -> if (isHealthy) "$crop ನಲ್ಲಿ ಆರೋಗ್ಯಕರ ಸಸ್ಯ ದೃಢಪಟ್ಟಿದೆ." else "$crop ನಲ್ಲಿ ರೋಗದ ಲಕ್ಷಣಗಳು ಕಂಡುಬಂದಿವೆ."
                "ml" -> if (isHealthy) "$crop ൽ ആരോഗ്യമുള്ള ചെടിയാണെന്ന് സ്ഥിരീകരിച്ചു." else "$crop ൽ രോഗലക്ഷണങ്ങൾ കണ്ടെത്തി."
                "or" -> if (isHealthy) "$crop ରେ ସୁସ୍ଥ ଗଛ ଚିହ୍ନଟ ହୋଇଛି।" else "$crop ରେ ରୋଗର ଲକ୍ଷଣ ଦେଖାଯାଇଛି।"
                "as" -> if (isHealthy) "$crop ত সুস্থ উদ্ভিদ নিশ্চিত কৰা হৈছে।" else "$crop ত ৰোগৰ লক্ষণ দেখা গৈছে।"
                "ur" -> if (isHealthy) "$crop میں صحت مند پودے کی تصدیق ہوئی ہے۔" else "$crop میں بیماری کی علامات پائی گئی ہیں۔"
                "mai" -> if (isHealthy) "$crop मे स्वस्थ गाछक पुष्टि भेल अछि।" else "$crop मे रोगक लक्षण भेटल अछि।"
                else -> if (isHealthy) "$crop में स्वस्थ पौधे की पुष्टि हुई है।" else "$crop में रोग के लक्षण पाए गए हैं।"
            }
        }

        // 2. Direct lookup in predefined ICAR advice bullet patterns
        for ((trigger, translations) in ADVICE_PATTERNS) {
            if (normalized.contains(trigger)) {
                return translations[langCode] ?: translations["hi"] ?: text
            }
        }

        // 3. Prefix clause translation for Biological / Chemical / Cultural recommendations
        if (text.startsWith("Biological:", ignoreCase = true) || text.startsWith("Chemical:", ignoreCase = true) || text.startsWith("Cultural:", ignoreCase = true)) {
            val parts = text.split(":", limit = 2)
            val prefix = parts[0].trim().lowercase()
            val body = parts.getOrNull(1)?.trim() ?: ""

            val localizedPrefix = when (prefix) {
                "biological" -> when (langCode) {
                    "hi" -> "जैविक नियंत्रण"
                    "mr" -> "जैविक उपाय"
                    "gu" -> "જૈવિક નિયંત્રણ"
                    "pa" -> "ਜੈਵਿਕ ਰੋਕਥਾਮ"
                    "bn" -> "জৈব নিয়ন্ত্রণ"
                    "ta" -> "இயற்கை கட்டுப்பாடு"
                    "te" -> "జీవ నియంత్రణ"
                    "kn" -> "ಜೈವಿಕ ನಿಯಂತ್ರಣ"
                    "ml" -> "ജൈവ നിയന്ത്രണം"
                    "or" -> "ଜୈବିକ ନିୟନ୍ତ୍ରଣ"
                    "as" -> "জৈৱিক নিয়ন্ত্ৰণ"
                    "ur" -> "حیاتیاتی کنٹرول"
                    "mai" -> "जैविक नियंत्रण"
                    else -> "जैविक नियंत्रण"
                }
                "chemical" -> when (langCode) {
                    "hi" -> "रासायनिक उपाय"
                    "mr" -> "रासायनिक उपाय"
                    "gu" -> "રાસાયણિક ઉપાય"
                    "pa" -> "ਰਸਾਇਣਕ ਰੋਕਥਾਮ"
                    "bn" -> "রাসায়নিক নিয়ন্ত্রণ"
                    "ta" -> "வேதியியல் கட்டுப்பாடு"
                    "te" -> "రసాయన నియంత్రణ"
                    "kn" -> "ರಾಸಾಯನಿಕ ನಿಯಂತ್ರಣ"
                    "ml" -> "രാസ നിയന്ത്രണം"
                    "or" -> "ରାସାୟନିକ ନିୟନ୍ତ୍ରଣ"
                    "as" -> "ৰাসায়নিক নিয়ন্ত্ৰণ"
                    "ur" -> "کیمیائی کنٹرول"
                    "mai" -> "रासायनिक नियंत्रण"
                    else -> "रासायनिक उपाय"
                }
                "cultural" -> when (langCode) {
                    "hi" -> "कृषि पद्धतियां"
                    "mr" -> "मशागत पद्धती"
                    "gu" -> "કૃષિ પદ્ધતિ"
                    "pa" -> "ਖੇਤੀ ਤਰੀਕੇ"
                    "bn" -> "কৃষি পদ্ধতি"
                    "ta" -> "பயிர் மேலாண்மை"
                    "te" -> "సాగు పద్ధతులు"
                    "kn" -> "ಕೃಷಿ ಪದ್ಧತಿ"
                    "ml" -> "കാർഷിക രീതികൾ"
                    "or" -> "କୃଷି ପଦ୍ଧତି"
                    "as" -> "কৃষি পদ্ধতি"
                    "ur" -> "زرعی طریقے"
                    "mai" -> "कृषि पद्धति"
                    else -> "कृषि पद्धतियां"
                }
                else -> prefix
            }

            // Check if body matches any known triggers
            val localizedBody = localizeDiseaseAdvice(body, langCode)
            return if (localizedBody != body) {
                localizedBody
            } else {
                "$localizedPrefix: $body"
            }
        }

        return text
    }

    fun localizeCity(rawCity: String?, langCode: String): String {
        if (rawCity.isNullOrBlank()) return if (langCode == "en") "Bengaluru" else localizeCity("Bengaluru", langCode)
        val normalized = rawCity.trim().lowercase()
        val match = CITY_TRANSLATIONS[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: rawCity
        }
        for ((key, translations) in CITY_TRANSLATIONS) {
            if (normalized.contains(key)) {
                return translations[langCode] ?: translations["hi"] ?: key
            }
        }
        return rawCity
    }

    fun localizeWeatherCondition(condition: String?, langCode: String): String {
        if (condition.isNullOrBlank()) return ""
        val normalized = condition.trim().lowercase()
        val match = WEATHER_CONDITIONS[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: condition
        }
        for ((key, translations) in WEATHER_CONDITIONS) {
            if (normalized.contains(key)) {
                return translations[langCode] ?: translations["hi"] ?: condition
            }
        }
        return condition
    }

    fun localizeCrop(crop: String?, langCode: String): String {
        if (crop.isNullOrBlank()) return ""
        val normalized = crop.trim().lowercase().replace("_", " ")
        val match = CROPS[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: crop
        }
        for ((key, translations) in CROPS) {
            if (normalized.contains(key)) {
                return translations[langCode] ?: translations["hi"] ?: crop
            }
        }
        return crop
    }

    fun localizeDisease(disease: String?, langCode: String): String {
        if (disease.isNullOrBlank()) return ""
        val normalized = disease.trim().lowercase().replace("_", " ").replace("-", " ")
        
        // Exact match
        val match = DISEASES[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: disease
        }

        // Substring / token matching
        for ((key, translations) in DISEASES) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: disease
            }
        }
        return disease
    }

    fun localizeAnimal(animal: String?, langCode: String): String {
        if (animal.isNullOrBlank()) return ""
        val normalized = animal.trim().lowercase()
        val match = ANIMALS[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: animal
        }
        for ((key, translations) in ANIMALS) {
            if (normalized.contains(key)) {
                return translations[langCode] ?: translations["hi"] ?: animal
            }
        }
        return animal
    }

    fun localizeSeverity(severity: String?, langCode: String): String {
        if (severity.isNullOrBlank()) return ""
        val normalized = severity.trim().lowercase()
        val match = SEVERITIES[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: severity.uppercase()
        }
        for ((key, translations) in SEVERITIES) {
            if (normalized.startsWith(key) || normalized.contains(key)) {
                val trans = translations[langCode] ?: translations["hi"] ?: key.uppercase()
                val extra = severity.substring(key.length).trim()
                return if (extra.isNotEmpty() && extra.startsWith("(")) "$trans $extra" else trans
            }
        }
        return severity.uppercase()
    }

    fun localizeTime(term: String?, langCode: String): String {
        if (term.isNullOrBlank()) return ""
        val normalized = term.trim().lowercase()
        val match = TIME_TERMS[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: term
        }
        return term
    }

    // ==========================================
    // SOIL TYPES (14 LANGUAGES)
    // ==========================================
    private val SOIL_TYPES = mapOf(
        "black soil" to mapOf("en" to "Black Soil", "hi" to "काली मिट्टी", "gu" to "કાળી જમીન", "mr" to "काळी माती", "pa" to "ਕਾਲੀ ਮਿੱਟੀ", "bn" to "কালো মাটি", "ta" to "கரிசல் மண்", "te" to "నల్ల రేగడి నేల", "kn" to "ಕಪ್ಪು ಮಣ್ಣು", "ml" to "കരിമണ്ണ്", "or" to "କଳା ମାଟି", "as" to "কলা মাটি", "ur" to "کالی مٹی", "mai" to "करिया माटी"),
        "red soil" to mapOf("en" to "Red Soil", "hi" to "लाल मिट्टी", "gu" to "લાલ જમીન", "mr" to "तांबडी माती", "pa" to "ਲਾਲ ਮਿੱਟੀ", "bn" to "লাল মাটি", "ta" to "செம்மண்", "te" to "ఎర్ర నేల", "kn" to "ಕೆಂಪು ಮಣ್ಣು", "ml" to "ചെമ്മണ്ണ്", "or" to "ଲାଲ୍ ମାଟି", "as" to "ৰঙা মাটি", "ur" to "سرخ مٹی", "mai" to "लाल माटी"),
        "alluvial soil" to mapOf("en" to "Alluvial Soil", "hi" to "दोमट / जलोढ़ मिट्टी", "gu" to "કાંપવાળી જમીન", "mr" to "गाळाची / दोमट माती", "pa" to "ਜਲੋਢ ਮਿੱਟੀ", "bn" to "পলিমাটি", "ta" to "வண்டல் மண்", "te" to "ఒండ్రు నేల", "kn" to "ಮೆಕ್ಕಲು ಮಣ್ಣು", "ml" to "ಎക്കൽ മണ്ണ്", "or" to "ପଟୁ ମାଟି", "as" to "পলসুৱা মাটি", "ur" to "زرخیز مٹی", "mai" to "जलोढ़ माटी"),
        "sandy soil" to mapOf("en" to "Sandy Soil", "hi" to "रेतीली मिट्टी", "gu" to "રેતાળ જમીન", "mr" to "वाळूयुक्त माती", "pa" to "ਰੇਤਲੀ ਮਿੱਟੀ", "bn" to "বেলে মাটি", "ta" to "மணல் மண்", "te" to "ఇసుక నేల", "kn" to "ಮರಳು ಮಣ್ಣು", "ml" to "മണൽ മണ്ണ്", "or" to "ବାଲିଆ ମାଟି", "as" to "বালিয়া মাটি", "ur" to "ریتلی مٹی", "mai" to "बलुआही माटी"),
        "clay loam" to mapOf("en" to "Clay Loam", "hi" to "चिकनी दोमट मिट्टी", "gu" to "ચીકણી કાંપવાળી જમીન", "mr" to "चिकण दोमट माती", "pa" to "ਚੀਕਣੀ ਜਲੋਢ ਮਿੱਟੀ", "bn" to "এঁটেল দোআঁশ মাটি", "ta" to "களிமண் வண்டல்", "te" to "బంకమట్టి ఒండ్రు", "kn" to "ಜೇಡಿ ಮೆಕ್ಕಲು ಮಣ್ಣು", "ml" to "കളിമൺ എക്കൽ", "or" to "ମଟାଳ ପଟୁ ମାଟି", "as" to "বোকা পলসুৱা মাটি", "ur" to "چکنی زرخیز مٹی", "mai" to "चिकनी दोमट माटी")
    )

    // ==========================================
    // SOIL DESCRIPTIONS (14 LANGUAGES)
    // ==========================================
    private val SOIL_DESCRIPTIONS = mapOf(
        "rich in clay" to mapOf(
            "en" to "Rich in clay,\nretains water well",
            "hi" to "चिकनी मिट्टी से भरपूर,\nजल संचयन क्षमता उत्तम",
            "gu" to "ચીકણી માટીથી ભરપૂર,\nપાણી સંગ્રહ ક્ષમતા સારી",
            "mr" to "चिकणमातीचे प्रमाण जास्त,\nपाणी टिकवून ठेवते",
            "pa" to "ਚੀਕਣੀ ਮਿੱਟੀ ਨਾਲ ਭਰਪੂਰ,\nਪਾਣੀ ਚੰਗੀ ਤਰ੍ਹਾਂ ਸੰਭਾਲਦੀ ਹੈ",
            "bn" to "কাদাযুক্ত মাটি,\nজল ধারণ ক্ষমতা চমৎকার",
            "ta" to "களிமண் நிறைந்தது,\nநீரை நன்கு தேக்கி வைக்கும்",
            "te" to "బంకమట్టి సమృద్ధిగా ఉంటుంది,\nనీటిని బాగా పట్టి ఉంచుతుంది",
            "kn" to "ಜೇಡಿಮಣ್ಣಿನಿಂದ ಸಮೃದ್ಧ,\nನೀರನ್ನು ಚೆನ್ನಾಗಿ ಹಿಡಿದಿಟ್ಟುಕೊಳ್ಳುತ್ತದೆ",
            "ml" to "കളിമണ്ണ് സമൃദ്ധം,\nവെള്ളം നന്നായി നിലനിർത്തുന്നു",
            "or" to "ଚିକିଟା ମାଟି,\nଜଳ ଧାରଣ କ୍ଷମତା ଭଲ",
            "as" to "বোকা মাটিৰ পৰিমাণ বেছি,\nপানী ধৰি ৰাখিব পাৰে",
            "ur" to "چکنی مٹی سے بھرپور،\nپانی کو اچھی طرح روکتی ہے",
            "mai" to "चिकनी माटी सं भरपूर,\nपानि सोखबाक क्षमता नीक"
        ),
        "good for cotton" to mapOf(
            "en" to "Good for cotton\nand pulses",
            "hi" to "कपास और दलहन\nके लिए उत्तम",
            "gu" to "કપાસ અને કઠોળ\nમાટે ઉત્તમ",
            "mr" to "कापूस आणि कडधान्यांसाठी\nअत्यंत उत्तम",
            "pa" to "ਕਪਾਹ ਅਤੇ ਦਾਲਾਂ\nਲਈ ਵਧੀਆ",
            "bn" to "তুলা এবং ডাল\nচাষের জন্য উপযুক্ত",
            "ta" to "பருத்தி மற்றும்\nபருப்பு வகைகளுக்கு ஏற்றது",
            "te" to "ప్రత్తి మరియు\nపప్పుధాన్యాలకు అనుకూలం",
            "kn" to "ಹತ್ತಿ ಮತ್ತು\nಬೇಳೆಕಾಳುಗಳಿಗೆ ಉತ್ತಮ",
            "ml" to "പരുത്തിക്കും പയറുവർഗ്ഗങ്ങൾക്കും\nഏറ്റവും അനുയോജ്യം",
            "or" to "କପା ଏବଂ ଡାଲି\nଜାତୀୟ ଫସଲ ପାଇଁ ଉପଯୁକ୍ତ",
            "as" to "কপাহ আৰু দাইল\nজাতীয় শস্যৰ বাবে উপযোগী",
            "ur" to "کپاس اور دالوں\nکے لیے بہترین",
            "mai" to "कपास आ दलहन\nकेर लेल नीक"
        ),
        "very fertile" to mapOf(
            "en" to "Very fertile, best for\nwheat and rice",
            "hi" to "अत्यधिक उपजाऊ, गेहूं\nऔर धान के लिए सर्वोत्तम",
            "gu" to "ખૂબ ફળદ્રુપ, ઘઉં\nઅને ડાંગર માટે શ્રેષ્ઠ",
            "mr" to "अत्यंत सुपीक, गहू\nआणि भातासाठी सर्वोत्तम",
            "pa" to "ਬਹੁਤ ਉਪਜਾਊ, ਕਣਕ\nਅਤੇ ਝੋਨੇ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ",
            "bn" to "অত্যন্ত উর্বর, গম\nও ধানের জন্য সবচেয়ে ভালো",
            "ta" to "மிகவும் வளமானது,\nகோதுமை மற்றும் நெல்லுக்கு சிறந்தது",
            "te" to "చాలా సారవంతమైనది,\nగోధుమ మరియు వరికి ఉత్తమం",
            "kn" to "ಬಹಳ ಫಲವತ್ತಾದದ್ದು,\nಗೋಧಿ ಮತ್ತು ಭತ್ತಕ್ಕೆ ಅತ್ಯುತ್ತಮ",
            "ml" to "വളരെ ഫലഭൂയിഷ്ഠം,\nഗോതമ്പിനും നെല്ലിനും അനുയോജ്യം",
            "or" to "ଅତ୍ୟନ୍ତ ଉର୍ବର, ଗହମ\nଏବଂ ଧାନ ପାଇଁ ସର୍ବୋତ୍ତମ",
            "as" to "অতি সাৰুৱা, গম\nআৰু ধানৰ বাবে অতি উত্তম",
            "ur" to "انتہائی زرخیز، گندم\nاور چاول کے لیے موزوں",
            "mai" to "अति उपजाऊ, गेहूँ\nआ धान केर लेल सर्वोत्तम"
        ),
        "drains quickly" to mapOf(
            "en" to "Drains quickly,\nneeds more water",
            "hi" to "पानी जल्दी रिसता है,\nअधिक सिंचाई चाहिए",
            "gu" to "પાણી ઝડપથી નીતરે છે,\nવધુ પાણીની જરૂર",
            "mr" to "पाण्याचा निचरा जलद होतो,\nवारंवार पाणी लागते",
            "pa" to "ਪਾਣੀ ਜਲਦੀ ਨਿਕਲਦਾ ਹੈ,\nਵਧੇਰੇ ਪਾਣੀ ਦੀ ਲੋੜ",
            "bn" to "দ্রুত জল নিষ্কাশিত হয়,\nবেশি জল প্রয়োজন",
            "ta" to "நீர் வேகமாக வடியும்,\nஅதிக நீர் தேவைப்படும்",
            "te" to "నీరు త్వరగా ఇంకిపోతుంది,\nఎక్కువ నీరు అవసరం",
            "kn" to "ನೀರು ಬೇಗನೆ ಹರಿಯುತ್ತದೆ,\nಹೆಚ್ಚು ನೀರು ಬೇಕು",
            "ml" to "വെള്ളം വേഗത്തിൽ പോകുന്നു,\nകൂടുതൽ വെള്ളം വേണം",
            "or" to "ପାଣି ଶୀଘ୍ର ନିଷ୍କାସିତ ହୁଏ,\nଅଧିକ ପାଣି ଆବଶ୍ୟକ",
            "as" to "পানী সোনকালে ওলাই যায়,\nঅধিক পানীৰ প্ৰয়োজন",
            "ur" to "پانی جلد نکل جاتا ہے،\nزیادہ پانی درکار ہے",
            "mai" to "पानि जल्दी सूखैत अछि,\nबेसी सिंचाइक जरूरत"
        )
    )

    // ==========================================
    // CROP ADVICE UI PHRASES (14 LANGUAGES)
    // ==========================================
    private val CROP_ADVICE_PHRASES = mapOf(
        "crop advice" to mapOf(
            "en" to "Crop Advice",
            "hi" to "फसल सलाह",
            "gu" to "પાક સલાહ",
            "mr" to "पीक सल्ला",
            "pa" to "ਫਸਲ ਸਲਾਹ",
            "bn" to "ফসলের পরামর্শ",
            "ta" to "பயிர் ஆலோசனை",
            "te" to "పంట సలహా",
            "kn" to "ಬೆಳೆ ಸಲಹೆ",
            "ml" to "വിള നിർദ്ദേശം",
            "or" to "ଫସଲ ପରାମର୍ଶ",
            "as" to "শস্যৰ পৰামৰ্শ",
            "ur" to "زرعی مشورہ",
            "mai" to "फसल सलाह"
        ),
        "soil selected" to mapOf(
            "en" to "Soil Type Selected:",
            "hi" to "चयनित मिट्टी का प्रकार:",
            "gu" to "પસંદ કરેલ જમીનનો પ્રકાર:",
            "mr" to "निवडलेला मातीचा प्रकार:",
            "pa" to "ਚੁਣੀ ਗਈ ਮਿੱਟੀ ਦੀ ਕਿਸਮ:",
            "bn" to "নির্বাচিত মাটির ধরন:",
            "ta" to "தேர்ந்தெடுக்கப்பட்ட மண் வகை:",
            "te" to "ఎంచుకున్న నేల రకం:",
            "kn" to "ಆಯ್ಕೆಮಾಡಿದ ಮಣ್ಣಿನ ವಿಧ:",
            "ml" to "തിരഞ്ഞെടുത്ത മണ്ണ്:",
            "or" to "ମନୋନୀତ ମାଟିର ପ୍ରକାର:",
            "as" to "নিৰ্বাচিত মাটিৰ প্ৰকাৰ:",
            "ur" to "منتخب کردہ مٹی کی قسم:",
            "mai" to "चुनल माटी केर प्रकार:"
        ),
        "refresh autofill" to mapOf(
            "en" to "Auto-fill from GPS & Live Weather",
            "hi" to "जीपीएस और मौसम से स्वतः भरें",
            "gu" to "જીપીએસ અને હવામાનથી આપમેળે ભરો",
            "mr" to "जीपीएस आणि हवामानातून आपोआप भरा",
            "pa" to "ਜੀਪੀਐਸ ਅਤੇ ਮੌਸਮ ਤੋਂ ਆਪਣੇ-ਆਪ ਭਰੋ",
            "bn" to "জিপিএস ও আবহাওয়া থেকে স্বয়ংক্রিয় পূরণ",
            "ta" to "ஜிபிஎஸ் & நேரடி வானிலையிலிருந்து தானாக நிரப்பவும்",
            "te" to "జీపీఎస్ & ప్రత్యక్ష వాతావరణం నుండి స్వయం పూరణ",
            "kn" to "ಜಿಪಿಎಸ್ ಮತ್ತು ಲೈವ್ ಹವಾಮಾನದಿಂದ ಸ್ವಯಂ ಭರ್ತಿ",
            "ml" to "ജിപിഎസ്, കാലാവസ്ഥ എന്നിവയിൽ നിന്ന് സ്വയമേവ പൂരിപ്പിക്കുക",
            "or" to "ଜିପିଏସ୍ ଏବଂ ପାଣିପାଗରୁ ସ୍ୱୟଂଚାଳିତ ଭାବେ ପୂରଣ କରନ୍ତୁ",
            "as" to "জিপিএছ আৰু বতৰৰ পৰা স্বয়ংক্ৰিয়ভাৱে পূৰণ কৰক",
            "ur" to "جی پی ایس اور لائیو موسم سے خودکار پُر کریں",
            "mai" to "जीपीएस आ मौसम सं स्वतः भरू"
        ),
        "what is your soil type" to mapOf(
            "en" to "What is your\nSoil Type?",
            "hi" to "आपकी मिट्टी का\nप्रकार क्या है?",
            "gu" to "તમારી જમીનનો\nપ્રકાર કયો છે?",
            "mr" to "तुमच्या मातीचा\nप्रकार कोणता आहे?",
            "pa" to "ਤੁਹਾਡੀ ਮਿੱਟੀ ਦੀ\nਕਿਸਮ ਕੀ ਹੈ?",
            "bn" to "আপনার মাটির\nধরন কি?",
            "ta" to "உங்கள் நிலத்தின்\nமண் வகை என்ன?",
            "te" to "మీ నేల రకం\nఏమిటి?",
            "kn" to "ನಿಮ್ಮ ಮಣ್ಣಿನ\nವಿಧ ಯಾವುದು?",
            "ml" to "നിങ്ങളുടെ മണ്ണിന്റെ\nതരം ഏതാണ്?",
            "or" to "ଆପଣଙ୍କ ମାଟିର\nପ୍ରକାର କ’ଣ?",
            "as" to "আপোনাৰ মাটিৰ\nপ্ৰকাৰ কি?",
            "ur" to "آپ کی مٹی کی\nقسم کیا ہے؟",
            "mai" to "अहाँक माटी केर\nप्रकार कोन अछि?"
        ),
        "this helps us suggest" to mapOf(
            "en" to "This helps us suggest\nthe best crops for\nyour field.",
            "hi" to "इससे हमें आपके खेत के लिए\nसर्वश्रेष्ठ फसलें सुझाने में\nमदद मिलती है।",
            "gu" to "આનાથી આપના ખેતર માટે\nશ્રેષ્ઠ પાક સૂચવવામાં\nમદદ મળે છે.",
            "mr" to "यामुळे आम्हाला तुमच्या शेतासाठी\nसर्वोत्तम पिकांचा सल्ला देणे\nशक्य होते.",
            "pa" to "ਇਸ ਨਾਲ ਤੁਹਾਡੇ ਖੇਤ ਲਈ\nਸਭ ਤੋਂ ਵਧੀਆ ਫਸਲਾਂ ਸੁਝਾਉਣ 'ਚ\nਮਦਦ ਮਿਲਦੀ ਹੈ।",
            "bn" to "এটি আপনার জমির জন্য\nসেরা ফসল সুপারিশ করতে\nসাহায্য করে।",
            "ta" to "இது உங்கள் வயலுக்கு\nசிறந்த பயிர்களைப் பரிந்துரைக்க\nஉதவுகிறது.",
            "te" to "ఇది మీ పొలానికి\nఉత్తమ పంటలను సూచించడానికి\nసహాయపడుతుంది.",
            "kn" to "ಇದು ನಿಮ್ಮ ಹೊಲಕ್ಕೆ\nಉತ್ತಮ ಬೆಳೆಗಳನ್ನು ಸೂಚಿಸಲು\nಸಹಾಯ ಮಾಡುತ್ತದೆ.",
            "ml" to "ഇത് നിങ്ങളുടെ പാടത്തിന്\nഏറ്റവും മികച്ച വിളകൾ നിർദ്ദേശിക്കാൻ\nസഹായിക്കുന്നു.",
            "or" to "ଏହା ଆପଣଙ୍କ ଜମି ପାଇଁ\nସର୍ବୋତ୍ତମ ଫସଲ ସୁପାରିଶ କରିବାରେ\nସାହାଯ୍ୟ କରେ।",
            "as" to "ইয়ে আপোনাৰ পথাৰৰ বাবে\nশ্ৰেষ্ঠ শস্য বাছনি কৰাত\nসহায় কৰে।",
            "ur" to "اس سے آپ کے کھیت کے لیے\nبہترین فصلیں تجویز کرنے میں\nمدد ملتی ہے۔",
            "mai" to "एहि सं अहाँक खेत लेल\nसर्वोत्तम फसल सुझाबय मे\nमदद भेटैत अछि।"
        ),
        "select soil match" to mapOf(
            "en" to "Select the soil type that best matches your field.",
            "hi" to "अपने खेत से सबसे मेल खाती मिट्टी का चयन करें।",
            "gu" to "તમારા ખેતર સાથે સૌથી વધુ મેળ ખાતી જમીન પસંદ કરો.",
            "mr" to "तुमच्या शेताशी जुळणारा मातीचा प्रकार निवडा.",
            "pa" to "ਆਪਣੇ ਖੇਤ ਨਾਲ ਮੇਲ ਖਾਂਦੀ ਮਿੱਟੀ ਦੀ ਕਿਸਮ ਚੁਣੋ।",
            "bn" to "আপনার জমির সাথে সবচেয়ে মানানসই মাটি নির্বাচন করুন।",
            "ta" to "உங்கள் வயலுக்குப் பொருந்தும் மண் வகையைத் தேர்ந்தெடுக்கவும்.",
            "te" to "మీ పొలానికి సరిపోయే నేల రకాన్ని ఎంచుకోండి.",
            "kn" to "ನಿಮ್ಮ ಹೊಲಕ್ಕೆ ಹೊಂದುವ ಮಣ್ಣಿನ ವಿಧವನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
            "ml" to "നിങ്ങളുടെ പാടത്തിന് അനുയോജ്യമായ മണ്ണ് തിരഞ്ഞെടുക്കുക.",
            "or" to "ଆପଣଙ୍କ ଜମି ସହିତ ମେଳ ଖାଉଥିବା ମାଟି ପ୍ରକାର ବାଛନ୍ତୁ।",
            "as" to "আপোনাৰ পথাৰৰ সৈতে মিল থকা মাটিৰ প্ৰকাৰ বাছক।",
            "ur" to "اپنے کھیت سے مطابقت رکھنے والی مٹی کا انتخاب کریں۔",
            "mai" to "खेत सं मेल खाय बला माटी केर प्रकार चुनू।"
        ),
        "soil report subtitle" to mapOf(
            "en" to "A Soil Health Card helps us understand your\nsoil better and give you accurate crop advice.",
            "hi" to "मृदा स्वास्थ्य कार्ड (Soil Health Card) से हमें आपकी\nमिट्टी को बेहतर समझने और सटीक सलाह देने में मदद मिलती है।",
            "gu" to "સોઇલ હેલ્થ કાર્ડથી તમારી જમીન વધુ સારી રીતે સમજીને\nસચોટ પાક સલાહ આપવામાં મદદ મળે છે.",
            "mr" to "सॉईल हेल्थ कार्डमुळे तुमच्या मातीची अचूक माहिती मिळून\nयोग्य पीक सल्ला देणे शक्य होते.",
            "pa" to "ਮਿੱਟੀ ਪਰਖ ਕਾਰਡ ਨਾਲ ਤੁਹਾਡੀ ਜ਼ਮੀਨ ਨੂੰ ਚੰਗੀ ਤਰ੍ਹਾਂ ਸਮਝ ਕੇ\nਸਹੀ ਫਸਲ ਸਲਾਹ ਦਿੱਤੀ ਜਾਂਦੀ ਹੈ।",
            "bn" to "মৃত্তিকা স্বাস্থ্য কার্ড আপনার মাটি আরও ভালোভাবে বুঝতে\nএবং সঠিক ফসলের পরামর্শ দিতে সাহায্য করে।",
            "ta" to "மண் வள அட்டை உங்கள் நிலத்தை நன்கு புரிந்துகொண்டு\nதுல்லியமான பயிர் ஆலோசனை வழங்க உதவுகிறது.",
            "te" to "సాయిల్ హెల్త్ కార్డ్ మీ నేలను బాగా అర్థం చేసుకోవడానికి\nమరియు ఖచ్చితమైన పంట సలహా ఇవ్వడానికి సహాయపడుతుంది.",
            "kn" to "ಮಣ್ಣು ಆರೋಗ್ಯ ಕಾರ್ಡ್ ನಿಮ್ಮ ಮಣ್ಣನ್ನು ಚೆನ್ನಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು\nಮತ್ತು ನಿಖರ ಬೆಳೆ ಸಲಹೆ ನೀಡಲು ಸಹಕಾರಿಯಾಗಿದೆ.",
            "ml" to "സോയിൽ ഹെൽത്ത് കാർഡ് നിങ്ങളുടെ മണ്ണിനെ നന്നായി മനസ്സിലാക്കാനും\nകൃത്യമായ വിള നിർദ്ദേശം നൽകാനും സഹായിക്കുന്നു.",
            "or" to "ମୃତ୍ତିକା ସ୍ୱାସ୍ଥ୍ୟ କାର୍ଡ ଆପଣଙ୍କ ମାଟିକୁ ଭଲ ଭାବରେ ବୁଝି\nସଠିକ୍ ଫସଲ ପରାମର୍ଶ ଦେବାରେ ସାହାଯ୍ୟ କରେ।",
            "as" to "মৃত্তিকা স্বাস্থ্য কাৰ্ডে আপোনাৰ মাটি ভালদৰে বুজিবলৈ\nআৰু সঠিক শস্যৰ পৰামৰ্শ দিয়াত সহায় কৰে।",
            "ur" to "سوائل ہیلتھ کارڈ آپ کی مٹی کو بہتر سمجھنے اور\nدرست زرعی مشورہ دینے میں مدد کرتا ہے۔",
            "mai" to "मृदा स्वास्थ्य कार्ड सं माटी केर नीक समझ आ\nसटीक फसल सलाह देबय मे मदद भेटैत अछि।"
        ),
        "ai analyzing" to mapOf(
            "en" to "AI is analyzing your soil & weather...",
            "hi" to "AI आपकी मिट्टी और मौसम का विश्लेषण कर रहा है...",
            "gu" to "AI તમારી જમીન અને હવામાનનું વિશ્લેષણ કરી રહ્યું છે...",
            "mr" to "AI तुमच्या माती आणि हवामानाचे विश्लेषण करत आहे...",
            "pa" to "AI ਤੁਹਾਡੀ ਮਿੱਟੀ ਅਤੇ ਮੌਸਮ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰ ਰਿਹਾ ਹੈ...",
            "bn" to "AI আপনার মাটি ও আবহাওয়া বিশ্লেষণ করছে...",
            "ta" to "AI உங்கள் மண் மற்றும் வானிலையை ஆய்வு செய்கிறது...",
            "te" to "AI మీ నేల మరియు వాతావరణాన్ని విశ్లేషిస్తోంది...",
            "kn" to "AI ನಿಮ್ಮ ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನವನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ...",
            "ml" to "AI നിങ്ങളുടെ മണ്ണും കാലാവസ്ഥയും വിശകലനം ചെയ്യുന്നു...",
            "or" to "AI ଆପଣଙ୍କ ମାଟି ଏବଂ ପାଣିପାଗ ବିଶ୍ଳେଷଣ କରୁଛି...",
            "as" to "AIয়ে আপোনাৰ মাটি আৰু বতৰ বিশ্লেষণ কৰি আছে...",
            "ur" to "AI آپ کی مٹی اور موسم کا تجزیہ کر رہا ہے...",
            "mai" to "AI अहाँक माटी आ मौसमक विश्लेषण क रहल अछि..."
        ),
        "fetching weather characteristics" to mapOf(
            "en" to "Fetching live weather and soil characteristics automatically",
            "hi" to "लाइव मौसम और मिट्टी के गुण स्वचालित रूप से प्राप्त किए जा रहे हैं",
            "gu" to "જીવંત હવામાન અને જમીનના ગુણધર્મો આપમેળે મેળવી રહ્યાં છીએ",
            "mr" to "थेट हवामान आणि जमिनीची वैशिष्ट्ये आपोआप मिळवली जात आहेत",
            "pa" to "ਤਾਜ਼ਾ ਮੌਸਮ ਅਤੇ ਮਿੱਟੀ ਦੇ ਲੱਛਣ ਆਪਣੇ-ਆਪ ਪ੍ਰਾਪਤ ਕੀਤੇ ਜਾ ਰਹੇ ਹਨ",
            "bn" to "সরাসরি আবহাওয়া ও মাটির বৈশিষ্ট্য স্বয়ংক্রিয়ভাবে সংগ্রহ করা হচ্ছে",
            "ta" to "நேரடி வானிலை மற்றும் மண் பண்புகள் தானாகப் பெறப்படுகின்றன",
            "te" to "ప్రత్యక్ష వాతావరణం మరియు నేల లక్షణాలు స్వయంచాలకంగా పొందబడుతున్నాయి",
            "kn" to "ಲೈವ್ ಹವಾಮಾನ ಮತ್ತು ಮಣ್ಣಿನ ಗುಣಲಕ್ಷಣಗಳನ್ನು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಪಡೆಯಲಾಗುತ್ತಿದೆ",
            "ml" to "തത്സമയ കാലാവസ്ഥയും മണ്ണിന്റെ സവിശേഷതകളും സ്വയമേവ ലഭ്യമാക്കുന്നു",
            "or" to "ପାଣିପାଗ ଏବଂ ମାଟିର ବିବରଣୀ ସ୍ୱୟଂଚାଳିତ ଭାବେ ଅଣାଯାଉଛି",
            "as" to "সরাসৰি বতৰ আৰু মাটিৰ বৈশিষ্ট্য স্বয়ংক্ৰিয়ভাৱে সংগ্ৰহ কৰা হৈছে",
            "ur" to "براہ راست موسم اور مٹی کی خصوصیات خود بخود حاصل کی جا رہی ہیں",
            "mai" to "लाईव मौसम आ माटीक गुण स्वचालित रूप सं प्राप्त कएल जा रहल अछि"
        ),
        "ai best recommendations" to mapOf(
            "en" to "AI Best Recommendations",
            "hi" to "AI सर्वश्रेष्ठ फसल अनुशंसाएं",
            "gu" to "AI શ્રેષ્ઠ પાક ભલામણો",
            "mr" to "AI सर्वोत्तम पीक शिफारसी",
            "pa" to "AI ਸਭ ਤੋਂ ਵਧੀਆ ਫਸਲ ਸਿਫਾਰਸ਼ਾਂ",
            "bn" to "AI সেরা ফসলের সুপারিশ",
            "ta" to "AI சிறந்த பயிர் பரிந்துரைகள்",
            "te" to "AI ఉత్తమ పంట సిఫార్సులు",
            "kn" to "AI ಅತ್ಯುತ್ತಮ ಬೆಳೆ ಶಿಫಾರಸುಗಳು",
            "ml" to "AI മികച്ച വിള നിർദ്ദേശങ്ങൾ",
            "or" to "AI ସର୍ବୋତ୍ତମ ଫସଲ ସୁପାରିଶ",
            "as" to "AI শ্ৰেষ্ঠ শস্য পৰামৰ্শ",
            "ur" to "AI بہترین فصل کی تجاویز",
            "mai" to "AI सर्वोत्तम फसल सिफारिस"
        ),
        "based on your soil" to mapOf(
            "en" to "Based on your field soil and location",
            "hi" to "आपके खेत की मिट्टी और स्थान के आधार पर",
            "gu" to "તમારા ખેતરની જમીન અને સ્થાનના આધારે",
            "mr" to "तुमच्या शेतातील माती आणि स्थानानुसार",
            "pa" to "ਤੁਹਾਡੇ ਖੇਤ ਦੀ ਮਿੱਟੀ ਅਤੇ ਟਿਕਾਣੇ ਦੇ ਆਧਾਰ 'ਤੇ",
            "bn" to "আপনার জমির মাটি ও অবস্থানের ওপর ভিত্তি করে",
            "ta" to "உங்கள் நிலத்தின் மண் மற்றும் இருப்பிடத்தின் அடிப்படையில்",
            "te" to "మీ పొలం నేల మరియు స్థానం ఆధారంగా",
            "kn" to "ನಿಮ್ಮ ಹೊಲದ ಮಣ್ಣು ಮತ್ತು ಸ್ಥಳದ ಆಧಾರದ ಮೇಲೆ",
            "ml" to "നിങ്ങളുടെ പാടത്തെ മണ്ണും സ്ഥലവും അടിസ്ഥാനമാക്കി",
            "or" to "ଆପଣଙ୍କ ଜମିର ମାଟି ଏବଂ ସ୍ଥାନ ଆଧାରରେ",
            "as" to "আপোনাৰ পথাৰৰ মাটি আৰু স্থানৰ ভিত্তিত",
            "ur" to "آپ کے کھیت کی مٹی اور مقام کی بنیاد پر",
            "mai" to "अहाँक खेतक माटी आ स्थान केर आधार पर"
        ),
        "shop seeds" to mapOf(
            "en" to "Shop Seeds & Agri Inputs",
            "hi" to "बीज और कृषि उत्पाद खरीदें",
            "gu" to "બિયારણ અને કૃષિ સાધનો ખરીદો",
            "mr" to "बियाणे आणि कृषी उत्पादने खरेदी करा",
            "pa" to "ਬੀਜ ਅਤੇ ਖੇਤੀ ਸਮੱਗਰੀ ਖਰੀਦੋ",
            "bn" to "বীজ এবং কৃষি উপকরণ কিনুন",
            "ta" to "விதைகள் மற்றும் வேளாண் இடுபொருட்கள் வாங்கவும்",
            "te" to "విత్తనాలు మరియు వ్యవసాయ వస్తువులు కొనండి",
            "kn" to "ಬೀಜಗಳು ಮತ್ತು ಕೃಷಿ ಪರಿಕರಗಳನ್ನು ಖರೀದಿಸಿ",
            "ml" to "വിത്തുകളും കാർഷിക ഉൽപ്പന്നങ്ങളും വാങ്ങുക",
            "or" to "ବିହନ ଏବଂ କୃଷି ସାମગ୍ରୀ କିଣନ୍ତୁ",
            "as" to "বীজ আৰু কৃষি সামগ্ৰী ক্ৰয় কৰক",
            "ur" to "بیج اور زرعی ادویات خریدیں",
            "mai" to "बीया आ कृषि उत्पाद कीनू"
        ),
        "start over" to mapOf(
            "en" to "START OVER",
            "hi" to "पुनः शुरू करें",
            "gu" to "ફરીથી શરૂ કરો",
            "mr" to "पुन्हा सुरू करा",
            "pa" to "ਮੁੜ ਸ਼ੁਰੂ ਕਰੋ",
            "bn" to "নতুন করে শুরু করুন",
            "ta" to "மீண்டும் தொடங்கவும்",
            "te" to "మొదటి నుండి ప్రారంభించండి",
            "kn" to "ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ",
            "ml" to "വീണ്ടും ആരംഭിക്കുക",
            "or" to "ପୁଣି ଆରମ୍ଭ କରନ୍ତୁ",
            "as" to "পুনৰ আৰম্ভ কৰক",
            "ur" to "دوبارہ شروع کریں",
            "mai" to "पुनः शुरू करू"
        ),
        "profit" to mapOf(
            "en" to "Profit",
            "hi" to "अनुमानित लाभ",
            "gu" to "અંદાજિત નફો",
            "mr" to "अपेक्षित नफा",
            "pa" to "ਅਨੁਮਾਨਿਤ ਮੁਨਾਫਾ",
            "bn" to "আনুমানিক লাভ",
            "ta" to "மதிப்பிடப்பட்ட லாபம்",
            "te" to "అంచనా లాభం",
            "kn" to "ಅಂದಾಜು ಲಾಭ",
            "ml" to "പ്രതീക്ഷിക്കുന്ന ലാഭം",
            "or" to "ଆନୁମାନିକ ଲାଭ",
            "as" to "আনুমানিক লাভ",
            "ur" to "متوقع منافع",
            "mai" to "अनुमानित मुनाफा"
        ),
        "duration" to mapOf(
            "en" to "Duration",
            "hi" to "अवधि",
            "gu" to "સમયગાળો",
            "mr" to "कालावधी",
            "pa" to "ਸਮਾਂ",
            "bn" to "সময়কাল",
            "ta" to "கால அளவு",
            "te" to "కాలపరిమితి",
            "kn" to "ಅವಧಿ",
            "ml" to "കാലയളവ്",
            "or" to "ଅବଧି",
            "as" to "সময়সীমা",
            "ur" to "مدت",
            "mai" to "अवधि"
        ),
        "water" to mapOf(
            "en" to "Water",
            "hi" to "जल आवश्यकता",
            "gu" to "પાણી જરૂરિયાત",
            "mr" to "पाण्याची गरज",
            "pa" to "ਪਾਣੀ ਦੀ ਲੋੜ",
            "bn" to "জলের চাহিদা",
            "ta" to "நீர் தேவை",
            "te" to "నీటి అవసరం",
            "kn" to "ನೀರಿನ ಅಗತ್ಯ",
            "ml" to "ജല ആവശ്യം",
            "or" to "ଜଳ ଆବଶ୍ୟକତା",
            "as" to "পানীৰ প্ৰয়োজন",
            "ur" to "پانی کی ضرورت",
            "mai" to "पानिक आवश्यकता"
        ),
        "match" to mapOf(
            "en" to "Match",
            "hi" to "उपयुक्तता",
            "gu" to "અનુકૂળતા",
            "mr" to "योग्य जुळणी",
            "pa" to "ਅਨੁਕੂਲਤਾ",
            "bn" to "উপযোগিতা",
            "ta" to "பொருத்தம்",
            "te" to "సరిపోలిక",
            "kn" to "ಹೊಂದಾಣಿಕೆ",
            "ml" to "പൊരുത്തം",
            "or" to "ଉପଯୁକ୍ତତା",
            "as" to "উপযোগিতা",
            "ur" to "مطابقت",
            "mai" to "उपयुक्तता"
        ),
        "month_unit" to mapOf(
            "en" to "Months",
            "hi" to "महीने",
            "gu" to "મહિના",
            "mr" to "महिने",
            "pa" to "ਮਹੀਨੇ",
            "bn" to "মাস",
            "ta" to "மாதங்கள்",
            "te" to "నెలలు",
            "kn" to "ತಿಂಗಳುಗಳು",
            "ml" to "മാസങ്ങൾ",
            "or" to "ମାସ",
            "as" to "মাহ",
            "ur" to "مہینے",
            "mai" to "माह"
        )
    )

    fun localizeSoil(soil: String?, langCode: String): String {
        if (soil.isNullOrBlank()) return ""
        val normalized = soil.trim().lowercase().replace("-", " ")
        val match = SOIL_TYPES[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: soil
        }
        for ((key, translations) in SOIL_TYPES) {
            if (normalized.contains(key)) {
                return translations[langCode] ?: translations["hi"] ?: soil
            }
        }
        return soil
    }

    fun localizeSoilDescription(desc: String?, langCode: String): String {
        if (desc.isNullOrBlank()) return ""
        val normalized = desc.trim().lowercase()
        for ((key, translations) in SOIL_DESCRIPTIONS) {
            if (normalized.contains(key)) {
                return translations[langCode] ?: translations["hi"] ?: desc
            }
        }
        return desc
    }

    fun localizeCropAdvicePhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase()
        val match = CROP_ADVICE_PHRASES[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        return phraseKey
    }

    fun localizeDuration(months: Int, langCode: String): String {
        val unit = CROP_ADVICE_PHRASES["month_unit"]?.get(langCode) 
            ?: CROP_ADVICE_PHRASES["month_unit"]?.get("hi") ?: "Months"
        return "$months $unit"
    }

    // ==========================================
    // 10. DAYS OF THE WEEK (14 LANGUAGES)
    // ==========================================
    private val DAYS_OF_WEEK = mapOf(
        "today" to mapOf("en" to "Today", "hi" to "आज", "gu" to "આજે", "mr" to "आज", "pa" to "ਅੱਜ", "bn" to "আজ", "ta" to "இன்று", "te" to "ఈ రోజు", "kn" to "ಇಂದು", "ml" to "ഇന്ന്", "or" to "ଆଜି", "as" to "আজি", "ur" to "آج", "mai" to "आइज"),
        "tomorrow" to mapOf("en" to "Tomorrow", "hi" to "कल", "gu" to "આવતીકાલે", "mr" to "उद्या", "pa" to "ਭਲਕੇ", "bn" to "আগামীকাল", "ta" to "நாளை", "te" to "రేపు", "kn" to "ನಾಳೆ", "ml" to "നാളെ", "or" to "ଆସନ୍ତାକାଲି", "as" to "কাইলৈ", "ur" to "کل", "mai" to "कालि"),
        "mon" to mapOf("en" to "Mon", "hi" to "सोम", "gu" to "સોમ", "mr" to "सोम", "pa" to "ਸੋਮ", "bn" to "সোম", "ta" to "திங்கள்", "te" to "సోమ", "kn" to "ಸೋಮ", "ml" to "തിങ്കൾ", "or" to "ସୋମ", "as" to "সোম", "ur" to "پیر", "mai" to "सोम"),
        "monday" to mapOf("en" to "Monday", "hi" to "सोमवार", "gu" to "સોમવાર", "mr" to "सोमवार", "pa" to "ਸੋਮਵਾਰ", "bn" to "সোমবার", "ta" to "திங்கட்கிழமை", "te" to "సోమవారం", "kn" to "ಸೋಮವಾರ", "ml" to "തിങ്കളാഴ്ച", "or" to "ସୋମବାର", "as" to "সোমবাৰ", "ur" to "پیر", "mai" to "सोमदिन"),
        "tue" to mapOf("en" to "Tue", "hi" to "मंगल", "gu" to "મંગળ", "mr" to "मंगळ", "pa" to "ਮੰਗਲ", "bn" to "মঙ্গল", "ta" to "செவ்வாய்", "te" to "మంగళ", "kn" to "ಮಂಗಳ", "ml" to "ചൊവ്വ", "or" to "ମଙ୍ଗଳ", "as" to "মঙ্গল", "ur" to "منگل", "mai" to "मंगल"),
        "tuesday" to mapOf("en" to "Tuesday", "hi" to "मंगलवार", "gu" to "મંગળવાર", "mr" to "मंगळवार", "pa" to "ਮੰਗਲਵਾਰ", "bn" to "মঙ্গলবার", "ta" to "செவ்வாய்க்கிழமை", "te" to "మంగళవారం", "kn" to "ಮಂಗಳವಾರ", "ml" to "ചൊവ്വാഴ്ച", "or" to "ମଙ୍ଗଳବାର", "as" to "মঙলবাৰ", "ur" to "منگل", "mai" to "मंगलदिन"),
        "wed" to mapOf("en" to "Wed", "hi" to "बुध", "gu" to "બુધ", "mr" to "बुध", "pa" to "ਬੁੱਧ", "bn" to "বুধ", "ta" to "புதன்", "te" to "బుధ", "kn" to "ಬುಧ", "ml" to "ബുധൻ", "or" to "ବୁଧ", "as" to "বুধ", "ur" to "بدھ", "mai" to "बुध"),
        "wednesday" to mapOf("en" to "Wednesday", "hi" to "बुधवार", "gu" to "બુધવાર", "mr" to "बुधवार", "pa" to "ਬੁੱਧਵਾਰ", "bn" to "বুধবার", "ta" to "புதன்கிழமை", "te" to "బుధవారం", "kn" to "ಬುಧವಾರ", "ml" to "ബുധനാഴ്ച", "or" to "ବୁଧବାର", "as" to "বুধবাৰ", "ur" to "بدھ", "mai" to "बुधदिन"),
        "thu" to mapOf("en" to "Thu", "hi" to "गुरु", "gu" to "ગુરુ", "mr" to "गुरु", "pa" to "ਵੀਰ", "bn" to "বৃহস্পতি", "ta" to "வியாழன்", "te" to "గురు", "kn" to "ಗುರು", "ml" to "വ്യാഴം", "or" to "ଗୁରୁ", "as" to "বৃহস্পতি", "ur" to "جمعرات", "mai" to "बृहस्पती"),
        "thursday" to mapOf("en" to "Thursday", "hi" to "गुरुवार", "gu" to "ગુરુવાર", "mr" to "गुरुवार", "pa" to "ਵੀਰਵਾਰ", "bn" to "বৃহস্পতিবার", "ta" to "வியாழக்கிழமை", "te" to "గురువారం", "kn" to "ಗುರುವಾರ", "ml" to "വ്യാഴാഴ്ച", "or" to "ଗୁରୁବାର", "as" to "বৃহস্পতিবাৰ", "ur" to "جمعرات", "mai" to "बृहस्पतिदिन"),
        "fri" to mapOf("en" to "Fri", "hi" to "शुक्र", "gu" to "શુક્ર", "mr" to "शुक्र", "pa" to "ਸ਼ੁੱਕਰ", "bn" to "শুক্র", "ta" to "வெள்ளி", "te" to "శుక్ర", "kn" to "ಶುಕ್ರ", "ml" to "വെള്ളി", "or" to "ଶୁକ୍ର", "as" to "শুক্ৰ", "ur" to "جمعہ", "mai" to "शुक्र"),
        "friday" to mapOf("en" to "Friday", "hi" to "शुक्रवार", "gu" to "શુક્રવાર", "mr" to "शुक्रवार", "pa" to "ਸ਼ੁੱਕਰਵਾਰ", "bn" to "শুক্রবার", "ta" to "வெள்ளிக்கிழமை", "te" to "శుక్రవారం", "kn" to "ಶುಕ್ರವಾರ", "ml" to "വെള്ളിയാഴ്ച", "or" to "ଶୁକ୍ରବାର", "as" to "শুক্ৰবাৰ", "ur" to "جمعہ", "mai" to "शुक्रदिन"),
        "sat" to mapOf("en" to "Sat", "hi" to "शनि", "gu" to "શનિ", "mr" to "शनि", "pa" to "ਸ਼ਨੀ", "bn" to "শনি", "ta" to "சனி", "te" to "శని", "kn" to "ಶನಿ", "ml" to "ശನಿ", "or" to "ଶନି", "as" to "শনি", "ur" to "ہفتہ", "mai" to "शनि"),
        "saturday" to mapOf("en" to "Saturday", "hi" to "शनिवार", "gu" to "શનિવાર", "mr" to "शनिवार", "pa" to "ਸ਼ਨੀਵਾਰ", "bn" to "শনিবার", "ta" to "சனிக்கிழமை", "te" to "శనివారం", "kn" to "ಶನಿವಾರ", "ml" to "ശനിയാഴ്ച", "or" to "ଶନିବାର", "as" to "শনিবাৰ", "ur" to "ہفتہ", "mai" to "शनिदिन"),
        "sun" to mapOf("en" to "Sun", "hi" to "रवि", "gu" to "રવિ", "mr" to "रवि", "pa" to "ਐਤ", "bn" to "রবি", "ta" to "ஞாயிறு", "te" to "ఆది", "kn" to "ಭಾನು", "ml" to "ഞായർ", "or" to "ରବି", "as" to "দেও", "ur" to "اتوار", "mai" to "रबि"),
        "sunday" to mapOf("en" to "Sunday", "hi" to "रविवार", "gu" to "રવિવાર", "mr" to "रविवार", "pa" to "ਐਤਵਾਰ", "bn" to "রবিবার", "ta" to "ஞாயிற்றுக்கிழமை", "te" to "ఆదివారం", "kn" to "ಭಾನುವಾರ", "ml" to "ഞായറാഴ്ച", "or" to "ରବିବାର", "as" to "দেওবাৰ", "ur" to "اتوار", "mai" to "रबिदिन")
    )

    // ==========================================
    // 11. WEATHER UI PHRASES (14 LANGUAGES)
    // ==========================================
    private val WEATHER_PHRASES = mapOf(
        "agronomic guidance sub" to mapOf(
            "en" to "Actionable agronomic guidance for field operations",
            "hi" to "खेत कार्यों के लिए व्यावहारिक कृषि सलाह",
            "gu" to "ખેતી કાર્યો માટે વ્યવહારુ કૃષિ માર્ગદર્શન",
            "mr" to "शेतातील कामांसाठी प्रत्यक्ष कृषी सल्ला",
            "pa" to "ਖੇਤ ਦੇ ਕੰਮਾਂ ਲਈ ਵਿਹਾਰਕ ਖੇਤੀਬਾੜੀ ਸਲਾਹ",
            "bn" to "মাঠের কাজের জন্য ব্যবহারিক কৃষি পরামর্শ",
            "ta" to "களப்பணிகளுக்கான நடைமுறை வேளாண் வழிகாட்டுதல்",
            "te" to "పొలం పనుల కోసం ఆచరణాత్మక వ్యవసాయ సలహా",
            "kn" to "ಕೃಷಿ ಕಾರ್ಯಾಚರಣೆಗಳಿಗಾಗಿ ಉಪಯುಕ್ತ ಕೃಷಿ ಸಲಹೆ",
            "ml" to "കൃഷിപ്പണികൾക്കുള്ള പ്രായോഗിക മാർഗ്ഗനിർദ്ദേശങ്ങൾ",
            "or" to "କ୍ଷେତ କାର୍ଯ୍ୟ ପାଇଁ କାର୍ଯ୍ୟକ୍ଷମ କୃଷି ପରାମର୍ଶ",
            "as" to "পথাৰৰ কামৰ বাবে ব্যৱহাৰিক কৃষি পৰামৰ্শ",
            "ur" to "کھیت کے کاموں کے لیے قابل عمل زرعی رہنمائی",
            "mai" to "खेत केर काज लेल व्यावहारिक कृषि सलाह"
        ),
        "farm operations sub" to mapOf(
            "en" to "Actionable farm operations & suitability for today",
            "hi" to "आज के लिए खेत कार्य एवं मौसम उपयुक्तता",
            "gu" to "આજના ખેતી કાર્યો અને હવામાન અનુકૂળતા",
            "mr" to "आजच्या शेती कामांची हवामान सुसंगतता",
            "pa" to "ਅੱਜ ਲਈ ਖੇਤ ਦੇ ਕੰਮ ਅਤੇ ਮੌਸਮ ਅਨੁਕੂਲਤਾ",
            "bn" to "আজকের জন্য উপযুক্ত খামার কার্যক্রম",
            "ta" to "இன்றைய பண்ணை பணிகள் & வானிலை பொருத்தம்",
            "te" to "ఈ రోజు కోసం పొలం పనులు & అనుకూలత",
            "kn" to "ಇಂದಿನ ಕೃಷಿ ಕೆಲಸಗಳು ಮತ್ತು ಸೂಕ್ತತೆ",
            "ml" to "ഇന്നത്തെ കൃഷിപ്പണികളും അനുയോജ്യതയും",
            "or" to "ଆଜିର କ୍ଷେତ କାର୍ଯ୍ୟ ଏବଂ ପାଣିପାଗ ଉପଯୁକ୍ତତା",
            "as" to "আজিৰ বাবে উপযুক্ত কৃষি কাৰ্যাৱলী",
            "ur" to "آج کے لیے فارم کے کام اور موزونیت",
            "mai" to "आइजुक लेल खेत काज आ उपयुक्तता"
        ),
        "7day forecast sub" to mapOf(
            "en" to "7-day forecast for farm planning",
            "hi" to "खेत की योजना के लिए 7 दिनों का पूर्वानुमान",
            "gu" to "ખેતી આયોજન માટે 7 દિવસનું પૂર્વાનુમાન",
            "mr" to "शेतीच्या नियोजनासाठी 7 दिवसांचा अंदाज",
            "pa" to "ਖੇਤੀ ਯੋਜਨਾ ਲਈ 7 ਦਿਨਾਂ ਦਾ ਮੌਸਮ ਅੰਦਾਜ਼ਾ",
            "bn" to "খামার পরিকল্পনার জন্য ৭ দিনের পূর্বাভাস",
            "ta" to "பண்ணைத் திட்டமிடலுக்கான 7 நாள் முன்னறிவிப்பு",
            "te" to "వ్యవసాయ ప్రణాళిక కోసం 7 రోజుల సూచన",
            "kn" to "ಕೃಷಿ ಯೋಜನೆಗಾಗಿ 7 ದಿನಗಳ ಮುನ್ಸೂಚನೆ",
            "ml" to "കാർഷിക ആസൂത്രണത്തിനുള്ള 7 ദിവസത്തെ പ്രവചനം",
            "or" to "କୃଷି ଯୋଜନା ପାଇଁ ୭ ଦିନର ପୂର୍ବାନୁମାନ",
            "as" to "কৃষি পৰিকল্পনাৰ বাবে ৭ দিনৰ পূৰ্বাভাস",
            "ur" to "کھیتی باڑی کی منصوبہ بندی کے لیے 7 دن کی پیشین گوئی",
            "mai" to "खेत केर योजना लेल 7 दिनक पूर्वानुमान"
        ),
        "irrigation guidance" to mapOf(
            "en" to "Irrigation Guidance",
            "hi" to "सिंचाई मार्गदर्शन",
            "gu" to "પિયત માર્ગદર્શન",
            "mr" to "पाणी व्यवस्थापन सल्ला",
            "pa" to "ਸਿੰਚਾਈ ਸਲਾਹ",
            "bn" to "সেচ নির্দেশনা",
            "ta" to "நீர்ப்பாசன வழிகாட்டுதல்",
            "te" to "నీటిపారుదల సలహా",
            "kn" to "ನೀರಾವರಿ ಮಾರ್ಗದರ್ಶನ",
            "ml" to "നനയ്ക്കൽ നിർദ്ദേശം",
            "or" to "ଜଳସେଚନ ମାର୍ଗଦର୍ଶନ",
            "as" to "জলসিঞ্চন নিৰ্দেশনা",
            "ur" to "آبپاشی کی رہنمائی",
            "mai" to "पटौनी मार्गदर्शन"
        ),
        "spraying window" to mapOf(
            "en" to "Spraying Window",
            "hi" to "दवा छिड़काव का सही समय",
            "gu" to "દવા છંટકાવ માટે યોગ્ય સમય",
            "mr" to "फवारणीसाठी योग्य वेळ",
            "pa" to "ਸਪਰੇਅ ਕਰਨ ਦਾ ਸਹੀ ਸਮਾਂ",
            "bn" to "স্প্রে করার উপযুক্ত সময়",
            "ta" to "மருந்து தெளிக்கும் நேரம்",
            "te" to "పిచికారీ సమయం",
            "kn" to "ಸಿಂಪಡಣೆ ಸಮಯ",
            "ml" to "മരുന്ന് തളിക്കൽ സമയം",
            "or" to "ଔଷଧ ସ୍ପ୍ରେ ସମୟ",
            "as" to "ঔষধ স্প্ৰে' কৰাৰ সময়",
            "ur" to "اسپرے کا موزوں وقت",
            "mai" to "दवाई छिड़काव केर समय"
        ),
        "field operations harvest" to mapOf(
            "en" to "Field Operations & Harvest",
            "hi" to "खेत कार्य एवं फसल कटाई",
            "gu" to "ખેતી કાર્યો અને લણણી",
            "mr" to "शेती कामे व काढणी",
            "pa" to "ਖੇਤ ਦੇ ਕੰਮ ਅਤੇ ਕਟਾਈ",
            "bn" to "মাঠের কাজ ও ফসল তোলা",
            "ta" to "களப்பணிகள் & அறுவடை",
            "te" to "పొలం పనులు & పంట కోత",
            "kn" to "ಹೊಲದ ಕೆಲಸಗಳು ಮತ್ತು ಕಟಾವು",
            "ml" to "കൃഷിപ്പണികളും വിളവെടുപ്പും",
            "or" to "କ୍ଷେତ କାର୍ଯ୍ୟ ଏବଂ ଅମଳ",
            "as" to "পথাৰৰ কাম আৰু শস্য চপোৱা",
            "ur" to "کھیت کے کام اور کٹائی",
            "mai" to "खेत काज आ कटनी"
        ),
        "assumptions" to mapOf(
            "en" to "Assumptions:",
            "hi" to "मान्यताएं:",
            "gu" to "ધારણાઓ:",
            "mr" to "गृहीतके:",
            "pa" to "ਧਾਰਨਾਵਾਂ:",
            "bn" to "অনুমান:",
            "ta" to "அனுமானங்கள்:",
            "te" to "అంచనాలు:",
            "kn" to "ಊಹೆಗಳು:",
            "ml" to "അനുമാനങ്ങൾ:",
            "or" to "ଅନୁମାନ:",
            "as" to "অনুমান:",
            "ur" to "قیاسات:",
            "mai" to "मान्यता:"
        ),
        "not suitable today" to mapOf(
            "en" to "Not Suitable For Today:",
            "hi" to "आज क्या न करें:",
            "gu" to "આજે શું ન કરવું:",
            "mr" to "आज काय करू नये:",
            "pa" to "ਅੱਜ ਕੀ ਨਾ ਕਰੋ:",
            "bn" to "আজ যা করবেন না:",
            "ta" to "இன்று செய்யக்கூடாதவை:",
            "te" to "ఈ రోజు చేయకూడని పనులు:",
            "kn" to "ಇಂದು ಮಾಡಬಾರದ ಕೆಲಸಗಳು:",
            "ml" to "ഇന്ന് ചെയ്യാൻ പാടില്ലാത്തവ:",
            "or" to "ଆଜି କ’ଣ କରିବେ ନାହିଁ:",
            "as" to "আজি কি নকৰিব:",
            "ur" to "آج کیا نہ کریں:",
            "mai" to "आइज की नै करू:"
        ),
        "recommended suitable" to mapOf(
            "en" to "Recommended & Suitable:",
            "hi" to "आज क्या करने की सलाह है:",
            "gu" to "આજે શું કરવાની ભલામણ છે:",
            "mr" to "आज काय करण्याची शिफारस आहे:",
            "pa" to "ਅੱਜ ਕੀ ਕਰਨ ਦੀ ਸਲਾਹ ਹੈ:",
            "bn" to "আজ যা করার পরামর্শ দেওয়া হচ্ছে:",
            "ta" to "இன்று செய்ய பரிந்துரைக்கப்படுபவை:",
            "te" to "ఈ రోజు చేయదగిన పనులు:",
            "kn" to "ಇಂದು ಮಾಡಲು ಶಿಫಾರಸು ಮಾಡಿದ ಕೆಲಸಗಳು:",
            "ml" to "ഇന്ന് ചെയ്യാൻ ശുപാർശ ചെയ്യുന്നവ:",
            "or" to "ଆଜି କ’ଣ କରିବା ପାଇଁ ପରାମର୍ଶ:",
            "as" to "আজি কি কৰিব পাৰি:",
            "ur" to "آج کیا کرنے کا مشورہ ہے:",
            "mai" to "आइज की करबाक सलाह अछि:"
        ),
        "key precautions" to mapOf(
            "en" to "Key Precautions:",
            "hi" to "मुख्य सावधानियां:",
            "gu" to "મુખ્ય સાવચેતીઓ:",
            "mr" to "महत्त्वाच्या खबरदाऱ्या:",
            "pa" to "ਮੁੱਖ ਸਾਵਧਾਨੀਆਂ:",
            "bn" to "প্রধান সতর্কতা:",
            "ta" to "முக்கிய முன்னெச்சரிக்கைகள்:",
            "te" to "ముఖ్యమైన జాగ్రత్తలు:",
            "kn" to "ಮುಖ್ಯ ಮುನ್ನೆಚ್ಚರಿಕೆಗಳು:",
            "ml" to "പ്രധാന മുൻകരുതലുകൾ:",
            "or" to "ମୁଖ୍ୟ ସତର୍କତା:",
            "as" to "মুখ্য সাৱধানতা:",
            "ur" to "اہم احتیاطی تدابیر:",
            "mai" to "मुख्य सावधानी:"
        ),
        "condition label" to mapOf(
            "en" to "Condition:",
            "hi" to "स्थिति:",
            "gu" to "સ્થિતિ:",
            "mr" to "स्थिती:",
            "pa" to "ਸਥਿਤੀ:",
            "bn" to "অবস্থা:",
            "ta" to "நிலை:",
            "te" to "పరిస్థితి:",
            "kn" to "ಸ್ಥಿತಿ:",
            "ml" to "അവസ്ഥ:",
            "or" to "ସ୍ଥିତି:",
            "as" to "অৱস্থা:",
            "ur" to "حالت:",
            "mai" to "स्थिति:"
        ),
        "loading live weather" to mapOf(
            "en" to "Loading live weather",
            "hi" to "लाइव मौसम लोड हो रहा है",
            "gu" to "લાઇવ હવામાન લોડ થઈ રહ્યું છે",
            "mr" to "थेट हवामान माहिती लोड होत आहे",
            "pa" to "ਲਾਈਵ ਮੌਸਮ ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ",
            "bn" to "লাইভ আবহাওয়া লোড হচ্ছে",
            "ta" to "நேரடி வானிலை ஏற்றப்படுகிறது",
            "te" to "ప్రత్యక్ష వాతావరణం లోడ్ అవుతోంది",
            "kn" to "ಲೈವ್ ಹವಾಮಾನ ಲೋಡ್ ಆಗುತ್ತಿದೆ",
            "ml" to "തത്സമയ കാലാവസ്ഥ ലഭ്യമാക്കുന്നു",
            "or" to "ଲାଇଭ୍ ପାଣିପାଗ ଲୋଡ୍ ହେଉଛି",
            "as" to "লাইভ বতৰ লোড হৈ আছে",
            "ur" to "لائیو موسم لوڈ ہو رہا ہے",
            "mai" to "लाइव मौसम लोड भ रहल अछि"
        ),
        "fetching field conditions" to mapOf(
            "en" to "Fetching your field conditions...",
            "hi" to "आपके खेत की मौसम जानकारी लाई जा रही है...",
            "gu" to "તમારા ખેતરની હવામાન માહિતી મેળવી રહ્યા છીએ...",
            "mr" to "तुमच्या शेतातील हवामान स्थिती मिळवत आहे...",
            "pa" to "ਤੁਹਾਡੇ ਖੇਤ ਦੀ ਮੌਸਮੀ ਸਥਿਤੀ ਪ੍ਰਾਪਤ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ...",
            "bn" to "আপনার জমির আবহাওয়ার তথ্য আনা হচ্ছে...",
            "ta" to "உங்கள் வயலின் வானிலை விவரங்கள் பெறப்படுகின்றன...",
            "te" to "మీ పొలం వాతావరణ వివరాలు తీసుకువస్తున్నాము...",
            "kn" to "ನಿಮ್ಮ ಹೊಲದ ಹವಾಮಾನ ವಿವರಗಳನ್ನು ತರಲಾಗುತ್ತಿದೆ...",
            "ml" to "നിങ്ങളുടെ പാടത്തെ കാലാവസ്ഥ വിവരങ്ങൾ ശേഖരിക്കുന്നു...",
            "or" to "ଆପଣଙ୍କ ଜମିର ପାଣିପାଗ ସୂଚନା ଅଣାଯାଉଛି...",
            "as" to "আপোনাৰ পথাৰৰ বতৰৰ তথ্য সংগ্ৰহ কৰা হৈছে...",
            "ur" to "آپ کے کھیت کے موسم کی تفصیلات حاصل کی جا رہی ہیں...",
            "mai" to "अहाँक खेत केर मौसम केर जानकारी आबि रहल अछि..."
        ),
        "weather unavailable" to mapOf(
            "en" to "Weather unavailable",
            "hi" to "मौसम जानकारी अनुपलब्ध",
            "gu" to "હવામાન ઉપલબ્ધ નથી",
            "mr" to "हवामान माहिती उपलब्ध नाही",
            "pa" to "ਮੌਸਮ ਉਪਲਬਧ ਨਹੀਂ",
            "bn" to "আবহাওয়া পাওয়া যায়নি",
            "ta" to "வானிலை தகவல் கிடைக்கவில்லை",
            "te" to "వాతావరణం అందుబాటులో లేదు",
            "kn" to "ಹವಾಮಾನ ಲಭ್ಯವಿಲ್ಲ",
            "ml" to "കാലാവസ്ഥ ലഭ്യമല്ല",
            "or" to "ପାଣିପାଗ ଉପଲବ୍ଧ ନାହିଁ",
            "as" to "বতৰৰ তথ্য উপলব্ধ নহয়",
            "ur" to "موسم دستیاب نہیں ہے",
            "mai" to "मौसम अनुपलब्ध अछि"
        ),
        "try again" to mapOf(
            "en" to "Try Again",
            "hi" to "पुनः प्रयास करें",
            "gu" to "ફરી પ્રયાસ કરો",
            "mr" to "पुन्हा प्रयत्न करा",
            "pa" to "ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ",
            "bn" to "আবার চেষ্টা করুন",
            "ta" to "மீண்டும் முயற்சிக்கவும்",
            "te" to "మళ్ళీ ప్రయత్నించండి",
            "kn" to "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",
            "ml" to "വീണ്ടും ശ്രമിക്കുക",
            "or" to "ପୁଣି ଆରମ୍ଭ କରନ୍ତୁ",
            "as" to "পুনৰ চেষ্টা কৰক",
            "ur" to "دوبارہ کوشش کریں",
            "mai" to "पुनः प्रयास करू"
        ),
        "weather" to mapOf(
            "en" to "Weather",
            "hi" to "मौसम",
            "gu" to "હવામાન",
            "mr" to "हवामान",
            "pa" to "ਮੌਸਮ",
            "bn" to "আবহাওয়া",
            "ta" to "வானிலை",
            "te" to "వాతావరణం",
            "kn" to "ಹವಾಮಾನ",
            "ml" to "കാലാവസ്ഥ",
            "or" to "ପାଣିପାଗ",
            "as" to "বতৰ",
            "ur" to "موسم",
            "mai" to "मौसम"
        ),
        "general indian agronomic standard; specific crop/soil not provided" to mapOf(
            "en" to "General Indian agronomic standard; specific crop/soil not provided",
            "hi" to "सामान्य भारतीय कृषि मानक; विशिष्ट फसल/मिट्टी निर्दिष्ट नहीं",
            "gu" to "સામાન્ય ભારતીય કૃષિ ધોરણ; વિશિષ્ટ પાક/જમીન આપવામાં આવેલ નથી",
            "mr" to "सामान्य भारतीय कृषी मानके; विशिष्ट पीक/माती दिलेली नाही",
            "pa" to "ਆਮ ਭਾਰਤੀ ਖੇਤੀਬਾੜੀ ਮਿਆਰ; ਖਾਸ ਫਸਲ/ਮਿੱਟੀ ਨਹੀਂ ਦਿੱਤੀ ਗਈ",
            "bn" to "সাধারণ ভারতীয় কৃষি মানদণ্ড; নির্দিষ্ট ফসল/মাটি প্রদান করা হয়নি",
            "ta" to "பொதுவான இந்திய வேளாண் தரம்; குறிப்பிட்ட பயிர்/மண் குறிப்பிடப்படவில்லை",
            "te" to "సాధారణ భారతీయ వ్యవసాయ ప్రమాణం; నిర్దిష్ట పంట/నేల ఇవ్వబడలేదు",
            "kn" to "ಸಾಮಾನ್ಯ ಭಾರತೀಯ ಕೃಷಿ ಮಾನದಂಡ; ನಿರ್ದಿಷ್ಟ ಬೆಳೆ/ಮಣ್ಣು ಒದಗಿಸಲಾಗಿಲ್ಲ",
            "ml" to "പൊതുവായ ഇന്ത്യൻ കാർഷിക മാനദണ്ഡം; പ്രത്യേക വിള/മണ്ണ് നൽകിയിട്ടില്ല",
            "or" to "ସାଧାରଣ ଭାରତୀୟ କୃଷି ମାନକ; ନିର୍ଦ୍ଦିଷ୍ଟ ଫସଲ/ମାଟି ପ୍ରଦାନ କରାଯାଇ ନାହିଁ",
            "as" to "সাধাৰণ ভাৰতীয় কৃষি মানদণ্ড; নিৰ্দিষ্ট শস্য/মাটি উল্লেখ কৰা নাই",
            "ur" to "عام ہندوستانی زرعی معیارات؛ مخصوص فصل/مٹی فراہم نہیں کی گئی",
            "mai" to "सामान्य भारतीय कृषि मानक; कोनो विशिष्ट फसल/माटी निर्दिष्ट नहि"
        )
    )

    fun localizeDay(day: String?, langCode: String): String {
        if (day.isNullOrBlank()) return ""
        val normalized = day.trim().lowercase()
        val match = DAYS_OF_WEEK[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: day
        }
        for ((key, translations) in DAYS_OF_WEEK) {
            if (normalized.startsWith(key)) {
                return translations[langCode] ?: translations["hi"] ?: day
            }
        }
        return day
    }

    fun localizeWeatherPhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase().trimEnd('.', ';', ':')
        val match = WEATHER_PHRASES[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        for ((key, translations) in WEATHER_PHRASES) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: phraseKey
            }
        }
        return phraseKey
    }

    // ==========================================
    // 12. CROP SERVICES UI PHRASES (14 LANGUAGES)
    // ==========================================
    private val CROP_SERVICES_PHRASES = mapOf(
        "crop services" to mapOf(
            "en" to "Crop Services", "hi" to "फसल सेवाएं", "gu" to "પાક સેવાઓ", "mr" to "पीक सेवा",
            "pa" to "ਫਸਲ ਸੇਵਾਵਾਂ", "bn" to "ফসল পরিষেবা", "ta" to "பயிர் சேவைகள்", "te" to "పంట సేవలు",
            "kn" to "ಬೆಳೆ ಸೇವೆಗಳು", "ml" to "വിള സേവനങ്ങൾ", "or" to "ଫସଲ ସେବା", "as" to "শস্য সেৱা",
            "ur" to "فصل کی خدمات", "mai" to "फसल सेवा सभ"
        ),
        "smart solutions for healthier crops" to mapOf(
            "en" to "Smart Solutions\nfor Healthier Crops",
            "hi" to "स्वस्थ फसलों के लिए\nस्मार्ट समाधान",
            "gu" to "તંદુરસ્ત પાક માટે\nસ્માર્ટ ઉપાયો",
            "mr" to "निरोगी पिकांसाठी\nस्मार्ट उपाय",
            "pa" to "ਸਿਹਤਮੰਦ ਫਸਲਾਂ ਲਈ\nਸਮਾਰਟ ਹੱਲ",
            "bn" to "সুস্থ ফসলের জন্য\nস্মার্ট সমাধান",
            "ta" to "ஆரோக்கியமான பயிர்களுக்கான\nஸ்மார்ட் தீர்வுகள்",
            "te" to "ఆరోగ్యకరమైన పంటల కోసం\nస్మార్ట్ పరిష్కారాలు",
            "kn" to "ಆರೋಗ್ಯಕರ ಬೆಳೆಗಳಿಗಾಗಿ\nಸ್ಮಾರ್ಟ್ ಪರಿಹಾರಗಳು",
            "ml" to "ആരോഗ്യമുള്ള വിളകൾക്കായി\nസ്മാർട്ട് പരിഹാരങ്ങൾ",
            "or" to "ସୁସ୍ଥ ଫସଲ ପାଇଁ\nସ୍ମାର୍ଟ ସମାଧାନ",
            "as" to "স্বাস্থ্যকৰ শস্যৰ বাবে\nস্মাৰ্ট সমাধান",
            "ur" to "بہتر فصلوں کے لیے\nاسمارٹ حل",
            "mai" to "स्वस्थ फसल लेल\nस्मार्ट समाधान"
        ),
        "crop services hero sub" to mapOf(
            "en" to "AI-powered tools and expert \nguidance for every stage of\nyour farming journey.",
            "hi" to "आपकी खेती के हर चरण के लिए\nएआई-संचालित उपकरण और\nविशेषज्ञ मार्गदर्शन।",
            "gu" to "તમારી ખેતીના દરેક તબક્કા માટે\nAI ટૂલ્સ અને નિષ્ણાત માર્ગદર્શન.",
            "mr" to "तुमच्या शेतीच्या प्रत्येक टप्प्यासाठी\nAI टूल्स आणि तज्ञांचे मार्गदर्शन.",
            "pa" to "ਤੁਹਾਡੀ ਖੇਤੀ ਦੇ ਹਰ ਪੜਾਅ ਲਈ\nAI ਟੂਲ ਅਤੇ ਮਾਹਿਰਾਂ ਦੀ ਸਲਾਹ।",
            "bn" to "আপনার চাষাবাদের প্রতিটি পর্যায়ের জন্য\nAI টুল এবং বিশেষজ্ঞের পরামর্শ।",
            "ta" to "உங்கள் விவசாயத்தின் ஒவ்வொரு கட்டத்திற்கும்\nAI கருவிகள் மற்றும் நிபுணர் வழிகாட்டுதல்.",
            "te" to "మీ వ్యవసాయ ప్రయాణంలోని ప్రతి దశకు\nAI సాధనాలు మరియు నిపుణుల మార్గదర్శకత్వం.",
            "kn" to "ನಿಮ್ಮ ಕೃಷಿಯ ಪ್ರತಿಯೊಂದು ಹಂತಕ್ಕೂ\nAI ಪರಿಕರಗಳು ಮತ್ತು ತಜ್ಞರ ಮಾರ್ಗದರ್ಶನ.",
            "ml" to "നിങ്ങളുടെ കൃഷിയുടെ ഓരോ ഘട്ടത്തിലും\nAI ടൂളുകളും വിദഗ്ദ്ധ മാർഗ്ഗനിർദ്ദേശങ്ങളും.",
            "or" to "ଆପଣଙ୍କ କୃଷିର ପ୍ରତ୍ୟେକ ପର୍ଯ୍ୟାୟ ପାଇଁ\nAI ଉପକਰଣ ଏବଂ ବିଶେଷଜ୍ଞ ପରାମର୍ଶ।",
            "as" to "আপোনাৰ খেতিৰ প্ৰতিটো পৰ্যায়ৰ বাবে\nAI সঁজুলি আৰু বিশেষজ্ঞৰ পৰামৰ্শ।",
            "ur" to "آپ کی کاشتکاری کے ہر مرحلے کے لیے\nAI ٹولز اور ماہرین کی رہنمائی۔",
            "mai" to "अहाँक खेती केर हर चरण लेल\nAI उपकरण आ विशेषज्ञ मार्गदर्शन।"
        ),
        "available services" to mapOf(
            "en" to "Available Services", "hi" to "उपलब्ध सेवाएं", "gu" to "ઉપલબ્ધ સેવાઓ", "mr" to "उपलब्ध सेवा",
            "pa" to "ਉਪਲਬਧ ਸੇਵਾਵਾਂ", "bn" to "উপলব্ধ পরিষেবা", "ta" to "கிடைக்கும் சேவைகள்", "te" to "అందుబాటులో ఉన్న సేవలు",
            "kn" to "ಲಭ್ಯವಿರುವ ಸೇವೆಗಳು", "ml" to "ലഭ്യമായ സേവനങ്ങൾ", "or" to "ଉପଲବ୍ଧ ସେବାସମୂହ", "as" to "উপলব্ধ সেৱাসমূহ",
            "ur" to "دستیاب خدمات", "mai" to "उपलब्ध सेवा सभ"
        ),
        "available services sub" to mapOf(
            "en" to "Explore AI-powered tools and expert guidance",
            "hi" to "एआई टूल्स और विशेषज्ञ मार्गदर्शन देखें",
            "gu" to "AI ટૂલ્સ અને નિષ્ણાત માર્ગદર્શન મેળવો",
            "mr" to "AI टूल्स आणि तज्ञांचे मार्गदर्शन एक्सप्लोर करा",
            "pa" to "AI ਟੂਲ ਅਤੇ ਮਾਹਿਰਾਂ ਦੀ ਸਲਾਹ ਪ੍ਰਾਪਤ ਕਰੋ",
            "bn" to "AI টুল এবং বিশেষজ্ঞের পরামর্শ অন্বেষণ করুন",
            "ta" to "AI கருவிகள் மற்றும் நிபுணர் வழிகாட்டலைக் கண்டறியவும்",
            "te" to "AI సాధనాలు మరియు నిపుణుల సలహాలను చూడండి",
            "kn" to "AI ಪರಿಕರಗಳು ಮತ್ತು ತಜ್ಞರ ಮಾರ್ಗದರ್ಶನವನ್ನು ಅನ್ವೇಷಿಸಿ",
            "ml" to "AI ടൂളുകളും വിദഗ്ദ്ധ നിർദ്ദേശങ്ങളും പര്യവേಕ್ಷണം ചെയ്യുക",
            "or" to "AI ଉପକରଣ ଏବଂ ବିଶେଷଜ୍ଞ ପରାମର୍ଶ ଅନ୍ୱେଷଣ କରନ୍ତୁ",
            "as" to "AI সঁজুলি আৰু বিশেষজ্ঞৰ নিৰ্দেশনা চাওক",
            "ur" to "AI ٹولز اور ماہرانہ رہنمائی دریافت کریں",
            "mai" to "AI उपकरण आ विशेषज्ञ मार्गदर्शन देखू"
        ),
        "crop advice" to mapOf(
            "en" to "Crop Advice", "hi" to "फसल सलाह", "gu" to "પાક સલાહ", "mr" to "पीक सल्ला",
            "pa" to "ਫਸਲ ਸਲਾਹ", "bn" to "ফসল পরামর্শ", "ta" to "பயிர் ஆலோசனை", "te" to "పంట సలహా",
            "kn" to "ಬೆಳೆ ಸಲಹೆ", "ml" to "വിള ഉപദേശം", "or" to "ଫସଲ ପରାମର୍ଶ", "as" to "শস্য পৰামৰ্শ",
            "ur" to "فصل کا مشورہ", "mai" to "फसल सलाह"
        ),
        "crop advice sub" to mapOf(
            "en" to "Personalized advice\nfor better yield",
            "hi" to "बेहतर पैदावार के लिए\nव्यक्तिगत सलाह",
            "gu" to "વધુ ઉત્પાદન માટે\nવ્યક્તિગત સલાહ",
            "mr" to "चांगल्या उत्पादनासाठी\nवैयक्तिक सल्ला",
            "pa" to "ਵਧੀਆ ਝਾੜ ਲਈ\nਨਿੱਜੀ ਸਲਾਹ",
            "bn" to "উন্নত ফলনের জন্য\nব্যক্তিগত পরামর্শ",
            "ta" to "சிறந்த விளைச்சலுக்கு\nதனிப்பயனாக்கப்பட்ட ஆலோசனை",
            "te" to "మంచి దిగుబడి కోసం\nవ్యక్తిగత సలహా",
            "kn" to "ಉತ್ತಮ ಇಳುವರಿಗಾಗಿ\nವೈಯಕ್ತಿಕ ಸಲಹೆ",
            "ml" to "മികച്ച വിളവിനായി\nപ്രത്യേക ഉപദേശം",
            "or" to "ଉତ୍ତମ ଅମଳ ପାଇଁ\nବ୍ୟକ୍ତିଗତ ପରାମର୍ଶ",
            "as" to "উন্নত উৎপাদনৰ বাবে\nব্যক্তিগত পৰামৰ্শ",
            "ur" to "بہتر پیداوار کے لیے\nذاتی مشورہ",
            "mai" to "बढ़िया पैदावार लेल\nव्यक्तिगत सलाह"
        ),
        "disease info" to mapOf(
            "en" to "Disease Info", "hi" to "रोग जानकारी", "gu" to "રોગ માહિતી", "mr" to "रोग माहिती",
            "pa" to "ਬਿਮਾਰੀ ਜਾਣਕਾਰੀ", "bn" to "রোগের তথ্য", "ta" to "நோய் தகவல்", "te" to "వ్యాధి సమాచారం",
            "kn" to "ರೋಗ ಮಾಹಿತಿ", "ml" to "രോഗ വിവരങ്ങൾ", "or" to "ରୋଗ ସୂଚନା", "as" to "ৰোগৰ তথ্য",
            "ur" to "بیماری کی معلومات", "mai" to "रोग केर जानकारी"
        ),
        "disease info sub" to mapOf(
            "en" to "Identify diseases\nand get solutions",
            "hi" to "रोगों की पहचान करें\nऔर समाधान पाएं",
            "gu" to "રોગ ઓળખો\nઅને ઉકેલ મેળવો",
            "mr" to "रोग ओळखा\nआणि उपाय मिळवा",
            "pa" to "ਬਿਮਾਰੀ ਪਛਾਣੋ\nਅਤੇ ਹੱਲ ਪਾਓ",
            "bn" to "রোগ শনাক্ত করুন\nও সমাধান পান",
            "ta" to "நோய்களைக் கண்டறிந்து\nதீர்வுகளைப் பெறுங்கள்",
            "te" to "వ్యాధులను గుర్తించి\nపరిష్కారాలు పొందండి",
            "kn" to "ರೋಗಗಳನ್ನು ಗುರುತಿಸಿ\nಪರಿಹಾರಗಳನ್ನು ಪಡೆಯಿರಿ",
            "ml" to "രോഗങ്ങൾ തിരിച്ചറിഞ്ഞ്\nപരിഹാരങ്ങൾ നേടുക",
            "or" to "ରୋଗ ଚିହ୍ନଟ କରନ୍ତୁ\nଏବଂ ସମାଧାନ ପାଆନ୍ତୁ",
            "as" to "ৰোগ চিনাক্ত কৰক\nআৰু সমাধান পাওক",
            "ur" to "بیماریوں کی شناخت کریں\nاور حل حاصل کریں",
            "mai" to "रोग केर पहचान करू\nआ समाधान पाबू"
        ),
        "harvesting" to mapOf(
            "en" to "Harvesting", "hi" to "फसल कटाई", "gu" to "લણણી", "mr" to "काढणी",
            "pa" to "ਵਾਢੀ", "bn" to "ফসল তোলা", "ta" to "அறுவடை", "te" to "పంట కోత",
            "kn" to "ಕಟಾವು", "ml" to "വിളവെടുപ്പ്", "or" to "ଅମଳ", "as" to "শস্য চপোৱা",
            "ur" to "کٹائی", "mai" to "कटनी"
        ),
        "harvesting sub" to mapOf(
            "en" to "Best time and tips\nfor harvesting",
            "hi" to "कटाई का सही समय\nऔर उपयोगी सुझाव",
            "gu" to "લણણી માટે યોગ્ય સમય\nઅને ઉપયોગી ટીપ્સ",
            "mr" to "काढणीसाठी योग्य वेळ\nआणि उपयुक्त टिप्स",
            "pa" to "ਵਾਢੀ ਦਾ ਸਹੀ ਸਮਾਂ\nਅਤੇ ਸੁਝਾਅ",
            "bn" to "ফসল তোলার সঠিক সময়\nও প্রয়োজনীয় টিপস",
            "ta" to "அறுவடைக்கான சிறந்த நேரம்\nமற்றும் குறிப்புகள்",
            "te" to "పంట కోతకు సరైన సమయం\nమరియు చిట్కాలు",
            "kn" to "ಕಟಾವಿಗೆ ಸೂಕ್ತ ಸಮಯ\nಮತ್ತು ಉಪಯುಕ್ತ ಸಲಹೆಗಳು",
            "ml" to "വിളവെടുപ്പിന് അനുയോജ്യമായ സമയവും\nനുറുങ്ങുകളും",
            "or" to "ଅମଳ ପାଇଁ ଉପଯୁକ୍ତ ସମୟ\nଏବଂ ଟିପ୍ସ",
            "as" to "শস্য চপোৱাৰ সঠিক সময়\nআৰু পৰামৰ্শ",
            "ur" to "کٹائی کا بہترین وقت\nاور اہم تجاویز",
            "mai" to "कटनी केर सही समय\nआ उपयोगी सुझाव"
        ),
        "selling" to mapOf(
            "en" to "Selling", "hi" to "फसल बिक्री", "gu" to "વેચાણ", "mr" to "विक्री",
            "pa" to "ਵੇਚਣਾ", "bn" to "বিক্রি", "ta" to "விற்பனை", "te" to "అమ్మకం",
            "kn" to "ಮಾರಾಟ", "ml" to "വിൽപ്പന", "or" to "ବିକ୍ରୟ", "as" to "বিক্ৰী",
            "ur" to "فروخت", "mai" to "बेचब"
        ),
        "selling sub" to mapOf(
            "en" to "Get the best price\nfor your produce",
            "hi" to "अपनी उपज का\nपाएं सबसे अच्छा दाम",
            "gu" to "તમારા ઉત્પાદનનો\nસારો ભાવ મેળવો",
            "mr" to "तुमच्या शेतमालाला\nमिळवा उत्तम भाव",
            "pa" to "ਆਪਣੀ ਉਪਜ ਦਾ\nਸਭ ਤੋਂ ਵਧੀਆ ਮੁੱਲ ਪਾਓ",
            "bn" to "আপনার ফসলের\nসেরা দাম পান",
            "ta" to "உங்கள் விளைபொருளுக்கு\nசிறந்த விலையைப் பெறுங்கள்",
            "te" to "మీ పంటకు\nమంచి ధర పొందండి",
            "kn" to "ನಿಮ್ಮ ಬೆಳೆಗೆ\nಉತ್ತಮ ಬೆಲೆ ಪಡೆಯಿರಿ",
            "ml" to "നിങ്ങളുടെ ഉൽപ്പന്നങ്ങൾക്ക്\nമികച്ച വില നേടുക",
            "or" to "ଆପଣଙ୍କ ଉତ୍ପାଦନର\nସର୍ବୋତ୍ତମ ମୂଲ୍ୟ ପାଆନ୍ତୁ",
            "as" to "আপোনাৰ শস্যৰ\nসৰ্বোত্তম মূল্য লাভ কৰক",
            "ur" to "اپنی پیداوار کی\nبہترین قیمت حاصل کریں",
            "mai" to "अपन उपजाऊ केर\nसबसँ नीक दाम पाबू"
        )
    )

    fun localizeCropServicesPhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase()
        val match = CROP_SERVICES_PHRASES[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        for ((key, translations) in CROP_SERVICES_PHRASES) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: phraseKey
            }
        }
        return phraseKey
    }

    // ==========================================
    // 13. HARVESTING HELP UI PHRASES (14 LANGUAGES)
    // ==========================================
    private val HARVESTING_PHRASES = mapOf(
        "harvesting help" to mapOf(
            "en" to "Harvesting Help", "hi" to "कटाई सहायता", "gu" to "લણણી સહાય", "mr" to "काढणी मदत",
            "pa" to "ਵਾਢੀ ਸਹਾਇਤਾ", "bn" to "ফসল তোলা সহায়তা", "ta" to "அறுவடை உதவி", "te" to "పంట కోత సహాయం",
            "kn" to "ಕಟಾವು ಸಹಾಯ", "ml" to "വിളവെടുപ്പ് സഹായം", "or" to "ଅମଳ ସହାୟତା", "as" to "শস্য চপোৱাৰ সহায়",
            "ur" to "کٹائی میں مدد", "mai" to "कटनी सहायता"
        ),
        "get the right help harvest with ease" to mapOf(
            "en" to "Get the right help,\nharvest with ease",
            "hi" to "सही मदद पाएं,\nआसानी से कटाई करें",
            "gu" to "યોગ્ય મદદ મેળવો,\nસરળતાથી લણણી કરો",
            "mr" to "योग्य मदत मिळवा,\nसहजतेने काढणी करा",
            "pa" to "ਸਹੀ ਮਦਦ ਲਓ,\nਸੌਖ ਨਾਲ ਵਾਢੀ ਕਰੋ",
            "bn" to "সঠিক সহায়তা পান,\nসহজে ফসল তুলুন",
            "ta" to "சரியான உதவி பெறுங்கள்,\nசுலபமாக அறுவடை செய்யுங்கள்",
            "te" to "సరైన సహాయం పొందండి,\nసులభంగా పంట కోయండి",
            "kn" to "ಸರಿಯಾದ ಸಹಾಯ ಪಡೆಯಿರಿ,\nಸುಲಭವಾಗಿ ಕಟಾವು ಮಾಡಿ",
            "ml" to "ശരിയായ സഹായം നേടൂ,\nഎളുപ്പത്തിൽ വിളവെടുക്കൂ",
            "or" to "ସଠିକ୍ ସହାୟତା ପାଆନ୍ତୁ,\nସହଜରେ ଅମଳ କରନ୍ତୁ",
            "as" to "সঠিক সহায় লওক,\nসহজে শস্য চপাওক",
            "ur" to "صحیح مدد حاصل کریں،\nآسانی سے کٹائی کریں",
            "mai" to "सही मदद पाबू,\nअसनगर कटनी करू"
        ),
        "harvesting hero sub" to mapOf(
            "en" to "Tools, people, and storage – all to make your harvest smooth.",
            "hi" to "उपकरण, मजदूर और भंडारण – आपकी कटाई को आसान बनाने के लिए।",
            "gu" to "સાધનો, મજૂરો અને સંગ્રહ – તમારી લણણીને સરળ બનાવવા માટે.",
            "mr" to "अवजारे, मजूर आणि साठवणूक – तुमची काढणी सुलभ करण्यासाठी.",
            "pa" to "ਸੰਦ, ਮਜ਼ਦੂਰ ਅਤੇ ਸਟੋਰੇਜ – ਤੁਹਾਡੀ ਵਾਢੀ ਨੂੰ ਸੁਖਾਲਾ ਬਣਾਉਣ ਲਈ।",
            "bn" to "যন্ত্রপাতি, শ্রমিক এবং গুদাম – আপনার ফসল তোলা সহজ করার জন্য।",
            "ta" to "கருவிகள், ஆட்கள் மற்றும் சேமிப்பு – உங்கள் அறுவடையை எளிதாக்க.",
            "te" to "పనిముట్లు, కూలీలు మరియు నిಲ್వ – మీ పంట కోతను సులభతరం చేయడానికి.",
            "kn" to "ಉಪಕರಣಗಳು, ಕಾರ್ಮಿಕರು ಮತ್ತು ಸಂಗ್ರಹಣೆ – ನಿಮ್ಮ ಕಟಾವನ್ನು ಸುಗಮಗೊಳಿಸಲು.",
            "ml" to "ഉപകരണങ്ങൾ, തൊഴിലാളികൾ, സംഭരണം – വിളവെടുപ്പ് സുഗമമാക്കാൻ എല്ലാം.",
            "or" to "ଯନ୍ତ୍ରପାତି, ଶ୍ରମିକ ଏବଂ ସଂରକ୍ଷଣ – ଅମଳକୁ ସହଜ କରିବା ପାଇଁ।",
            "as" to "সঁজুলি, শ্ৰমিক আৰু সংৰক্ষণ – শস্য চপোৱা সহজ কৰিবলৈ।",
            "ur" to "اوزار، مزدور اور اسٹوریج – آپ کی کٹائی کو آسان بنانے کے لیے۔",
            "mai" to "उपकरण, मजदूर आ भंडारण – अहाँक कटनी के सरल बनेबा लेल।"
        ),
        "find labour" to mapOf(
            "en" to "Find Labour", "hi" to "मजदूर खोजें", "gu" to "મજૂર શોધો", "mr" to "मजूर शोधा",
            "pa" to "ਮਜ਼ਦੂਰ ਲੱਭੋ", "bn" to "শ্রমিক খুঁজুন", "ta" to "தொழிலாளர்களைத் தேடுங்கள்", "te" to "కూలీలను కనుగొనండి",
            "kn" to "ಕಾರ್ಮಿಕರನ್ನು ಹುಡುಕಿ", "ml" to "തൊഴിലാളികളെ കണ്ടെത്തുക", "or" to "ଶ୍ରମିକ ଖୋଜନ୍ତୁ", "as" to "শ্ৰমিক বিচাৰক",
            "ur" to "مزدور تلاش کریں", "mai" to "मजदूर खोजू"
        ),
        "find labour sub" to mapOf(
            "en" to "Hire trusted workers\nfor harvesting",
            "hi" to "कटाई के लिए\nभरोसेमंद मजदूर प्राप्त करें",
            "gu" to "લણણી માટે\nવિશ્વસનીય મજૂરો મેળવો",
            "mr" to "काढणीसाठी\nविश्वासू मजूर मिळवा",
            "pa" to "ਵਾਢੀ ਲਈ\nਭਰੋਸੇਮੰਦ ਮਜ਼ਦੂਰ ਪ੍ਰਾਪਤ ਕਰੋ",
            "bn" to "ফসল তোলার জন্য\nবিশ্বস্ত শ্রমিক নিন",
            "ta" to "அறுவடைக்கு\nநம்பகமான தொழிலாளர்களை அமர்த்தவும்",
            "te" to "పంట కోత కోసం\nనమ్మకమైన కూలీలను పొందండి",
            "kn" to "ಕಟಾವಿಗಾಗಿ\nವಿಶ್ವಾಸಾರ್ಹ ಕಾರ್ಮಿಕರನ್ನು ಪಡೆಯಿರಿ",
            "ml" to "വിളവെടുപ്പിനായി\nവിശ്വസ്തരായ തൊഴിലാളികളെ നേടൂ",
            "or" to "ଅମଳ ପାଇଁ\nବିଶ୍ୱାସଯୋଗ୍ୟ ଶ୍ରମିକ ପାଆନ୍ତୁ",
            "as" to "শস্য চপোৱাৰ বাবে\nবিশ্বাসী শ্ৰমিক লাভ কৰক",
            "ur" to "کٹائی کے لیے\nقابل اعتماد مزدور حاصل کریں",
            "mai" to "कटनी लेल\nभरोसेमंद मजदूर पाबू"
        ),
        "nearby cold storage" to mapOf(
            "en" to "Nearby Cold Storage", "hi" to "नजदीकी कोल्ड स्टोरेज", "gu" to "નજીકનું કોલ્ડ સ્ટોરેજ", "mr" to "जवळचे कोल्ड स्टोरेज",
            "pa" to "ਨੇੜਲਾ ਕੋਲਡ ਸਟੋਰੇਜ", "bn" to "নিকটবর্তী কোল্ড স্টোরেজ", "ta" to "அருகிலுள்ள குளிர்பதன கிடங்கு", "te" to "సమీప శీతల నిల్వ గిడ్డంగి",
            "kn" to "ಹತ್ತಿರದ ಕೋಲ್ಡ್ ಸ್ಟೋರೇಜ್", "ml" to "അടുത്തുള്ള കോൾഡ് സ്റ്റോറേജ്", "or" to "ନିକଟସ୍ଥ କୋଲ୍ଡ ଷ୍ଟୋରେଜ୍", "as" to "ওচৰৰ শীতল ভঁৰাল",
            "ur" to "قریبی کولڈ اسٹوریج", "mai" to "नजदीक केर कोल्ड स्टोरेज"
        ),
        "nearby cold storage sub" to mapOf(
            "en" to "Save your crop\nfrom rotting",
            "hi" to "अपनी फसल को\nखराब होने से बचाएं",
            "gu" to "તમારા પાકને\nબગડતો બચાવો",
            "mr" to "तुमचे पीक\nसडण्यापासून वाचवा",
            "pa" to "ਆਪਣੀ ਫਸਲ ਨੂੰ\nਖਰਾਬ ਹੋਣ ਤੋਂ ਬਚਾਓ",
            "bn" to "ফসল নষ্ট হওয়া থেকে\nরক্ষা করুন",
            "ta" to "உங்கள் பயிரை\nஅழுகாமல் பாதுகாக்கவும்",
            "te" to "మీ పంటను\nపాడవకుండా కాపాడుకోండి",
            "kn" to "ನಿಮ್ಮ ಬೆಳೆಯನ್ನು\nಹಾಳಾಗದಂತೆ ಕಾಪಾಡಿ",
            "ml" to "വിളവ് ചീഞ്ഞുപോകാതെ\nസംരക്ഷിക്കുക",
            "or" to "ଆପଣଙ୍କ ଫସଲକୁ\nନଷ୍ଟ ହେବାରୁ ରକ୍ଷା କରନ୍ତୁ",
            "as" to "আপোনাৰ শস্য\nপচি যোৱাৰ পৰা ৰক্ষা কৰক",
            "ur" to "اپنی فصل کو\nخراب ہونے سے بچائیں",
            "mai" to "अपन फसल के\nसड़य सं बचाबू"
        )
    )

    fun localizeHarvestingPhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase()
        val match = HARVESTING_PHRASES[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        for ((key, translations) in HARVESTING_PHRASES) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: phraseKey
            }
        }
        return phraseKey
    }

    // ==========================================
    // 14. LABOUR SERVICES UI PHRASES (14 LANGUAGES)
    // ==========================================
    private val LABOUR_PHRASES = mapOf(
        "labour service" to mapOf(
            "en" to "Labour Service", "hi" to "मजदूर सेवा", "gu" to "મજૂર સેવા", "mr" to "मजूर सेवा",
            "pa" to "ਮਜ਼ਦੂਰ ਸੇਵਾ", "bn" to "শ্রমিক পরিষেবা", "ta" to "தொழிலாளர் சேவை", "te" to "కూలీల సేవ",
            "kn" to "ಕಾರ್ಮಿಕ ಸೇವೆ", "ml" to "തൊഴിലാളി സേവനം", "or" to "ଶ୍ରମିକ ସେବା", "as" to "শ্ৰমিক সেৱা",
            "ur" to "مزدور سروس", "mai" to "मजदूर सेवा"
        ),
        "find trusted help" to mapOf(
            "en" to "Find Trusted Help,", "hi" to "भरोसेमंद मदद पाएं,", "gu" to "વિશ્વસનીય મદદ મેળવો,", "mr" to "विश्वासू मदत मिळवा,",
            "pa" to "ਭਰੋਸੇਮੰਦ ਮਦਦ ਲੱਭੋ,", "bn" to "বিশ্বস্ত সহায়তা পান,", "ta" to "நம்பகமான உதவி பெறுங்கள்,", "te" to "నమ్మకమైన సహాయం పొందండి,",
            "kn" to "ವಿಶ್ವಾಸಾರ್ಹ ಸಹಾಯ ಪಡೆಯಿರಿ,", "ml" to "വിശ്വസ്ത സഹായം കണ്ടെത്തൂ,", "or" to "ବିଶ୍ୱାସଯୋଗ୍ୟ ସହାୟତା ପାଆନ୍ତୁ,", "as" to "বিশ্বাসী সহায় লাভ কৰক,",
            "ur" to "قابل اعتماد مدد تلاش کریں،", "mai" to "भरोसेमंद मदद पाबू,"
        ),
        "get work done" to mapOf(
            "en" to "Get Work Done.", "hi" to "काम समय पर पूरा करें।", "gu" to "કામ સમયસર પૂરું કરો.", "mr" to "काम वेळेत पूर्ण करा.",
            "pa" to "ਕੰਮ ਸਮੇਂ ਸਿਰ ਪੂਰਾ ਕਰੋ।", "bn" to "কাজ সহজে সম্পন্ন করুন।", "ta" to "வேலையை முடியுங்கள்.", "te" to "పనిని పూర్తి చేయండి.",
            "kn" to "ಕೆಲಸವನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ.", "ml" to "ജോലി വേഗത്തിൽ തീർക്കൂ.", "or" to "କାମ ସମ୍ପନ୍ନ କରନ୍ତୁ।", "as" to "কাম সহজে সম্পন্ন কৰক।",
            "ur" to "کام مکمل کروائیں۔", "mai" to "काज समय पर पूरा करू।"
        ),
        "labour hero sub" to mapOf(
            "en" to "Hire skilled labour or find daily work quickly and easily.",
            "hi" to "कुशल मजदूर किराए पर लें या आसानी से दैनिक काम खोजें।",
            "gu" to "કુશળ મજૂરો મેળવો અથવા સરળતાથી રોજિંદુ કામ શોધો.",
            "mr" to "कुशल मजूर मिळवा किंवा सहजपणे रोजंदारी काम शोधा.",
            "pa" to "ਹੁਨਰਮੰਦ ਮਜ਼ਦੂਰ ਲੱਭੋ ਜਾਂ ਆਸਾਨੀ ਨਾਲ ਰੋਜ਼ਾਨਾ ਕੰਮ ਪ੍ਰਾਪਤ ਕਰੋ।",
            "bn" to "দক্ষ শ্রমিক নিয়োগ করুন বা সহজে দৈনিক কাজ খুঁজুন।",
            "ta" to "திறமையான தொழிலாளர்களை அமர்த்தவும் அல்லது தினசரி வேலையைக் கண்டறியவும்.",
            "te" to "నైపుణ్యం కలిగిన కూలీలను నియమించుకోండి లేదా రోజువారీ పనిని సులభంగా కనుగొనండి.",
            "kn" to "ನುರಿತ ಕಾರ್ಮಿಕರನ್ನು ನೇಮಿಸಿಕೊಳ್ಳಿ ಅಥವಾ ಸುಲಭವಾಗಿ ದಿನಗೂಲಿ ಕೆಲಸ ಪಡೆಯಿರಿ.",
            "ml" to "വിദഗ്ദ്ധ തൊഴിലാളികളെ നിയമിക്കുകയോ ദൈനംദിന ജോലി കണ്ടെത്തുകയോ ചെയ്യുക.",
            "or" to "ଦକ୍ଷ ଶ୍ରମିକ ନିୟୋଜିତ କରନ୍ତୁ କିମ୍ବା ସହଜରେ ଦୈନିକ କାର୍ଯ୍ୟ ଖୋଜନ୍ତୁ।",
            "as" to "দক্ষ শ্ৰমিক বিচাৰক বা সহজে দৈনিক কাম বিচাৰি লওক।",
            "ur" to "ماہر مزدور تلاش کریں یا روزانہ کا کام آسانی سے پائیں۔",
            "mai" to "कुशल मजदूर राखू वा आसानी सं दैनिक काज खोजू।"
        ),
        "hire labour" to mapOf(
            "en" to "Hire Labour", "hi" to "मजदूर लगाएं", "gu" to "મજૂર રાખો", "mr" to "मजूर नेमा",
            "pa" to "ਮਜ਼ਦੂਰ ਰੱਖੋ", "bn" to "শ্রমিক নিয়োগ", "ta" to "தொழிலாளர்களை அமர்த்தவும்", "te" to "కూలీలను తీసుకోండి",
            "kn" to "ಕಾರ್ಮಿಕರನ್ನು ನೇಮಿಸಿ", "ml" to "തൊഴിലാളികളെ നിയമിക്കുക", "or" to "ଶ୍ରମିକ ରଖନ୍ତୁ", "as" to "শ্ৰমিক নিয়োজন",
            "ur" to "مزدور رکھیں", "mai" to "मजदूर राखू"
        ),
        "hire labour desc" to mapOf(
            "en" to "Find skilled and reliable workers for your farm.",
            "hi" to "अपने खेत के लिए कुशल और भरोसेमंद मजदूर खोजें।",
            "gu" to "તમારા ખેતર માટે કુશળ અને વિશ્વસનીય મજૂરો શોધો.",
            "mr" to "तुमच्या शेतासाठी कुशल आणि विश्वासू मजूर शोधा.",
            "pa" to "ਆਪਣੇ ਖੇਤ ਲਈ ਹੁਨਰਮੰਦ ਅਤੇ ਭਰੋਸੇਮੰਦ ਮਜ਼ਦੂਰ ਲੱਭੋ।",
            "bn" to "আপনার খামারের জন্য দক্ষ ও বিশ্বস্ত শ্রমিক খুঁজুন।",
            "ta" to "உங்கள் பண்ணைக்கு திறமையான மற்றும் நம்பகமான தொழிலாளர்களைத் தேடுங்கள்.",
            "te" to "మీ పొలం కోసం నైపుణ్యం మరియు నమ్మకమైన కూలీలను కనుగొనండి.",
            "kn" to "ನಿಮ್ಮ ಕೃಷಿಗಾಗಿ ನುರಿತ ಮತ್ತು ವಿಶ್ವಾಸಾರ್ಹ ಕಾರ್ಮಿಕರನ್ನು ಹುಡುಕಿ.",
            "ml" to "നിങ്ങളുടെ പാടത്തിനായി വിദഗ്ദ്ധരും വിശ്വസ്തരുമായ തൊഴിലാളികളെ കണ്ടെത്തുക.",
            "or" to "ଆପଣଙ୍କ ଜମି ପାଇଁ ଦକ୍ଷ ଏବଂ ବିଶ୍ୱାସଯୋଗ୍ୟ ଶ୍ରମିକ ଖୋଜନ୍ତୁ।",
            "as" to "আপোনাৰ পথাৰৰ বাবে দক্ষ আৰু বিশ্বাসী শ্ৰমিক বিচাৰক।",
            "ur" to "اپنے کھیت کے لیے ہنر مند اور قابل اعتماد مزدور تلاش کریں۔",
            "mai" to "अपन खेत लेल कुशल आ भरोसेमंद मजदूर खोजू।"
        ),
        "for farmers" to mapOf(
            "en" to "FOR FARMERS", "hi" to "किसानों के लिए", "gu" to "ખેડૂતો માટે", "mr" to "शेतकऱ्यांसाठी",
            "pa" to "ਕਿਸਾਨਾਂ ਲਈ", "bn" to "কৃষকদের জন্য", "ta" to "விவசாயிகளுக்கு", "te" to "రైతుల కోసం",
            "kn" to "ರೈತರಿಗಾಗಿ", "ml" to "കർഷകർക്കായി", "or" to "କୃଷକଙ୍କ ପାଇଁ", "as" to "কৃষকসকলৰ বাবে",
            "ur" to "کسانوں کے لیے", "mai" to "किसान सभ लेल"
        ),
        "get work" to mapOf(
            "en" to "Get Work", "hi" to "काम पाएं", "gu" to "કામ મેળવો", "mr" to "काम मिळवा",
            "pa" to "ਕੰਮ ਲੱਭੋ", "bn" to "কাজ খুঁজুন", "ta" to "வேலை பெறுங்கள்", "te" to "పని పొందండి",
            "kn" to "ಕೆಲಸ ಪಡೆಯಿರಿ", "ml" to "ജോലി നേടുക", "or" to "କାମ ପାଆନ୍ତୁ", "as" to "কাম বিচাৰক",
            "ur" to "کام تلاش کریں", "mai" to "काज पाबू"
        ),
        "get work desc" to mapOf(
            "en" to "Find nearby job opportunities and earn daily.",
            "hi" to "आस-पास काम के अवसर खोजें और रोज कमाएं।",
            "gu" to "નજીકમાં કામની તકો શોધો અને રોજ કમાઓ.",
            "mr" to "जवळपास कामाच्या संधी शोधा आणि दररोज कमवा.",
            "pa" to "ਨੇੜੇ ਕੰਮ ਦੇ ਮੌਕੇ ਲੱਭੋ ਅਤੇ ਰੋਜ਼ਾਨਾ ਕਮਾਓ।",
            "bn" to "কাছাকাছি কাজের সুযোগ খুঁজুন এবং দৈনিক আয় করুন।",
            "ta" to "அருகிலுள்ள வேலை வாய்ப்புகளைக் கண்டறிந்து தினமும் சம்பாதிக்கவும்.",
            "te" to "సమీపంలోని పని అవకాశాలను కనుగొనండి మరియు ప్రతిరోజూ సంపాదించండి.",
            "kn" to "ಹತ್ತಿರದ ಉದ್ಯೋಗಾವಕಾಶಗಳನ್ನು ಹುಡುಕಿ ಮತ್ತು ದಿನವೂ ಸಂಪಾದಿಸಿ.",
            "ml" to "സമീപത്തുള്ള തൊഴിലവസരങ്ങൾ കണ്ടെത്തി ദിവസേന സമ്പാദിക്കുക.",
            "or" to "ନିକଟସ୍ଥ କାର୍ଯ୍ୟ ସୁଯୋଗ ଖୋଜନ୍ତୁ ଏବଂ ଦୈନିକ ରୋଜଗାର କରନ୍ତୁ।",
            "as" to "ওচৰৰ কামৰ সুযোগ বিচাৰক আৰু দৈনিক উপাৰ্জন কৰক।",
            "ur" to "قریبی کام کے مواقع تلاش کریں اور روزانہ کمائیں۔",
            "mai" to "आसपास काज केर अवसर खोजू आ रोज कमाऊ।"
        ),
        "for workers" to mapOf(
            "en" to "FOR WORKERS", "hi" to "मजदूरों के लिए", "gu" to "મજૂરો માટે", "mr" to "मजुरांसाठी",
            "pa" to "ਮਜ਼ਦੂਰਾਂ ਲਈ", "bn" to "শ্রমিকদের জন্য", "ta" to "தொழிலாளர்களுக்கு", "te" to "కూలీల కోసం",
            "kn" to "ಕಾರ್ಮಿಕರಿಗಾಗಿ", "ml" to "തൊഴിലാളികൾക്കായി", "or" to "ଶ୍ରମିକଙ୍କ ପାଇଁ", "as" to "শ্ৰমিকসকলৰ বাবে",
            "ur" to "مزدوروں کے لیے", "mai" to "मजदूर सभ लेल"
        ),
        "verified workers" to mapOf(
            "en" to "Verified Workers", "hi" to "सत्यापित मजदूर", "gu" to "ચકાસાયેલ મજૂરો", "mr" to "सत्यापित मजूर",
            "pa" to "ਤਸਦੀਕਸ਼ੁਦਾ ਮਜ਼ਦੂਰ", "bn" to "যাচাইকৃত শ্রমিক", "ta" to "சரிபார்க்கப்பட்ட தொழிலாளர்கள்", "te" to "ధృవీకరించబడిన కూలీలు",
            "kn" to "ಪರಿಶೀಲಿಸಿದ ಕಾರ್ಮಿಕರು", "ml" to "പരിശോധിച്ച തൊഴിലാളികൾ", "or" to "ଯାଞ୍ଚ ହୋଇଥିବା ଶ୍ରମିକ", "as" to "পৰীক্ষিত শ্ৰমিক",
            "ur" to "تصدیق شدہ مزدور", "mai" to "सत्यापित मजदूर"
        ),
        "safe secure connections" to mapOf(
            "en" to "Safe & secure connections", "hi" to "सुरक्षित एवं भरोसेमंद", "gu" to "સુરક્ષિત અને ભરોસાપાત્ર", "mr" to "सुरक्षित आणि विश्वासार्ह",
            "pa" to "ਸੁਰੱਖਿਅਤ ਅਤੇ ਭਰੋਸੇਯੋਗ", "bn" to "নিরাপদ ও বিশ্বস্ত সংযোগ", "ta" to "பாதுகாப்பான மற்றும் நம்பகமான", "te" to "సురక్షితమైన మరియు నమ్మకమైన",
            "kn" to "ಸುರಕ್ಷಿತ ಮತ್ತು ವಿಶ್ವಾಸಾರ್ಹ", "ml" to "സുരക്ഷിതവും വിശ്വസനീയവുമായ ബന്ധം", "or" to "ସୁରକ୍ଷିତ ଏବଂ ନିର୍ଭରଯୋଗ୍ୟ", "as" to "সুৰক্ষিত আৰু নিৰ্ভৰযোগ্য",
            "ur" to "محفوظ اور قابل اعتماد", "mai" to "सुरक्षित आ भरोसेमंद"
        ),
        "local opportunities" to mapOf(
            "en" to "Local Opportunities", "hi" to "स्थानीय अवसर", "gu" to "સ્થાનિક તકો", "mr" to "स्थानिक संधी",
            "pa" to "ਸਥਾਨਕ ਮੌਕੇ", "bn" to "স্থানীয় সুযোগ", "ta" to "உள்ளூர் வாய்ப்புகள்", "te" to "స్థానిక అవకాశాలు",
            "kn" to "ಸ್ಥಳೀಯ ಅವಕಾಶಗಳು", "ml" to "പ്രാദേശിക അവസരങ്ങൾ", "or" to "ସ୍ଥାନୀୟ ସୁଯୋଗ", "as" to "স্থানীয় সুযোগ",
            "ur" to "مقامی مواقع", "mai" to "स्थानीय अवसर"
        ),
        "jobs and workers near you" to mapOf(
            "en" to "Jobs and workers near you", "hi" to "आपके पास काम और मजदूर", "gu" to "તમારી નજીક કામ અને મજૂરો", "mr" to "तुमच्या जवळ काम व मजूर",
            "pa" to "ਤੁਹਾਡੇ ਨੇੜੇ ਕੰਮ ਅਤੇ ਮਜ਼ਦੂਰ", "bn" to "আপনার কাছে কাজ ও শ্রমিক", "ta" to "உங்களுக்கு அருகிலுள்ள வேலை & ஆட்கள்", "te" to "మీ సమీపంలో పనులు & కూలీలు",
            "kn" to "ನಿಮ್ಮ ಹತ್ತಿರ ಕೆಲಸ ಮತ್ತು ಕಾರ್ಮಿಕರು", "ml" to "നിങ്ങൾക്ക് സമീപമുള്ള ജോലിയും തൊഴിലാളികളും", "or" to "ଆପଣଙ୍କ ନିକଟରେ କାମ ଏବଂ ଶ୍ରମିକ", "as" to "আপোনাৰ ওচৰৰ কাম আৰু শ্ৰমিক",
            "ur" to "آپ کے قریب کام اور مزدور", "mai" to "अहाँक लग काज आ मजदूर"
        ),
        "secure payments" to mapOf(
            "en" to "Secure Payments", "hi" to "सुरक्षित भुगतान", "gu" to "સુરક્ષિત ચુકવણી", "mr" to "सुरक्षित देयके",
            "pa" to "ਸੁਰੱਖਿਅਤ ਭੁਗਤਾਨ", "bn" to "নিরাপদ পেমেন্ট", "ta" to "பாதுகாப்பான கொடுப்பனவுகள்", "te" to "సురక్షిత చెల్లింపులు",
            "kn" to "ಸುರಕ್ಷಿತ ಪಾವತಿಗಳು", "ml" to "സുരക്ഷിത പേയ്‌മെന്റുകൾ", "or" to "ସୁରକ୍ଷିତ ପେମେଣ୍ଟ", "as" to "সুৰক্ষিত পৰিশোধ",
            "ur" to "محفوظ ادائیگیاں", "mai" to "सुरक्षित भुगतान"
        ),
        "trusted and protected" to mapOf(
            "en" to "Trusted and protected", "hi" to "विश्वसनीय और सुरक्षित", "gu" to "વિશ્વસનીય અને સુરક્ષિત", "mr" to "विश्वसनीय आणि संरक्षित",
            "pa" to "ਭਰੋਸੇਯੋਗ ਅਤੇ ਸੁਰੱਖਿਅਤ", "bn" to "বিশ্বস্ত ও সুরক্ষিত", "ta" to "நம்பகமான மற்றும் பாதுகாக்கப்பட்ட", "te" to "విశ్వసనీయ మరియు రక్షిత",
            "kn" to "ವಿಶ್ವಾಸಾರ್ಹ ಮತ್ತು ರಕ್ಷಿತ", "ml" to "വിശ്വസനീയവും സുരക്ഷിതവും", "or" to "ବିଶ୍ୱାସନୀୟ ଏବଂ ସୁରକ୍ଷିତ", "as" to "বিশ্বাসী আৰু সুৰক্ষিত",
            "ur" to "قابل اعتماد اور محفوظ", "mai" to "विश्वसनीय आ सुरक्षित"
        ),
        "hire workers" to mapOf(
            "en" to "Hire Workers", "hi" to "मजदूर लगाएं", "gu" to "મજૂરો રાખો", "mr" to "मजूर नेमा",
            "pa" to "ਮਜ਼ਦੂਰ ਲਗਾਓ", "bn" to "শ্রমিক নিয়োগ করুন", "ta" to "தொழிலாளர்களை அமர்த்தவும்", "te" to "కూలీలను తీసుకోండి",
            "kn" to "ಕಾರ್ಮಿಕರನ್ನು ನೇಮಿಸಿ", "ml" to "തൊഴിലാളികളെ നിയമിക്കുക", "or" to "ଶ୍ରମିକ ନିୟୋଜିତ କରନ୍ତୁ", "as" to "শ্ৰমিক নিয়োগ কৰক",
            "ur" to "مزدور رکھیں", "mai" to "मजदूर राखू"
        ),
        "fill details for workers" to mapOf(
            "en" to "Fill in details for workers", "hi" to "मजदूरों के लिए जानकारी भरें", "gu" to "મજૂરો માટે વિગતો ભરો", "mr" to "मजुरांसाठी माहिती भरा",
            "pa" to "ਮਜ਼ਦੂਰਾਂ ਲਈ ਜਾਣਕਾਰੀ ਭਰੋ", "bn" to "শ্রমিকদের জন্য বিবরণ পূরণ করুন", "ta" to "தொழிலாளர்களுக்கான விவரங்களை நிரப்பவும்", "te" to "కూలీల కోసం వివరాలను పూరించండి",
            "kn" to "ಕಾರ್ಮಿಕರಿಗಾಗಿ ವಿವರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ", "ml" to "തൊഴിലാളികൾക്കായി വിവരങ്ങൾ പൂരിപ്പിക്കുക", "or" to "ଶ୍ରମିକଙ୍କ ପାଇଁ ବିବରଣୀ ପୂରଣ କରନ୍ତୁ", "as" to "শ্ৰমিকৰ বাবে বিৱৰণ পূৰণ কৰক",
            "ur" to "مزدوروں کے لیے تفصیلات بھریں", "mai" to "मजदूर सभ लेल विवरण भरू"
        ),
        "what work" to mapOf(
            "en" to "What work? (e.g. Rice Sowing)", "hi" to "क्या काम है? (जैसे धान की बुवाई)", "gu" to "શું કામ છે? (જેમ કે ડાંગર રોપણી)", "mr" to "काय काम आहे? (उदा. भात लावणी)",
            "pa" to "ਕੀ ਕੰਮ ਹੈ? (ਜਿਵੇਂ ਝੋਨੇ ਦੀ ਬਿਜਾਈ)", "bn" to "কী কাজ? (যেমন ধান রোপণ)", "ta" to "என்ன வேலை? (எ.கா. நெல் நடுவு)", "te" to "ఏ పని? (ఉదా. వరి నాటు)",
            "kn" to "ಯಾವ ಕೆಲಸ? (ಉದಾ. ಭತ್ತ ನಾಟಿ)", "ml" to "എന്ത് ജോലി? (ഉദാ. നെല്ല് നടീൽ)", "or" to "କ’ଣ କାମ? (ଯେପରି ଧାନ ରୋପଣ)", "as" to "কি কাম? (যেনে ধান ৰোপণ)",
            "ur" to "کیا کام ہے؟ (مثلاً دھان کی بوائی)", "mai" to "की काज अछि? (जहिना धान रोपनी)"
        ),
        "farm location" to mapOf(
            "en" to "Farm Location", "hi" to "खेत का स्थान", "gu" to "ખેતરનું સ્થળ", "mr" to "शेताचे ठिकाण",
            "pa" to "ਖੇਤ ਦਾ ਸਥਾਨ", "bn" to "জমির অবস্থান", "ta" to "பண்ணை அமைவிடம்", "te" to "పొలం స్థలం",
            "kn" to "ಹೊಲದ ಸ್ಥಳ", "ml" to "പാടത്തിന്റെ സ്ഥലം", "or" to "ଜମିର ସ୍ଥାନ", "as" to "পথাৰৰ স্থান",
            "ur" to "کھیت کا مقام", "mai" to "खेत केर स्थान"
        ),
        "how many workers needed" to mapOf(
            "en" to "How many workers needed?", "hi" to "कितने मजदूरों की जरूरत है?", "gu" to "કેટલા મજૂરોની જરૂર છે?", "mr" to "किती मजुरांची गरज आहे?",
            "pa" to "ਕਿੰਨੇ ਮਜ਼ਦੂਰਾਂ ਦੀ ਲੋੜ ਹੈ?", "bn" to "কতজন শ্রমিক প্রয়োজন?", "ta" to "எத்தனை தொழிலாளர்கள் தேவை?", "te" to "ఎంతమంది కూలీలు కావాలి?",
            "kn" to "ಎಷ್ಟು ಜನ ಕಾರ್ಮಿಕರು ಬೇಕು?", "ml" to "എത്ര തൊഴിലാളികളെ വേണം?", "or" to "କେତେ ଶ୍ରମିକ ଆବଶ୍ୟକ?", "as" to "কিমানজন শ্ৰমিকৰ প্ৰয়োজন?",
            "ur" to "کتنے مزدوروں کی ضرورت ہے؟", "mai" to "केतेक मजदूरक आवश्यकता अछि?"
        ),
        "pay per day" to mapOf(
            "en" to "Pay per day (₹)", "hi" to "दैनिक मजदूरी (₹)", "gu" to "દૈનિક વેતન (₹)", "mr" to "दैनिक मजुरी (₹)",
            "pa" to "ਰੋਜ਼ਾਨਾ ਮਜ਼ਦૂਰੀ (₹)", "bn" to "দৈনিক মজুরি (₹)", "ta" to "தினசரி கூலி (₹)", "te" to "రోజువారీ కూలి (₹)",
            "kn" to "ದಿನದ ಕೂಲಿ (₹)", "ml" to "ദിവസ കൂലി (₹)", "or" to "ଦୈନିକ ମଜୁରୀ (₹)", "as" to "দৈনিক মজুৰি (₹)",
            "ur" to "روزانہ اجرت (₹)", "mai" to "दैनिक मजूरी (₹)"
        ),
        "post job" to mapOf(
            "en" to "POST JOB", "hi" to "काम पोस्ट करें", "gu" to "કામ પોસ્ટ કરો", "mr" to "काम पोस्ट करा",
            "pa" to "ਕੰਮ ਪੋਸਟ ਕਰੋ", "bn" to "কাজ পোস্ট করুন", "ta" to "வேலை பதிவிடவும்", "te" to "పనిని పోస్ట్ చేయండి",
            "kn" to "ಕೆಲಸ ಪೋಸ್ಟ್ ಮಾಡಿ", "ml" to "ജോലി പോസ്റ്റ് ചെയ്യുക", "or" to "କାମ ପୋଷ୍ଟ କରନ୍ତୁ", "as" to "কাম প’ষ্ট কৰক",
            "ur" to "کام پوسٹ کریں", "mai" to "काज पोस्ट करू"
        ),
        "available work near you" to mapOf(
            "en" to "Available Work Near You", "hi" to "आपके आस-पास उपलब्ध काम", "gu" to "તમારી નજીક ઉપલબ્ધ કામ", "mr" to "तुमच्या जवळ उपलब्ध काम",
            "pa" to "ਤੁਹਾਡੇ ਨੇੜੇ ਉਪਲਬਧ ਕੰਮ", "bn" to "আপনার কাছে উপলব্ধ কাজ", "ta" to "அருகில் உள்ள வேலைகள்", "te" to "మీ సమీపంలో అందుబాటులో ఉన్న పనులు",
            "kn" to "ನಿಮ್ಮ ಹತ್ತಿರ ಲಭ್ಯವಿರುವ ಕೆಲಸ", "ml" to "സമീപത്ത് ലഭ്യമായ ജോലികൾ", "or" to "ଆପଣଙ୍କ ନିକଟରେ ଉପଲବ୍ଧ କାମ", "as" to "আপোনাৰ ওচৰত উপলব্ধ কাম",
            "ur" to "آپ کے قریب دستیاب کام", "mai" to "अहाँक लग उपलब्ध काज"
        ),
        "needed workers" to mapOf(
            "en" to "Needed: %s Workers", "hi" to "आवश्यकता: %s मजदूर", "gu" to "જરૂરિયાત: %s મજૂર", "mr" to "गरज: %s मजूर",
            "pa" to "ਲੋੜ: %s ਮਜ਼ਦੂਰ", "bn" to "প্রয়োজন: %s জন শ্রমিক", "ta" to "தேவை: %s தொழிலாளர்கள்", "te" to "అవసరం: %s మంది కూలీలు",
            "kn" to "ಅಗತ್ಯ: %s ಕಾರ್ಮಿಕರು", "ml" to "ആവശ്യമുണ്ട്: %s തൊഴിലാളികൾ", "or" to "ଆବଶ୍ୟକ: %s ଜଣ ଶ୍ରମିକ", "as" to "প্ৰয়োজন: %s জন শ্ৰমিক",
            "ur" to "ضرورت: %s مزدور", "mai" to "आवश्यकता: %s मजदूर"
        ),
        "contact farmer" to mapOf(
            "en" to "Contact Farmer", "hi" to "किसान से संपर्क करें", "gu" to "ખેડૂતનો સંપર્ક કરો", "mr" to "शेतकऱ्याशी संपर्क साधा",
            "pa" to "ਕਿਸਾਨ ਨਾਲ ਸੰਪਰਕ ਕਰੋ", "bn" to "কৃষকের সাথে যোগাযোগ করুন", "ta" to "விவசாயியைத் தொடர்பு கொள்ளவும்", "te" to "రైతును సంప్రదించండి",
            "kn" to "ರೈತರನ್ನು ಸಂಪರ್ಕಿಸಿ", "ml" to "കർഷകനുമായി ബന്ധപ്പെടുക", "or" to "କୃଷକଙ୍କ ସହ ଯୋଗାଯୋଗ କରନ୍ତୁ", "as" to "কৃষকৰ সৈতে যোগাযোগ কৰক",
            "ur" to "کسان سے رابطہ کریں", "mai" to "किसान सं संपर्क करू"
        ),
        "just now" to mapOf(
            "en" to "Just now", "hi" to "अभी-अभी", "gu" to "હમણાં જ", "mr" to "आत्ताच",
            "pa" to "ਹੁਣੇ ਹੀ", "bn" to "এইমাত্র", "ta" to "இப்போது", "te" to "ఇప్పుడే",
            "kn" to "ಈಗಷ್ಟೇ", "ml" to "ഇപ്പോൾ", "or" to "ଏହିମାତ୍ର", "as" to "এইমাত্ৰ",
            "ur" to "ابھی ابھی", "mai" to "एखने"
        ),
        "wheat harvesting" to mapOf(
            "en" to "Wheat Harvesting", "hi" to "गेहूं की कटाई", "gu" to "ઘઉંની લણણી", "mr" to "गहू काढणी",
            "pa" to "ਕਣਕ ਦੀ ਵਾਢੀ", "bn" to "গম তোলা", "ta" to "கோதுமை அறுவடை", "te" to "గోధుమ కోత",
            "kn" to "ಗೋಧಿ ಕಟಾವು", "ml" to "ഗോതമ്പ് വിളവെടുപ്പ്", "or" to "ଗହମ ଅମଳ", "as" to "গম চপোৱা",
            "ur" to "گندم کی کٹائی", "mai" to "गेहूँ कटनी"
        ),
        "soil preparation" to mapOf(
            "en" to "Soil Preparation", "hi" to "खेत की तैयारी व जुताई", "gu" to "જમીનની તૈયારી", "mr" to "जमीन मशागत",
            "pa" to "ਜ਼ਮੀਨ ਦੀ ਤਿਆਰੀ", "bn" to "জমি প্রস্তুতকরণ", "ta" to "நிலம் தயார் செய்தல்", "te" to "నేల తయారీ",
            "kn" to "ಭೂಮಿ ಸಿದ್ಧತೆ", "ml" to "നിലം ഒരുക്കൽ", "or" to "ଜମି ପ୍ରସ୍ତୁତି", "as" to "মাটি প্ৰস্তুতকৰণ",
            "ur" to "زمین کی تیاری", "mai" to "खेत केर तैयारी"
        ),
        "fertilizer spray" to mapOf(
            "en" to "Fertilizer Spray", "hi" to "खाद व दवा का छिड़काव", "gu" to "ખાતર અને દવા છંટકાવ", "mr" to "खत व औषध फवारणी",
            "pa" to "ਖਾਦ ਅਤੇ ਸਪਰੇਅ", "bn" to "সার ও কীটনাশক স্প্রে", "ta" to "உர தெளித்தல்", "te" to "ఎరువుల పిచికారీ",
            "kn" to "ಗೊಬ್ಬರ ಸಿಂಪಡಣೆ", "ml" to "വളം തളിക്കൽ", "or" to "ଖତ ଏବଂ ସ୍ପ୍ରେ", "as" to "সাৰ প্ৰয়োগ",
            "ur" to "کھاد اور اسپرے", "mai" to "खाद आ दवाई छिड़काव"
        ),
        "north farm" to mapOf(
            "en" to "North Farm", "hi" to "उत्तरी खेत", "gu" to "ઉત્તર ખેતર", "mr" to "उत्तर शेत",
            "pa" to "ਉੱਤਰੀ ਖੇਤ", "bn" to "উত্তর জমি", "ta" to "வடக்குப் பண்ணை", "te" to "ఉత్తర పొలం",
            "kn" to "ಉತ್ತರ ಹೊಲ", "ml" to "വടക്കൻ പാടം", "or" to "ଉତ୍ତର ଜମି", "as" to "উত্তৰ পথাৰ",
            "ur" to "شمالی کھیت", "mai" to "उत्तर खेत"
        ),
        "east field" to mapOf(
            "en" to "East Field", "hi" to "पूर्वी खेत", "gu" to "પૂર્વ ખેતર", "mr" to "पूर्व शेत",
            "pa" to "ਪੂਰਬੀ ਖੇਤ", "bn" to "পূর্ব জমি", "ta" to "கிழக்குப் பண்ணை", "te" to "తూర్పు పొలం",
            "kn" to "ಪೂರ್ವ ಹೊಲ", "ml" to "കിഴക്കൻ പാടം", "or" to "ପୂର୍ବ ଜମି", "as" to "পূব পথাৰ",
            "ur" to "مشرقی کھیت", "mai" to "पूरब खेत"
        ),
        "main orchard" to mapOf(
            "en" to "Main Orchard", "hi" to "मुख्य बाग", "gu" to "મુખ્ય બગીચો", "mr" to "मुख्य बाग",
            "pa" to "ਮੁੱਖ ਬਾਗ", "bn" to "প্রধান বাগান", "ta" to "முக்கிய தோட்டம்", "te" to "ప్రధాన తోట",
            "kn" to "ಮುಖ್ಯ ತೋಟ", "ml" to "പ്രധാന തോട്ടം", "or" to "ମୁଖ୍ୟ ବଗିଚା", "as" to "মুখ্য বাগান",
            "ur" to "مرکزی باغ", "mai" to "मुख्य बगीचा"
        ),
        "per day" to mapOf(
            "en" to "/day", "hi" to "/दिन", "gu" to "/દિવસ", "mr" to "/दिवस",
            "pa" to "/ਦਿਨ", "bn" to "/দিন", "ta" to "/நாள்", "te" to "/రోజు",
            "kn" to "/ದಿನ", "ml" to "/ദിവസം", "or" to "/ଦିନ", "as" to "/দিন",
            "ur" to "/دن", "mai" to "/दिन"
        )
    )

    fun localizeLabourPhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase()
        val match = LABOUR_PHRASES[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        for ((key, translations) in LABOUR_PHRASES) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: phraseKey
            }
        }
        return phraseKey
    }

    // ==========================================
    // 15. ANIMAL ALERT & IOT INTRUSION (14 LANGUAGES)
    // ==========================================
    fun localizeAnimalDetectionPhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase()
        val phrases = AnimalDetectionLocalizerData.PHRASES
        val match = phrases[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        for ((key, translations) in phrases) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: phraseKey
            }
        }
        return phraseKey
    }

    // ==========================================
    // 16. DASHBOARD GREETINGS & HERO CARDS (14 LANGUAGES)
    // ==========================================
    fun localizeDashboardPhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase()
        val phrases = DashboardLocalizerData.PHRASES
        val match = phrases[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        for ((key, translations) in phrases) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: phraseKey
            }
        }
        return phraseKey
    }

    // ==========================================
    // 17. VOICE ASSISTANT (14 LANGUAGES)
    // ==========================================
    fun localizeVoiceAssistantPhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase()
        val phrases = VoiceAssistantLocalizerData.PHRASES
        val match = phrases[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        for ((key, translations) in phrases) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: phraseKey
            }
        }
        return phraseKey
    }

    // ==========================================
    // 18. PROFILE SCREEN (14 LANGUAGES)
    // ==========================================
    fun localizeProfilePhrase(phraseKey: String, langCode: String): String {
        val normalized = phraseKey.trim().lowercase()
        val phrases = ProfileLocalizerData.PHRASES
        val match = phrases[normalized]
        if (match != null) {
            return match[langCode] ?: match["hi"] ?: phraseKey
        }
        for ((key, translations) in phrases) {
            if (normalized.contains(key) || key.contains(normalized)) {
                return translations[langCode] ?: translations["hi"] ?: phraseKey
            }
        }
        return phraseKey
    }
}
