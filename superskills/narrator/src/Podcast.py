"""
Podcast.py - Multi-segment podcast generation for CoachSteff AI voice.
"""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from elevenlabs.client import ElevenLabs

from .VoiceConfig import VoiceConfig

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available - audio stitching will be disabled")

@dataclass
class PodcastSegment:
    text: str
    content_type: str = "podcast"
    profile_type: Optional[str] = None
    voice_name: str = "CoachSteff"
    output_filename: Optional[str] = None

    def __post_init__(self):
        if not self.output_filename:
            self.output_filename = f"segment_{id(self)}.mp3"

class PodcastGenerator:
    CONTENT_TYPE_TO_PROFILE = {
        "educational": "narration",
        "marketing": "narration",
        "podcast": "podcast",
        "meditation": "meditation",
    }

    def __init__(self, api_key: Optional[str] = None, output_dir: str = "output", profile_type: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found")

        self.voice_config = VoiceConfig()
        self.profile_type = profile_type or "podcast"

        self.client = ElevenLabs(api_key=self.api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_segment(self, segment: PodcastSegment) -> str:
        profile_to_use = segment.profile_type or self.CONTENT_TYPE_TO_PROFILE.get(segment.content_type, self.profile_type)

        profile = self.voice_config.get_profile(profile_to_use)
        voice_settings = self.voice_config.get_voice_settings(profile_to_use)
        model = profile["model"]
        voice_id = profile["voice_id"]

        audio_generator = self.client.text_to_speech.convert(
            voice_id=voice_id,
            text=segment.text,
            model_id=model,
            voice_settings=voice_settings
        )

        output_path = self.output_dir / segment.output_filename

        with open(output_path, 'wb') as f:
            for chunk in audio_generator:
                f.write(chunk)

        return str(output_path)

    def stitch_segments(self, audio_files: List[str], output_filename: str, transition_ms: int = 500) -> str:
        if not PYDUB_AVAILABLE:
            raise ImportError("pydub is required for audio stitching. Segments saved individually.")

        combined = AudioSegment.empty()
        silence = AudioSegment.silent(duration=transition_ms)
        for audio_file in audio_files:
            segment = AudioSegment.from_mp3(audio_file)
            combined += segment + silence
        output_path = self.output_dir / output_filename
        combined.export(output_path, format="mp3", bitrate="320k")
        return str(output_path)

    def generate_podcast(self, segments: List[PodcastSegment], output_filename: str = "podcast.mp3", transition_ms: int = 500) -> Dict:
        print(f"Generating {len(segments)} segments...")
        segment_files = []
        for i, segment in enumerate(segments, 1):
            print(f"  [{i}/{len(segments)}] Generating segment...")
            file_path = self.generate_segment(segment)
            segment_files.append(file_path)
        print("Stitching segments together...")
        final_path = self.stitch_segments(segment_files, output_filename, transition_ms)
        metadata = {
            "output_file": final_path,
            "segments": len(segments),
            "segment_files": segment_files,
        }
        metadata_path = self.output_dir / f"{Path(output_filename).stem}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Podcast generated: {final_path}")
        return metadata
