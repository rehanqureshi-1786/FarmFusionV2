"""
Category R: Adversarial / Trick Questions (13 conversations)
Category S: Natural Voice Transcription Errors (13 conversations)
Category T: Natural Farmer Speech & Follow-ups (14 conversations)
Languages: en, hi, hinglish, gu, mr, pa, bn, ta, te, kn, ml, marwari
"""

def get_adversarial_asr_followup_conversations():
    convs = []

    # =========================================================================
    # R. ADVERSARIAL / TRICK QUESTIONS (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "R_01", "category": "R", "domain": "ADVERSARIAL", "language": "hinglish",
            "description": "Hinglish: Weather nahi chahiye, bas batao irrigation kab karu (Negative constraint)",
            "turns": [{
                "turn_number": 1, "user_input": "Weather nahi chahiye, bas batao meri wheat crop ko irrigation kab karu?", "previous_context": None,
                "expected_intent": "irrigation_advisory", "expected_entities": {"crop": "wheat"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["SMART_IRRIGATION"],
                "expected_tool_sequence": ["calculate_water_requirement"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Adversarial negative instruction: Do not run standalone weather report, answer irrigation directly"
            }]
        },
        {
            "id": "R_02", "category": "R", "domain": "ADVERSARIAL", "language": "en",
            "description": "English: Don't check weather. Tell me mandi price for cotton.",
            "turns": [{
                "turn_number": 1, "user_input": "Don't check weather. Just tell me the mandi price of cotton in Rajkot.", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": "cotton"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": "Rajkot", "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Must route to mandi tool only and suppress weather routing"
            }]
        },
        {
            "id": "R_03", "category": "R", "domain": "ADVERSARIAL", "language": "en",
            "description": "English: Don't ask me for a photo, just guess the disease",
            "turns": [{
                "turn_number": 1, "user_input": "Don't ask me for a photo, just guess what disease my potato has from your imagination.", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {"crop": "potato"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "REFUSE_GUESS_REQUIRE_IMAGE", "expected_response_language": "en", "expect_clarify": True,
                "notes": "Must strictly refuse to hallucinate a disease diagnosis without visual evidence"
            }]
        },
        {
            "id": "R_04", "category": "R", "domain": "ADVERSARIAL", "language": "hinglish",
            "description": "Hinglish: I think mandi rate is 5000, confirm it (Fabricated price prompt)",
            "turns": [{
                "turn_number": 1, "user_input": "I think Kota mandi mein wheat ka rate ₹5000 per quintal hai, confirm karke batao.", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": "wheat"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": "Kota", "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Grounding test: LLM must verify against real tool data, NOT agree with user's inflated ₹5000 claim"
            }]
        },
        {
            "id": "R_05", "category": "R", "domain": "ADVERSARIAL", "language": "hi",
            "description": "Hindi: Context override (Actually forget wheat, I grow tomato now)",
            "turns": [
                {
                    "turn_number": 1, "user_input": "मैं अपने 5 बीघा खेत में गेहूं उगा रहा हूँ।", "previous_context": None,
                    "expected_intent": "general_farming", "expected_entities": {"crop": "wheat", "farm_size": "5 bigha"},
                    "expected_time_context": None, "expected_location": None, "expected_capabilities": ["FARM_MANAGEMENT"],
                    "expected_tool_sequence": [], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 1 sets wheat context"
                },
                {
                    "turn_number": 2, "user_input": "गेहूं छोड़ो, असल में मैंने टमाटर लगाया है। अब बताओ पानी कब दूँ?", "previous_context": {"crop": "wheat"},
                    "expected_intent": "irrigation_advisory", "expected_entities": {"crop": "tomato"},
                    "expected_time_context": None, "expected_location": None, "expected_capabilities": ["SMART_IRRIGATION"],
                    "expected_tool_sequence": ["calculate_water_requirement"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 2 overrides crop entity to tomato; must purge wheat context"
                }
            ]
        },
        {
            "id": "R_06", "category": "R", "domain": "ADVERSARIAL", "language": "en",
            "description": "English: Forecast weather for the next 60 days (Unrealistic forecast horizon)",
            "turns": [{
                "turn_number": 1, "user_input": "Give me the daily rainfall forecast for the next 60 days in Bhopal.", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"timeframe": "60_days"}, "expected_location": "Bhopal", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER_WITH_HORIZON_LIMITATION", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Numerical limit: Open-Meteo accurate horizon is 7-14 days; must explain limitation and not hallucinate 60-day exact days"
            }]
        },
        {
            "id": "R_07", "category": "R", "domain": "ADVERSARIAL", "language": "gu",
            "description": "Gujarati: ખાતર વગર બમણું ઉત્પાદન? (Unrealistic farming myth)",
            "turns": [{
                "turn_number": 1, "user_input": "કોઈ એવી જાદુઈ દવા છે જેનાથી એક જ રાતમાં કપાસ બમણો થઈ જાય?", "previous_context": None,
                "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "cotton"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["AGRICULTURAL_RAG"],
                "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                "expected_action": "SCIENTIFIC_DEBUNK", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Adversarial magic yield claim; scientific grounding must debunk overnight double yield safely"
            }]
        },
        {
            "id": "R_08", "category": "R", "domain": "ADVERSARIAL", "language": "mr",
            "description": "Marathi: हवामान नको, फक्त कांद्याचे भाव सांगा (Negative filter in Marathi)",
            "turns": [{
                "turn_number": 1, "user_input": "मला हवामानाशी काही देणंघेणं नाही, फक्त लासलगावचे कांद्याचे भाव सांगा.", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": "onion"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": "Lasalgaon", "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Marathi negative filter rejecting weather"
            }]
        },
        {
            "id": "R_09", "category": "R", "domain": "ADVERSARIAL", "language": "pa",
            "description": "Punjabi: ਕੱਲ੍ਹ ਦਾ ਮੌਸਮ ਨਹੀਂ, ਪਾਣੀ ਕਦੋਂ ਲਾਈਏ? (Irrigation only)",
            "turns": [{
                "turn_number": 1, "user_input": "ਮੌਸਮ ਛੱਡੋ, ਬੱਸ ਇਹ ਦੱਸੋ ਕਿ ਝੋਨੇ ਨੂੰ ਪਾਣੀ ਕਦੋਂ ਦੇਣਾ ਹੈ?", "previous_context": None,
                "expected_intent": "irrigation_advisory", "expected_entities": {"crop": "paddy"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["SMART_IRRIGATION"],
                "expected_tool_sequence": ["calculate_water_requirement"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Punjabi adversarial suppression of weather"
            }]
        },
        {
            "id": "R_10", "category": "R", "domain": "ADVERSARIAL", "language": "bn",
            "description": "Bengali: আলুর দাম ১০ হাজার তো? (Confirm inflated price in Bengali)",
            "turns": [{
                "turn_number": 1, "user_input": "বর্ধমানে আলুর দাম নাকি ১০ হাজার টাকা কুইন্টাল, সত্যি নাকি?", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": "potato"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": "Bardhaman", "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Bengali verification of fake price claim"
            }]
        },
        {
            "id": "R_11", "category": "R", "domain": "ADVERSARIAL", "language": "ta",
            "description": "Tamil: வானிலை வேண்டாம் தக்காளி விலை மட்டும் சொல் (No weather, price only)",
            "turns": [{
                "turn_number": 1, "user_input": "வானிலை தகவல் வேண்டாம், திண்டுக்கல் சந்தையில் தக்காளி விலை மட்டும் சொல்.", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": "tomato"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": "Dindigul", "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Tamil negative condition"
            }]
        },
        {
            "id": "R_12", "category": "R", "domain": "ADVERSARIAL", "language": "te",
            "description": "Telugu: ఫోటో లేకుండా రోగం పేరు చెప్పు (Demand guess without photo)",
            "turns": [{
                "turn_number": 1, "user_input": "ఫోటో లేకుండానే నా మిరప తోటకి ఏ రోగం వచ్చిందో చెప్పు.", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {"crop": "chilli"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "REFUSE_GUESS_REQUIRE_IMAGE", "expected_response_language": "te", "expect_clarify": True,
                "notes": "Telugu adversarial request to bypass image requirement"
            }]
        },
        {
            "id": "R_13", "category": "R", "domain": "ADVERSARIAL", "language": "marwari",
            "description": "Marwari: म्हारे पिछले गाँव रो मौसम बता (Use previous location context)",
            "turns": [
                {
                    "turn_number": 1, "user_input": "म्हारो गाँव नागौर में है।", "previous_context": None,
                    "expected_intent": "general_farming", "expected_entities": {},
                    "expected_time_context": None, "expected_location": "Nagaur", "expected_capabilities": ["FARM_MANAGEMENT"],
                    "expected_tool_sequence": [], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 1 registers Nagaur"
                },
                {
                    "turn_number": 2, "user_input": "उसी गाँव रो काल रो मौसम कइसो रहसी?", "previous_context": {"location": "Nagaur"},
                    "expected_intent": "weather", "expected_entities": {},
                    "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Nagaur", "expected_capabilities": ["WEATHER"],
                    "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 2 refers back with 'उसी गाँव' (same village); must inherit Nagaur"
                }
            ]
        },
    ])

    # =========================================================================
    # S. NATURAL VOICE TRANSCRIPTION ERRORS (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "S_01", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "en",
            "description": "English ASR errors: 'week' for wheat, 'mandy' for mandi",
            "turns": [{
                "turn_number": 1, "user_input": "umm what is the mandy rate for week in kota today haan", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": "wheat"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": "Kota", "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Phonetic ASR errors: week -> wheat, mandy -> mandi, filler words umm/haan, lowercase no punctuation"
            }]
        },
        {
            "id": "S_02", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "hinglish",
            "description": "Hinglish ASR: 'baris' for baarish, 'tamato' for tomato, missing stops",
            "turns": [{
                "turn_number": 1, "user_input": "are kal baris hogi kya mere tamato ke khet me matlab pani du ya nahi", "previous_context": None,
                "expected_intent": "multi_intent", "expected_entities": {"crop": "tomato"},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": None, "expected_capabilities": ["WEATHER", "SMART_IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "calculate_water_requirement"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "baris -> baarish, tamato -> tomato, fillers 'are', 'matlab', multi-intent weather + irrigation"
            }]
        },
        {
            "id": "S_03", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "hinglish",
            "description": "Hinglish ASR: 'lasal gaon' split and 'piyaz' phonetics",
            "turns": [{
                "turn_number": 1, "user_input": "lasal gaon mandi me piyaz ka bhav kya h", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": "onion"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": "Lasalgaon", "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "lasal gaon -> Lasalgaon, piyaz -> onion, SMS spelling 'h' for 'hai'"
            }]
        },
        {
            "id": "S_04", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "hi",
            "description": "Hindi ASR: Phonetic Roman Hindi 'gehu ke patte pile pad rahe'",
            "turns": [{
                "turn_number": 1, "user_input": "gehun k pate peele pad rhe h kisan bhai", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {"crop": "wheat", "symptom": "yellow leaves"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "REQUEST_IMAGE", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "Informal Romanized Hindi with contractions 'k', 'rhe h', requesting diagnosis without image"
            }]
        },
        {
            "id": "S_05", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "gu",
            "description": "Gujarati ASR: Filler words and unpunctuated stream",
            "turns": [{
                "turn_number": 1, "user_input": "એલા ભાઈ પેલું શું કહેવાય રાજકોટ મા કપાસ નો ભાવ શુ ચાલે છે આજે", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": "cotton"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": "Rajkot", "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Colloquial Gujarati filler 'એલા ભાઈ પેલું શું કહેવાય' (hey brother what you call it)"
            }]
        },
        {
            "id": "S_06", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "mr",
            "description": "Marathi ASR: 'पाऊस पडनार का' dialectal phonetics",
            "turns": [{
                "turn_number": 1, "user_input": "अरे भाऊ उद्या पाऊस पडनार का पुण्यात सांगा बरं", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Pune", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Rural Marathi phonetics 'पडनार' instead of standard 'पडणार', filler 'अरे भाऊ'"
            }]
        },
        {
            "id": "S_07", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "pa",
            "description": "Punjabi ASR: Repeated words and hesitation",
            "turns": [{
                "turn_number": 1, "user_input": "ਹਾਂ ਜੀ ਉਹ ਮਤਲਬ ਕੱਲ੍ਹ ਕੱਲ੍ਹ ਮੀਂਹ ਪਵੇਗਾ ਕਿ ਨਹੀਂ ਲੁਧਿਆਣੇ ਵਿੱਚ", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Ludhiana", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Punjabi stuttering 'ਕੱਲ੍ਹ ਕੱਲ੍ਹ', hesitation 'ਹਾਂ ਜੀ ਉਹ ਮਤਲਬ'"
            }]
        },
        {
            "id": "S_08", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "bn",
            "description": "Bengali ASR: 'brishti' misheard and fillers",
            "turns": [{
                "turn_number": 1, "user_input": "মানে ওই কালকে বৃষ্টি হবে নাকি বর্ধমানে একটু দেখুন তো", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Bardhaman", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Bengali filler 'মানে ওই', informal polite 'একটু দেখুন তো'"
            }]
        },
        {
            "id": "S_09", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "ta",
            "description": "Tamil ASR: Speech pause and colloquial contraction",
            "turns": [{
                "turn_number": 1, "user_input": "அட... நாளைக்கு மதுரைல மழை வருமா வராதா சொல்லுங்க", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Madurai", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Tamil interjection 'அட...' and colloquial phrasing 'வருமா வராதா'"
            }]
        },
        {
            "id": "S_10", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "te",
            "description": "Telugu ASR: Hesitation particles and informal tone",
            "turns": [{
                "turn_number": 1, "user_input": "అదేనండి రేపు గుంటూరులో వర్షం పడుతుందా లేదా కొంచెం చెప్పండి", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Guntur", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Telugu conversation starter 'అదేనండి', rain check tomorrow"
            }]
        },
        {
            "id": "S_11", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "kn",
            "description": "Kannada ASR: Filler words and rural phrasing",
            "turns": [{
                "turn_number": 1, "user_input": "ಹೌದು ಕಣ್ರೀ ನಾಳೆ ಧಾರವಾಡದಲ್ಲಿ ಮಳೆ ಬರುತ್ತಾ ಇಲ್ವಾ", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Dharwad", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Kannada rustic dialect marker 'ಕಣ್ರೀ'"
            }]
        },
        {
            "id": "S_12", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "ml",
            "description": "Malayalam ASR: Informal conversational particle",
            "turns": [{
                "turn_number": 1, "user_input": "അല്ല നാളെ പാലക്കാട്ട് മഴ പെയ്യുമോ ആവോ", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Palakkad", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Malayalam conversational filler 'അല്ല', ending doubt particle 'ആവോ'"
            }]
        },
        {
            "id": "S_13", "category": "S", "domain": "VOICE_ASR_ERRORS", "language": "marwari",
            "description": "Marwari ASR: Heavy dialectal phonetics and fillers",
            "turns": [{
                "turn_number": 1, "user_input": "अरे भाई सा... काल म्हारे बाड़मेर कानी मेह बरसेगा के?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Barmer", "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Marwari honorific 'भाई सा', rain 'मेह', directional marker 'कानी'"
            }]
        },
    ])

    # =========================================================================
    # T. NATURAL FARMER SPEECH & FOLLOW-UPS (14 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "T_01", "category": "T", "domain": "NATURAL_SPEECH", "language": "hinglish",
            "description": "Hinglish: Bhai kal paani dena padega kya? (Colloquial irrigation)",
            "turns": [{
                "turn_number": 1, "user_input": "bhai kal khet me paani dena padega kya?", "previous_context": None,
                "expected_intent": "irrigation_advisory", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": None, "expected_capabilities": ["SMART_IRRIGATION"],
                "expected_tool_sequence": ["calculate_water_requirement"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Extremely common casual phrasing for irrigation"
            }]
        },
        {
            "id": "T_02", "category": "T", "domain": "NATURAL_SPEECH", "language": "hinglish",
            "description": "Hinglish: Yaar meri fasal kuch ajeeb si lag rahi hai",
            "turns": [{
                "turn_number": 1, "user_input": "Yaar meri fasal kuch ajeeb si lag rahi hai, samajh nahi aa raha kya karu.", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "REQUEST_IMAGE", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "Farmer worried about sick crop; prompt for photo politely"
            }]
        },
        {
            "id": "T_03", "category": "T", "domain": "NATURAL_SPEECH", "language": "hi",
            "description": "Hindi: Arey kal baarish toh nahi hogi na? (Anxious harvest check)",
            "turns": [{
                "turn_number": 1, "user_input": "अरे कल बारिश तो नहीं होगी ना? कल गेहूं काटना है।", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {"crop": "wheat", "operation": "harvest"},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": None, "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Harvest planning weather inquiry"
            }]
        },
        {
            "id": "T_04", "category": "T", "domain": "NATURAL_SPEECH", "language": "hi",
            "description": "Hindi: Mere khet mein mitti kaafi geeli hai, pani du?",
            "turns": [{
                "turn_number": 1, "user_input": "मेरे खेत में मिट्टी काफी गीली है, क्या फिर भी पानी लगाना चाहिए?", "previous_context": None,
                "expected_intent": "irrigation_advisory", "expected_entities": {"soil_moisture": "wet"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": None, "expected_capabilities": ["SMART_IRRIGATION"],
                "expected_tool_sequence": ["calculate_water_requirement"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Farmer observing wet soil; irrigation advisory should advise delaying"
            }]
        },
        {
            "id": "T_05", "category": "T", "domain": "NATURAL_SPEECH", "language": "hinglish",
            "description": "Hinglish: Rate gir raha hai kya? Abhi bechna theek rahega? (Market timing)",
            "turns": [{
                "turn_number": 1, "user_input": "Onion ka rate gir raha hai kya? Abhi bechna theek rahega ya hold karu?", "previous_context": None,
                "expected_intent": "multi_intent", "expected_entities": {"crop": "onion"},
                "expected_time_context": {"relative_day": "TODAY"}, "expected_location": None, "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": ["get_mandi_prices"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Sell vs hold advisory combining current price and trend"
            }]
        },
        {
            "id": "T_06", "category": "T", "domain": "NATURAL_SPEECH", "language": "hinglish",
            "description": "Hinglish: Mere paas photo hai, dekh ke batao (Proactive image upload readiness)",
            "turns": [{
                "turn_number": 1, "user_input": "Mere paas patte ki photo hai, dekh ke batao kaunsi bimari hai.", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "NAVIGATE_TO_DISEASE_DETECTOR", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Farmer states they have photo ready; navigate to disease scanner screen"
            }]
        },
        {
            "id": "T_07", "category": "T", "domain": "NATURAL_SPEECH", "language": "en",
            "description": "English Multi-turn follow-up: Crop -> Disease -> Treatment spray dosage",
            "turns": [
                {
                    "turn_number": 1, "user_input": "I am growing tomato plants in my 2 acre farm.", "previous_context": None,
                    "expected_intent": "general_farming", "expected_entities": {"crop": "tomato", "farm_size": "2 acre"},
                    "expected_time_context": None, "expected_location": None, "expected_capabilities": ["FARM_MANAGEMENT"],
                    "expected_tool_sequence": [], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                    "notes": "Turn 1 registers tomato crop"
                },
                {
                    "turn_number": 2, "user_input": "They have black concentric rings on lower leaves.", "previous_context": {"crop": "tomato"},
                    "expected_intent": "disease_detection", "expected_entities": {"crop": "tomato", "symptom": "early blight rings"},
                    "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                    "expected_tool_sequence": [], "expected_required_input": "image",
                    "expected_action": "REQUEST_IMAGE", "expected_response_language": "en", "expect_clarify": True,
                    "notes": "Turn 2 describes early blight symptom; requests image"
                },
                {
                    "turn_number": 3, "user_input": "If it is early blight, what fungicide spray should I use and how much per liter?", "previous_context": {"crop": "tomato", "disease": "early blight"},
                    "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "tomato", "disease": "early blight"},
                    "expected_time_context": None, "expected_location": None, "expected_capabilities": ["AGRICULTURAL_RAG"],
                    "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                    "notes": "Turn 3 requests exact scientific dosage (e.g. Mancozeb 2g/L)"
                }
            ]
        },
        {
            "id": "T_08", "category": "T", "domain": "NATURAL_SPEECH", "language": "hi",
            "description": "Hindi Multi-turn follow-up: Wheat fertilizer dosage",
            "turns": [
                {
                    "turn_number": 1, "user_input": "मैंने पिछले हफ्ते गेहूं बोया है।", "previous_context": None,
                    "expected_intent": "general_farming", "expected_entities": {"crop": "wheat"},
                    "expected_time_context": None, "expected_location": None, "expected_capabilities": ["FARM_MANAGEMENT"],
                    "expected_tool_sequence": [], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 1 establishes wheat sowing"
                },
                {
                    "turn_number": 2, "user_input": "पहली सिंचाई के समय यूरिया कितना डालूँ?", "previous_context": {"crop": "wheat"},
                    "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "wheat", "fertilizer": "urea"},
                    "expected_time_context": None, "expected_location": None, "expected_capabilities": ["AGRICULTURAL_RAG"],
                    "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                    "notes": "Turn 2 asks specific urea dosage for first irrigation in wheat"
                }
            ]
        },
        {
            "id": "T_09", "category": "T", "domain": "NATURAL_SPEECH", "language": "gu",
            "description": "Gujarati: હવે દવા છાંટવાનો યોગ્ય સમય કયો? (Follow-up timing)",
            "turns": [
                {
                    "turn_number": 1, "user_input": "આવતીકાલે રાજકોટમાં વરસાદ પડશે?", "previous_context": None,
                    "expected_intent": "weather", "expected_entities": {},
                    "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": "Rajkot", "expected_capabilities": ["WEATHER"],
                    "expected_tool_sequence": ["get_current_weather"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                    "notes": "Turn 1 checks rain"
                },
                {
                    "turn_number": 2, "user_input": "તો પછી કપાસમાં કીટનાશક છાંટવાનો સારો સમય કયો રહેશે?", "previous_context": {"location": "Rajkot"},
                    "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "cotton"},
                    "expected_time_context": None, "expected_location": "Rajkot", "expected_capabilities": ["AGRICULTURAL_RAG", "WEATHER"],
                    "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                    "notes": "Turn 2 asks for optimal spraying window considering tomorrow's weather"
                }
            ]
        },
        {
            "id": "T_10", "category": "T", "domain": "NATURAL_SPEECH", "language": "mr",
            "description": "Marathi: कांद्याला दुसरा खत डोस कधी द्यावा? (Follow-up fertilizer)",
            "turns": [
                {
                    "turn_number": 1, "user_input": "मी नाशिकमध्ये कांदा लावला आहे.", "previous_context": None,
                    "expected_intent": "general_farming", "expected_entities": {"crop": "onion"},
                    "expected_time_context": None, "expected_location": "Nashik", "expected_capabilities": ["FARM_MANAGEMENT"],
                    "expected_tool_sequence": [], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                    "notes": "Turn 1 establishes Nashik onion crop"
                },
                {
                    "turn_number": 2, "user_input": "त्याला खताचा दुसरा हप्ता कधी आणि कोणता द्यावा?", "previous_context": {"crop": "onion", "location": "Nashik"},
                    "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "onion", "topic": "fertilizer dose"},
                    "expected_time_context": None, "expected_location": "Nashik", "expected_capabilities": ["AGRICULTURAL_RAG"],
                    "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                    "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                    "notes": "Turn 2 asks second fertilizer dose"
                }
            ]
        },
        {
            "id": "T_11", "category": "T", "domain": "NATURAL_SPEECH", "language": "pa",
            "description": "Punjabi: ਕਣਕ ਦੀ ਗੁੱਲੀ ਡੰਡੇ ਵਾਲੀ ਦਵਾਈ ਕਿਹੜੀ ਹੈ? (Weedicide query)",
            "turns": [{
                "turn_number": 1, "user_input": "ਵੀਰ ਜੀ ਕਣਕ ਵਿੱਚ ਗੁੱਲੀ ਡੰਡਾ ਬਹੁਤ ਹੋ ਗਿਆ ਹੈ, ਕਿਹੜੀ ਸਪਰੇਅ ਕਰਾਂ?", "previous_context": None,
                "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "wheat", "weed": "phalaris minor (gulli danda)"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["AGRICULTURAL_RAG"],
                "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Punjabi natural phrasing for canary grass / gulli danda weed control"
            }]
        },
        {
            "id": "T_12", "category": "T", "domain": "NATURAL_SPEECH", "language": "bn",
            "description": "Bengali: ধানের শিষ পচা রোগের ওষুধ কী? (Sheath rot medicine)",
            "turns": [{
                "turn_number": 1, "user_input": "দাদা ধানের শীষ পচা রোগের জন্য কোন ওষুধ স্প্রে করব?", "previous_context": None,
                "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "paddy", "disease": "sheath rot"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["AGRICULTURAL_RAG"],
                "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Bengali colloquial request for paddy sheath rot medicine"
            }]
        },
        {
            "id": "T_13", "category": "T", "domain": "NATURAL_SPEECH", "language": "ta",
            "description": "Tamil: வாழையில் இலை கருகல் நோய் மருந்து (Banana leaf blight treatment)",
            "turns": [{
                "turn_number": 1, "user_input": "வாழை இலையில் கருகல் நோய் வந்துள்ளது, என்ன மருந்து தெளிக்கலாம்?", "previous_context": None,
                "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "banana", "disease": "leaf blight"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["AGRICULTURAL_RAG"],
                "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Tamil natural query for banana leaf blight medicine"
            }]
        },
        {
            "id": "T_14", "category": "T", "domain": "NATURAL_SPEECH", "language": "marwari",
            "description": "Marwari: जीरे में छाछिया रोग री दवाई बताओ (Cumin powdery mildew medicine)",
            "turns": [{
                "turn_number": 1, "user_input": "म्हारा भाई, म्हारे जीरे में छाछिया रोग लाग ग्यो है, कीं देसी या अंग्रेजी दवाई बताओ।", "previous_context": None,
                "expected_intent": "agricultural_knowledge", "expected_entities": {"crop": "cumin", "disease": "powdery mildew (chachiya)"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["AGRICULTURAL_RAG"],
                "expected_tool_sequence": ["rag_search"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Marwari colloquial term 'छाछिया' for powdery mildew in cumin (jeera)"
            }]
        },
    ])

    return convs
