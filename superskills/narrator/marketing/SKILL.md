---
name: narrator-marketing
description: Generate energetic, persuasive marketing voiceovers (150-170 WPM). Optimized for promotional content, ads, and sales materials with confident, motivating delivery.
---

# Narrator: Marketing Specialist

> **Note**: Review `PROFILE.md` in this folder for marketing-specific voice settings and delivery guidelines.

Generate professional marketing voiceovers optimized for energetic, persuasive delivery using ElevenLabs AI voice cloning.

## Tools

**Voiceover.py** (in ../src/):
- Single-segment marketing voiceover generation
- Script optimization for persuasive impact
- Marketing-optimized voice settings
- ElevenLabs API integration
- Quality checks (energy, persuasion)
- Export formats (MP3, WAV)

## Marketing Delivery Characteristics

**Target WPM**: 150-170 words per minute
**Tone**: Confident, persuasive, motivating
**Energy**: High and engaging
**Pacing**: Dynamic with strategic emphasis

**Voice Profile**: CoachSteff Basic (narration optimized)
- Stability: 0.70
- Similarity Boost: 0.80
- Style: 0.30
- Speed: 1.0

## Core Workflow

### 1. Script Review
- Receive marketing copy or promotional script
- Identify key selling points and CTAs
- Review for persuasive flow and energy
- Check brand voice alignment

### 2. Voice Generation
- Optimize script for persuasive delivery
- Apply marketing voice profile settings
- Generate voiceover with dynamic energy
- Review for confidence and motivation
- Re-generate low-energy segments

### 3. Delivery
- Export in required format (MP3 for ads, WAV for video)
- Package with metadata (duration, WPM, CTA timing)
- Handoff to marketer or video editor

## Quality Checklist

- [ ] Energy level high and engaging
- [ ] Pacing creates urgency without rushing (150-170 WPM)
- [ ] Tone is confident and persuasive
- [ ] Key benefits emphasized effectively
- [ ] CTA (Call-to-Action) clear and compelling
- [ ] Brand voice maintained throughout
- [ ] Audio quality professional (no artifacts)
- [ ] Overall delivery motivating and actionable

## Script Optimization for Marketing

**Best Practices:**
- Start with a strong hook
- Emphasize benefits over features
- Use power words (transform, discover, unlock)
- Build to clear call-to-action
- Keep sentences punchy and direct
- Create momentum through pacing

**Example Optimized Script:**
```
Imagine cutting your workflow time in half. That's exactly what 
SuperSkills delivers.

No more jumping between tools. No more wasted hours. Just powerful 
AI skills that work the way you do.

Transform your productivity today. Get started with SuperSkills... 
and see results in minutes, not hours.

Ready to supercharge your workflow? Visit superskills dot io now.
```

**Avoid:**
- Weak, passive language
- Buried benefits
- Unclear or weak CTAs
- Monotone delivery
- Over-complicating the message

## Using the Marketing Generator

```python
from src.Voiceover import VoiceoverGenerator

generator = VoiceoverGenerator(profile_type="narration")

result = generator.generate(
    script="Transform your business with...",
    content_type="marketing",
    optimize_script=True,
    output_filename="promo-video.mp3"
)

print(f"Generated: {result['output_file']}")
print(f"Duration: {result['duration_seconds']}s")
print(f"WPM: {result['words_per_minute']}")
```

## Marketing Content Types

**Promotional Videos:**
- Strong hook in first 3 seconds
- Benefits-focused messaging
- Clear, compelling CTA
- WPM: 155-165

**Product Demos:**
- Problem-solution framework
- Feature highlights with benefits
- Urgency and scarcity elements
- WPM: 150-160

**Testimonial Voiceovers:**
- Authentic, credible tone
- Social proof emphasis
- Emotional connection
- WPM: 145-155

**Sales Pages:**
- Value proposition clarity
- Objection handling
- Multiple CTAs
- WPM: 160-170

## Persuasion Techniques

**AIDA Framework:**
- **Attention**: Strong hook
- **Interest**: Compelling benefits
- **Desire**: Emotional appeal
- **Action**: Clear CTA

**Power Words:**
- Transform, Unlock, Discover, Proven, Guaranteed
- Exclusive, Limited, Revolutionary, Effortless
- Instant, Simple, Powerful, Results

**Energy Peaks:**
- Build energy toward key benefits
- Peak energy at CTA
- Vary pacing for emphasis

## Avoid

- **Low Energy**: Flat delivery → Dynamic, engaging enthusiasm
- **Feature Dumping**: Technical specs → Benefits and transformation
- **Weak CTAs**: Passive suggestions → Clear, direct action steps
- **Too Slow**: Dragging pace → 150-170 WPM momentum

## Escalate When

- Brand voice guidelines unclear
- Target audience not defined (B2B vs B2C)
- CTA timing critical for video sync
- Multiple versions needed (A/B testing)
- Legal compliance review required
