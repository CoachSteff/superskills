"""
Local Transcriber - Privacy-focused offline transcription.
"""
from .LocalTranscriber import (
    LocalTranscriber,
    TranscriptionResult,
    transcribe_file
)

__all__ = [
    'LocalTranscriber',
    'TranscriptionResult',
    'transcribe_file'
]
