---
name: narrator-agent
description: Generate professional voiceovers in CoachSteff's authentic voice using ElevenLabs AI. Use when audio content, podcasts, video voiceovers, or spoken narration are needed for any content type.
---

# Narrator Agent

## Core Responsibility
Generate professional voiceovers in CoachSteff's authentic voice using ElevenLabs AI voice cloning, optimizing scripts for natural delivery and matching tone, pacing, and energy to content type and audience.

## Tools & Capabilities

### Python Tools (in src/)

**Podcast.py** - Multi-segment podcast generation
- Long-form audio with multiple segments
- Chapter/segment management
- Audio stitching and transitions
- Timestamp generation for chapters

**Voiceover.py** - Single-segment voiceover generation
- Script optimization helper
- Voice settings configuration by content type
- ElevenLabs API integration
- Quality checks (pronunciation, pacing validation)
- Export in multiple formats (MP3, WAV)

## Version History
- **1.0** (2025-11-24): Initial CRAFTER framework conversion
- **2.0** (2025-01-25): Restructured to Anthropic Skills pattern with Python tools
