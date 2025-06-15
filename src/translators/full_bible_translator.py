#!/usr/bin/env python3
"""
Full Bible translator that processes entire books and outputs in BBE.json format.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from translators.chapter_translator import ChapterTranslator, VerseByVerseTranslator
from utils.persona_loader import get_persona

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FullBibleTranslator:
    """Handles full Bible translation with progress tracking and checkpointing."""
    
    def __init__(self, model_id: str = "us.deepseek.r1-v1:0", max_tokens: int = 4000, intensity: str = "medium", max_workers: int = 1):
        """
        Initialize the full Bible translator.
        
        Args:
            model_id: Bedrock model ID to use
            max_tokens: Maximum safe tokens for the model
            intensity: "mild", "medium", "wild", or "nuclear" for style transfer
            max_workers: Maximum concurrent translation workers (1 for rate limiting)
        """
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.intensity = intensity
        self.max_workers = max_workers
        self.chapter_translator = ChapterTranslator(model_id, max_tokens, intensity)
        self.verse_translator = VerseByVerseTranslator(model_id)
        
        # Progress tracking
        self.progress_lock = threading.Lock()
        self.total_chapters = 0
        self.completed_chapters = 0
        self.failed_chapters = []
        
        # Cost tracking
        self.total_cost = 0.0
        self.cost_lock = threading.Lock()
    
    def load_bible_data(self, input_file: str = "data/processed/kjv_bible.json") -> Dict[str, Any]:
        """
        Load the source Bible data.
        
        Args:
            input_file: Path to the source Bible JSON file
            
        Returns:
            Bible data dictionary
        """
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"📖 Loaded Bible data with {len(data)} books")
        return data
    
    def estimate_full_translation_cost(self, bible_data: Dict[str, Any], persona: str) -> Dict[str, Any]:
        """
        Estimate the cost for translating the entire Bible.
        
        Args:
            bible_data: Bible data dictionary
            persona: Persona name for translation
            
        Returns:
            Cost estimation dictionary
        """
        total_chapters = 0
        total_verses = 0
        estimated_input_tokens = 0
        estimated_output_tokens = 0
        
        for book_name, book_data in bible_data.items():
            for chapter_num, chapter_data in book_data.items():
                total_chapters += 1
                total_verses += len(chapter_data)
                
                # Estimate tokens for this chapter
                input_tokens, output_tokens = self.chapter_translator.estimate_chapter_tokens(
                    book_name, chapter_num, chapter_data, persona
                )
                estimated_input_tokens += input_tokens
                estimated_output_tokens += output_tokens
        
        # Calculate cost (DeepSeek R1 pricing)
        input_cost = (estimated_input_tokens / 1000) * 0.0005
        output_cost = (estimated_output_tokens / 1000) * 0.0010
        total_cost = input_cost + output_cost
        
        return {
            "total_books": len(bible_data),
            "total_chapters": total_chapters,
            "total_verses": total_verses,
            "estimated_input_tokens": estimated_input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_input_cost": input_cost,
            "estimated_output_cost": output_cost,
            "estimated_total_cost": total_cost
        }
    
    def translate_chapter_with_fallback(self, book: str, chapter: str, verses: Dict[str, str], persona: str) -> Optional[Dict[str, str]]:
        """
        Translate a chapter with fallback to verse-by-verse if needed.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses: Dictionary of verse numbers to verse text
            persona: Persona name for translation
            
        Returns:
            Translated verses dictionary or None if failed
        """
        try:
            # Try chapter-level translation first
            if self.chapter_translator.should_translate_chapter(book, chapter, verses, persona):
                result = self.chapter_translator.translate_chapter(book, chapter, verses, persona)
                if result:
                    return result
            
            # Fallback to verse-by-verse translation
            logger.info(f"🔄 Falling back to verse-by-verse translation for {book} {chapter}")
            translated_verses = {}
            
            for verse_num, verse_text in verses.items():
                translated_text = self.verse_translator.translate_verse(book, chapter, verse_num, verse_text, persona)
                if translated_text:
                    translated_verses[verse_num] = translated_text
                else:
                    # Ultimate fallback: use original with persona prefix
                    persona_prefixes = {
                        "joe_rogan": "Dude, ",
                        "samuel_l_jackson": "Listen up, ",
                        "cardi_b": "Okurrr, ",
                        "maya_angelou": "With grace, ",
                        "ram_dass": "In consciousness, ",
                        "hunter_s_thompson": "In the gonzo spirit, "
                    }
                    prefix = persona_prefixes.get(persona, "")
                    translated_verses[verse_num] = f"{prefix}{verse_text.lower()}"
            
            return translated_verses if len(translated_verses) == len(verses) else None
            
        except Exception as e:
            logger.error(f"❌ Error translating {book} {chapter}: {e}")
            return None
    
    def translate_book(self, book_name: str, book_data: Dict[str, Any], persona: str, output_dir: str) -> Dict[str, Any]:
        """
        Translate an entire book.
        
        Args:
            book_name: Name of the book
            book_data: Book data dictionary
            persona: Persona name for translation
            output_dir: Output directory for checkpoints
            
        Returns:
            Translated book data
        """
        logger.info(f"📚 Starting translation of {book_name} ({len(book_data)} chapters)")
        
        translated_book = {}
        
        for chapter_num, chapter_verses in book_data.items():
            try:
                # Translate chapter
                translated_verses = self.translate_chapter_with_fallback(book_name, chapter_num, chapter_verses, persona)
                
                if translated_verses:
                    translated_book[chapter_num] = translated_verses
                    
                    # Update progress
                    with self.progress_lock:
                        self.completed_chapters += 1
                        progress = (self.completed_chapters / self.total_chapters) * 100
                        logger.info(f"📊 Progress: {self.completed_chapters}/{self.total_chapters} chapters ({progress:.1f}%) - {book_name} {chapter_num}")
                    
                    # Save checkpoint
                    self._save_checkpoint(book_name, chapter_num, translated_verses, persona, output_dir)
                    
                    # Rate limiting
                    time.sleep(1)  # 1 second between chapters
                    
                else:
                    logger.error(f"❌ Failed to translate {book_name} {chapter_num}")
                    with self.progress_lock:
                        self.failed_chapters.append(f"{book_name} {chapter_num}")
                    
            except Exception as e:
                logger.error(f"❌ Error in {book_name} {chapter_num}: {e}")
                with self.progress_lock:
                    self.failed_chapters.append(f"{book_name} {chapter_num}")
        
        logger.info(f"✅ Completed translation of {book_name}")
        return translated_book
    
    def _save_checkpoint(self, book: str, chapter: str, verses: Dict[str, str], persona: str, output_dir: str):
        """Save a checkpoint for a translated chapter."""
        try:
            checkpoint_dir = Path(output_dir) / "checkpoints" / persona
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            checkpoint_file = checkpoint_dir / f"{book}_{chapter}.json"
            
            checkpoint_data = {
                "book": book,
                "chapter": chapter,
                "verses": verses,
                "translation_date": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "persona": persona,
                "model_used": self.model_id,
                "intensity": self.intensity
            }
            
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"⚠️  Failed to save checkpoint for {book} {chapter}: {e}")
    
    def translate_full_bible(self, persona: str, input_file: str = "data/processed/kjv_bible.json", 
                           output_dir: str = "data/processed/translations", 
                           books_to_translate: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Translate the full Bible for a given persona.
        
        Args:
            persona: Persona name for translation
            input_file: Path to source Bible JSON file
            output_dir: Output directory for translations
            books_to_translate: List of specific books to translate (None for all)
            
        Returns:
            Complete translated Bible data
        """
        # Load Bible data
        bible_data = self.load_bible_data(input_file)
        
        # Filter books if specified
        if books_to_translate:
            bible_data = {book: bible_data[book] for book in books_to_translate if book in bible_data}
            logger.info(f"🎯 Translating specific books: {books_to_translate}")
        
        # Calculate total chapters for progress tracking
        self.total_chapters = sum(len(book_data) for book_data in bible_data.values())
        self.completed_chapters = 0
        self.failed_chapters = []
        
        # Estimate cost
        cost_estimate = self.estimate_full_translation_cost(bible_data, persona)
        logger.info(f"💰 Cost estimate: ${cost_estimate['estimated_total_cost']:.2f}")
        logger.info(f"📊 Will translate {cost_estimate['total_chapters']} chapters, {cost_estimate['total_verses']} verses")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Start translation
        start_time = time.time()
        translated_bible = {}
        
        try:
            # Use ThreadPoolExecutor for potential parallelization (but max_workers=1 for rate limiting)
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all book translations
                future_to_book = {
                    executor.submit(self.translate_book, book_name, book_data, persona, output_dir): book_name
                    for book_name, book_data in bible_data.items()
                }
                
                # Collect results
                for future in as_completed(future_to_book):
                    book_name = future_to_book[future]
                    try:
                        translated_book = future.result()
                        translated_bible[book_name] = translated_book
                    except Exception as e:
                        logger.error(f"❌ Failed to translate book {book_name}: {e}")
                        self.failed_chapters.append(f"Book: {book_name}")
            
            # Save complete translation
            output_file = output_path / f"{persona}_full_bible.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translated_bible, f, indent=2, ensure_ascii=False)
            
            # Calculate final statistics
            end_time = time.time()
            duration = end_time - start_time
            
            final_stats = {
                "persona": persona,
                "total_books": len(translated_bible),
                "total_chapters": self.completed_chapters,
                "failed_chapters": len(self.failed_chapters),
                "duration_seconds": duration,
                "duration_hours": duration / 3600,
                "estimated_cost": cost_estimate['estimated_total_cost'],
                "output_file": str(output_file),
                "failed_chapters_list": self.failed_chapters
            }
            
            # Save statistics
            stats_file = output_path / f"{persona}_translation_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(final_stats, f, indent=2)
            
            logger.info(f"🎉 Full Bible translation completed!")
            logger.info(f"📊 Final stats: {final_stats}")
            
            return translated_bible
            
        except Exception as e:
            logger.error(f"❌ Full Bible translation failed: {e}")
            raise


def main():
    """Test the full Bible translator with a small subset."""
    import sys
    sys.path.insert(0, 'src')
    
    # Test with just Genesis
    translator = FullBibleTranslator(intensity="nuclear")
    
    try:
        result = translator.translate_full_bible(
            persona="joe_rogan",
            books_to_translate=["Genesis"]  # Just Genesis for testing
        )
        
        print(f"✅ Translation completed! Output saved to data/processed/translations/joe_rogan_full_bible.json")
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")


if __name__ == "__main__":
    main() 