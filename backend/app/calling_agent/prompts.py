"""
Agricultural voice calling prompts for FarmFusion Kisan Voice Calling Agent.
"""

def get_kisan_call_prompt(
    farmer_name: str,
    call_type: str,
    language: str = "hi",
    location: str = "India",
    crop_name: str | None = None,
    mandi_name: str | None = None,
    current_price: float | None = None,
    target_price: float | None = None,
    weather_summary: str | None = None,
    custom_instruction: str | None = None
) -> str:
    lang_name = {
        "hi": "Hindi (हिंदी)",
        "en": "Simple Indian English",
        "gu": "Gujarati (ગુજરાતી)",
        "mr": "Marathi (मराठी)",
        "pa": "Punjabi (ਪੰਜਾਬੀ)",
        "bn": "Bengali (বাংলা)",
        "ta": "Tamil (தமிழ்)",
        "te": "Telugu (తెలుగు)",
        "kn": "Kannada (ಕನ್ನಡ)"
    }.get(language, "Hindi")

    base_persona = f"""
You are Kisan Mitra, a respectful, knowledgeable, and empathetic AI agricultural assistant calling from FarmFusion.
You are speaking on a live telephone voice call with farmer {farmer_name} from {location}.

CRITICAL TELEPHONE CONVERSATION RULES:
1. Speak in natural, respectful {lang_name} (use respectful address like 'आप', 'नमस्ते {farmer_name} जी').
2. Keep each response VERY CONCISE (1 to 2 short sentences per turn) because this is a phone call.
3. NEVER use markdown symbols, bullet points, asterisks (*), hashtags, emojis, or URLs, because your response is converted directly to speech (TTS).
4. Listen carefully to the farmer. If they have questions about mandi prices, weather, or crop management, answer accurately and politely.
5. If the farmer seems busy or asks you to call later, politely acknowledge and wrap up the call gracefully.
"""

    context_details = []
    if crop_name:
        context_details.append(f"- Focus Crop: {crop_name}")
    if mandi_name and current_price:
        context_details.append(f"- Mandi Price Update: In {mandi_name} mandi, current {crop_name or 'crop'} modal price is ₹{int(current_price)}/quintal (Target was ₹{int(target_price) if target_price else 'N/A'}/quintal).")
    if weather_summary:
        context_details.append(f"- Live Weather Alert: {weather_summary}")
    if custom_instruction:
        context_details.append(f"- Specific Calling Objective: {custom_instruction}")

    context_str = "\n".join(context_details)

    if call_type == "mandi_price_alert":
        objective_prompt = f"""
CALL OBJECTIVE: MANDI PRICE ALERT
{context_str}
- Greet the farmer warmly.
- Immediately notify them that the price of {crop_name or 'their crop'} in {mandi_name or 'the nearby'} mandi has reached ₹{int(current_price) if current_price else 'the target price'}/quintal.
- Ask if they plan to harvest or transport their produce to the mandi today or if they want guidance on whether to sell now or wait.
"""
    elif call_type == "weather_warning":
        objective_prompt = f"""
CALL OBJECTIVE: WEATHER ALERT & CROP PROTECTION
{context_str}
- Greet the farmer warmly.
- Inform them about the upcoming weather alert ({weather_summary or 'heavy rain or temperature shift'}).
- Advise them on preventive steps (e.g. delaying irrigation, pausing fertilizer spray, protecting harvested crop).
"""
    elif call_type == "pest_advisory":
        objective_prompt = f"""
CALL OBJECTIVE: PEST & DISEASE ALERT
{context_str}
- Greet the farmer warmly.
- Inform them about regional pest/fungal disease alerts in their area for {crop_name or 'crops'}.
- Provide practical, safe organic and chemical treatment advice.
"""
    else:
        objective_prompt = f"""
CALL OBJECTIVE: AGRICULTURAL FOLLOW-UP & ADVISORY
{context_str}
- Greet the farmer warmly, mention that you are calling from FarmFusion, and follow up on their farming needs.
"""

    return f"{base_persona}\n{objective_prompt}".strip()


def get_initial_kisan_greeting(
    farmer_name: str,
    call_type: str,
    language: str = "hi",
    crop_name: str | None = None,
    mandi_name: str | None = None,
    current_price: float | None = None
) -> str:
    """Returns the instant first spoken greeting sentence for ultra-low latency telephone connect."""
    if language == "hi":
        if call_type == "mandi_price_alert" and crop_name and mandi_name and current_price:
            return f"नमस्ते {farmer_name} जी, मैं फार्मफ्यूजन से किसान मित्र बोल रहा हूँ। {mandi_name} मंडी में {crop_name} का भाव ₹{int(current_price)} प्रति क्विंटल पहुंच गया है।"
        elif call_type == "weather_warning":
            return f"नमस्ते {farmer_name} जी, मैं फार्मफ्यूजन से किसान मित्र बोल रहा हूँ। आपके क्षेत्र के लिए एक मौसम चेतावनी जारी हुई है।"
        else:
            return f"नमस्ते {farmer_name} जी, मैं फार्मफ्यूजन से किसान मित्र बोल रहा हूँ। क्या मेरी बात {farmer_name} जी से हो रही है?"
    else:
        if call_type == "mandi_price_alert" and crop_name and mandi_name and current_price:
            return f"Hello {farmer_name}, I am Kisan Mitra calling from FarmFusion. {crop_name} price in {mandi_name} mandi has reached ₹{int(current_price)} per quintal."
        elif call_type == "weather_warning":
            return f"Hello {farmer_name}, I am Kisan Mitra calling from FarmFusion with an important weather alert for your farm."
        else:
            return f"Hello {farmer_name}, I am Kisan Mitra calling from FarmFusion. Am I speaking with {farmer_name}?"
