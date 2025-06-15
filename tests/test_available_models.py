#!/usr/bin/env python3
"""
Test available Bedrock models
"""

import boto3
import json
import os

# Set the profile
os.environ['AWS_PROFILE'] = 'personal'

def list_models():
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        response = bedrock.list_foundation_models()
        
        print("Available models:")
        for model in response.get('modelSummaries', []):
            print(f"  - {model['modelId']} ({model['modelName']})")
            
        return response.get('modelSummaries', [])
        
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def test_model(model_id):
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    simple_prompt = "Say hello"
    
    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "prompt": simple_prompt,
                "max_tokens": 50,
                "temperature": 0.7
            })
        )
        
        response_body = json.loads(response['body'].read())
        completion = response_body.get('completion', '').strip()
        
        print(f"Model {model_id} response: '{completion}'")
        return completion
        
    except Exception as e:
        print(f"Error with model {model_id}: {e}")
        return None

if __name__ == "__main__":
    models = list_models()
    
    # Try a few common models
    test_models = [
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "amazon.titan-text-express-v1",
        "ai21.j2-ultra-v1"
    ]
    
    for model_id in test_models:
        print(f"\nTesting {model_id}...")
        test_model(model_id) 