"""
Model resolver with registry-based resolution, multi-provider support, and fallback logic.
"""
import yaml
from typing import Optional, Dict, Any
from pathlib import Path
from anthropic import Anthropic, APIError


class ModelResolver:
    
    _registry: Optional[Dict[str, Any]] = None
    _resolved_cache: Dict[str, str] = {}
    
    @classmethod
    def _load_registry(cls) -> Dict[str, Any]:
        """Load model registry from YAML file"""
        if cls._registry is not None:
            return cls._registry
        
        registry_path = Path(__file__).parent.parent / 'config' / 'models.yaml'
        
        if not registry_path.exists():
            # Fallback to hardcoded registry if file not found
            cls._registry = {
                'models': {
                    'claude-opus-latest': {'provider': 'anthropic', 'id': 'claude-3-opus-20240229'},
                    'claude-sonnet-latest': {'provider': 'anthropic', 'id': 'claude-sonnet-4-20250514'},
                    'claude-haiku-latest': {'provider': 'anthropic', 'id': 'claude-sonnet-4-20250514'},
                    'gemini-flash-latest': {'provider': 'google', 'id': 'gemini-3-flash-preview'},
                    'gemini-flash-2': {'provider': 'google', 'id': 'gemini-2.0-flash-exp'},
                    'openai-default': {'provider': 'openai', 'id': 'gpt-4o-mini'},
                },
                'legacy_aliases': {
                    'claude-3-opus-latest': 'claude-opus-latest',
                    'claude-3-sonnet-latest': 'claude-sonnet-latest',
                    'claude-3-haiku-latest': 'claude-haiku-latest',
                    'claude-4.5-sonnet': 'claude-sonnet-latest',
                    'gemini-2.0-flash-exp': 'gemini-flash-2',
                }
            }
            return cls._registry
        
        with open(registry_path, 'r') as f:
            cls._registry = yaml.safe_load(f)
        
        return cls._registry
    
    @classmethod
    def resolve(cls, model: str, api_key: str, provider: Optional[str] = None) -> str:
        """
        Resolve a model name to its concrete ID.
        
        Args:
            model: Logical model name or concrete ID
            api_key: API key for the provider (used for fallback testing)
            provider: Optional provider name (anthropic, google, openai)
        
        Returns:
            Concrete model ID
        """
        # Check cache first
        if model in cls._resolved_cache:
            return cls._resolved_cache[model]
        
        registry = cls._load_registry()
        
        # Handle legacy aliases
        if model in registry.get('legacy_aliases', {}):
            model = registry['legacy_aliases'][model]
        
        # If model is not in registry, assume it's a concrete ID
        if model not in registry.get('models', {}):
            cls._resolved_cache[model] = model
            return model
        
        # Get model info from registry
        model_info = registry['models'][model]
        concrete_id = model_info['id']
        model_provider = model_info['provider']
        
        # For Anthropic models, test if the alias is available
        if model_provider == 'anthropic' and provider != 'google' and provider != 'openai':
            try:
                client = Anthropic(api_key=api_key)
                # Try to use the logical name first
                client.messages.create(
                    model=model,
                    max_tokens=1,
                    messages=[{"role": "user", "content": "test"}]
                )
                # If successful, use the logical name
                cls._resolved_cache[model] = model
                return model
            
            except APIError as e:
                status_code = getattr(e, 'status_code', None)
                if status_code == 404:
                    print(f"ℹ Model '{model}' not available. Using fallback: {concrete_id}")
                    cls._resolved_cache[model] = concrete_id
                    return concrete_id
                else:
                    # For other errors, still use concrete ID as fallback
                    cls._resolved_cache[model] = concrete_id
                    return concrete_id
            
            except Exception:
                # On any exception, use concrete ID
                cls._resolved_cache[model] = concrete_id
                return concrete_id
        
        # For non-Anthropic providers, use concrete ID directly
        cls._resolved_cache[model] = concrete_id
        return concrete_id
    
    @classmethod
    def get_provider(cls, model: str) -> Optional[str]:
        """
        Get the provider for a given model.
        
        Args:
            model: Logical model name
        
        Returns:
            Provider name (anthropic, google, openai) or None
        """
        registry = cls._load_registry()
        
        # Handle legacy aliases
        if model in registry.get('legacy_aliases', {}):
            model = registry['legacy_aliases'][model]
        
        if model in registry.get('models', {}):
            return registry['models'][model]['provider']
        
        return None
    
    @classmethod
    def clear_cache(cls):
        """Clear the resolution cache"""
        cls._resolved_cache.clear()
    
    @classmethod
    def reload_registry(cls):
        """Reload the model registry from file"""
        cls._registry = None
        cls._load_registry()
