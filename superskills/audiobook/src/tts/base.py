"""
Base classes for TTS provider abstraction.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, Optional


@dataclass
class TTSConfig:
    """Generic TTS configuration."""
    provider: str  # "elevenlabs", "gemini", "openai"
    model: str
    voice_id: str
    speed: float = 1.0
    # Provider-specific settings stored as dict
    extra_settings: Optional[dict] = field(default_factory=dict)


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    @abstractmethod
    def generate_speech(
        self, 
        text: str, 
        config: TTSConfig
    ) -> Iterator[bytes]:
        """Generate speech from text.
        
        Args:
            text: Text to convert to speech
            config: TTS configuration
            
        Yields:
            Audio chunks as bytes
        """
        pass
    
    @abstractmethod
    def get_character_limit(self) -> int:
        """Return max characters per request for this provider."""
        pass
    
    @abstractmethod
    def validate_config(self, config: TTSConfig) -> None:
        """Validate provider-specific configuration.
        
        Raises:
            ValueError: If config is invalid
        """
        pass
    
    def check_quota(self, estimated_characters: int) -> dict:
        """Check if provider has sufficient quota (optional).
        
        Args:
            estimated_characters: Estimated character count
            
        Returns:
            Dict with: {
                'sufficient': bool,
                'available': int (-1 if unknown),
                'required': int,
                'provider_supports_check': bool
            }
        """
        # Default implementation: no quota check support
        return {
            'sufficient': True,
            'available': -1,  # Unknown
            'required': estimated_characters,
            'provider_supports_check': False
        }
