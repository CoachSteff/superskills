"""
Gemini TTS provider implementation.
"""
import io
from typing import Iterator

from .base import TTSProvider, TTSConfig


class GeminiProvider(TTSProvider):
    """Gemini TTS provider using Google Generative AI."""
    
    # Available voices with characteristics
    VOICES = {
        "Puck": "Upbeat",
        "Charon": "Informative",
        "Aoede": "Breezy",
        "Kore": "Firm",
        "Fenrir": "Excitable",
        "Iapetus": "Clear",
        "Achird": "Friendly",
        "Sadaltager": "Knowledgeable",
    }
    
    def __init__(self, api_key: str):
        """Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key
        """
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "google-genai package not installed. "
                "Install with: pip install google-genai"
            )
        
        self.client = genai.Client(api_key=api_key)
        self.genai = genai
    
    def get_character_limit(self) -> int:
        """Return Gemini character limit.
        
        Gemini supports 32,000 tokens ≈ 120,000 characters.
        Using conservative estimate of 100,000.
        """
        return 100000
    
    def generate_speech(self, text: str, config: TTSConfig) -> Iterator[bytes]:
        """Generate speech using Gemini API.
        
        Args:
            text: Text to convert to speech
            config: TTS configuration
            
        Yields:
            Audio chunks as MP3 bytes
        """
        # Determine model
        model = config.model or "gemini-2.5-flash-preview-tts"
        
        # Determine voice
        voice_name = config.voice_id or "Puck"  # Default voice
        
        # Build generation config
        generation_config = {
            "response_modalities": ["Audio"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": voice_name
                    }
                }
            }
        }
        
        # Generate audio
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=text,
                config=generation_config
            )
        except Exception as e:
            error_msg = str(e)
            
            # Detect token limit error
            if 'token count' in error_msg.lower() and 'exceeds' in error_msg.lower():
                raise ValueError(
                    f"Text exceeds Gemini's token limit. "
                    f"Error: {error_msg}\n"
                    f"Suggestion: Reduce chapter size or use auto-splitting."
                )
            
            # Re-raise other errors
            raise
        
        # Extract audio data (PCM format)
        if not response.candidates or not response.candidates[0].content.parts:
            raise ValueError("No audio generated from Gemini API")
        
        audio_part = response.candidates[0].content.parts[0]
        if not hasattr(audio_part, 'inline_data'):
            raise ValueError("Response does not contain audio data")
        
        pcm_data = audio_part.inline_data.data
        
        # Convert PCM to MP3
        mp3_data = self._convert_pcm_to_mp3(pcm_data)
        
        # Yield as single chunk (Gemini doesn't stream)
        yield mp3_data
    
    def _convert_pcm_to_mp3(self, pcm_data: bytes) -> bytes:
        """Convert PCM audio to MP3 format.
        
        Args:
            pcm_data: Raw PCM audio bytes
            
        Returns:
            MP3 audio bytes
        """
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError(
                "pydub required for Gemini audio conversion. "
                "Install with: pip install pydub"
            )
        
        # Gemini returns PCM: 24kHz, mono, 16-bit
        audio = AudioSegment(
            data=pcm_data,
            sample_width=2,  # 16-bit = 2 bytes
            frame_rate=24000,  # 24kHz
            channels=1  # mono
        )
        
        # Export as MP3
        mp3_buffer = io.BytesIO()
        audio.export(mp3_buffer, format="mp3", bitrate="128k")
        mp3_buffer.seek(0)
        
        return mp3_buffer.read()
    
    def validate_config(self, config: TTSConfig) -> None:
        """Validate Gemini configuration.
        
        Args:
            config: TTS configuration
            
        Raises:
            ValueError: If config is invalid
        """
        # Voice is optional (defaults to Puck)
        if config.voice_id and config.voice_id not in self.VOICES:
            available = ", ".join(list(self.VOICES.keys())[:8])  # Show first 8
            print(f"Info: Voice '{config.voice_id}' not in common voices.")
            print(f"  Common voices: {available}, ...")
            print(f"  Gemini supports 30 voices total. Proceeding...")
        
        # Model validation (optional, uses default if not set)
        valid_models = [
            "gemini-2.5-flash-preview-tts",
            "gemini-2.5-pro-preview-tts"
        ]
        if config.model and config.model not in valid_models:
            print(f"Info: Model '{config.model}' not in known TTS models.")
            print(f"  Valid models: {', '.join(valid_models)}")
            print(f"  Using default: gemini-2.5-flash-preview-tts")
    
    def check_quota(self, estimated_characters: int) -> dict:
        """Check Gemini quota (not supported by API).
        
        Args:
            estimated_characters: Estimated character count
            
        Returns:
            Dict indicating quota check not supported
        """
        # Gemini doesn't provide quota API yet
        return {
            'sufficient': True,
            'available': -1,  # Unknown
            'required': estimated_characters,
            'provider_supports_check': False
        }
