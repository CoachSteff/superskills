"""
Voiceover.py - Single-segment voiceover generation for CoachSteff AI voice.
"""
import os
import re
from typing import Optional, Dict, Literal
from pathlib import Path
from datetime import datetime

from elevenlabs.client import ElevenLabs

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available - audio metadata will be skipped")

ContentType = Literal["educational", "marketing", "social", "podcast"]

class ScriptOptimizer:
    @staticmethod
    def optimize_for_speech(text: str) -> str:
        optimized = re.sub(r'\([^)]*\)', '', text)
        optimized = re.sub(r'\[[^\]]*\]', '', optimized)
        optimized = optimized.replace('—', '...').replace(' - ', '... ').replace(':', '...')
        optimized = re.sub(r'\s+', ' ', optimized)
        return optimized.strip()
    
    @staticmethod
    def add_pronunciation_guide(text: str, custom_pronunciations: Optional[Dict[str, str]] = None) -> str:
        pronunciations = {
            "ElevenLabs": "Eleven Labs",
            "API": "A-P-I",
            "AI": "A-I",
            "ChatGPT": "Chat-G-P-T",
            "LLM": "L-L-M",
        }
        if custom_pronunciations:
            pronunciations.update(custom_pronunciations)
        result = text
        for term, pronunciation in pronunciations.items():
            result = result.replace(term, pronunciation)
        return result

class VoiceoverGenerator:
    # Voice settings by content type (for ElevenLabs v2)
    VOICE_SETTINGS = {
        "educational": {"stability": 0.70, "similarity_boost": 0.80, "style": 0.30, "use_speaker_boost": True},
        "marketing": {"stability": 0.65, "similarity_boost": 0.75, "style": 0.40, "use_speaker_boost": True},
        "social": {"stability": 0.60, "similarity_boost": 0.75, "style": 0.45, "use_speaker_boost": True},
        "podcast": {"stability": 0.75, "similarity_boost": 0.85, "style": 0.35, "use_speaker_boost": True},
    }
    
    MODELS = {
        "educational": "eleven_turbo_v2_5",  # Changed: stock voices don't support multilingual_v2
        "marketing": "eleven_turbo_v2_5",
        "social": "eleven_turbo_v2_5",
        "podcast": "eleven_turbo_v2_5",  # Changed: stock voices don't support multilingual_v2
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
        self.optimizer = ScriptOptimizer()
        
    def generate(self, script: str, content_type: ContentType = "educational", optimize_script: bool = True, custom_pronunciations: Optional[Dict[str, str]] = None, output_filename: Optional[str] = None) -> Dict:
        processed_script = script
        if optimize_script:
            processed_script = self.optimizer.optimize_for_speech(script)
            processed_script = self.optimizer.add_pronunciation_guide(processed_script, custom_pronunciations)
        
        settings = self.VOICE_SETTINGS[content_type]
        model = self.MODELS[content_type]
        
        print(f"Generating {content_type} voiceover with {model}...")
        
        # Use ElevenLabs v2 API - try with fallback models
        from elevenlabs.core.api_error import ApiError
        
        models_to_try = [model, "eleven_monolingual_v1", "eleven_flash_v2_5"]
        chunks = []
        success_model = None
        
        for model_attempt in models_to_try:
            try:
                audio_generator = self.client.text_to_speech.convert(
                    voice_id=self.voice_id,
                    text=processed_script,
                    model_id=model_attempt,
                    voice_settings=settings
                )
                # Collect all chunks
                chunks = []
                for chunk in audio_generator:
                    chunks.append(chunk)
                
                if chunks:
                    print(f"  ✓ Using model: {model_attempt}")
                    success_model = model_attempt
                    break
            except ApiError as e:
                if "voice_not_fine_tuned" in str(e) or "not fine-tuned" in str(e):
                    print(f"  ! {model_attempt} not compatible, trying next model...")
                    continue
                else:
                    raise
        
        if not chunks or not success_model:
            raise ValueError(f"Voice ID {self.voice_id} is not compatible with any available models")
        
        model = success_model  # Update model name for metadata
        
        # Generate filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            output_filename = f"{timestamp}-{content_type}-voiceover.mp3"
        
        output_path = self.output_dir / output_filename
        
        # Write audio chunks to file
        with open(output_path, 'wb') as f:
            for chunk in chunks:
                f.write(chunk)
        
        # Get audio metadata (if pydub available)
        word_count = len(processed_script.split())
        
        if PYDUB_AVAILABLE:
            try:
                audio_segment = AudioSegment.from_mp3(output_path)
                duration_seconds = audio_segment.duration_seconds
                wpm = int((word_count / duration_seconds) * 60) if duration_seconds > 0 else 0
                
                print(f"✓ Generated: {output_path} | Duration: {duration_seconds:.1f}s | WPM: {wpm}")
                
                return {
                    "output_file": str(output_path),
                    "content_type": content_type,
                    "model": model,
                    "duration_seconds": round(duration_seconds, 2),
                    "word_count": word_count,
                    "words_per_minute": wpm,
                    "optimized": optimize_script,
                }
            except Exception as e:
                print(f"✓ Generated: {output_path} (metadata calculation failed: {e})")
        else:
            print(f"✓ Generated: {output_path}")
        
        # Return without metadata if pydub unavailable
        return {
            "output_file": str(output_path),
            "content_type": content_type,
            "model": model,
            "word_count": word_count,
            "optimized": optimize_script,
        }
