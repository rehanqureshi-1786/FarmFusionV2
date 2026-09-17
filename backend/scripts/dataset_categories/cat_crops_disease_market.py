"""
Category C: Crop Recommendation (13 conversations)
Category D: Disease Detection (13 conversations)
Category E: Mandi / Market (14 conversations)
Languages: en, hi, hinglish, gu, mr, pa, bn, ta, te, kn, ml, marwari
"""

def get_crops_disease_market_conversations():
    convs = []

    # =========================================================================
    # C. CROP RECOMMENDATION (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "C_01", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "hi",
            "description": "Hindi: Kali mitti hai aur paani kam hai, kaunsi fasal lagau?",
            "turns": [{
                "turn_number": 1, "user_input": "मेरे पास काली मिट्टी है और पानी की कमी है, कौन सी फसल लगाना सबसे सही रहेगा?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Low water + black soil recommendation in Hindi"
            }]
        },
        {
            "id": "C_02", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "hinglish",
            "description": "Hinglish: Gehun ke baad konsi crop lagau? NPK test report nahi hai.",
            "turns": [{
                "turn_number": 1, "user_input": "Gehun ke baad konsi crop lagau? NPK test report nahi hai mere paas.",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Crop rotation without soil test report in Hinglish"
            }]
        },
        {
            "id": "C_03", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "gu",
            "description": "Gujarati: કાળી જમીન અને મધ્યમ વરસાદમાં કયો પાક વાવવો જોઈએ?",
            "turns": [{
                "turn_number": 1, "user_input": "કાળી જમીન અને મધ્યમ વરસાદમાં કયો પાક વાવવો જોઈએ?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Gujarati crop recommendation for black soil"
            }]
        },
        {
            "id": "C_04", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "mr",
            "description": "Marathi: मराठवाड्यात कमी पाण्यात येणारे कोणते पीक फायदेशीर ठरेल?",
            "turns": [{
                "turn_number": 1, "user_input": "मराठवाड्यात कमी पाण्यात येणारे कोणते पीक फायदेशीर ठरेल?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Marathwada",
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Marathwada drought-resistant crop inquiry in Marathi"
            }]
        },
        {
            "id": "C_05", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "pa",
            "description": "Punjabi: ਕਣਕ ਦੀ ਵਾਢੀ ਤੋਂ ਬਾਅਦ ਕਿਹੜੀ ਫ਼ਸਲ ਲਗਾਉਣੀ ਚਾਹੀਦੀ ਹੈ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਕਣਕ ਦੀ ਵਾਢੀ ਤੋਂ ਬਾਅਦ ਕਿਹੜੀ ਫ਼ਸਲ ਲਗਾਉਣੀ ਚਾਹੀਦੀ ਹੈ ਤਾਂ ਜੋ ਜ਼ਮੀਨ ਦੀ ਉਪਜਾਊ ਸ਼ਕਤੀ ਵਧੇ?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Post-wheat soil restorative crop in Punjabi"
            }]
        },
        {
            "id": "C_06", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "bn",
            "description": "Bengali: দোআঁশ মাটিতে বোরো ধানের পর কোন ফসল সবচেয়ে ভালো হবে?",
            "turns": [{
                "turn_number": 1, "user_input": "দোআঁশ মাটিতে বোরো ধানের পর কোন ফসল সবচেয়ে ভালো হবে?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": "paddy", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Loamy soil post-Boro rice in Bengali"
            }]
        },
        {
            "id": "C_07", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "ta",
            "description": "Tamil: குறைந்த நீர் வசதி உள்ள செம்மண் நிலத்திற்கு ஏற்ற பயிர் எது?",
            "turns": [{
                "turn_number": 1, "user_input": "குறைந்த நீர் வசதி உள்ள செம்மண் நிலத்திற்கு ஏற்ற பயிர் எது?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Red soil low-water crop in Tamil"
            }]
        },
        {
            "id": "C_08", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "te",
            "description": "Telugu: నల్లరేగడి నేలలో ఈ సీజన్‌లో ఏ పంట వేస్తే ఎక్కువ లాభం వస్తుంది?",
            "turns": [{
                "turn_number": 1, "user_input": "నల్లరేగడి నేలలో ఈ సీజన్‌లో ఏ పంట వేస్తే ఎక్కువ లాభం వస్తుంది?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Black cotton soil profit crop in Telugu"
            }]
        },
        {
            "id": "C_09", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "kn",
            "description": "Kannada: ಮರಳು ಮಿಶ್ರಿತ ಮಣ್ಣಿಗೆ ಯಾವ ಬೆಳೆ ಸೂಕ್ತ?",
            "turns": [{
                "turn_number": 1, "user_input": "ಮರಳು ಮಿಶ್ರಿತ ಮಣ್ಣಿಗೆ ಮತ್ತು ಕಡಿಮೆ ಮಳೆಗೆ ಯಾವ ಬೆಳೆ ಸೂಕ್ತ?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Sandy loam low-rainfall crop in Kannada"
            }]
        },
        {
            "id": "C_10", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "ml",
            "description": "Malayalam: ഉയർന്ന മഴയുള്ള മലയോര പ്രദേശത്ത് അനുയോജ്യമായ വിള ഏതാണ്?",
            "turns": [{
                "turn_number": 1, "user_input": "ഉയർന്ന മഴയുള്ള മലയോര പ്രദേശത്ത് അനുയോജ്യമായ വിള ഏതാണ്?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "High rainfall hill slope crop in Malayalam"
            }]
        },
        {
            "id": "C_11", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "marwari",
            "description": "Marwari: रेतीली धोरा वाळी जमीन में बाजरी रे सिवाय कांई बीजो?",
            "turns": [{
                "turn_number": 1, "user_input": "म्हारी रेतीली धोरा वाळी जमीन में बाजरी रे सिवाय कांई बीजो? कम पाणी में कांई उपजेला?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": "bajra", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Sandy desert dunes alternatives in Marwari"
            }]
        },
        {
            "id": "C_12", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "en",
            "description": "English: I have sandy loam soil and medium borewell water in Kota. What should I sow?",
            "turns": [{
                "turn_number": 1, "user_input": "I have sandy loam soil and medium borewell water in Kota. What should I sow this season?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Kota",
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Detailed agronomy features in English"
            }]
        },
        {
            "id": "C_13", "category": "C", "domain": "CROP_RECOMMENDATION", "language": "hi",
            "description": "Hindi: NPK 120:60:40 hai, khet mein konsi fasal acchi paidawar degi?",
            "turns": [{
                "turn_number": 1, "user_input": "मेरी मिट्टी की जांच में NPK 120:60:40 आया है, खेत में कौन सी फसल सबसे अच्छी पैदावार देगी?",
                "previous_context": None, "expected_intent": "crop_recommendation",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": ["recommend_crops"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Soil test NPK ratio crop match in Hindi"
            }]
        }
    ])

    # =========================================================================
    # D. DISEASE DETECTION (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "D_01", "category": "D", "domain": "DISEASE_DETECTION", "language": "hi",
            "description": "Hindi with image: Meri fasal ke patte pe daag aa gaye hain.",
            "turns": [{
                "turn_number": 1, "user_input": "मेरी फसल के पत्तों पे अजीब से दाग आ गए हैं, क्या बीमारी है?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Image provided: execute disease detection"
            }]
        },
        {
            "id": "D_02", "category": "D", "domain": "DISEASE_DETECTION", "language": "en",
            "description": "English without image: Can you diagnose this disease on my plant?",
            "turns": [{
                "turn_number": 1, "user_input": "Can you diagnose what disease my crop has?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "LEAF_IMAGE",
                "expected_action": "NAVIGATE", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Safety rule: Do not invent disease without leaf image -> NAVIGATE to scan screen"
            }]
        },
        {
            "id": "D_03", "category": "D", "domain": "DISEASE_DETECTION", "language": "hinglish",
            "description": "Hinglish: Tamatar ke leaf pe yellow spots aa rahe hain.",
            "turns": [{
                "turn_number": 1, "user_input": "Tamatar ke leaf pe yellow spots aa rahe hain, check karo.",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "tomato", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Tomato leaf yellow spots with photo"
            }]
        },
        {
            "id": "D_04", "category": "D", "domain": "DISEASE_DETECTION", "language": "gu",
            "description": "Gujarati: કપાસના પાંદડા કાળા પડીને સુકાઈ રહ્યા છે, શું રોગ છે?",
            "turns": [{
                "turn_number": 1, "user_input": "કપાસના પાંદડા કાળા પડીને સુકાઈ રહ્યા છે, શું રોગ છે?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "cotton", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Cotton leaf blackening symptom in Gujarati"
            }]
        },
        {
            "id": "D_05", "category": "D", "domain": "DISEASE_DETECTION", "language": "mr",
            "description": "Marathi: सोयाबीनच्या पानांवर तांबेरा सारखे ठिपके दिसत आहेत.",
            "turns": [{
                "turn_number": 1, "user_input": "सोयाबीनच्या पानांवर तांबेरा सारखे ठिपके दिसत आहेत, कोणता रोग आहे हा?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "soybean", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Soybean rust symptoms in Marathi"
            }]
        },
        {
            "id": "D_06", "category": "D", "domain": "DISEASE_DETECTION", "language": "pa",
            "description": "Punjabi: ਕਣਕ ਦੇ ਪੱਤੇ ਪੀਲੇ ਪੈ ਰਹੇ ਹਨ, ਕੀ ਇਹ ਪੀਲੀ ਕੁੰਗੀ ਹੈ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਕਣਕ ਦੇ ਪੱਤੇ ਪੀਲੇ ਪੈ ਰਹੇ ਹਨ, ਕੀ ਇਹ ਪੀਲੀ ਕੁੰਗੀ ਹੈ?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Yellow rust query in Punjabi"
            }]
        },
        {
            "id": "D_07", "category": "D", "domain": "DISEASE_DETECTION", "language": "bn",
            "description": "Bengali: ধানের পাতায় বাদামী দাগ পড়েছে, প্রতিকার কী?",
            "turns": [{
                "turn_number": 1, "user_input": "ধানের পাতায় বাদামী দাগ পড়েছে, এটা কি বাদামী দাগ রোগ?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "paddy", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Brown spot disease in Bengali"
            }]
        },
        {
            "id": "D_08", "category": "D", "domain": "DISEASE_DETECTION", "language": "ta",
            "description": "Tamil: நெல் இலையில் வெண்மை நிற கோடுகள் தெரிகிறது, என்ன நோய்?",
            "turns": [{
                "turn_number": 1, "user_input": "நெல் இலையில் வெண்மை நிற கோடுகள் தெரிகிறது, என்ன நோய் என்று சொல்லுங்கள்?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "paddy", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Bacterial leaf blight symptom in Tamil"
            }]
        },
        {
            "id": "D_09", "category": "D", "domain": "DISEASE_DETECTION", "language": "te",
            "description": "Telugu: మిరప ఆకులు ముడుచుకుపోతున్నాయి, ఏం చేయాలి?",
            "turns": [{
                "turn_number": 1, "user_input": "మిరప ఆకులు ముడుచుకుపోతున్నాయి, ఇది ఏ తెగులు?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "chilli", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Chilli leaf curl virus in Telugu"
            }]
        },
        {
            "id": "D_10", "category": "D", "domain": "DISEASE_DETECTION", "language": "kn",
            "description": "Kannada: ಆಲೂಗಡ್ಡೆ ಎಲೆಗಳು ಕಪ್ಪಾಗುತ್ತಿವೆ, ರೋಗ ಪತ್ತೆ ಮಾಡಿ.",
            "turns": [{
                "turn_number": 1, "user_input": "ಆಲೂಗಡ್ಡೆ ಎಲೆಗಳು ಕಪ್ಪಾಗುತ್ತಿವೆ, ರೋಗ ಪತ್ತೆ ಮಾಡಿ.",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "potato", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Potato early/late blight in Kannada"
            }]
        },
        {
            "id": "D_11", "category": "D", "domain": "DISEASE_DETECTION", "language": "ml",
            "description": "Malayalam: ഇഞ്ചി ചെടിയുടെ ഇലകൾ മഞ്ഞളിക്കുന്നു, എന്താണ് അസുഖം?",
            "turns": [{
                "turn_number": 1, "user_input": "ഇഞ്ചി ചെടിയുടെ ഇലകൾ മഞ്ഞളിക്കുന്നു, എന്താണ് അസുഖം?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "ginger", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Ginger soft rot / yellowing in Malayalam"
            }]
        },
        {
            "id": "D_12", "category": "D", "domain": "DISEASE_DETECTION", "language": "marwari",
            "description": "Marwari: ग्वार रा पानां माथे भूरो धब्बो पड़ गयो है।",
            "turns": [{
                "turn_number": 1, "user_input": "ग्वार रा पानां माथे भूरो धब्बो पड़ गयो है, कांई रोग लाग्यो है?",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": "guar", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Guar blight symptoms in Marwari"
            }]
        },
        {
            "id": "D_13", "category": "D", "domain": "DISEASE_DETECTION", "language": "hi",
            "description": "Hindi without image: Meri fasal mein bimari hai, bina photo ke batao.",
            "turns": [{
                "turn_number": 1, "user_input": "मेरी फसल में कोई बीमारी है, बिना फोटो के बताओ क्या है।",
                "previous_context": None, "expected_intent": "disease",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "LEAF_IMAGE",
                "expected_action": "NAVIGATE", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Refuses to hallucinate without photo; safely guides to camera"
            }]
        }
    ])

    # =========================================================================
    # E. MANDI / MARKET (14 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "E_01", "category": "E", "domain": "MANDI_MARKET", "language": "hi",
            "description": "Hindi: Aaj Kota mandi mein sarson ka bhav kya hai?",
            "turns": [{
                "turn_number": 1, "user_input": "आज कोटा मंडी में सरसों का क्या भाव चल रहा है?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "mustard", "market": "Kota"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Kota", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Kota mandi mustard price in Hindi"
            }]
        },
        {
            "id": "E_02", "category": "E", "domain": "MANDI_MARKET", "language": "mr",
            "description": "Marathi: लासलगाव मार्केटमध्ये कांद्याचा आजचा दर काय आहे आणि पुढील आठवड्यात वाढेल का?",
            "turns": [{
                "turn_number": 1, "user_input": "लासलगाव मार्केटमध्ये कांद्याचा आजचा दर काय आहे आणि पुढील आठवड्यात भाव वाढेल का?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "onion", "market": "Lasalgaon"},
                "expected_time_context": {"relative_day": "NEXT_WEEK", "time_of_day": None, "timeframe": "next week"},
                "expected_location": "Lasalgaon", "expected_capabilities": ["MARKET_PRICE", "MARKET_FORECAST"],
                "expected_tool_sequence": ["get_mandi_prices", "get_price_forecast"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Current price + 7-day forecast in Lasalgaon onion"
            }]
        },
        {
            "id": "E_03", "category": "E", "domain": "MANDI_MARKET", "language": "hinglish",
            "description": "Hinglish: Wheat abhi sell karu ya hold karu agle 7 din ke liye?",
            "turns": [{
                "turn_number": 1, "user_input": "Wheat abhi sell karu ya hold karu agle 7 din ke liye? Forecast dekh ke decision do.",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": {"relative_day": "NEXT_7_DAYS", "time_of_day": None, "timeframe": "7 days"},
                "expected_location": None, "expected_capabilities": ["MARKET_PRICE", "MARKET_FORECAST"],
                "expected_tool_sequence": ["get_mandi_prices", "get_price_forecast"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Sell vs Hold decision workflow in Hinglish"
            }]
        },
        {
            "id": "E_04", "category": "E", "domain": "MANDI_MARKET", "language": "gu",
            "description": "Gujarati: રાજકોટ માર્કેટિંગ યાર્ડમાં જીરાનો ભાવ શું છે?",
            "turns": [{
                "turn_number": 1, "user_input": "રાજકોટ માર્કેટિંગ યાર્ડમાં જીરાનો ભાવ શું છે?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "cumin", "market": "Rajkot"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Rajkot", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Rajkot cumin price in Gujarati"
            }]
        },
        {
            "id": "E_05", "category": "E", "domain": "MANDI_MARKET", "language": "pa",
            "description": "Punjabi: ਖੰਨਾ ਮੰਡੀ ਵਿੱਚ ਝੋਨੇ ਦਾ ਭਾਅ ਕੀ ਚੱਲ ਰਿਹਾ ਹੈ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਖੰਨਾ ਮੰਡੀ ਵਿੱਚ ਝੋਨੇ ਦਾ ਭਾਅ ਕੀ ਚੱਲ ਰਿਹਾ ਹੈ ਅੱਜ?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "paddy", "market": "Khanna"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Khanna", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Khanna mandi paddy price in Punjabi"
            }]
        },
        {
            "id": "E_06", "category": "E", "domain": "MANDI_MARKET", "language": "bn",
            "description": "Bengali: মেদিনীপুর বাজারে আলুর আজকের পাইকারি দর কত?",
            "turns": [{
                "turn_number": 1, "user_input": "মেদিনীপুর বাজারে আলুর আজকের পাইকারি দর কত?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "potato", "market": "Medinipur"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Medinipur", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Medinipur potato wholesale price in Bengali"
            }]
        },
        {
            "id": "E_07", "category": "E", "domain": "MANDI_MARKET", "language": "ta",
            "description": "Tamil: கோயம்புத்தூர் மார்க்கெட்டில் தக்காளியின் இன்றைய விலை என்ன?",
            "turns": [{
                "turn_number": 1, "user_input": "கோயம்புத்தூர் மார்க்கெட்டில் தக்காளியின் இன்றைய விலை என்ன?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "tomato", "market": "Coimbatore"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Coimbatore", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Coimbatore tomato price in Tamil"
            }]
        },
        {
            "id": "E_08", "category": "E", "domain": "MANDI_MARKET", "language": "te",
            "description": "Telugu: గుంటూరు మిర్చి యార్డులో తేజ రకం మిర్చి ధర ఎంత?",
            "turns": [{
                "turn_number": 1, "user_input": "గుంటూరు మిర్చి యార్డులో తేజ రకం మిర్చి ధర ఎంత?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "chilli", "market": "Guntur"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Guntur", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Guntur chilli price in Telugu"
            }]
        },
        {
            "id": "E_09", "category": "E", "domain": "MANDI_MARKET", "language": "kn",
            "description": "Kannada: ಶಿವಮೊಗ್ಗ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಅಡಿಕೆ ಧಾರಣೆ ಎಷ್ಟಿದೆ?",
            "turns": [{
                "turn_number": 1, "user_input": "ಶಿವಮೊಗ್ಗ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಅಡಿಕೆ ಧಾರಣೆ ಎಷ್ಟಿದೆ?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "arecanut", "market": "Shivamogga"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Shivamogga", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Arecanut price in Kannada"
            }]
        },
        {
            "id": "E_10", "category": "E", "domain": "MANDI_MARKET", "language": "ml",
            "description": "Malayalam: കൊച്ചിയിൽ ഏലക്കായുടെ ഇന്നത്തെ വിപണി വില എത്രയാണ്?",
            "turns": [{
                "turn_number": 1, "user_input": "കൊച്ചിയിൽ ഏലക്കായുടെ ഇന്നത്തെ വിപണി വില എത്രയാണ്?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "cardamom", "market": "Kochi"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Kochi", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Cardamom price in Kochi in Malayalam"
            }]
        },
        {
            "id": "E_11", "category": "E", "domain": "MANDI_MARKET", "language": "marwari",
            "description": "Marwari: नागौर मंडी में जीरा रो कांई भाव चाल रह्यो है?",
            "turns": [{
                "turn_number": 1, "user_input": "नागौर मंडी में जीरा रो कांई भाव चाल रह्यो है? बेचना में फायदो है के?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "cumin", "market": "Nagaur"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Nagaur", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Nagaur cumin rate in Marwari"
            }]
        },
        {
            "id": "E_12", "category": "E", "domain": "MANDI_MARKET", "language": "en",
            "description": "English: Compare soybean prices between Indore and Ujjain mandis.",
            "turns": [{
                "turn_number": 1, "user_input": "Compare soybean prices between Indore and Ujjain mandis right now.",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "soybean", "market": "Indore"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Indore", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Dual mandi price comparison in English"
            }]
        },
        {
            "id": "E_13", "category": "E", "domain": "MANDI_MARKET", "language": "hi",
            "description": "Hindi: Agle 7 dino mein chana ka rate badhega ya ghatega?",
            "turns": [{
                "turn_number": 1, "user_input": "अगले 7 दिनों में चना का भाव बढ़ेगा या घटेगा?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "gram", "market": None},
                "expected_time_context": {"relative_day": "NEXT_7_DAYS", "time_of_day": None, "timeframe": "next 7 days"},
                "expected_location": None, "expected_capabilities": ["MARKET_FORECAST"],
                "expected_tool_sequence": ["get_price_forecast"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Gram price forecast trend in Hindi"
            }]
        },
        {
            "id": "E_14", "category": "E", "domain": "MANDI_MARKET", "language": "hinglish",
            "description": "Hinglish: Where can I sell my cotton near Rajkot for best rate?",
            "turns": [{
                "turn_number": 1, "user_input": "Where can I sell my cotton near Rajkot for the highest rate?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "cotton", "market": "Rajkot"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Rajkot", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Highest price market locator in English"
            }]
        }
    ])

    return convs
