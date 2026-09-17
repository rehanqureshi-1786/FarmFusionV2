"""
Generate and validate the unified FarmFusion F7 Voice Orchestrator Generalization Test Dataset.
Aggregates all 20 categories (A through T) across 12 languages.
Outputs to: backend/tests/data/f7_voice_generalization_dataset.json
"""

import json
import os
import sys
from collections import Counter

# Add parent directory to sys.path so we can import from dataset_categories
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dataset_categories.cat_weather_irrigation import get_weather_irrigation_conversations
from dataset_categories.cat_crops_disease_market import get_crops_disease_market_conversations
from dataset_categories.cat_disaster_security_calling import get_disaster_security_calling_conversations
from dataset_categories.cat_knowledge_schemes_multiintent import get_knowledge_schemes_multiintent_conversations
from dataset_categories.cat_context_temporal_location import get_context_temporal_location_conversations
from dataset_categories.cat_missing_ambiguous_outofscope import get_missing_ambiguous_outofscope_conversations
from dataset_categories.cat_adversarial_asr_followup import get_adversarial_asr_followup_conversations

def generate_unified_dataset():
    all_convs = []
    
    # 1. Weather & Irrigation (A, B)
    all_convs.extend(get_weather_irrigation_conversations())
    
    # 2. Crop Rec, Disease, Market (C, D, E)
    all_convs.extend(get_crops_disease_market_conversations())
    
    # 3. Disaster, Animal Security, Calling (F, G, H)
    all_convs.extend(get_disaster_security_calling_conversations())
    
    # 4. Knowledge/RAG, Schemes, Multi-Intent (I, J, K)
    all_convs.extend(get_knowledge_schemes_multiintent_conversations())
    
    # 5. Context, Temporal, Location (L, M, N)
    all_convs.extend(get_context_temporal_location_conversations())
    
    # 6. Missing Input, Ambiguous, Out-of-Scope (O, P, Q)
    all_convs.extend(get_missing_ambiguous_outofscope_conversations())
    
    # 7. Adversarial, Voice ASR, Natural Speech / Follow-up (R, S, T)
    all_convs.extend(get_adversarial_asr_followup_conversations())

    # Validation
    id_counts = Counter(c["id"] for c in all_convs)
    duplicates = [cid for cid, count in id_counts.items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate conversation IDs found: {duplicates}")

    total_convs = len(all_convs)
    total_turns = sum(len(c["turns"]) for c in all_convs)

    category_counts = Counter(c["category"] for c in all_convs)
    language_counts = Counter(c["language"] for c in all_convs)
    domain_counts = Counter(c["domain"] for c in all_convs)

    multi_turn_convs = sum(1 for c in all_convs if len(c["turns"]) > 1)
    single_turn_convs = sum(1 for c in all_convs if len(c["turns"]) == 1)

    dataset_obj = {
        "metadata": {
            "title": "FarmFusion F7 Voice Orchestrator Generalization Test Dataset",
            "version": "1.0.0",
            "total_conversations": total_convs,
            "total_turns": total_turns,
            "single_turn_conversations": single_turn_convs,
            "multi_turn_conversations": multi_turn_convs,
            "categories_supported": 20,
            "languages_supported": len(language_counts),
            "category_distribution": dict(category_counts),
            "language_distribution": dict(language_counts),
            "domain_distribution": dict(domain_counts)
        },
        "conversations": all_convs
    }

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "tests", "data", "f7_voice_generalization_dataset.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset_obj, f, ensure_ascii=False, indent=2)

    print("==================================================")
    print("F7 VOICE DATASET GENERATION COMPLETE")
    print("==================================================")
    print(f"File written to: {output_path}")
    print(f"Total Conversations: {total_convs}")
    print(f"Total Turns:         {total_turns}")
    print(f"Single-Turn:         {single_turn_convs}")
    print(f"Multi-Turn:          {multi_turn_convs}")
    print("\n--- Category Breakdown ---")
    for cat in sorted(category_counts.keys()):
        print(f"  Category {cat}: {category_counts[cat]} conversations")
    print("\n--- Language Breakdown ---")
    for lang in sorted(language_counts.keys()):
        print(f"  {lang}: {language_counts[lang]} conversations")
    print("==================================================")

if __name__ == "__main__":
    generate_unified_dataset()
