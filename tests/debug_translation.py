#!/usr/bin/env python3
"""
Debug script to see what's happening in translation
"""

import sys
import json
import os

# Set the profile
os.environ['AWS_PROFILE'] = 'personal'

# Add src to path
sys.path.insert(0, 'src')

from translators.chapter_translator import ChapterTranslator

def main():
    # Load Bible data
    with open('data/processed/kjv_bible.json', 'r') as f:
        data = json.load(f)
    
    verses = data['Genesis']['1']
    print(f"Genesis 1 has {len(verses)} verses")
    
    # Create translator
    translator = ChapterTranslator()
    
    # Check token estimation
    input_tokens, output_tokens = translator.estimate_chapter_tokens('Genesis', '1', verses, 'joe_rogan')
    total_tokens = input_tokens + output_tokens
    safe_limit = translator.max_tokens * 0.8
    
    print(f"Token estimation:")
    print(f"  Input: {input_tokens}")
    print(f"  Output: {output_tokens}")
    print(f"  Total: {total_tokens}")
    print(f"  Safe limit: {safe_limit}")
    print(f"  Fits: {total_tokens <= safe_limit}")
    
    # Check should_translate_chapter
    should_translate = translator.should_translate_chapter('Genesis', '1', verses, 'joe_rogan')
    print(f"Should translate as chapter: {should_translate}")
    
    if should_translate:
        print("\n🔄 Attempting chapter translation...")
        result = translator.translate_chapter('Genesis', '1', verses, 'joe_rogan')
        
        if result:
            print(f"✅ Chapter translation successful! Got {len(result)} verses")
            print("\nFirst 3 verses:")
            for i in range(1, min(4, len(result) + 1)):
                if str(i) in result:
                    print(f"Verse {i}: {result[str(i)]}")
        else:
            print("❌ Chapter translation failed")
    else:
        print("❌ Should not translate as chapter")

if __name__ == "__main__":
    main() 