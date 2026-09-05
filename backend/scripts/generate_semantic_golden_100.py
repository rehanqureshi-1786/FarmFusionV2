"""
Script to generate the Phase F3 100-query semantic evaluation golden dataset.
"""
import json
from pathlib import Path

queries = [
    # 1. WEATHER (1-10)
    {"id": "w_01", "query": "आज मौसम कैसा रहेगा जयपुर में?", "language": "hi", "expected_intent": "weather", "expected_crop": None, "expected_market": "Jaipur", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_02", "query": "Will it rain tomorrow in Udaipur?", "language": "en", "expected_intent": "weather", "expected_crop": None, "expected_market": "Udaipur", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_03", "query": "aaj barish hogi kya kota mein?", "language": "hi", "expected_intent": "weather", "expected_crop": None, "expected_market": "Kota", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_04", "query": "આજે અમદાવાદમાં વરસાદ પડશે?", "language": "gu", "expected_intent": "weather", "expected_crop": None, "expected_market": "Ahmedabad", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_05", "query": "पुण्यात आज हवामान कसे राहील?", "language": "mr", "expected_intent": "weather", "expected_crop": None, "expected_market": "Pune", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_06", "query": "ਕੱਲ੍ਹ ਲੁਧਿਆਣੇ ਵਿੱਚ ਮੌਸਮ ਕਿਵੇਂ ਰਹੇਗਾ?", "language": "pa", "expected_intent": "weather", "expected_crop": None, "expected_market": "Ludhiana", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_07", "query": "আজকে বৃষ্টি হবে কি কলকাতায়?", "language": "bn", "expected_intent": "weather", "expected_crop": None, "expected_market": "Kolkata", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_08", "query": "चेन्नई में अगले 3 दिन का तापमान क्या रहेगा?", "language": "hi", "expected_intent": "weather", "expected_crop": None, "expected_market": "Chennai", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_09", "query": "खम्मा घणी, आज मौसम कांई रैवेला जोधपुर में?", "language": "hi", "dialect": "marwari", "expected_intent": "weather", "expected_crop": None, "expected_market": "Jodhpur", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},
    {"id": "w_10", "query": "क्या कल तेज हवा या धूप निकलेगी दिल्ली में?", "language": "hi", "expected_intent": "weather", "expected_crop": None, "expected_market": "Delhi", "expected_capabilities": ["WEATHER"], "expected_required_input": "NONE"},

    # 2. SMART IRRIGATION & COMPOUND IRRIGATION ADVISORY (11-20)
    {"id": "i_01", "query": "कल बारिश होगी तो क्या आज गेहूं में पानी देना चाहिए?", "language": "hi", "expected_intent": "irrigation_advisory", "expected_crop": "Wheat", "expected_capabilities": ["WEATHER", "SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_02", "query": "Should I irrigate wheat today if it might rain tomorrow?", "language": "en", "expected_intent": "irrigation_advisory", "expected_crop": "Wheat", "expected_capabilities": ["WEATHER", "SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_03", "query": "kal rain hone wali hai kya wheat ko water karun?", "language": "hi", "expected_intent": "irrigation_advisory", "expected_crop": "Wheat", "expected_capabilities": ["WEATHER", "SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_04", "query": "धान में अगली सिंचाई कब करनी चाहिए?", "language": "hi", "expected_intent": "smart_irrigation", "expected_crop": "Paddy", "expected_capabilities": ["SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_05", "query": "કપાસના પાકમાં પાણી ક્યારે આપવું?", "language": "gu", "expected_intent": "smart_irrigation", "expected_crop": "Cotton", "expected_capabilities": ["SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_06", "query": "जमीन में नमी कम है, क्या मक्का में पानी दूं?", "language": "hi", "expected_intent": "smart_irrigation", "expected_crop": "Maize", "expected_capabilities": ["SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_07", "query": "बारिश आने वाली है, क्या मुझे खेत में सिंचाई रोक देनी चाहिए?", "language": "hi", "expected_intent": "irrigation_advisory", "expected_crop": None, "expected_capabilities": ["WEATHER", "SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_08", "query": "सरसों की फसल में पहली सिंचाई कब करें?", "language": "hi", "expected_intent": "smart_irrigation", "expected_crop": "Mustard", "expected_capabilities": ["SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_09", "query": "चना में पानी देने का सही समय क्या है?", "language": "hi", "expected_intent": "smart_irrigation", "expected_crop": "Gram", "expected_capabilities": ["SMART_IRRIGATION"], "expected_required_input": "NONE"},
    {"id": "i_10", "query": "Does my potato crop need irrigation this evening?", "language": "en", "expected_intent": "smart_irrigation", "expected_crop": "Potato", "expected_capabilities": ["SMART_IRRIGATION"], "expected_required_input": "NONE"},

    # 3. DISASTER RISK (21-30)
    {"id": "d_01", "query": "Flood ka risk hai kya aur kya karna chahiye?", "language": "hi", "expected_intent": "disaster_risk", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_02", "query": "क्या अगले 7 दिनों में जयपुर में बाढ़ का खतरा है?", "language": "hi", "expected_intent": "disaster_risk", "expected_market": "Jaipur", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_03", "query": "Is there any cyclone warning near Gujarat coast?", "language": "en", "expected_intent": "disaster_risk", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_04", "query": "વાવાઝોડું કે ભારે વરસાદનું કોઈ જોખમ છે?", "language": "gu", "expected_intent": "disaster_risk", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_05", "query": "पुढील आठवड्यात दुष्काळाची किंवा अतिवृष्टीची शक्यता आहे का?", "language": "mr", "expected_intent": "disaster_risk", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_06", "query": "ਕੀ ਆਉਣ ਵਾਲੇ ਦਿਨਾਂ ਵਿੱਚ ਹੜ੍ਹ ਦਾ ਕੋਈ ਖ਼ਤਰਾ ਹੈ?", "language": "pa", "expected_intent": "disaster_risk", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_07", "query": "Heavy storm alert in Bhopal area?", "language": "en", "expected_intent": "disaster_risk", "expected_market": "Bhopal", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_08", "query": "क्या अगले हफ्ते सूखा पड़ने की कोई चेतावनी है?", "language": "hi", "expected_intent": "disaster_risk", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_09", "query": "आंधी तूफान का कोई अलर्ट है क्या?", "language": "hi", "expected_intent": "disaster_risk", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "d_10", "query": "Severe weather calamity risk in coastal areas?", "language": "en", "expected_intent": "disaster_risk", "expected_capabilities": ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"], "expected_required_input": "NONE"},

    # 4. CROP RECOMMENDATION (31-40)
    {"id": "c_01", "query": "काली मिट्टी में कौन सी फसल लगाएं?", "language": "hi", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_02", "query": "Which crop is best for sandy soil in Rajasthan?", "language": "en", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_03", "query": "रेतीली मिट्टी में क्या बोएं?", "language": "hi", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_04", "query": "लाल मिट्टी के लिए सबसे अच्छी फसल कौन सी है?", "language": "hi", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_05", "query": "કાળી જમીનમાં કયો પાક સારો થશે?", "language": "gu", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_06", "query": "खेत में इस मौसम में क्या बोना फायदेमंद रहेगा?", "language": "hi", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_07", "query": "दोमट मिट्टी में रबी में क्या लगाएं?", "language": "hi", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_08", "query": "What crop to grow in Kharif season?", "language": "en", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_09", "query": "चिकनी मिट्टी के लिए फसल की सलाह दो", "language": "hi", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},
    {"id": "c_10", "query": "Recommend optimal crops for alluvial soil with high rainfall", "language": "en", "expected_intent": "crop_recommendation", "expected_capabilities": ["CROP_RECOMMENDATION"], "expected_required_input": "NONE"},

    # 5. DISEASE DETECTION WITH REQUIRED INPUT GATE (41-50)
    {"id": "dis_01", "query": "Meri gehun ki fasal mein kaunsi bimari hai?", "language": "hi", "expected_intent": "disease_detection", "expected_crop": "Wheat", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_02", "query": "What disease does my tomato plant have?", "language": "en", "expected_intent": "disease_detection", "expected_crop": "Tomato", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_03", "query": "कपास के पत्ते पीले पड़ रहे हैं और धब्बे हैं, क्या बीमारी है?", "language": "hi", "expected_intent": "disease_detection", "expected_crop": "Cotton", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_04", "query": "धान में पत्ते सूख रहे हैं, कौन सा रोग है?", "language": "hi", "expected_intent": "disease_detection", "expected_crop": "Paddy", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_05", "query": "રીંગણના પાંદડા પર ડાઘ પડ્યા છે, કયો રોગ છે?", "language": "gu", "expected_intent": "disease_detection", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_06", "query": "सरसों में सफेद फफूंद लग गई है, कौन सी दवा छिड़कें?", "language": "hi", "expected_intent": "disease_detection", "expected_crop": "Mustard", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_07", "query": "White spots on potato leaves, what is the disease?", "language": "en", "expected_intent": "disease_detection", "expected_crop": "Potato", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_08", "query": "चना में उकठा रोग लग गया है क्या?", "language": "hi", "expected_intent": "disease_detection", "expected_crop": "Gram", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_09", "query": "सोयाबीन में इल्ली का प्रकोप है, कौन सा कीटनाशक स्प्रे करें?", "language": "hi", "expected_intent": "disease_detection", "expected_crop": "Soybean", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},
    {"id": "dis_10", "query": "पौधे की पत्ती खराब हो गई है, फोटो देखकर पहचानो", "language": "hi", "expected_intent": "disease_detection", "expected_capabilities": ["DISEASE_DETECTION", "RAG_KNOWLEDGE"], "expected_required_input": "LEAF_IMAGE"},

    # 6. MANDI PRICE (51-60)
    {"id": "m_01", "query": "Gehu ka mandi bhav kya hai Jaipur mein?", "language": "hi", "expected_intent": "mandi_price", "expected_crop": "Wheat", "expected_market": "Jaipur", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_02", "query": "What is the price of wheat in Udaipur today?", "language": "en", "expected_intent": "mandi_price", "expected_crop": "Wheat", "expected_market": "Udaipur", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_03", "query": "pyaz ka rate kya hai nashik mandi mein?", "language": "hi", "expected_intent": "mandi_price", "expected_crop": "Onion", "expected_market": "Nashik", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_04", "query": "રાજકોટ માર્કેટ યાર્ડમાં કપાસનો શું ભાવ ચાલે છે?", "language": "gu", "expected_intent": "mandi_price", "expected_crop": "Cotton", "expected_market": "Rajkot", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_05", "query": "पुण्यात कांद्याचा आजचा भाव काय आहे?", "language": "mr", "expected_intent": "mandi_price", "expected_crop": "Onion", "expected_market": "Pune", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_06", "query": "ਕਣਕ ਦਾ ਭਾਅ ਲੁਧਿਆਣਾ ਮੰਡੀ ਵਿੱਚ ਕੀ ਹੈ?", "language": "pa", "expected_intent": "mandi_price", "expected_crop": "Wheat", "expected_market": "Ludhiana", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_07", "query": "सोयाबीन का ताजा भाव इंदौर मंडी में कितना है?", "language": "hi", "expected_intent": "mandi_price", "expected_crop": "Soybean", "expected_market": "Indore", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_08", "query": "सरसों का भाव कोटा में कितना चल रहा है?", "language": "hi", "expected_intent": "mandi_price", "expected_crop": "Mustard", "expected_market": "Kota", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_09", "query": "चिकन चना का रेट भोपाल में क्या है?", "language": "hi", "expected_intent": "mandi_price", "expected_crop": "Gram", "expected_market": "Bhopal", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},
    {"id": "m_10", "query": "Current modal price of maize in Sendhwa?", "language": "en", "expected_intent": "mandi_price", "expected_crop": "Maize", "expected_market": "Sendhwa", "expected_capabilities": ["CURRENT_PRICE"], "expected_required_input": "NONE"},

    # 7. MANDI FORECAST (61-65)
    {"id": "mf_01", "query": "गेहूं का भाव अगले 7 दिन में क्या रहेगा?", "language": "hi", "expected_intent": "mandi_forecast", "expected_crop": "Wheat", "expected_capabilities": ["MANDI_FORECAST"], "expected_required_input": "NONE"},
    {"id": "mf_02", "query": "What is the 7-day price forecast for onion in Nashik?", "language": "en", "expected_intent": "mandi_forecast", "expected_crop": "Onion", "expected_market": "Nashik", "expected_capabilities": ["MANDI_FORECAST"], "expected_required_input": "NONE"},
    {"id": "mf_03", "query": "कपास का रेट अगले हफ्ते बढ़ेगा या घटेगा?", "language": "hi", "expected_intent": "mandi_forecast", "expected_crop": "Cotton", "expected_capabilities": ["MANDI_FORECAST"], "expected_required_input": "NONE"},
    {"id": "mf_04", "query": "सोयाबीन का 14 दिन का भाव अनुमान बताओ", "language": "hi", "expected_intent": "mandi_forecast", "expected_crop": "Soybean", "expected_capabilities": ["MANDI_FORECAST"], "expected_required_input": "NONE"},
    {"id": "mf_05", "query": "Will mustard prices rise over the next week in Kota?", "language": "en", "expected_intent": "mandi_forecast", "expected_crop": "Mustard", "expected_market": "Kota", "expected_capabilities": ["MANDI_FORECAST"], "expected_required_input": "NONE"},

    # 8. MANDI COMPARISON (66-70)
    {"id": "mc_01", "query": "गेहूं का भाव जयपुर और उदयपुर में compare करो", "language": "hi", "expected_intent": "mandi_comparison", "expected_crop": "Wheat", "expected_capabilities": ["CURRENT_PRICE", "MANDI_COMPARISON"], "expected_required_input": "NONE"},
    {"id": "mc_02", "query": "Compare onion prices between Nashik and Pune", "language": "en", "expected_intent": "mandi_comparison", "expected_crop": "Onion", "expected_capabilities": ["CURRENT_PRICE", "MANDI_COMPARISON"], "expected_required_input": "NONE"},
    {"id": "mc_03", "query": "कपास कोटा में महंगा है या जयपुर में?", "language": "hi", "expected_intent": "mandi_comparison", "expected_crop": "Cotton", "expected_capabilities": ["CURRENT_PRICE", "MANDI_COMPARISON"], "expected_required_input": "NONE"},
    {"id": "mc_04", "query": "सोयाबीन इंदौर बनाम भोपाल तुलना करो", "language": "hi", "expected_intent": "mandi_comparison", "expected_crop": "Soybean", "expected_capabilities": ["CURRENT_PRICE", "MANDI_COMPARISON"], "expected_required_input": "NONE"},
    {"id": "mc_05", "query": "Which market has better mustard rates, Alwar or Kota?", "language": "en", "expected_intent": "mandi_comparison", "expected_crop": "Mustard", "expected_capabilities": ["CURRENT_PRICE", "MANDI_COMPARISON"], "expected_required_input": "NONE"},

    # 9. COMPOUND MANDI DECISION & ADVISORY (71-75)
    {"id": "md_01", "query": "Gehu Jaipur mein bechu ya Kalapipal aur agle 7 din ka bhav kya rahega?", "language": "hi", "expected_intent": "mandi_decision", "expected_crop": "Wheat", "expected_capabilities": ["CURRENT_PRICE", "MANDI_COMPARISON", "MANDI_FORECAST", "MANDI_DECISION"], "expected_required_input": "NONE"},
    {"id": "md_02", "query": "Should I sell my wheat today in Jaipur or wait for next week?", "language": "en", "expected_intent": "mandi_decision", "expected_crop": "Wheat", "expected_market": "Jaipur", "expected_capabilities": ["CURRENT_PRICE", "MANDI_FORECAST", "MANDI_DECISION"], "expected_required_input": "NONE"},
    {"id": "md_03", "query": "आज बेचूं या रुकूं, प्याज का भाव आगे बढ़ेगा क्या?", "language": "hi", "expected_intent": "mandi_decision", "expected_crop": "Onion", "expected_capabilities": ["CURRENT_PRICE", "MANDI_FORECAST", "MANDI_DECISION"], "expected_required_input": "NONE"},
    {"id": "md_04", "query": "कपास सेंधवा में बेचना ठीक रहेगा या 10 दिन रुक जाऊं?", "language": "hi", "expected_intent": "mandi_decision", "expected_crop": "Cotton", "expected_market": "Sendhwa", "expected_capabilities": ["CURRENT_PRICE", "MANDI_FORECAST", "MANDI_DECISION"], "expected_required_input": "NONE"},
    {"id": "md_05", "query": "Should I hold my soybean harvest or sell right now in Indore?", "language": "en", "expected_intent": "mandi_decision", "expected_crop": "Soybean", "expected_market": "Indore", "expected_capabilities": ["CURRENT_PRICE", "MANDI_FORECAST", "MANDI_DECISION"], "expected_required_input": "NONE"},

    # 10. GOVERNMENT SCHEMES (76-80)
    {"id": "s_01", "query": "पीएम किसान सम्मान निधि की अगली किस्त कब आएगी?", "language": "hi", "expected_intent": "government_scheme", "expected_capabilities": ["GOVERNMENT_SCHEME"], "expected_required_input": "NONE"},
    {"id": "s_02", "query": "How to apply for PM Fasal Bima Yojana?", "language": "en", "expected_intent": "government_scheme", "expected_capabilities": ["GOVERNMENT_SCHEME"], "expected_required_input": "NONE"},
    {"id": "s_03", "query": "ट्रैक्टर सब्सिडी के लिए कौन-कौन से दस्तावेज चाहिए?", "language": "hi", "expected_intent": "government_scheme", "expected_capabilities": ["GOVERNMENT_SCHEME"], "expected_required_input": "NONE"},
    {"id": "s_04", "query": "किसान क्रेडिट कार्ड कैसे बनवाएं?", "language": "hi", "expected_intent": "government_scheme", "expected_capabilities": ["GOVERNMENT_SCHEME"], "expected_required_input": "NONE"},
    {"id": "s_05", "query": "What are the eligibility conditions for drip irrigation subsidy?", "language": "en", "expected_intent": "government_scheme", "expected_capabilities": ["GOVERNMENT_SCHEME"], "expected_required_input": "NONE"},

    # 11. ANIMAL ALERT & FARM SECURITY (81-85)
    {"id": "a_01", "query": "खेत में नीलगाय घुस आई है क्या?", "language": "hi", "expected_intent": "animal_alert", "expected_capabilities": ["ANIMAL_ALERT"], "expected_required_input": "NONE"},
    {"id": "a_02", "query": "Is my farm perimeter safe right now?", "language": "en", "expected_intent": "animal_alert", "expected_capabilities": ["ANIMAL_ALERT"], "expected_required_input": "NONE"},
    {"id": "a_03", "query": "सेंसर में कोई जंगली जानवर डिटेक्ट हुआ क्या?", "language": "hi", "expected_intent": "animal_alert", "expected_capabilities": ["ANIMAL_ALERT"], "expected_required_input": "NONE"},
    {"id": "a_04", "query": "Wild pig intrusion detected in the field?", "language": "en", "expected_intent": "animal_alert", "expected_capabilities": ["ANIMAL_ALERT"], "expected_required_input": "NONE"},
    {"id": "a_05", "query": "खेत सुरक्षा अलार्म स्टेटस चेक करो", "language": "hi", "expected_intent": "animal_alert", "expected_capabilities": ["ANIMAL_ALERT"], "expected_required_input": "NONE"},

    # 12. IN-APP NAVIGATION (86-90)
    {"id": "n_01", "query": "मंडी भाव वाली स्क्रीन खोलो", "language": "hi", "expected_intent": "navigation_request", "expected_capabilities": ["NAVIGATION"], "expected_required_input": "NONE"},
    {"id": "n_02", "query": "Navigate to weather screen", "language": "en", "expected_intent": "navigation_request", "expected_capabilities": ["NAVIGATION"], "expected_required_input": "NONE"},
    {"id": "n_03", "query": "रोग पहचान का कैमरा खोलो", "language": "hi", "expected_intent": "navigation_request", "expected_capabilities": ["NAVIGATION"], "expected_required_input": "NONE"},
    {"id": "n_04", "query": "Open crop recommendation page", "language": "en", "expected_intent": "navigation_request", "expected_capabilities": ["NAVIGATION"], "expected_required_input": "NONE"},
    {"id": "n_05", "query": "होम स्क्रीन पर वापस चलो", "language": "hi", "expected_intent": "navigation_request", "expected_capabilities": ["NAVIGATION"], "expected_required_input": "NONE"},

    # 13. REPEAT LAST & VOICE CONTROL (91-93)
    {"id": "r_01", "query": "फिर से बताओ", "language": "hi", "expected_intent": "repeat_last", "expected_capabilities": [], "expected_required_input": "NONE"},
    {"id": "r_02", "query": "Please repeat the last answer", "language": "en", "expected_intent": "repeat_last", "expected_capabilities": [], "expected_required_input": "NONE"},
    {"id": "r_03", "query": "वो वाली बात दोबारा बोलो", "language": "hi", "expected_intent": "repeat_last", "expected_capabilities": [], "expected_required_input": "NONE"},

    # 14. GENERAL AGRICULTURAL KNOWLEDGE (94-96)
    {"id": "g_01", "query": "धान की रोपाई करते समय किन बातों का ध्यान रखें?", "language": "hi", "expected_intent": "agricultural_knowledge", "expected_crop": "Paddy", "expected_capabilities": ["RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "g_02", "query": "How to increase mustard yield with balanced fertilizers?", "language": "en", "expected_intent": "agricultural_knowledge", "expected_crop": "Mustard", "expected_capabilities": ["RAG_KNOWLEDGE"], "expected_required_input": "NONE"},
    {"id": "g_03", "query": "जीवामृत खाद कैसे तैयार करें?", "language": "hi", "expected_intent": "agricultural_knowledge", "expected_capabilities": ["RAG_KNOWLEDGE"], "expected_required_input": "NONE"},

    # 15. CLARIFICATION & AMBIGUITY (97-100)
    {"id": "cl_01", "query": "हम्म", "language": "hi", "expected_intent": "clarification", "expected_capabilities": [], "expected_required_input": "NONE"},
    {"id": "cl_02", "query": "...", "language": "hi", "expected_intent": "clarification", "expected_capabilities": [], "expected_required_input": "NONE"},
    {"id": "cl_03", "query": "ok", "language": "en", "expected_intent": "clarification", "expected_capabilities": [], "expected_required_input": "NONE"},
    {"id": "cl_04", "query": "बताओ", "language": "hi", "expected_intent": "clarification", "expected_capabilities": [], "expected_required_input": "NONE"},
]

out_dir = Path("/home/rdj/FarmFusionFinal/backend/tests/data")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "semantic_extraction_golden_100.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(queries, f, ensure_ascii=False, indent=2)

print(f"Generated {len(queries)} golden evaluation queries in {out_file}")
