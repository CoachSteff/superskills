---
name: narrator-meditation
description: Generate calm, soothing meditation voiceovers with slow, deliberate pacing. Optimized for relaxation, mindfulness, and guided meditation content.
---

# Narrator: Meditation Specialist

> **Note**: Review `PROFILE.md` in this folder for meditation-specific voice settings and delivery guidelines.

Generate professional meditation voiceovers optimized for calm, soothing delivery using ElevenLabs AI voice cloning.

## Tools

**Voiceover.py** (in ../src/):
- Single-segment meditation guide generation
- Script optimization for meditative pacing
- Meditation-optimized voice settings
- ElevenLabs API integration
- Quality checks (calmness, flow)
- Export formats (MP3, WAV)

## Meditation Delivery Characteristics

**Target Pacing**: Slow and deliberate (varies by meditation type)
**Tone**: Calm, soothing, peaceful
**Energy**: Gentle and grounding
**Pausing**: Extended pauses for breathing and reflection

**Voice Profile**: Calm Meditation Voice
- Stability: 0.12 (high variation for natural softness)
- Similarity Boost: 0.97 (maximum authenticity)
- Style: 0.97 (expressive, gentle)
- Speed: 0.95 (slightly slower)

## Core Workflow

### 1. Script Review
- Receive meditation script or outline
- Identify pause points for breathing/reflection
- Review pacing and energy requirements
- Check for calming language patterns

### 2. Voice Generation
- Optimize script for meditative delivery
- Apply calm meditation voice profile
- Generate voiceover with deliberate pacing
- Review for soothing quality and flow
- Re-generate if energy feels too high

### 3. Delivery
- Export in MP3 format for meditation apps/courses
- Package with metadata (duration, meditation type)
- Handoff for background music integration (if needed)

## Quality Checklist

- [ ] Voice feels calm and soothing
- [ ] Pacing is slow and deliberate
- [ ] Pauses are long enough for breathing
- [ ] Tone remains gentle throughout
- [ ] No rushed or tense moments
- [ ] Pronunciation soft and clear
- [ ] Audio quality pristine (no artifacts)
- [ ] Overall energy grounding and peaceful

## Script Optimization for Meditation

**Best Practices:**
- Use extended ellipses (...) for breathing pauses
- Keep sentences simple and flowing
- Repeat key calming phrases
- Use present tense and direct address
- Include explicit pause instructions
- Choose soft, gentle vocabulary

**Example Optimized Script:**
```
Take a deep breath in... and slowly release...

Notice how your body feels in this moment... without judgment... 
just observing...

With each breath... you're becoming more relaxed... more at peace...

Let any tension in your shoulders melt away... slowly... gently...

There's nowhere you need to be... nothing you need to do... 
just breathe...
```

**Avoid:**
- Rushed instructions
- Complex or technical language
- Abrupt transitions
- High-energy phrasing
- Unnecessary details

## Using the Meditation Generator

```python
from src.Voiceover import VoiceoverGenerator

generator = VoiceoverGenerator(profile_type="meditation")

result = generator.generate(
    script="Take a deep breath in... and slowly release...",
    content_type="meditation",
    optimize_script=True,
    output_filename="morning-meditation.mp3"
)

print(f"Generated: {result['output_file']}")
print(f"Duration: {result['duration_seconds']}s")
```

## Meditation Types

**Breathing Meditation:**
- Focus on breath awareness
- Simple, repetitive instructions
- Long pauses between guidance

**Body Scan:**
- Systematic body awareness
- Gentle direction through body parts
- Slow, flowing transitions

**Visualization:**
- Descriptive, calming imagery
- Sensory language
- Spacious pacing for imagination

**Mindfulness:**
- Present-moment awareness
- Non-judgmental observation
- Gentle reminders to return to breath

## Avoid

- **Rushed Delivery**: Fast pacing → Slow, deliberate speech
- **Too Much Energy**: Enthusiastic tone → Calm, soothing presence
- **Short Pauses**: Quick transitions → Extended breathing space
- **Complex Language**: Technical terms → Simple, accessible words

## Escalate When

- Script feels too busy or complex
- Pacing doesn't allow for proper breathing pauses
- Voice quality lacks soothing quality
- Background music integration needed
- Meditation type requires specialized guidance
