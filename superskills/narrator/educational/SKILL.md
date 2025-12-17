---
name: narrator-educational
description: Generate clear, patient educational voiceovers (130-150 WPM). Optimized for courses, tutorials, and instructional content with authoritative, calm delivery.
---

# Narrator: Educational Specialist

> **Note**: Review `PROFILE.md` in this folder for educational-specific voice settings and delivery guidelines.

Generate professional educational voiceovers optimized for clear, patient instruction using ElevenLabs AI voice cloning.

## Tools

**Voiceover.py** (in ../src/):
- Single-segment educational voiceover generation
- Script optimization for instructional clarity
- Educational-optimized voice settings
- ElevenLabs API integration
- Quality checks (clarity, pacing)
- Export formats (MP3, WAV)

## Educational Delivery Characteristics

**Target WPM**: 130-150 words per minute
**Tone**: Calm, authoritative, patient
**Energy**: Measured and clear
**Pacing**: Deliberate with pauses for comprehension

**Voice Profile**: CoachSteff Basic (narration optimized)
- Stability: 0.70
- Similarity Boost: 0.80
- Style: 0.30
- Speed: 1.0

## Core Workflow

### 1. Script Review
- Receive educational script or course content
- Identify key learning points
- Review technical terms and pronunciation
- Check for clarity and logical flow

### 2. Voice Generation
- Optimize script for instructional delivery
- Apply educational voice profile settings
- Generate voiceover with clear pacing
- Review for clarity and authority
- Re-generate unclear segments

### 3. Delivery
- Export in required format (MP3 for courses, WAV for video sync)
- Package with metadata (duration, WPM, key topics)
- Handoff to course packager or video editor

## Quality Checklist

- [ ] Pronunciation of technical terms accurate
- [ ] Pacing allows for comprehension (130-150 WPM)
- [ ] Tone is calm and authoritative
- [ ] Key concepts emphasized appropriately
- [ ] Transitions between topics clear
- [ ] No rushed or confusing moments
- [ ] Audio quality high (no artifacts)
- [ ] Overall delivery feels patient and supportive

## Script Optimization for Education

**Best Practices:**
- Break complex concepts into simple steps
- Use clear transitions between topics
- Emphasize key terms on first mention
- Include brief pauses after important points
- Spell out technical terms phonetically if needed
- Number steps explicitly ("First...", "Second...")

**Example Optimized Script:**
```
In this lesson, we'll learn three fundamental principles of 
time management.

First... the principle of prioritization. This means focusing on 
what truly matters, rather than what feels urgent.

Let's look at a practical example...

[pause]

The second principle is time blocking. Here's how it works...
```

**Avoid:**
- Rushing through complex concepts
- Assuming prior knowledge
- Skipping transitions
- Technical jargon without explanation
- Long, unbroken explanations

## Using the Educational Generator

```python
from src.Voiceover import VoiceoverGenerator

generator = VoiceoverGenerator(profile_type="narration")

result = generator.generate(
    script="In this lesson, we'll explore...",
    content_type="educational",
    optimize_script=True,
    output_filename="lesson-01.mp3"
)

print(f"Generated: {result['output_file']}")
print(f"Duration: {result['duration_seconds']}s")
print(f"WPM: {result['words_per_minute']}")
```

## Educational Content Types

**Course Lessons:**
- Structured, logical flow
- Clear learning objectives
- Recaps and summaries
- WPM: 130-140

**Tutorials:**
- Step-by-step instructions
- Practical demonstrations
- Verification points
- WPM: 140-150

**Explainer Videos:**
- Concept introduction
- Visual synchronization points
- Clear conclusions
- WPM: 135-145

**Training Materials:**
- Professional, authoritative tone
- Compliance or certification focus
- Assessment preparation
- WPM: 130-140

## Avoid

- **Too Fast**: Rushing → 130-150 WPM pacing
- **Unclear Terms**: Jargon → Plain explanations
- **Monotone**: Flat delivery → Calm but engaging authority
- **No Structure**: Rambling → Clear, logical progression

## Escalate When

- Script has complex technical terms needing pronunciation guide
- Content requires visual synchronization timing
- Target audience level unclear (beginner vs advanced)
- Assessment or quiz content needs special treatment
- Timeline doesn't allow for quality review
