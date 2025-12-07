---
name: narrator
description: Generate professional voiceovers in the user's voice using ElevenLabs AI. Use when creating audio for videos, podcasts, courses, or any content requiring spoken narration.
---

# Narrator

> **Note**: Review `PROFILE.md` in this skill folder for user-specific voice settings, content type preferences, and script optimization guidelines.

Generate professional voiceovers in the user's authentic voice using ElevenLabs AI voice cloning, optimizing scripts for natural delivery.

## Tools

**Voiceover.py** (in src/):
- Single-segment voiceover generation
- Script optimization for natural speech
- Voice settings by content type
- ElevenLabs API integration
- Quality checks (pronunciation, pacing)
- Export formats (MP3, WAV)

**Podcast.py** (in src/):
- Multi-segment podcast generation
- Chapter/segment management
- Audio stitching and transitions
- Timestamp generation
- Long-form audio production

## Core Workflow

### 1. Script Review
- Receive script from author
- Identify content type (educational, marketing, social, podcast)
- Review for voice optimization opportunities

### 2. Voice Generation
- Optimize script for natural spoken delivery
- Select appropriate voice settings for content type
- Generate voiceover using ElevenLabs
- Review for pronunciation, pacing, emphasis
- Re-generate if needed

### 3. Delivery
- Export in required format (MP3 for distribution, WAV for master)
- Package with metadata (duration, WPM, content type)
- Handoff to producer for video sync or podcast production

## Quality Checklist

- [ ] Script optimized for spoken delivery (natural flow)
- [ ] Appropriate content type settings applied
- [ ] Pronunciation accurate (no awkward AI pronunciations)
- [ ] Pacing appropriate (not too fast/slow)
- [ ] Emphasis on key points effective
- [ ] Audio quality high (no artifacts)
- [ ] Export format correct for use case

## Content Type Settings

**Educational**:
- Clear, patient delivery
- 130-150 WPM
- Calm, authoritative tone

**Marketing**:
- Energetic, persuasive
- 150-170 WPM
- Confident, motivating tone

**Social**:
- Fast-paced, attention-grabbing
- 160-180 WPM
- Dynamic, engaging tone

**Podcast**:
- Natural, conversational
- 140-160 WPM
- Warm, authentic tone

## Using Voiceover Generator

```python
from src.Voiceover import VoiceoverGenerator

generator = VoiceoverGenerator()

result = generator.generate(
    script="Your script here",
    content_type="educational",
    optimize_script=True,
    output_filename="voiceover.mp3"
)

print(f"Generated: {result['output_file']}")
print(f"Duration: {result['duration_seconds']}s")
print(f"WPM: {result['words_per_minute']}")
```

## Using Podcast Generator

```python
from src.Podcast import PodcastGenerator, PodcastSegment

generator = PodcastGenerator()

segments = [
    PodcastSegment(
        text="Welcome to the podcast!",
        content_type="podcast"
    ),
    PodcastSegment(
        text="Let me share three principles...",
        content_type="educational"
    )
]

result = generator.generate_podcast(
    segments=segments,
    output_filename="episode-01.mp3",
    transition_ms=800
)
```

## Script Optimization Tips

**For Natural Delivery:**
- Write how you speak (contractions, casual language)
- Use short sentences for breathing room
- Add punctuation for pausing (commas, periods, ellipses)
- Spell out numbers ("twenty-five" not "25")
- Phonetic spelling for difficult words
- Mark emphasis with CAPS or **bold** (implementation-dependent)

**Avoid:**
- Long run-on sentences
- Complex technical jargon without pronunciation guide
- Acronyms without expansion on first use
- Awkward phrasing that sounds unnatural

## Avoid

- **Robotic Scripts**: Written text → Conversational, spoken language
- **Wrong Pacing**: One-size settings → Match content type to appropriate WPM and tone
- **Skip Review**: Auto-publish → Review for pronunciation, pacing issues
- **Poor Format**: Wrong export → MP3 for distribution, WAV for master archive

## Escalate When

- Script too complex or technical (needs simplification)
- Voice quality issues persist (may need ElevenLabs support)
- Pronunciation challenges with key terms (needs phonetic guidance)
- Content type unclear (affects voice settings)
- Timeline unrealistic for quality review
