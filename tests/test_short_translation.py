#!/usr/bin/env python3
"""
Test script for shorter translation prompt
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src/holyremix')

from translators.chapter_translator import ChapterTranslator

def main():
    # Load Bible data
    with open('data/processed/kjv_bible.json', 'r') as f:
        data = json.load(f)
    
    # Take only first 5 verses
    verses = {k: v for k, v in data['Genesis']['1'].items() if int(k) <= 5}
    
    print(f"Testing with {len(verses)} verses...")
    
    # Create translator and try translation
    translator = ChapterTranslator()
    
    # Check token estimation
    input_tokens, output_tokens = translator.estimate_chapter_tokens('Genesis', '1', verses, 'joe_rogan')
    print(f"Estimated tokens: {input_tokens} input, {output_tokens} output")
    
    # Try translation
    result = translator.translate_chapter('Genesis', '1', verses, 'joe_rogan')
    
    if result:
        print("✅ Translation successful!")
        for verse_num, text in sorted(result.items(), key=lambda x: int(x[0])):
            print(f"Verse {verse_num}: {text}")
    else:
        print("❌ Translation failed")

if __name__ == "__main__":
    main() 