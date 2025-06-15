#!/usr/bin/env python3
"""
KJV Bible Preprocessor

Downloads the King James Version from a reliable source and restructures it
into a nested dictionary format for easier processing by the AI translator.
"""

import json
import requests
import sys
from typing import Dict, Any
from pathlib import Path


def download_kjv_data() -> Dict[str, Any]:
    """
    Download KJV data from a reliable source or use local JSON file.
    
    Returns:
        Dict containing the raw KJV data
    """
    # Check for local JSON files first
    local_files = ["BBE.json", "kjv.json", "bible.json"]
    
    for local_file in local_files:
        if Path(local_file).exists():
            print(f"📖 Using local file: {local_file}")
            try:
                with open(local_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Successfully loaded {len(data)} entries from {local_file}")
                return data
            except Exception as e:
                print(f"❌ Error reading {local_file}: {e}")
                continue
    
    # Try multiple sources for KJV data if no local files found
    sources = [
        "https://api.bibliaapi.com/v1/bibles/kjv/verses.json",
        "https://raw.githubusercontent.com/bibleapi/bibleapi-bibles-json/master/kjv.json",
        "https://api.scripture.api.bible/v1/bibles/de4e12af7f28f599-02/verses"
    ]
    
    print("📥 Attempting to download KJV data...")
    
    for i, url in enumerate(sources, 1):
        try:
            print(f"   Trying source {i}/{len(sources)}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check if this looks like Bible data
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ Successfully downloaded from source {i}")
                return data
            elif isinstance(data, dict) and any(key in data for key in ['verses', 'data', 'books']):
                print(f"✅ Successfully downloaded from source {i}")
                return data
                
        except requests.RequestException as e:
            print(f"   ❌ Source {i} failed: {e}")
            continue
    
    # If all sources fail, create sample data for testing
    print("⚠️  All online sources failed, creating sample KJV data for testing...")
    return create_sample_kjv_data()


def create_sample_kjv_data() -> Dict[str, Any]:
    """
    Create sample KJV data for testing when online sources are unavailable.
    
    Returns:
        Sample KJV data in the expected format
    """
    sample_data = [
        {"book": "Genesis", "chapter": 1, "verse": 1, "text": "In the beginning God created the heaven and the earth."},
        {"book": "Genesis", "chapter": 1, "verse": 2, "text": "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters."},
        {"book": "Genesis", "chapter": 1, "verse": 3, "text": "And God said, Let there be light: and there was light."},
        {"book": "Genesis", "chapter": 1, "verse": 4, "text": "And God saw the light, that it was good: and God divided the light from the darkness."},
        {"book": "Genesis", "chapter": 1, "verse": 5, "text": "And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day."},
        {"book": "Genesis", "chapter": 2, "verse": 1, "text": "Thus the heavens and the earth were finished, and all the host of them."},
        {"book": "Genesis", "chapter": 2, "verse": 2, "text": "And on the seventh day God ended his work which he had made; and he rested on the seventh day from all his work which he had made."},
        {"book": "Exodus", "chapter": 1, "verse": 1, "text": "Now these are the names of the children of Israel, which came into Egypt; every man and his household came with Jacob."},
        {"book": "Exodus", "chapter": 1, "verse": 2, "text": "Reuben, Simeon, Levi, and Judah,"},
        {"book": "Matthew", "chapter": 1, "verse": 1, "text": "The book of the generation of Jesus Christ, the son of David, the son of Abraham."},
        {"book": "Matthew", "chapter": 1, "verse": 2, "text": "Abraham begat Isaac; and Isaac begat Jacob; and Jacob begat Judas and his brethren;"},
        {"book": "John", "chapter": 1, "verse": 1, "text": "In the beginning was the Word, and the Word was with God, and the Word was God."},
        {"book": "John", "chapter": 1, "verse": 2, "text": "The same was in the beginning with God."},
        {"book": "John", "chapter": 1, "verse": 3, "text": "All things were made by him; and without him was not any thing made that was made."},
        {"book": "Revelation", "chapter": 1, "verse": 1, "text": "The Revelation of Jesus Christ, which God gave unto him, to shew unto his servants things which must shortly come to pass; and he sent and signified it by his angel unto his servant John:"},
        {"book": "Revelation", "chapter": 1, "verse": 2, "text": "Who bare record of the word of God, and of the testimony of Jesus Christ, and of all things that he saw."}
    ]
    
    print(f"📝 Created sample data with {len(sample_data)} verses")
    return sample_data


def restructure_kjv_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Restructure raw KJV data into nested dictionary format.
    
    Args:
        raw_data: Raw KJV data from source
        
    Returns:
        Restructured data in format: {book: {chapter: {verse: text}}}
    """
    print("🔄 Restructuring KJV data...")
    
    restructured = {}
    
    # Handle different data formats
    if isinstance(raw_data, list):
        # Direct list of verses (original format)
        for entry in raw_data:
            if isinstance(entry, dict):
                book = entry.get('book', '').strip()
                chapter = str(entry.get('chapter', ''))
                verse = str(entry.get('verse', ''))
                text = entry.get('text', '').strip()
                
                if not all([book, chapter, verse, text]):
                    continue
                    
                # Initialize book if it doesn't exist
                if book not in restructured:
                    restructured[book] = {}
                    
                # Initialize chapter if it doesn't exist
                if chapter not in restructured[book]:
                    restructured[book][chapter] = {}
                    
                # Add verse
                restructured[book][chapter][verse] = text
    
    elif isinstance(raw_data, dict):
        # Handle nested dictionary format
        if 'verses' in raw_data:
            # API format with verses array
            for entry in raw_data['verses']:
                book = entry.get('book', '').strip()
                chapter = str(entry.get('chapter', ''))
                verse = str(entry.get('verse', ''))
                text = entry.get('text', '').strip()
                
                if not all([book, chapter, verse, text]):
                    continue
                    
                if book not in restructured:
                    restructured[book] = {}
                if chapter not in restructured[book]:
                    restructured[book][chapter] = {}
                restructured[book][chapter][verse] = text
        
        elif 'books' in raw_data:
            # BBE format with books/chapters/verses structure
            print(f"📚 Processing {len(raw_data['books'])} books in BBE format...")
            
            for book_data in raw_data['books']:
                book_name = book_data.get('name', '').strip()
                if not book_name:
                    continue
                
                print(f"   📖 Processing book: {book_name}")
                restructured[book_name] = {}
                
                chapters = book_data.get('chapters', [])
                for chapter_data in chapters:
                    chapter_num = str(chapter_data.get('chapter', ''))
                    if not chapter_num:
                        continue
                    
                    restructured[book_name][chapter_num] = {}
                    
                    verses = chapter_data.get('verses', [])
                    for verse_data in verses:
                        verse_num = str(verse_data.get('verse', ''))
                        verse_text = verse_data.get('text', '').strip()
                        
                        if verse_num and verse_text:
                            restructured[book_name][chapter_num][verse_num] = verse_text
    
    return restructured


def save_restructured_data(data: Dict[str, Any], output_file: str = "tests/fixtures/kjv_bible.json") -> None:
    """
    Save restructured data to JSON file.
    
    Args:
        data: Restructured KJV data
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
        data: Restructured KJV data
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
    
    # Check for common books
    expected_books = ["Genesis", "Exodus", "Matthew", "John", "Revelation"]
    missing_books = [book for book in expected_books if book not in data]
    
    if missing_books:
        print(f"⚠️  Warning: Missing expected books: {missing_books}")
    else:
        print("✅ All expected books found")


def main():
    """Main function to orchestrate the KJV preprocessing."""
    print("🎭 HOLY REMIX - KJV Preprocessor")
    print("=" * 40)
    
    # Download raw data
    raw_data = download_kjv_data()
    print(f"📥 Downloaded {len(raw_data)} entries")
    
    # Restructure data
    restructured_data = restructure_kjv_data(raw_data)
    
    # Validate data
    validate_restructured_data(restructured_data)
    
    # Save to file
    save_restructured_data(restructured_data)
    
    print("\n🎉 KJV preprocessing complete!")
    print("�� Output file: tests/fixtures/kjv_bible.json")
    print("🚀 Ready for AI translation!")


if __name__ == "__main__":
    main() 