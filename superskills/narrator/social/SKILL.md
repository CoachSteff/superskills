---
name: narrator-social
description: Generate fast-paced, attention-grabbing social media voiceovers (160-180 WPM). Optimized for short-form content, reels, and viral-style delivery.
---

# Narrator: Social Media Specialist

> **Note**: Review `PROFILE.md` in this folder for social media-specific voice settings and delivery guidelines.

Generate professional social media voiceovers optimized for fast-paced, engaging delivery using ElevenLabs AI voice cloning.

## Tools

**Voiceover.py** (in ../src/):
- Single-segment social media voiceover generation
- Script optimization for viral-style delivery
- Social-optimized voice settings
- ElevenLabs API integration
- Quality checks (energy, hook strength)
- Export formats (MP3, WAV)

## Social Media Delivery Characteristics

**Target WPM**: 160-180 words per minute
**Tone**: Dynamic, engaging, relatable
**Energy**: High and attention-grabbing
**Pacing**: Fast with punchy delivery

**Voice Profile**: CoachSteff Basic (narration optimized)
- Stability: 0.70
- Similarity Boost: 0.80
- Style: 0.30
- Speed: 1.0

## Core Workflow

### 1. Script Review
- Receive social media script or hook
- Identify attention-grabbing opening
- Review for platform requirements (TikTok, Reels, Shorts)
- Check length constraints (15s, 30s, 60s)

### 2. Voice Generation
- Optimize script for rapid, engaging delivery
- Apply social media voice profile settings
- Generate voiceover with high energy
- Review for hook strength and pacing
- Re-generate if energy drops

### 3. Delivery
- Export in MP3 format for social platforms
- Package with metadata (duration, WPM, hook timing)
- Handoff to social media manager or video editor

## Quality Checklist

- [ ] Hook grabs attention in first 2 seconds
- [ ] Pacing feels urgent and engaging (160-180 WPM)
- [ ] Energy remains high throughout
- [ ] Delivery feels authentic and relatable
- [ ] Key message clear despite speed
- [ ] Fits platform time constraints
- [ ] Audio quality mobile-optimized
- [ ] Overall vibe shareable and viral-worthy

## Script Optimization for Social Media

**Best Practices:**
- Start with a pattern interrupt or question
- Front-load the value proposition
- Use short, punchy sentences
- Create urgency and FOMO
- End with a hook or CTA
- Write for retention (hold attention)

**Example Optimized Script (30s Reel):**
```
Stop scrolling. I just discovered something that'll change how you 
work forever.

Imagine having forty AI experts on demand. Copywriters. Designers. 
Developers. All in one CLI.

I used it to build an entire podcast workflow in five minutes. 
No code. No complexity. Just results.

This is SuperSkills... and it's completely free.

Link in bio. You're welcome.
```

**Avoid:**
- Slow introductions or preamble
- Complex explanations
- Low energy delivery
- Unclear value proposition
- Weak or missing hooks

## Using the Social Media Generator

```python
from src.Voiceover import VoiceoverGenerator

generator = VoiceoverGenerator(profile_type="narration")

result = generator.generate(
    script="Stop scrolling. I just discovered...",
    content_type="social",
    optimize_script=True,
    output_filename="tiktok-demo.mp3"
)

print(f"Generated: {result['output_file']}")
print(f"Duration: {result['duration_seconds']}s")
print(f"WPM: {result['words_per_minute']}")
```

## Platform-Specific Guidelines

**TikTok / Instagram Reels:**
- 15-30 second sweet spot
- Vertical format consideration
- Hook in first 1-2 seconds
- WPM: 165-180

**YouTube Shorts:**
- 30-60 second format
- Strong retention curve
- Mid-roll engagement hook
- WPM: 160-175

**LinkedIn / Twitter Video:**
- 30-45 seconds optimal
- Professional yet engaging
- Value-first messaging
- WPM: 155-170

**Stories (Instagram/Facebook):**
- 7-15 seconds
- Direct, personal tone
- Swipe-up or link CTA
- WPM: 170-180

## Viral Content Patterns

**Hook Templates:**
- "Stop scrolling..."
- "I can't believe this actually works..."
- "Here's what nobody tells you about..."
- "Wait... did you know..."
- "This changed everything..."

**Retention Tactics:**
- Pattern interrupt opening
- Promise specific value quickly
- Tease upcoming information
- Use visual text cues
- End with open loop or CTA

**Pacing Strategy:**
- Fast start (grab attention)
- Quick value delivery
- Build to payoff or CTA
- No dead air or slow moments

## Avoid

- **Slow Start**: Rambling intro → Immediate hook
- **Too Formal**: Corporate tone → Relatable, authentic voice
- **Low Energy**: Monotone → Fast, dynamic delivery
- **Too Long**: Over-explaining → Punchy, concise messaging

## Escalate When

- Platform specs unclear (aspect ratio, length)
- Audience targeting needs refinement
- Trending audio integration needed
- Multi-variant testing required
- Hook testing and optimization needed
