# Transcriber SuperSkill 🎙️

AI-powered audio and video transcription using OpenAI Whisper or AssemblyAI.

## Features

- **Multi-Provider Support**: OpenAI Whisper and AssemblyAI
- **Multiple Formats**: Export as TXT, JSON, SRT, VTT
- **Timestamps**: Word-level timestamps for precise timing
- **Batch Processing**: Transcribe multiple files efficiently
- **Quote Extraction**: Extract key quotes for marketing
- **Subtitle Generation**: Auto-generate SRT/VTT captions

## Installation

```bash
pip install openai assemblyai
```

## Quick Start

### Basic Transcription

```python
from superskills.transcriber.src import transcribe_file

# Transcribe a single file
result = transcribe_file("recording.mp3")
print(result.transcript)
```

### With Timestamps

```python
from superskills.transcriber.src import Transcriber

transcriber = Transcriber(provider="openai")
result = transcriber.transcribe(
    "session.mp4",
    include_timestamps=True,
    output_format="srt"
)
print(f"Transcript: {result.output_file}")
```

### Batch Transcription

```python
files = ["session1.mp3", "session2.mp3", "session3.mp3"]
results = transcriber.transcribe_batch(files, output_format="json")

for result in results:
    print(f"{result.source_file}: {result.word_count} words")
```

## API Reference

### Transcriber

**Constructor:**
```python
Transcriber(
    output_dir="transcripts",
    provider="openai",  # or "assemblyai"
    verbose=True
)
```

**Methods:**

- `transcribe(file_path, language=None, include_timestamps=False, output_format="txt")` - Transcribe single file
- `transcribe_batch(file_paths, **kwargs)` - Transcribe multiple files
- `extract_key_quotes(result, min_words=10, max_quotes=5)` - Extract marketing quotes

### TranscriptionResult

**Attributes:**
- `source_file`: Original file path
- `transcript`: Full transcript text
- `language`: Detected/specified language
- `duration_seconds`: Audio duration
- `word_count`: Total words
- `timestamps`: Word-level timestamps (if requested)
- `confidence`: Transcription confidence score
- `output_file`: Saved transcript path
- `timestamp`: ISO timestamp

## Output Formats

### TXT
Plain text transcript.

### JSON
Full metadata including timestamps:
```json
{
  "source_file": "recording.mp3",
  "transcript": "Hello world...",
  "language": "en",
  "duration_seconds": 120.5,
  "word_count": 215,
  "timestamps": [
    {"word": "Hello", "start": 0.5, "end": 0.8},
    ...
  ]
}
```

### SRT
Standard subtitle format for video players.

### VTT
WebVTT format for web video.

## Integration Examples

### With Narrator (Podcast Transcripts)

```python
from superskills.narrator.src import PodcastGenerator
from superskills.transcriber.src import Transcriber

# Generate podcast
podcast = PodcastGenerator()
result = podcast.generate_podcast(segments, "episode.mp3")

# Transcribe for show notes
transcriber = Transcriber()
transcript = transcriber.transcribe("episode.mp3", output_format="txt")
print(transcript.transcript)
```

### With Marketer (Social Snippets)

```python
from superskills.transcriber.src import Transcriber
from superskills.marketer.src import SocialMediaPublisher

# Transcribe
transcriber = Transcriber()
result = transcriber.transcribe("training.mp4", include_timestamps=True)

# Extract quotes
quotes = transcriber.extract_key_quotes(result, min_words=15, max_quotes=3)

# Share on social
publisher = SocialMediaPublisher()
for quote in quotes:
    publisher.schedule_post(quote, platforms=["TWITTER", "LINKEDIN"])
```

### With CoursePackager (Searchable Transcripts)

```python
from superskills.transcriber.src import Transcriber

transcriber = Transcriber()
results = transcriber.transcribe_batch(
    ["lesson1.mp4", "lesson2.mp4", "lesson3.mp4"],
    output_format="json"
)

# Package with course materials
# (transcripts are searchable in JSON format)
```

## Environment Variables

```bash
# OpenAI (recommended)
OPENAI_API_KEY=your_openai_api_key

# Or AssemblyAI
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
```

## Configuration

Edit `config/transcriber_config.yaml`:

```yaml
providers:
  primary: "openai"
  fallback: "assemblyai"

transcription:
  language: "auto"
  temperature: 0.0
  
output:
  formats: ["txt", "json", "srt", "vtt"]
  include_timestamps: true
```

## Best Practices

1. **File Size**: Keep files under 25MB for OpenAI Whisper
2. **Audio Quality**: Higher quality = better accuracy
3. **Language**: Specify language if known for better results
4. **Timestamps**: Only request when needed (increases processing time)
5. **Batch Processing**: Process multiple files for efficiency

## Troubleshooting

### API Key Error
```bash
# Set environment variable
export OPENAI_API_KEY=your_key_here
```

### File Too Large
Split large files or use AssemblyAI (no size limit).

### Poor Accuracy
- Improve audio quality
- Reduce background noise
- Specify the correct language

## Version

1.0.0

## License

MIT
