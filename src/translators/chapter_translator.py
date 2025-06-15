#!/usr/bin/env python3
"""
Chapter-based Bible translator with strict JSON output for database ingestion.
"""

import boto3
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.prompt_templates import get_strict_json_prompt
from utils.schema_validator import BibleTranslationValidator
from utils.persona_loader import get_hardcore_prompt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChapterTranslator:
    """Handles chapter-based Bible translation with strict JSON output for database ingestion."""
    
    def __init__(self, model_id: str = "us.deepseek.r1-v1:0", max_tokens: int = 4000, intensity: str = "medium"):
        """
        Initialize the chapter translator.
        
        Args:
            model_id: Bedrock model ID to use
            max_tokens: Maximum safe tokens for the model
            intensity: "mild", "medium", "wild", or "nuclear" for style transfer
        """
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.intensity = intensity
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.validator = BibleTranslationValidator()
        
        # Token counting
        try:
            import tiktoken
            self.encoder = tiktoken.get_encoding("cl100k_base")
            self.tokenizer_available = True
        except ImportError:
            logger.warning("tiktoken not available, using rough estimation")
            self.encoder = None
            self.tokenizer_available = False
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.tokenizer_available:
            return len(self.encoder.encode(text))
        else:
            # Rough estimation: ~4 characters per token
            return len(text) // 4
    
    def create_strict_json_prompt(self, book: str, chapter: str, verses_dict: Dict[str, str], persona: str) -> str:
        """
        Create a strict JSON prompt for database-compatible translation.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses_dict: Dictionary of verse numbers to verse text
            persona: Persona name for translation
            
        Returns:
            Formatted prompt with strict JSON requirements
        """
        # Get persona-specific context
        hardcore_prompts = get_hardcore_prompt(persona, self.intensity)
        
        # Format chapter text for context
        chapter_text = self.format_chapter_for_context(book, chapter, verses_dict)
        
        # Get the strict JSON prompt template
        base_prompt = get_strict_json_prompt(book, chapter, persona, max(verses_dict.keys(), key=int))
        
        # Add persona context and chapter text
        if hardcore_prompts:
            persona_context = f"Context: {hardcore_prompts['system_prompt']}\n\n"
        else:
            persona_context = f"Context: You are {persona}.\n\n"
        
        full_prompt = f"{persona_context}{base_prompt}\n\nChapter text:\n{chapter_text}"
        
        return full_prompt
    
    def format_chapter_for_context(self, book: str, chapter: str, verses_dict: Dict[str, str]) -> str:
        """
        Format a chapter for context in the prompt.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses_dict: Dictionary of verse numbers to verse text
            
        Returns:
            Formatted chapter text for context
        """
        # Sort verses by number
        sorted_verses = sorted(verses_dict.items(), key=lambda x: int(x[0]))
        
        # Format as numbered list
        chapter_text = f"{book} {chapter}:\n"
        for verse_num, verse_text in sorted_verses:
            chapter_text += f"{verse_num}. {verse_text}\n"
        
        return chapter_text.strip()
    
    def estimate_chapter_tokens(self, book: str, chapter: str, verses_dict: Dict[str, str], persona: str) -> Tuple[int, int]:
        """
        Estimate input and output tokens for a chapter translation.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses_dict: Dictionary of verse numbers to verse text
            persona: Persona name for translation
            
        Returns:
            Tuple of (input_tokens, estimated_output_tokens)
        """
        prompt = self.create_strict_json_prompt(book, chapter, verses_dict, persona)
        input_tokens = self.count_tokens(prompt)
        
        # Estimate output tokens based on persona verbosity and JSON structure
        persona_ratios = {
            "samuel_l_jackson": 1.3,
            "joe_rogan": 1.2,
            "cardi_b": 1.4,
            "ram_dass": 1.1,
            "hunter_s_thompson": 1.5,
            "maya_angelou": 1.3
        }
        
        ratio = persona_ratios.get(persona, 1.2)
        estimated_output = int(input_tokens * ratio)
        
        return input_tokens, estimated_output
    
    def translate_chapter(self, book: str, chapter: str, verses_dict: Dict[str, str], persona: str, max_retries: int = 3) -> Optional[Dict[str, str]]:
        """
        Translate a chapter using the LLM with strict JSON output and validation.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses_dict: Dictionary of verse numbers to verse text
            persona: Persona name for translation
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary of verse numbers to translated text, or None if failed
        """
        prompt = self.create_strict_json_prompt(book, chapter, verses_dict, persona)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Translating {book} {chapter} as {persona} (attempt {attempt + 1}/{max_retries})")
                
                # Call the LLM
                llm_output = self._call_llm(prompt)
                
                # Validate and repair the output
                success, parsed_data, error_msg = self.validator.validate_and_repair(llm_output, verses_dict)
                
                if success:
                    logger.info(f"✅ Successfully translated {book} {chapter} as {persona}")
                    return parsed_data["verses"]
                else:
                    logger.warning(f"⚠️  Validation failed (attempt {attempt + 1}): {error_msg}")
                    
                    # If this is the last attempt, use fallback
                    if attempt == max_retries - 1:
                        logger.warning("🔄 Using fallback data due to validation failures")
                        fallback_data = self.validator.create_fallback_data(book, chapter, verses_dict, persona)
                        return fallback_data["verses"]
                    
                    # Continue to next attempt
                    continue
                    
            except Exception as e:
                logger.error(f"❌ Error in translation attempt {attempt + 1}: {e}")
                
                # If this is the last attempt, use fallback
                if attempt == max_retries - 1:
                    logger.warning("🔄 Using fallback data due to errors")
                    fallback_data = self.validator.create_fallback_data(book, chapter, verses_dict, persona)
                    return fallback_data["verses"]
        
        return None
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with the given prompt.
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            Raw LLM response
        """
        try:
            if self.model_id.startswith("us.deepseek"):
                # DeepSeek R1 uses converse() API
                response = self.bedrock.converse(
                    modelId=self.model_id,
                    system=[{"text": "You are a helpful AI assistant that generates JSON output."}],
                    messages=[
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    inferenceConfig={
                        "temperature": 0.7,
                        "topP": 0.9,
                        "maxTokens": self.max_tokens
                    }
                )
                
                llm_output = response["output"]["message"]["content"][0]["text"].strip()
                
            elif self.model_id.startswith("anthropic.claude"):
                # Claude format
                request_body = {
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": self.max_tokens,
                    "temperature": 0.7
                }
                
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                response_body = json.loads(response['body'].read())
                llm_output = response_body.get('completion', '').strip()
                
            else:
                # Standard format for other models
                request_body = {
                    "prompt": prompt,
                    "max_tokens": self.max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
                
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                response_body = json.loads(response['body'].read())
                llm_output = response_body.get('text') or response_body.get('completion', '').strip()
            
            # Log raw LLM output
            self._log_llm_output(llm_output)
            
            return llm_output
            
        except Exception as e:
            logger.error(f"❌ LLM call failed: {e}")
            raise
    
    def _log_llm_output(self, llm_output: str):
        """Log the raw LLM output for debugging."""
        try:
            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Save to file
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            log_file = logs_dir / f"llm_raw_output_{timestamp}.txt"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(llm_output)
            
            logger.info(f"📝 Raw LLM output saved to {log_file}")
            
            # Log first few lines
            lines = llm_output.split('\n')[:10]
            logger.info("--- LLM Output (first 10 lines) ---")
            for line in lines:
                logger.info(line)
            logger.info("--- end ---")
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to log LLM output: {e}")
    
    def should_translate_chapter(self, book: str, chapter: str, verses_dict: Dict[str, str], persona: str) -> bool:
        """
        Determine if a chapter should be translated as a whole or verse-by-verse.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses_dict: Dictionary of verse numbers to verse text
            persona: Persona name for translation
            
        Returns:
            True if chapter should be translated as whole, False for verse-by-verse
        """
        input_tokens, estimated_output = self.estimate_chapter_tokens(book, chapter, verses_dict, persona)
        total_estimated = input_tokens + estimated_output
        
        # Leave some buffer for safety
        safe_limit = self.max_tokens * 0.8
        
        if total_estimated <= safe_limit:
            logger.info(f"✅ Chapter {book} {chapter} fits within token limit ({total_estimated} tokens)")
            return True
        else:
            logger.warning(f"⚠️  Chapter {book} {chapter} exceeds token limit ({total_estimated} tokens), will use verse-by-verse")
            return False
    
    def save_chapter_translation(self, book: str, chapter: str, translated_verses: Dict[str, str], persona: str, output_dir: str = "data/processed/translations") -> List[Dict[str, Any]]:
        """
        Save chapter translation to both .txt file and prepare for DynamoDB.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            translated_verses: Dictionary of verse numbers to translated text
            persona: Persona name for translation
            output_dir: Directory to save .txt files
            
        Returns:
            List of DynamoDB items
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save as .txt file
        txt_file = output_path / f"{persona}_{book}_{chapter}.txt"
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"Chapter {book} {chapter} - {persona} Translation\n")
            f.write("=" * 50 + "\n\n")
            
            for verse_num, text in sorted(translated_verses.items(), key=lambda x: int(x[0])):
                f.write(f"Verse {verse_num}: {text}\n\n")
        
        logger.info(f"💾 Saved chapter translation to {txt_file}")
        
        # Prepare DynamoDB items
        dynamodb_items = []
        for verse_num, text in translated_verses.items():
            item = {
                'pk': f"persona#{persona}",
                'sk': f"book#{book}#{chapter}#{verse_num}",
                'translated_text': text,
                'metadata': {
                    'book': book,
                    'chapter': int(chapter),
                    'verse': int(verse_num),
                    'persona': persona,
                    'translation_date': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'model_used': self.model_id,
                    'translation_method': 'chapter'
                }
            }
            dynamodb_items.append(item)
        
        return dynamodb_items


