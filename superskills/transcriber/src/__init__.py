"""Transcriber skill - AI-powered audio/video transcription."""

from .Transcriber import Transcriber, TranscriptionResult, transcribe_file

__all__ = [
    'Transcriber',
    'TranscriptionResult',
    'transcribe_file'
]

__version__ = "1.0.0"
