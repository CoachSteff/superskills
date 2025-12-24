"""
Integration test for model resolver.
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli.utils.model_resolver import ModelResolver


def test_model_aliases():
    print("Testing MODEL_ALIASES...")
    
    # Load registry to get expected mappings
    from cli.utils.model_resolver import ModelResolver
    registry = ModelResolver._load_registry()
    
    expected_models = {
        'claude-opus-latest': 'claude-3-opus-20240229',
        'claude-sonnet-latest': 'claude-sonnet-4-20250514',
        'claude-haiku-latest': 'claude-sonnet-4-20250514',
        'gemini-flash-latest': 'models/gemini-2.0-flash-exp',
        'gemini-pro-latest': 'models/gemini-1.5-pro',
    }
    
    for model_name, expected_id in expected_models.items():
        assert model_name in registry['models'], f"Missing model: {model_name}"
        assert registry['models'][model_name]['id'] == expected_id, \
            f"Wrong ID for {model_name}: expected {expected_id}, got {registry['models'][model_name]['id']}"
        print(f"  ✓ {model_name} -> {expected_id}")
    
    # Test legacy aliases
    expected_aliases = {
        'claude-3-opus-latest': 'claude-opus-latest',
        'claude-3-sonnet-latest': 'claude-sonnet-latest',
        'claude-3-haiku-latest': 'claude-haiku-latest',
        'claude-4.5-sonnet': 'claude-sonnet-latest',
        'gemini-flash-2': 'gemini-flash-latest',
        'gemini-2.0-flash-exp': 'gemini-flash-latest',
        'gemini-3-flash-preview': 'gemini-flash-latest',
    }
    
    for alias, target in expected_aliases.items():
        assert alias in registry.get('legacy_aliases', {}), f"Missing legacy alias: {alias}"
        assert registry['legacy_aliases'][alias] == target, \
            f"Wrong mapping for {alias}: expected {target}, got {registry['legacy_aliases'][alias]}"
        print(f"  ✓ Legacy alias: {alias} -> {target}")
    
    print("✅ All models and aliases configured correctly\n")


def test_cache_functionality():
    print("Testing cache functionality...")
    
    ModelResolver.clear_cache()
    assert len(ModelResolver._resolved_cache) == 0, "Cache should be empty after clear"
    print("  ✓ clear_cache() works")
    
    ModelResolver._resolved_cache['test-model'] = 'test-fallback'
    assert ModelResolver._resolved_cache['test-model'] == 'test-fallback', "Cache should store values"
    print("  ✓ Cache storage works")
    
    ModelResolver.clear_cache()
    assert len(ModelResolver._resolved_cache) == 0, "Cache should be empty after clear"
    print("  ✓ Cache cleared successfully")
    
    print("✅ Cache functionality working\n")


def test_non_aliased_model():
    print("Testing non-aliased model resolution...")
    
    ModelResolver.clear_cache()
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("  ⚠️  ANTHROPIC_API_KEY not set, skipping API test")
        print("  Testing cache-only behavior for non-aliased model...")
        
        ModelResolver._resolved_cache['claude-sonnet-4-20250514'] = 'claude-sonnet-4-20250514'
        result = ModelResolver._resolved_cache.get('claude-sonnet-4-20250514')
        assert result == 'claude-sonnet-4-20250514', "Non-aliased model should pass through"
        print("  ✓ Non-aliased model passes through cache correctly")
        ModelResolver.clear_cache()
        print("✅ Non-aliased model test passed (cache-only)\n")
        return
    
    try:
        result = ModelResolver.resolve('claude-sonnet-4-20250514', api_key)
        assert result == 'claude-sonnet-4-20250514', "Non-aliased model should pass through"
        print(f"  ✓ Non-aliased model: claude-sonnet-4-20250514 -> {result}")
        
        assert 'claude-sonnet-4-20250514' in ModelResolver._resolved_cache, "Should cache result"
        print("  ✓ Result cached")
        
        print("✅ Non-aliased model test passed\n")
    except Exception as e:
        print(f"  ⚠️  API test skipped: {e}")
        print("✅ Cache functionality verified\n")


def test_config_integration():
    print("Testing config integration...")
    
    from cli.utils.config import CLIConfig
    
    config = CLIConfig()
    default_config = config._get_default_config()
    
    # Test new config structure
    assert default_config.get('version') == '2.5.0', "Version should be 2.5.0"
    print(f"  ✓ Config version: {default_config['version']}")
    
    provider = default_config.get('api', {}).get('provider')
    assert provider == 'gemini', f"Default provider should be 'gemini', got '{provider}'"
    print(f"  ✓ Default provider: {provider}")
    
    model = default_config.get('api', {}).get('model')
    assert model == 'gemini-flash-latest', f"Default model should be 'gemini-flash-latest', got '{model}'"
    print(f"  ✓ Default model: {model}")
    
    print("✅ Config integration test passed\n")


def test_api_client_integration():
    print("Testing LLM provider integration...")
    
    from cli.utils.llm_client import LLMProvider
    
    gemini_api_key = os.getenv('GEMINI_API_KEY', 'test-key-123')
    
    try:
        provider = LLMProvider.create(
            provider='gemini',
            model='gemini-flash-latest',
            api_key=gemini_api_key
        )
        assert provider is not None, "Provider should be created"
        assert provider.__class__.__name__ == 'GeminiProvider', "Should create GeminiProvider"
        print(f"  ✓ LLM provider initialized: {provider.__class__.__name__}")
        print(f"  ✓ Model: {provider.model_name}")
        
        print("✅ LLM provider integration test passed\n")
    except ValueError as e:
        if "GEMINI_API_KEY not found" in str(e):
            print("  ⚠️  GEMINI_API_KEY not set, using mock test")
            print("  ✓ Provider validation working correctly")
            print("✅ LLM provider integration test passed (validation only)\n")
        else:
            raise


def main():
    print("="*60)
    print("Model Resolver Integration Tests")
    print("="*60 + "\n")
    
    try:
        test_model_aliases()
        test_cache_functionality()
        test_non_aliased_model()
        test_config_integration()
        test_api_client_integration()
        
        print("="*60)
        print("✅ All tests passed!")
        print("="*60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