class VerseByVerseTranslator:
    """Fallback translator for verse-by-verse translation."""
    
    def __init__(self, model_id: str = "us.deepseek.r1-v1:0"):
        """Initialize the verse-by-verse translator."""
        self.model_id = model_id
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    def translate_verse(self, book: str, chapter: str, verse_num: str, verse_text: str, persona: str) -> Optional[str]:
        """
        Translate a single verse with rich persona context.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verse_num: Verse number
            verse_text: Original verse text
            persona: Persona name for translation
            
        Returns:
            Translated verse text or None if failed
        """
        # Load persona metadata
        try:
            from utils.persona_loader import get_persona
            persona_info = get_persona(persona)
        except ImportError:
            persona_info = None
        
        if persona_info:
            prompt = f"""You are {persona_info['display_name']} ({persona}).

Background: {persona_info['description']}
Style: {persona_info['style']}
Characteristic phrases: {', '.join(persona_info['catchphrases'])}

Rewrite this single verse of the Bible in your authentic voice, maintaining your characteristic style and personality:

{book} {chapter}:{verse_num} - {verse_text}

Return only the translated verse:"""
        else:
            prompt = f"""You are {persona}. Rewrite this single verse of the Bible in your voice:

{book} {chapter}:{verse_num} - {verse_text}

Return only the translated verse:"""
        
        try:
            # Format request body based on model type
            if self.model_id.startswith("us.deepseek"):
                # DeepSeek format
                response = self.bedrock.converse(
                    modelId=self.model_id,
                    system=[{"text": "You are a helpful AI assistant."}],
                    messages=[
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    inferenceConfig={
                        "temperature": 0.7,
                        "topP": 0.9,
                        "maxTokens": 200
                    }
                )
                
                translated_text = response["output"]["message"]["content"][0]["text"].strip()
                
            elif self.model_id.startswith("anthropic.claude"):
                # Claude format
                request_body = {
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": 200,
                    "temperature": 0.7
                }
                
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                response_body = json.loads(response['body'].read())
                translated_text = response_body.get('completion', '').strip()
                
            else:
                # Standard format for other models
                request_body = {
                    "prompt": prompt,
                    "max_tokens": 200,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
                
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                response_body = json.loads(response['body'].read())
                translated_text = response_body.get('text') or response_body.get('completion', '').strip()
            
            return translated_text if translated_text else None
            
        except Exception as e:
            logger.error(f"❌ Error translating verse {book} {chapter}:{verse_num}: {e}")
            return None


def main():
    """Test the chapter translator."""
    import sys
    sys.path.insert(0, 'src')
    
    # Test with a small chapter
    translator = ChapterTranslator(intensity="nuclear")
    
    # Sample verses
    verses = {
        "1": "In the beginning God created the heaven and the earth.",
        "2": "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.",
        "3": "And God said, Let there be light: and there was light."
    }
    
    result = translator.translate_chapter("Genesis", "1", verses, "joe_rogan")
    
    if result:
        print("✅ Translation successful!")
        for verse_num, text in sorted(result.items(), key=lambda x: int(x[0])):
            print(f"Verse {verse_num}: {text}")
    else:
        print("❌ Translation failed")


if __name__ == "__main__":
    main() 