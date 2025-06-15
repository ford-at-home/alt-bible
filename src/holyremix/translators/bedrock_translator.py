#!/usr/bin/env python3
"""
AI-Powered Bible Chapter Translator

Translates Bible chapters into different personas using Amazon Bedrock.
Supports retry logic, error handling, and checkpointing for reliability.
"""

import json
import time
import re
import sys
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BedrockTranslator:
    """Handles AI-powered Bible translations using Amazon Bedrock."""
    
    def __init__(self, model_id: str = "us.deepseek.r1-v1:0"):
        """
        Initialize the Bedrock translator.
        
        Args:
            model_id: Bedrock model ID to use for translations
        """
        self.model_id = model_id
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
    def create_prompt(self, book: str, chapter: str, verses_dict: Dict[str, str], persona: str) -> str:
        """
        Create the translation prompt for a given persona.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses_dict: Dictionary of verse numbers to verse text
            persona: Persona name for translation
            
        Returns:
            Formatted prompt string
        """
        # Build verses text
        verses_text = "\n".join([
            f"{verse_num}. {verse_text}"
            for verse_num, verse_text in sorted(verses_dict.items(), key=lambda x: int(x[0]))
        ])
        
        prompt = f"""You are {persona}. Rewrite the following chapter of the Bible in your voice. Keep the number of verses the same. Format each verse like this:

1. [your rewrite]
2. ...
3. ...

Do not skip verses. Do not add extra commentary. Return only the numbered verses.

Chapter: {book} {chapter}

{verses_text}"""
        
        return prompt
    
    def translate_chapter(self, book: str, chapter: str, verses_dict: Dict[str, str], persona: str, max_retries: int = 3) -> Optional[Dict[str, str]]:
        """
        Translate a chapter using the specified persona.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses_dict: Dictionary of verse numbers to verse text
            persona: Persona name for translation
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary of verse numbers to translated text, or None if failed
        """
        prompt = self.create_prompt(book, chapter, verses_dict, persona)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Translating {book} {chapter} as {persona} (attempt {attempt + 1}/{max_retries})")
                
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "prompt": prompt,
                        "max_tokens": 4000,
                        "temperature": 0.7,
                        "top_p": 0.9
                    })
                )
                
                response_body = json.loads(response['body'].read())
                translated_text = response_body.get('completion', '').strip()
                
                # Parse the response into verse dictionary
                translated_verses = self._parse_translation_response(translated_text, verses_dict)
                
                if translated_verses:
                    logger.info(f"✅ Successfully translated {book} {chapter} as {persona}")
                    return translated_verses
                else:
                    logger.warning(f"⚠️  Failed to parse translation response for {book} {chapter}")
                    
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ThrottlingException':
                    wait_time = (2 ** attempt) * 5  # Exponential backoff
                    logger.warning(f"⏳ Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Bedrock error: {e}")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                break
        
        logger.error(f"❌ Failed to translate {book} {chapter} as {persona} after {max_retries} attempts")
        return None
    
    def _parse_translation_response(self, response_text: str, original_verses: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Parse the AI response into a verse dictionary.
        
        Args:
            response_text: Raw response from the AI model
            original_verses: Original verses for validation
            
        Returns:
            Parsed verse dictionary or None if parsing failed
        """
        try:
            # Extract numbered verses using regex
            verse_pattern = r'^(\d+)\.\s*(.+)$'
            verses = {}
            
            for line in response_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                match = re.match(verse_pattern, line)
                if match:
                    verse_num = match.group(1)
                    verse_text = match.group(2).strip()
                    
                    # Validate that this verse number exists in original
                    if verse_num in original_verses:
                        verses[verse_num] = verse_text
            
            # Check if we got all verses
            if len(verses) == len(original_verses):
                return verses
            else:
                logger.warning(f"⚠️  Parsed {len(verses)} verses, expected {len(original_verses)}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error parsing translation response: {e}")
            return None


class TranslationManager:
    """Manages the overall translation process with checkpointing."""
    
    def __init__(self, translator: BedrockTranslator):
        """
        Initialize the translation manager.
        
        Args:
            translator: BedrockTranslator instance
        """
        self.translator = translator
        self.checkpoint_file = None
        
    def load_checkpoint(self, persona: str) -> Dict[str, Any]:
        """
        Load translation checkpoint for a persona.
        
        Args:
            persona: Persona name
            
        Returns:
            Checkpoint data
        """
        self.checkpoint_file = f"checkpoint_{persona}.json"
        
        try:
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"completed_chapters": [], "failed_chapters": []}
        except Exception as e:
            logger.error(f"❌ Error loading checkpoint: {e}")
            return {"completed_chapters": [], "failed_chapters": []}
    
    def save_checkpoint(self, persona: str, checkpoint_data: Dict[str, Any]) -> None:
        """
        Save translation checkpoint for a persona.
        
        Args:
            persona: Persona name
            checkpoint_data: Checkpoint data to save
        """
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving checkpoint: {e}")
    
    def translate_bible(self, kjv_data: Dict[str, Any], persona: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Translate the entire Bible for a given persona.
        
        Args:
            kjv_data: Restructured KJV data
            persona: Persona name for translation
            dry_run: If True, only show what would be translated
            
        Returns:
            Translated Bible data
        """
        print(f"🎭 Starting Bible translation for persona: {persona}")
        print("=" * 50)
        
        checkpoint = self.load_checkpoint(persona)
        completed_chapters = set(checkpoint["completed_chapters"])
        failed_chapters = set(checkpoint["failed_chapters"])
        
        translated_bible = {}
        total_chapters = sum(len(chapters) for chapters in kjv_data.values())
        processed_chapters = 0
        
        for book, chapters in kjv_data.items():
            translated_bible[book] = {}
            
            for chapter, verses in chapters.items():
                chapter_key = f"{book}_{chapter}"
                processed_chapters += 1
                
                print(f"📖 Processing {book} {chapter} ({processed_chapters}/{total_chapters})")
                
                # Skip if already completed
                if chapter_key in completed_chapters:
                    print(f"⏭️  Skipping {book} {chapter} (already completed)")
                    continue
                
                # Skip if previously failed
                if chapter_key in failed_chapters:
                    print(f"⚠️  Skipping {book} {chapter} (previously failed)")
                    continue
                
                if dry_run:
                    print(f"🔍 DRY RUN: Would translate {book} {chapter} as {persona}")
                    continue
                
                # Perform translation
                translated_verses = self.translator.translate_chapter(book, chapter, verses, persona)
                
                if translated_verses:
                    translated_bible[book][chapter] = translated_verses
                    completed_chapters.add(chapter_key)
                    checkpoint["completed_chapters"] = list(completed_chapters)
                    self.save_checkpoint(persona, checkpoint)
                else:
                    failed_chapters.add(chapter_key)
                    checkpoint["failed_chapters"] = list(failed_chapters)
                    self.save_checkpoint(persona, checkpoint)
        
        return translated_bible


def main():
    """Main function for testing the translator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Bible Translator")
    parser.add_argument("--persona", required=True, help="Persona name for translation")
    parser.add_argument("--book", help="Specific book to translate (optional)")
    parser.add_argument("--chapter", help="Specific chapter to translate (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated without actually translating")
    parser.add_argument("--kjv-file", default="data/processed/kjv_bible.json", help="Path to KJV Bible JSON file")
    
    args = parser.parse_args()
    
    # Load KJV data
    try:
        with open(args.kjv_file, 'r') as f:
            kjv_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ KJV file not found: {args.kjv_file}")
        print("💡 Run scripts/kjv_preprocessor.py first to download and structure the KJV data")
        sys.exit(1)
    
    # Initialize translator
    translator = BedrockTranslator()
    manager = TranslationManager(translator)
    
    if args.book and args.chapter:
        # Translate specific chapter
        if args.book in kjv_data and args.chapter in kjv_data[args.book]:
            verses = kjv_data[args.book][args.chapter]
            result = translator.translate_chapter(args.book, args.chapter, verses, args.persona)
            if result:
                print(f"✅ Translation complete for {args.book} {args.chapter}:")
                for verse_num, text in result.items():
                    print(f"{verse_num}. {text}")
            else:
                print(f"❌ Translation failed for {args.book} {args.chapter}")
        else:
            print(f"❌ Chapter {args.book} {args.chapter} not found")
    else:
        # Translate entire Bible
        result = manager.translate_bible(kjv_data, args.persona, args.dry_run)
        
        if not args.dry_run:
            # Save results
            output_file = f"translated_bible_{args.persona}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Translation saved to {output_file}")


if __name__ == "__main__":
    main() 