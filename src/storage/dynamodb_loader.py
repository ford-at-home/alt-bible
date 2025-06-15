#!/usr/bin/env python3
"""
Load Bible Data to DynamoDB

Loads processed Bible JSON data into DynamoDB with the proper schema
for storing translations and baseline KJV text.
"""

import json
import boto3
import sys
from typing import Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
import argparse


class DynamoDBLoader:
    """Handles loading Bible data to DynamoDB."""
    
    def __init__(self, table_name: str = "BibleTranslations", region: str = "us-east-1"):
        """
        Initialize the DynamoDB loader.
        
        Args:
            table_name: DynamoDB table name
            region: AWS region
        """
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    def create_table_if_not_exists(self) -> None:
        """Create the DynamoDB table if it doesn't exist."""
        try:
            # Check if table exists
            self.table.load()
            print(f"✅ Table {self.table_name} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"📦 Creating table {self.table_name}...")
                self._create_table()
            else:
                raise e
    
    def _create_table(self) -> None:
        """Create the DynamoDB table."""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'pk',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'sk',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'pk',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'sk',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'  # On-demand billing
            )
            
            # Wait for table to be created
            table.wait_until_exists()
            print(f"✅ Table {self.table_name} created successfully")
            
        except ClientError as e:
            print(f"❌ Error creating table: {e}")
            sys.exit(1)
    
    def load_bible_data(self, bible_data: Dict[str, Any], persona: str = "kjv") -> None:
        """
        Load Bible data into DynamoDB.
        
        Args:
            bible_data: Processed Bible data in format {book: {chapter: {verse: text}}}
            persona: Persona identifier (e.g., "kjv" for baseline)
        """
        print(f"📤 Loading Bible data for persona: {persona}")
        
        total_items = 0
        successful_items = 0
        failed_items = 0
        
        # Count total items first
        for book, chapters in bible_data.items():
            for chapter, verses in chapters.items():
                total_items += len(verses)
        
        print(f"📊 Total verses to load: {total_items}")
        
        # Load data
        for book, chapters in bible_data.items():
            print(f"📚 Loading {book}...")
            
            for chapter, verses in chapters.items():
                print(f"   📖 Chapter {chapter} ({len(verses)} verses)")
                
                for verse_num, verse_text in verses.items():
                    try:
                        # Create item for DynamoDB
                        item = {
                            'pk': f"persona#{persona}",
                            'sk': f"book#{book}#{chapter}#{verse_num}",
                            'translated_text': verse_text,
                            'metadata': {
                                'book': book,
                                'chapter': int(chapter),
                                'verse': int(verse_num),
                                'persona': persona,
                                'translation_date': '2024-01-01T00:00:00Z',
                                'model_used': 'baseline'
                            }
                        }
                        
                        # Put item in DynamoDB
                        self.table.put_item(Item=item)
                        successful_items += 1
                        
                        # Progress indicator
                        if successful_items % 100 == 0:
                            print(f"   ✅ Loaded {successful_items}/{total_items} verses")
                    
                    except Exception as e:
                        print(f"❌ Error loading {book} {chapter}:{verse_num}: {e}")
                        failed_items += 1
        
        print(f"\n🎉 Loading complete!")
        print(f"✅ Successful: {successful_items}")
        print(f"❌ Failed: {failed_items}")
        print(f"📊 Total: {total_items}")
    
    def verify_data(self, persona: str = "kjv") -> None:
        """
        Verify that data was loaded correctly.
        
        Args:
            persona: Persona identifier to verify
        """
        print(f"🔍 Verifying data for persona: {persona}")
        
        try:
            # Query for a sample of items
            response = self.table.query(
                KeyConditionExpression='pk = :pk',
                ExpressionAttributeValues={
                    ':pk': f"persona#{persona}"
                },
                Limit=10
            )
            
            items = response.get('Items', [])
            print(f"📊 Found {len(items)} items in sample query")
            
            if items:
                print("📝 Sample items:")
                for item in items[:3]:
                    book = item['metadata']['book']
                    chapter = item['metadata']['chapter']
                    verse = item['metadata']['verse']
                    text = item['translated_text'][:50] + "..." if len(item['translated_text']) > 50 else item['translated_text']
                    print(f"   {book} {chapter}:{verse} - {text}")
            
            # Get total count
            response = self.table.query(
                KeyConditionExpression='pk = :pk',
                ExpressionAttributeValues={
                    ':pk': f"persona#{persona}"
                },
                Select='COUNT'
            )
            
            total_count = response.get('Count', 0)
            print(f"📊 Total items in DynamoDB: {total_count}")
            
        except Exception as e:
            print(f"❌ Error verifying data: {e}")


def main():
    """Main function for loading Bible data to DynamoDB."""
    parser = argparse.ArgumentParser(description="Load Bible data to DynamoDB")
    parser.add_argument("input_file", help="Path to the processed Bible JSON file")
    parser.add_argument("--table", default="BibleTranslations", help="DynamoDB table name")
    parser.add_argument("--persona", default="kjv", help="Persona identifier")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument("--verify", action="store_true", help="Verify data after loading")
    
    args = parser.parse_args()
    
    print("🎭 HOLY REMIX - DynamoDB Loader")
    print("=" * 40)
    
    # Load Bible data
    try:
        with open(args.input_file, 'r') as f:
            bible_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {args.input_file}")
        print("💡 Run the preprocessor first to generate the JSON file")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)
    
    # Initialize loader
    try:
        loader = DynamoDBLoader(args.table, args.region)
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        print("💡 Run 'aws configure' to set up your credentials")
        sys.exit(1)
    
    # Create table if needed
    loader.create_table_if_not_exists()
    
    # Load data
    loader.load_bible_data(bible_data, args.persona)
    
    # Verify if requested
    if args.verify:
        loader.verify_data(args.persona)
    
    print("\n🎉 Bible data loaded to DynamoDB successfully!")
    print(f"📁 Table: {args.table}")
    print(f"👤 Persona: {args.persona}")
    print("🚀 Ready for AI translation!")


if __name__ == "__main__":
    main() 