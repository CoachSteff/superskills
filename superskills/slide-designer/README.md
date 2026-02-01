# Slide Designer SuperSkill

Technical documentation for the slide-designer SuperSkill.

## Overview

The slide-designer SuperSkill transforms content (scripts, outlines, or structured data) into professionally branded HTML slide decks optimized for video production.

## Architecture

```
Content Input → ContentAnalyzer → LayoutSelector → StyleEngine → HTMLGenerator → HTML Output
                                                          ↑
                                                    Brand Config
```

### Components

1. **SlideDesigner.py** - Main orchestrator class
2. **ContentAnalyzer.py** - Parses and chunks content into slides
3. **LayoutSelector.py** - Selects optimal layout for each slide
4. **StyleEngine.py** - Loads brand config and generates CSS
5. **HTMLGenerator.py** - Renders Jinja2 templates to HTML

## Installation

```bash
cd superskills/slide-designer
pip install -r requirements.txt
```

### Dependencies

- jinja2>=3.1.0
- pyyaml>=6.0
- markdown>=3.4.0

## Brand Customization

The slide-designer skill uses template files that you customize with your brand identity. **Personal brand files are gitignored** to protect your information.

### Quick Setup

1. **Copy template files:**
   ```bash
   cd superskills/slide-designer
   cp PROFILE.md.template PROFILE.md
   cp brand/default.yaml.template brand/default.yaml
   ```

2. **Customize PROFILE.md:**
   - Replace `[Your Brand Name]` with your brand
   - Replace `[Your Primary Color]` with your color preferences
   - Adjust design philosophy if needed (optional)

3. **Customize brand/default.yaml:**
   - Set `identity.name` and `identity.tagline`
   - Configure `colors.primary` (your main brand color)
   - Adjust `colors.background` (dark or light theme)
   - Add your logo to `brand/assets/` directory
   - Update `identity.logo.file` path

4. **Add your logo (optional):**
   ```bash
   # Place your logo file in brand/assets/
   cp /path/to/your-logo.svg brand/assets/
   # Update brand/default.yaml to reference it
   ```

5. **Test your customization:**
   ```bash
   python3 -c "from superskills.slide_designer import SlideDesigner; print('✓ Works!')"
   ```

### What Gets Protected

