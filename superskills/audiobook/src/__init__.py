"""
Audiobook skill - Convert documents to narrated audiobooks with chapter detection.
"""
from .AudiobookConfig import AudiobookConfig
from .AudiobookGenerator import AudiobookGenerator, AudiobookResult, ChapterAudioResult
from .ChapterDetector import Chapter, ChapterDetector
from .DocumentParser import DocumentParser

__all__ = [
    "AudiobookGenerator",
    "AudiobookResult",
    "ChapterAudioResult",
    "AudiobookConfig",
    "ChapterDetector",
    "Chapter",
    "DocumentParser",
    "execute",
]

__version__ = "1.0.0"


def _parse_chapter_range(range_str: str) -> tuple[int, int]:
    """Parse chapter range string.
    
    Args:
        range_str: Range string like "1", "1-3", "5-10"
        
    Returns:
        Tuple of (start_chapter, end_chapter) (1-indexed, inclusive)
        
    Raises:
        ValueError: If range format is invalid
    """
    range_str = range_str.strip()
    
    if '-' in range_str:
        # Range format: "1-3"
        parts = range_str.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid range format: '{range_str}'. Expected 'N' or 'N-M'")
        
        try:
            start = int(parts[0].strip())
            end = int(parts[1].strip())
        except ValueError:
            raise ValueError(f"Invalid range format: '{range_str}'. Chapter numbers must be integers")
        
        if start < 1:
            raise ValueError(f"Invalid range: '{range_str}'. Start chapter must be >= 1")
        if end < start:
            raise ValueError(f"Invalid range: '{range_str}'. End chapter must be >= start chapter")
        
        return (start, end)
    else:
        # Single chapter: "1"
        try:
            chapter_num = int(range_str)
        except ValueError:
            raise ValueError(f"Invalid chapter number: '{range_str}'. Must be an integer")
        
        if chapter_num < 1:
            raise ValueError(f"Chapter number must be >= 1, got: {chapter_num}")
        
        return (chapter_num, chapter_num)


def execute(input_text: str, **kwargs):
    """CLI entry point for audiobook skill.
    
    Args:
        input_text: Path to input document OR file path from --input flag
        **kwargs: Additional arguments:
            - output_prefix: Custom output filename prefix
            - chapter_strategy: Chapter detection strategy
            - output: Output directory (from --output flag)
            - input_file: File path from --input flag (if provided)
            - clean_text: Apply text cleaning (default: True)
            - chapter_range: Chapter range to process (e.g., "1", "1-3")
            - tts_provider: TTS provider (elevenlabs/gemini/openai)
            - tts_model: TTS model name
            - tts_voice: Voice ID
    
    Returns:
        Dict with generation results for CLI display
    """
    from pathlib import Path
    
    # Extract parameters
    # Prefer input_file kwarg (file path) over input_text (which might be file contents)
    input_file = kwargs.get('input_file', input_text.strip())
    output_prefix = kwargs.get('output_prefix')
    chapter_strategy = kwargs.get('chapter_strategy', 'auto')
    output_dir = kwargs.get('output', 'output')
    clean_text = kwargs.get('clean_text', True)
    chapter_range_str = kwargs.get('chapter_range')
    
    # NEW: Extract TTS parameters
    tts_provider = kwargs.get('tts_provider')
    tts_model = kwargs.get('tts_model')
    tts_voice = kwargs.get('tts_voice')
    skip_quota_check = kwargs.get('skip_quota_check', False)
    
    # Parse chapter range if provided
    chapter_range = None
    if chapter_range_str:
        chapter_range = _parse_chapter_range(chapter_range_str)
    
    # Validate input file exists
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Generate audiobook
    generator = AudiobookGenerator(
        output_dir=output_dir,
        chapter_strategy=chapter_strategy,
        clean_text=clean_text,
        tts_provider=tts_provider,  # NEW
        tts_model=tts_model,        # NEW
        tts_voice=tts_voice,        # NEW
        skip_quota_check=skip_quota_check,  # NEW
    )
    
    result = generator.generate_audiobook(
        file_path=str(input_path),
        output_prefix=output_prefix,
        chapter_range=chapter_range
    )
    
    # Return CLI-friendly result
    return {
        'output': f"Generated {result.total_chapters} chapters in {result.total_duration_seconds / 3600:.1f} hours",
        'metadata': {
            'skill': 'audiobook',
            'type': 'python',
            'total_chapters': result.total_chapters,
            'total_duration_seconds': result.total_duration_seconds,
            'total_word_count': result.total_word_count,
            'average_wpm': result.average_wpm,
            'metadata_file': result.metadata_file,
            'chapter_files': result.chapter_files
        }
    }
