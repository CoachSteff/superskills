# Narrator Agent Tools

Professional voiceover generation for CoachSteff's AI voice using ElevenLabs API.

## Overview

The Narrator Agent provides Python tools for generating high-quality voiceovers:
- **Podcast.py** - Multi-segment podcast generation with audio stitching
- **Voiceover.py** - Single-segment voiceover generation with script optimization

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
export ELEVENLABS_VOICE_ID="your_voice_id_here"
```

## Usage

### Voiceover Generation

```python
from agents.narrator.src.Voiceover import VoiceoverGenerator

generator = VoiceoverGenerator()

result = generator.generate(
    script="Your script here",
    content_type="educational",  # or "marketing", "social", "podcast"
    optimize_script=True,
    output_filename="my-voiceover.mp3"
)

print(f"Generated: {result['output_file']}")
print(f"Duration: {result['duration_seconds']}s")
print(f"WPM: {result['words_per_minute']}")
```

### Podcast Generation

```python
from agents.narrator.src.Podcast import PodcastGenerator, PodcastSegment

generator = PodcastGenerator()

segments = [
    PodcastSegment(
        text="Welcome to the podcast!",
        content_type="podcast"
    ),
    PodcastSegment(
        text="Let me share three core principles...",
        content_type="educational"
    )
]

result = generator.generate_podcast(
    segments=segments,
    output_filename="episode-01.mp3",
    transition_ms=800
)
```

## Content Types

- **educational**: Clear, patient delivery (130-150 WPM)
- **marketing**: Energetic, persuasive (150-170 WPM)
- **social**: Fast-paced, attention-grabbing (160-180 WPM)
- **podcast**: Natural, conversational (140-160 WPM)

## Documentation

See `SKILL.md` for full agent capabilities, quality gates, and best practices.
