"""
VoiceConfig.py - Voice profile configuration loader for Narrator skill.
"""
import json
import os
from pathlib import Path
from typing import Dict


class VoiceConfig:
    _instance = None
    _profiles = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoiceConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._profiles is None:
            self._load_profiles()

    def _load_profiles(self) -> None:
        config_path = Path(__file__).parent.parent / "voice_profiles.json"

        if config_path.exists():
            with open(config_path, 'r') as f:
                self._profiles = json.load(f)

            for profile_type, profile in self._profiles.items():
                if profile_type.startswith("_"):
                    continue
                self._validate_profile(profile, profile_type)
        else:
            self._profiles = self._get_fallback_profiles()

    def _validate_profile(self, profile: Dict, profile_type: str) -> None:
        required_fields = ["voice_id", "model", "speed", "stability", "similarity_boost", "style"]

        for field in required_fields:
            if field not in profile:
                raise ValueError(f"Profile '{profile_type}' missing required field: {field}")

        if not (0.7 <= profile["speed"] <= 1.2):
            raise ValueError(f"Profile '{profile_type}': speed must be between 0.7 and 1.2")

        for param in ["stability", "similarity_boost", "style"]:
            if not (0.0 <= profile[param] <= 1.0):
                raise ValueError(f"Profile '{profile_type}': {param} must be between 0.0 and 1.0")

    def _get_fallback_profiles(self) -> Dict:
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        if not voice_id:
            raise ValueError("No voice_profiles.json found and ELEVENLABS_VOICE_ID not set")

        return {
            "narration": {
                "voice_id": voice_id,
                "voice_name": "Default Voice",
                "language": "English",
                "model": "eleven_turbo_v2_5",
                "speed": 1.0,
                "stability": 0.70,
                "similarity_boost": 0.80,
                "style": 0.30
            },
            "podcast": {
                "voice_id": voice_id,
                "voice_name": "Default Voice",
                "language": "English",
                "model": "eleven_turbo_v2_5",
                "speed": 1.0,
                "stability": 0.75,
                "similarity_boost": 0.85,
                "style": 0.35
            },
            "meditation": {
                "voice_id": voice_id,
                "voice_name": "Default Voice",
                "language": "English",
                "model": "eleven_flash_v2_5",
                "speed": 0.95,
                "stability": 0.12,
                "similarity_boost": 0.97,
                "style": 0.97
            }
        }

    def get_profile(self, profile_type: str) -> Dict:
        if profile_type not in self._profiles:
            available = ", ".join(self._profiles.keys())
            raise ValueError(f"Unknown profile type '{profile_type}'. Available: {available}")

        return self._profiles[profile_type].copy()

    def get_voice_settings(self, profile_type: str) -> Dict:
        profile = self.get_profile(profile_type)

        return {
            "stability": profile["stability"],
            "similarity_boost": profile["similarity_boost"],
            "style": profile["style"],
            "speed": profile["speed"],
            "use_speaker_boost": True
        }

    def get_available_profiles(self) -> list:
        return list(self._profiles.keys())
