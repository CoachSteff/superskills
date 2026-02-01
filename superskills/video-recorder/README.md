# Video Recorder SuperSkill

Generate professional videos with branded slides and AI voiceover.

## Overview

The **video-recorder** skill enables autonomous video generation by combining:
- Branded HTML slide presentations
- ElevenLabs TTS voiceover (CoachSteff's voice)
- Synchronized audio-visual output as MP4

**Use Cases:**
- Training videos
- Workshop recaps
- Educational content
- Client explainer videos
- Social media content

## Quick Start

### Installation

```bash
# Install system dependencies
brew install ffmpeg

# Install Python dependencies
cd superskills/video-recorder
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### Brand Customization

The video-recorder skill uses template files that you customize with your brand identity. **Personal brand files are gitignored** to protect your information.

**Setup steps:**

1. **Copy template files:**
   ```bash
   cd superskills/video-recorder
   cp PROFILE.md.template PROFILE.md
   cp brand/default.yaml.template brand/default.yaml
   ```

2. **Customize PROFILE.md:**
   - Replace `[Your Brand Name]` with your brand
   - Replace `[Your Program Name]` with your workshop/training name
   - Replace `[#YourHashtag]` with your branding hashtag
   - Review content guidelines and adjust to your style

3. **Customize brand/default.yaml:**
   - Set `identity.name` and `identity.tagline`
   - Configure `colors.primary` (your main brand color)
   - Set `logo.text` (fallback text when no logo file)
   - Optionally add your logo to `brand/assets/`
   - Configure timing preferences (slide durations)

4. **Add your logo (optional):**
   ```bash
   cp /path/to/your-logo.svg brand/assets/
   # Update brand/default.yaml: logo.file = "assets/your-logo.svg"
   ```

5. **Configure ElevenLabs voice:**
   - Set `ELEVENLABS_API_KEY` in `.env`
   - Set `ELEVENLABS_VOICE_ID` for your voice

**Protected files (gitignored):**
- `PROFILE.md` - Your personal content guidelines
- `brand/default.yaml` - Your brand configuration
- `brand/assets/*` - Your logo files

**Shared files (tracked in git):**
- `PROFILE.md.template` - Template for all users
- `brand/default.yaml.template` - Example configuration with full documentation
- `brand/assets/.gitkeep` - Directory structure

### Basic Usage

```bash
superskills call video-recorder '{
  "script": "Welcome to this presentation.",
  "slides": [
    {"type": "title", "heading": "Welcome"}
  ],
  "output_name": "my_video"
}'
```

## Input Schema

```json
{
  "script": "Narration text for voiceover",
  "slides": [
    {
      "type": "title|content|image",
      "heading": "Slide title",
      "subheading": "Optional subtitle (title slides)",
      "bullets": ["Item 1", "Item 2"],
      "text": "Additional text",
      "image_url": "/path/to/image.png",
      "caption": "Image caption",
      "duration_ms": 5000
    }
  ],
  "output_name": "video_name",
  "brand_config": "/path/to/custom/brand.yaml"
}
```

## Output Schema

```json
{
  "video_path": "/path/to/output.mp4",
  "duration_seconds": 45.2,
  "slide_count": 3,
  "audio_path": "/path/to/audio.mp3",
  "metadata": {
    "resolution": "1920x1080",
    "fps": 1,
    "voice": "steff",
    "profile_type": "podcast"
  }
}
```

## Brand Customization

Default brand uses CoachSteff's visual identity:
- **Primary Color:** DeepSkyBlue (#00BFFF)
- **Theme:** Dark (charcoal backgrounds, white text)
- **Signature:** CoachSteff watermark (bottom-right)
- **Accent Colors:** Red, yellow/gold, green

To customize, edit `brand/default.yaml` or provide `brand_config` path in input.

### Logo Customization

#### Using Image Logos (SVG/PNG)

Place your logo file in `brand/assets/` and reference in `brand/default.yaml`:

```yaml
logo:
  enabled: true
  file: "assets/logo.svg"    # Relative to brand/ directory
  position: "bottom-right"
  width: 200                 # Adjust size
  opacity: 0.9
```

**Supported Formats:**
- SVG (recommended - scalable)
- PNG (with transparency)
- JPG, WEBP

**Position Options:**
- `top-left`
- `top-right`
- `bottom-left`
- `bottom-right` (default)

#### Fallback Text Logo

If no image file is provided, falls back to text:

```yaml
logo:
  enabled: true
  file: null
  text: "CoachSteff"
  size: 36
  color: "#ffffff"
```

## Architecture

```
Script + Slides JSON
        ↓
    VideoRecorder
        ↓
   ┌────────────┬────────────┐
   ↓            ↓            ↓
SlideRenderer AudioGenerator TimingSync
   ↓            ↓            ↓
PNG Frames   MP3 Audio   Timing Map
   └────────────┴────────────┘
            ↓
       VideoEncoder
            ↓
         MP4 Output
```

## Components

### SlideRenderer
- Renders HTML templates to PNG frames using Playwright
- Applies brand configuration (colors, fonts, layout)
- Supports multiple slide types

### AudioGenerator
- Wraps narrator skill for ElevenLabs TTS
- Generates voiceover from script
- Measures audio duration for timing

### TimingSync
- Distributes slides evenly across audio duration
- Supports explicit duration overrides
- Calculates start times and durations

### VideoEncoder
- Assembles PNG frames into video using FFmpeg
- Syncs video with audio track
- Encodes as H.264 MP4

## Examples

### Training Video

```bash
superskills call video-recorder '{
  "script": "Welcome to AI adoption training. First, understand the landscape. Second, identify use cases. Finally, implement solutions.",
  "slides": [
    {"type": "title", "heading": "AI Adoption", "subheading": "A Practical Guide"},
    {"type": "content", "heading": "Steps", "bullets": ["Understand", "Identify", "Implement"]},
    {"type": "title", "heading": "Let'\''s Begin"}
  ],
  "output_name": "ai_training"
}'
```

### Social Media Post

```bash
superskills call video-recorder '{
  "script": "Ethics first. AI second. This is the foundation of responsible AI adoption.",
  "slides": [
    {"type": "title", "heading": "Ethics First", "subheading": "AI Second"}
  ],
  "output_name": "ethics_post"
}'
```

## Testing

### Validated Test Results (2026-01-31)

✅ **Single-Slide MVP Test**
- Command: `superskills call video-recorder '{...single slide...}'`
- Result: 61KB MP4, 3.2s duration, 1920x1080, branded DeepSkyBlue heading
- Status: ✓ PASSED

✅ **Multi-Slide Test**
- Command: `superskills call video-recorder '{...3 slides...}'`
- Result: 283KB MP4, 13.5s duration, H.264 + AAC, all slides rendered correctly
- Timing: 4.5s per slide (auto-distributed)
- Status: ✓ PASSED

### Running Tests

```bash
# Run unit tests
pytest superskills/video-recorder/tests/

# Quick integration test
superskills call video-recorder '{
  "script": "Test",
  "slides": [{"type": "title", "heading": "Test"}],
  "output_name": "test"
}'

# Verify output
ls -lh output/videos/test.mp4
ffprobe output/videos/test.mp4
```

## Performance

- **Rendering:** ~2-5 seconds per slide (Playwright)
- **Voice:** ~5-10 seconds (ElevenLabs API call)
- **Encoding:** ~5-15 seconds (FFmpeg, depends on duration)
- **Total:** ~15-45 seconds for 3-slide video

## Limitations

- Static slides only (MVP)
- 1 FPS encoding (sufficient for static content)
- Equal timing distribution (advanced timing future)
- Internet required for voice generation

## Troubleshooting

See [SKILL.md](SKILL.md#troubleshooting) for common issues and solutions.

## Future Enhancements

- Live window capture with vision skill
- Silence-based timing
- Slide transitions
- CSS animations
- Multiple voices
- Background music
- Subtitle generation

## License

MIT License - See LICENSE file for details.
