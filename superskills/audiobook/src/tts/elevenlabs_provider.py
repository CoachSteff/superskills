"""
ElevenLabs TTS provider implementation.
"""
from typing import Iterator
from elevenlabs.client import ElevenLabs
from elevenlabs.core.api_error import ApiError

from .base import TTSProvider, TTSConfig


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS provider."""
    
    # Model fallback chain (try in order if voice not compatible)
    MODELS = [
        "eleven_turbo_v2_5",
        "eleven_multilingual_v2",
        "eleven_monolingual_v1"
    ]
    
    def __init__(self, api_key: str):
        """Initialize ElevenLabs provider.
        
        Args:
            api_key: ElevenLabs API key
        """
        self.client = ElevenLabs(api_key=api_key)
    
    def get_character_limit(self) -> int:
        """Return ElevenLabs character limit."""
        return 40000
    
    def generate_speech(self, text: str, config: TTSConfig) -> Iterator[bytes]:
        """Generate speech using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            config: TTS configuration
            
        Yields:
            Audio chunks as bytes
            
        Raises:
            ApiError: If API call fails
        """
        extra = config.extra_settings or {}
        
        # Try primary model first
        model = config.model
        
        try:
            audio_generator = self.client.text_to_speech.convert(
                voice_id=config.voice_id,
                text=text,
                model_id=model,
                output_format="mp3_44100_128",
                voice_settings={
                    "stability": extra.get("stability", 0.65),
                    "similarity_boost": extra.get("similarity_boost", 0.85),
                    "style": extra.get("style", 0.20),
                }
            )
            
            for chunk in audio_generator:
                yield chunk
                
        except ApiError as e:
            # If voice not compatible with model, try fallback models
            if "voice_not_fine_tuned" in str(e) or "not_found" in str(e):
                for fallback_model in self.MODELS:
                    if fallback_model == model:
                        continue  # Skip the one we just tried
                    
                    print(f"  Model '{model}' incompatible, trying '{fallback_model}'...")
                    
                    try:
                        audio_generator = self.client.text_to_speech.convert(
                            voice_id=config.voice_id,
                            text=text,
                            model_id=fallback_model,
                            output_format="mp3_44100_128",
                            voice_settings={
                                "stability": extra.get("stability", 0.65),
                                "similarity_boost": extra.get("similarity_boost", 0.85),
                                "style": extra.get("style", 0.20),
                            }
                        )
                        
                        for chunk in audio_generator:
                            yield chunk
                        
                        return  # Success
                        
                    except ApiError:
                        continue  # Try next fallback
                
                # If all fallbacks failed, raise original error
                raise e
            else:
                # Other API error, re-raise
                raise
    
    def validate_config(self, config: TTSConfig) -> None:
        """Validate ElevenLabs configuration.
        
        Args:
            config: TTS configuration
            
        Raises:
            ValueError: If config is invalid
        """
        if not config.voice_id:
            raise ValueError("ElevenLabs requires voice_id")
        if not config.model:
            raise ValueError("ElevenLabs requires model")
    
    def check_quota(self, estimated_characters: int) -> dict:
        """Check ElevenLabs subscription quota.
        
        Args:
            estimated_characters: Estimated character count
            
        Returns:
            Dict with quota information
        """
        try:
            # Get subscription info
            subscription = self.client.user.get()
            
            # Extract quota information
            # Note: ElevenLabs API returns subscription object with character limits
            if hasattr(subscription, 'subscription'):
                sub = subscription.subscription
                char_limit = sub.character_limit if hasattr(sub, 'character_limit') else -1
                char_count = sub.character_count if hasattr(sub, 'character_count') else 0
                
                available = char_limit - char_count if char_limit > 0 else -1
                
                return {
                    'sufficient': available >= estimated_characters if available > 0 else True,
                    'available': available,
                    'required': estimated_characters,
                    'provider_supports_check': True
                }
            else:
                # Fallback if subscription structure different
                return {
                    'sufficient': True,
                    'available': -1,
                    'required': estimated_characters,
                    'provider_supports_check': False,
                    'error': 'Unable to parse subscription data'
                }
                
        except Exception as e:
            # If quota check fails, allow to proceed (graceful degradation)
            print(f"  Warning: Could not check ElevenLabs quota: {e}")
            return {
                'sufficient': True,
                'available': -1,
                'required': estimated_characters,
                'provider_supports_check': False,
                'error': str(e)
            }
