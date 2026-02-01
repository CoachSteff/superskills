"""
AudiobookGenerator.py - Main orchestrator for audiobook generation.
"""
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .AudiobookConfig import AudiobookConfig
from .ChapterDetector import Chapter, ChapterDetector, DetectionStrategy
from .DocumentParser import DocumentParser
from .tts import create_tts_provider, TTSConfig, TTSProvider

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available - audio metadata will be skipped")


@dataclass
class ChapterAudioResult:
    """Result from generating audio for a single chapter."""
    chapter_number: int
    chapter_title: str
    output_file: str
    duration_seconds: float
    word_count: int
    words_per_minute: int


@dataclass
class AudiobookResult:
    """Result from complete audiobook generation."""
    source_file: str
    output_prefix: str
    total_chapters: int
    chapter_files: List[str]
    metadata_file: str
    total_duration_seconds: float
    total_word_count: int
    average_wpm: int
    generated_at: str
    failed_chapters: List[Dict] = None  # NEW
    partial_success: bool = False  # NEW
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.failed_chapters is None:
            self.failed_chapters = []


class ScriptOptimizer:
    """Optimize text for natural speech delivery."""
    
    @staticmethod
    def optimize_for_speech(text: str) -> str:
        """Optimize text for text-to-speech.
        
        Args:
            text: Raw text content
            
        Returns:
            Optimized text
        """
        # Remove parenthetical asides and brackets
        optimized = re.sub(r'\([^)]*\)', '', text)
        optimized = re.sub(r'\[[^\]]*\]', '', optimized)
        
        # Replace em-dashes and colons with pauses
        optimized = optimized.replace('—', '...').replace(' - ', '... ').replace(':', '...')
        
        # Normalize whitespace
        optimized = re.sub(r'\s+', ' ', optimized)
        
        return optimized.strip()


