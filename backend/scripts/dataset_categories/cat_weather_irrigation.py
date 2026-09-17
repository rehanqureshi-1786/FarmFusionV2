"""
Category A: Weather (13 conversations)
Category B: Smart Irrigation (14 conversations)
Languages: en, hi, hinglish, gu, mr, pa, bn, ta, te, kn, ml, marwari
"""

def get_weather_irrigation_conversations():
    convs = []

    # =========================================================================
    # A. WEATHER (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "A_01", "category": "A", "domain": "WEATHER", "language": "hi",
            "description": "Hindi: Kal mausam kaisa rahega Jaipur mein?",
            "turns": [{
                "turn_number": 1, "user_input": "कल जयपुर में मौसम कैसा रहेगा?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Jaipur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Tomorrow forecast check in Devanagari Hindi"
            }]
        },
        {
            "id": "A_02", "category": "A", "domain": "WEATHER", "language": "hinglish",
            "description": "Hinglish: Is week rain ka kya scene hai Kota mein?",
            "turns": [{
                "turn_number": 1, "user_input": "Is week rain ka kya scene hai Kota mein? Barish aayegi kya?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "THIS_WEEK", "time_of_day": None, "timeframe": "week"},
                "expected_location": "Kota", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Week-long rain query in Hinglish slang"
            }]
        },
        {
            "id": "A_03", "category": "A", "domain": "WEATHER", "language": "gu",
            "description": "Gujarati: આવતીકાલે બપોરે રાજકોટમાં તાપમાન કેટલું રહેશે?",
            "turns": [{
                "turn_number": 1, "user_input": "આવતીકાલે બપોરે રાજકોટમાં તાપમાન કેટલું રહેશે?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": "AFTERNOON", "timeframe": "tomorrow afternoon"},
                "expected_location": "Rajkot", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Afternoon temperature query in Gujarati"
            }]
        },
        {
            "id": "A_04", "category": "A", "domain": "WEATHER", "language": "pa",
            "description": "Punjabi: ਕੱਲ੍ਹ ਸਵੇਰੇ ਲੁਧਿਆਣੇ ਵਿੱਚ ਤੇਜ਼ ਹਵਾ ਚੱਲੇਗੀ ਕੀ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਕੱਲ੍ਹ ਸਵੇਰੇ ਲੁਧਿਆਣੇ ਵਿੱਚ ਤੇਜ਼ ਹਵਾ ਚੱਲੇਗੀ ਕੀ?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": "MORNING", "timeframe": "tomorrow morning"},
                "expected_location": "Ludhiana", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Morning wind query in Gurmukhi Punjabi"
            }]
        },
        {
            "id": "A_05", "category": "A", "domain": "WEATHER", "language": "mr",
            "description": "Marathi: परवा नाशिकमध्ये ढगाळ हवामान राहील की कडक ऊन पडेल?",
            "turns": [{
                "turn_number": 1, "user_input": "परवा नाशिकमध्ये ढगाळ हवामान राहील की कडक ऊन पडेल?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "DAY_AFTER_TOMORROW", "time_of_day": None, "timeframe": "day after tomorrow"},
                "expected_location": "Nashik", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Day after tomorrow cloud/sun question in Marathi"
            }]
        },
        {
            "id": "A_06", "category": "A", "domain": "WEATHER", "language": "bn",
            "description": "Bengali: আগামী তিন দিন বর্ধমানে কি ভারী বৃষ্টির সম্ভাবনা আছে?",
            "turns": [{
                "turn_number": 1, "user_input": "আগামী তিন দিন বর্ধমানে কি ভারী বৃষ্টির সম্ভাবনা আছে?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "NEXT_3_DAYS", "time_of_day": None, "timeframe": "next 3 days"},
                "expected_location": "Bardhaman", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "3-day heavy rain outlook in Bengali"
            }]
        },
        {
            "id": "A_07", "category": "A", "domain": "WEATHER", "language": "ta",
            "description": "Tamil: தஞ்சாவூரில் நாளை மாலை மழை பெய்யுமா?",
            "turns": [{
                "turn_number": 1, "user_input": "தஞ்சாவூரில் நாளை மாலை மழை பெய்யுமா?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": "EVENING", "timeframe": "tomorrow evening"},
                "expected_location": "Thanjavur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Tomorrow evening rain in Tamil"
            }]
        },
        {
            "id": "A_08", "category": "A", "domain": "WEATHER", "language": "te",
            "description": "Telugu: వరంగల్‌లో ఈ రాత్రి వర్షం పడే అవకాశం ఉందా?",
            "turns": [{
                "turn_number": 1, "user_input": "వరంగల్‌లో ఈ రాత్రి వర్షం పడే అవకాశం ఉందా?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": "NIGHT", "timeframe": "tonight"},
                "expected_location": "Warangal", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Tonight rain in Telugu"
            }]
        },
        {
            "id": "A_09", "category": "A", "domain": "WEATHER", "language": "kn",
            "description": "Kannada: ಹಾಸನದಲ್ಲಿ ಮುಂದಿನ 7 ದಿನಗಳ ಹವಾಮಾನ ವರದಿ ನೀಡಿ.",
            "turns": [{
                "turn_number": 1, "user_input": "ಹಾಸನದಲ್ಲಿ ಮುಂದಿನ 7 ದಿನಗಳ ಹವಾಮಾನ ವರದಿ ನೀಡಿ.", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "NEXT_7_DAYS", "time_of_day": None, "timeframe": "next 7 days"},
                "expected_location": "Hassan", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "7-day forecast in Kannada"
            }]
        },
        {
            "id": "A_10", "category": "A", "domain": "WEATHER", "language": "ml",
            "description": "Malayalam: വയനാട്ടിൽ നാളെ കനത്ത മഴ പെയ്യാൻ സാധ്യതയുണ്ടോ?",
            "turns": [{
                "turn_number": 1, "user_input": "വയനാട്ടിൽ നാളെ കനത്ത മഴ പെയ്യാൻ സാധ്യതയുണ്ടോ?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Wayanad", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Wayanad heavy rain query in Malayalam"
            }]
        },
        {
            "id": "A_11", "category": "A", "domain": "WEATHER", "language": "marwari",
            "description": "Marwari: काल जोधपुर कानी मींह बरसेगा के?",
            "turns": [{
                "turn_number": 1, "user_input": "काल जोधपुर कानी मींह बरसेगा के? खेत में काम करणो है।", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Jodhpur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Marwari dialect weather inquiry"
            }]
        },
        {
            "id": "A_12", "category": "A", "domain": "WEATHER", "language": "en",
            "description": "English: Should I harvest my wheat tomorrow considering the weather in Karnal?",
            "turns": [{
                "turn_number": 1, "user_input": "Should I harvest my wheat tomorrow considering the weather in Karnal?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Karnal", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Weather-based harvest timing inquiry in English"
            }]
        },
        {
            "id": "A_13", "category": "A", "domain": "WEATHER", "language": "hi",
            "description": "Hindi: Agle teen din dhoop niklegi ya badal chhayenge Udaipur mein?",
            "turns": [{
                "turn_number": 1, "user_input": "अगले तीन दिन धूप निकलेगी या बादल छाये रहेंगे उदयपुर में?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "NEXT_3_DAYS", "time_of_day": None, "timeframe": "next 3 days"},
                "expected_location": "Udaipur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Multi-day cloud cover inquiry in Hindi"
            }]
        }
    ])

    # =========================================================================
    # B. SMART IRRIGATION (14 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "B_01", "category": "B", "domain": "SMART_IRRIGATION", "language": "hi",
            "description": "Hindi: Abhi paani dena chahiye ya mitti mein moisture kaafi hai?",
            "turns": [{
                "turn_number": 1, "user_input": "गेहूं में अभी पानी देना चाहिए या मिट्टी में नमी काफी है?", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "now"},
                "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Immediate soil moisture irrigation decision for wheat"
            }]
        },
        {
            "id": "B_02", "category": "B", "domain": "SMART_IRRIGATION", "language": "hinglish",
            "description": "Hinglish: Kal irrigation karu kya? Barish ka forecast bhi dekh lena Jaipur mein.",
            "turns": [{
                "turn_number": 1, "user_input": "Kal irrigation karu kya? Barish ka forecast bhi dekh lena Jaipur mein.", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Jaipur", "expected_capabilities": ["WEATHER", "IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Weather + Irrigation compound decision in Hinglish"
            }]
        },
        {
            "id": "B_03", "category": "B", "domain": "SMART_IRRIGATION", "language": "gu",
            "description": "Gujarati: કપાસમાં ટપક પદ્ધતિથી પાણી ક્યારે આપવું યોગ્ય રહેશે?",
            "turns": [{
                "turn_number": 1, "user_input": "કપાસમાં ટપક પદ્ધતિથી પાણી ક્યારે આપવું યોગ્ય રહેશે?", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "cotton", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "optimal"},
                "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Drip irrigation timing for cotton in Gujarati"
            }]
        },
        {
            "id": "B_04", "category": "B", "domain": "SMART_IRRIGATION", "language": "mr",
            "description": "Marathi: कांद्याच्या पिकाला पाणी कधी देणे सर्वात योग्य ठरेल?",
            "turns": [{
                "turn_number": 1, "user_input": "कांद्याच्या पिकाला पाणी कधी देणे सर्वात योग्य ठरेल? जमीन कोरडी वाटतेय.", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "onion", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Onion irrigation timing on dry soil in Marathi"
            }]
        },
        {
            "id": "B_05", "category": "B", "domain": "SMART_IRRIGATION", "language": "pa",
            "description": "Punjabi: ਝੋਨੇ ਨੂੰ ਪਾਣੀ ਕੱਲ੍ਹ ਲਾਵਾਂ ਜਾਂ ਮੀਂਹ ਪੈਣ ਦੀ ਉਡੀਕ ਕਰਾਂ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਝੋਨੇ ਨੂੰ ਪਾਣੀ ਕੱਲ੍ਹ ਲਾਵਾਂ ਜਾਂ ਮੀਂਹ ਪੈਣ ਦੀ ਉਡੀਕ ਕਰਾਂ?", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "paddy", "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": None, "expected_capabilities": ["WEATHER", "IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Paddy irrigation vs rain wait in Punjabi"
            }]
        },
        {
            "id": "B_06", "category": "B", "domain": "SMART_IRRIGATION", "language": "bn",
            "description": "Bengali: আলুর জমিতে সেচ আজ দেওয়া উচিত না কি মাটি বেশি ভেজা?",
            "turns": [{
                "turn_number": 1, "user_input": "আলুর জমিতে সেচ আজ দেওয়া উচিত না কি মাটি বেশি ভেজা?", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "potato", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Potato field moisture and irrigation test in Bengali"
            }]
        },
        {
            "id": "B_07", "category": "B", "domain": "SMART_IRRIGATION", "language": "ta",
            "description": "Tamil: கரும்பு பயிருக்கு இன்று தண்ணீர் பாய்ச்சலாமா?",
            "turns": [{
                "turn_number": 1, "user_input": "கரும்பு பயிருக்கு இன்று தண்ணீர் பாய்ச்சலாமா? மண்ணில் ஈரப்பதம் குறைவு.", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "sugarcane", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Sugarcane irrigation in Tamil"
            }]
        },
        {
            "id": "B_08", "category": "B", "domain": "SMART_IRRIGATION", "language": "te",
            "description": "Telugu: మిరప తోటకు రేపు నీరు పెట్టవచ్చా లేదా వర్షం పడుతుందా?",
            "turns": [{
                "turn_number": 1, "user_input": "మిరప తోటకు రేపు నీరు పెట్టవచ్చా లేదా వర్షం పడుతుందా?", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "chilli", "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": None, "expected_capabilities": ["WEATHER", "IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Chilli irrigation with rain contingency in Telugu"
            }]
        },
        {
            "id": "B_09", "category": "B", "domain": "SMART_IRRIGATION", "language": "kn",
            "description": "Kannada: ರಾಗಿ ಬೆಳೆಗೆ ಈಗ ನೀರುಣಿಸಬೇಕೇ?",
            "turns": [{
                "turn_number": 1, "user_input": "ರಾಗಿ ಬೆಳೆಗೆ ಈಗ ನೀರುಣಿಸಬೇಕೇ? ಭೂಮಿ ಒಣಗಿದಂತೆ ಕಾಣುತ್ತಿದೆ.", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "ragi", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "now"},
                "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Finger millet irrigation in Kannada"
            }]
        },
        {
            "id": "B_10", "category": "B", "domain": "SMART_IRRIGATION", "language": "ml",
            "description": "Malayalam: കുരുമുളകിന് ഇന്ന് നനയ്ക്കേണ്ടതുണ്ടോ?",
            "turns": [{
                "turn_number": 1, "user_input": "കുരുമുളകിന് ഇന്ന് നനയ്ക്കേണ്ടതുണ്ടോ? മഴ പെയ്യാൻ സാധ്യതയുണ്ടോ?", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "pepper", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": None, "expected_capabilities": ["WEATHER", "IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Pepper watering vs rain risk in Malayalam"
            }]
        },
        {
            "id": "B_11", "category": "B", "domain": "SMART_IRRIGATION", "language": "marwari",
            "description": "Marwari: बाजरी में अबार पाणी देणो ठीक रेवेला के?",
            "turns": [{
                "turn_number": 1, "user_input": "बाजरी में अबार पाणी देणो ठीक रेवेला के? टीबा सूका पड़्या है।", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "bajra", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "now"},
                "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Bajra watering in sandy dunes in Marwari"
            }]
        },
        {
            "id": "B_12", "category": "B", "domain": "SMART_IRRIGATION", "language": "en",
            "description": "English: How many hours should I run the drip system for my tomato field today?",
            "turns": [{
                "turn_number": 1, "user_input": "How many hours should I run the drip system for my tomato field today?", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "tomato", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Drip duration for tomato in English"
            }]
        },
        {
            "id": "B_13", "category": "B", "domain": "SMART_IRRIGATION", "language": "hi",
            "description": "Hindi: Kal baarish bhi hai aur mitti dry bhi lag rahi hai, paani du?",
            "turns": [{
                "turn_number": 1, "user_input": "कल बारिश भी है और मिट्टी सूखी भी लग रही है, क्या मुझे पानी देना चाहिए?", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": None, "expected_capabilities": ["WEATHER", "IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Crucial prompt test: WEATHER + IRRIGATION combination"
            }]
        },
        {
            "id": "B_14", "category": "B", "domain": "SMART_IRRIGATION", "language": "hinglish",
            "description": "Hinglish: Is the soil already too wet to irrigate mustard in Alwar?",
            "turns": [{
                "turn_number": 1, "user_input": "Is the soil already too wet to irrigate mustard in Alwar? Check moisture.", "previous_context": None,
                "expected_intent": "irrigation", "expected_entities": {"crop": "mustard", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Alwar", "expected_capabilities": ["IRRIGATION"],
                "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Moisture sufficiency inquiry in Hinglish"
            }]
        }
    ])

    return convs
