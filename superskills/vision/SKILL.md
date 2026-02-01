---
name: vision
description: AI-powered screen monitoring and analysis using Gemini Vision API. Captures and analyzes screenshots to describe UI, detect elements, extract text, identify errors, monitor changes, and suggest automated tests.
version: 1.0.0
type: python
python_module: superskills.vision.src:VisionAnalyzer
---

# Vision

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific vision analysis preferences, monitoring settings, and output formatting.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically.

Give AI the ability to "see" what's happening on your screen. Analyze UI elements, extract text, detect errors, monitor changes, and generate testing insights.

## Tools

**VisionAnalyzer.py** (in src/):
- Screenshot capture using PyAutoGUI
- Multi-mode analysis (describe, detect, ocr, errors, monitor, test)
- Gemini Vision API integration
- Region-specific capture
- Change detection and monitoring
- Structured output with coordinates

**ScreenCapture.py** (in src/):
- Screen information utilities
- Mouse position tracking
- Region-based capture
- **Window-specific capture** (by app name, window title, or window ID)
- Window enumeration via JXA (JavaScript for Automation)
- Visual element location

## Core Workflow

### 1. Capture
- Take full screen, region screenshot, or specific window
- Window capture by app name, title, or ID (macOS)
- Or accept existing image file path
- Save with timestamp if configured

### 2. Analyze
- Send image + prompt to Gemini Vision
- Mode-specific analysis:
  - **describe**: Plain text description of screen content
  - **detect**: Identify UI elements with positions
  - **ocr**: Extract all visible text
  - **errors**: Find UI problems and accessibility issues
  - **monitor**: Detect changes from previous capture
  - **test**: Generate automated test scenarios

### 3. Deliver
- Return structured VisionResult
- Include screenshot path, coordinates, suggestions
- Format output as text, JSON, or markdown

## Usage

**Basic Screen Description:**
```bash
superskills call vision "analyze current screen"
```

**Detect UI Elements:**
```bash
superskills call vision '{"mode": "detect"}'
```

**Extract Text (OCR):**
```bash
superskills call vision '{"mode": "ocr"}'
```

**Find Errors:**
```bash
superskills call vision '{"mode": "errors"}'
```

**Monitor Specific Region:**
```bash
superskills call vision '{"mode": "monitor", "region": [0, 0, 800, 600]}'
```

**Generate Test Cases:**
```bash
superskills call vision '{"mode": "test"}'
```

**Analyze Existing Screenshot:**
```bash
superskills call vision '{"screenshot_path": "/path/to/screenshot.png", "mode": "describe"}'
```

**Custom Analysis Prompt:**
```bash
superskills call vision "Check if the login button is visible and enabled"
```

## Python API

**Quick Analysis:**
```python
from superskills.vision.src import analyze_screen

result = analyze_screen(mode="describe")
print(result.description)
print(f"Screenshot: {result.screenshot_path}")
```

**Detailed Analysis:**
```python
from superskills.vision.src import VisionAnalyzer

analyzer = VisionAnalyzer(output_dir="screenshots")

# Detect UI elements
result = analyzer.analyze(mode="detect")
if result.elements:
    for element in result.elements:
        print(f"{element.get('type')}: {element.get('label')}")

# Extract text
result = analyzer.analyze(mode="ocr")
print(result.text_content)

# Find errors
result = analyzer.analyze(mode="errors")
if result.errors:
    for error in result.errors:
        print(f"[{error.get('severity', 'unknown')}] {error.get('description')}")
```

**Monitor Changes:**
```python
analyzer = VisionAnalyzer()

# Monitor for 30 seconds, checking every 5 seconds
changes = analyzer.monitor_changes(
    interval_seconds=5,
    max_iterations=6
)

for change in changes:
    print(f"Change detected: {change.description}")
```

**Region-Specific Capture:**
```python
# Capture only top-left quarter of screen
result = analyzer.analyze(
    mode="describe",
    region=(0, 0, 960, 540)  # x, y, width, height
)
```

## Analysis Modes

