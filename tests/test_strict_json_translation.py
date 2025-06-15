#!/usr/bin/env python3
"""
Test script for strict JSON translation system
"""

import sys
import json
import os

# Set the profile
os.environ['AWS_PROFILE'] = 'personal'

# Add src to path
sys.path.insert(0, 'src/holyremix')

from translators.chapter_translator import ChapterTranslator

def test_strict_json_translation(persona: str, intensity: str = "nuclear"):
    """Test strict JSON translation with validation."""
    
    # Load Bible data
    with open('tests/fixtures/kjv_bible.json', 'r') as f:
        data = json.load(f)
    
    # Take first 3 verses of Genesis 1 for testing
    verses = {k: v for k, v in data['Genesis']['1'].items() if int(k) <= 3}
    
    print(f"🔥 Testing {intensity.upper()} intensity {persona} with STRICT JSON format...")
    print(f"📖 Using Genesis 1:1-3 ({len(verses)} verses)")
    print("=" * 60)
    
    # Create translator with specified intensity
    translator = ChapterTranslator(intensity=intensity)
    
    # Check token estimation
    input_tokens, output_tokens = translator.estimate_chapter_tokens('Genesis', '1', verses, persona)
    print(f"Token estimation: {input_tokens} input, {output_tokens} output")
    
    # Create and show the prompt
    prompt = translator.create_strict_json_prompt('Genesis', '1', verses, persona)
    print(f"\n📝 Prompt length: {len(prompt)} characters")
    print("\n--- PROMPT PREVIEW ---")
    print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
    print("--- END PROMPT PREVIEW ---\n")
    
    # Try translation
    result = translator.translate_chapter('Genesis', '1', verses, persona)
    
    if result:
        print("✅ Translation successful!")
        print("\n--- TRANSLATION (Strict JSON Format) ---")
        for verse_num, text in sorted(result.items(), key=lambda x: int(x[0])):
            print(f"Verse {verse_num}: {text}")
        print("--- END TRANSLATION ---")
        
        # Test JSON structure
        test_json = {
            "book": "Genesis",
            "chapter": 1,
            "verses": result
        }
        
        print(f"\n📊 JSON Structure Validation:")
        print(f"✅ Book: {test_json['book']}")
        print(f"✅ Chapter: {test_json['chapter']}")
        print(f"✅ Verses: {len(test_json['verses'])} verses")
        print(f"✅ Database Ready: {all(isinstance(k, str) and k.isdigit() for k in test_json['verses'].keys())}")
        
    else:
        print("❌ Translation failed")

def main():
    """Test different personas with strict JSON format."""
    
    # Test Joe Rogan with nuclear intensity
    print("🎭 Testing Joe Rogan NUCLEAR MODE with STRICT JSON")
    test_strict_json_translation("joe_rogan", "nuclear")
    
    print("\n" + "="*80 + "\n")
    
    # Test Samuel L. Jackson with wild intensity
    print("🎭 Testing Samuel L. Jackson WILD MODE with STRICT JSON")
    test_strict_json_translation("samuel_l_jackson", "wild")

if __name__ == "__main__":
    main() 