#!/usr/bin/env python3
"""
Prompt templates for strict JSON output format
"""

STRICT_JSON_PROMPT_TEMPLATE = """You are an AI assistant generating stylized Bible chapter translations using a given persona.

This output will be parsed and inserted into a database. Any deviation from the required structure will break downstream ingestion.

You must:
1. Preserve all verse numbers from the original chapter.
2. Return a single JSON object in the exact format below.
3. Avoid wrapping the output in markdown, code blocks, or any additional commentary.

The required JSON format is:

{{
  "book": "{book}",
  "chapter": {chapter},
  "verses": {{
    "1": "Stylized verse 1 in the requested persona voice...",
    "2": "Stylized verse 2 in the requested persona voice...",
    "...": "...",
    "{max_verse}": "Last verse in this chapter."
  }}
}}

Do not add any extra keys, omit any verse numbers, or generate prose outside the `verses` object. Verse numbers must remain string keys.

Now return the stylized translation of **{book} Chapter {chapter}** in the voice of **{persona}**."""

def get_strict_json_prompt(book: str, chapter: str, persona: str, max_verse: int) -> str:
    """
    Generate the strict JSON prompt for database-compatible translations.
    
    Args:
        book: Bible book name
        chapter: Chapter number
        persona: Persona name for translation
        max_verse: Maximum verse number in the chapter
        
    Returns:
        Formatted prompt string
    """
    return STRICT_JSON_PROMPT_TEMPLATE.format(
        book=book,
        chapter=chapter,
        persona=persona,
        max_verse=max_verse
    ) 