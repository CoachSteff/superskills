"""AudioGenerator - Voice generation via ElevenLabs for video-recorder skill."""

from pathlib import Path
import subprocess
from typing import Optional


class AudioGenerator:
    """Generate voiceover audio using ElevenLabs via narrator skill."""
    
    def __init__(
        self,
        voice: str = "steff",
        profile_type: str = "podcast"
    ):
        """
        Initialize audio generator.
        
        Args:
            voice: Voice identifier (default: "steff")
            profile_type: Narrator profile (podcast, meditation, educational, etc.)
        """
        self.voice = voice
        self.profile_type = profile_type
    
    def generate(
        self,
        script: str,
        output_path: Path
    ) -> Path:
        """
        Generate audio from script using narrator skill.
        
        This wraps the existing narrator skill rather than
        reimplementing ElevenLabs integration.
        
        Args:
            script: Text to convert to speech
            output_path: Where to save audio file
        
        Returns:
            Path to generated audio file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to use narrator skill directly
        try:
            from superskills.narrator.src import VoiceoverGenerator
            
            voiceover = VoiceoverGenerator(
                output_dir=str(output_path.parent),
                profile_type=self.profile_type
            )
            
            result = voiceover.generate(
                script=script,
                output_filename=output_path.name
            )
            
            return Path(result['output_file'])
        
        except ImportError:
            # Fallback to CLI call if direct import fails
            subprocess.run([
                'superskills', 'call', f'narrator-{self.profile_type}',
                script,
                '--output', str(output_path)
            ], check=True)
            
            return output_path
    
    def get_duration(self, audio_path: Path) -> float:
        """
        Get audio duration in seconds using ffprobe.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Duration in seconds
        """
        result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_path)
        ], capture_output=True, text=True, check=True)
        
        return float(result.stdout.strip())
