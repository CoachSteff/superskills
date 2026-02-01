"""TimingSync - Slide-audio synchronization for video-recorder skill."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
import subprocess


@dataclass
class TimedSlide:
    """Represents a slide with timing information."""
    slide_index: int
    start_ms: int
    duration_ms: int
    slide_data: Dict


class TimingSync:
    """Synchronize slides with audio timing."""
    
    def auto_timing(
        self,
        slides: List[Dict],
        audio_path: Path
    ) -> List[TimedSlide]:
        """
        Distribute slides evenly across audio duration.
        
        Simple strategy for MVP: divide audio into equal segments.
        Future: parse script for natural breaks, use silence detection.
        
        Args:
            slides: List of slide definitions
            audio_path: Path to audio file
        
        Returns:
            List of TimedSlide objects with timing information
        """
        total_duration_ms = int(self._get_duration_ms(audio_path))
        num_slides = len(slides)
        
        if num_slides == 0:
            return []
        
        # Equal distribution
        duration_per_slide = total_duration_ms // num_slides
        
        timed_slides = []
        for i, slide_data in enumerate(slides):
            # Allow explicit duration override
            duration_ms = slide_data.get('duration_ms', duration_per_slide)
            start_ms = i * duration_per_slide
            
            timed_slides.append(TimedSlide(
                slide_index=i,
                start_ms=start_ms,
                duration_ms=duration_ms,
                slide_data=slide_data
            ))
        
        return timed_slides
    
    def _get_duration_ms(self, audio_path: Path) -> float:
        """Get audio duration in milliseconds using ffprobe."""
        result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(audio_path)
        ], capture_output=True, text=True, check=True)
        
        return float(result.stdout.strip()) * 1000