Files that are **gitignored** (won't be committed):
- `PROFILE.md` - Your personal design profile
- `brand/default.yaml` - Your brand configuration
- `brand/assets/*` - Your logo and brand assets

Files that are **tracked** (will be committed):
- `PROFILE.md.template` - Shared template for all users
- `brand/default.yaml.template` - Example configuration
- `brand/assets/.gitkeep` - Directory structure keeper

This ensures your personal brand information stays private while templates are shared with the community.

## API Reference

### SlideDesigner

```python
from superskills.slide_designer import SlideDesigner

designer = SlideDesigner(
    output_dir="output/slides",  # Output directory
    theme="dark",                 # "dark" or "light"
    brand_config=None            # Optional custom brand YAML
)
```

#### Methods

**design_from_script(script, title, max_slides, output_name)**

Analyzes a narration script and generates slides automatically.

Parameters:
- `script` (str): Full narration text
- `title` (str, optional): Presentation title
- `max_slides` (int): Maximum slides to generate (default: 7)
- `output_name` (str): Base name for output files

Returns: `DesignResult`

**design_from_outline(outline, output_name)**

Parses markdown outline into slides.

Parameters:
- `outline` (str): Markdown-formatted content
- `output_name` (str): Base name for output files

Returns: `DesignResult`

**design_from_specs(slides, output_name)**

Generates slides from explicit specifications.

Parameters:
- `slides` (List[dict]): List of slide specification dicts
- `output_name` (str): Base name for output files

Returns: `DesignResult`

### Data Models

#### SlideSpec

```python
@dataclass
class SlideSpec:
    type: Literal["title", "content", "image", "quote", "question"]
    heading: str
    subheading: Optional[str] = None
    bullets: Optional[List[str]] = None
    image_url: Optional[str] = None
    caption: Optional[str] = None
    quote_text: Optional[str] = None
    quote_author: Optional[str] = None
    text: Optional[str] = None
```

#### DesignResult

```python
@dataclass
class DesignResult:
    slides: List[SlideSpec]
    html_files: List[Path]
    combined_html: Optional[Path]
    slide_count: int
    estimated_duration_seconds: float
    theme: str
```

## Brand Configuration

Brand settings are stored in `brand/default.yaml`. Custom brand configs can be provided via the `brand_config` parameter.

### YAML Schema

```yaml
identity:
  name: "BrandName"
  tagline: "#tagline"
  logo:
    file: "assets/logo.svg"
    width: 200
    position: "bottom-right"
    opacity: 0.9

colors:
  primary: "#00BFFF"
  background: "#1f2937"
  text: "#ffffff"
  text_secondary: "#9ca3af"

typography:
  heading:
    family: "system-ui, sans-serif"
    weight: 700
  body:
    family: "system-ui, sans-serif"
    weight: 400
  sizes:
    title_heading: "72px"
    content_heading: "48px"
    body: "32px"
    caption: "28px"

spacing:
  padding: "80px"
  line_height: "1.5"
  bullet_spacing: "0.8em"

slides:
  width: 1920
  height: 1080
  max_bullets: 5
  max_words_per_bullet: 12
  max_heading_chars: 50

themes:
  dark:
    background: "#1f2937"
    text: "#ffffff"
  light:
    background: "#ffffff"
    text: "#1f2937"
```

## Templates

Jinja2 templates are located in `templates/`:

- `base.html.j2` - Base template with CSS and layout
- `title.html.j2` - Title slide
- `content.html.j2` - Bullet points slide
- `question.html.j2` - Question/engagement slide
- `image.html.j2` - Image with caption
- `quote.html.j2` - Quote/testimonial

### Template Variables

- `slide` - SlideSpec object
- `brand` - BrandConfig object
- `theme_colors` - Theme-specific colors
- `logo_path` - Path to logo file
- `title` - Page title

## Usage Examples

### Example 1: Quick Script

```python
from superskills.slide_designer import SlideDesigner

designer = SlideDesigner()
result = designer.design_from_script(
    script="Welcome to our workshop. Today we'll cover three topics: AI basics, prompt engineering, and automation.",
    title="AI Workshop"
)

print(f"Generated {result.slide_count} slides in {result.estimated_duration_seconds}s")
for file in result.html_files:
    print(f"  - {file}")
```

### Example 2: Markdown Outline

```python
outline = """
# Introduction
Welcome to the course

# Module 1
- Topic A
- Topic B
- Topic C

# Conclusion
Thank you for attending
"""

result = designer.design_from_outline(outline)
```

### Example 3: Custom Specs

```python
slides = [
    {
        "type": "title",
        "heading": "My Presentation",
        "subheading": "A professional deck"
    },
    {
        "type": "content",
        "heading": "Key Points",
        "bullets": ["Point 1", "Point 2", "Point 3"]
    },
    {
        "type": "question",
        "heading": "Any questions?",
        "bullets": ["Contact us", "Visit our website"]
    }
]

result = designer.design_from_specs(slides)
```

## Output Format

### File Structure

```
output/slides/
├── presentation_001.html  # Individual slides
├── presentation_002.html
├── presentation_003.html
└── presentation_deck.html # Combined deck
```

### HTML Specifications

- **Resolution:** 1920x1080 pixels
- **Encoding:** UTF-8
- **Dependencies:** None (fully standalone)
- **CSS:** Inline (no external stylesheets)
- **Images:** Absolute or relative paths

## Integration

### With video-recorder

```python
from superskills.slide_designer import SlideDesigner
from superskills.video_recorder import VideoRecorder

designer = SlideDesigner()
slide_result = designer.design_from_script(
    script="Your script here",
    title="Presentation Title"
)

recorder = VideoRecorder()
video_result = recorder.record_video(
    script="Your script here",
    slides_html=str(slide_result.combined_html)
)
```

## Testing

Run tests with pytest:

```bash
cd superskills/slide-designer
pytest tests/
```

## License

MIT License - See LICENSE file for details.

## Version

1.0.0

---

**Maintained by:** CoachSteff SuperSkills Team
**Last Updated:** 2026-01-31
