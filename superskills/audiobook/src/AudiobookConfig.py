"""
AudiobookConfig.py - Voice profile configuration loader for Audiobook skill.
"""
import json
import os
from pathlib import Path
from typing import Dict


class AudiobookConfig:
    """Singleton configuration loader for audiobook voice profiles."""
    
    _instance = None
    _profiles = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudiobookConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._profiles is None:
            self._load_profiles()

    def _load_profiles(self) -> None:
        """Load voice profiles from configuration file or environment."""
        config_path = Path(__file__).parent.parent / "voice_profiles.json"

        if config_path.exists():
            with open(config_path, 'r') as f:
                self._profiles = json.load(f)

            for profile_type, profile in self._profiles.items():
                self._validate_profile(profile, profile_type)
        else:
            self._profiles = self._get_fallback_profiles()

    def _validate_profile(self, profile: Dict, profile_type: str) -> None:
        """Validate voice profile configuration.
        
        Args:
            profile: Profile configuration dictionary
            profile_type: Profile type name
            
        Raises:
            ValueError: If profile configuration is invalid
        """
        # Add default provider if not specified (backward compatibility)
        if "provider" not in profile:
            profile["provider"] = "gemini"
        
        required_fields = ["voice_id", "model", "speed"]
        
        # Provider-specific validation
        provider = profile.get("provider", "gemini")
        if provider == "elevenlabs":
            required_fields.extend(["stability", "similarity_boost", "style"])

        for field in required_fields:
            if field not in profile:
                raise ValueError(f"Profile '{profile_type}' missing required field: {field}")

        if not (0.7 <= profile["speed"] <= 1.2):
            raise ValueError(f"Profile '{profile_type}': speed must be between 0.7 and 1.2")

        # ElevenLabs-specific parameter validation
        if provider == "elevenlabs":
            for param in ["stability", "similarity_boost", "style"]:
                if not (0.0 <= profile[param] <= 1.0):
                    raise ValueError(f"Profile '{profile_type}': {param} must be between 0.0 and 1.0")

    def _get_fallback_profiles(self) -> Dict:
        """Get fallback profile configuration from environment.
        
        Returns:
            Dictionary of fallback profiles
            
        Raises:
            ValueError: If GEMINI_API_KEY not set
        """
        # Check for Gemini API key (new default)
        if os.getenv("GEMINI_API_KEY"):
            return {
                "audiobook": {
                    "provider": "gemini",
                    "voice_id": "Puck",
                    "voice_name": "Puck",
                    "language": "English",
                    "model": "gemini-2.5-flash-preview-tts",
                    "speed": 1.0,
                }
            }
        
        # Fallback to ElevenLabs for backward compatibility
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        if voice_id:
            return {
                "audiobook": {
                    "provider": "elevenlabs",
                    "voice_id": voice_id,
                    "voice_name": "Default Voice",
                    "language": "English",
                    "model": "eleven_turbo_v2_5",
                    "speed": 0.95,
                    "stability": 0.65,
                    "similarity_boost": 0.85,
                    "style": 0.20
                }
            }
        
        raise ValueError(
            "No voice_profiles.json found and no API key configured. "
            "Set GEMINI_API_KEY or ELEVENLABS_VOICE_ID environment variable."
        )

    def get_profile(self, profile_type: str = "audiobook") -> Dict:
        """Get voice profile configuration.
        
        Args:
            profile_type: Type of profile to retrieve
            
        Returns:
            Profile configuration dictionary
            
        Raises:
            ValueError: If profile type not found
        """
        if profile_type not in self._profiles:
            available = ", ".join(self._profiles.keys())
            raise ValueError(f"Unknown profile type '{profile_type}'. Available: {available}")

        profile = self._profiles[profile_type].copy()
        
        # Add default provider if not specified (backward compatibility)
        if "provider" not in profile:
            profile["provider"] = "gemini"
        
        return profile

    def get_voice_settings(self, profile_type: str = "audiobook") -> Dict:
        """Get ElevenLabs voice settings for profile.
        
        Args:
            profile_type: Type of profile to use
            
        Returns:
            Voice settings dictionary for ElevenLabs API
        """
        profile = self.get_profile(profile_type)

        return {
            "stability": profile["stability"],
            "similarity_boost": profile["similarity_boost"],
            "style": profile["style"],
            "speed": profile["speed"],
            "use_speaker_boost": True
        }

    def get_available_profiles(self) -> list:
        """Get list of available profile types.
        
        Returns:
            List of profile type names
        """
        return list(self._profiles.keys())
