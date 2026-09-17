"""
Category I: Agricultural Knowledge / RAG (13 conversations)
Category J: Government Schemes (13 conversations)
Category K: Multi-Intent (14 conversations)
Languages: en, hi, hinglish, gu, mr, pa, bn, ta, te, kn, ml, marwari
"""

def get_knowledge_schemes_multiintent_conversations():
    convs = []

    # =========================================================================
    # I. RAG / AGRICULTURAL KNOWLEDGE (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "I_01", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "hi",
            "description": "Hindi: Gehun ki buwai kab karni chahiye aur beej dar kya honi chahiye?",
            "turns": [{
                "turn_number": 1, "user_input": "गेहूं की बुवाई का सही समय क्या है और प्रति हेक्टेयर बीज दर क्या होनी चाहिए?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Wheat sowing agronomy knowledge in Hindi"
            }]
        },
        {
            "id": "I_02", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "hinglish",
            "description": "Hinglish: Tomato mein fungal disease ka organic treatment kya hai?",
            "turns": [{
                "turn_number": 1, "user_input": "Tomato mein fungal disease ka organic treatment kya hai? Neem oil spray kaise karein?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": "tomato", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Organic fungus treatment in Hinglish"
            }]
        },
        {
            "id": "I_03", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "gu",
            "description": "Gujarati: કપાસમાં ગુલાબી ઇયળ નિયંત્રણ માટે ફેરોમોન ટ્રેપનો ઉપયોગ કેવી રીતે કરવો?",
            "turns": [{
                "turn_number": 1, "user_input": "કપાસમાં ગુલાબી ઇયળ નિયંત્રણ માટે ફેરોમોન ટ્રેપનો ઉપયોગ કેવી રીતે કરવો?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": "cotton", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Pheromone trap setup for pink bollworm in Gujarati"
            }]
        },
        {
            "id": "I_04", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "mr",
            "description": "Marathi: गांडूळ खत (वर्मीकंपोस्ट) तयार करण्याची योग्य पद्धत कोणती आहे?",
            "turns": [{
                "turn_number": 1, "user_input": "गांडूळ खत तयार करण्याची योग्य पद्धत कोणती आहे?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Vermicompost practice in Marathi"
            }]
        },
        {
            "id": "I_05", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "pa",
            "description": "Punjabi: ਕਣਕ ਵਿੱਚ ਯੂਰੀਆ ਖਾਦ ਪਾਉਣ ਦਾ ਸਹੀ ਸਮਾਂ ਕੀ ਹੈ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਕਣਕ ਵਿੱਚ ਯੂਰੀਆ ਖਾਦ ਪਾਉਣ ਦਾ ਸਹੀ ਸਮਾਂ ਕੀ ਹੈ?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Urea application timing in Punjabi"
            }]
        },
        {
            "id": "I_06", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "bn",
            "description": "Bengali: মাটিতে জৈব কার্বনের পরিমাণ কিভাবে বাড়ানো যায়?",
            "turns": [{
                "turn_number": 1, "user_input": "মাটিতে জৈব কার্বনের পরিমাণ কিভাবে বাড়ানো যায়?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Soil organic carbon enhancement in Bengali"
            }]
        },
        {
            "id": "I_07", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "ta",
            "description": "Tamil: சொட்டு நீர் பாசன முறையில் உரமிடுவது எப்படி?",
            "turns": [{
                "turn_number": 1, "user_input": "சொட்டு நீர் பாசன முறையில் உரமிடுவது (Fertigation) எப்படி?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Fertigation agronomy in Tamil"
            }]
        },
        {
            "id": "I_08", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "te",
            "description": "Telugu: పంట మార్పిడి వల్ల భూమికి కలిగే ప్రయోజనాలు ఏమిటి?",
            "turns": [{
                "turn_number": 1, "user_input": "పంట మార్పిడి వల్ల భూమికి కలిగే ప్రయోజనాలు ఏమిటి?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Crop rotation benefits in Telugu"
            }]
        },
        {
            "id": "I_09", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "kn",
            "description": "Kannada: ಬೀಜೋಪಚಾರ (Seed treatment) ಮಾಡುವುದು ಹೇಗೆ?",
            "turns": [{
                "turn_number": 1, "user_input": "ಬೀಜೋಪಚಾರ ಮಾಡುವುದು ಹೇಗೆ ಮತ್ತು ಅದರಿಂದ ಏನು ಲಾಭ?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Seed treatment methods in Kannada"
            }]
        },
        {
            "id": "I_10", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "ml",
            "description": "Malayalam: ജൈവ കീടനാശിനികൾ എങ്ങനെ വീട്ടിൽ ഉണ്ടാക്കാം?",
            "turns": [{
                "turn_number": 1, "user_input": "ജൈവ കീടനാശിനികൾ എങ്ങനെ വീട്ടിൽ ഉണ്ടാക്കാം?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Bio-pesticide preparation in Malayalam"
            }]
        },
        {
            "id": "I_11", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "marwari",
            "description": "Marwari: मिट्टी रो पीएच सुधारण वास्ते जिप्सम कीकर नाखणी?",
            "turns": [{
                "turn_number": 1, "user_input": "मिट्टी रो पीएच सुधारण वास्ते जिप्सम कीकर नाखणी? घणी खारी जमीन है।",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Gypsum application for saline soil in Marwari"
            }]
        },
        {
            "id": "I_12", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "en",
            "description": "English: How does mulching prevent soil moisture loss in summer?",
            "turns": [{
                "turn_number": 1, "user_input": "How does plastic and organic mulching prevent soil moisture loss during peak summer?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Mulching moisture retention physics in English"
            }]
        },
        {
            "id": "I_13", "category": "I", "domain": "RAG_KNOWLEDGE", "language": "hi",
            "description": "Hindi: Sarson mein chepa (aphid) ke prakop ko kaise rokein?",
            "turns": [{
                "turn_number": 1, "user_input": "सरसों में मोयला (चेपा) लग गया है, बिना नुकसान के रोकथाम कैसे करें?",
                "previous_context": None, "expected_intent": "general_agriculture",
                "expected_entities": {"crop": "mustard", "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["search_agricultural_knowledge"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Mustard aphid organic/chemical control in Hindi"
            }]
        }
    ])

    # =========================================================================
    # J. GOVERNMENT SCHEMES (13 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "J_01", "category": "J", "domain": "SCHEMES", "language": "hi",
            "description": "Hindi: PM Kisan Samman Nidhi ki agli kist kab aayegi aur eligibility kya hai?",
            "turns": [{
                "turn_number": 1, "user_input": "पीएम किसान सम्मान निधि योजना के तहत पात्रता क्या है और सहायता कैसे मिलती है?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "PM Kisan eligibility in Hindi"
            }]
        },
        {
            "id": "J_02", "category": "J", "domain": "SCHEMES", "language": "hinglish",
            "description": "Hinglish: Solar pump lagwane ke liye Kusum yojana mein subsidy kitni milti hai?",
            "turns": [{
                "turn_number": 1, "user_input": "Solar pump lagwane ke liye PM Kusum yojana mein subsidy kitni milti hai?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Kusum solar pump subsidy in Hinglish"
            }]
        },
        {
            "id": "J_03", "category": "J", "domain": "SCHEMES", "language": "gu",
            "description": "Gujarati: ટપક સિંચાઈ પદ્ધતિ માટે સરકાર તરફથી કેટલી સબસિડી મળે છે?",
            "turns": [{
                "turn_number": 1, "user_input": "ટપક સિંચાઈ પદ્ધતિ માટે સરકાર તરફથી કેટલી સબસિડી મળે છે?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Drip irrigation subsidy in Gujarati"
            }]
        },
        {
            "id": "J_04", "category": "J", "domain": "SCHEMES", "language": "mr",
            "description": "Marathi: ट्रॅक्टर खरेदीसाठी कृषी यांत्रिकीकरण योजनेत अनुदान कसे मिळवायचे?",
            "turns": [{
                "turn_number": 1, "user_input": "ट्रॅक्टर खरेदीसाठी कृषी यांत्रिकीकरण योजनेतून अनुदान कसे मिळवायचे?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Tractor subsidy in Marathi"
            }]
        },
        {
            "id": "J_05", "category": "J", "domain": "SCHEMES", "language": "pa",
            "description": "Punjabi: ਪਰਾਲੀ ਪ੍ਰਬੰਧਨ ਮਸ਼ੀਨਾਂ 'ਤੇ ਸਰਕਾਰ ਕਿੰਨੀ ਸਬਸਿਡੀ ਦੇ ਰਹੀ ਹੈ?",
            "turns": [{
                "turn_number": 1, "user_input": "ਪਰਾਲੀ ਪ੍ਰਬੰਧਨ ਮਸ਼ੀਨਾਂ 'ਤੇ ਸਰਕਾਰ ਕਿੰਨੀ ਸਬਸਿਡੀ ਦੇ ਰਹੀ ਹੈ?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Stubble management equipment subsidy in Punjabi"
            }]
        },
        {
            "id": "J_06", "category": "J", "domain": "SCHEMES", "language": "bn",
            "description": "Bengali: বাংলা শস্য বীমা যোজনায় আবেদনের শেষ তারিখ ও নিয়ম কি?",
            "turns": [{
                "turn_number": 1, "user_input": "বাংলা শস্য বীমা যোজনায় আবেদনের নিয়ম কি?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Crop insurance scheme in Bengali"
            }]
        },
        {
            "id": "J_07", "category": "J", "domain": "SCHEMES", "language": "ta",
            "description": "Tamil: பிரதம மந்திரி பயிர் காப்பீட்டுத் திட்டம் (PMFBY) பற்றி கூறவும்.",
            "turns": [{
                "turn_number": 1, "user_input": "பிரதம மந்திரி பயிர் காப்பீட்டுத் திட்டம் (PMFBY) பற்றி கூறவும்.",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ta", "expect_clarify": False,
                "notes": "PMFBY scheme in Tamil"
            }]
        },
        {
            "id": "J_08", "category": "J", "domain": "SCHEMES", "language": "te",
            "description": "Telugu: రైతు భరోసా పథకం అర్హతలు ఏమిటి?",
            "turns": [{
                "turn_number": 1, "user_input": "రైతు భరోసా పథకం అర్హతలు ఏమిటి?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "te", "expect_clarify": False,
                "notes": "Rythu Bharosa in Telugu"
            }]
        },
        {
            "id": "J_09", "category": "J", "domain": "SCHEMES", "language": "kn",
            "description": "Kannada: ಕೃಷಿ ಹೊಂಡ ನಿರ್ಮಾಣಕ್ಕೆ ಸರ್ಕಾರದ ಸಹಾಯಧನ ಸಿಗುತ್ತದೆಯೇ?",
            "turns": [{
                "turn_number": 1, "user_input": "ಕೃಷಿ ಹೊಂಡ ನಿರ್ಮಾಣಕ್ಕೆ ಸರ್ಕಾರದ ಸಹಾಯಧನ ಸಿಗುತ್ತದೆಯೇ?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Farm pond subsidy in Kannada"
            }]
        },
        {
            "id": "J_10", "category": "J", "domain": "SCHEMES", "language": "ml",
            "description": "Malayalam: സുഭിക്ഷ കേരളം പദ്ധതിയുടെ ആനുകൂല്യങ്ങൾ എന്തൊക്കെയാണ്?",
            "turns": [{
                "turn_number": 1, "user_input": "സുഭിക്ഷ കേരളം പദ്ധതിയുടെ ആനുകൂല്യങ്ങൾ എന്തൊക്കെയാണ്?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Subhiksha Keralam scheme in Malayalam"
            }]
        },
        {
            "id": "J_11", "category": "J", "domain": "SCHEMES", "language": "marwari",
            "description": "Marwari: तारबंदी योजना में सरकार कत्ती सब्सिडी देवे है?",
            "turns": [{
                "turn_number": 1, "user_input": "खेत री तारबंदी वास्ते सरकार कत्ती सब्सिडी देवे है? फॉर्म कीकर भरणो?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Rajasthan field fencing subsidy in Marwari"
            }]
        },
        {
            "id": "J_12", "category": "J", "domain": "SCHEMES", "language": "en",
            "description": "English: Are there any financial subsidies available for setting up a polyhouse?",
            "turns": [{
                "turn_number": 1, "user_input": "Are there any financial subsidies available for setting up a protected polyhouse or greenhouse?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "en", "expect_clarify": False,
                "notes": "Polyhouse horticulture mission subsidy in English"
            }]
        },
        {
            "id": "J_13", "category": "J", "domain": "SCHEMES", "language": "hi",
            "description": "Hindi: Kisan Credit Card (KCC) par interest rate kitna hota hai?",
            "turns": [{
                "turn_number": 1, "user_input": "किसान क्रेडिट कार्ड (KCC) पर ब्याज दर कितनी होती है और कैसे बनवाएं?",
                "previous_context": None, "expected_intent": "schemes",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["SCHEMES"],
                "expected_tool_sequence": ["get_government_schemes"], "expected_required_input": None,
                "expected_action": "ANSWER", "expected_response_language": "hi", "expect_clarify": False,
                "notes": "KCC credit facility and interest subvention in Hindi"
            }]
        }
    ])

    # =========================================================================
    # K. MULTI-INTENT (14 CONVERSATIONS)
    # =========================================================================
    convs.extend([
        {
            "id": "K_01", "category": "K", "domain": "MULTI_INTENT", "language": "hi",
            "description": "Hindi: Kal ka weather batao aur wheat ko paani dena hai ya nahi?",
            "turns": [{
                "turn_number": 1, "user_input": "कल जयपुर का मौसम कैसा रहेगा और गेहूं को पानी देना चाहिए या नहीं?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Jaipur",
                "expected_capabilities": ["WEATHER", "IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Weather + Irrigation multi-intent DAG in Hindi"
            }]
        },
        {
            "id": "K_02", "category": "K", "domain": "MULTI_INTENT", "language": "hinglish",
            "description": "Hinglish: Mandi rate batao Kota mein sarson ka aur 7 din ka forecast bhi.",
            "turns": [{
                "turn_number": 1, "user_input": "Mandi rate batao Kota mein sarson ka aur next 7 days ka price forecast bhi check karo.",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "mustard", "market": "Kota"},
                "expected_time_context": {"relative_day": "NEXT_7_DAYS", "time_of_day": None, "timeframe": "7 days"},
                "expected_location": "Kota",
                "expected_capabilities": ["MARKET_PRICE", "MARKET_FORECAST"],
                "expected_tool_sequence": ["get_mandi_prices", "get_price_forecast"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Current Mandi Price + 7-Day Forecast in Hinglish"
            }]
        },
        {
            "id": "K_03", "category": "K", "domain": "MULTI_INTENT", "language": "en",
            "description": "English: Check weather, irrigation and disaster risk in Udaipur.",
            "turns": [{
                "turn_number": 1, "user_input": "Check the current weather, irrigation recommendation for wheat, and flood disaster risk in Udaipur.",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Udaipur",
                "expected_capabilities": ["WEATHER", "IRRIGATION", "DISASTER_RISK"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice", "assess_disaster_risk"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "en", "expect_clarify": False,
                "notes": "Triple capability DAG: WEATHER + IRRIGATION + DISASTER"
            }]
        },
        {
            "id": "K_04", "category": "K", "domain": "MULTI_INTENT", "language": "mr",
            "description": "Marathi: लासलगाव कांद्याचा भाव आणि नाशिकचे उद्याचे हवामान दोन्ही सांगा.",
            "turns": [{
                "turn_number": 1, "user_input": "लासलगाव कांद्याचा आजचा भाव आणि नाशिकचे उद्याचे हवामान दोन्ही सांगा.",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "onion", "market": "Lasalgaon"},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Nashik",
                "expected_capabilities": ["MARKET_PRICE", "WEATHER"],
                "expected_tool_sequence": ["get_mandi_prices", "get_current_weather"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "mr", "expect_clarify": False,
                "notes": "Market Price + Weather in Marathi"
            }]
        },
        {
            "id": "K_05", "category": "K", "domain": "MULTI_INTENT", "language": "gu",
            "description": "Gujarati: કપાસનો ભાવ જણાવો અને કપાસમાં ગુલાબી ઇયળ નિયંત્રણની દવા પણ સૂચવો.",
            "turns": [{
                "turn_number": 1, "user_input": "રાજકોટમાં કપાસનો ભાવ જણાવો અને કપાસમાં ગુલાબી ઇયળ નિયંત્રણ માટે ઉપાય પણ સૂચવો.",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "cotton", "market": "Rajkot"},
                "expected_time_context": None, "expected_location": "Rajkot",
                "expected_capabilities": ["MARKET_PRICE", "RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["get_mandi_prices", "search_agricultural_knowledge"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "gu", "expect_clarify": False,
                "notes": "Market + Agronomy advice in Gujarati"
            }]
        },
        {
            "id": "K_06", "category": "K", "domain": "MULTI_INTENT", "language": "pa",
            "description": "Punjabi: ਲੁਧਿਆਣੇ ਦਾ ਮੌਸਮ ਦੱਸੋ ਅਤੇ ਝੋਨੇ ਲਈ ਸਿੰਚਾਈ ਦੀ ਸਲਾਹ ਦਿਓ।",
            "turns": [{
                "turn_number": 1, "user_input": "ਲੁਧਿਆਣੇ ਦਾ ਮੌਸਮ ਦੱਸੋ ਅਤੇ ਝੋਨੇ ਲਈ ਸਿੰਚਾਈ ਦੀ ਸਲਾਹ ਦਿਓ।",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": "paddy", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Ludhiana",
                "expected_capabilities": ["WEATHER", "IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "pa", "expect_clarify": False,
                "notes": "Weather + Irrigation in Punjabi"
            }]
        },
        {
            "id": "K_07", "category": "K", "domain": "MULTI_INTENT", "language": "bn",
            "description": "Bengali: মেদিনীপুরের আবহাওয়া কেমন থাকবে এবং আলুর বর্তমান বাজার দর কত?",
            "turns": [{
                "turn_number": 1, "user_input": "মেদিনীপুরের আবহাওয়া কেমন থাকবে এবং আলুর বর্তমান বাজার দর কত?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": "potato", "market": "Medinipur"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Medinipur",
                "expected_capabilities": ["WEATHER", "MARKET_PRICE"],
                "expected_tool_sequence": ["get_current_weather", "get_mandi_prices"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "bn", "expect_clarify": False,
                "notes": "Weather + Market in Bengali"
            }]
        },
        {
            "id": "K_08", "category": "K", "domain": "MULTI_INTENT", "language": "ta",
            "description": "Tamil: தஞ்சாவூர் வானிலை மற்றும் நெல் பயிருக்கான பாசன ஆலோசனையை வழங்கவும்.",
            "turns": [{
                "turn_number": 1, "user_input": "தஞ்சாவூர் வானிலை மற்றும் நெல் பயிருக்கான பாசன ஆலோசனையை வழங்கவும்.",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": "paddy", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Thanjavur",
                "expected_capabilities": ["WEATHER", "IRRIGATION"],
                "expected_tool_sequence": ["get_current_weather", "get_irrigation_advice"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "ta", "expect_clarify": False,
                "notes": "Weather + Irrigation in Tamil"
            }]
        },
        {
            "id": "K_09", "category": "K", "domain": "MULTI_INTENT", "language": "te",
            "description": "Telugu: గుంటూరులో మిర్చి ధర ఎంత మరియు వర్షం పడే అవకాశం ఉందా?",
            "turns": [{
                "turn_number": 1, "user_input": "గుంటూరులో మిర్చి ధర ఎంత మరియు రేపు వర్షం పడే అవకాశం ఉందా?",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "chilli", "market": "Guntur"},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Guntur",
                "expected_capabilities": ["MARKET_PRICE", "WEATHER"],
                "expected_tool_sequence": ["get_mandi_prices", "get_current_weather"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "te", "expect_clarify": False,
                "notes": "Market Price + Rain probability in Telugu"
            }]
        },
        {
            "id": "K_10", "category": "K", "domain": "MULTI_INTENT", "language": "kn",
            "description": "Kannada: ಶಿವಮೊಗ್ಗ ಹವಾಮಾನ ಮತ್ತು ಅಡಿಕೆ ಮಾರುಕಟ್ಟೆ ದರ ಎರಡನ್ನೂ ತಿಳಿಸಿ.",
            "turns": [{
                "turn_number": 1, "user_input": "ಶಿವಮೊಗ್ಗ ಹವಾಮಾನ ಮತ್ತು ಅಡಿಕೆ ಮಾರುಕಟ್ಟೆ ದರ ಎರಡನ್ನೂ ತಿಳಿಸಿ.",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": "arecanut", "market": "Shivamogga"},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Shivamogga",
                "expected_capabilities": ["WEATHER", "MARKET_PRICE"],
                "expected_tool_sequence": ["get_current_weather", "get_mandi_prices"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "kn", "expect_clarify": False,
                "notes": "Weather + Market in Kannada"
            }]
        },
        {
            "id": "K_11", "category": "K", "domain": "MULTI_INTENT", "language": "ml",
            "description": "Malayalam: വയനാട്ടിൽ മഴയുടെ സാധ്യതയും ഏലക്കായുടെ ഇന്നത്തെ വിലയും പറയൂ.",
            "turns": [{
                "turn_number": 1, "user_input": "വയനാട്ടിൽ മഴയുടെ സാധ്യതയും ഏലക്കായുടെ ഇന്നത്തെ വിലയും പറയൂ.",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": "cardamom", "market": None},
                "expected_time_context": {"relative_day": "TODAY", "time_of_day": None, "timeframe": "today"},
                "expected_location": "Wayanad",
                "expected_capabilities": ["WEATHER", "MARKET_PRICE"],
                "expected_tool_sequence": ["get_current_weather", "get_mandi_prices"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "ml", "expect_clarify": False,
                "notes": "Rain + Cardamom market in Malayalam"
            }]
        },
        {
            "id": "K_12", "category": "K", "domain": "MULTI_INTENT", "language": "marwari",
            "description": "Marwari: काल जोधपुर रो मौसम बताओ और जीरा रो भाव भी बताओ।",
            "turns": [{
                "turn_number": 1, "user_input": "काल जोधपुर रो मौसम कीकर रेवेला और जीरा रो भाव कांई है मंडी में?",
                "previous_context": None, "expected_intent": "weather",
                "expected_entities": {"crop": "cumin", "market": None},
                "expected_time_context": {"relative_day": "TOMORROW", "time_of_day": None, "timeframe": "tomorrow"},
                "expected_location": "Jodhpur",
                "expected_capabilities": ["WEATHER", "MARKET_PRICE"],
                "expected_tool_sequence": ["get_current_weather", "get_mandi_prices"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Weather + Cumin price in Marwari"
            }]
        },
        {
            "id": "K_13", "category": "K", "domain": "MULTI_INTENT", "language": "hi",
            "description": "Hindi: Heavy rain hai, flood risk check karo aur mujhe batao crop ko kaise protect karu.",
            "turns": [{
                "turn_number": 1, "user_input": "भारी बारिश हो रही है, बाढ़ का खतरा जांचो और फसल को बचाने के उपाय बताओ।",
                "previous_context": None, "expected_intent": "disaster",
                "expected_entities": {"crop": None, "market": None},
                "expected_time_context": None, "expected_location": None,
                "expected_capabilities": ["DISASTER_RISK", "RAG_KNOWLEDGE"],
                "expected_tool_sequence": ["assess_disaster_risk", "search_agricultural_knowledge"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Disaster risk + RAG crop protection workflow"
            }]
        },
        {
            "id": "K_14", "category": "K", "domain": "MULTI_INTENT", "language": "hinglish",
            "description": "Hinglish: Current mandi price check karo, forecast dekho aur batao sell karna chahiye ya hold.",
            "turns": [{
                "turn_number": 1, "user_input": "Current mandi price check karo, 7-day forecast dekho aur batao wheat sell karna chahiye ya hold.",
                "previous_context": None, "expected_intent": "market",
                "expected_entities": {"crop": "wheat", "market": None},
                "expected_time_context": {"relative_day": "NEXT_7_DAYS", "time_of_day": None, "timeframe": "7 days"},
                "expected_location": None,
                "expected_capabilities": ["MARKET_PRICE", "MARKET_FORECAST"],
                "expected_tool_sequence": ["get_mandi_prices", "get_price_forecast"],
                "expected_required_input": None, "expected_action": "ANSWER",
                "expected_response_language": "hi", "expect_clarify": False,
                "notes": "Market Current + Forecast + Advisory Decision in Hinglish"
            }]
        }
    ])

    return convs
