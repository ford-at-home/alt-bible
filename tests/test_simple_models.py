#!/usr/bin/env python3
"""
Test simpler models with completion API
"""

import boto3
import json
import os

# Set the profile
os.environ['AWS_PROFILE'] = 'personal'

def test_model(model_id, prompt_format="simple"):
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    if prompt_format == "simple":
        prompt = "Say hello"
        body = {
            "prompt": prompt,
            "max_tokens": 50,
            "temperature": 0.7
        }
    elif prompt_format == "claude":
        prompt = "Say hello"
        body = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 50,
            "temperature": 0.7
        }
    
    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body.get('completion', '').strip()
        
        print(f"{model_id} response: '{completion}'")
        return completion
        
    except Exception as e:
        print(f"{model_id} error: {e}")
        return None

if __name__ == "__main__":
    # Test models that should work with completion API
    models_to_test = [
        ("anthropic.claude-v2", "claude"),
        ("anthropic.claude-instant-v1", "claude"),
        ("amazon.titan-text-express-v1:0:8k", "simple"),
        ("meta.llama3-8b-instruct-v1:0", "simple"),
        ("mistral.mistral-7b-instruct-v0:2", "simple")
    ]
    
    for model_id, format_type in models_to_test:
        print(f"\nTesting {model_id}...")
        test_model(model_id, format_type) 