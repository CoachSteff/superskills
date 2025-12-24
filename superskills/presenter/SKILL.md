---
name: presenter
description: Slide deck generation from markdown using python-pptx. Use when creating presentations, transforming content to slides, or automating PowerPoint creation.
version: 1.0.0
---

# Presenter

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific presentation themes, branding, and slide design preferences.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Transform markdown content into professional PowerPoint presentations with customizable themes and automated slide generation.

## Tools

**Presenter.py** (in src/):
- Markdown to PowerPoint conversion
- Multiple presentation themes (default, dark, professional)
- Automatic slide layout detection
- Title slides, content slides, bullet lists
- Code block formatting
- Custom styling (colors, fonts, backgrounds)
- Image insertion support

## Core Workflow

### 1. Content Preparation
- Receive markdown content or file
- Identify slide structure (H1 = new slide, H2 = subtitle)
- Determine presentation theme
- Gather any images or media

### 2. Slide Generation
- Parse markdown into slide structure
- Create title slide
- Generate content slides from headings
- Format bullet points and lists
- Apply theme styling
- Insert code blocks with formatting

### 3. Delivery
- Export as .pptx file
- Validate slide count and layout
- Package with metadata
- Handoff for review or distribution

## Usage

**Create from Markdown File:**
```python
from superskills.presenter.src import Presenter

presenter = Presenter(
    output_dir="output/presentations",
    theme="professional"
)

result = presenter.create_from_markdown(
    markdown_file="course_outline.md",
    title_slide=True,
    output_name="Course_Presentation"
)

print(f"Created: {result.output_file}")
print(f"Slides: {result.slide_count}")
```

**Create from Markdown String:**
```python
markdown_content = """
# Course Introduction
## Welcome to AI Automation

# Module 1: Getting Started
- Install dependencies
- Configure API keys
- Run first automation

# Module 2: Core Concepts
- Skills and workflows
- Integration patterns
- Best practices
"""

result = presenter.create_from_markdown(
    markdown_file=markdown_content,
    output_name="ai_course_slides"
)
```

**Available Themes:**
- `default`: Clean white background, blue titles
- `dark`: Dark background, yellow/white text
- `professional`: Light gray background, navy titles

## Environment Variables

```bash
# No API keys required - python-pptx is a local library
# Optional: Configure presentation settings in config/presenter_config.yaml
```

**Dependencies:**
```bash
pip install python-pptx markdown
```

## Quality Checklist

- [ ] Markdown properly formatted (H1 for slides, H2 for subtitles)
- [ ] Theme applied consistently
- [ ] Text readable (appropriate font sizes)
- [ ] Bullet points not overcrowded (<7 per slide)
- [ ] Code blocks formatted clearly
- [ ] File size reasonable
- [ ] Slides flow logically

## Avoid

- **Too Much Text**: Paragraphs → Concise bullet points
- **Inconsistent Formatting**: Mixed styles → Use single theme
- **Missing Title Slide**: Jump to content → Include professional title slide
- **Poor Hierarchy**: Flat content → Use H1/H2 for structure
- **Ignoring Limits**: 50+ items per slide → Break into multiple slides

## Escalate When

- Need custom templates beyond built-in themes
- Require advanced animations or transitions
- Need to edit existing presentations
- Complex layouts (multi-column, charts)
- Branding requires specific fonts/colors not in themes

## Integration Examples

**With Author (Content to Slides):**
```python
from superskills.author.src import ContentWriter
from superskills.presenter.src import Presenter

writer = ContentWriter()
outline = writer.create_outline(topic="AI Automation", sections=5)

presenter = Presenter(theme="professional")
result = presenter.create_from_markdown(
    markdown_file=outline,
    output_name="ai_automation_presentation"
)
```

**With Craft (Craft Doc to Presentation):**
```python
from superskills.craft.src import CraftClient
from superskills.presenter.src import Presenter

craft = CraftClient()
doc = craft.get_document("course_outline_id")

presenter = Presenter()
result = presenter.create_from_markdown(
    markdown_file=doc.content,
    output_name=doc.title
)
```

**With CoursePackager (Complete Course Package):**
```python
from superskills.presenter.src import Presenter
from superskills.coursepackager.src import CoursePackager

presenter = Presenter()
slides = presenter.create_from_markdown("course_content.md")

packager = CoursePackager()
package = packager.package_course(
    course_name="Complete Training",
    files=[slides.output_file, "workbook.pdf", "resources.zip"]
)
```

## Markdown Formatting Guide

```markdown
# Slide Title
## Subtitle (optional)

- Bullet point 1
- Bullet point 2
- Bullet point 3

# Next Slide
Content here...

# Code Example
```python
def hello():
    print("Hello, World!")
```
```
