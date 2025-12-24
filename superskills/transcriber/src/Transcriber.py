"""
Transcriber.py - AI-powered audio/video transcription using Whisper API.
"""
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai not available - install with: pip install openai")

try:
    import assemblyai as aai
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False
    print("Warning: assemblyai not available - install with: pip install assemblyai")


OutputFormat = Literal["txt", "json", "srt", "vtt"]


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

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class Transcriber:
    """AI-powered transcription using OpenAI Whisper or AssemblyAI."""

    def __init__(
        self,
        output_dir: str = "transcripts",
        provider: Literal["openai", "assemblyai"] = "openai",
        verbose: bool = True
    ):
        """Initialize Transcriber.
        
        Args:
            output_dir: Directory to save transcripts
            provider: Transcription provider (openai or assemblyai)
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.provider = provider
        self.verbose = verbose

        if provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai is required. Install with: pip install openai")
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = OpenAI(api_key=self.api_key)

        elif provider == "assemblyai":
            if not ASSEMBLYAI_AVAILABLE:
                raise ImportError("assemblyai is required. Install with: pip install assemblyai")
            self.api_key = os.getenv("ASSEMBLYAI_API_KEY")
            if not self.api_key:
                raise ValueError("ASSEMBLYAI_API_KEY environment variable not set")
            aai.settings.api_key = self.api_key

    def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        include_timestamps: bool = False,
        output_format: OutputFormat = "txt"
    ) -> TranscriptionResult:
        """Transcribe audio/video file.
        
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

        if self.provider == "openai":
            result = self._transcribe_with_openai(file_path, language, include_timestamps)
        elif self.provider == "assemblyai":
            result = self._transcribe_with_assemblyai(file_path, language, include_timestamps)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        output_file = self._save_transcript(result, output_format)
        result.output_file = output_file

        if self.verbose:
            print(f"✓ Transcribed: {result.word_count} words in {result.duration_seconds:.1f}s")
            print(f"✓ Saved to: {output_file}")

        return result

    def _transcribe_with_openai(
        self,
        file_path: Path,
        language: Optional[str],
        include_timestamps: bool
    ) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API."""
        with open(file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json" if include_timestamps else "json",
                timestamp_granularities=["word"] if include_timestamps else None
            )

        transcript = response.text
        word_count = len(transcript.split())

        timestamps = None
        if include_timestamps and hasattr(response, 'words'):
            timestamps = [
                {"word": w.word, "start": w.start, "end": w.end}
                for w in response.words
            ]

        duration = getattr(response, 'duration', 0.0)
        language_detected = getattr(response, 'language', language or 'en')

        return TranscriptionResult(
            source_file=str(file_path),
            transcript=transcript,
            language=language_detected,
            duration_seconds=duration,
            word_count=word_count,
            timestamps=timestamps,
            confidence=1.0
        )

    def _transcribe_with_assemblyai(
        self,
        file_path: Path,
        language: Optional[str],
        include_timestamps: bool
    ) -> TranscriptionResult:
        """Transcribe using AssemblyAI API."""
        config = aai.TranscriptionConfig(
            language_code=language,
            word_boost=[] if not language else None
        )

        transcriber = aai.Transcriber(config=config)
        transcript_obj = transcriber.transcribe(str(file_path))

        transcript = transcript_obj.text
        word_count = len(transcript.split())

        timestamps = None
        if include_timestamps and transcript_obj.words:
            timestamps = [
                {"word": w.text, "start": w.start / 1000.0, "end": w.end / 1000.0}
                for w in transcript_obj.words
            ]

        duration = (transcript_obj.audio_duration / 1000.0) if transcript_obj.audio_duration else 0.0
        confidence = transcript_obj.confidence or 1.0

        return TranscriptionResult(
            source_file=str(file_path),
            transcript=transcript,
            language=language or 'en',
            duration_seconds=duration,
            word_count=word_count,
            timestamps=timestamps,
            confidence=confidence
        )

    def _save_transcript(
        self,
        result: TranscriptionResult,
        format: OutputFormat
    ) -> str:
        """Save transcript to file.
        
        Args:
            result: TranscriptionResult to save
            format: Output format
            
        Returns:
            Path to saved file
        """
        base_name = Path(result.source_file).stem

        if format == "txt":
            output_path = self.output_dir / f"{base_name}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.transcript)

        elif format == "json":
            output_path = self.output_dir / f"{base_name}.json"
            data = {
                "source_file": result.source_file,
                "transcript": result.transcript,
                "language": result.language,
                "duration_seconds": result.duration_seconds,
                "word_count": result.word_count,
                "timestamps": result.timestamps,
                "confidence": result.confidence,
                "timestamp": result.timestamp
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format == "srt":
            output_path = self.output_dir / f"{base_name}.srt"
            srt_content = self._generate_srt(result)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)

        elif format == "vtt":
            output_path = self.output_dir / f"{base_name}.vtt"
            vtt_content = self._generate_vtt(result)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(vtt_content)

        return str(output_path)

    def _generate_srt(self, result: TranscriptionResult) -> str:
        """Generate SRT subtitle format."""
        if not result.timestamps:
            return result.transcript

        srt_lines = []
        chunk_size = 10

        for i in range(0, len(result.timestamps), chunk_size):
            chunk = result.timestamps[i:i+chunk_size]
            start_time = chunk[0]['start']
            end_time = chunk[-1]['end']
            text = ' '.join(w['word'] for w in chunk)

            srt_lines.append(f"{i // chunk_size + 1}")
            srt_lines.append(f"{self._format_timestamp_srt(start_time)} --> {self._format_timestamp_srt(end_time)}")
            srt_lines.append(text)
            srt_lines.append("")

        return '\n'.join(srt_lines)

    def _generate_vtt(self, result: TranscriptionResult) -> str:
        """Generate VTT subtitle format."""
        vtt = "WEBVTT\n\n"
        vtt += self._generate_srt(result).replace(',', '.')
        return vtt

    def _format_timestamp_srt(self, seconds: float) -> str:
        """Format timestamp for SRT format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def extract_key_quotes(
        self,
        result: TranscriptionResult,
        min_words: int = 10,
        max_quotes: int = 5
    ) -> List[str]:
        """Extract key quotes from transcript for marketing.
        
        Args:
            result: TranscriptionResult to extract from
            min_words: Minimum words per quote
            max_quotes: Maximum number of quotes to return
            
        Returns:
            List of quote strings
        """
        sentences = result.transcript.replace('!', '.').replace('?', '.').split('.')
        quotes = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) >= min_words:
                quotes.append(sentence)
                if len(quotes) >= max_quotes:
                    break

        return quotes

    def transcribe_batch(
        self,
        file_paths: List[str],
        **kwargs
    ) -> List[TranscriptionResult]:
        """Transcribe multiple files.
        
        Args:
            file_paths: List of file paths to transcribe
            **kwargs: Additional arguments for transcribe()
            
        Returns:
            List of TranscriptionResult objects
        """
        if self.verbose:
            print(f"Transcribing {len(file_paths)} files...")

        results = []
        for i, file_path in enumerate(file_paths, 1):
            if self.verbose:
                print(f"[{i}/{len(file_paths)}] Processing {Path(file_path).name}")

            try:
                result = self.transcribe(file_path, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Error transcribing {file_path}: {e}")
                results.append(TranscriptionResult(
                    source_file=file_path,
                    transcript="",
                    language="unknown",
                    duration_seconds=0,
                    word_count=0,
                    confidence=0.0
                ))

        if self.verbose:
            successful = sum(1 for r in results if r.word_count > 0)
            print(f"✓ Completed: {successful}/{len(file_paths)} successful")

        return results


def transcribe_file(
    file_path: str,
    output_dir: str = "transcripts",
    provider: Literal["openai", "assemblyai"] = "openai",
    **kwargs
) -> TranscriptionResult:
    """Convenience function to transcribe a single file.
    
    Args:
        file_path: Path to audio/video file
        output_dir: Output directory
        provider: Transcription provider
        **kwargs: Additional arguments for Transcriber
        
    Returns:
        TranscriptionResult
    """
    transcriber = Transcriber(output_dir=output_dir, provider=provider)
    return transcriber.transcribe(file_path, **kwargs)
