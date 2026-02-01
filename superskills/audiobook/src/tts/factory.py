"""
TTS provider factory.
"""
from typing import Dict, Type
from .base import TTSProvider
from .elevenlabs_provider import ElevenLabsProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider


PROVIDER_REGISTRY: Dict[str, Type[TTSProvider]] = {
    "elevenlabs": ElevenLabsProvider,
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
}


def create_tts_provider(provider_name: str, api_key: str) -> TTSProvider:
    """Factory function to create TTS provider instances.
    
    Args:
        provider_name: "elevenlabs", "gemini", or "openai"
        api_key: API key for the provider
        
    Returns:
        TTSProvider instance
        
    Raises:
        ValueError: If provider not supported
    """
    provider_class = PROVIDER_REGISTRY.get(provider_name.lower())
    if not provider_class:
        supported = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unsupported TTS provider: '{provider_name}'. "
            f"Supported providers: {supported}"
        )
    
    return provider_class(api_key=api_key)
