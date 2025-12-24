---
name: coursepackager
description: Course packaging and workbook generation using ReportLab. Use when creating professional PDF workbooks, packaging course materials, or generating training documents.
version: 1.0.0
---

# Course Packager

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific branding, course style preferences, and formatting standards.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Transform course content into professional PDF workbooks and packaged learning materials ready for distribution.

## Tools

**CoursePackager.py** (in src/):
- PDF workbook generation using ReportLab
- Custom styling and branding
- Multi-section course structure
- Table of contents generation
- ZIP packaging for complete courses
- Exercise and worksheet inclusion
- Professional formatting (headers, footers, page numbers)

## Core Workflow

### 1. Content Preparation
- Receive course outline and materials
- Structure content into sections/modules
- Organize exercises, worksheets, resources
- Define branding and styling requirements

### 2. Workbook Generation
- Create PDF with custom styles
- Generate table of contents
- Format sections with headings and body text
- Include exercises and worksheets
- Add page numbers and headers
- Apply brand colors and styling

### 3. Packaging & Delivery
- Package PDF with supplementary materials
- Create ZIP archive for distribution
- Validate file integrity and size
- Handoff complete course package

## Usage

**Create Workbook:**
```python
from superskills.coursepackager.src import CoursePackager

packager = CoursePackager(output_dir="output/courses")

sections = [
    {
        "title": "Module 1: Introduction",
        "content": "Welcome to the course...",
        "exercises": ["Exercise 1.1", "Exercise 1.2"]
    },
    {
        "title": "Module 2: Core Concepts",
        "content": "Let's explore...",
        "exercises": ["Practice Activity"]
    }
]

result = packager.create_workbook(
    title="Complete Training Course",
    sections=sections,
    include_toc=True
)

print(f"Workbook created: {result.output_file}")
print(f"File size: {result.file_size_mb} MB")
```

**Package Course Materials:**
```python
files = [
    "workbook.pdf",
    "slides.pptx",
    "resources/cheatsheet.pdf"
]

package = packager.package_course(
    course_name="AI Automation Training",
    files=files,
    output_name="ai_automation_course"
)

print(f"Package: {package.output_file}")
```

## Environment Variables

```bash
# No API keys required - ReportLab is a local library
# Optional: Configure PDF settings in config/coursepackager_config.yaml
```

**Dependencies:**
```bash
pip install reportlab
```

## Quality Checklist

- [ ] Table of contents generated and accurate
- [ ] All sections included and ordered correctly
- [ ] Branding applied (colors, fonts, logos)
- [ ] Page numbers present and sequential
- [ ] Exercises clearly formatted
- [ ] File size reasonable (<10MB for web distribution)
- [ ] PDF readable on all devices

## Avoid

- **Generic Styling**: Default styles → Custom branded appearance
- **Missing TOC**: Long document without navigation → Generate table of contents
- **Poor Structure**: Flat content → Clear section hierarchy
- **Large Files**: Uncompressed images → Optimize file size
- **Missing Exercises**: Theory only → Include practice activities

## Escalate When

- Custom fonts or advanced styling needed
- Interactive PDF features required
- File size exceeds distribution limits
- Need digital rights management (DRM)
- Complex layouts beyond ReportLab capabilities

## Integration Examples

**With Transcriber (Convert Recordings to Workbook):**
```python
from superskills.transcriber.src import Transcriber
from superskills.coursepackager.src import CoursePackager

transcriber = Transcriber()
results = transcriber.transcribe_batch(
    ["lesson1.mp4", "lesson2.mp4", "lesson3.mp4"],
    output_format="json"
)

packager = CoursePackager()
sections = [
    {
        "title": f"Lesson {i+1}",
        "content": result.transcript
    }
    for i, result in enumerate(results)
]

workbook = packager.create_workbook(
    title="Course Transcript Workbook",
    sections=sections
)
```

**With Author (Content to PDF):**
```python
from superskills.author.src import ContentWriter
from superskills.coursepackager.src import CoursePackager

writer = ContentWriter()
article = writer.create_article(topic="AI Trends", word_count=2000)

packager = CoursePackager()
sections = [{"title": "AI Trends Report", "content": article}]

workbook = packager.create_workbook(
    title="AI Trends - Professional Report",
    sections=sections
)
```
