#!/usr/bin/env python3
"""
Test suite for HOLY REMIX project

Tests the preprocessing, translation, and storage components.
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_preprocessor():
    """Test the JSON preprocessor."""
    print("🧪 Testing JSON preprocessor...")
    
    try:
        from preprocessors.json_preprocessor import restructure_kjv_data, validate_restructured_data
        
        # Test with sample data
        sample_data = {
            "Genesis": {
                "1": {
                    "1": "In the beginning God created the heaven and the earth.",
                    "2": "And the earth was without form, and void; and darkness was upon the face of the deep."
                }
            }
        }
        
        # Test restructuring
        restructured = restructure_kjv_data(sample_data)
        assert "Genesis" in restructured
        assert "1" in restructured["Genesis"]
        assert "1" in restructured["Genesis"]["1"]
        
        # Test validation
        is_valid = validate_restructured_data(restructured)
        assert is_valid
        
        print("✅ JSON preprocessor tests passed")
        return True
        
    except Exception as e:
        print(f"❌ JSON preprocessor test failed: {e}")
        return False


def test_persona_loader():
    """Test the persona loader."""
    print("🧪 Testing persona loader...")
    
    try:
        from utils.persona_loader import get_persona, list_personas
        
        # Test getting a specific persona
        joe_info = get_persona("joe_rogan")
        assert joe_info is not None
        assert joe_info["display_name"] == "Joe Rogan"
        assert "description" in joe_info
        assert "style" in joe_info
        assert "catchphrases" in joe_info
        
        # Test listing all personas
        personas = list_personas()
        assert len(personas) > 0
        assert any(p["key"] == "joe_rogan" for p in personas)
        
        print("✅ Persona loader tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Persona loader test failed: {e}")
        return False


def test_chapter_translator():
    """Test the chapter translator."""
    print("🧪 Testing chapter translator...")
    
    try:
        from translators.chapter_translator import ChapterTranslator
        
        translator = ChapterTranslator()
        
        # Test prompt creation
        verses = {
            "1": "In the beginning God created the heaven and the earth.",
            "2": "And the earth was without form, and void; and darkness was upon the face of the deep."
        }
        
        prompt = translator.create_chapter_prompt("Genesis", "1", verses, "joe_rogan")
        assert "Joe Rogan" in prompt
        assert "Background:" in prompt
        assert "Style:" in prompt
        assert "Characteristic phrases:" in prompt
        
        # Test token estimation
        input_tokens, output_tokens = translator.estimate_chapter_tokens("Genesis", "1", verses, "joe_rogan")
        assert input_tokens > 0
        assert output_tokens > 0
        
        print("✅ Chapter translator tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Chapter translator test failed: {e}")
        return False


def test_cost_calculator():
    """Test the cost calculator."""
    print("🧪 Testing cost calculator...")
    
    try:
        from utils.cost_calculator import calculate_translation_cost
        
        # Test cost calculation
        cost = calculate_translation_cost(1000, 2000, "us.deepseek.r1-v1:0")
        assert cost > 0
        
        print("✅ Cost calculator tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Cost calculator test failed: {e}")
        return False


def test_data_structure():
    """Test the processed data structure."""
    print("🧪 Testing data structure...")
    
    try:
        # Check if processed data exists
        data_file = Path("data/processed/kjv_bible.json")
        if not data_file.exists():
            print("⚠️  No processed data found, skipping structure test")
            return True
        
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        # Test structure
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Test first book structure
        first_book = list(data.keys())[0]
        assert isinstance(data[first_book], dict)
        
        first_chapter = list(data[first_book].keys())[0]
        assert isinstance(data[first_book][first_chapter], dict)
        
        first_verse = list(data[first_book][first_chapter].keys())[0]
        assert isinstance(data[first_book][first_chapter][first_verse], str)
        
        print("✅ Data structure tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Running HOLY REMIX test suite...")
    print("=" * 50)
    
    tests = [
        test_preprocessor,
        test_persona_loader,
        test_chapter_translator,
        test_cost_calculator,
        test_data_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 