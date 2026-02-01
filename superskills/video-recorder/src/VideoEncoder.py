"""VideoEncoder - FFmpeg wrapper for video-recorder skill."""

import subprocess
from pathlib import Path
from typing import List
from .TimingSync import TimedSlide


class VideoEncoder:
    """Encode video from frames and audio using FFmpeg."""
    
    def __init__(
        self,
        fps: int = 1,  # 1 FPS for static slides (MVP)
        quality: str = "high"
    ):
        """
        Initialize video encoder.
        
        Args:
            fps: Frames per second (1 for static slides)
            quality: Encoding quality (low/medium/high)
        """
        self.fps = fps
        self.crf = {"low": 28, "medium": 23, "high": 18}[quality]
    
    def encode_complete(
        self,
        frames: List[Path],
        audio: Path,
        timing: List[TimedSlide],
        output: Path
    ) -> Path:
        """
        Encode final video from frames and audio.
        
        Uses filter_complex to properly time each frame as a "slide"
        that displays for its specified duration.
        
        Args:
            frames: List of PNG frame paths
            audio: Path to audio file
            timing: List of TimedSlide objects with durations
            output: Where to save final video
        
        Returns:
            Path to encoded video
        """
        output.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Build filter_complex for concatenating timed frames
            # Each frame displays for its duration
            inputs = []
            filter_parts = []
            
            for i, (frame, timed) in enumerate(zip(frames, timing)):
                inputs.extend(['-loop', '1', '-t', str(timed.duration_ms / 1000.0), '-i', str(frame)])
                filter_parts.append(f"[{i}:v]")
            
            # Concat all frames
            filter_complex = f"{''.join(filter_parts)}concat=n={len(frames)}:v=1:a=0[v]"
            
            # Add audio input
            inputs.extend(['-i', str(audio)])
            
            # Encode with proper timing
            cmd = ['ffmpeg', '-y'] + inputs + [
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-map', f'{len(frames)}:a',  # Audio is the last input
                '-c:v', 'libx264',
                '-crf', str(self.crf),
                '-preset', 'medium',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                str(output)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            return output
        
        except Exception as e:
            raise RuntimeError(f"Video encoding failed: {e}")