class AudiobookGenerator:
    """Generate audiobooks from documents with automatic chapter detection."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        output_dir: str = "output",
        profile_type: str = "audiobook",
        chapter_strategy: DetectionStrategy = "auto",
        custom_chapter_patterns: Optional[List[str]] = None,
        clean_text: bool = True,
        # NEW PARAMETERS for multi-provider support
        tts_provider: Optional[str] = None,
        tts_model: Optional[str] = None,
        tts_voice: Optional[str] = None,
        skip_quota_check: bool = False,  # NEW
    ):
        """Initialize AudiobookGenerator.
        
        Args:
            api_key: TTS API key (provider-specific env var used if not provided)
            output_dir: Directory for output files
            profile_type: Voice profile to use
            chapter_strategy: Chapter detection strategy
            custom_chapter_patterns: Custom regex patterns for chapter detection
            clean_text: Apply text cleaning to remove page numbers, headers, etc.
            tts_provider: TTS provider override (elevenlabs/gemini/openai)
            tts_model: TTS model override
            tts_voice: Voice ID override
            skip_quota_check: Skip pre-flight quota validation
        """
        # Load config and profile
        self.config = AudiobookConfig()
        self.profile_type = profile_type
        self.profile = self.config.get_profile(profile_type)
        
        # CLI overrides config (highest priority)
        original_provider = self.profile.get("provider", "gemini")
        
        if tts_provider:
            # If switching providers, clear model/voice to use provider defaults
            if tts_provider != original_provider:
                if not tts_model:
                    self.profile.pop("model", None)  # Will use provider default
                if not tts_voice:
                    self.profile.pop("voice_id", None)  # Will use provider default
            
            self.profile["provider"] = tts_provider
            
        if tts_model:
            self.profile["model"] = tts_model
        if tts_voice:
            self.profile["voice_id"] = tts_voice
        
        # Determine provider and API key
        provider = self.profile["provider"]
        api_key = api_key or self._get_api_key_for_provider(provider)
        
        # Create TTS provider
        self.tts_provider: TTSProvider = create_tts_provider(provider, api_key)
        
        # Build and validate TTS config
        self.tts_config = self._build_tts_config()
        self.tts_provider.validate_config(self.tts_config)
        
        # Get character limit from provider
        self.char_limit = self.tts_provider.get_character_limit()
        
        # Quota check setting
        self.skip_quota_check = skip_quota_check
        
        # Setup output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.parser = DocumentParser()
        self.detector = ChapterDetector(custom_patterns=custom_chapter_patterns)
        self.chapter_strategy = chapter_strategy
        self.optimizer = ScriptOptimizer()
        self.clean_text = clean_text
    
    def _get_api_key_for_provider(self, provider: str) -> str:
        """Get API key from environment based on provider.
        
        Uses credential cascade: system env → skill .env → user .env → root .env
        
        Args:
            provider: TTS provider name
            
        Returns:
            API key from environment
            
        Raises:
            ValueError: If API key not found
        """
        from superskills.core.credentials import load_credentials
        
        env_var_map = {
            "elevenlabs": "ELEVENLABS_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
        }
        
        env_var = env_var_map.get(provider)
        if not env_var:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Load credentials with cascade: system → skill .env → user .env → root .env
        load_credentials(skill_name="audiobook")
        
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(
                f"{env_var} not found. Set environment variable or pass api_key parameter."
            )
        
        return api_key
    
    def _build_tts_config(self) -> TTSConfig:
        """Build TTSConfig from profile settings.
        
        Returns:
            TTSConfig object
        """
        return TTSConfig(
            provider=self.profile["provider"],
            model=self.profile.get("model", ""),  # Empty string = use provider default
            voice_id=self.profile.get("voice_id", ""),  # Empty string = use provider default
            speed=self.profile.get("speed", 1.0),
            extra_settings={
                k: v for k, v in self.profile.items()
                if k not in ["provider", "model", "voice_id", "speed"]
            }
        )

    def generate_audiobook(
        self,
        file_path: str,
        output_prefix: Optional[str] = None,
        chapter_range: Optional[tuple[int, int]] = None
    ) -> AudiobookResult:
        """Generate complete audiobook from document.
        
        Args:
            file_path: Path to source document
            output_prefix: Prefix for output filenames (defaults to source filename)
            chapter_range: Optional tuple (start, end) for chapter range (1-indexed, inclusive)
            
        Returns:
            AudiobookResult with generation metadata
        """
        print(f"Parsing document: {file_path}")
        text = self.parser.parse_file(file_path, clean_text=self.clean_text)
        
        print(f"Detecting chapters using '{self.chapter_strategy}' strategy...")
        chapters = self.detector.detect_chapters(text, strategy=self.chapter_strategy)
        
        total_detected = len(chapters)
        print(f"Found {total_detected} chapters")
        
        # Filter chapters by range if specified
        if chapter_range:
            start_idx, end_idx = chapter_range
            
            # Validate range
            if start_idx > total_detected:
                raise ValueError(
                    f"Start chapter {start_idx} exceeds total chapters ({total_detected})"
                )
            
            # Adjust end_idx if it exceeds available chapters
            end_idx = min(end_idx, total_detected)
            
            # Filter (convert to 0-indexed)
            chapters = chapters[start_idx - 1:end_idx]
            print(f"Processing chapters {start_idx}-{end_idx} (selected {len(chapters)} of {total_detected} chapters)")
        
        # PRE-FLIGHT QUOTA VALIDATION
        if not self.skip_quota_check:
            # Calculate total estimated characters
            total_chars = sum(len(ch.text) for ch in chapters)
            # Add buffer for chapter announcements (~200 chars each)
            total_chars += len(chapters) * 200
            
            print(f"Estimated total: {total_chars:,} characters for {len(chapters)} chapter(s)")
            
            # Check provider quota
            quota_check = self.tts_provider.check_quota(total_chars)
            
            if quota_check['provider_supports_check']:
                print(f"  Provider quota: {quota_check['available']:,} characters available")
                
                if not quota_check['sufficient']:
                    print(f"\n⚠ WARNING: Insufficient quota!")
                    print(f"  Required: {quota_check['required']:,} characters")
                    print(f"  Available: {quota_check['available']:,} characters")
                    print(f"  Shortfall: {quota_check['required'] - quota_check['available']:,} characters")
                    print(f"\n  Suggestion: Reduce chapter range or add more credits to your account")
                    
                    # Ask user to continue or abort
                    try:
                        response = input("\n  Continue anyway? This will likely fail mid-generation. (y/N): ")
                        if response.lower() != 'y':
                            raise ValueError("Aborted: Insufficient quota")
                    except (EOFError, KeyboardInterrupt):
                        raise ValueError("Aborted: Insufficient quota")
        
        if not output_prefix:
            output_prefix = Path(file_path).stem
        
        # Sanitize output prefix for filenames
        output_prefix = self._sanitize_filename(output_prefix)
        
        # Get book title for announcements (use original filename, not sanitized)
        book_title = Path(file_path).stem.replace('_', ' ').replace('-', ' ').title()
        
        # Generate audio for each chapter WITH GRACEFUL DEGRADATION
        chapter_results = []
        failed_chapters = []
        
        for i, chapter in enumerate(chapters, 1):
            print(f"[{i}/{len(chapters)}] Generating Chapter {chapter.number}: \"{chapter.title}\"...")
            
            try:
                part_results = self._generate_chapter_audio(chapter, output_prefix, book_title)
                chapter_results.extend(part_results)
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if quota exceeded
                if 'quota_exceeded' in error_msg.lower() or 'quota' in error_msg.lower():
                    print(f"  ✗ QUOTA EXCEEDED: {e}")
                    print(f"\n  Generated {len(chapter_results)} of {len(chapters)} chapters successfully")
                    print(f"  Completed chapters saved to: {self.output_dir}")
                    
                    failed_chapters.append({
                        'chapter': chapter.number,
                        'title': chapter.title,
                        'error': 'quota_exceeded'
                    })
                    
                    # Stop processing
                    print(f"\n  Stopping audiobook generation due to quota limit.")
                    break
                    
                else:
                    # Other error
                    print(f"  ✗ ERROR: {e}")
                    failed_chapters.append({
                        'chapter': chapter.number,
                        'title': chapter.title,
                        'error': error_msg
                    })
                    
                    # Ask to continue
                    try:
                        response = input("\n  Continue with next chapter? (y/N): ")
                        if response.lower() == 'y':
                            continue
                        else:
                            break
                    except (EOFError, KeyboardInterrupt):
                        break
        
        # Check if we have any successful chapters
        if not chapter_results:
            raise ValueError("No chapters were successfully generated")
        
        # Create metadata file
        metadata_file = self._create_metadata(
            chapters, 
            chapter_results, 
            output_prefix,
            file_path
        )
        
        # Add failed chapters to metadata if any
        if failed_chapters:
            metadata_path = Path(metadata_file)
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata['failed_chapters'] = failed_chapters
            metadata['partial_success'] = True
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        # Calculate totals
        total_duration = sum(r.duration_seconds for r in chapter_results)
        total_words = sum(r.word_count for r in chapter_results)
        avg_wpm = int((total_words / total_duration) * 60) if total_duration > 0 else 0
        
        # Print completion message
        if failed_chapters:
            print(f"\n⚠ Audiobook generation completed with warnings!")
            print(f"  Successfully generated: {len(chapter_results)} of {len(chapters)} chapters")
            print(f"  Failed chapters: {len(failed_chapters)}")
            for fc in failed_chapters:
                print(f"    - Chapter {fc['chapter']}: {fc['title']} ({fc['error']})")
        else:
            print(f"\n✓ Audiobook generation complete!")
        
        print(f"  Total chapters: {len(chapter_results)}")
        print(f"  Total duration: {total_duration / 3600:.1f} hours")
        print(f"  Total words: {total_words:,}")
        print(f"  Average WPM: {avg_wpm}")
        print(f"  Metadata: {metadata_file}")
        
        return AudiobookResult(
            source_file=file_path,
            output_prefix=output_prefix,
            total_chapters=len(chapter_results),
            chapter_files=[r.output_file for r in chapter_results],
            metadata_file=metadata_file,
            total_duration_seconds=round(total_duration, 2),
            total_word_count=total_words,
            average_wpm=avg_wpm,
            generated_at=datetime.now().isoformat(),
            failed_chapters=failed_chapters,
            partial_success=len(failed_chapters) > 0
        )

    def _generate_chapter_audio(
        self,
        chapter: Chapter,
        output_prefix: str,
        book_title: str
    ) -> List[ChapterAudioResult]:
        """Generate audio for a single chapter with automatic splitting if needed.
        
        Args:
            chapter: Chapter object with text content
            output_prefix: Prefix for output filename
            book_title: Book title for chapter announcement
            
        Returns:
            List of ChapterAudioResult (multiple parts if chapter was split)
        """
        # Create chapter announcement
        announcement = self._create_chapter_announcement(book_title, chapter)
        
        # Optimize text for speech
        processed_text = self.optimizer.optimize_for_speech(chapter.text)
        
        # Combine announcement with chapter text
        full_text = f"{announcement} ... {processed_text}"
        
        # Check if splitting needed
        if len(full_text) <= self.char_limit:
            # Single part generation (original behavior)
            return [self._generate_single_audio_part(
                text=full_text,
                chapter=chapter,
                output_prefix=output_prefix,
                part_suffix=""
            )]
        
        # SPLIT INTO PARTS
        print(f"  ⚠ Chapter exceeds {self.char_limit:,} char limit ({len(full_text):,} chars). Auto-splitting...")
        
        # Split chapter text into parts
        parts = self._split_text_to_parts(processed_text, announcement)
        
        results = []
        part_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        
        for idx, part_text in enumerate(parts):
            part_label = part_labels[idx] if idx < len(part_labels) else str(idx + 1)
            
            # First part includes announcement, others just continuation
            if idx == 0:
                text_to_generate = f"{announcement} ... {part_text}"
            else:
                continuation = f"Continuing chapter {chapter.number}, {chapter.title}, part {part_label}."
                text_to_generate = f"{continuation} ... {part_text}"
            
            result = self._generate_single_audio_part(
                text=text_to_generate,
                chapter=chapter,
                output_prefix=output_prefix,
                part_suffix=part_label
            )
            results.append(result)
        
        return results
    
    def _split_text_to_parts(
        self,
        text: str,
        announcement: str
    ) -> List[str]:
        """Split text into parts that fit within character limit.
        
        Args:
            text: Text to split
            announcement: Chapter announcement (for buffer calculation)
            
        Returns:
            List of text parts
        """
        # Reserve space for announcement + continuation text (~200 chars)
        buffer = len(announcement) + 200
        max_part_size = self.char_limit - buffer
        
        # Split by paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        parts = []
        current_part = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > max_part_size and current_part:
                # Save current part
                parts.append('\n\n'.join(current_part))
                current_part = []
                current_size = 0
            
            current_part.append(para)
            current_size += para_size + 2
        
        # Save final part
        if current_part:
            parts.append('\n\n'.join(current_part))
        
        return parts
    
    def _generate_single_audio_part(
        self,
        text: str,
        chapter: Chapter,
        output_prefix: str,
        part_suffix: str
    ) -> ChapterAudioResult:
        """Generate audio for a single text segment.
        
        Args:
            text: Text to convert (already includes announcement if first part)
            chapter: Original chapter object
            output_prefix: Prefix for output filename
            part_suffix: Part label ('', 'a', 'b', etc.)
            
        Returns:
            ChapterAudioResult with generation metadata
        """
        # Validate character limit (should never exceed now)
        if len(text) > self.char_limit:
            raise ValueError(
                f"Part text still exceeds limit: {len(text):,} > {self.char_limit:,}. "
                f"This should not happen - please report as bug."
            )
        
        # Generate filename with part suffix
        sanitized_title = self._sanitize_filename(chapter.title)
        if part_suffix:
            output_filename = f"{output_prefix}_chapter_{chapter.number:02d}{part_suffix}_{sanitized_title}.mp3"
        else:
            output_filename = f"{output_prefix}_chapter_{chapter.number:02d}_{sanitized_title}.mp3"
        
        output_path = self.output_dir / output_filename
        
        # Generate audio using TTS provider
        audio_generator = self.tts_provider.generate_speech(text, self.tts_config)
        
        # Collect audio chunks
        chunks = []
        for chunk in audio_generator:
            chunks.append(chunk)
        
        # Write audio file
        with open(output_path, 'wb') as f:
            for chunk in chunks:
                f.write(chunk)
        
        # Calculate metadata (word count for this part only)
        word_count = len(text.split())
        
        if PYDUB_AVAILABLE:
            try:
                audio_segment = AudioSegment.from_mp3(output_path)
                duration_seconds = audio_segment.duration_seconds
                wpm = int((word_count / duration_seconds) * 60) if duration_seconds > 0 else 0
                
                suffix_display = f" (part {part_suffix})" if part_suffix else ""
                print(f"  ✓ Generated: {output_filename}{suffix_display} | {duration_seconds:.1f}s | {wpm} WPM")
                
                return ChapterAudioResult(
                    chapter_number=chapter.number,
                    chapter_title=f"{chapter.title}{' (part ' + part_suffix + ')' if part_suffix else ''}",
                    output_file=str(output_path),
                    duration_seconds=round(duration_seconds, 2),
                    word_count=word_count,
                    words_per_minute=wpm
                )
            except Exception as e:
                print(f"  ✓ Generated: {output_filename} (metadata calculation failed: {e})")
        else:
            print(f"  ✓ Generated: {output_filename}")
        
        # Fallback without pydub
        return ChapterAudioResult(
            chapter_number=chapter.number,
            chapter_title=f"{chapter.title}{' (part ' + part_suffix + ')' if part_suffix else ''}",
            output_file=str(output_path),
            duration_seconds=0.0,
            word_count=word_count,
            words_per_minute=0
        )

    def _create_metadata(
        self,
        chapters: List[Chapter],
        audio_results: List[ChapterAudioResult],
        output_prefix: str,
        source_file: str
    ) -> str:
        """Create metadata JSON file.
        
        Args:
            chapters: List of chapter objects
            audio_results: List of audio generation results
            output_prefix: Output filename prefix
            source_file: Source document path
            
        Returns:
            Path to metadata file
        """
        total_duration = sum(r.duration_seconds for r in audio_results)
        total_words = sum(r.word_count for r in audio_results)
        avg_wpm = int((total_words / total_duration) * 60) if total_duration > 0 else 0
        
        metadata = {
            "title": output_prefix,
            "source_file": source_file,
            "total_chapters": len(chapters),
            "total_duration_seconds": round(total_duration, 2),
            "total_duration_formatted": self._format_duration(total_duration),
            "total_word_count": total_words,
            "average_wpm": avg_wpm,
            "generated_at": datetime.now().isoformat(),
            "profile_type": self.profile_type,
            "voice_name": self.profile.get("voice_name", "Unknown"),
            "chapters": [
                {
                    "number": result.chapter_number,
                    "title": result.chapter_title,
                    "file": Path(result.output_file).name,
                    "duration_seconds": result.duration_seconds,
                    "duration_formatted": self._format_duration(result.duration_seconds),
                    "word_count": result.word_count,
                    "wpm": result.words_per_minute
                }
                for result in audio_results
            ]
        }
        
        metadata_filename = f"{output_prefix}_metadata.json"
        metadata_path = self.output_dir / metadata_filename
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(metadata_path)

    def _create_chapter_announcement(self, book_title: str, chapter: Chapter) -> str:
        """Create spoken announcement for chapter beginning.
        
        Args:
            book_title: Title of the book
            chapter: Chapter object
            
        Returns:
            Announcement text to be spoken
        """
        # Detect if this is a special section (Prologue, Epilogue, etc.)
        special_sections = ['Prologue', 'Epilogue', 'Foreword', 'Afterword', 'Preface']
        is_special = any(section.lower() in chapter.title.lower() for section in special_sections)
        
        if is_special:
            # For special sections: "Book Title. Prologue: [subtitle if any]"
            return f"{book_title}. {chapter.title}"
        else:
            # For regular chapters: "Book Title. Chapter Number. Chapter Title"
            if chapter.title.lower().startswith('chapter'):
                # Title already includes "Chapter", just add book title
                return f"{book_title}. {chapter.title}"
            else:
                # Add chapter number
                return f"{book_title}. Chapter {chapter.number}. {chapter.title}"

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize string for use in filename.
        
        Args:
            name: Original string
            
        Returns:
            Sanitized filename-safe string
        """
        import unicodedata
        
        # Remove null bytes explicitly
        sanitized = name.replace('\x00', '')
        
        # Remove all control characters (Unicode categories Cc, Cf)
        sanitized = ''.join(
            char for char in sanitized 
            if unicodedata.category(char) not in ('Cc', 'Cf')
        )
        
        # Normalize Unicode to NFKD (decompose accents)
        sanitized = unicodedata.normalize('NFKD', sanitized)
        
        # Remove or replace invalid filename characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', sanitized)
        
        # Replace whitespace with underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        
        # Strip leading/trailing dots and underscores
        sanitized = sanitized.strip('._')
        
        # Fallback if completely sanitized away
        if not sanitized or len(sanitized) < 3:
            sanitized = "chapter"
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50].rstrip('._')
        
        return sanitized.lower()

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string (e.g., "1h 23m 45s")
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
