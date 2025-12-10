#!/usr/bin/env python3
"""
Discover available Anthropic models.

This utility helps discover which model names are currently supported
by the Anthropic API. Use this to find new model releases or verify
model availability.

Usage:
    python tools/discover_models.py
    
Environment:
    ANTHROPIC_API_KEY - Required for API access
"""
import os
import sys
from anthropic import Anthropic, APIError


KNOWN_MODEL_PATTERNS = [
    'claude-3-opus-latest',
    'claude-3-5-opus-latest',
    'claude-3-sonnet-latest',
    'claude-3-5-sonnet-latest',
    'claude-3-haiku-latest',
    'claude-3-5-haiku-latest',
    'claude-3-opus-20240229',
    'claude-3-5-sonnet-20241022',
    'claude-3-5-sonnet-20240620',
    'claude-3-5-haiku-20241022',
    'claude-3-haiku-20240307',
    'claude-2.1',
    'claude-2.0',
]


def test_model(client: Anthropic, model_name: str) -> dict:
    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=1,
            messages=[{"role": "user", "content": "test"}]
        )
        return {
            'model': model_name,
            'available': True,
            'status_code': 200,
            'error': None
        }
    except APIError as e:
        status_code = getattr(e, 'status_code', None)
        return {
            'model': model_name,
            'available': False,
            'status_code': status_code,
            'error': str(e)
        }
    except Exception as e:
        return {
            'model': model_name,
            'available': False,
            'status_code': None,
            'error': str(e)
        }


def discover_models():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("Please set it with: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)
    
    print("🔍 Discovering available Anthropic models...\n")
    
    client = Anthropic(api_key=api_key)
    
    available = []
    unavailable = []
    
    for model_name in KNOWN_MODEL_PATTERNS:
        print(f"Testing {model_name}...", end=' ')
        result = test_model(client, model_name)
        
        if result['available']:
            print("✅ Available")
            available.append(model_name)
        else:
            status = result['status_code']
            if status == 404:
                print("❌ Not Found")
            elif status == 400:
                print("⚠️  Bad Request (may be deprecated)")
            else:
                print(f"❌ Error ({status})")
            unavailable.append(result)
    
    print("\n" + "="*60)
    print(f"\n✅ Available Models ({len(available)}):")
    for model in available:
        print(f"  • {model}")
    
    if unavailable:
        print(f"\n❌ Unavailable Models ({len(unavailable)}):")
        for result in unavailable:
            status = result['status_code'] or 'Unknown'
            print(f"  • {result['model']} (Status: {status})")
    
    print("\n" + "="*60)
    print("\n💡 Recommended aliases for cli/utils/model_resolver.py:")
    print("MODEL_ALIASES = {")
    
    latest_aliases = [m for m in available if 'latest' in m]
    for alias in latest_aliases:
        versioned = [m for m in available if alias.replace('-latest', '') in m and '-latest' not in m]
        if versioned:
            print(f"    '{alias}': '{versioned[0]}',")
    
    print("}")


if __name__ == '__main__':
    discover_models()
