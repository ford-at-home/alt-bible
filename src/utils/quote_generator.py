#!/usr/bin/env python3
"""
Quote Generator for Bible Translation Costs

Estimates the cost of translating Bible chapters into different personas
using Amazon Bedrock, providing detailed quotes before processing.
"""

import json
import sys
from typing import Dict, Any, List, Tuple
from pathlib import Path
import tiktoken


class CostCalculator:
    """Calculates costs for AI-powered Bible translations."""
    
    # Bedrock DeepSeek pricing (as of 2024, adjust as needed)
    DEEPSEEK_PRICING = {
        "input": 0.00014,   # $0.00014 per 1K input tokens
        "output": 0.00056,  # $0.00056 per 1K output tokens
    }
    
    # Estimated token ratios for different personas (output/input ratio)
    PERSONA_TOKEN_RATIOS = {
        "samuel_l_jackson": 1.2,    # More verbose, dramatic
        "joe_rogan": 1.1,           # Conversational, explanatory
        "cardi_b": 1.3,             # Very expressive, longer
        "ram_dass": 1.0,            # Spiritual, concise
        "hunter_s_thompson": 1.4,   # Very verbose, descriptive
        "maya_angelou": 1.2,        # Poetic, rich language
    }
    
    def __init__(self):
        """Initialize the cost calculator."""
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        except ImportError:
            print("⚠️  tiktoken not available, using rough estimation")
            self.encoder = None
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken or rough estimation.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        if self.encoder:
            return len(self.encoder.encode(text))
        else:
            # Rough estimation: ~4 characters per token
            return len(text) // 4
    
    def estimate_chapter_cost(self, book: str, chapter: str, verses_dict: Dict[str, str], persona: str) -> Dict[str, Any]:
        """
        Estimate cost for translating a single chapter.
        
        Args:
            book: Bible book name
            chapter: Chapter number
            verses_dict: Dictionary of verse numbers to verse text
            persona: Persona name for translation
            
        Returns:
            Dictionary with cost breakdown
        """
        # Build input text (verses only)
        verses_text = "\n".join([
            f"{verse_num}. {verse_text}"
            for verse_num, verse_text in sorted(verses_dict.items(), key=lambda x: int(x[0]))
        ])
        
        # Create prompt template
        prompt_template = f"""You are {persona}. Rewrite the following chapter of the Bible in your voice. Keep the number of verses the same. Format each verse like this:

1. [your rewrite]
2. ...
3. ...

Do not skip verses. Do not add extra commentary. Return only the numbered verses.

Chapter: {book} {chapter}

{verses_text}"""
        
        # Count input tokens
        input_tokens = self.count_tokens(prompt_template)
        
        # Estimate output tokens based on persona ratio
        persona_ratio = self.PERSONA_TOKEN_RATIOS.get(persona, 1.0)
        estimated_output_tokens = int(input_tokens * persona_ratio)
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * self.DEEPSEEK_PRICING["input"]
        output_cost = (estimated_output_tokens / 1000) * self.DEEPSEEK_PRICING["output"]
        total_cost = input_cost + output_cost
        
        return {
            "book": book,
            "chapter": chapter,
            "persona": persona,
            "input_tokens": input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "verse_count": len(verses_dict)
        }
    
    def estimate_bible_cost(self, kjv_data: Dict[str, Any], persona: str) -> Dict[str, Any]:
        """
        Estimate cost for translating the entire Bible for a persona.
        
        Args:
            kjv_data: Restructured KJV data
            persona: Persona name for translation
            
        Returns:
            Dictionary with total cost breakdown
        """
        print(f"🧮 Calculating cost estimate for {persona}...")
        
        total_cost = 0
        total_input_tokens = 0
        total_output_tokens = 0
        total_chapters = 0
        total_verses = 0
        chapter_breakdown = []
        
        for book, chapters in kjv_data.items():
            for chapter, verses in chapters.items():
                chapter_cost = self.estimate_chapter_cost(book, chapter, verses, persona)
                
                total_cost += chapter_cost["total_cost"]
                total_input_tokens += chapter_cost["input_tokens"]
                total_output_tokens += chapter_cost["estimated_output_tokens"]
                total_chapters += 1
                total_verses += chapter_cost["verse_count"]
                
                chapter_breakdown.append(chapter_cost)
        
        return {
            "persona": persona,
            "total_cost": total_cost,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_chapters": total_chapters,
            "total_verses": total_verses,
            "chapter_breakdown": chapter_breakdown,
            "cost_per_chapter": total_cost / total_chapters if total_chapters > 0 else 0,
            "cost_per_verse": total_cost / total_verses if total_verses > 0 else 0
        }
    
    def generate_quote(self, estimate: Dict[str, Any], markup_percentage: float = 20.0) -> Dict[str, Any]:
        """
        Generate a formal quote with markup.
        
        Args:
            estimate: Cost estimate from estimate_bible_cost
            markup_percentage: Percentage markup to add
            
        Returns:
            Formal quote with pricing details
        """
        base_cost = estimate["total_cost"]
        markup_amount = base_cost * (markup_percentage / 100)
        final_price = base_cost + markup_amount
        
        return {
            "quote_id": f"quote_{estimate['persona']}_{int(base_cost * 1000)}",
            "persona": estimate["persona"],
            "base_cost": base_cost,
            "markup_percentage": markup_percentage,
            "markup_amount": markup_amount,
            "final_price": final_price,
            "total_chapters": estimate["total_chapters"],
            "total_verses": estimate["total_verses"],
            "cost_per_chapter": estimate["cost_per_chapter"],
            "cost_per_verse": estimate["cost_per_verse"],
            "estimated_tokens": {
                "input": estimate["total_input_tokens"],
                "output": estimate["total_output_tokens"],
                "total": estimate["total_input_tokens"] + estimate["total_output_tokens"]
            }
        }


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:.4f}"


