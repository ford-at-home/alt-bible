#!/usr/bin/env python3
"""
Cost Calculator for Bible Translation

Calculates estimated costs for AI translation based on token usage and model pricing.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CostCalculator:
    """Calculates translation costs based on token usage and model pricing."""
    
    def __init__(self):
        """Initialize the cost calculator with model pricing."""
        # Bedrock model pricing (per 1M tokens) - as of 2024
        self.model_pricing = {
            "us.deepseek.r1-v1:0": {
                "input": 0.00014,  # $0.14 per 1M input tokens
                "output": 0.00056  # $0.56 per 1M output tokens
            },
            "anthropic.claude-3-haiku-20240307-v1:0": {
                "input": 0.00025,  # $0.25 per 1M input tokens
                "output": 0.00125  # $1.25 per 1M output tokens
            },
            "anthropic.claude-3-sonnet-20240229-v1:0": {
                "input": 0.003,    # $3.00 per 1M input tokens
                "output": 0.015    # $15.00 per 1M output tokens
            },
            "meta.llama2-70b-chat-v1": {
                "input": 0.00065,  # $0.65 per 1M input tokens
                "output": 0.0026   # $2.60 per 1M output tokens
            }
        }
        
        # Markup percentage for overhead
        self.markup_percentage = 0.10  # 10% markup
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model_id: str) -> float:
        """
        Calculate the cost for a translation job.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_id: Bedrock model ID
            
        Returns:
            Estimated cost in USD
        """
        if model_id not in self.model_pricing:
            logger.warning(f"⚠️  Unknown model {model_id}, using DeepSeek pricing")
            model_id = "us.deepseek.r1-v1:0"
        
        pricing = self.model_pricing[model_id]
        
        # Calculate base cost
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        base_cost = input_cost + output_cost
        
        # Add markup
        total_cost = base_cost * (1 + self.markup_percentage)
        
        return total_cost
    
    def estimate_bible_cost(self, persona: str, model_id: str = "us.deepseek.r1-v1:0") -> Dict[str, Any]:
        """
        Estimate the cost for translating the entire Bible.
        
        Args:
            persona: Persona name for translation
            model_id: Bedrock model ID
            
        Returns:
            Cost estimation details
        """
        # Rough estimates based on KJV Bible statistics
        # KJV Bible has approximately:
        # - 783,137 words
        # - ~1.2M tokens (roughly 1.5 tokens per word)
        # - Output typically 20-50% longer depending on persona
        
        base_tokens = 1_200_000
        
        # Persona-specific expansion ratios
        persona_ratios = {
            "samuel_l_jackson": 1.3,
            "joe_rogan": 1.2,
            "cardi_b": 1.4,
            "ram_dass": 1.1,
            "hunter_s_thompson": 1.5,
            "maya_angelou": 1.3,
            "ernest_hemingway": 0.9
        }
        
        expansion_ratio = persona_ratios.get(persona, 1.2)
        estimated_output_tokens = int(base_tokens * expansion_ratio)
        
        cost = self.calculate_cost(base_tokens, estimated_output_tokens, model_id)
        
        return {
            "input_tokens": base_tokens,
            "output_tokens": estimated_output_tokens,
            "estimated_cost": cost,
            "model_id": model_id,
            "persona": persona,
            "expansion_ratio": expansion_ratio
        }
    
    def compare_models(self, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """
        Compare costs across different models.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Dictionary of model costs
        """
        costs = {}
        
        for model_id in self.model_pricing:
            cost = self.calculate_cost(input_tokens, output_tokens, model_id)
            costs[model_id] = cost
        
        return costs
    
    def format_cost_breakdown(self, input_tokens: int, output_tokens: int, model_id: str) -> str:
        """
        Format a detailed cost breakdown.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_id: Bedrock model ID
            
        Returns:
            Formatted cost breakdown string
        """
        if model_id not in self.model_pricing:
            return f"❌ Unknown model: {model_id}"
        
        pricing = self.model_pricing[model_id]
        cost = self.calculate_cost(input_tokens, output_tokens, model_id)
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        markup = cost - (input_cost + output_cost)
        
        breakdown = f"""
💰 Cost Breakdown for {model_id}:
   Input tokens: {input_tokens:,} (${input_cost:.4f})
   Output tokens: {output_tokens:,} (${output_cost:.4f})
   Base cost: ${input_cost + output_cost:.4f}
   Markup ({self.markup_percentage*100}%): ${markup:.4f}
   Total: ${cost:.4f}
"""
        
        return breakdown
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_id: Bedrock model ID
            
        Returns:
            Model information
        """
        if model_id not in self.model_pricing:
            return {"error": f"Unknown model: {model_id}"}
        
        pricing = self.model_pricing[model_id]
        
        return {
            "model_id": model_id,
            "input_price_per_1m": pricing["input"],
            "output_price_per_1m": pricing["output"],
            "total_price_per_1m": pricing["input"] + pricing["output"]
        }


def main():
    """Test the cost calculator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cost Calculator for Bible Translation")
    parser.add_argument("--input-tokens", type=int, default=1000, help="Input tokens")
    parser.add_argument("--output-tokens", type=int, default=1200, help="Output tokens")
    parser.add_argument("--model", default="us.deepseek.r1-v1:0", help="Model ID")
    parser.add_argument("--persona", help="Persona for Bible estimation")
    parser.add_argument("--compare", action="store_true", help="Compare all models")
    
    args = parser.parse_args()
    
    calculator = CostCalculator()
    
    if args.persona:
        # Estimate Bible cost for persona
        estimation = calculator.estimate_bible_cost(args.persona, args.model)
        print(f"\n📊 Bible Translation Cost Estimate for {args.persona}:")
        print(f"   Input tokens: {estimation['input_tokens']:,}")
        print(f"   Output tokens: {estimation['output_tokens']:,}")
        print(f"   Estimated cost: ${estimation['estimated_cost']:.2f}")
        print(f"   Model: {estimation['model_id']}")
        print(f"   Expansion ratio: {estimation['expansion_ratio']:.1f}x")
    
    elif args.compare:
        # Compare models
        costs = calculator.compare_models(args.input_tokens, args.output_tokens)
        print(f"\n📊 Model Cost Comparison ({args.input_tokens:,} input, {args.output_tokens:,} output tokens):")
        for model_id, cost in sorted(costs.items(), key=lambda x: x[1]):
            print(f"   {model_id}: ${cost:.4f}")
    
    else:
        # Single calculation
        cost = calculator.calculate_cost(args.input_tokens, args.output_tokens, args.model)
        breakdown = calculator.format_cost_breakdown(args.input_tokens, args.output_tokens, args.model)
        print(breakdown)


if __name__ == "__main__":
    main() 