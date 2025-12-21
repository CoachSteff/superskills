# Transcriber Local - Privacy-Focused Offline Transcription

Privacy-first audio/video transcription using local Whisper models. Zero cloud dependencies.

## Features

✅ **100% Offline** - No internet required after model download
✅ **Complete Privacy** - Data never leaves your machine  
✅ **Zero API Costs** - Unlimited transcriptions  
✅ **GDPR/HIPAA Compatible** - Suitable for sensitive content  
✅ **GPU Acceleration** - CUDA and Apple Silicon support  
✅ **Multiple Models** - Choose speed vs accuracy trade-off  

## Quick Start

```python
from superskills.transcriber_local.src import Local Transcriber

# Initialize with your preferred model
transcriber = LocalTranscriber(model_size="small")

# Transcribe a file
result = transcriber.transcribe("recording.mp3")
print(result.transcript)
```

## Installation

```bash
# Basic installation
pip install openai-whisper

# GPU support (NVIDIA)
pip install openai-whisper[cuda]

# Apple Silicon support
pip install openai-whisper[metal]
```

## Model Selection

| Model  | Speed      | Accuracy   | RAM Needed | Best For                    |
|--------|------------|------------|------------|-----------------------------|
| tiny   | Fastest    | Good       | 1GB        | Quick drafts, low-end hardware |
| base   | Fast       | Better     | 1GB        | Daily transcription         |
| small  | Balanced   | Great      | 2GB        | **Recommended for most**    |
| medium | Slower     | Excellent  | 5GB        | Professional content        |
| large  | Slowest    | Best       | 10GB       | Critical accuracy           |

## Usage Examples

### Basic Transcription
```python
from superskills.transcriber_local.src import transcribe_file

result = transcribe_file(
    "interview.mp3",
    model_size="small",
    output_format="txt"
)
```

### With Timestamps (for video captions)
```python
transcriber = LocalTranscriber(model_size="medium")
result = transcriber.transcribe(
    "video.mp4",
    include_timestamps=True,
    output_format="srt"  # or "vtt" for web
)
```

### Batch Processing
```python
files = ["day1.mp3", "day2.mp3", "day3.mp3"]
results = transcriber.transcribe_batch(files, output_format="json")
```

### GPU Acceleration
```python
# Automatically uses CUDA if available
transcriber = LocalTranscriber(model_size="large", device="cuda")
result = transcriber.transcribe("long_recording.wav")
```

## Privacy & Compliance

### HIPAA Compliance
Suitable for healthcare recordings - all processing stays local. No PHI transmission.

### GDPR Compliance
No personal data leaves your control. Perfect for EU data residency requirements.

### Zero Trust Architecture
No external API dependencies. Runs in air-gapped environments.

## Output Formats

**TXT**: Plain text transcript
```
This is the transcribed text from your audio file.
```

**JSON**: Full metadata with timestamps
```json
{
  "source_file": "recording.mp3",
  "transcript": "Full text...",
  "language": "en",
  "duration_seconds": 120.5,
  "word_count": 215,
  "timestamps": [{"word": "Hello", "start": 0.5, "end": 0.8}]
}
```

**SRT**: Video subtitles
```
1
00:00:00,500 --> 00:00:00,800
Hello

2
00:00:00,800 --> 00:00:01,200
world
```

**VTT**: Web video captions
```
WEBVTT

00:00:00.500 --> 00:00:00.800
Hello

00:00:00.800 --> 00:00:01.200
world
```

## Performance Tips

### Speed Optimization
1. **Use GPU** if available (3-10x faster)
2. **Choose smaller model** for acceptable quality
3. **Process shorter segments** for large files
4. **Close other applications** to free resources

### Quality Optimization
1. **Use larger model** (medium or large)
2. **Specify language** instead of auto-detect
3. **Clean audio first** (noise reduction)
4. **High-quality source** (lossless preferred)

## Troubleshooting

### Model Download Issues
- Check internet connection (one-time download)
- Ensure ~500MB-3GB free disk space
- Try different model size

### Out of Memory
```python
# Use smaller model
transcriber = LocalTranscriber(model_size="tiny")

# Or process shorter segments
# Split large files before processing
```

### Slow Performance
```python
# Enable GPU if available
transcriber = LocalTranscriber(device="cuda")

# Or use faster model
transcriber = LocalTranscriber(model_size="base")
```

## Integration with Other Skills

### → author (Structured Content)
```python
result = transcriber.transcribe("webinar.mp4")
# Feed transcript to author skill for blog post
```

### → editor (Polish Transcript)
```python
result = transcriber.transcribe("rough_recording.mp3")
# Use editor skill to clean up transcription errors
```

### → coursepackager (Training Materials)
```python
results = transcriber.transcribe_batch(lesson_files)
# Package transcripts into course documentation
```

## When to Use

**Perfect for:**
- ✅ Sensitive content (legal, medical, counseling)
- ✅ Offline workflows
- ✅ High-volume transcription (cost savings)
- ✅ Data sovereignty requirements
- ✅ Air-gapped environments

**Consider cloud transcriber when:**
- ⚠️ Need fastest results (cloud GPUs faster)
- ⚠️ Limited local hardware
- ⚠️ Don't want to manage models
- ⚠️ Working with very large files (>10GB)

## System Requirements

**Minimum:**
- Python 3.9+
- 4GB RAM (for tiny/base models)
- 2GB free disk space

**Recommended:**
- Python 3.10+
- 8GB RAM (for small/medium models)
- NVIDIA GPU with 4GB+ VRAM or Apple Silicon
- 5GB free disk space

**Optimal:**
- Python 3.11+
- 16GB RAM
- NVIDIA GPU with 8GB+ VRAM
- SSD storage

## License

Follows SuperSkills project license (MIT).
Whisper model license: MIT (OpenAI).
