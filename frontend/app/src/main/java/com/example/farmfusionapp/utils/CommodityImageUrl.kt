package com.example.farmfusionapp.utils

import java.util.Locale

/**
 * Maps mandi / e-NAM style commodity labels (English, Hindi transliterations, mixed) to a stable hero image.
 */
fun commodityHeroImageUrl(rawCommodity: String): String {
    val c = rawCommodity
        .lowercase(Locale.ROOT)
        .replace(Regex("[^a-z0-9\\s]"), " ")
        .replace(Regex("\\s+"), " ")
        .trim()

    fun has(vararg keys: String): Boolean = keys.any { c.contains(it) }

    return when {
        // GRAINS
        has("wheat", "gehu", "kanak", "atta", "godhumai", "godhuma") ->
            "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=500&q=80"
        has("rice", "paddy", "dhan", "basmati", "chawal", "nellu", "arisi") ->
            "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500&q=80"
        has("maize", "corn", "makka", "makai", "cholam") ->
            "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=500&q=80"
        has("bajra", "pearl millet", "kambu") ->
            "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=500&q=80"
        has("jowar", "sorghum", "cholam") ->
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=500&q=80"
        has("barley", "jau") ->
            "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=500&q=80"
        has("ragi", "finger millet") ->
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=500&q=80"

        // VEGETABLES
        has("onion", "pyaj", "pyaaz", "piaz", "vengayam", "ulligadda") ->
            "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500&q=80"
        has("potato", "aloo", "alu", "urulaikizhangu", "bangaladumpa") ->
            "https://images.unsplash.com/photo-1518977673343-a4a623db80db?w=500&q=80"
        has("tomato", "tamatar", "thakkali") ->
            "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80"
        has("cabbage", "patta gobi", "muttaikose") ->
            "https://images.unsplash.com/photo-1594282486552-05ade4e4fbc7?w=500&q=80"
        has("cauliflower", "gobhi", "phool gobi") ->
            "https://images.unsplash.com/photo-1568584711075-3d021a7c3fb3?w=500&q=80"
        has("carrot", "gajar") ->
            "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=500&q=80"
        has("cucumber", "kheera", "kakdi", "vellari") ->
            "https://images.unsplash.com/photo-1547516508-8b75d56a9466?w=500&q=80"
        has("garlic", "lasun", "lahsun", "poondu", "vellulli") ->
            "https://images.unsplash.com/photo-1547514701-42782101795e?w=500&q=80"
        has("ginger", "adrak", "inchi", "allam") ->
            "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&q=80"
        has("brinjal", "eggplant", "baigan", "baingan", "kathirikai", "vankaya") ->
            "https://images.unsplash.com/photo-1561394142-835697284f93?w=500&q=80"
        has("chilli", "mirch", "chili", "milagai", "mirapa") ->
            "https://images.unsplash.com/photo-1583119508843-6f584976cda0?w=500&q=80"
        has("lemon", "nimbu", "lime", "ezhumichai") ->
            "https://images.unsplash.com/photo-1590502593747-42a996133562?w=500&q=80"
        has("peas", "matar", "pea", "pattani") ->
            "https://images.unsplash.com/photo-1587735243615-c03f25a50782?w=500&q=80"
        has("lady finger", "ladyfinger", "bhindi", "okra", "vendakkai", "bendakaya") ->
            "https://images.unsplash.com/photo-1449339042239-0bd9f14371fa?w=500&q=80"
        has("beetroot", "bitroot") ->
            "https://images.unsplash.com/photo-1590502593747-42a996133562?w=500&q=80"
        has("radish", "mooli", "mullangi") ->
            "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=500&q=80"

        // PULSES
        has("gram", "chana", "chickpea", "kadalai") ->
            "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500&q=80"
        has("moong", "mung", "pasipayiru") ->
            "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500&q=80"
        has("urad", "udad", "ulundhu") ->
            "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500&q=80"
        has("arhar", "tur", "toor", "thuvaram", "red gram") ->
            "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500&q=80"
        has("masur", "masoor", "lentil") ->
            "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500&q=80"
        has("soybean", "soya", "soyabean") ->
            "https://images.unsplash.com/photo-1550989460-0adf9ea622e2?w=500&q=80"

        // FRUITS
        has("apple", "seb") ->
            "https://images.unsplash.com/photo-1560806887-1e4cd0b6bccb?w=500&q=80"
        has("mango", "aam") ->
            "https://images.unsplash.com/photo-1553279768-865429fa0078?w=500&q=80"
        has("banana", "kela") ->
            "https://images.unsplash.com/photo-1571771894821-ce9b6c11b3b7?w=500&q=80"
        has("grapes", "angoor") ->
            "https://images.unsplash.com/photo-1596333522248-112f36218d66?w=500&q=80"
        has("orange", "santra", "mosambi") ->
            "https://images.unsplash.com/photo-1495195134817-aeb325a55b65?w=500&q=80"
        has("pomegranate", "anar") ->
            "https://images.unsplash.com/photo-1615485501306-38250269f845?w=500&q=80"
        has("papaya", "papita") ->
            "https://images.unsplash.com/photo-1526318896980-cf78c088247c?w=500&q=80"
        has("watermelon", "tarbooz") ->
            "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?w=500&q=80"

        // SPICES
        has("cumin", "jeera") ->
            "https://images.unsplash.com/photo-1593121925328-369ec94b5977?w=500&q=80"
        has("turmeric", "haldi") ->
            "https://images.unsplash.com/photo-1615485500704-8e990fdd9044?w=500&q=80"
        has("coriander", "dhania") ->
            "https://images.unsplash.com/photo-1605027628030-9bb6f83535e6?w=500&q=80"
        has("mustard", "sarson", "rai") ->
            "https://images.unsplash.com/photo-1563223023-eb56e696fbe5?w=500&q=80"
        has("garlic", "lasun") ->
            "https://images.unsplash.com/photo-1547514701-42782101795e?w=500&q=80"

        // OTHERS
        has("cotton", "kapas") ->
            "https://images.unsplash.com/photo-1625246333195-f89889981f88?w=500&q=80"
        has("sugarcane", "ganna", "karumbu") ->
            "https://images.unsplash.com/photo-1599839575945-a9e50a0d3211?w=500&q=80"
        has("groundnut", "peanut", "moongphali", "verkadalai") ->
            "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500&q=80"
        has("sesame", "til", "ellu") ->
            "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500&q=80"
        has("guar", "guar seed") ->
            "https://images.unsplash.com/photo-1628186214502-d961e6afccd8?w=500&q=80"
        has("mustard", "sarson", "rai") ->
            "https://images.unsplash.com/photo-1563223023-eb56e696fbe5?w=500&q=80"
        has("castor", "arandi") ->
            "https://images.unsplash.com/photo-1621217030557-23847e909a34?w=500&q=80"
        
        else ->
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=500&q=80"
    }
}
