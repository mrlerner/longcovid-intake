"""
Quick test script to see what Claude returns for symptom analysis
"""
import os
from dotenv import load_dotenv
from config import Config
from services.symptom_analyzer import analyze_symptoms

load_dotenv()

# Test transcription
transcriptions = {
    1: "I'm very tired, I get dizzy when I stand up, and I have neck and jaw pain"
}

print("=" * 80)
print("TESTING SYMPTOM ANALYZER")
print("=" * 80)
print(f"\nTranscription: {transcriptions[1]}")
print(f"\nNumber of categories provided: {len(Config.SYMPTOM_CATEGORIES)}")
print(f"\nFirst 3 categories:")
for i, cat in enumerate(Config.SYMPTOM_CATEGORIES[:3]):
    print(f"  {i+1}. {cat['name']} (ID: {cat['id']})")

print("\n" + "=" * 80)
print("CALLING CLAUDE API...")
print("=" * 80)

result = analyze_symptoms(
    transcriptions,
    Config.CLAUDE_API_KEY,
    Config.CLAUDE_MODEL,
    Config.SYMPTOM_CATEGORIES
)

print("\n" + "=" * 80)
print("RESULT FROM CLAUDE:")
print("=" * 80)
import json
print(json.dumps(result, indent=2))

print("\n" + "=" * 80)
print("CHECKING MATCHED_CATEGORIES:")
print("=" * 80)
if "matched_categories" in result:
    print(f"✓ Found matched_categories with {len(result['matched_categories'])} items")
    for i, cat in enumerate(result['matched_categories']):
        print(f"\n  Category {i+1}:")
        print(f"    ID: {cat.get('category_id')}")
        print(f"    Name: {cat.get('category_name')}")
        print(f"    Confidence: {cat.get('confidence')}")
        print(f"    Symptoms: {cat.get('patient_symptoms')}")
else:
    print("✗ NO matched_categories in result!")
    print(f"  Keys found: {list(result.keys())}")
