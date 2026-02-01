"""
OpenAI TTS provider implementation (placeholder).
"""
from typing import Iterator
from .base import TTSProvider, TTSConfig


class OpenAIProvider(TTSProvider):
    """OpenAI TTS provider (placeholder - not yet implemented)."""
    
    def __init__(self, api_key: str):
        """Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        # TODO: Initialize OpenAI client
    
    def get_character_limit(self) -> int:
        """Return OpenAI character limit."""
        return 4096  # OpenAI TTS limit
    
    def generate_speech(self, text: str, config: TTSConfig) -> Iterator[bytes]:
        """Generate speech using OpenAI API.
        
        Args:
            text: Text to convert to speech
            config: TTS configuration
            
        Yields:
            Audio chunks as bytes
            
        Raises:
            NotImplementedError: OpenAI TTS not yet implemented
        """
        raise NotImplementedError(
            "OpenAI TTS support is coming soon. "
            "Currently only ElevenLabs is supported. "
            "Use --tts-provider elevenlabs or update your config."
        )
    
    def validate_config(self, config: TTSConfig) -> None:
        """Validate OpenAI configuration.
        
        Args:
            config: TTS configuration
            
        Raises:
            NotImplementedError: OpenAI TTS not yet implemented
        """
        raise NotImplementedError(
            "OpenAI TTS support is coming soon. "
            "Currently only ElevenLabs is supported."
        )
