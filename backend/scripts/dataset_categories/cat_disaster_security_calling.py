"""
Category F: Disaster Risk (13 conversations)
Category G: Animal / Farm Security (13 conversations)
Category H: Calling / Vobiz Telephony (14 conversations)
Languages: en, hi, hinglish, gu, mr, pa, bn, ta, te, kn, ml, marwari
"""

def get_disaster_security_calling_conversations():
    convs = []

    # =========================================================================
    # F. DISASTER RISK (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "F_01", "category": "F", "domain": "DISASTER_RISK", "language": "hi",
            "description": "Hindi: Barish bahut tez hone wali hai, khet ke liye flood ka khatra hai kya?",
            "turns": [{
                "turn_number": 1, "user_input": "बारिश बहुत तेज होने वाली है, खेत के लिए बाढ़ या जलभराव का खतरा है क्या?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Flood risk assessment in Hindi"
            }]
        },
        {
            "id": "F_02", "category": "F", "domain": "DISASTER_RISK", "language": "hinglish",
            "description": "Hinglish: Cyclone ka danger kitna hai Gujarat coastal area mein?",
            "turns": [{
                "turn_number": 1, "user_input": "Cyclone ka danger kitna hai Gujarat coastal area mein? Crop ko protect kaise karu?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Gujarat",
                "expected_capabilities": ["DISASTER_RISK", "RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Cyclone risk + crop protection advisory in Hinglish"
            }]
        },
        {
            "id": "F_03", "category": "F", "domain": "DISASTER_RISK", "language": "gu",
            "description": "Gujarati: દરિયાકાંઠાના વિસ્તારમાં વાવાઝોડાનું જોખમ કેટલું છે?",
            "turns": [{
                "turn_number": 1, "user_input": "દરિયાકાંઠાના વિસ્તારમાં વાવાઝોડાનું જોખમ કેટલું છે? ખેતર માટે શું તકેદારી રાખવી?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Cyclone risk in coastal Gujarat"
            }]
        },
        {
            "id": "F_04", "category": "F", "domain": "DISASTER_RISK", "language": "mr",
            "description": "Marathi: मराठवाड्यात दुष्काळाचा धोका किती आहे या हंगामात?",
            "turns": [{
                "turn_number": 1, "user_input": "मराठवाड्यात दुष्काळाचा धोका किती आहे या हंगामात?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Marathwada",
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Drought disaster risk in Marathi"
            }]
        },
        {
            "id": "F_05", "category": "F", "domain": "DISASTER_RISK", "language": "pa",
            "description": "Punjabi: ਕੀ ਸਾਡੇ ਇਲਾਕੇ ਵਿੱਚ ਹੜ੍ਹ ਦਾ ਕੋਈ ਖ਼ਤਰਾ ਹੈ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਕੀ ਸਾਡੇ ਇਲਾਕੇ ਵਿੱਚ ਹੜ੍ਹ ਦਾ ਕੋਈ ਖ਼ਤਰਾ ਹੈ? ਦਰਿਆ ਵਿੱਚ ਪਾਣੀ ਵੱਧ ਰਿਹਾ ਹੈ।",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "River flood risk in Punjabi"
            }]
        },
        {
            "id": "F_06", "category": "F", "domain": "DISASTER_RISK", "language": "bn",
            "description": "Bengali: সুন্দরবন অঞ্চলে কি আগামী ২৪ ঘণ্টায় ঘূর্ণিঝড়ের সতর্কতা আছে?",
            "turns": [{
                "turn_number": 1, "user_input": "সুন্দরবন অঞ্চলে কি আগামী ২৪ ঘণ্টায় ঘূর্ণিঝড়ের সতর্কতা আছে?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "24 hours"},
                "expected_location": "Sundarbans", "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Cyclone alert in Bengali"
            }]
        },
        {
            "id": "F_07", "category": "F", "domain": "DISASTER_RISK", "language": "ta",
            "description": "Tamil: காவிரி டெல்டா பகுதியில் வெள்ள அபாயம் உள்ளதா?",
            "turns": [{
                "turn_number": 1, "user_input": "காவிரி டெல்டா பகுதியில் வெள்ள அபாயம் உள்ளதா?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Cauvery Delta",
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Delta flood alert in Tamil"
            }]
        },
        {
            "id": "F_08", "category": "F", "domain": "DISASTER_RISK", "language": "te",
            "description": "Telugu: భారీ తుఫాను వల్ల పంటలకు ఏమైనా ప్రమాదం ఉందా?",
            "turns": [{
                "turn_number": 1, "user_input": "భారీ తుఫాను వల్ల పంటలకు ఏమైనా ప్రమాదం ఉందా?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Cyclone danger to crops in Telugu"
            }]
        },
        {
            "id": "F_09", "category": "F", "domain": "DISASTER_RISK", "language": "kn",
            "description": "Kannada: ಕರಾವಳಿ ಭಾಗದಲ್ಲಿ ಭಾರೀ ಗಾಳಿ-ಮಳೆಯಿಂದ ಪ್ರವಾಹದ ಅಪಾಯವಿದೆಯೇ?",
            "turns": [{
                "turn_number": 1, "user_input": "ಕರಾವಳಿ ಭಾಗದಲ್ಲಿ ಭಾರೀ ಗಾಳಿ-ಮಳೆಯಿಂದ ಪ್ರವಾಹದ ಅಪಾಯವಿದೆಯೇ?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Coastal flash flood risk in Kannada"
            }]
        },
        {
            "id": "F_10", "category": "F", "domain": "DISASTER_RISK", "language": "ml",
            "description": "Malayalam: ഉരുൾപൊട്ടലിനും വെള്ളപ്പൊക്കത്തിനും സാധ്യതയുണ്ടോ?",
            "turns": [{
                "turn_number": 1, "user_input": "ഉരുൾപൊട്ടലിനും വെള്ളപ്പൊക്കത്തിനും സാധ്യതയുണ്ടോ? ശക്തമായ മഴ പെയ്യുന്നു.",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Landslide and flood risk during heavy rains in Malayalam"
            }]
        },
        {
            "id": "F_11", "category": "F", "domain": "DISASTER_RISK", "language": "marwari",
            "description": "Marwari: काल आंधी-तूफान रो कोई मोटो खतरो है के?",
            "turns": [{
                "turn_number": 1, "user_input": "काल आंधी-तूफान रो कोई मोटो खतरो है के? फसल ढांपणी पड़ेला के?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": None, "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Sandstorm/storm danger in Marwari"
            }]
        },
        {
            "id": "F_12", "category": "F", "domain": "DISASTER_RISK", "language": "en",
            "description": "English: Is there an extreme heatwave risk for vegetables in Udaipur this weekend?",
            "turns": [{
                "turn_number": 1, "user_input": "Is there an extreme heatwave or drought risk for vegetables in Udaipur this weekend?",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": "vegetables", "market": None},
                "expected_time_context": {"relative_day": "THIS_WEEK", "time_of_day": None, "timeframe": "weekend"},
                "expected_location": "Udaipur", "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Heatwave disaster prediction in English"
            }]
        },
        {
            "id": "F_13", "category": "F", "domain": "DISASTER_RISK", "language": "hi",
            "description": "Hindi: Olabari (hailstorm) aane ki koi sambhavna hai kya?",
            "turns": [{
                "turn_number": 1, "user_input": "ओलावृष्टि होने की कोई संभावना है क्या? गेहूं की पकी फसल खड़ी है।",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISASTER_RISK"],
                "expected_tool_sequence": ["assess_disaster_risk"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Hailstorm hazard on ripe standing crop in Hindi"
            }]
        }
    ])

    # =========================================================================
    # G. ANIMAL / FARM SECURITY (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "G_01", "category": "G", "domain": "FARM_SECURITY", "language": "hi",
            "description": "Hindi: Nilgai mere khet mein ghus rahi hain, kaise rokun?",
            "turns": [{
                "turn_number": 1, "user_input": "नीलगाय मेरे खेत में घुसकर फसल बर्बाद कर रही हैं, कैसे रोकूं?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Nilgai bluebull deterrence in Hindi"
            }]
        },
        {
            "id": "G_02", "category": "G", "domain": "FARM_SECURITY", "language": "hinglish",
            "description": "Hinglish: Wild boar raat ko khet kharab kar rahe hain. IoT sensor alert check karo.",
            "turns": [{
                "turn_number": 1, "user_input": "Wild boar raat ko khet kharab kar rahe hain. Farm security sensors ka alert status check karo.",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": "NIGHT", "timeframe": "night"},
                "expected_location": None, "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Wild boar security monitoring in Hinglish"
            }]
        },
        {
            "id": "G_03", "category": "G", "domain": "FARM_SECURITY", "language": "gu",
            "description": "Gujarati: રાત્રે ખેતરમાં જંગલી ભૂંડ આવે છે, સેન્સર એલર્ટ આપશે?",
            "turns": [{
                "turn_number": 1, "user_input": "રાત્રે ખેતરમાં જંગલી ભૂંડ આવે છે, સેન્સર સિસ્ટમ ચાલુ છે કે નહીં?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Wild boar sensor check in Gujarati"
            }]
        },
        {
            "id": "G_04", "category": "G", "domain": "FARM_SECURITY", "language": "mr",
            "description": "Marathi: रात्रीच्या वेळी रानडुक्कर पिकांचे नुकसान करत आहेत, काही उपाय आहे का?",
            "turns": [{
                "turn_number": 1, "user_input": "रात्रीच्या वेळी रानडुक्कर पिकांचे नुकसान करत आहेत, सुरक्षा प्रणाली काय सांगते?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Wild boar damage in Marathi"
            }]
        },
        {
            "id": "G_05", "category": "G", "domain": "FARM_SECURITY", "language": "pa",
            "description": "Punjabi: ਅਵਾਰਾ ਪਸ਼ੂ ਖੇਤ ਵਿੱਚ ਵੜ ਰਹੇ ਹਨ, ਸੁਰੱਖਿਆ ਸਿਸਟਮ ਕੀ ਕਹਿੰਦਾ ਹੈ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਅਵਾਰਾ ਪਸ਼ੂ ਖੇਤ ਵਿੱਚ ਵੜ ਰਹੇ ਹਨ, ਸੁਰੱਖਿਆ ਸਿਸਟਮ ਨੇ ਕੋਈ ਜਾਨਵਰ ਫੜਿਆ?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Stray cattle sensor check in Punjabi"
            }]
        },
        {
            "id": "G_06", "category": "G", "domain": "FARM_SECURITY", "language": "bn",
            "description": "Bengali: রাতে বুনো শুয়োর জমিতে ঢুকছে, অ্যালার্ম কি কাজ করছে?",
            "turns": [{
                "turn_number": 1, "user_input": "রাতে বুনো শুয়োর জমিতে ঢুকছে, খামারের নিরাপত্তা অ্যালার্ম কি কাজ করছে?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Wild boar sensor alarm check in Bengali"
            }]
        },
        {
            "id": "G_07", "category": "G", "domain": "FARM_SECURITY", "language": "ta",
            "description": "Tamil: காட்டுப்பன்றிகள் இரவில் பயிர்களை அழிக்கின்றன, பாதுகாப்பு எச்சரிக்கை உள்ளதா?",
            "turns": [{
                "turn_number": 1, "user_input": "காட்டுப்பன்றிகள் இரவில் பயிர்களை அழிக்கின்றன, பண்ணை பாதுகாப்பு நிலை என்ன?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Wild boar farm security in Tamil"
            }]
        },
        {
            "id": "G_08", "category": "G", "domain": "FARM_SECURITY", "language": "te",
            "description": "Telugu: అడవి పందులు పొలంలోకి రాకుండా సెన్సార్ ఏదైనా హెచ్చరిక ఇచ్చిందా?",
            "turns": [{
                "turn_number": 1, "user_input": "అడవి పందులు పొలంలోకి రాకుండా సెన్సార్ ఏదైనా హెచ్చరిక ఇచ్చిందా?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Wild boar sensor alert check in Telugu"
            }]
        },
        {
            "id": "G_09", "category": "G", "domain": "FARM_SECURITY", "language": "kn",
            "description": "Kannada: ಕಾಡು ಪ್ರಾಣಿಗಳು ಹೊಲಕ್ಕೆ ನುಗ್ಗುತ್ತಿವೆ, ಸಿಸ್ಟಮ್ ಪತ್ತೆ ಹಚ್ಚಿದೆಯೇ?",
            "turns": [{
                "turn_number": 1, "user_input": "ಕಾಡು ಪ್ರಾಣಿಗಳು ಹೊಲಕ್ಕೆ ನುಗ್ಗುತ್ತಿವೆ, ಸಿಸ್ಟಮ್ ಪತ್ತೆ ಹಚ್ಚಿದೆಯೇ?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Wild animal perimeter breach in Kannada"
            }]
        },
        {
            "id": "G_10", "category": "G", "domain": "FARM_SECURITY", "language": "ml",
            "description": "Malayalam: കാട്ടുപന്നികൾ തോട്ടത്തിൽ കയറുന്നുണ്ടോ എന്ന് സെൻസർ പരിശോധിക്ക്.",
            "turns": [{
                "turn_number": 1, "user_input": "കാട്ടുപന്നികൾ തോട്ടത്തിൽ കയറുന്നുണ്ടോ എന്ന് സെൻസർ പരിശോധിക്ക്.",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Plantation wild boar intrusion in Malayalam"
            }]
        },
        {
            "id": "G_11", "category": "G", "domain": "FARM_SECURITY", "language": "marwari",
            "description": "Marwari: रोझड़ा रात ने खेत में आवे है, बाड़ माथे कंटीला तार लगाऊं के?",
            "turns": [{
                "turn_number": 1, "user_input": "रोझड़ा रात ने खेत में आवे है, कीकर भगावां? कदी जानवर आयो है के?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Bluebull intrusion check in Marwari"
            }]
        },
        {
            "id": "G_12", "category": "G", "domain": "FARM_SECURITY", "language": "en",
            "description": "English: Can the farm security system detect if cattle crossed the east perimeter?",
            "turns": [{
                "turn_number": 1, "user_input": "Can the farm security system detect if any animal crossed the east perimeter boundary?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Boundary intrusion query in English"
            }]
        },
        {
            "id": "G_13", "category": "G", "domain": "FARM_SECURITY", "language": "hi",
            "description": "Hindi: Pichhle 24 ghante mein khet mein koi janwar aaya kya?",
            "turns": [{
                "turn_number": 1, "user_input": "पिछले 24 घंटे में खेत की बाउंड्री पर कोई जानवर आया था क्या?",
                "previous_context": None, "expected_intent": "farm_security",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "24 hours"},
                "expected_location": None, "expected_capabilities": ["FARM_SECURITY"],
                "expected_tool_sequence": ["detect_animal_intrusion"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "24-hour perimeter security audit in Hindi"
            }]
        }
    ])

    # =========================================================================
    # H. CALLING / VOBIZ TELEPHONY (14 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "H_01", "category": "H", "domain": "CALLING", "language": "hi",
            "description": "Hindi with number: Mujhe kisan expert ko call lagana hai +919876543210 pe.",
            "turns": [{
                "turn_number": 1, "user_input": "मुझे किसान एक्सपर्ट से बात करनी है, मेरे नंबर +919876543210 पर तुरंत कॉल करो।",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Direct telephony dispatch with valid E.164 phone"
            }]
        },
        {
            "id": "H_02", "category": "H", "domain": "CALLING", "language": "en",
            "description": "English without number: Call the agriculture officer for me.",
            "turns": [{
                "turn_number": 1, "user_input": "Call the agriculture officer for me immediately.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": [], "expected_required_input": "PHONE_NUMBER",
                "expected_action": "REQUEST_INPUT", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Missing phone number safety gate -> REQUEST_INPUT"
            }]
        },
        {
            "id": "H_03", "category": "H", "domain": "CALLING", "language": "hinglish",
            "description": "Hinglish: Expert se phone pe baat karwao, number 9876543210 hai.",
            "turns": [{
                "turn_number": 1, "user_input": "Expert se phone pe baat karwao, mera number 9876543210 hai.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "10-digit Indian phone normalized to +91 and dispatched"
            }]
        },
        {
            "id": "H_04", "category": "H", "domain": "CALLING", "language": "gu",
            "description": "Gujarati: કૃષિ અધિકારી સાથે વાત કરવા માટે ફોન કરો, નંબર +919876543210.",
            "turns": [{
                "turn_number": 1, "user_input": "કૃષિ અધિકારી સાથે વાત કરવા માટે ફોન કરો, મારો નંબર +919876543210 છે.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Outbound Vobiz call in Gujarati"
            }]
        },
        {
            "id": "H_05", "category": "H", "domain": "CALLING", "language": "mr",
            "description": "Marathi: मला कृषी तज्ञांशी बोलायचे आहे, +919876543210 वर कॉल लावा.",
            "turns": [{
                "turn_number": 1, "user_input": "मला कृषी तज्ञांशी बोलायचे आहे, +919876543210 वर कॉल लावा.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Agri expert call in Marathi"
            }]
        },
        {
            "id": "H_06", "category": "H", "domain": "CALLING", "language": "pa",
            "description": "Punjabi: ਮੈਨੂੰ ਖੇਤੀਬਾੜੀ ਅਫ਼ਸਰ ਨਾਲ ਗੱਲ ਕਰਵਾਓ, ਮੇਰੇ ਫੋਨ +919876543210 'ਤੇ ਕਾਲ ਕਰੋ।",
            "turns": [{
                "turn_number": 1, "user_input": "ਮੈਨੂੰ ਖੇਤੀਬਾੜੀ ਅਫ਼ਸਰ ਨਾਲ ਗੱਲ ਕਰਵਾਓ, ਮੇਰੇ ਫੋਨ +919876543210 'ਤੇ ਕਾਲ ਕਰੋ।",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Agri officer call in Punjabi"
            }]
        },
        {
            "id": "H_07", "category": "H", "domain": "CALLING", "language": "bn",
            "description": "Bengali: কৃষি বিজ্ঞানীদের সাথে কথা বলতে চাই, +919876543210 নম্বরে ফোন করুন।",
            "turns": [{
                "turn_number": 1, "user_input": "কৃষি বিজ্ঞানীদের সাথে কথা বলতে চাই, +919876543210 নম্বরে ফোন করুন।",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Bengali telephony request"
            }]
        },
        {
            "id": "H_08", "category": "H", "domain": "CALLING", "language": "ta",
            "description": "Tamil: விவசாய அதிகாரியிடம் பேச எனக்கு +919876543210 எண்ணிற்கு அழைக்கவும்.",
            "turns": [{
                "turn_number": 1, "user_input": "விவசாய அதிகாரியிடம் பேச எனக்கு +919876543210 எண்ணிற்கு அழைக்கவும்.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Tamil telephony invocation"
            }]
        },
        {
            "id": "H_09", "category": "H", "domain": "CALLING", "language": "te",
            "description": "Telugu: వ్యవసాయ అధికారికి కాల్ చేయండి.",
            "turns": [{
                "turn_number": 1, "user_input": "వ్యవసాయ అధికారికి కాల్ చేయండి.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": [], "expected_required_input": "PHONE_NUMBER",
                "expected_action": "REQUEST_INPUT", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Telugu call request missing phone number"
            }]
        },
        {
            "id": "H_10", "category": "H", "domain": "CALLING", "language": "kn",
            "description": "Kannada: ತುರ್ತಾಗಿ ಕೃಷಿ ಅಧಿಕಾರಿಗೆ ಕರೆ ಮಾಡಿ, ಸಂಖ್ಯೆ +919876543210.",
            "turns": [{
                "turn_number": 1, "user_input": "ತುರ್ತಾಗಿ ಕೃಷಿ ಅಧಿಕಾರಿಗೆ ಕರೆ ಮಾಡಿ, ಸಂಖ್ಯೆ +919876543210.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Emergency calling in Kannada"
            }]
        },
        {
            "id": "H_11", "category": "H", "domain": "CALLING", "language": "ml",
            "description": "Malayalam: അടിയന്തിരമായി കാർഷിക ഓഫീസറെ ബന്ധപ്പെടണം, +919876543210 ലേക്ക് വിളിക്കുക.",
            "turns": [{
                "turn_number": 1, "user_input": "അടിയന്തിരമായി കാർഷിക ഓഫീസറെ ബന്ധപ്പെടണം, +919876543210 ലേക്ക് വിളിക്കുക.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Emergency Malayalam call"
            }]
        },
        {
            "id": "H_12", "category": "H", "domain": "CALLING", "language": "marwari",
            "description": "Marwari: म्हारे फोन नंबर +919876543210 माथे कॉल करो सा।",
            "turns": [{
                "turn_number": 1, "user_input": "म्हारा फोन नंबर +919876543210 माथे कॉल करो सा, खेत री समस्या समझानी है।",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Marwari calling invocation with honorific 'sa'"
            }]
        },
        {
            "id": "H_13", "category": "H", "domain": "CALLING", "language": "hi",
            "description": "Hindi without number: Phone kar do mujhe turant.",
            "turns": [{
                "turn_number": 1, "user_input": "फोन कर दो मुझे तुरंत।",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": [], "expected_required_input": "PHONE_NUMBER",
                "expected_action": "REQUEST_INPUT", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Missing phone number prompt -> REQUEST_INPUT"
            }]
        },
        {
            "id": "H_14", "category": "H", "domain": "CALLING", "language": "en",
            "description": "English: The disaster risk is critical, initiate an urgent voice call to +919876543210.",
            "turns": [{
                "turn_number": 1, "user_input": "Disaster risk is critical, initiate an urgent voice call to +919876543210 immediately.",
                "previous_context": None, "expected_intent": "calling",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": ["calling_tool"], "expected_required_input": None,
                "expected_action": "CALL", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Critical escalation call trigger in English"
            }]
        }
    ])

    return convs
