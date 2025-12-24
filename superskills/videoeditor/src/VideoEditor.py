"""
VideoEditor.py - Automated video editing using FFmpeg.
"""
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class VideoEditResult:
    """Result from a video editing operation."""
    input_file: str
    output_file: str
    edit_type: str
    duration_seconds: float
    file_size_mb: float
    resolution: str
    processing_time_seconds: float
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class VideoEditor:
    """Automated video editing using FFmpeg."""

    # Platform presets
    PLATFORM_PRESETS = {
        "youtube_short": {"width": 1080, "height": 1920, "max_duration": 60},
        "linkedin_video": {"width": 1280, "height": 720, "max_size_mb": 200},
        "instagram_reel": {"width": 1080, "height": 1920, "max_duration": 90},
        "twitter": {"width": 1280, "height": 720, "max_duration": 140},
        "facebook": {"width": 1280, "height": 720, "max_duration": 240},
    }

    def __init__(
        self,
        output_dir: str = "output/videos",
        verbose: bool = True
    ):
        """Initialize VideoEditor.

        Args:
            output_dir: Directory to save edited videos
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose

        # Check if ffmpeg is available
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg not found. Please install: brew install ffmpeg")

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def clip_highlights(
        self,
        video_path: str,
        timestamps: List[Tuple[float, float]],
        output_name: Optional[str] = None
    ) -> List[VideoEditResult]:
        """Extract clips from video at specified timestamps.

        Args:
            video_path: Path to source video
            timestamps: List of (start_seconds, end_seconds) tuples
            output_name: Base name for output clips

        Returns:
            List of VideoEditResult objects
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        if self.verbose:
            print(f"Extracting {len(timestamps)} clips from {video_path.name}")

        results = []
        base_name = output_name or video_path.stem

        for i, (start, end) in enumerate(timestamps, 1):
            output_file = self.output_dir / f"{base_name}_clip{i:02d}.mp4"

            start_time = datetime.now()
            self._run_ffmpeg([
                "-i", str(video_path),
                "-ss", str(start),
                "-to", str(end),
                "-c", "copy",
                str(output_file)
            ])

            processing_time = (datetime.now() - start_time).total_seconds()
            duration = end - start
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            resolution = self._get_resolution(str(output_file))

            results.append(VideoEditResult(
                input_file=str(video_path),
                output_file=str(output_file),
                edit_type="clip",
                duration_seconds=duration,
                file_size_mb=file_size_mb,
                resolution=resolution,
                processing_time_seconds=processing_time
            ))

            if self.verbose:
                print(f"  ✓ Clip {i}: {duration:.1f}s → {output_file.name}")

        return results

    def add_intro_outro(
        self,
        video_path: str,
        intro_path: Optional[str] = None,
        outro_path: Optional[str] = None,
        output_name: Optional[str] = None
    ) -> VideoEditResult:
        """Add intro and/or outro to video.

        Args:
            video_path: Path to main video
            intro_path: Path to intro video (optional)
            outro_path: Path to outro video (optional)
            output_name: Output filename

        Returns:
            VideoEditResult
        """
        video_path = Path(video_path)
        output_file = self.output_dir / (output_name or f"{video_path.stem}_branded.mp4")

        # Create concat file
        concat_file = self.output_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            if intro_path:
                f.write(f"file '{Path(intro_path).absolute()}'\n")
            f.write(f"file '{video_path.absolute()}'\n")
            if outro_path:
                f.write(f"file '{Path(outro_path).absolute()}'\n")

        start_time = datetime.now()
        self._run_ffmpeg([
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_file)
        ])

        processing_time = (datetime.now() - start_time).total_seconds()

        # Clean up
        concat_file.unlink()

        return VideoEditResult(
            input_file=str(video_path),
            output_file=str(output_file),
            edit_type="add_intro_outro",
            duration_seconds=self._get_duration(str(output_file)),
            file_size_mb=output_file.stat().st_size / (1024 * 1024),
            resolution=self._get_resolution(str(output_file)),
            processing_time_seconds=processing_time
        )

    def generate_preview(
        self,
        video_path: str,
        duration: int = 30,
        from_start: bool = True,
        output_name: Optional[str] = None
    ) -> VideoEditResult:
        """Generate preview clip from video.

        Args:
            video_path: Path to source video
            duration: Preview duration in seconds
            from_start: If True, clip from start; else from middle
            output_name: Output filename

        Returns:
            VideoEditResult
        """
        video_path = Path(video_path)
        output_file = self.output_dir / (output_name or f"{video_path.stem}_preview.mp4")

        total_duration = self._get_duration(str(video_path))
        start_time_offset = 0 if from_start else max(0, (total_duration - duration) / 2)

        start_time = datetime.now()
        self._run_ffmpeg([
            "-i", str(video_path),
            "-ss", str(start_time_offset),
            "-t", str(duration),
            "-c", "copy",
            str(output_file)
        ])

        processing_time = (datetime.now() - start_time).total_seconds()

        return VideoEditResult(
            input_file=str(video_path),
            output_file=str(output_file),
            edit_type="preview",
            duration_seconds=duration,
            file_size_mb=output_file.stat().st_size / (1024 * 1024),
            resolution=self._get_resolution(str(output_file)),
            processing_time_seconds=processing_time
        )

    def resize_for_platform(
        self,
        video_path: str,
        platform: str,
        output_name: Optional[str] = None
    ) -> VideoEditResult:
        """Resize video for social media platform.

        Args:
            video_path: Path to source video
            platform: Platform name (youtube_short, linkedin_video, etc.)
            output_name: Output filename

        Returns:
            VideoEditResult
        """
        if platform not in self.PLATFORM_PRESETS:
            raise ValueError(f"Unknown platform: {platform}. Choose from: {list(self.PLATFORM_PRESETS.keys())}")

        video_path = Path(video_path)
        preset = self.PLATFORM_PRESETS[platform]
        output_file = self.output_dir / (output_name or f"{video_path.stem}_{platform}.mp4")

        resolution = f"{preset['width']}x{preset['height']}"

        start_time = datetime.now()
        self._run_ffmpeg([
            "-i", str(video_path),
            "-vf", f"scale={preset['width']}:{preset['height']}:force_original_aspect_ratio=decrease,pad={preset['width']}:{preset['height']}:-1:-1:color=black",
            "-c:a", "copy",
            str(output_file)
        ])

        processing_time = (datetime.now() - start_time).total_seconds()

        return VideoEditResult(
            input_file=str(video_path),
            output_file=str(output_file),
            edit_type=f"resize_{platform}",
            duration_seconds=self._get_duration(str(output_file)),
            file_size_mb=output_file.stat().st_size / (1024 * 1024),
            resolution=resolution,
            processing_time_seconds=processing_time
        )

    def add_captions(
        self,
        video_path: str,
        srt_file: str,
        output_name: Optional[str] = None
    ) -> VideoEditResult:
        """Burn captions into video.

        Args:
            video_path: Path to source video
            srt_file: Path to SRT subtitle file
            output_name: Output filename

        Returns:
            VideoEditResult
        """
        video_path = Path(video_path)
        srt_file = Path(srt_file)
        output_file = self.output_dir / (output_name or f"{video_path.stem}_captioned.mp4")

        start_time = datetime.now()
        self._run_ffmpeg([
            "-i", str(video_path),
            "-vf", f"subtitles={srt_file}",
            str(output_file)
        ])

        processing_time = (datetime.now() - start_time).total_seconds()

        return VideoEditResult(
            input_file=str(video_path),
            output_file=str(output_file),
            edit_type="add_captions",
            duration_seconds=self._get_duration(str(output_file)),
            file_size_mb=output_file.stat().st_size / (1024 * 1024),
            resolution=self._get_resolution(str(output_file)),
            processing_time_seconds=processing_time
        )

    def _run_ffmpeg(self, args: List[str]):
        """Run FFmpeg command."""
        cmd = ["ffmpeg", "-y"] + args

        if not self.verbose:
            cmd.extend(["-loglevel", "error"])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")

    def _get_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ],
            capture_output=True,
            text=True
        )
        return float(result.stdout.strip())

    def _get_resolution(self, video_path: str) -> str:
        """Get video resolution."""
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=s=x:p=0",
                video_path
            ],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
