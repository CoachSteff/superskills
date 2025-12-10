"""
Model resolver with lazy resolution, caching, and fallback logic.
"""
from typing import Optional, Dict
from anthropic import Anthropic, APIError


class ModelResolver:
    
    MODEL_ALIASES = {
        'claude-3-opus-latest': 'claude-3-opus-20240229',
        'claude-3-sonnet-latest': 'claude-3-5-sonnet-20241022',
        'claude-3-haiku-latest': 'claude-3-5-haiku-20241022',
        'claude-4.5-sonnet': 'claude-3-5-sonnet-20241022'
    }
    
    _resolved_cache: Dict[str, str] = {}
    
    @classmethod
    def resolve(cls, model: str, api_key: str) -> str:
        if model in cls._resolved_cache:
            return cls._resolved_cache[model]
        
        if model not in cls.MODEL_ALIASES:
            cls._resolved_cache[model] = model
            return model
        
        fallback = cls.MODEL_ALIASES[model]
        
        try:
            client = Anthropic(api_key=api_key)
            client.messages.create(
                model=model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            cls._resolved_cache[model] = model
            return model
        
        except APIError as e:
            status_code = getattr(e, 'status_code', None)
            if status_code == 404:
                print(f"ℹ Model '{model}' not available. Using fallback: {fallback}")
                cls._resolved_cache[model] = fallback
                return fallback
            else:
                raise
        
        except Exception:
            raise
    
    @classmethod
    def clear_cache(cls):
        cls._resolved_cache.clear()
