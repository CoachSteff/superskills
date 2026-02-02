---
name: narrator-podcast
description: Generate professional podcast voiceovers with conversational, warm tone (140-160 WPM). Optimized for natural, engaging delivery in multi-segment episodes.
---

# Narrator: Podcast Specialist

> **Note**: Review `PROFILE.md` in this folder for podcast-specific voice settings and delivery guidelines.

Generate professional podcast voiceovers optimized for conversational, authentic delivery using ElevenLabs AI voice cloning.

## Tools

**Voiceover.py** (in ../src/):
- Single-segment voiceover generation
- Script optimization for conversational speech
- Podcast-optimized voice settings
- ElevenLabs API integration
- Quality checks (naturalness, pacing)
- Export formats (MP3, WAV)

**Podcast.py** (in ../src/):
- Multi-segment podcast generation
- Chapter/segment management
- Audio stitching and transitions
- Timestamp generation
- Long-form audio production

## Podcast Delivery Characteristics

**Target WPM**: 140-160 words per minute
**Tone**: Warm, conversational, authentic
**Energy**: Natural and engaging
**Pacing**: Relaxed with natural pauses

**Voice Profile**: Configured in parent skill's `voice_profiles.json` (podcast profile)
- See PROFILE.md for conversational style guidance
- Technical settings managed centrally

## Core Workflow

### 1. Script Review
- Receive podcast script or outline
- Check for conversational flow
- Identify natural break points for segments
- Review for pronunciation challenges

### 2. Voice Generation
- Optimize script for spoken, conversational delivery
- Apply podcast voice profile settings
- Generate voiceover with natural pacing
- Review for authenticity and warmth
- Re-generate problematic segments

### 3. Delivery
- Export in MP3 format for podcast distribution
- Package with metadata (duration, WPM, segment timestamps)
- Handoff to producer for final podcast assembly

## Quality Checklist

- [ ] Script sounds conversational (not scripted/robotic)
- [ ] Pacing feels natural (140-160 WPM)
- [ ] Tone is warm and authentic
- [ ] Natural pauses at appropriate points
- [ ] Emphasis on key points feels organic
- [ ] No awkward AI pronunciations
- [ ] Audio quality high (no artifacts)
- [ ] Segment transitions smooth

## Script Optimization for Podcasts

**Best Practices:**
- Write exactly how you speak (use contractions)
- Keep sentences short for breathing room
- Use ellipses (...) for natural pauses
- Spell out numbers ("twenty-five" not "25")
- Add phonetic spelling for tricky words
- Include natural filler where appropriate ("you know", "right?")

**Example Optimized Script:**
```
Welcome back to the show... I'm [Your Name], and today we're diving into 
something I've been thinking about a lot lately.

You know how we all struggle with staying focused? Well, I've got 
three simple principles that changed everything for me. And I think 
they'll work for you too.

Let's start with the first one...
```

**Avoid:**
- Formal, written language
- Long, complex sentences
- Unnatural transitions
- Over-scripted delivery

## Using the Podcast Generator

```python
from src.Podcast import PodcastGenerator, PodcastSegment

generator = PodcastGenerator()

segments = [
    PodcastSegment(
        text="Welcome to the show...",
        content_type="podcast"
    ),
    PodcastSegment(
        text="Today's main topic...",
        content_type="podcast"
    )
]

result = generator.generate_podcast(
    segments=segments,
    output_filename="episode-01.mp3",
    transition_ms=800
)
```

## Avoid

- **Scripted Reading**: Formal writing → Conversational, natural speech
- **Too Fast**: Rushing → 140-160 WPM pacing
- **Monotone**: Flat delivery → Warm, engaging tone
- **No Pauses**: Continuous speech → Natural breathing room

## Escalate When

- Script feels too formal or written
- Pronunciation challenges with guest names or terms
- Segment transitions feel abrupt
- Voice quality doesn't match podcast tone
- Timeline doesn't allow for quality review
