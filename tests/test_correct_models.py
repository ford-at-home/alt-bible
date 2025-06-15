#!/usr/bin/env python3
"""
Test models with correct input formats
"""

import boto3
import json
import os

# Set the profile
os.environ['AWS_PROFILE'] = 'personal'

def test_deepseek():
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    simple_prompt = "Say hello"
    
    try:
        response = bedrock.invoke_model(
            modelId="deepseek.r1-v1:0",  # Correct ID
            body=json.dumps({
                "prompt": simple_prompt,
                "max_tokens": 50,
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body.get('completion', '').strip()
        
        print(f"DeepSeek response: '{completion}'")
        return completion
        
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return None

def test_claude():
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    simple_prompt = "Say hello"
    
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "prompt": f"\n\nHuman: {simple_prompt}\n\nAssistant:",
                "max_tokens_to_sample": 50,
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body.get('completion', '').strip()
        
        print(f"Claude response: '{completion}'")
        return completion
        
    except Exception as e:
        print(f"Claude error: {e}")
        return None

if __name__ == "__main__":
    print("Testing DeepSeek...")
    test_deepseek()
    
    print("\nTesting Claude...")
    test_claude() 