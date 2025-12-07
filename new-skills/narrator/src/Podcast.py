"""
Podcast.py - Multi-segment podcast generation for CoachSteff AI voice.
"""
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import json

from elevenlabs.client import ElevenLabs

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
    voice_name: str = "CoachSteff"
    output_filename: Optional[str] = None
    
    def __post_init__(self):
        if not self.output_filename:
            self.output_filename = f"segment_{id(self)}.mp3"

class PodcastGenerator:
    # Voice settings by content type (for ElevenLabs v2)
    VOICE_SETTINGS = {
        "podcast": {"stability": 0.75, "similarity_boost": 0.85, "style": 0.35, "use_speaker_boost": True},
        "educational": {"stability": 0.70, "similarity_boost": 0.80, "style": 0.30, "use_speaker_boost": True},
        "marketing": {"stability": 0.65, "similarity_boost": 0.75, "style": 0.40, "use_speaker_boost": True},
    }
    
    def __init__(self, api_key: Optional[str] = None, output_dir: str = "output"):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found")
        
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        if not self.voice_id:
            raise ValueError("ELEVENLABS_VOICE_ID not found")
        
        self.client = ElevenLabs(api_key=self.api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_segment(self, segment: PodcastSegment) -> str:
        settings = self.VOICE_SETTINGS.get(segment.content_type, self.VOICE_SETTINGS["podcast"])
        
        # Use ElevenLabs v2 API
        audio_generator = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=segment.text,
            model_id="eleven_turbo_v2_5",  # Changed: stock voices don't support multilingual_v2
            voice_settings=settings
        )
        
        output_path = self.output_dir / segment.output_filename
        
        # Write audio to file
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