| Mode | Purpose | Output |
|------|---------|--------|
| `describe` | General screen description | Plain text description |
| `detect` | Identify UI elements | List of elements with types, labels, positions |
| `ocr` | Extract all text | Full text content in reading order |
| `errors` | Find UI/accessibility issues | List of errors with severity and fixes |
| `monitor` | Detect changes | Description of what changed |
| `test` | Generate test scenarios | Suggested test cases and automation steps |

## Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
VISION_OUTPUT_DIR=~/Documents/vision-screenshots  # Custom output directory
VISION_SAVE_SCREENSHOTS=true                       # Save screenshots (default: true)
```

**Global .env (repository root):**
```bash
echo "GEMINI_API_KEY=your-key" >> .env
```

**Or skill-specific .env:**
```bash
echo "GEMINI_API_KEY=your-key" >> superskills/vision/.env
```

## Quality Checklist

- [ ] Screenshot captured successfully
- [ ] Image quality sufficient for analysis
- [ ] Analysis mode appropriate for task
- [ ] Coordinates/positions accurate (detect mode)
- [ ] Text extracted completely (ocr mode)
- [ ] Errors identified with helpful suggestions
- [ ] Output format suitable for use case

## Avoid

- **Full Screen for Details**: Capture full screen → Capture specific region of interest
- **Wrong Mode**: Generic describe → Use specific mode (detect/ocr/errors)
- **Missing Context**: Single snapshot → Use monitor mode for change detection
- **Ignoring Privacy**: Capture sensitive data → Disable save_screenshots or use region capture

## Escalate When

- Screenshot capture fails (permission issues)
- Gemini API quota exceeded
- Analysis inaccurate for specific UI patterns
- Need real-time monitoring (< 1 second intervals)
- Require precise pixel-level coordinates

## Integration Examples

**With Testing Workflow:**
```python
from superskills.vision.src import VisionAnalyzer

analyzer = VisionAnalyzer()

# Generate test cases from current screen
result = analyzer.analyze(mode="test")
if result.suggestions:
    print("Suggested Tests:")
    for suggestion in result.suggestions:
        print(f"- {suggestion}")
```

**With Error Reporting:**
```python
result = analyzer.analyze(mode="errors")

if result.errors:
    print(f"Found {len(result.errors)} issues:")
    for error in result.errors:
        severity = error.get('severity', 'unknown')
        description = error.get('description', 'No description')
        print(f"[{severity}] {description}")
```

**With Accessibility Audit:**
```python
result = analyzer.analyze(
    mode="errors",
    custom_prompt="""
    Analyze this screenshot for accessibility issues:
    - Color contrast problems
    - Missing alt text or labels
    - Keyboard navigation concerns
    - Screen reader compatibility
    """
)
```

## Use Cases

- **QA/Testing**: Automated UI testing, visual regression detection
- **Documentation**: Screenshot annotation, UI element identification
- **Accessibility**: Audit screens for accessibility compliance
- **Monitoring**: Track UI changes, detect errors in production
- **Automation**: Identify click targets, verify UI state before actions
- **Research**: Analyze competitor UIs, extract data from screenshots

## Limitations

- **Performance**: API latency (~2-5 seconds per analysis)
- **Accuracy**: Gemini may misidentify ambiguous UI elements
- **Coordinates**: Approximate positions (not pixel-perfect)
- **Dynamic Content**: May miss rapidly changing elements
- **Privacy**: Screenshot files saved by default (can be disabled)

## Platform Notes

### macOS
- **Screenshot capture**: Uses native `screencapture` tool via PyAutoGUI
- **Window capture**: Uses JXA (JavaScript for Automation) for window enumeration and `screencapture -l` for capture
- **Window shadows**: Excluded by default (cleaner for AI analysis); configurable via `include_shadow` parameter
- **Automatic fallback**: If PATH issues occur (e.g., in virtual environments), automatically falls back to direct subprocess call
- **Permissions required**: 
  - Screen Recording permission in System Preferences → Security & Privacy → Screen Recording
  - Automation permission for accessing window information (prompted on first use)

---

**Requirements:**
- PyAutoGUI for screen capture
- Pillow for image processing
- google-genai for Gemini API
- GEMINI_API_KEY environment variable
