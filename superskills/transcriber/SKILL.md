---
name: transcriber
description: AI-powered audio and video transcription using OpenAI Whisper or AssemblyAI. Use when converting recordings to text, generating subtitles, or creating searchable transcripts.
---

# Transcriber

Convert audio and video to accurate text transcripts with timestamps, perfect for creating course materials, show notes, and searchable content.

## Tools

**Transcriber.py** (in src/):
- Multi-provider support (OpenAI Whisper, AssemblyAI)
- Word-level timestamps for precise timing
- Multiple output formats (TXT, JSON, SRT, VTT)
- Batch processing for multiple files
- Key quote extraction for marketing
- Automatic language detection
- Confidence scoring

## Core Workflow

### 1. File Preparation
- Receive audio/video file(s)
- Validate file format and size
- Determine output requirements (format, timestamps)
- Select transcription provider

### 2. Transcription
- Upload and process file through API
- Capture word-level timestamps if needed
- Detect language automatically
- Extract metadata (duration, word count)
- Generate confidence scores

### 3. Delivery
- Export in requested format (TXT, JSON, SRT, VTT)
- Extract key quotes if needed
- Package with metadata
- Handoff to downstream workflows (narrator, coursepackager, author)

## Usage

**Basic Transcription:**
```python
from superskills.transcriber.src import transcribe_file

result = transcribe_file("recording.mp3")
print(result.transcript)
print(f"Duration: {result.duration_seconds}s")
print(f"Words: {result.word_count}")
```

**With Timestamps:**
```python
from superskills.transcriber.src import Transcriber

transcriber = Transcriber(provider="openai")
result = transcriber.transcribe(
    "session.mp4",
    include_timestamps=True,
    output_format="srt"
)
print(f"Saved to: {result.output_file}")
```

**Batch Processing:**
```python
files = ["session1.mp3", "session2.mp3", "session3.mp3"]
results = transcriber.transcribe_batch(files, output_format="json")

for result in results:
    print(f"{result.source_file}: {result.word_count} words")
```

**Extract Marketing Quotes:**
```python
result = transcriber.transcribe("podcast.mp3", include_timestamps=True)
quotes = transcriber.extract_key_quotes(result, min_words=15, max_quotes=5)

for quote in quotes:
    print(quote)
```

## Output Formats

**TXT**: Plain text transcript  
**JSON**: Full metadata including timestamps and confidence  
**SRT**: Standard subtitle format for video players  
**VTT**: WebVTT format for web video  

## Environment Variables

```bash
# OpenAI Whisper (recommended)
OPENAI_API_KEY=your_openai_api_key

# Or AssemblyAI (alternative)
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
```

**Global .env (repository root):**
```bash
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

**Or skill-specific .env:**
```bash
echo "OPENAI_API_KEY=sk-your-key" >> superskills/transcriber/.env
```

## Quality Checklist

- [ ] Audio quality sufficient (clear speech, minimal background noise)
- [ ] File size within limits (OpenAI: <25MB)
- [ ] Language correctly detected or specified
- [ ] Timestamps accurate if requested
- [ ] Confidence scores reviewed
- [ ] Output format correct for use case
- [ ] Metadata captured (duration, word count)

## Avoid

- **Poor Audio Quality**: Accept any file → Pre-check audio quality and clarity
- **Missing Context**: Generic transcription → Specify language/domain for better accuracy
- **Wrong Format**: Text only → Use SRT/VTT for video subtitles
- **Ignoring Timestamps**: Plain text → Capture timestamps for editing/navigation
- **Large Files**: Single upload → Split files >25MB or use AssemblyAI

## Escalate When

- Audio quality too poor for accurate transcription
- Multiple speakers need identification (diarization)
- Technical jargon requires custom vocabulary
- File size exceeds API limits
- Budget constraints require cost optimization

## Integration Examples

**With Narrator (Podcast Transcripts):**
```python
from superskills.narrator.src import PodcastGenerator
from superskills.transcriber.src import Transcriber

podcast = PodcastGenerator()
result = podcast.generate_podcast(segments, "episode.mp3")

transcriber = Transcriber()
transcript = transcriber.transcribe("episode.mp3", output_format="txt")
print(transcript.transcript)
```

**With Marketer (Social Snippets):**
```python
from superskills.transcriber.src import Transcriber
from superskills.marketer.src import SocialMediaPublisher

transcriber = Transcriber()
result = transcriber.transcribe("training.mp4", include_timestamps=True)

quotes = transcriber.extract_key_quotes(result, min_words=15, max_quotes=3)

publisher = SocialMediaPublisher()
for quote in quotes:
    publisher.schedule_post(quote, platforms=["TWITTER", "LINKEDIN"])
```

**With CoursePackager (Searchable Transcripts):**
```python
from superskills.transcriber.src import Transcriber

transcriber = Transcriber()
results = transcriber.transcribe_batch(
    ["lesson1.mp4", "lesson2.mp4", "lesson3.mp4"],
    output_format="json"
)
```
