---
name: slide-designer
description: Design and generate branded HTML slide decks from scripts, outlines, or specifications. Outputs video-ready slides for the video-recorder skill.
version: 1.0.0
type: python
python_module: superskills.slide_designer.src:SlideDesigner
license: MIT
---

# Slide Designer

> **Profile:** Review [PROFILE.md](PROFILE.md) for brand customization and design rules.

Transform content into visually designed HTML slides optimized for video production.

## Purpose

Bridge the gap between content creation and video production. Takes scripts, outlines, or structured content and generates professionally branded HTML slides ready for the `video-recorder` skill.

## Tools

**SlideDesigner.py** - Main orchestrator
**ContentAnalyzer.py** - Script → slide structure
**LayoutSelector.py** - Choose optimal layouts
**StyleEngine.py** - Apply brand styling
**HTMLGenerator.py** - Render to HTML

## Core Workflow

1. **Analyze Content** - Parse input, identify slide boundaries
2. **Select Layouts** - Match content type to visual template
3. **Apply Branding** - Your brand colors, typography, logo (configured in PROFILE.md and brand/default.yaml)
4. **Generate HTML** - Standalone files, 1920x1080 viewport

## Usage

### From Script (Auto-Chunking)

```python
from superskills.slide_designer import SlideDesigner

designer = SlideDesigner(output_dir="output/slides", theme="dark")
result = designer.design_from_script(
    script="Welcome to AI automation. Today we learn three key concepts: prompt engineering, personalization, and your second brain.",
    title="AI Automation Workshop",
    output_name="workshop_slides"
)

print(f"Created {result.slide_count} slides")
print(f"Combined deck: {result.combined_html}")
```

### From Outline (Markdown Structure)

```python
outline = """
# Welcome
## AI Automation Workshop

# Topics
- Prompt engineering
- Personalization
- Second brain
"""

result = designer.design_from_outline(
    outline=outline,
    output_name="workshop_slides"
)
```

### From Specifications (Explicit Control)

```python
slides = [
    {"type": "title", "heading": "AI Automation", "subheading": "[Your Brand Tagline]"},
    {"type": "content", "heading": "Today We Learn", "bullets": ["Prompt engineering", "Personalization", "Second brain"]},
    {"type": "question", "heading": "What do you want to learn?"}
]

result = designer.design_from_specs(
    slides=slides,
    output_name="workshop_slides"
)
```

## Slide Types

| Type | Use Case | Key Fields |
|------|----------|------------|
| `title` | Opening, transitions | heading, subheading |
| `content` | Main information | heading, bullets, text |
| `question` | Engagement | heading, bullets (optional follow-ups) |
| `image` | Visuals, diagrams | heading, image_url, caption |
| `quote` | Testimonials | quote_text, quote_author |

## Output

Returns DesignResult with:
- `html_files`: List of individual slide HTML paths
- `combined_html`: Path to full deck (all slides)
- `slide_count`: Number of slides generated
- `estimated_duration_seconds`: Based on content density
- `slides`: List of SlideSpec objects

## Integration with video-recorder

```python
from superskills.slide_designer import SlideDesigner
from superskills.video_recorder import VideoRecorder

designer = SlideDesigner()
result = designer.design_from_script(
    script="Your presentation script here...",
    title="My Presentation"
)

recorder = VideoRecorder()
video_result = recorder.record_video(
    script="Your presentation script here...",
    slides_html=str(result.combined_html)
)
```

## Quality Standards

- **Resolution:** 1920x1080 (Full HD video-ready)
- **Density:** 3-5 bullets per slide, 5-12 words per bullet
- **Timing:** Optimized for 10-15 seconds per slide
- **Branding:** Your brand colors, logo, typography (configured in brand/default.yaml)

## Dependencies

- **Python:** jinja2, pyyaml, markdown
- **Optional:** playwright (for validation screenshots)

## Troubleshooting

**Templates not found:**
- Ensure `templates/` directory exists with all .html.j2 files

**Brand config missing:**
- Check `brand/default.yaml` exists
- Or provide custom path via `brand_config` parameter

**Output too many slides:**
- Reduce input content or increase `max_slides` parameter
- Default: 7 slides maximum
