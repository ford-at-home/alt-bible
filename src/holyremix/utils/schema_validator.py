#!/usr/bin/env python3
"""
Schema validator and repair utilities for LLM JSON output
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class BibleTranslationValidator:
    """Validates and repairs Bible translation JSON output."""
    
    def __init__(self):
        self.required_keys = ["book", "chapter", "verses"]
        self.verses_required_keys = ["book", "chapter"]
    
    def validate_structure(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate the basic structure of the JSON response.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required top-level keys
            for key in self.required_keys:
                if key not in data:
                    return False, f"Missing required key: {key}"
            
            # Check verses object
            if not isinstance(data["verses"], dict):
                return False, "Verses must be an object"
            
            # Check that verses has at least one entry
            if not data["verses"]:
                return False, "Verses object is empty"
            
            # Check verse number format (should be strings)
            for verse_num in data["verses"].keys():
                if not isinstance(verse_num, str):
                    return False, f"Verse number {verse_num} must be a string"
                if not verse_num.isdigit():
                    return False, f"Verse number {verse_num} must be numeric"
            
            # Check verse content (should be strings)
            for verse_num, content in data["verses"].items():
                if not isinstance(content, str):
                    return False, f"Verse {verse_num} content must be a string"
                if not content.strip():
                    return False, f"Verse {verse_num} content is empty"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def repair_json_string(self, json_string: str) -> Optional[str]:
        """
        Repair common JSON formatting issues.
        
        Args:
            json_string: Raw JSON string from LLM
            
        Returns:
            Repaired JSON string or None if unrepairable
        """
        try:
            # Remove markdown code blocks
            json_string = re.sub(r'```json\s*', '', json_string)
            json_string = re.sub(r'```\s*$', '', json_string)
            json_string = re.sub(r'^```\s*', '', json_string)
            
            # Remove leading/trailing text
            json_start = json_string.find('{')
            json_end = json_string.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return None
            
            json_string = json_string[json_start:json_end]
            
            # Fix common JSON issues
            json_string = re.sub(r',\s*}', '}', json_string)  # Remove trailing commas
            json_string = re.sub(r',\s*]', ']', json_string)  # Remove trailing commas in arrays
            
            # Try to parse to validate
            json.loads(json_string)
            return json_string
            
        except Exception as e:
            logger.warning(f"Failed to repair JSON string: {e}")
            return None
    
    def validate_and_repair(self, llm_output: str, expected_verses: Dict[str, str]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Validate and repair LLM output.
        
        Args:
            llm_output: Raw LLM response
            expected_verses: Original verses for validation
            
        Returns:
            Tuple of (success, parsed_data, error_message)
        """
        try:
            # First, try to repair the JSON string
            repaired_json = self.repair_json_string(llm_output)
            if not repaired_json:
                return False, None, "Could not extract valid JSON from LLM output"
            
            # Parse the JSON
            data = json.loads(repaired_json)
            
            # Validate structure
            is_valid, error_msg = self.validate_structure(data)
            if not is_valid:
                return False, None, f"Structure validation failed: {error_msg}"
            
            # Validate verse completeness
            expected_verse_nums = set(expected_verses.keys())
            actual_verse_nums = set(data["verses"].keys())
            
            missing_verses = expected_verse_nums - actual_verse_nums
            extra_verses = actual_verse_nums - expected_verse_nums
            
            if missing_verses:
                return False, None, f"Missing verses: {missing_verses}"
            
            if extra_verses:
                logger.warning(f"Extra verses found: {extra_verses}")
                # Remove extra verses for database compatibility
                for extra_verse in extra_verses:
                    del data["verses"][extra_verse]
            
            logger.info(f"✅ Successfully validated and repaired JSON with {len(data['verses'])} verses")
            return True, data, "Success"
            
        except json.JSONDecodeError as e:
            return False, None, f"JSON parsing failed: {str(e)}"
        except Exception as e:
            return False, None, f"Validation error: {str(e)}"
    
    def create_fallback_data(self, book: str, chapter: str, original_verses: Dict[str, str], persona: str) -> Dict[str, Any]:
        """
        Create fallback data structure when validation fails.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            original_verses: Original verse content
            persona: Persona name
            
        Returns:
            Fallback data structure
        """
        # Add persona prefixes to original verses
        persona_prefixes = {
            "joe_rogan": "Dude, ",
            "samuel_l_jackson": "Listen up, ",
            "cardi_b": "Okurrr, ",
            "maya_angelou": "With grace, ",
            "ram_dass": "In consciousness, ",
            "hunter_s_thompson": "In the gonzo spirit, "
        }
        
        prefix = persona_prefixes.get(persona, "")
        
        fallback_verses = {}
        for verse_num, original_text in original_verses.items():
            fallback_verses[verse_num] = f"{prefix}{original_text.lower()}"
        
        return {
            "book": book,
            "chapter": int(chapter),
            "verses": fallback_verses
        } 