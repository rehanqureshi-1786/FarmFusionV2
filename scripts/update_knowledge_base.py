"""
Update disease_knowledge_base.json to ensure full 38-class coverage with verified ICAR/extension agronomic profiles.
"""
import json
from pathlib import Path

KB_PATH = Path(__file__).resolve().parents[1] / "backend" / "app" / "data" / "disease_knowledge_base.json"

with open(KB_PATH, "r", encoding="utf-8") as f:
    kb = json.load(f)

additional_entries = {
    "Blueberry___healthy": {
        "crop": "Blueberry",
        "disease": "Healthy Plant",
        "scientific_name": "Vaccinium corymbosum",
        "symptoms": ["Vigorous green foliage with no visible chlorosis, spotting, or dieback."],
        "causes": ["Normal physiological condition."],
        "favorable_conditions": ["Acidic soil (pH 4.5-5.5) with well-drained organic matter."],
        "prevention": ["Maintain acidic soil conditions with sulfur and balanced ericaceous fertilizers."],
        "cultural_control": ["Mulch with pine bark or acidic compost; drip irrigation."],
        "biological_control": ["Preserve mycorrhizal root associations."],
        "chemical_control": ["No chemical treatment required."],
        "active_ingredients": [],
        "product_categories": ["Organic Mulch", "Acidifying Fertilizer"],
        "treatment_notes": ["Plant is healthy. Regular monitoring recommended."],
        "severity_guidance": ["Zero risk."],
        "sources": ["ICAR Horticulture Advisory"]
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Powdery Mildew",
        "scientific_name": "Podosphaera clandestina",
        "symptoms": [
            "White powdery fungal patches on young leaves and fruit stems",
            "Leaf curling, distortion, and premature defoliation",
            "Web-like fungal growth on ripening cherry fruit"
        ],
        "causes": ["Ascomycete fungus overwintering in bud scales and bark crevices"],
        "favorable_conditions": ["Warm (15-28°C), dry weather with high relative humidity and dense tree canopies"],
        "prevention": [
            "Prune inner canopy branches to promote airflow and sunlight exposure",
            "Avoid excessive nitrogen fertilization which produces susceptible tender shoot growth"
        ],
        "cultural_control": ["Prune and destroy infected terminal shoots early in spring"],
        "biological_control": ["Foliar spray of Ampelomyces quisqualis or Potassium Bicarbonate @ 3 g/L"],
        "chemical_control": [
            "Wettable Sulfur 80% WP @ 2.5 g/L applied at shuck split and repeated at 14-day intervals",
            "Myclobutanil 10% WP @ 1.0 g/L or Hexaconazole 5% SC @ 1.0 ml/L for curative intervention"
        ],
        "active_ingredients": ["Wettable Sulfur", "Hexaconazole", "Myclobutanil", "Difenoconazole"],
        "product_categories": ["Fungicide", "Bio-fungicide", "PPE Kit", "Pruning Shears"],
        "treatment_notes": ["Do not apply sulfur when temperatures exceed 30°C to prevent phytotoxicity. Follow CIBRC guidelines."],
        "severity_guidance": ["Moderate to high risk in young orchards and fruit development stages."],
        "sources": ["ICAR-CITH Srinagar Advisory", "CIBRC Pesticide Compendium"]
    },
    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry",
        "disease": "Healthy Plant",
        "scientific_name": "Prunus cerasus",
        "symptoms": ["Uniform green leaves without powdery coating, necrosis, or shot-hole lesions."],
        "causes": ["Normal physiological condition."],
        "favorable_conditions": ["Adequate winter chill hours and well-drained loam soil."],
        "prevention": ["Regular sanitation and balanced fertilization."],
        "cultural_control": ["Maintain annual dormant pruning and orchard floor clean."],
        "biological_control": ["Preserve beneficial predatory mites and ladybugs."],
        "chemical_control": ["No chemical treatment required."],
        "active_ingredients": [],
        "product_categories": ["Organic Fertilizer", "Orchard Tools"],
        "treatment_notes": ["Plant is healthy. No intervention required."],
        "severity_guidance": ["Zero risk."],
        "sources": ["ICAR Temperate Horticulture Guidelines"]
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange",
        "disease": "Citrus Greening (Huanglongbing / HLB)",
        "scientific_name": "Candidatus Liberibacter asiaticus",
        "symptoms": [
            "Blotchy mottle chlorosis on leaves with asymmetrical yellowing across midrib",
            "Stunted, yellow upright shoots ('yellow shoots')",
            "Small, lopsided fruit with bitter taste and aborted seeds",
            "Severe twig dieback and gradual tree decline"
        ],
        "causes": ["Phloem-limited fastidious bacterium transmitted by the Asian citrus psyllid (Diaphorina citri)"],
        "favorable_conditions": ["Warm subtropical climates (20-32°C) facilitating rapid vector proliferation"],
        "prevention": [
            "Plant only certified disease-free budwood from registered nurseries",
            "Establish windbreaks to deter psyllid flights into citrus blocks",
            "Regular scout monitoring of psyllid nymphs on new flush growth"
        ],
        "cultural_control": [
            "Eradicate severely infected trees showing full canopy decline to prevent vector acquisition",
            "Enhanced nutritional programs (foliar zinc, manganese, iron, potassium) to maintain tree vigor"
        ],
        "biological_control": [
            "Release parasitoid wasps (Tamarixia radiata) for biological suppression of citrus psyllid",
            "Apply Neem seed kernel extract (NSKE 5%) or Entomopathogenic fungi (Beauveria bassiana)"
        ],
        "chemical_control": [
            "Vector control: Imidacloprid 17.8% SL @ 0.5 ml/L or Thiamethoxam 25% WG @ 0.3 g/L during new leaf flushes",
            "Systemic vector rotation: Dimethoate 30% EC @ 1.5 ml/L or Chlorpyrifos 20% EC @ 2.0 ml/L"
        ],
        "active_ingredients": ["Imidacloprid", "Thiamethoxam", "Dimethoate", "Neem Oil"],
        "product_categories": ["Insecticide", "Neem Bio-pesticide", "Micronutrient Spray", "PPE Kit"],
        "treatment_notes": ["Bacterial pathogen cannot be cured once systemic; rigorous vector control is mandatory. Follow ICAR-CCRI Nagpur guidelines."],
        "severity_guidance": ["Critical severe risk. Threatens complete orchard longevity if vector is uncontrolled."],
        "sources": ["ICAR-CCRI Nagpur (Central Citrus Research Institute)", "CIBRC Approved Vector Insecticides"]
    },
    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "disease": "Bacterial Spot",
        "scientific_name": "Xanthomonas arboricola pv. pruni",
        "symptoms": [
            "Water-soaked polygonal angular spots on leaves turning purple-brown and dropping out ('shot hole')",
            "Deep, pitted, gummy necrotic cracks on peach fruit surface",
            "Spring and summer cankers on twigs and young branches"
        ],
        "causes": ["Bacterial pathogen entering through stomata, leaf scars, and fruit lenticels"],
        "favorable_conditions": ["Warm (20-30°C), windy, wet spring weather with blowing rain and sandy soils"],
        "prevention": [
            "Plant tolerant varieties (e.g. Redhaven, Harvester)",
            "Plant windbreaks to minimize blowing sand injury on tender leaves and fruit"
        ],
        "cultural_control": ["Avoid excessive nitrogen that induces tender late-season succulent growth"],
        "biological_control": ["Bacillus amyloliquefaciens or Copper bio-complexes during early season"],
        "chemical_control": [
            "Copper Oxychloride 50% WP @ 2.5 g/L or Bordeaux mixture (1%) at late dormant / bud swell stage",
            "Oxytetracycline / Streptocycline @ 0.5 g/L combined with Copper sprays at petal fall"
        ],
        "active_ingredients": ["Copper Oxychloride", "Bordeaux Mixture", "Streptocycline"],
        "product_categories": ["Bactericide", "Copper Fungicide", "PPE Kit"],
        "treatment_notes": ["Do not apply high rate copper post-bloom to avoid phytotoxicity on peach leaves. Follow KVK advisory."],
        "severity_guidance": ["High risk during spring wet spells."],
        "sources": ["ICAR-CITH Srinagar", "State Horticulture Department Advisory"]
    },
    "Peach___healthy": {
        "crop": "Peach",
        "disease": "Healthy Plant",
        "scientific_name": "Prunus persica",
        "symptoms": ["Lush green lanceolate leaves free from lesions, shot-hole perforations, and gumming."],
        "causes": ["Normal physiological condition."],
        "favorable_conditions": ["Well-drained sandy loam soil with full sunlight exposure."],
        "prevention": ["Regular annual dormant spraying and balanced potassium fertilization."],
        "cultural_control": ["Annual fruit thinning and canopy pruning."],
        "biological_control": ["Preserve predatory wasps and hoverflies."],
        "chemical_control": ["No chemical treatment required."],
        "active_ingredients": [],
        "product_categories": ["Organic Compost", "Pruning Tools"],
        "treatment_notes": ["Plant is healthy. Regular monitoring recommended."],
        "severity_guidance": ["Zero risk."],
        "sources": ["ICAR Horticulture Advisory"]
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Pepper (Bell / Capsicum)",
        "disease": "Bacterial Spot",
        "scientific_name": "Xanthomonas campestris pv. vesicatoria",
        "symptoms": [
            "Small water-soaked circular to irregular dark green spots on leaf undersides",
            "Lesions turn brown with greasy appearance and yellow halo, causing extensive leaf drop",
            "Raised, warty, brown blister-like rough spots on bell pepper fruit"
        ],
        "causes": ["Seed-borne and debris-borne bacterial pathogen splashing onto foliage"],
        "favorable_conditions": ["Warm (24-30°C) temperatures with frequent rains and high relative humidity (>85%)"],
        "prevention": [
            "Use certified disease-free treated hybrid seeds (hot water treatment at 50°C for 25 mins)",
            "Adopt 2 to 3-year crop rotation with non-solanaceous crops (e.g. Corn, Pulses)"
        ],
        "cultural_control": [
            "Use drip irrigation under plastic mulch; avoid overhead sprinkler watering",
            "Disinfect pruning knives and farm equipment with 1% sodium hypochlorite solution"
        ],
        "biological_control": [
            "Seed and seedling dip with Pseudomonas fluorescens @ 10 g/L or Bacillus subtilis @ 5 g/L",
            "Foliar spray of organic copper bio-formulations or neem formulation (1500 ppm @ 3 ml/L)"
        ],
        "chemical_control": [
            "Foliar spray of Copper Hydroxide 53.8% DF @ 2.0 g/L or Copper Oxychloride 50% WP @ 2.5 g/L",
            "Combined tank-mix of Copper Oxychloride (2.0 g/L) + Streptocycline @ 0.1 g/L at early disease onset"
        ],
        "active_ingredients": ["Copper Oxychloride", "Copper Hydroxide", "Streptocycline", "Kasugamycin"],
        "product_categories": ["Bactericide", "Copper Fungicide", "PPE Kit", "Drip Irrigation Parts"],
        "treatment_notes": ["Spray during cool morning or evening hours. Comply with 7-day PHI. Follow CIBRC guidelines."],
        "severity_guidance": ["High risk in monsoon/rainy season. Rapid defoliation leads to severe fruit sunscald."],
        "sources": ["ICAR-IIHR Bengaluru", "TNAU Agritech Portal", "CIBRC Approved Pesticides List"]
    },
    "Pepper,_bell___healthy": {
        "crop": "Pepper (Bell / Capsicum)",
        "disease": "Healthy Plant",
        "scientific_name": "Capsicum annuum",
        "symptoms": ["Deep green glossy leaves with robust flowering and fruit set without spots or distortion."],
        "causes": ["Normal physiological condition."],
        "favorable_conditions": ["Moderate temperature (20-28°C) with fertile well-drained loam."],
        "prevention": ["Maintain balanced NPK fertilization and uniform soil moisture."],
        "cultural_control": ["Mulching and stake support for heavy fruiting."],
        "biological_control": ["Encourage beneficial biocontrol agents like Trichogramma."],
        "chemical_control": ["No chemical treatment required."],
        "active_ingredients": [],
        "product_categories": ["Bio-fertilizer", "Mulch Film", "Plant Stakes"],
        "treatment_notes": ["Plant is healthy. Regular monitoring recommended."],
        "severity_guidance": ["Zero risk."],
        "sources": ["ICAR-IIHR Bengaluru"]
    },
    "Raspberry___healthy": {
        "crop": "Raspberry",
        "disease": "Healthy Plant",
        "scientific_name": "Rubus idaeus",
        "symptoms": ["Vigorous canes with uniform green trifoliate leaves and healthy cane growth."],
        "causes": ["Normal physiological condition."],
        "favorable_conditions": ["Cool temperate climate with rich organic soil."],
        "prevention": ["Annual pruning of spent floricanes and trellis support."],
        "cultural_control": ["Maintain 10-15 cm organic mulch."],
        "biological_control": ["Preserve pollinators and beneficial predatory insects."],
        "chemical_control": ["No chemical treatment required."],
        "active_ingredients": [],
        "product_categories": ["Organic Compost", "Trellis Wire"],
        "treatment_notes": ["Plant is healthy. No intervention required."],
        "severity_guidance": ["Zero risk."],
        "sources": ["ICAR Horticulture Advisory"]
    },
    "Soybean___healthy": {
        "crop": "Soybean",
        "disease": "Healthy Plant",
        "scientific_name": "Glycine max",
        "symptoms": ["Vibrant green trifoliate leaves, strong nodulation, and healthy pod development."],
        "causes": ["Normal physiological condition."],
        "favorable_conditions": ["Warm soil (20-30°C) with adequate monsoon moisture."],
        "prevention": ["Inoculate seeds with Bradyrhizobium japonicum before sowing."],
        "cultural_control": ["Maintain broad bed furrow (BBF) planting for drainage."],
        "biological_control": ["Conserve natural field predators."],
        "chemical_control": ["No chemical treatment required."],
        "active_ingredients": [],
        "product_categories": ["Rhizobium Bio-fertilizer", "Farm Equipment"],
        "treatment_notes": ["Crop is healthy. Regular scouting recommended."],
        "severity_guidance": ["Zero risk."],
        "sources": ["ICAR-IISR Indore (Indian Institute of Soybean Research)"]
    },
    "Squash___Powdery_mildew": {
        "crop": "Squash",
        "disease": "Powdery Mildew",
        "scientific_name": "Podosphaera xanthii",
        "symptoms": [
            "White talcum-like powdery fungal growth on both upper and lower leaf surfaces",
            "Infected leaves turn chlorotic, become brittle, brown, and die prematurely",
            "Reduced fruit yield and fruit sunscald due to loss of protective leaf canopy"
        ],
        "causes": ["Obligate biotrophic fungus dispersing airborne conidia across cucurbit fields"],
        "favorable_conditions": ["Warm dry weather (20-30°C) with shaded conditions and high relative humidity"],
        "prevention": [
            "Plant powdery mildew-resistant squash hybrids",
            "Provide ample vine spacing (1.5 - 2.0 m) for sunlight penetration and air movement"
        ],
        "cultural_control": ["Remove and bury senescing lower canopy leaves showing initial white spots"],
        "biological_control": [
            "Foliar spray of Ampelomyces quisqualis @ 5 g/L or Trichoderma viride @ 5 g/L",
            "Baking soda (Potassium/Sodium bicarbonate @ 3 g/L) + horticultural oil (5 ml/L)"
        ],
        "chemical_control": [
            "Wettable Sulfur 80% WDG @ 2.0 g/L (avoid in hot weather above 32°C)",
            "Systemic spray: Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1.0 ml/L or Hexaconazole 5% SC @ 1.0 ml/L"
        ],
        "active_ingredients": ["Wettable Sulfur", "Azoxystrobin", "Difenoconazole", "Hexaconazole"],
        "product_categories": ["Fungicide", "Bio-fungicide", "Neem Oil", "PPE Kit"],
        "treatment_notes": ["Alternate systemic fungicides with contact sulfur to prevent resistance. Follow CIBRC guidelines."],
        "severity_guidance": ["Moderate to high risk during mid-to-late fruiting period."],
        "sources": ["ICAR-IIVR Varanasi", "TNAU Agritech Portal", "CIBRC Pesticide Compendium"]
    },
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "disease": "Leaf Scorch",
        "scientific_name": "Diplocarpon earlianum",
        "symptoms": [
            "Numerous small, irregular purple to dark red spots on upper leaf surfaces",
            "Spots enlarge and merge, giving entire leaf a dry, scorched, burnt brown appearance",
            "Leaf margins curl upward and die; calyx infection causes brown caps on fruit"
        ],
        "causes": ["Ascomycete fungus surviving in infected crown leaves and plant debris"],
        "favorable_conditions": ["Warm, humid conditions (20-28°C) with prolonged leaf wetness"],
        "prevention": [
            "Use certified disease-free strawberry runners from tissue culture",
            "Plant in well-drained raised beds with plastic mulch"
        ],
        "cultural_control": [
            "Prune and destroy all older diseased foliage at renovation post-harvest",
            "Avoid overhead sprinkler irrigation; employ drip lines beneath mulch"
        ],
        "biological_control": ["Foliar bio-fungicide spray of Bacillus subtilis or Trichoderma harzianum @ 5 g/L"],
        "chemical_control": [
            "Spray Captan 50% WP @ 2.0 g/L or Mancozeb 75% WP @ 2.5 g/L at first appearance of purple spots",
            "Azoxystrobin 23% SC @ 1.0 ml/L or Pyraclostrobin 20% WG @ 1.0 g/L for curative control"
        ],
        "active_ingredients": ["Captan", "Mancozeb", "Azoxystrobin", "Pyraclostrobin"],
        "product_categories": ["Fungicide", "Drip Tape", "Raised Bed Mulch", "PPE Kit"],
        "treatment_notes": ["Observe 3-day pre-harvest interval for strawberry fruit. Follow KVK advisory."],
        "severity_guidance": ["Moderate risk. Defoliation reduces next season crown vigor."],
        "sources": ["ICAR-CITH Srinagar", "State Horticulture Advisory"]
    },
    "Strawberry___healthy": {
        "crop": "Strawberry",
        "disease": "Healthy Plant",
        "scientific_name": "Fragaria × ananassa",
        "symptoms": ["Vibrant dark green trifoliate leaves, robust crowns, and clear white blossoms."],
        "causes": ["Normal physiological condition."],
        "favorable_conditions": ["Raised bed with drip fertigation and silver-black mulch."],
        "prevention": ["Balanced fertigation with potassium and calcium during fruit sizing."],
        "cultural_control": ["Maintain drip irrigation and sanitize bed runners."],
        "biological_control": ["Preserve pollinating bees and beneficial predatory mites."],
        "chemical_control": ["No chemical treatment required."],
        "active_ingredients": [],
        "product_categories": ["Water Soluble Fertilizer", "Runner Clips"],
        "treatment_notes": ["Plant is healthy. Regular monitoring recommended."],
        "severity_guidance": ["Zero risk."],
        "sources": ["ICAR Horticulture Advisory"]
    }
}

for k, v in additional_entries.items():
    kb[k] = v

with open(KB_PATH, "w", encoding="utf-8") as f:
    json.dump(kb, f, indent=2)

print(f"Updated knowledge base. Total entries: {len(kb)}")
