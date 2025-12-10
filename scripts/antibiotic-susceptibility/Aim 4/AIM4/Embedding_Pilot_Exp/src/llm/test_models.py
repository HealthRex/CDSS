#!/usr/bin/env python3
"""
Test script to verify each model's payload and response parsing works correctly.

Usage:
    python src/llm/test_models.py                    # Test all models
    python src/llm/test_models.py gpt-5              # Test specific model
    python src/llm/test_models.py --list             # List available models
    python src/llm/test_models.py gpt-5 --raw        # Show raw response JSON
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dotenv import load_dotenv
load_dotenv()

import aiohttp
from llm.model_registry import MODEL_CONFIGS, get_model_config, list_available_models

# Test prompt
TEST_PROMPT = "What is 2 + 2? Reply with just the number."


async def test_model(model_alias: str, show_raw: bool = False) -> bool:
    """
    Test a single model by sending a simple prompt and verifying the response.
    Returns True if successful, False otherwise.
    """
    print(f"\n{'='*60}")
    print(f"Testing: {model_alias}")
    print("="*60)
    
    try:
        config = get_model_config(model_alias)
    except ValueError as e:
        print(f"❌ Error: {e}")
        return False
    
    url = config.url
    print(f"URL: {url[:60]}...")
    print(f"Display Name: {config.display_name}")
    
    # Build payload
    payload = config.build_payload(model_alias, TEST_PROMPT)
    print(f"\n📤 Payload:")
    print(json.dumps(payload, indent=2)[:500])
    
    # Get API key
    api_key = os.getenv("HEALTHREX_API_KEY")
    if not api_key:
        print("❌ HEALTHREX_API_KEY not set in .env")
        return False
    
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Make request
    print(f"\n📡 Sending request...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=60) as response:
                status = response.status
                print(f"Status: {status}")
                
                if status != 200:
                    error_text = await response.text()
                    print(f"❌ Error response: {error_text[:500]}")
                    return False
                
                data = await response.json()
                
                if show_raw:
                    print(f"\n📥 Raw Response:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
                
                # Parse response
                try:
                    content = config.parse_response(data)
                    print(f"\n✅ Parsed Content:")
                    print(f"   {content[:200]}")
                    
                    if content.startswith("[PARSE_ERROR]"):
                        print("\n⚠️  Response parsed with fallback. Update parse_response for this model.")
                        return False
                    
                    print(f"\n✅ Model '{model_alias}' is working correctly!")
                    return True
                    
                except Exception as e:
                    print(f"\n❌ Parse error: {e}")
                    print(f"Raw response: {json.dumps(data, indent=2)[:500]}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out (60s)")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


async def test_all_models(show_raw: bool = False):
    """Test all configured models."""
    results = {}
    
    for model_alias in MODEL_CONFIGS.keys():
        success = await test_model(model_alias, show_raw)
        results[model_alias] = success
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for model, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {model:<22} {status}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Test LLM model configurations")
    parser.add_argument("model", nargs="?", help="Model alias to test (omit to test all)")
    parser.add_argument("--list", "-l", action="store_true", help="List available models")
    parser.add_argument("--raw", "-r", action="store_true", help="Show raw response JSON")
    
    args = parser.parse_args()
    
    if args.list:
        list_available_models()
        return
    
    if args.model:
        asyncio.run(test_model(args.model, args.raw))
    else:
        asyncio.run(test_all_models(args.raw))


if __name__ == "__main__":
    main()

