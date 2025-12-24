"""
LocalTranscriber.py - Privacy-focused offline transcription using local Whisper models.
"""
import json
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

try:
    import torch
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    warnings.warn(
        "openai-whisper not available. Install with: pip install openai-whisper"
    )


OutputFormat = Literal["txt", "json", "srt", "vtt"]
ModelSize = Literal["tiny", "base", "small", "medium", "large"]


@dataclass
class TranscriptionResult:
    """Result from a transcription operation."""
    source_file: str
    transcript: str
    language: str
    duration_seconds: float
    word_count: int
    timestamps: Optional[List[Dict]] = None
    confidence: float = 1.0
    output_file: str = ""
    timestamp: str = None
    model_size: str = "small"
    device: str = "cpu"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class LocalTranscriber:
    """Privacy-focused offline transcription using local Whisper models."""

    def __init__(
        self,
        output_dir: str = "transcripts",
        model_size: ModelSize = "small",
        device: Optional[str] = None,
        verbose: bool = True
    ):
        """Initialize LocalTranscriber.
        
        Args:
            output_dir: Directory to save transcripts
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (cuda, cpu, mps). Auto-detect if None
            verbose: Enable verbose logging
        """
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "openai-whisper is required. Install with:\n"
                "  pip install openai-whisper\n"
                "For GPU support:\n"
                "  pip install openai-whisper[cuda]  # NVIDIA\n"
                "  pip install openai-whisper[metal] # Apple Silicon"
            )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_size = model_size
        self.verbose = verbose

        # Auto-detect best device if not specified
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = "mps"  # Apple Silicon
            else:
                self.device = "cpu"
        else:
            self.device = device

        # Load model (will download on first use, then cache)
        if self.verbose:
            print(f"Loading Whisper {model_size} model on {self.device}...")

        self.model = whisper.load_model(model_size, device=self.device)

        if self.verbose:
            print(f"✓ Model loaded: {model_size} on {self.device}")

    def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        include_timestamps: bool = False,
        output_format: OutputFormat = "txt"
    ) -> TranscriptionResult:
        """Transcribe audio/video file locally.
        
        Args:
            file_path: Path to audio/video file
            language: Language code (e.g., 'en', 'es'). Auto-detect if None
            include_timestamps: Include word-level timestamps
            output_format: Output format (txt, json, srt, vtt)
            
        Returns:
            TranscriptionResult with transcript and metadata
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if self.verbose:
            print(f"Transcribing: {file_path.name}")

        # Transcribe with Whisper
        options = {
            "verbose": self.verbose,
            "word_timestamps": include_timestamps
        }
        if language:
            options["language"] = language

        result = self.model.transcribe(str(file_path), **options)

        # Extract timestamps if requested
        timestamps_data = None
        if include_timestamps and "segments" in result:
            timestamps_data = []
            for segment in result["segments"]:
                if "words" in segment:
                    for word_info in segment["words"]:
                        timestamps_data.append({
                            "word": word_info.get("word", "").strip(),
                            "start": word_info.get("start", 0.0),
                            "end": word_info.get("end", 0.0)
                        })
                else:
                    # Segment-level timestamps as fallback
                    timestamps_data.append({
                        "text": segment.get("text", "").strip(),
                        "start": segment.get("start", 0.0),
                        "end": segment.get("end", 0.0)
                    })

        # Calculate metadata
        transcript_text = result["text"].strip()
        word_count = len(transcript_text.split())
        detected_language = result.get("language", language or "unknown")

        # Estimate duration (Whisper doesn't always provide it)
        try:
            import librosa
            audio, sr = librosa.load(str(file_path), sr=None)
            duration = len(audio) / sr
        except (ImportError, IOError, OSError, Exception):
            # Fallback: estimate from segments if librosa unavailable or audio load fails
            if "segments" in result and result["segments"]:
                duration = result["segments"][-1].get("end", 0.0)
            else:
                duration = 0.0

        # Create result
        transcription_result = TranscriptionResult(
            source_file=str(file_path),
            transcript=transcript_text,
            language=detected_language,
            duration_seconds=duration,
            word_count=word_count,
            timestamps=timestamps_data,
            confidence=1.0,  # Whisper doesn't provide confidence scores
            model_size=self.model_size,
            device=self.device
        )

        # Save output
        output_file = self._save_output(transcription_result, output_format)
        transcription_result.output_file = output_file

        if self.verbose:
            print(f"✓ Transcribed {word_count} words in {detected_language}")
            print(f"  Saved to: {output_file}")

        return transcription_result

    def transcribe_batch(
        self,
        file_paths: List[str],
        language: Optional[str] = None,
        include_timestamps: bool = False,
        output_format: OutputFormat = "txt"
    ) -> List[TranscriptionResult]:
        """Transcribe multiple files.
        
        Args:
            file_paths: List of file paths
            language: Language code. Auto-detect if None
            include_timestamps: Include word-level timestamps
            output_format: Output format (txt, json, srt, vtt)
            
        Returns:
            List of TranscriptionResult objects
        """
        results = []
        total = len(file_paths)

        for idx, file_path in enumerate(file_paths, 1):
            if self.verbose:
                print(f"\n[{idx}/{total}] Processing: {Path(file_path).name}")

            try:
                result = self.transcribe(
                    file_path,
                    language=language,
                    include_timestamps=include_timestamps,
                    output_format=output_format
                )
                results.append(result)
            except Exception as e:
                if self.verbose:
                    print(f"✗ Error: {e}")
                # Continue with next file
                continue

        if self.verbose:
            print(f"\n✓ Completed {len(results)}/{total} transcriptions")

        return results

    def _save_output(
        self,
        result: TranscriptionResult,
        format: OutputFormat
    ) -> str:
        """Save transcription to file.
        
        Args:
            result: TranscriptionResult object
            format: Output format
            
        Returns:
            Path to saved file
        """
        base_name = Path(result.source_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "txt":
            output_file = self.output_dir / f"{base_name}_{timestamp}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.transcript)

        elif format == "json":
            output_file = self.output_dir / f"{base_name}_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        elif format == "srt":
            output_file = self.output_dir / f"{base_name}_{timestamp}.srt"
            srt_content = self._to_srt(result.timestamps or [])
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)

        elif format == "vtt":
            output_file = self.output_dir / f"{base_name}_{timestamp}.vtt"
            vtt_content = self._to_vtt(result.timestamps or [])
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(vtt_content)

        return str(output_file)

    def _to_srt(self, timestamps: List[Dict]) -> str:
        """Convert timestamps to SRT format."""
        if not timestamps:
            return ""

        srt_lines = []
        for idx, ts in enumerate(timestamps, 1):
            start = self._format_timestamp_srt(ts.get("start", 0))
            end = self._format_timestamp_srt(ts.get("end", 0))
            text = ts.get("word") or ts.get("text", "")

            srt_lines.append(f"{idx}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")  # Blank line

        return "\n".join(srt_lines)

    def _to_vtt(self, timestamps: List[Dict]) -> str:
        """Convert timestamps to WebVTT format."""
        if not timestamps:
            return "WEBVTT\n\n"

        vtt_lines = ["WEBVTT", ""]
        for ts in timestamps:
            start = self._format_timestamp_vtt(ts.get("start", 0))
            end = self._format_timestamp_vtt(ts.get("end", 0))
            text = ts.get("word") or ts.get("text", "")

            vtt_lines.append(f"{start} --> {end}")
            vtt_lines.append(text)
            vtt_lines.append("")  # Blank line

        return "\n".join(vtt_lines)

    @staticmethod
    def _format_timestamp_srt(seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _format_timestamp_vtt(seconds: float) -> str:
        """Format seconds as WebVTT timestamp (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


# Module-level convenience function
def transcribe_file(
    file_path: str,
    model_size: ModelSize = "small",
    language: Optional[str] = None,
    output_format: OutputFormat = "txt",
    device: Optional[str] = None
) -> TranscriptionResult:
    """Convenience function for quick transcription.
    
    Args:
        file_path: Path to audio/video file
        model_size: Whisper model size
        language: Language code (auto-detect if None)
        output_format: Output format
        device: Device to use (auto-detect if None)
        
    Returns:
        TranscriptionResult
    """
    transcriber = LocalTranscriber(model_size=model_size, device=device)
    return transcriber.transcribe(
        file_path,
        language=language,
        output_format=output_format
    )
