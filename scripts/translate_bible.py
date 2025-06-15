#!/usr/bin/env python3
"""
Main Bible Translation Orchestrator

Coordinates the entire process of downloading KJV data, preprocessing it,
and translating it into different personas using AI.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import our modules from the new package structure
from preprocessors.json_preprocessor import download_kjv_data, restructure_kjv_data, save_restructured_data, validate_restructured_data
from translators.bedrock_translator import BedrockTranslator, TranslationManager
from translators.chapter_translator import ChapterTranslator
from utils.persona_loader import list_personas, get_persona


def load_kjv_data(kjv_file: str = "data/processed/kjv_bible.json") -> Dict[str, Any]:
    """
    Load KJV data from file or download if not available.
    
    Args:
        kjv_file: Path to KJV Bible JSON file
        
    Returns:
        Restructured KJV data
    """
    if Path(kjv_file).exists():
        print(f"📖 Loading existing KJV data from {kjv_file}")
        with open(kjv_file, 'r') as f:
            return json.load(f)
    else:
        print(f"📥 KJV file not found, downloading and processing...")
        raw_data = download_kjv_data()
        restructured_data = restructure_kjv_data(raw_data)
        validate_restructured_data(restructured_data)
        save_restructured_data(restructured_data, kjv_file)
        return restructured_data


def get_persona_prompts() -> Dict[str, str]:
    """
    Get predefined persona descriptions for consistent translations.
    
    Returns:
        Dictionary of persona names to their descriptions
    """
    return {
        "samuel_l_jackson": "Samuel L. Jackson - Use his distinctive voice with frequent use of 'motherf*cker', strong emphasis, and dramatic delivery",
        "joe_rogan": "Joe Rogan - Use his conversational, curious, and often philosophical style with frequent 'man' and 'dude'",
        "cardi_b": "Cardi B - Use her energetic, expressive style with modern slang, 'okurrr', and bold personality",
        "ram_dass": "Ram Dass - Use his spiritual, contemplative style with references to consciousness, love, and mindfulness",
        "hunter_s_thompson": "Hunter S. Thompson - Use his gonzo journalism style with vivid imagery, paranoia, and counterculture references",
        "maya_angelou": "Maya Angelou - Use her poetic, powerful, and inspirational voice with rich metaphors and spiritual depth"
    }


def translate_single_persona(kjv_data: Dict[str, Any], persona: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Translate the entire Bible for a single persona.
    
    Args:
        kjv_data: Restructured KJV data
        persona: Persona name for translation
        dry_run: If True, only show what would be translated
        
    Returns:
        Translated Bible data
    """
    print(f"\n🎭 Starting translation for persona: {persona}")
    print("=" * 60)
    
    # Initialize translator and manager
    translator = BedrockTranslator()
    manager = TranslationManager(translator)
    
    # Perform translation
    result = manager.translate_bible(kjv_data, persona, dry_run)
    
    if not dry_run:
        # Save results
        output_file = f"data/processed/translated_bible_{persona}.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Translation saved to {output_file}")
        
        # Generate summary
        total_books = len(result)
        total_chapters = sum(len(chapters) for chapters in result.values())
        total_verses = sum(
            len(verses) 
            for chapters in result.values() 
            for verses in chapters.values()
        )
        
        print(f"\n📊 Translation Summary for {persona}:")
        print(f"   Books: {total_books}")
        print(f"   Chapters: {total_chapters}")
        print(f"   Verses: {total_verses}")
    
    return result


def list_available_personas():
    """List all available personas with descriptions."""
    print("🎭 Available Personas:")
    print("=" * 60)
    
    personas = list_personas()
    for persona in personas:
        print(f"📝 {persona['key']}")
        print(f"   Name: {persona['display_name']}")
        print(f"   Description: {persona['description']}")
        print()


def create_persona_prompt(persona: str, book: str, chapter: str, verses: dict) -> str:
    """Create a prompt for a specific persona and chapter."""
    translator = ChapterTranslator()
    return translator.create_chapter_prompt(book, chapter, verses, persona)


