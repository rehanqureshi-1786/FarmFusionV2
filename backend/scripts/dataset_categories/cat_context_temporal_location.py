"""
Category L: Multi-Turn Context (13 multi-turn conversations, 2 to 4 turns each)
Category M: Temporal Questions (13 conversations)
Category N: Location Questions (14 conversations)
Languages: en, hi, hinglish, gu, mr, pa, bn, ta, te, kn, ml, marwari
"""

def get_context_temporal_location_conversations():
    convs = []

    # =========================================================================
    # L. MULTI-TURN CONTEXT (13 MULTI-TURN CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "L_01", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "hi",
            "description": "Hindi 2-turn: Turn 1 sets crop (Wheat), Turn 2 asks about irrigation for it.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "मैं अपने 5 एकड़ खेत में गेहूं उगा रहा हूँ।",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "wheat", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 1: Establishes active_crop=wheat"
                },
                {
                    "turn_number": 2, "user_input": "इसके लिए कल क्या मुझे पानी देना चाहिए?",
                    "previous_context": {"crop": "wheat"}, "expected_intent": "irrigation",
                    "expected_entities": {"crop": "wheat", "market": None},
                    "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                    "expected_location": None, "expected_capabilities": ["IRRIGATION"],
                    "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 2: 'इसके लिए' successfully inherits wheat; correctly routes to IRRIGATION"
                }
            ]
        },
        {
            "id": "L_02", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "hinglish",
            "description": "Hinglish 2-turn: Turn 1 sets farm location (Jaipur), Turn 2 asks weather without repeating location.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "Mera farm Jaipur ke paas Chomu mein hai.",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": None, "market": None},
                    "expected_time_context": None, "expected_location": "Jaipur",
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 1: Stores farm location=Jaipur"
                },
                {
                    "turn_number": 2, "user_input": "Kal baarish hogi kya?",
                    "previous_context": {"location": "Jaipur"}, "expected_intent": "weather",
                    "expected_entities": {"crop": None, "market": None},
                    "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                    "expected_location": "Jaipur", "expected_capabilities": ["WEATHER"],
                    "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 2: Uses stored Jaipur location without re-asking"
                }
            ]
        },
        {
            "id": "L_03", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "en",
            "description": "English 3-turn: Turn 1 tomato, Turn 2 disease symptom, Turn 3 treatment.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "I am growing tomatoes in my field.",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "tomato", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                    "notes": "Turn 1: tomato context"
                },
                {
                    "turn_number": 2, "user_input": "The leaves are curling and have yellow spots.",
                    "previous_context": {"crop": "tomato"}, "expected_intent": "disease",
                    "expected_entities": {"crop": "tomato", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["DISEASE_DETECTION"],
                    "expected_tool_sequence": ["detect_disease"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                    "notes": "Turn 2: tomato leaf curl symptom"
                },
                {
                    "turn_number": 3, "user_input": "What is the organic treatment for this?",
                    "previous_context": {"crop": "tomato", "disease": "leaf_curl"}, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "tomato", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                    "notes": "Turn 3: organic treatment for tomato leaf curl"
                }
            ]
        },
        {
            "id": "L_04", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "mr",
            "description": "Marathi 2-turn: Turn 1 sets onion in Nashik, Turn 2 asks price without repeating crop/market.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "मी नाशिकमध्ये कांद्याची शेती करतो.",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "onion", "market": "Nashik"},
                    "expected_time_context": None, "expected_location": "Nashik",
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                    "notes": "Turn 1: Crop onion, location Nashik"
                },
                {
                    "turn_number": 2, "user_input": "आजचा बाजार भाव काय आहे?",
                    "previous_context": {"crop": "onion", "market": "Nashik"}, "expected_intent": "market",
                    "expected_entities": {"crop": "onion", "market": "Nashik"},
                    "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                    "expected_location": "Nashik", "expected_capabilities": ["MARKET_PRICE"],
                    "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                    "notes": "Turn 2: Inherits crop=onion and market=Nashik"
                }
            ]
        },
        {
            "id": "L_05", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "gu",
            "description": "Gujarati 2-turn: Turn 1 cotton, Turn 2 pest query.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "હું રાજકોટ પાસે કપાસ વાવી રહ્યો છું.",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "cotton", "market": "Rajkot"},
                    "expected_time_context": None, "expected_location": "Rajkot",
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                    "notes": "Turn 1: Cotton in Rajkot"
                },
                {
                    "turn_number": 2, "user_input": "આમાં ગુલાબી ઈયળ માટે શું છાંટવું જોઈએ?",
                    "previous_context": {"crop": "cotton"}, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "cotton", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                    "notes": "Turn 2: 'આમાં' inherits cotton"
                }
            ]
        },
        {
            "id": "L_06", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "pa",
            "description": "Punjabi 2-turn: Turn 1 paddy, Turn 2 water advice.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "ਮੈਂ ਲੁਧਿਆਣੇ ਵਿੱਚ ਬਾਸਮਤੀ ਝੋਨਾ ਲਗਾਇਆ ਹੈ।",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "paddy", "market": "Ludhiana"},
                    "expected_time_context": None, "expected_location": "Ludhiana",
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                    "notes": "Turn 1: Basmati paddy in Ludhiana"
                },
                {
                    "turn_number": 2, "user_input": "ਇਸਨੂੰ ਹੁਣ ਪਾਣੀ ਦੇਣ ਦੀ ਲੋੜ ਹੈ?",
                    "previous_context": {"crop": "paddy"}, "expected_intent": "irrigation",
                    "expected_entities": {"crop": "paddy", "market": None},
                    "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "now"},
                    "expected_location": "Ludhiana", "expected_capabilities": ["IRRIGATION"],
                    "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                    "notes": "Turn 2: 'ਇਸਨੂੰ' inherits paddy"
                }
            ]
        },
        {
            "id": "L_07", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "bn",
            "description": "Bengali 2-turn: Turn 1 potato in Burdwan, Turn 2 market price.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "বর্ধমান জেলায় আমার দশ বিঘা আলুর জমি আছে।",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "potato", "market": "Bardhaman"},
                    "expected_time_context": None, "expected_location": "Bardhaman",
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                    "notes": "Turn 1: Potato in Bardhaman"
                },
                {
                    "turn_number": 2, "user_input": "আজকে আলুর দর কেমন চলছে?",
                    "previous_context": {"crop": "potato", "location": "Bardhaman"}, "expected_intent": "market",
                    "expected_entities": {"crop": "potato", "market": "Bardhaman"},
                    "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                    "expected_location": "Bardhaman", "expected_capabilities": ["MARKET_PRICE"],
                    "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                    "notes": "Turn 2: Inherits potato + Bardhaman"
                }
            ]
        },
        {
            "id": "L_08", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "ta",
            "description": "Tamil 2-turn: Turn 1 sugarcane in Thanjavur, Turn 2 irrigation.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "தஞ்சாவூரில் கரும்பு சாகுபடி செய்கிறேன்.",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "sugarcane", "market": "Thanjavur"},
                    "expected_time_context": None, "expected_location": "Thanjavur",
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                    "notes": "Turn 1: Sugarcane in Thanjavur"
                },
                {
                    "turn_number": 2, "user_input": "நாளை தண்ணீர் பாய்ச்சலாமா?",
                    "previous_context": {"crop": "sugarcane", "location": "Thanjavur"}, "expected_intent": "irrigation",
                    "expected_entities": {"crop": "sugarcane", "market": None},
                    "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                    "expected_location": "Thanjavur", "expected_capabilities": ["IRRIGATION"],
                    "expected_tool_sequence": ["get_irrigation_advice"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                    "notes": "Turn 2: Inherits sugarcane"
                }
            ]
        },
        {
            "id": "L_09", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "te",
            "description": "Telugu 2-turn: Turn 1 chilli in Guntur, Turn 2 market price.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "నేను గుంటూరులో మిరప సాగు చేస్తున్నాను.",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "chilli", "market": "Guntur"},
                    "expected_time_context": None, "expected_location": "Guntur",
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                    "notes": "Turn 1: Chilli in Guntur"
                },
                {
                    "turn_number": 2, "user_input": "ఇప్పుడు ధర ఎలా ఉంది?",
                    "previous_context": {"crop": "chilli", "location": "Guntur"}, "expected_intent": "market",
                    "expected_entities": {"crop": "chilli", "market": "Guntur"},
                    "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "now"},
                    "expected_location": "Guntur", "expected_capabilities": ["MARKET_PRICE"],
                    "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                    "notes": "Turn 2: Inherits chilli and Guntur"
                }
            ]
        },
        {
            "id": "L_10", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "kn",
            "description": "Kannada 2-turn: Turn 1 ragi, Turn 2 fertilizer.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "ನನ್ನ ಹೊಲದಲ್ಲಿ ರಾಗಿ ಬೆಳೆದಿದ್ದೇನೆ.",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "ragi", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                    "notes": "Turn 1: Ragi"
                },
                {
                    "turn_number": 2, "user_input": "ಇದಕ್ಕೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?",
                    "previous_context": {"crop": "ragi"}, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "ragi", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                    "notes": "Turn 2: 'ಇದಕ್ಕೆ' inherits ragi"
                }
            ]
        },
        {
            "id": "L_11", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "ml",
            "description": "Malayalam 2-turn: Turn 1 pepper in Wayanad, Turn 2 rain check.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "വയനാട്ടിൽ കുരുമുളക് തോട്ടമുണ്ട് എനിക്ക്.",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "pepper", "market": "Wayanad"},
                    "expected_time_context": None, "expected_location": "Wayanad",
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                    "notes": "Turn 1: Pepper in Wayanad"
                },
                {
                    "turn_number": 2, "user_input": "நாളെ അവിടെ മഴ പെയ്യുമോ?",
                    "previous_context": {"crop": "pepper", "location": "Wayanad"}, "expected_intent": "weather",
                    "expected_entities": {"crop": None, "market": None},
                    "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                    "expected_location": "Wayanad", "expected_capabilities": ["WEATHER"],
                    "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                    "notes": "Turn 2: Inherits Wayanad location"
                }
            ]
        },
        {
            "id": "L_12", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "marwari",
            "description": "Marwari 2-turn: Turn 1 mustard, Turn 2 aphid spray advice.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "म्हैं खेत में रायड़ो (सरसों) बो राख्यो है।",
                    "previous_context": None, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "mustard", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 1: Mustard (raydo) in Marwari"
                },
                {
                    "turn_number": 2, "user_input": "इण में कीड़ा लाग्या है, दवाई बतावो।",
                    "previous_context": {"crop": "mustard"}, "expected_intent": "general_agriculture",
                    "expected_entities": {"crop": "mustard", "market": None},
                    "expected_time_context": None, "expected_location": None,
                    "expected_capabilities": ["RAG_KNOWLEDGE"],
                    "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 2: 'इण में' inherits mustard"
                }
            ]
        },
        {
            "id": "L_13", "category": "L", "domain": "MULTI_TURN_CONTEXT", "language": "hi",
            "description": "Hindi 2-turn: Turn 1 sets Kota mustard, Turn 2 switches to wheat without dropping location.",
            "turns": [
                {
                    "turn_number": 1, "user_input": "कोटा में सरसों का भाव क्या है?",
                    "previous_context": None, "expected_intent": "market",
                    "expected_entities": {"crop": "mustard", "market": "Kota"},
                    "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                    "expected_location": "Kota", "expected_capabilities": ["MARKET_PRICE"],
                    "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 1: Mustard in Kota"
                },
                {
                    "turn_number": 2, "user_input": "और गेहूं का क्या रेट है वहीं?",
                    "previous_context": {"crop": "mustard", "market": "Kota"}, "expected_intent": "market",
                    "expected_entities": {"crop": "wheat", "market": "Kota"},
                    "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                    "expected_location": "Kota", "expected_capabilities": ["MARKET_PRICE"],
                    "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 2: Switches crop to wheat, preserves location=Kota from 'वहीं'"
                }
            ]
        }
    ])

    # =========================================================================
    # M. TEMPORAL QUESTIONS (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "M_01", "category": "M", "domain": "TEMPORAL", "language": "hi",
            "description": "Hindi: Parson dhoop rahegi ya badal chhayenge Jaipur mein?",
            "turns": [{
                "turn_number": 1, "user_input": "परसों धूप रहेगी या बादल छाये रहेंगे जयपुर में?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "DAY_AFTER_TOMORROW", "time_of_day": None, "timeframe": "parson"},
                "expected_location": "Jaipur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Day after tomorrow temporal anchor in Hindi"
            }]
        },
        {
            "id": "M_02", "category": "M", "domain": "TEMPORAL", "language": "hinglish",
            "description": "Hinglish: Aaj shaam ko rain aayegi kya Kota mein?",
            "turns": [{
                "turn_number": 1, "user_input": "Aaj shaam ko rain aayegi kya Kota mein?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": "EVENING", "timeframe": "this evening"},
                "expected_location": "Kota", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Today evening temporal query in Hinglish"
            }]
        },
        {
            "id": "M_03", "category": "M", "domain": "TEMPORAL", "language": "gu",
            "description": "Gujarati: આવતા અઠવાડિયે રાજકોટમાં કેવો વરસાદ રહેશે?",
            "turns": [{
                "turn_number": 1, "user_input": "આવતા અઠવાડિયે રાજકોટમાં કેવો વરસાદ રહેશે?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "NEXT_WEEK", "time_of_day": None, "timeframe": "next week"},
                "expected_location": "Rajkot", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Next week temporal anchor in Gujarati"
            }]
        },
        {
            "id": "M_04", "category": "M", "domain": "TEMPORAL", "language": "mr",
            "description": "Marathi: उद्या सकाळी नाशिकमध्ये धुके पडेल का?",
            "turns": [{
                "turn_number": 1, "user_input": "उद्या सकाळी नाशिकमध्ये धुके पडेल का?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": "MORNING", "timeframe": "tomorrow morning"},
                "expected_location": "Nashik", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Tomorrow morning fog temporal test in Marathi"
            }]
        },
        {
            "id": "M_05", "category": "M", "domain": "TEMPORAL", "language": "pa",
            "description": "Punjabi: ਅੱਜ ਰਾਤ ਨੂੰ ਲੁਧਿਆਣੇ ਵਿੱਚ ਤਾਪਮਾਨ ਕਿੰਨਾ ਡਿੱਗੇਗਾ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਅੱਜ ਰਾਤ ਨੂੰ ਲੁਧਿਆਣੇ ਵਿੱਚ ਤਾਪਮਾਨ ਕਿੰਨਾ ਡਿੱਗੇਗਾ?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": "NIGHT", "timeframe": "tonight"},
                "expected_location": "Ludhiana", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Tonight temperature in Punjabi"
            }]
        },
        {
            "id": "M_06", "category": "M", "domain": "TEMPORAL", "language": "bn",
            "description": "Bengali: আগামী ৩ দিন বর্ধমানে বৃষ্টিপাতের সম্ভাবনা কতটা?",
            "turns": [{
                "turn_number": 1, "user_input": "আগামী ৩ দিন বর্ধমানে বৃষ্টিপাতের সম্ভাবনা কতটা?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "NEXT_3_DAYS", "time_of_day": None, "timeframe": "next 3 days"},
                "expected_location": "Bardhaman", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Next 3 days temporal test in Bengali"
            }]
        },
        {
            "id": "M_07", "category": "M", "domain": "TEMPORAL", "language": "ta",
            "description": "Tamil: இந்த வார இறுதியில் தஞ்சாவூரில் மழை பெய்யுமா?",
            "turns": [{
                "turn_number": 1, "user_input": "இந்த வார இறுதியில் தஞ்சாவூரில் மழை பெய்யுமா?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "THIS_WEEK", "time_of_day": None, "timeframe": "this weekend"},
                "expected_location": "Thanjavur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "This weekend temporal test in Tamil"
            }]
        },
        {
            "id": "M_08", "category": "M", "domain": "TEMPORAL", "language": "te",
            "description": "Telugu: రేపు మధ్యాహ్నం వరంగల్‌లో ఎండ తీవ్రత ఎలా ఉంటుంది?",
            "turns": [{
                "turn_number": 1, "user_input": "రేపు మధ్యాహ్నం వరంగల్‌లో ఎండ తీవ్రత ఎలా ఉంటుంది?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": "AFTERNOON", "timeframe": "tomorrow afternoon"},
                "expected_location": "Warangal", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Tomorrow afternoon heat query in Telugu"
            }]
        },
        {
            "id": "M_09", "category": "M", "domain": "TEMPORAL", "language": "kn",
            "description": "Kannada: ನಾಳೆ ಮುಂಜಾನೆ ಹಾಸನದಲ್ಲಿ ತಂಪಾದ ವಾತಾವರಣವಿರುತ್ತದೆಯೇ?",
            "turns": [{
                "turn_number": 1, "user_input": "ನಾಳೆ ಮುಂಜಾನೆ ಹಾಸನದಲ್ಲಿ ತಂಪಾದ ವಾತಾವರಣವಿರುತ್ತದೆಯೇ?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": "MORNING", "timeframe": "tomorrow morning"},
                "expected_location": "Hassan", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Tomorrow early morning query in Kannada"
            }]
        },
        {
            "id": "M_10", "category": "M", "domain": "TEMPORAL", "language": "ml",
            "description": "Malayalam: മറ്റന്നാൾ വയനാട്ടിൽ കാലാവസ്ഥ എങ്ങനെയായിരിക്കും?",
            "turns": [{
                "turn_number": 1, "user_input": "മറ്റന്നാൾ വയനാട്ടിൽ കാലാവസ്ഥ എങ്ങനെയായിരിക്കും?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "DAY_AFTER_TOMORROW", "time_of_day": None, "timeframe": "day after tomorrow"},
                "expected_location": "Wayanad", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Day after tomorrow (mattanall) in Malayalam"
            }]
        },
        {
            "id": "M_11", "category": "M", "domain": "TEMPORAL", "language": "marwari",
            "description": "Marwari: परसों संवारे जोधपुर कानी लू चालसी के?",
            "turns": [{
                "turn_number": 1, "user_input": "परसों संवारे जोधपुर कानी लू चालसी के?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "DAY_AFTER_TOMORROW", "time_of_day": "MORNING", "timeframe": "parson sanware"},
                "expected_location": "Jodhpur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Day after tomorrow morning hot winds in Marwari"
            }]
        },
        {
            "id": "M_12", "category": "M", "domain": "TEMPORAL", "language": "en",
            "description": "English: What is the weather outlook for the next 7 days in Karnal?",
            "turns": [{
                "turn_number": 1, "user_input": "What is the 7-day weather outlook in Karnal?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "NEXT_7_DAYS", "time_of_day": None, "timeframe": "7 days"},
                "expected_location": "Karnal", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "7-day forecast in English"
            }]
        },
        {
            "id": "M_13", "category": "M", "domain": "TEMPORAL", "language": "hi",
            "description": "Hindi: Aaj raat ko kohra padega kya Alwar mein?",
            "turns": [{
                "turn_number": 1, "user_input": "आज रात को कोहरा पड़ेगा क्या अलवर में?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": "NIGHT", "timeframe": "tonight"},
                "expected_location": "Alwar", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Tonight fog prediction in Hindi"
            }]
        }
    ])

    # =========================================================================
    # N. LOCATION QUESTIONS (14 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "N_01", "category": "N", "domain": "LOCATION", "language": "hi",
            "description": "Hindi: Mere farm ke paas weather kaisa hai?",
            "turns": [{
                "turn_number": 1, "user_input": "मेरे फार्म के पास मौसम कैसा है?",
                "previous_context": {"location": "Jaipur"}, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "now"},
                "expected_location": "Jaipur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Resolves 'mere farm ke paas' to active user location Jaipur"
            }]
        },
        {
            "id": "N_02", "category": "N", "domain": "LOCATION", "language": "hinglish",
            "description": "Hinglish: Udaipur side weather kaisa chal raha hai abhi?",
            "turns": [{
                "turn_number": 1, "user_input": "Udaipur side weather kaisa chal raha hai abhi?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "now"},
                "expected_location": "Udaipur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Extracts 'Udaipur side' -> Udaipur"
            }]
        },
        {
            "id": "N_03", "category": "N", "domain": "LOCATION", "language": "gu",
            "description": "Gujarati: સૌરાષ્ટ્ર વિસ્તારમાં વરસાદનું પ્રમાણ કેવું રહેશે?",
            "turns": [{
                "turn_number": 1, "user_input": "સૌરાષ્ટ્ર વિસ્તારમાં વરસાદનું પ્રમાણ કેવું રહેશે?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Saurashtra",
                "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Regional location Saurashtra in Gujarati"
            }]
        },
        {
            "id": "N_04", "category": "N", "domain": "LOCATION", "language": "mr",
            "description": "Marathi: विदर्भात उद्या उष्णतेची लाट येण्याची शक्यता आहे का?",
            "turns": [{
                "turn_number": 1, "user_input": "विदर्भात उद्या उष्णतेची लाट येण्याची शक्यता आहे का?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Vidarbha", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Vidarbha regional location in Marathi"
            }]
        },
        {
            "id": "N_05", "category": "N", "domain": "LOCATION", "language": "pa",
            "description": "Punjabi: ਮਾਲਵਾ ਖੇਤਰ ਵਿੱਚ ਕੱਲ੍ਹ ਮੀਂਹ ਪਵੇਗਾ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਮਾਲਵਾ ਖੇਤਰ ਵਿੱਚ ਕੱਲ੍ਹ ਮੀਂਹ ਪਵੇਗਾ?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Malwa", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Malwa regional belt in Punjabi"
            }]
        },
        {
            "id": "N_06", "category": "N", "domain": "LOCATION", "language": "bn",
            "description": "Bengali: হুগলি জেলার আবহাওয়া আগামীকাল কেমন থাকবে?",
            "turns": [{
                "turn_number": 1, "user_input": "হুগলি জেলার আবহাওয়া আগামীকাল কেমন থাকবে?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Hooghly", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Hooghly district in Bengali"
            }]
        },
        {
            "id": "N_07", "category": "N", "domain": "LOCATION", "language": "ta",
            "description": "Tamil: மதுரை பகுதியில் தக்காளி விலை என்ன?",
            "turns": [{
                "turn_number": 1, "user_input": "மதுரை மார்க்கெட்டில் தக்காளி விலை என்ன?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "tomato", "market": "Madurai"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Madurai", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Madurai market in Tamil"
            }]
        },
        {
            "id": "N_08", "category": "N", "domain": "LOCATION", "language": "te",
            "description": "Telugu: అనంతపురం జిల్లాలో వర్షపాతం ఎలా ఉంది?",
            "turns": [{
                "turn_number": 1, "user_input": "అనంతపురం జిల్లాలో వర్షపాతం ఎలా ఉంది?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Anantapur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Anantapur drought district in Telugu"
            }]
        },
        {
            "id": "N_09", "category": "N", "domain": "LOCATION", "language": "kn",
            "description": "Kannada: ಬೆಳಗಾವಿ ಜಿಲ್ಲೆಯಲ್ಲಿ ಕಬ್ಬಿನ ದರ ಎಷ್ಟಿದೆ?",
            "turns": [{
                "turn_number": 1, "user_input": "ಬೆಳಗಾವಿ ಜಿಲ್ಲೆಯಲ್ಲಿ ಕಬ್ಬಿನ ದರ ಎಷ್ಟಿದೆ?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "sugarcane", "market": "Belagavi"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Belagavi", "expected_capabilities": ["MARKET_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Belagavi sugarcane in Kannada"
            }]
        },
        {
            "id": "N_10", "category": "N", "domain": "LOCATION", "language": "ml",
            "description": "Malayalam: ഇടുക്കി ജില്ലയിൽ കനത്ത കാറ്റും മഴയും ഉണ്ടാകുമോ?",
            "turns": [{
                "turn_number": 1, "user_input": "ഇടുക്കി ജില്ലയിൽ കനത്ത കാറ്റും മഴയും ഉണ്ടാകുമോ?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Idukki",
                "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Idukki high-range district in Malayalam"
            }]
        },
        {
            "id": "N_11", "category": "N", "domain": "LOCATION", "language": "marwari",
            "description": "Marwari: बाड़मेर कानी रो मौसम बतावो सा।",
            "turns": [{
                "turn_number": 1, "user_input": "बाड़मेर कानी रो मौसम बतावो सा।",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Barmer",
                "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Barmer border district in Marwari"
            }]
        },
        {
            "id": "N_12", "category": "N", "domain": "LOCATION", "language": "en",
            "description": "English: Near my farm in Varanasi, what will the temperature be tonight?",
            "turns": [{
                "turn_number": 1, "user_input": "Near my farm in Varanasi, what will the temperature be tonight?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": "NIGHT", "timeframe": "tonight"},
                "expected_location": "Varanasi", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Explicit location Varanasi extracted in English"
            }]
        },
        {
            "id": "N_13", "category": "N", "domain": "LOCATION", "language": "hi",
            "description": "Hindi: Mere gaaon mein barish hogi? (without profile location -> request input)",
            "turns": [{
                "turn_number": 1, "user_input": "मेरे गाँव में बारिश होगी क्या?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": [], "expected_required_input": "LOCATION",
                "expected_action": "REQUEST_INPUT", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Safety: Unknown village with no stored location must ask user location"
            }]
        },
        {
            "id": "N_14", "category": "N", "domain": "LOCATION", "language": "hinglish",
            "description": "Hinglish: Switch from Jaipur to Kota weather.",
            "turns": [{
                "turn_number": 1, "user_input": "Jaipur nahi, ab Kota ka weather batao.",
                "previous_context": {"location": "Jaipur"}, "expected_intent": "weather",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": "Kota",
                "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Overrides previous Jaipur location with explicit Kota"
            }]
        }
    ])

    return convs
