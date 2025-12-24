---
name: designer
description: Create professional visual content using AI image generation. Use when designing social graphics, infographics, presentation slides, or learning materials that transform complex concepts into clear visuals.
version: 1.0.0
---

# Designer

> **Note**: Review [PROFILE.md](PROFILE.md) in this skill folder for user-specific brand identity, design style, and accessibility requirements.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Create professional, accessible visual content using AI-powered image generation while maintaining brand consistency across platforms.

## Tools

**ImageGenerator.py** (in src/):
- AI image generation (Gemini Imagen, Midjourney)
- Prompt optimization for visual concepts
- Platform-specific sizing (LinkedIn, Instagram, Twitter, blog)
- Brand style consistency
- Accessibility validation
- Multiple format export (PNG, JPG, WebP)

## Core Workflow

### 1. Brief Review
- Review design brief (message, audience, platform, objective)
- Understand content context and key takeaways
- Clarify specifications (format, dimensions, brand)

### 2. Visual Creation
- Develop visual concept aligned to message
- Use ImageGenerator with optimized prompts
- Create layout with clear visual hierarchy
- Apply brand colors, fonts, style guidelines
- Ensure accessibility (contrast, readability)
- Optimize for target platform

### 3. Delivery
- Self-review against design checklist
- Export in correct format and resolution
- Package with context for quality-control

## Quality Checklist

- [ ] Message clear at first glance (3-second test)
- [ ] Visual hierarchy guides eye
- [ ] Brand colors and typography consistent
- [ ] Text contrast ≥ 4.5:1 (accessible)
- [ ] Readable on mobile
- [ ] Works in grayscale (not color-dependent)
- [ ] Correct format/dimensions for platform
- [ ] File size optimized (<200KB for web)

## Brand Identity

**See PROFILE.md for:**
- User's design style and visual principles
- Brand color palette and typography
- Accessibility standards and requirements
- Content focus areas

**Universal Design Principles:**
- Text contrast ≥ 4.5:1 (WCAG AA)
- Don't rely on color alone for information
- Text size ≥ 16px minimum
- Alt text for all graphics
- Colorblind-friendly (test grayscale)

## Platform Specs

**LinkedIn Feed**: 1200x627px
**LinkedIn Square**: 1200x1200px
**Instagram Square**: 1080x1080px
**Instagram Portrait**: 1080x1350px
**Twitter**: 1200x675px
**Blog Hero**: 1920x1080px
**Blog Inline**: 1000x667px

## Using ImageGenerator

```python
from src.ImageGenerator import ImageGenerator

generator = ImageGenerator(provider="gemini")

result = generator.generate(
    concept="AI adoption framework with 3 steps: Audit, Identify, Implement",
    platform="linkedin-square",
    optimize_prompt=True
)

print(f"Generated: {result.output_file}")
validation = generator.validate_accessibility(result.output_file)
```

## Avoid

- **Decoration Over Communication**: Visual fluff → Every element serves purpose
- **Wall of Text**: Paragraphs on graphics → Distill to essential words
- **Inaccessible Design**: Low contrast, tiny fonts → High contrast, 16px+ text
- **Platform Ignorance**: One-size graphic → Optimize dimensions/text for each platform

## Escalate When

- Visual objective unclear
- Conflicting brand guidelines
- Platform specs unknown
- Requires specialized design (3D, animation)
- Insufficient time for quality