def main():
    """Main function to orchestrate the Bible translation process."""
    parser = argparse.ArgumentParser(
        description="🎭 HOLY REMIX - AI-Powered Scripture Translation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate entire Bible for Samuel L. Jackson
  python scripts/translate_bible.py --persona samuel_l_jackson
  
  # Dry run to see what would be translated
  python scripts/translate_bible.py --persona joe_rogan --dry-run
  
  # Translate specific book and chapter
  python scripts/translate_bible.py --persona cardi_b --book Genesis --chapter 1
  
  # List available personas
  python scripts/translate_bible.py --list-personas
        """
    )
    
    parser.add_argument("--persona", help="Persona name for translation")
    parser.add_argument("--book", help="Specific book to translate (optional)")
    parser.add_argument("--chapter", help="Specific chapter to translate (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be translated without actually translating")
    parser.add_argument("--kjv-file", default="data/processed/kjv_bible.json", help="Path to KJV Bible JSON file")
    parser.add_argument("--list-personas", action="store_true", help="List available personas")
    parser.add_argument("--all-personas", action="store_true", help="Translate for all available personas")
    
    args = parser.parse_args()
    
    if args.list_personas:
        list_available_personas()
        return
    
    if not args.persona and not args.all_personas:
        print("❌ Error: Please specify --persona or --all-personas")
        parser.print_help()
        sys.exit(1)
    
    # Validate persona exists
    persona_info = get_persona(args.persona)
    if not persona_info:
        print(f"❌ Error: Unknown persona '{args.persona}'")
        print("Use --list-personas to see available options")
        sys.exit(1)
    
    # Load KJV data
    try:
        kjv_data = load_kjv_data(args.kjv_file)
    except Exception as e:
        print(f"❌ Error loading KJV data: {e}")
        sys.exit(1)
    
    if args.all_personas:
        # Translate for all personas
        print("🎭 Starting translation for ALL personas")
        print("=" * 50)
        
        results = {}
        for persona in get_persona_prompts().keys():
            try:
                result = translate_single_persona(kjv_data, persona, args.dry_run)
                results[persona] = result
            except Exception as e:
                print(f"❌ Error translating for {persona}: {e}")
                continue
        
        if not args.dry_run:
            print(f"\n🎉 Translation complete for {len(results)} personas!")
            print("📁 Output files:")
            for persona in results.keys():
                print(f"   • data/processed/translated_bible_{persona}.json")
    
    elif args.persona:
        # Handle specific book/chapter translation
        if args.book and args.chapter:
            if args.book not in kjv_data:
                print(f"❌ Error: Book '{args.book}' not found in Bible data")
                sys.exit(1)
            
            if args.chapter not in kjv_data[args.book]:
                print(f"❌ Error: Chapter '{args.chapter}' not found in {args.book}")
                sys.exit(1)
            
            verses = kjv_data[args.book][args.chapter]
            
            if args.dry_run:
                print(f"🎭 Creating prompt for {args.persona} ({persona_info['display_name']})")
                print(f"📖 Translating {args.book} {args.chapter}")
                print("=" * 60)
                
                prompt = create_persona_prompt(args.persona, args.book, args.chapter, verses)
                print(prompt)
            else:
                print(f"🎭 Translating {args.book} {args.chapter} as {persona_info['display_name']}")
                print(f"📝 Style: {persona_info['style']}")
                print("=" * 60)
                
                translator = ChapterTranslator()
                
                # Check if we should translate as chapter or verse-by-verse
                if translator.should_translate_chapter(args.book, args.chapter, verses, args.persona):
                    result = translator.translate_chapter(args.book, args.chapter, verses, args.persona)
                    if result:
                        translator.save_chapter_translation(args.book, args.chapter, result, args.persona)
                        print(f"✅ Chapter translation complete: {len(result)} verses")
                    else:
                        print("❌ Chapter translation failed")
                else:
                    print("🔄 Using verse-by-verse translation...")
                # Implement verse-by-verse translation here if needed
                print("Verse-by-verse translation not yet implemented in this script")
        else:
            # Translate entire Bible
            translate_single_persona(kjv_data, args.persona, args.dry_run)


if __name__ == "__main__":
    main() 