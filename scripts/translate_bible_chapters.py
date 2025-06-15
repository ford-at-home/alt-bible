#!/usr/bin/env python3
"""
Bible Chapter Translation Orchestrator

Intelligently translates Bible chapters using the hybrid approach:
- Chapter-by-chapter when token limits allow
- Verse-by-verse fallback for long chapters
- Cost tracking and resume capability
"""

import json
import time
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from translators.chapter_translator import ChapterTranslator, VerseByVerseTranslator
from storage.dynamodb_loader import DynamoDBLoader
from utils.cost_calculator import CostCalculator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BibleChapterOrchestrator:
    """Orchestrates the translation of Bible chapters with intelligent token management."""
    
    def __init__(self, model_id: str = "us.deepseek.r1-v1:0", max_tokens: int = 4000):
        """
        Initialize the orchestrator.
        
        Args:
            model_id: Bedrock model ID to use
            max_tokens: Maximum safe tokens for the model
        """
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.chapter_translator = ChapterTranslator(model_id, max_tokens)
        self.verse_translator = VerseByVerseTranslator(model_id)
        self.dynamodb_loader = DynamoDBLoader()
        self.cost_calculator = CostCalculator()
        
        # Translation statistics
        self.stats = {
            'chapters_translated': 0,
            'verses_translated': 0,
            'chapters_failed': 0,
            'verses_failed': 0,
            'total_cost': 0.0,
            'chapter_translations': 0,
            'verse_translations': 0
        }
    
    def load_bible_data(self, bible_file: str) -> Dict[str, Any]:
        """Load Bible data from JSON file."""
        try:
            with open(bible_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error loading Bible data: {e}")
            raise
    
    def get_chapter_list(self, bible_data: Dict[str, Any], book_filter: Optional[str] = None, 
                        chapter_filter: Optional[str] = None) -> List[tuple]:
        """
        Get list of chapters to translate.
        
        Args:
            bible_data: Loaded Bible data
            book_filter: Optional book name filter
            chapter_filter: Optional chapter number filter
            
        Returns:
            List of (book, chapter) tuples
        """
        chapters = []
        
        for book in bible_data:
            if book_filter and book != book_filter:
                continue
                
            for chapter in bible_data[book]:
                if chapter_filter and chapter != chapter_filter:
                    continue
                    
                chapters.append((book, chapter))
        
        return sorted(chapters)
    
    def estimate_translation_cost(self, bible_data: Dict[str, Any], chapters: List[tuple], persona: str) -> Dict[str, Any]:
        """
        Estimate the cost of translating the specified chapters.
        
        Args:
            bible_data: Loaded Bible data
            chapters: List of (book, chapter) tuples
            persona: Persona name for translation
            
        Returns:
            Cost estimation details
        """
        total_input_tokens = 0
        total_output_tokens = 0
        chapter_methods = {}
        
        for book, chapter in chapters:
            verses = bible_data[book][chapter]
            
            if self.chapter_translator.should_translate_chapter(book, chapter, verses, persona):
                # Chapter translation
                input_tokens, output_tokens = self.chapter_translator.estimate_chapter_tokens(book, chapter, verses, persona)
                chapter_methods[(book, chapter)] = 'chapter'
            else:
                # Verse-by-verse translation
                input_tokens = 0
                output_tokens = 0
                for verse_num, verse_text in verses.items():
                    # Rough estimation for verse prompts
                    verse_prompt = f"You are {persona}. Rewrite this single verse of the Bible in your voice:\n\n{book} {chapter}:{verse_num} - {verse_text}\n\nReturn only the translated verse:"
                    input_tokens += self.chapter_translator.count_tokens(verse_prompt)
                    output_tokens += self.chapter_translator.count_tokens(verse_text) * 1.2  # Estimate 20% longer
                chapter_methods[(book, chapter)] = 'verse'
            
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        
        # Calculate cost
        cost = self.cost_calculator.calculate_cost(total_input_tokens, total_output_tokens, self.model_id)
        
        return {
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'estimated_cost': cost,
            'chapter_methods': chapter_methods,
            'num_chapters': len(chapters)
        }
    
    def translate_chapters(self, bible_data: Dict[str, Any], chapters: List[tuple], persona: str, 
                          checkpoint_file: Optional[str] = None, batch_size: int = 10) -> Dict[str, Any]:
        """
        Translate the specified chapters.
        
        Args:
            bible_data: Loaded Bible data
            chapters: List of (book, chapter) tuples
            persona: Persona name for translation
            checkpoint_file: Optional checkpoint file for resume
            batch_size: Number of chapters to process before saving checkpoint
            
        Returns:
            Translation statistics
        """
        # Load checkpoint if provided
        completed_chapters = set()
        if checkpoint_file and Path(checkpoint_file).exists():
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
                completed_chapters = set(checkpoint_data.get('completed_chapters', []))
                self.stats = checkpoint_data.get('stats', self.stats)
                logger.info(f"📋 Loaded checkpoint: {len(completed_chapters)} chapters completed")
        
        # Filter out completed chapters
        remaining_chapters = [(book, chapter) for book, chapter in chapters 
                             if (book, chapter) not in completed_chapters]
        
        logger.info(f"🎯 Starting translation of {len(remaining_chapters)} chapters as {persona}")
        
        for i, (book, chapter) in enumerate(remaining_chapters):
            try:
                logger.info(f"📖 Processing {book} {chapter} ({i+1}/{len(remaining_chapters)})")
                
                verses = bible_data[book][chapter]
                
                # Determine translation method
                if self.chapter_translator.should_translate_chapter(book, chapter, verses, persona):
                    # Chapter translation
                    result = self.chapter_translator.translate_chapter(book, chapter, verses, persona)
                    if result:
                        dynamodb_items = self.chapter_translator.save_chapter_translation(book, chapter, result, persona)
                        self.stats['chapters_translated'] += 1
                        self.stats['verses_translated'] += len(result)
                        self.stats['chapter_translations'] += 1
                        
                        # Save to DynamoDB
                        self.dynamodb_loader.batch_write_items(dynamodb_items)
                        logger.info(f"✅ Chapter {book} {chapter} translated successfully")
                    else:
                        self.stats['chapters_failed'] += 1
                        logger.error(f"❌ Chapter {book} {chapter} translation failed")
                        continue
                else:
                    # Verse-by-verse translation
                    logger.info(f"🔄 Using verse-by-verse translation for {book} {chapter}")
                    results = {}
                    for verse_num, verse_text in verses.items():
                        translated = self.verse_translator.translate_verse(book, chapter, verse_num, verse_text, persona)
                        if translated:
                            results[verse_num] = translated
                            self.stats['verses_translated'] += 1
                        else:
                            self.stats['verses_failed'] += 1
                        
                        time.sleep(0.1)  # Small delay to avoid rate limiting
                    
                    if results:
                        dynamodb_items = self.chapter_translator.save_chapter_translation(book, chapter, results, persona)
                        self.stats['chapters_translated'] += 1
                        self.stats['verse_translations'] += 1
                        
                        # Save to DynamoDB
                        self.dynamodb_loader.batch_write_items(dynamodb_items)
                        logger.info(f"✅ Verse-by-verse translation complete for {book} {chapter}")
                    else:
                        self.stats['chapters_failed'] += 1
                        logger.error(f"❌ Verse-by-verse translation failed for {book} {chapter}")
                        continue
                
                # Mark as completed
                completed_chapters.add((book, chapter))
                
                # Save checkpoint every batch_size chapters
                if (i + 1) % batch_size == 0 and checkpoint_file:
                    self._save_checkpoint(checkpoint_file, completed_chapters)
                    logger.info(f"💾 Checkpoint saved after {i + 1} chapters")
                
                # Small delay between chapters
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error processing {book} {chapter}: {e}")
                self.stats['chapters_failed'] += 1
                continue
        
        # Final checkpoint save
        if checkpoint_file:
            self._save_checkpoint(checkpoint_file, completed_chapters)
        
        return self.stats
    
    def _save_checkpoint(self, checkpoint_file: str, completed_chapters: set) -> None:
        """Save checkpoint data."""
        checkpoint_data = {
            'completed_chapters': list(completed_chapters),
            'stats': self.stats,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def print_summary(self, stats: Dict[str, Any], cost_estimate: Dict[str, Any]) -> None:
        """Print translation summary."""
        print("\n" + "="*60)
        print("📊 TRANSLATION SUMMARY")
        print("="*60)
        print(f"✅ Chapters translated: {stats['chapters_translated']}")
        print(f"✅ Verses translated: {stats['verses_translated']}")
        print(f"❌ Chapters failed: {stats['chapters_failed']}")
        print(f"❌ Verses failed: {stats['verses_failed']}")
        print(f"📝 Chapter translations: {stats['chapter_translations']}")
        print(f"📝 Verse translations: {stats['verse_translations']}")
        print(f"💰 Estimated cost: ${cost_estimate['estimated_cost']:.2f}")
        print(f"🔢 Total input tokens: {cost_estimate['total_input_tokens']:,}")
        print(f"🔢 Total output tokens: {cost_estimate['total_output_tokens']:,}")
        print("="*60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Bible Chapter Translation Orchestrator")
    parser.add_argument("--bible-file", default="data/processed/kjv_bible.json", help="Bible JSON file")
    parser.add_argument("--persona", required=True, help="Persona name for translation")
    parser.add_argument("--book", help="Specific book to translate")
    parser.add_argument("--chapter", help="Specific chapter to translate")
    parser.add_argument("--model", default="us.deepseek.r1-v1:0", help="Bedrock model ID")
    parser.add_argument("--max-tokens", type=int, default=4000, help="Maximum tokens for model")
    parser.add_argument("--checkpoint", help="Checkpoint file for resume capability")
    parser.add_argument("--batch-size", type=int, default=10, help="Chapters per checkpoint")
    parser.add_argument("--estimate-only", action="store_true", help="Only estimate cost, don't translate")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = BibleChapterOrchestrator(args.model, args.max_tokens)
    
    try:
        # Load Bible data
        logger.info(f"📚 Loading Bible data from {args.bible_file}")
        bible_data = orchestrator.load_bible_data(args.bible_file)
        
        # Get chapter list
        chapters = orchestrator.get_chapter_list(bible_data, args.book, args.chapter)
        logger.info(f"📖 Found {len(chapters)} chapters to process")
        
        # Estimate cost
        logger.info("💰 Estimating translation cost...")
        cost_estimate = orchestrator.estimate_translation_cost(bible_data, chapters, args.persona)
        
        print(f"\n💡 COST ESTIMATION")
        print(f"📊 Chapters to translate: {cost_estimate['num_chapters']}")
        print(f"💰 Estimated cost: ${cost_estimate['estimated_cost']:.2f}")
        print(f"🔢 Input tokens: {cost_estimate['total_input_tokens']:,}")
        print(f"🔢 Output tokens: {cost_estimate['total_output_tokens']:,}")
        
        # Show translation methods
        chapter_methods = cost_estimate['chapter_methods']
        chapter_count = sum(1 for method in chapter_methods.values() if method == 'chapter')
        verse_count = sum(1 for method in chapter_methods.values() if method == 'verse')
        print(f"📝 Chapter translations: {chapter_count}")
        print(f"📝 Verse translations: {verse_count}")
        
        if args.estimate_only:
            return
        
        # Confirm before proceeding
        response = input(f"\n🤔 Proceed with translation? (y/N): ")
        if response.lower() != 'y':
            print("❌ Translation cancelled")
            return
        
        # Start translation
        logger.info("🚀 Starting translation...")
        stats = orchestrator.translate_chapters(bible_data, chapters, args.persona, args.checkpoint, args.batch_size)
        
        # Print summary
        orchestrator.print_summary(stats, cost_estimate)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Translation interrupted by user")
        if args.checkpoint:
            logger.info(f"💾 Progress saved to {args.checkpoint}")
    except Exception as e:
        logger.error(f"❌ Translation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 