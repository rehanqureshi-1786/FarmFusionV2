# FarmFusion Disease Model V1 — Dataset Provenance & Architectural Audit

This document records the provenance, licensing, image characteristics, and treatment mapping for the vision datasets used in FarmFusion Crop Disease Model V1.

---

## 1. Candidate Dataset Audit Matrix

| Metric / Dimension | Dataset A: PlantVillage | Dataset B: PlantDoc | Dataset C: Kamal-Shirupa Cotton Repo |
| :--- | :--- | :--- | :--- |
| **Source & Authors** | Hughes & Salathé (2015), Penn State University | Singh et al. (2020), ACM India Joint Int. Conf. | Kamal-Shirupa (2025), GitHub Open Source |
| **Official URL** | [github.com/spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset) | [github.com/pratikkayal/PlantDoc-Dataset](https://github.com/pratikkayal/PlantDoc-Dataset) | [github.com/Kamal-Shirupa/...](https://github.com/Kamal-Shirupa/Cotton-Disease-Detection-and-Pesticide-Suggestion-System) |
| **License** | **CC0 1.0 (Public Domain)** | **Creative Commons CC BY 4.0** | **MIT License** |
| **Number of Images** | 54,303 leaf images | 2,598 field images | ~1,500 cotton images + CSVs |
| **Number of Crops** | 14 crop species | 13 crop species | 1 crop species (Cotton) |
| **Disease Classes** | 26 disease classes | 17 disease classes | 3 disease classes (Bacterial Blight, Curl Virus, Fusarium) |
| **Healthy Classes** | 12 healthy classes | 10 healthy classes | 1 healthy cotton class |
| **Image Resolution** | Uniform 256×256 pixels | Variable high resolution (1024×768 to 4K) | Variable (224×224 to 800×600) |
| **Field vs Lab Conditions** | Controlled laboratory background (grey/black paper) | **Real-world in-field farmer photographs** (natural backgrounds, weeds, varying lighting) | Mixed field & segmented images |
| **Indian Crop Relevance** | Moderate (Tomato, Potato, Corn, Pepper, Grape, Apple) | High (Indian researcher curated field images) | High (Cotton is a premier Indian commercial Kharif cash crop) |
| **Pesticide / Treatment Data** | None (pure image dataset) | None (pure image dataset) | **CSV-based pesticide recommendation dataset** |
| **Training Suitability** | **PRIMARY Vision Backbone** | **SUPPLEMENTARY Field Robustness** | **KNOWLEDGE BASE SOURCE for Cotton** |

---

## 2. Technical Audit of `Kamal-Shirupa/Cotton-Disease-Detection-and-Pesticide-Suggestion-System`

### A. Repository Architecture
* **License**: MIT License (allows free academic and commercial reuse with attribution).
* **Vision Model**: Uses baseline CNN (VGG / ResNet) trained specifically on 4 cotton classes.
* **Pesticide Data Directory (`pesticide_data/`)**: Uses a tabular CSV schema mapping detected cotton diseases to active chemical molecules and trade recommendations.

### B. Pesticide Dataset Schema Extraction & Evaluation
The repository organizes pesticide suggestions with the following column structure:
* `disease_name`: Disease identification key (e.g. *Bacterial Blight*, *Leaf Curl Virus*, *Fusarium Wilt*).
* `active_ingredient`: Chemical molecule (e.g. *Copper Oxychloride*, *Streptocycline*, *Diafenthiuron*, *Carbendazim*).
* `dosage`: Recommended application rate per liter of water.
* `application_method`: Foliar spray vs seed treatment vs soil drench.
* `precautions`: Basic PPE guidance.

### C. Scientific Validation & ICAR-CICR Alignment
1. **Bacterial Blight**: Sourced active ingredients (*Copper Oxychloride 50% WP* + *Streptocycline*) match ICAR-CICR Nagpur recommendations exactly.
2. **Cotton Leaf Curl Virus**: The repository correctly notes that chemical sprays target the insect vector (*Bemisia tabaci* / whitefly) rather than the virus itself (*Diafenthiuron*, *Flonicamid*, *Pyriproxyfen*).
3. **Safety Disclaimers**: While the active molecules are accurate, exact dosages in the wild vary based on formulation percentage. In FarmFusion, all dosages are tied directly to Central Insecticides Board & Registration Committee (CIBRC) approved labels, with mandatory fallbacks: *"Follow product label & consult local KVK for verified field dosage"*.

---

## 3. Final Multi-Crop Vision & Knowledge Strategy

```
           VISION CLASSIFICATION LAYER                  AGRICULTURAL KNOWLEDGE LAYER
       ┌───────────────────────────────────┐        ┌──────────────────────────────────┐
       │   PlantVillage (54,303 images)    │        │  ICAR / SAU / CIBRC Publications │
       │                +                  │        │                +                 │
       │     PlantDoc (2,598 images)       │   ──►  │ Kamal-Shirupa Cotton Pesticides  │
       │                +                  │        │                +                 │
       │      Cotton Leaf Dataset          │        │ Amazon India Affiliate Catalog   │
       └─────────────────┬─────────────────┘        └────────────────┬─────────────────┘
                         │                                           │
                         ▼                                           ▼
             EfficientNet-B3 Model                     Structured JSON Knowledge Base
             (Confidence Tiers)                       (Biological, Cultural, Chemical)
```

1. **Vision Backbone**:
   * Model: `EfficientNet-B3` (300×300 input resolution, ImageNet transfer learning).
   * Classes: 36 canonical classes covering Tomato, Potato, Rice, Wheat, Cotton, Corn, Grape, and Apple.
2. **Treatment Separation (Rule #5)**:
   * Vision model outputs ONLY `{crop, disease, confidence}`.
   * Treatment recommendations are retrieved strictly from `backend/app/data/disease_knowledge_base.json`.
3. **Product Monetization (Rule #8)**:
   * Active ingredients and product categories map to verified Amazon India search links via `StoreRecommendationService`.
