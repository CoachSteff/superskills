# Designer Agent Tools

AI-powered visual content creation for CoachSteff using image generation APIs.

## Overview

The Designer Agent provides Python tools for generating professional visuals:
- **ImageGenerator.py** - Multi-provider AI image generation (Gemini Imagen, Midjourney)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
export GEMINI_API_KEY="your_gemini_api_key"
# Optional: Midjourney support
export MIDJOURNEY_API_KEY="your_midjourney_api_key"
```

## Usage

### Basic Image Generation

```python
from agents.designer.src.ImageGenerator import ImageGenerator

generator = ImageGenerator(provider="gemini")

result = generator.generate(
    concept="AI adoption framework infographic showing 3 steps",
    platform="linkedin-square",
    optimize_prompt=True
)

print(f"Generated: {result.output_file}")
print(f"File size: {result.file_size_kb:.2f}KB")
```

### Platform-Specific Sizing

```python
# LinkedIn feed post
result = generator.generate(
    concept="Professional headshot with modern office background",
    platform="linkedin-feed"  # 1200x627px
)

# Instagram square
result = generator.generate(
    concept="Quote graphic with clean typography",
    platform="instagram-square"  # 1080x1080px
)

# Blog hero image
result = generator.generate(
    concept="Technology workspace with AI elements",
    platform="blog-hero"  # 1920x1080px
)
```

### Accessibility Validation

```python
# Generate and validate
result = generator.generate(
    concept="Data visualization showing AI ROI metrics",
    platform="linkedin-square"
)

validation = generator.validate_accessibility(result.output_file)

if validation['passes_validation']:
    print("✓ Image meets accessibility standards")
else:
    print(f"✗ Issues: File size: {validation['file_size_kb']:.2f}KB")
```

## Supported Platforms

- `linkedin-feed`: 1200x627px (horizontal)
- `linkedin-square`: 1200x1200px
- `instagram-square`: 1080x1080px
- `instagram-portrait`: 1080x1350px
- `twitter`: 1200x675px
- `blog-hero`: 1920x1080px
- `blog-inline`: 1000x667px

## Brand Style

All images are automatically enhanced with CoachSteff's brand style:
- Modern, clean, professional design
- Approachable but authoritative aesthetic
- High contrast for accessibility
- Clarity-focused composition

## Providers

### Gemini Imagen (Default)
- **Pros**: Fast, cost-effective, reliable
- **Best for**: Quick iterations, social graphics, diagrams
- **API**: Google Gemini

### Midjourney
- **Pros**: Highest visual quality, artistic
- **Best for**: Hero images, marketing materials
- **API**: Midjourney (requires API access)

## Documentation

See `SKILL.md` for full agent capabilities, quality gates, and design principles.
