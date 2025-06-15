#!/usr/bin/env python3
"""
Bible Preprocessing Wrapper

Simple script to preprocess Bible files (JSON or text) and save to the processed directory.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from preprocessors.json_preprocessor import main as json_main
from preprocessors.text_preprocessor import main as text_main


def main():
    """Main function to handle preprocessing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Preprocess Bible files")
    parser.add_argument("input_file", help="Path to input Bible file (JSON or text)")
    parser.add_argument("--output", default="data/processed/bible.json", help="Output JSON file path")
    
    args = parser.parse_args()
    
    # Determine file type and call appropriate preprocessor
    input_path = Path(args.input_file)
    
    if not input_path.exists():
        print(f"❌ Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if input_path.suffix.lower() == '.json':
        print("📖 Processing JSON Bible file...")
        # For JSON files, we need to modify the sys.argv to work with the existing main function
        original_argv = sys.argv
        sys.argv = ['json_preprocessor.py']  # Simulate command line args
        json_main()
    else:
        print("📖 Processing text Bible file...")
        # For text files, call the text preprocessor
        original_argv = sys.argv
        sys.argv = ['text_preprocessor.py', str(input_path), '--output', str(output_path)]
        text_main()
    
    print(f"✅ Preprocessing complete! Output: {args.output}")


if __name__ == "__main__":
    main() 