#!/usr/bin/env python3
"""
Text Bible Preprocessor

Processes plain text Bible files with verse markers like [1:1] and converts them
to the nested dictionary format needed for AI translation and DynamoDB storage.
"""

import json
import re
import sys
from typing import Dict, Any
from pathlib import Path


def parse_text_bible(file_path: str) -> Dict[str, Any]:
    """
    Parse a plain text Bible file with verse markers like [1:1].
    
    Args:
        file_path: Path to the text Bible file
        
    Returns:
        Restructured data in format: {book: {chapter: {verse: text}}}
    """
    print(f"📖 Parsing text Bible file: {file_path}")
    
    restructured = {}
    current_book = None
    current_chapter = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)
    
    # Split content into lines
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a book header (starts with ### or similar)
        if line.startswith('###') or line.startswith('##'):
            current_book = line.replace('#', '').strip()
            print(f"📚 Processing book: {current_book}")
            restructured[current_book] = {}
            current_chapter = None
            continue
        
        # Check if this is a verse with marker like [1:1]
        verse_match = re.match(r'\[(\d+):(\d+)\]\s*(.+)', line)
        if verse_match:
            chapter_num = verse_match.group(1)
            verse_num = verse_match.group(2)
            verse_text = verse_match.group(3).strip()
            
            # If we don't have a current book, try to infer from context
            if not current_book:
                current_book = "Unknown"
                restructured[current_book] = {}
            
            # Initialize chapter if it doesn't exist
            if chapter_num not in restructured[current_book]:
                restructured[current_book][chapter_num] = {}
                if current_chapter != chapter_num:
                    print(f"   📖 Chapter {chapter_num}")
                    current_chapter = chapter_num
            
            # Add verse
            restructured[current_book][chapter_num][verse_num] = verse_text
        
        # Handle other formats - look for patterns like "1:1" or "1.1"
        else:
            # Try different verse patterns
            patterns = [
                r'(\d+):(\d+)\s*(.+)',  # 1:1 format
                r'(\d+)\.(\d+)\s*(.+)',  # 1.1 format
                r'Verse\s+(\d+):(\d+)\s*(.+)',  # Verse 1:1 format
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    chapter_num = match.group(1)
                    verse_num = match.group(2)
                    verse_text = match.group(3).strip()
                    
                    if not current_book:
                        current_book = "Unknown"
                        restructured[current_book] = {}
                    
                    if chapter_num not in restructured[current_book]:
                        restructured[current_book][chapter_num] = {}
                        if current_chapter != chapter_num:
                            print(f"   📖 Chapter {chapter_num}")
                            current_chapter = chapter_num
                    
                    restructured[current_book][chapter_num][verse_num] = verse_text
                    break
    
    return restructured


def save_restructured_data(data: Dict[str, Any], output_file: str = "kjv_bible.json") -> None:
    """
    Save restructured data to JSON file.
    
    Args:
        data: Restructured Bible data
        output_file: Output file path
    """
    print(f"💾 Saving restructured data to {output_file}...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully saved {output_file}")
    except IOError as e:
        print(f"❌ Error saving file: {e}")
        sys.exit(1)


def validate_restructured_data(data: Dict[str, Any]) -> None:
    """
    Validate the restructured data for completeness.
    
    Args:
        data: Restructured Bible data
    """
    print("🔍 Validating restructured data...")
    
    total_books = len(data)
    total_chapters = sum(len(chapters) for chapters in data.values())
    total_verses = sum(
        len(verses) 
        for chapters in data.values() 
        for verses in chapters.values()
    )
    
    print(f"📊 Validation Results:")
    print(f"   Books: {total_books}")
    print(f"   Chapters: {total_chapters}")
    print(f"   Verses: {total_verses}")
    
    # Show sample of what was parsed
    if data:
        first_book = list(data.keys())[0]
        first_chapter = list(data[first_book].keys())[0]
        first_verse = list(data[first_book][first_chapter].keys())[0]
        
        print(f"📝 Sample verse ({first_book} {first_chapter}:{first_verse}):")
        print(f"   {data[first_book][first_chapter][first_verse]}")


def main():
    """Main function to orchestrate the text Bible preprocessing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Text Bible Preprocessor")
    parser.add_argument("input_file", help="Path to the text Bible file")
    parser.add_argument("--output", default="kjv_bible.json", help="Output JSON file path")
    
    args = parser.parse_args()
    
    print("🎭 Alt Bible - Text Bible Preprocessor")
    print("=" * 40)
    
    # Parse the text Bible file
    restructured_data = parse_text_bible(args.input_file)
    
    # Validate data
    validate_restructured_data(restructured_data)
    
    # Save to file
    save_restructured_data(restructured_data, args.output)
    
    print("\n🎉 Text Bible preprocessing complete!")
    print(f"📁 Output file: {args.output}")
    print("🚀 Ready for AI translation!")


if __name__ == "__main__":
    main() 