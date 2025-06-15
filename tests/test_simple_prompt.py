#!/usr/bin/env python3
"""
Simple test to see if Bedrock model responds
"""

import json
import boto3
import os

# Set the profile
os.environ['AWS_PROFILE'] = 'personal'

def test_simple_prompt():
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    simple_prompt = "Hello, can you respond with 'Yes, I can help you'?"
    
    try:
        response = bedrock.invoke_model(
            modelId="us.deepseek.r1-v1:0",
            body=json.dumps({
                "prompt": simple_prompt,
                "max_tokens": 50,
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body.get('completion', '').strip()
        
        print(f"Model response: '{completion}'")
        print(f"Response length: {len(completion)} characters")
        
        return completion
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_simple_prompt() 