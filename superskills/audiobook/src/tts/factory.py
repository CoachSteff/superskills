"""
TTS provider factory.
"""
from typing import Dict, Type
from .base import TTSProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .voicebox_provider import VoiceboxProvider

# ElevenLabs was retired on 20 September 2026 and replaced by Voicebox, which runs
# locally at no cost in Steff's own cloned voice. elevenlabs_provider.py is left in
# the tree but is deliberately not registered; asking for it raises a pointer below.
RETIRED_PROVIDERS = {
    "elevenlabs": (
        "ElevenLabs was retired on 20 September 2026. Use provider='voicebox': it runs "
        "locally (Chatterbox Multilingual, EN + NL, Steff's cloned voice), needs no API "
        "key and costs nothing per character. The server must be running — `open -a Voicebox`."
    ),
}

PROVIDER_REGISTRY: Dict[str, Type[TTSProvider]] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "voicebox": VoiceboxProvider,
}


def create_tts_provider(provider_name: str, api_key: str) -> TTSProvider:
    """Factory function to create TTS provider instances.
    
    Args:
        provider_name: "voicebox", "gemini", or "openai"
        api_key: API key for the provider. Ignored by "voicebox", which is local.
        
    Returns:
        TTSProvider instance
        
    Raises:
        ValueError: If provider not supported
    """
    name = provider_name.lower()
    if name in RETIRED_PROVIDERS:
        raise ValueError(RETIRED_PROVIDERS[name])

    provider_class = PROVIDER_REGISTRY.get(name)
    if not provider_class:
        supported = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unsupported TTS provider: '{provider_name}'. "
            f"Supported providers: {supported}"
        )
    
    return provider_class(api_key=api_key)