def print_quote(quote: Dict[str, Any]) -> None:
    """Print a formatted quote."""
    print("\n" + "=" * 60)
    print("🎭 ALT BIBLE - TRANSLATION QUOTE")
    print("=" * 60)
    print(f"Quote ID: {quote['quote_id']}")
    print(f"Persona: {quote['persona']}")
    print(f"Scope: Complete Bible Translation")
    print(f"Chapters: {quote['total_chapters']:,}")
    print(f"Verses: {quote['total_verses']:,}")
    print("-" * 60)
    print("COST BREAKDOWN:")
    print(f"  Base Cost (AI Model): {format_currency(quote['base_cost'])}")
    print(f"  Service Markup ({quote['markup_percentage']}%): {format_currency(quote['markup_amount'])}")
    print(f"  Final Price: {format_currency(quote['final_price'])}")
    print("-" * 60)
    print("DETAILS:")
    print(f"  Cost per Chapter: {format_currency(quote['cost_per_chapter'])}")
    print(f"  Cost per Verse: {format_currency(quote['final_price'] / quote['total_verses'])}")
    print(f"  Estimated Tokens: {quote['estimated_tokens']['total']:,}")
    print("=" * 60)


def main():
    """Main function for quote generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate translation cost quotes")
    parser.add_argument("--persona", required=True, help="Persona name for translation")
    parser.add_argument("--book", help="Specific book to quote (optional)")
    parser.add_argument("--chapter", help="Specific chapter to quote (optional)")
    parser.add_argument("--markup", type=float, default=20.0, help="Markup percentage (default: 20)")
    parser.add_argument("--kjv-file", default="kjv_bible.json", help="Path to KJV Bible JSON file")
    parser.add_argument("--save-quote", help="Save quote to JSON file")
    
    args = parser.parse_args()
    
    # Load KJV data
    try:
        with open(args.kjv_file, 'r') as f:
            kjv_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ KJV file not found: {args.kjv_file}")
        print("💡 Run 'make preprocess' first to generate KJV data")
        sys.exit(1)
    
    # Initialize calculator
    calculator = CostCalculator()
    
    if args.book and args.chapter:
        # Quote for specific chapter
        if args.book in kjv_data and args.chapter in kjv_data[args.book]:
            verses = kjv_data[args.book][args.chapter]
            chapter_cost = calculator.estimate_chapter_cost(args.book, args.chapter, verses, args.persona)
            
            print(f"\n📊 Cost Estimate for {args.book} {args.chapter} ({args.persona})")
            print(f"Input Tokens: {chapter_cost['input_tokens']:,}")
            print(f"Estimated Output Tokens: {chapter_cost['estimated_output_tokens']:,}")
            print(f"Base Cost: {format_currency(chapter_cost['total_cost'])}")
            print(f"With {args.markup}% markup: {format_currency(chapter_cost['total_cost'] * (1 + args.markup/100))}")
        else:
            print(f"❌ Chapter {args.book} {args.chapter} not found")
    else:
        # Quote for entire Bible
        estimate = calculator.estimate_bible_cost(kjv_data, args.persona)
        quote = calculator.generate_quote(estimate, args.markup)
        
        print_quote(quote)
        
        # Save quote if requested
        if args.save_quote:
            with open(args.save_quote, 'w') as f:
                json.dump(quote, f, indent=2)
            print(f"💾 Quote saved to {args.save_quote}")


if __name__ == "__main__":
    main() 