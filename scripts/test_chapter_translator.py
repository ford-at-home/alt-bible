#!/usr/bin/env python3
"""
Test script for the Chapter Translator

Tests token counting, cost estimation, and translation methods.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from translators.chapter_translator import ChapterTranslator, VerseByVerseTranslator


def test_token_counting():
    """Test token counting functionality."""
    print("🧪 Testing token counting...")
    
    translator = ChapterTranslator()
    
    # Test with known text
    test_text = "This is a test sentence with some words."
    tokens = translator.count_tokens(test_text)
    
    print(f"   Text: '{test_text}'")
    print(f"   Tokens: {tokens}")
    
    if translator.tokenizer_available:
        print("   ✅ tiktoken available - accurate counting")
    else:
        print("   ⚠️  Using rough estimation")
    
    return tokens > 0


def test_chapter_formatting():
    """Test chapter formatting."""
    print("\n🧪 Testing chapter formatting...")
    
    translator = ChapterTranslator()
    
    # Sample verses
    verses = {
        "1": "In the beginning God created the heaven and the earth.",
        "2": "And the earth was without form, and void; and darkness was upon the face of the deep.",
        "3": "And the Spirit of God moved upon the face of the waters."
    }
    
    formatted = translator.format_chapter_for_translation("Genesis", "1", verses)
    print(f"   Formatted chapter:\n{formatted}")
    
    return "Verse 1:" in formatted and "Verse 2:" in formatted


def test_token_estimation():
    """Test token estimation for different personas."""
    print("\n🧪 Testing token estimation...")
    
    translator = ChapterTranslator()
    
    # Sample verses
    verses = {
        "1": "In the beginning God created the heaven and the earth.",
        "2": "And the earth was without form, and void; and darkness was upon the face of the deep.",
        "3": "And the Spirit of God moved upon the face of the waters."
    }
    
    personas = ["joe_rogan", "samuel_l_jackson", "cardi_b"]
    
    for persona in personas:
        input_tokens, output_tokens = translator.estimate_chapter_tokens("Genesis", "1", verses, persona)
        total = input_tokens + output_tokens
        
        print(f"   {persona}:")
        print(f"     Input tokens: {input_tokens}")
        print(f"     Output tokens: {output_tokens}")
        print(f"     Total: {total}")
        print(f"     Should translate as chapter: {translator.should_translate_chapter('Genesis', '1', verses, persona)}")
    
    return True


def test_long_chapter_detection():
    """Test detection of long chapters that need verse-by-verse translation."""
    print("\n🧪 Testing long chapter detection...")
    
    translator = ChapterTranslator()
    
    # Create a long chapter (simulate Psalm 119)
    long_verses = {}
    for i in range(1, 177):  # Psalm 119 has 176 verses
        long_verses[str(i)] = "This is a long verse that would make the chapter very long and exceed token limits."
    
    should_translate_as_chapter = translator.should_translate_chapter("Psalms", "119", long_verses, "joe_rogan")
    
    print(f"   Long chapter (176 verses): {should_translate_as_chapter}")
    print(f"   Expected: False (should use verse-by-verse)")
    
    return not should_translate_as_chapter


def test_prompt_creation():
    """Test prompt creation for different personas."""
    print("\n🧪 Testing prompt creation...")
    
    translator = ChapterTranslator()
    
    verses = {
        "1": "In the beginning God created the heaven and the earth.",
        "2": "And the earth was without form, and void; and darkness was upon the face of the deep."
    }
    
    prompt = translator.create_chapter_prompt("Genesis", "1", verses, "joe_rogan")
    
    print(f"   Prompt length: {len(prompt)} characters")
    print(f"   Contains persona: {'joe_rogan' in prompt}")
    print(f"   Contains verse markers: {'Verse 1:' in prompt}")
    
    return len(prompt) > 100 and "joe_rogan" in prompt


def main():
    """Run all tests."""
    print("🚀 Testing Chapter Translator")
    print("=" * 50)
    
    tests = [
        test_token_counting,
        test_chapter_formatting,
        test_token_estimation,
        test_long_chapter_detection,
        test_prompt_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("   ✅ PASSED")
            else:
                print("   ❌ FAILED")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 