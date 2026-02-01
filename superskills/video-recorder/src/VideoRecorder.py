"""VideoRecorder - Main orchestrator for video generation pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import json

from .SlideRenderer import SlideRenderer
from .AudioGenerator import AudioGenerator
from .TimingSync import TimingSync
from .VideoEncoder import VideoEncoder


@dataclass
class VideoResult:
    """Result of video generation."""
    video_path: Path
    duration_seconds: float
    slide_count: int
    audio_path: Path
    frames_path: Path
    metadata: Dict


class VideoRecorder:
    """Main orchestrator for video generation pipeline."""
    
    def __init__(
        self,
        output_dir: str = "output/videos",
        resolution: tuple = (1920, 1080),
        fps: int = 1,
        voice: str = "steff",
        profile_type: str = "podcast"
    ):
        """
        Initialize video recorder.
        
        Args:
            output_dir: Where to save generated videos
            resolution: Output resolution (width, height)
            fps: Frames per second (1 for static slides)
            voice: Voice identifier for TTS
            profile_type: Narrator profile type
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.renderer = SlideRenderer(resolution=resolution)
        self.audio_gen = AudioGenerator(voice=voice, profile_type=profile_type)
        self.timing = TimingSync()
        self.encoder = VideoEncoder(fps=fps)
    
    def create_video(
        self,
        script: str,
        slides: List[Dict],
        output_name: str,
        brand_config: Optional[Path] = None
    ) -> VideoResult:
        """
        Full video generation pipeline.
        
        Args:
            script: Narration text for voiceover
            slides: List of slide definitions (type, heading, bullets, etc.)
            output_name: Output filename without extension
            brand_config: Path to custom brand.yaml (optional)
        
        Returns:
            VideoResult with paths and metadata
        """
        print(f"🎬 Video Recorder: Generating '{output_name}'")
        print(f"   Slides: {len(slides)}, Script: {len(script)} chars")
        
        # Setup work directory
        work_dir = self.output_dir / f".{output_name}_work"
        work_dir.mkdir(exist_ok=True)
        
        try:
            # Step 1: Generate voiceover
            print("\n1️⃣  Generating voiceover...")
            audio_path = work_dir / "audio.mp3"
            self.audio_gen.generate(script, audio_path)
            duration = self.audio_gen.get_duration(audio_path)
            print(f"   ✓ Audio generated: {duration:.1f}s")
            
            # Step 2: Render slides to frames
            print("\n2️⃣  Rendering slides to PNG frames...")
            frames_dir = work_dir / "frames"
            frames_dir.mkdir(exist_ok=True)
            self.renderer.output_dir = frames_dir
            frames = self.renderer.render_slides(slides)
            print(f"   ✓ {len(frames)} frames rendered")
            
            # Step 3: Calculate timing
            print("\n3️⃣  Calculating slide timing...")
            timed_slides = self.timing.auto_timing(slides, audio_path)
            for ts in timed_slides:
                print(f"   Slide {ts.slide_index}: {ts.duration_ms/1000:.1f}s")
            
            # Step 4: Encode video
            print("\n4️⃣  Encoding video with FFmpeg...")
            output_path = self.output_dir / f"{output_name}.mp4"
            self.encoder.encode_complete(frames, audio_path, timed_slides, output_path)
            print(f"   ✓ Video encoded: {output_path}")
            
            # Step 5: Build result
            result = VideoResult(
                video_path=output_path,
                duration_seconds=duration,
                slide_count=len(slides),
                audio_path=audio_path,
                frames_path=frames_dir,
                metadata={
                    "resolution": f"{self.renderer.width}x{self.renderer.height}",
                    "fps": self.encoder.fps,
                    "voice": self.audio_gen.voice,
                    "profile_type": self.audio_gen.profile_type
                }
            )
            
            print(f"\n✅ Video generation complete!")
            print(f"   Output: {result.video_path}")
            print(f"   Duration: {result.duration_seconds:.1f}s")
            
            return result
        
        except Exception as e:
            print(f"\n❌ Video generation failed: {e}")
            raise
    
    def __call__(self, input_data: str, **kwargs) -> str:
        """
        CLI entry point for superskills framework.
        
        Expects JSON input with:
        - script: str
        - slides: List[Dict]
        - output_name: str (optional)
        
        Args:
            input_data: JSON string or plain text script
            **kwargs: Additional arguments from framework (ignored)
        
        Returns:
            JSON string with result
        """
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            # Treat as plain script with single title slide
            data = {
                "script": input_data,
                "slides": [{"type": "title", "heading": input_data.split('.')[0][:50]}]
            }
        
        script = data.get('script', '')
        slides = data.get('slides', [])
        output_name = data.get('output_name', 'video_output')
        
        if not script:
            raise ValueError("No script provided")
        if not slides:
            raise ValueError("No slides provided")
        
        result = self.create_video(
            script=script,
            slides=slides,
            output_name=output_name
        )
        
        return json.dumps({
            'video_path': str(result.video_path),
            'duration_seconds': result.duration_seconds,
            'slide_count': result.slide_count,
            'audio_path': str(result.audio_path),
            'metadata': result.metadata
        }, indent=2)
