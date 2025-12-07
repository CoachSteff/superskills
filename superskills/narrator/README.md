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

### Environment Variables

Set the following environment variable:

```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

**Global .env (repository root):**
```bash
echo "ELEVENLABS_API_KEY=your-key" >> .env
```

**Or skill-specific .env (superskills/narrator/.env):**
```bash
echo "ELEVENLABS_API_KEY=your-key" >> superskills/narrator/.env
```

The skill-specific `.env` file takes priority and allows this skill to work independently with its own credentials.

### Voice Profiles

Voice profiles are configured in `voice_profiles.json` in the narrator directory. Each profile defines:
- **voice_id**: ElevenLabs voice ID
- **voice_name**: Descriptive name
- **language**: Target language
- **model**: ElevenLabs model (e.g., `eleven_multilingual_v2`, `eleven_flash_v2_5`)
- **speed**: Speaking speed (0.7-1.2, default 1.0)
- **stability**: Voice stability (0.0-1.0)
- **similarity_boost**: Voice clarity/similarity (0.0-1.0)
- **style**: Style exaggeration (0.0-1.0)

**Available profiles:**
- `narration` - For educational/marketing/social content
- `podcast` - For podcast content
- `meditation` - For meditation/relaxation content

**Example voice_profiles.json:**
```json
{
  "narration": {
    "voice_id": "SMMOjVQfdxsjkBbDKPWy",
    "voice_name": "Steff Basic",
    "language": "Nederlands",
    "model": "eleven_multilingual_v2",
    "speed": 0.85,
    "stability": 0.40,
    "similarity_boost": 0.97,
    "style": 0.12
  },
  "podcast": {
    "voice_id": "Y8liEJ0I1PUVRbGdbUbn",
    "voice_name": "Steff Pro",
    "language": "English (British)",
    "model": "eleven_multilingual_v2",
    "speed": 0.90,
    "stability": 0.35,
    "similarity_boost": 0.97,
    "style": 0.17
  }
}
```

If `voice_profiles.json` is not found, the system falls back to `ELEVENLABS_VOICE_ID` environment variable with default settings.

## Usage

### Voiceover Generation

```python
from agents.narrator.src.Voiceover import VoiceoverGenerator

# Use default profile (narration)
generator = VoiceoverGenerator()

# Or specify a profile
generator = VoiceoverGenerator(profile_type="podcast")

result = generator.generate(
    script="Your script here",
    content_type="educational",  # or "marketing", "social", "podcast", "meditation"
    optimize_script=True,
    output_filename="my-voiceover.mp3"
)

print(f"Generated: {result['output_file']}")
print(f"Duration: {result['duration_seconds']}s")
print(f"WPM: {result['words_per_minute']}")
print(f"Profile: {result['profile']}")
```

### Podcast Generation

```python
from agents.narrator.src.Podcast import PodcastGenerator, PodcastSegment

# Use default profile (podcast)
generator = PodcastGenerator()

# Or specify a profile
generator = PodcastGenerator(profile_type="meditation")

segments = [
    PodcastSegment(
        text="Welcome to the podcast!",
        content_type="podcast"
    ),
    PodcastSegment(
        text="Let me share three core principles...",
        content_type="educational"
    ),
    # Override profile for a specific segment
    PodcastSegment(
        text="Take a deep breath and relax...",
        profile_type="meditation"
    )
]

result = generator.generate_podcast(
    segments=segments,
    output_filename="episode-01.mp3",
    transition_ms=800
)
```

## Content Types

Content types automatically map to voice profiles:
- **educational**: Uses `narration` profile - Clear, patient delivery
- **marketing**: Uses `narration` profile - Energetic, persuasive
- **social**: Uses `narration` profile - Fast-paced, attention-grabbing
- **podcast**: Uses `podcast` profile - Natural, conversational
- **meditation**: Uses `meditation` profile - Calm, soothing

## Documentation

See `SKILL.md` for full agent capabilities, quality gates, and best practices.
