---
name: video-recorder
description: Generate professional videos with branded slides and AI voiceover. Renders HTML presentations to video with synchronized audio using ElevenLabs TTS.
version: 1.0.0
type: python
python_module: superskills.video_recorder.src:VideoRecorder
license: MIT
---

# Video Recorder

> **Profile:** Review [PROFILE.md](PROFILE.md) for brand customization.  
> **Master Briefing:** Global brand at `~/.superskills/master-briefing.yaml` applies automatically.

Generate complete videos with branded slide presentations and professional voiceover.

## Purpose

Enable autonomous video generation for training materials, workshop recaps, educational content, and client explainer videos. Combines branded visual slides with AI-generated ElevenLabs voice for polished, professional output.

## Tools

**VideoRecorder.py** - Main orchestrator  
**SlideRenderer.py** - HTML slides to PNG frames (Playwright)  
**AudioGenerator.py** - Script to voiceover (ElevenLabs via narrator skill)  
**VideoEncoder.py** - Frame + audio assembly (FFmpeg)  
**TimingSync.py** - Slide-audio synchronization

## Core Workflow

1. **Generate Audio** - Convert script to voiceover via ElevenLabs
2. **Render Slides** - HTML templates → PNG frames (branded)
3. **Calculate Timing** - Distribute slides across audio duration
4. **Encode Video** - Assemble frames + audio → MP4

## Usage

### Basic Usage

```bash
superskills call video-recorder '{
  "script": "Welcome to this presentation. Today we cover three key topics.",
  "slides": [
    {"type": "title", "heading": "Welcome"},
    {"type": "content", "heading": "Topics", "bullets": ["Planning", "Execution", "Results"]}
  ],
  "output_name": "my_video"
}'
```

### Slide Types

**Title Slide:**
```json
{
  "type": "title",
  "heading": "Welcome",
  "subheading": "Optional subtitle"
}
```

**Content Slide:**
```json
{
  "type": "content",
  "heading": "Key Points",
  "bullets": ["Point 1", "Point 2", "Point 3"],
  "text": "Optional additional context"
}
```

**Image Slide:**
```json
{
  "type": "image",
  "heading": "Diagram",
  "image_url": "/path/to/image.png",
  "caption": "Optional caption text"
}
```

## Output

Returns JSON with:
- `video_path`: Full path to generated MP4
- `duration_seconds`: Total video duration
- `slide_count`: Number of slides
- `audio_path`: Path to voiceover audio
- `metadata`: Resolution, FPS, voice info

## Quality Standards

- **Resolution:** 1920x1080 (Full HD)
- **Format:** MP4 (H.264 video, AAC audio)
- **Audio:** 192kbps, clear voiceover
- **Branding:** Consistent colors, fonts, your brand signature (configured in brand/default.yaml)
- **Timing:** Slides distributed evenly across audio

## Examples

### Single Slide Test

```bash
superskills call video-recorder '{
  "script": "This is a test of the video recording system.",
  "slides": [{"type": "title", "heading": "Test Video"}],
  "output_name": "test"
}'
```

### Multi-Slide Presentation

```bash
superskills call video-recorder '{
  "script": "Welcome everyone. First, we discuss planning. Then implementation. Finally, results.",
  "slides": [
    {"type": "title", "heading": "Welcome", "subheading": "AI Video Generation"},
    {"type": "content", "heading": "Agenda", "bullets": ["Planning", "Implementation", "Results"]},
    {"type": "title", "heading": "Thank You"}
  ],
  "output_name": "presentation"
}'
```

## Dependencies

- **System:** FFmpeg (install via `brew install ffmpeg`)
- **Python:** playwright, ffmpeg-python, pydub, jinja2
- **Browser:** Chromium (install via `playwright install chromium`)
- **Voice:** ElevenLabs API key (via narrator skill)

## Limitations

- Static slides (no animations in MVP)
- Equal timing distribution (advanced timing in future)
- macOS/Linux/Windows compatible (Playwright cross-platform)
- Requires internet for voice generation

## Troubleshooting

**FFmpeg not found:**
- Install: `brew install ffmpeg`
- Verify: `ffmpeg -version`

**Playwright browser missing:**
- Install: `playwright install chromium`

**Voice generation fails:**
- Check narrator skill configuration
- Verify ElevenLabs API key in `~/.superskills/.env`

**Video encoding fails:**
- Check FFmpeg logs in error output
- Verify temp files in `.{output_name}_work/` directory
- Ensure sufficient disk space

## Future Enhancements

- Live window capture mode (using vision skill)
- Advanced timing with silence detection
- Slide transitions (fade, slide)
- Multiple voice support
- Background music
- CSS animations
- Auto-generated thumbnails
- Subtitle generation (SRT/VTT)
