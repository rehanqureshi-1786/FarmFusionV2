"""
Category O: Missing Required Input (13 conversations)
Category P: Ambiguous Questions (13 conversations)
Category Q: Out-of-Scope Questions (14 conversations)
Languages: en, hi, hinglish, gu, mr, pa, bn, ta, te, kn, ml, marwari
"""

def get_missing_ambiguous_outofscope_conversations():
    convs = []

    # =========================================================================
    # O. MISSING REQUIRED INPUT (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "O_01", "category": "O", "domain": "MISSING_INPUT", "language": "en",
            "description": "English: Identify my crop disease without image",
            "turns": [{
                "turn_number": 1, "user_input": "Can you diagnose the disease affecting my crop right now?", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {"crop": None, "disease": None},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "REQUEST_IMAGE", "expected_response_language": "en", "expect_clarify": True,
                "notes": "Disease workflow strictly requires leaf image; must navigate or prompt farmer to upload photo"
            }]
        },
        {
            "id": "O_02", "category": "O", "domain": "MISSING_INPUT", "language": "hi",
            "description": "Hindi: Kal mausam kaisa rahega without location context",
            "turns": [{
                "turn_number": 1, "user_input": "कल मौसम कैसा रहेगा?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW", "timeframe": "tomorrow"},
                "expected_location": None, "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": [], "expected_required_input": "location",
                "expected_action": "REQUEST_LOCATION", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "No location provided in query or profile; must ask which district/village"
            }]
        },
        {
            "id": "O_03", "category": "O", "domain": "MISSING_INPUT", "language": "hinglish",
            "description": "Hinglish: Expert ko call lagao without phone number or contact",
            "turns": [{
                "turn_number": 1, "user_input": "Bhai turant kisan expert ko call lagao mujhe baat karni hai.", "previous_context": None,
                "expected_intent": "calling", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": [], "expected_required_input": "phone_number",
                "expected_action": "REQUEST_PHONE_NUMBER", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "Calling requested with zero contact details; must prompt for phone number without inventing one"
            }]
        },
        {
            "id": "O_04", "category": "O", "domain": "MISSING_INPUT", "language": "gu",
            "description": "Gujarati: પાક માં રોગ ઓળખો (Disease diagnosis without photo)",
            "turns": [{
                "turn_number": 1, "user_input": "મારા પાંદડા બગડી ગયા છે, કયો રોગ છે તે કહો.", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {"crop": None},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "REQUEST_IMAGE", "expected_response_language": "gu", "expect_clarify": True,
                "notes": "Gujarati missing image request for crop disease"
            }]
        },
        {
            "id": "O_05", "category": "O", "domain": "MISSING_INPUT", "language": "mr",
            "description": "Marathi: कोणतं पीक घेऊ? (Crop rec without soil or location)",
            "turns": [{
                "turn_number": 1, "user_input": "मी माझ्या शेतात कोणतं पीक लावू? सांगा ना.", "previous_context": None,
                "expected_intent": "crop_recommendation", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": [], "expected_required_input": "soil_or_location",
                "expected_action": "REQUEST_INPUT", "expected_response_language": "mr", "expect_clarify": True,
                "notes": "Cannot run ML crop model without at least soil type or district agro-climate"
            }]
        },
        {
            "id": "O_06", "category": "O", "domain": "MISSING_INPUT", "language": "pa",
            "description": "Punjabi: ਅਫਸਰ ਨੂੰ ਫੋਨ ਮਿਲਾਓ (Call officer without contact)",
            "turns": [{
                "turn_number": 1, "user_input": "ਖੇਤੀਬਾੜੀ ਅਫਸਰ ਨੂੰ ਹੁਣੇ ਫੋਨ ਮਿਲਾਓ ਜੀ।", "previous_context": None,
                "expected_intent": "calling", "expected_entities": {"recipient": "agriculture_officer"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": [], "expected_required_input": "phone_number",
                "expected_action": "REQUEST_PHONE_NUMBER", "expected_response_language": "pa", "expect_clarify": True,
                "notes": "Punjabi request to call officer without provided phone number"
            }]
        },
        {
            "id": "O_07", "category": "O", "domain": "MISSING_INPUT", "language": "bn",
            "description": "Bengali: কাল বৃষ্টি হবে কিনা বলো (Tomorrow rain without location)",
            "turns": [{
                "turn_number": 1, "user_input": "কালকে বৃষ্টি হবে কি হবে না?", "previous_context": None,
                "expected_intent": "weather", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW", "timeframe": "tomorrow"},
                "expected_location": None, "expected_capabilities": ["WEATHER"],
                "expected_tool_sequence": [], "expected_required_input": "location",
                "expected_action": "REQUEST_LOCATION", "expected_response_language": "bn", "expect_clarify": True,
                "notes": "Bengali missing location for weather forecast"
            }]
        },
        {
            "id": "O_08", "category": "O", "domain": "MISSING_INPUT", "language": "ta",
            "description": "Tamil: இந்த பயிருக்கு என்ன நோய் என்று கண்டுபிடி (Diagnose disease no pic)",
            "turns": [{
                "turn_number": 1, "user_input": "என் பயிரில் என்ன நோய் தாக்கியுள்ளது என்று கண்டுபிடி.", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "REQUEST_IMAGE", "expected_response_language": "ta", "expect_clarify": True,
                "notes": "Tamil request for disease detection without leaf image"
            }]
        },
        {
            "id": "O_09", "category": "O", "domain": "MISSING_INPUT", "language": "te",
            "description": "Telugu: నా పొలానికి ఏ పంట వేయాలి? (Crop rec no soil/climate)",
            "turns": [{
                "turn_number": 1, "user_input": "నా పొలంలో ఏ పంట వేస్తే బాగుంటుంది?", "previous_context": None,
                "expected_intent": "crop_recommendation", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": [], "expected_required_input": "soil_or_location",
                "expected_action": "REQUEST_INPUT", "expected_response_language": "te", "expect_clarify": True,
                "notes": "Telugu crop recommendation missing soil properties and location"
            }]
        },
        {
            "id": "O_10", "category": "O", "domain": "MISSING_INPUT", "language": "kn",
            "description": "Kannada: ತಜ್ಞರಿಗೆ ಕಾಲ್ ಮಾಡಿ (Call expert without phone)",
            "turns": [{
                "turn_number": 1, "user_input": "ಕೃಷಿ ತಜ್ಞರಿಗೆ ಈಗಲೇ ಕರೆ ಮಾಡಿ.", "previous_context": None,
                "expected_intent": "calling", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["CALLING"],
                "expected_tool_sequence": [], "expected_required_input": "phone_number",
                "expected_action": "REQUEST_PHONE_NUMBER", "expected_response_language": "kn", "expect_clarify": True,
                "notes": "Kannada call request without destination number"
            }]
        },
        {
            "id": "O_11", "category": "O", "domain": "MISSING_INPUT", "language": "ml",
            "description": "Malayalam: ഇലകൾ മഞ്ഞനിറമാകുന്നു (Leaves yellowing no image)",
            "turns": [{
                "turn_number": 1, "user_input": "എന്റെ ചെടിയുടെ ഇലകൾ മഞ്ഞനിറമാകുന്നു, രോഗം പരിശോധിക്കൂ.", "previous_context": None,
                "expected_intent": "disease_detection", "expected_entities": {"symptom": "yellowing"},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["DISEASE_DETECTION"],
                "expected_tool_sequence": [], "expected_required_input": "image",
                "expected_action": "REQUEST_IMAGE", "expected_response_language": "ml", "expect_clarify": True,
                "notes": "Malayalam disease symptom without image"
            }]
        },
        {
            "id": "O_12", "category": "O", "domain": "MISSING_INPUT", "language": "marwari",
            "description": "Marwari: म्हारे खेत में कीं फसल बोऊं? (Crop rec missing soil)",
            "turns": [{
                "turn_number": 1, "user_input": "म्हारा भाई, म्हारे खेत में अबार कीं फसल बोऊं? कोई सलाह दे।", "previous_context": None,
                "expected_intent": "crop_recommendation", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": ["CROP_RECOMMENDATION"],
                "expected_tool_sequence": [], "expected_required_input": "soil_or_location",
                "expected_action": "REQUEST_INPUT", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "Marwari crop suggestion without specifying soil type, rainfall, or village"
            }]
        },
        {
            "id": "O_13", "category": "O", "domain": "MISSING_INPUT", "language": "en",
            "description": "English: What is the current market price? (Commodity missing)",
            "turns": [{
                "turn_number": 1, "user_input": "What is the mandi price today in my nearest market?", "previous_context": None,
                "expected_intent": "mandi_prices", "expected_entities": {"crop": None},
                "expected_time_context": {"relative_day": "TODAY", "timeframe": "today"},
                "expected_location": None, "expected_capabilities": ["MANDI_PRICE"],
                "expected_tool_sequence": [], "expected_required_input": "commodity",
                "expected_action": "REQUEST_INPUT", "expected_response_language": "en", "expect_clarify": True,
                "notes": "Mandi lookup missing crop/commodity name; cannot query price database"
            }]
        },
    ])

    # =========================================================================
    # P. AMBIGUOUS QUESTIONS (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "P_01", "category": "P", "domain": "AMBIGUOUS", "language": "hi",
            "description": "Hindi: Rate batao (Extremely vague price query)",
            "turns": [{
                "turn_number": 1, "user_input": "रेट बताओ।", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "crop_and_market",
                "expected_action": "CLARIFY", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "Extremely brief; clarify which commodity and mandi market"
            }]
        },
        {
            "id": "P_02", "category": "P", "domain": "AMBIGUOUS", "language": "hinglish",
            "description": "Hinglish: Kal kaisa rahega? (Weather or price or market?)",
            "turns": [{
                "turn_number": 1, "user_input": "Kal kaisa rahega?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": {"relative_day": "TOMORROW"}, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "Could mean tomorrow's weather, market prices, or general farming; must clarify"
            }]
        },
        {
            "id": "P_03", "category": "P", "domain": "AMBIGUOUS", "language": "en",
            "description": "English: What should I do with this?",
            "turns": [{
                "turn_number": 1, "user_input": "What should I do with this?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "en", "expect_clarify": True,
                "notes": "Vague pronoun 'this' without context or uploaded media"
            }]
        },
        {
            "id": "P_04", "category": "P", "domain": "AMBIGUOUS", "language": "hi",
            "description": "Hindi: Ye sahi hai kya? (Is this correct/okay?)",
            "turns": [{
                "turn_number": 1, "user_input": "ये सही है क्या?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "No antecedent provided; ask farmer what practice, dose, or decision they refer to"
            }]
        },
        {
            "id": "P_05", "category": "P", "domain": "AMBIGUOUS", "language": "en",
            "description": "English: Help me with my farm",
            "turns": [{
                "turn_number": 1, "user_input": "Help me with my farm.", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "en", "expect_clarify": True,
                "notes": "Broad greeting/help request; provide overview of copilot capabilities"
            }]
        },
        {
            "id": "P_06", "category": "P", "domain": "AMBIGUOUS", "language": "gu",
            "description": "Gujarati: શું કરું હવે? (What to do now?)",
            "turns": [{
                "turn_number": 1, "user_input": "હું હવે શું કરું? કઈ ખબર નથી પડતી.", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "gu", "expect_clarify": True,
                "notes": "Gujarati ambiguous expression of confusion"
            }]
        },
        {
            "id": "P_07", "category": "P", "domain": "AMBIGUOUS", "language": "mr",
            "description": "Marathi: याचं काय करू? (What to do with this?)",
            "turns": [{
                "turn_number": 1, "user_input": "याचं आता काय करू सांगा?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "mr", "expect_clarify": True,
                "notes": "Marathi ambiguous deictic reference"
            }]
        },
        {
            "id": "P_08", "category": "P", "domain": "AMBIGUOUS", "language": "pa",
            "description": "Punjabi: ਇਹ ਠੀਕ ਹੈ? (Is this okay?)",
            "turns": [{
                "turn_number": 1, "user_input": "ਇਹ ਤਰੀਕਾ ਠੀਕ ਹੈ ਕਿ ਨਹੀਂ?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "pa", "expect_clarify": True,
                "notes": "Punjabi ambiguous reference to unknown method"
            }]
        },
        {
            "id": "P_09", "category": "P", "domain": "AMBIGUOUS", "language": "bn",
            "description": "Bengali: কোনটা ভালো হবে? (Which one is better?)",
            "turns": [{
                "turn_number": 1, "user_input": "কোনটা ভালো হবে বলুন তো?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "bn", "expect_clarify": True,
                "notes": "Bengali comparative question without options"
            }]
        },
        {
            "id": "P_10", "category": "P", "domain": "AMBIGUOUS", "language": "ta",
            "description": "Tamil: என்ன பிரச்சனை? (What's the problem?)",
            "turns": [{
                "turn_number": 1, "user_input": "என்ன பிரச்சனை என்று சொல்லுங்கள்?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "ta", "expect_clarify": True,
                "notes": "Tamil ambiguous question about problem without context"
            }]
        },
        {
            "id": "P_11", "category": "P", "domain": "AMBIGUOUS", "language": "te",
            "description": "Telugu: రేటు ఎంత? (What is the rate?)",
            "turns": [{
                "turn_number": 1, "user_input": "మార్కెట్లో రేటు ఎంత నడుస్తోంది?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "crop",
                "expected_action": "CLARIFY", "expected_response_language": "te", "expect_clarify": True,
                "notes": "Telugu rate inquiry without specifying which crop"
            }]
        },
        {
            "id": "P_12", "category": "P", "domain": "AMBIGUOUS", "language": "kn",
            "description": "Kannada: ಏನು ಮಾಡಬೇಕು? (What should be done?)",
            "turns": [{
                "turn_number": 1, "user_input": "ನನ್ನ ತೋಟದಲ್ಲಿ ಏನು ಮಾಡಬೇಕು?", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "kn", "expect_clarify": True,
                "notes": "Kannada vague farm management query"
            }]
        },
        {
            "id": "P_13", "category": "P", "domain": "AMBIGUOUS", "language": "marwari",
            "description": "Marwari: कीं समझ कोनी आ रह्यो (Cannot understand what to do)",
            "turns": [{
                "turn_number": 1, "user_input": "म्हारो कछु समझ कोनी आ रह्यो, कीं तो बोलो।", "previous_context": None,
                "expected_intent": "ambiguous_clarify", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": "clarification",
                "expected_action": "CLARIFY", "expected_response_language": "hi", "expect_clarify": True,
                "notes": "Marwari general expression of distress without specifics"
            }]
        },
    ])

    # =========================================================================
    # Q. OUT-OF-SCOPE (14 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "Q_01", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "en",
            "description": "English: Who won yesterday's cricket match?",
            "turns": [{
                "turn_number": 1, "user_input": "Who won yesterday's cricket match between India and Australia?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Sports scores out of scope for agricultural assistant; decline politely and offer farm help"
            }]
        },
        {
            "id": "Q_02", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "hinglish",
            "description": "Hinglish: Write me a Python program for web scraping",
            "turns": [{
                "turn_number": 1, "user_input": "Ek Python script likh ke do jo Flipkart se price scrape kare.", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Software coding request out of scope; maintain agriculture focus"
            }]
        },
        {
            "id": "Q_03", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "hi",
            "description": "Hindi: What's the capital of France?",
            "turns": [{
                "turn_number": 1, "user_input": "फ्रांस की राजधानी क्या है?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "World geography trivia out of scope"
            }]
        },
        {
            "id": "Q_04", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "hinglish",
            "description": "Hinglish: Tell me a joke",
            "turns": [{
                "turn_number": 1, "user_input": "Bhai ek mast sa chutkula sunao na maza aa jaye.", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "General entertainment/jokes out of scope"
            }]
        },
        {
            "id": "Q_05", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "en",
            "description": "English: Book me a movie ticket for Sunday",
            "turns": [{
                "turn_number": 1, "user_input": "Book two movie tickets for the evening show this Sunday near me.", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Ticketing/commercial bookings out of scope"
            }]
        },
        {
            "id": "Q_06", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "hinglish",
            "description": "Hinglish: What's Bitcoin price today?",
            "turns": [{
                "turn_number": 1, "user_input": "Aaj Bitcoin aur Ethereum ka price kya chal raha hai crypto market mein?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Cryptocurrency prices out of scope; do not confuse with agri commodities"
            }]
        },
        {
            "id": "Q_07", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "gu",
            "description": "Gujarati: શેરબજારમાં કયો શેર ખરીદવો? (Stock market advice)",
            "turns": [{
                "turn_number": 1, "user_input": "શેરબજારમાં આજે કયો સ્ટોક ખરીદવો સારો રહેશે?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Stock trading advice out of scope"
            }]
        },
        {
            "id": "Q_08", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "mr",
            "description": "Marathi: नवीन मोबाईल कोणता चांगला आहे? (Smartphone recommendation)",
            "turns": [{
                "turn_number": 1, "user_input": "मला १५ हजार रुपयांत नवीन मोबाईल कोणता चांगला मिळेल?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Consumer electronics recommendation out of scope"
            }]
        },
        {
            "id": "Q_09", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "pa",
            "description": "Punjabi: ਕਾਰ ਰਿਪੇਅਰ ਕਿਵੇਂ ਕਰੀਏ? (Car engine repair)",
            "turns": [{
                "turn_number": 1, "user_input": "ਮੇਰੀ ਕਾਰ ਦਾ ਇੰਜਣ ਗਰਮ ਹੋ ਰਿਹਾ ਹੈ, ਕਿਵੇਂ ਠੀਕ ਕਰਾਂ?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Automobile repair advice out of scope"
            }]
        },
        {
            "id": "Q_10", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "bn",
            "description": "Bengali: নতুন সিনেমার রিভিউ বলো (Movie review)",
            "turns": [{
                "turn_number": 1, "user_input": "নতুন সিনেমাটা কেমন হয়েছে? রিভিউ বলো তো।", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Film reviews out of scope"
            }]
        },
        {
            "id": "Q_11", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "ta",
            "description": "Tamil: மனித உடலின் உறுப்புகள் (Human biology query)",
            "turns": [{
                "turn_number": 1, "user_input": "மனித உடலில் எத்தனை எலும்புகள் உள்ளன?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Human anatomy trivia out of scope"
            }]
        },
        {
            "id": "Q_12", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "te",
            "description": "Telugu: రైలు టికెట్ బుకింగ్ (Train ticket booking)",
            "turns": [{
                "turn_number": 1, "user_input": "హైదరాబాద్ నుండి ఢిల్లీకి రైలు టికెట్ బుక్ చేయి.", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Train ticket booking out of scope"
            }]
        },
        {
            "id": "Q_13", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "kn",
            "description": "Kannada: ರಾಜಕೀಯ ಸುದ್ದಿ (Political election debate)",
            "turns": [{
                "turn_number": 1, "user_input": "ಮುಂದಿನ ಚುನಾವಣೆಯಲ್ಲಿ ಯಾರು ಗೆಲ್ಲುತ್ತಾರೆ?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Political election forecasting out of scope"
            }]
        },
        {
            "id": "Q_14", "category": "Q", "domain": "OUT_OF_SCOPE", "language": "ml",
            "description": "Malayalam: ഇംഗ്ലീഷ് ഗ്രാമർ പഠിപ്പിക്കൂ (English grammar lesson)",
            "turns": [{
                "turn_number": 1, "user_input": "എനിക്ക് ഇംഗ്ലീഷ് വ്യാകരണം പഠിപ്പിച്ചു തരാമോ?", "previous_context": None,
                "expected_intent": "out_of_scope", "expected_entities": {},
                "expected_time_context": None, "expected_location": None, "expected_capabilities": [],
                "expected_tool_sequence": [], "expected_required_input": None,
                "expected_action": "DECLINE_POLITELY", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Language grammar tutoring out of scope"
            }]
        },
    ])

    return convs
