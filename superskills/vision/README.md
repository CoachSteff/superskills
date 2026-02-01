# Vision Skill - AI Screen Monitoring and Analysis

Give AI the ability to "see" and analyze your computer screen using Gemini's vision capabilities.

## Features

✅ **Multiple Analysis Modes**
- Screen descriptions (what's on screen)
- UI element detection (buttons, inputs, links with positions)
- Text extraction (OCR)
- Error detection (UI bugs, accessibility issues)
- Change monitoring (detect what changed)
- Test generation (automated testing suggestions)

✅ **Flexible Capture**
- Full screen or specific regions
- **Window-specific capture** (by app name, window title, or window ID)
- Automatic capture via PyAutoGUI
- Analyze existing screenshot files
- Configurable screenshot saving

✅ **Gemini Vision Integration**
- Powered by Gemini 2.0 Flash
- Multimodal prompts (image + text)
- Structured output options
- Error handling and retries

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install pyautogui pillow google-genai numpy
```

2. Set up API key:
```bash
export GEMINI_API_KEY=your_key_here
# Or add to .env file in project root
```

3. **macOS Permission**: Grant screen recording permission
   - System Preferences → Security & Privacy → Screen Recording
   - Add Terminal or your IDE to the allowed apps

### Basic Usage

**Describe current screen:**
```bash
superskills call vision "what's on my screen?"
```

**Detect UI elements:**
```bash
superskills call vision '{"mode": "detect"}'
```

**Extract all text:**
```bash
superskills call vision '{"mode": "ocr"}'
```

**Find errors:**
```bash
superskills call vision '{"mode": "errors"}'
```

## Python API

```python
from superskills.vision.src import VisionAnalyzer

analyzer = VisionAnalyzer()

# Quick description
result = analyzer.analyze(mode="describe")
print(result.description)

# Detect UI elements
result = analyzer.analyze(mode="detect")
if result.elements:
    for element in result.elements:
        print(f"{element.get('type')}: {element.get('label')}")

# Extract text (OCR)
result = analyzer.analyze(mode="ocr")
print(result.text_content)

# Find errors
result = analyzer.analyze(mode="errors")
if result.errors:
    for error in result.errors:
        print(f"[{error.get('severity')}] {error.get('description')}")

# Monitor changes
changes = analyzer.monitor_changes(interval_seconds=5, max_iterations=6)

# Capture specific region
result = analyzer.analyze(mode="describe", region=(0, 0, 800, 600))
```

## Configuration

### Environment Variables

```bash
GEMINI_API_KEY=your_key          # Required
VISION_OUTPUT_DIR=/custom/path   # Optional: Screenshot save location
VISION_SAVE_SCREENSHOTS=true     # Optional: Save screenshots (default: true)
```

### Custom Prompts

```bash
superskills call vision "Is the login button visible and what color is it?"
```

Or with JSON:
```bash
superskills call vision '{
  "mode": "describe",
  "custom_prompt": "Focus on the navigation bar. List all menu items."
}'
```

## Window Capture

Capture specific application windows instead of full screen or region.

### By Application Name

```python
from superskills.vision.src import analyze_screen

# Capture first Chrome window
result = analyze_screen(
    mode="describe",
    app_name="Google Chrome"
)
```

### By Window Title (Substring)

```python
# Find Chrome window with "Canvas" in title
result = analyze_screen(
    mode="describe",
    app_name="Google Chrome",
    window_title="Canvas"
)
```

### By Window Title (Regex Pattern)

```python
# Find Chrome window matching pattern
result = analyze_screen(
    mode="describe",
    app_name="Google Chrome",
    window_title="Canvas.*Presenter",
    window_title_regex=True
)
```

### By Direct Window ID

```python
from superskills.vision.src import ScreenCapture

# Get window ID first
window_id = ScreenCapture.get_window_id("Google Chrome")

# Capture specific window
result = analyze_screen(
    mode="describe",
    window_id=window_id
)
```

### CLI Usage

```bash
# By app name
superskills call vision '{"mode": "describe", "app_name": "Google Chrome"}'

# With title filter
superskills call vision '{
    "mode": "describe",
    "app_name": "Google Chrome",
    "window_title": "Canvas"
}'

# With regex pattern
superskills call vision '{
    "mode": "describe",
    "app_name": "Google Chrome",
    "window_title": "Canvas.*",
    "window_title_regex": true
}'

# By window ID
superskills call vision '{"mode": "describe", "window_id": 12345}'
```

### Window Discovery

List all windows or find specific window IDs:

```python
from superskills.vision.src import ScreenCapture

# List all windows
all_windows = ScreenCapture.list_windows()
for w in all_windows:
    print(f"{w['app_name']}: {w['window_title']} (ID: {w['window_id']})")

# List windows for specific app
chrome_windows = ScreenCapture.list_windows(app_name="Google Chrome")

# Get specific window ID
window_id = ScreenCapture.get_window_id(
    app_name="Google Chrome",
    window_title="Canvas Presenter"
)
```

### Error Handling

By default, if a window is not found, the skill falls back to full-screen capture with a warning:

```python
# Fallback enabled (default)
result = analyze_screen(
    mode="describe",
    app_name="NonExistentApp"
)
# Warning printed, captures full screen instead
```

To raise an exception instead:

```python
from superskills.vision.src import ScreenCapture, WindowNotFoundError

try:
    image = ScreenCapture.capture_window(
        app_name="NonExistentApp",
        fallback_to_fullscreen=False
    )
except WindowNotFoundError as e:
    print(f"Error: {e}")
    # Exception includes list of available windows for the app
    print(f"Available windows: {e.available_windows}")
```

## Use Cases

**QA Testing:**
- Automated visual testing
- UI regression detection
- Accessibility audits

**Documentation:**
- Screenshot annotation
- UI element cataloging
- User guide creation

**Monitoring:**
- Production UI health checks
- Error detection in dashboards
- Change alerts

**Automation:**
- Verify UI state before actions
- Extract data from legacy UIs
- Visual element location for scripting

## Analysis Modes

| Mode | Purpose | Example Usage |
|------|---------|---------------|
| `describe` | General screen description | `{"mode": "describe"}` |
| `detect` | Identify UI elements | `{"mode": "detect"}` |
| `ocr` | Extract all text | `{"mode": "ocr"}` |
| `errors` | Find UI/accessibility issues | `{"mode": "errors"}` |
| `monitor` | Detect changes | `{"mode": "monitor"}` |
| `test` | Generate test scenarios | `{"mode": "test"}` |

## Limitations

- **API Latency**: 2-5 seconds per analysis
- **Coordinates**: Approximate positions (not pixel-perfect)
- **Privacy**: Screenshots saved by default (configure `save_screenshots=False` if sensitive)
- **Rate Limits**: Subject to Gemini API quotas

## Troubleshooting

**"GEMINI_API_KEY not found"**
- Set environment variable: `export GEMINI_API_KEY=your_key`
- Or add to `.env` file in project root

**Screenshot capture fails**
- Check screen recording permissions (macOS System Preferences → Security & Privacy → Screen Recording)
- Ensure PyAutoGUI is installed: `pip install pyautogui`

**Screenshot capture fails in virtual environment**
- Issue: `FileNotFoundError: [Errno 2] No such file or directory: 'screencapture'`
- Cause: Virtual environment doesn't include `/usr/sbin` in PATH
- Solution: Automatic fallback implemented - no action required
- The vision skill will:
  1. Try standard PyAutoGUI capture
  2. Fix PATH and retry if needed
  3. Fall back to direct subprocess call
- If issues persist, ensure `/usr/sbin/screencapture` exists and is executable

**Inaccurate UI detection**
- Try different mode (detect vs describe)
- Use region capture for specific areas
- Add custom prompt with more context

**"FailSafeException" error**
- PyAutoGUI failsafe triggered (mouse moved to corner)
- Disable with: `pyautogui.FAILSAFE = False` (not recommended)
- Or move mouse away from screen corners during capture

**Window capture fails or returns wrong window**
- Issue: Window not found or incorrect window captured
- Diagnosis:
  ```python
  from superskills.vision.src import ScreenCapture
  windows = ScreenCapture.list_windows(app_name="YourApp")
  print(windows)  # Check available windows and their titles
  ```
- Common causes:
  - App name doesn't match exactly (case-sensitive)
  - Window title changed or is empty
  - App has no visible windows
  - Missing Automation permission (System Preferences → Security & Privacy → Automation)
- Solution: Use `list_windows()` to verify exact app name and window titles, then adjust filters accordingly

## API Reference

See [VisionAnalyzer.py](src/VisionAnalyzer.py) for full API documentation.

## Examples

### Example 1: Automated UI Testing

```python
from superskills.vision.src import VisionAnalyzer

analyzer = VisionAnalyzer()

# Capture current state
result = analyzer.analyze(mode="describe")
print(f"Current screen: {result.description}")

# Generate test cases
test_result = analyzer.analyze(mode="test")
if test_result.suggestions:
    print("\nSuggested Tests:")
    for suggestion in test_result.suggestions:
        print(f"  - {suggestion}")
```

### Example 2: Accessibility Audit

```python
result = analyzer.analyze(
    mode="errors",
    custom_prompt="Check for accessibility issues: contrast, labels, keyboard navigation"
)

if result.errors:
    print(f"Found {len(result.errors)} accessibility issues:")
    for error in result.errors:
        print(f"  [{error.get('severity', 'unknown')}] {error.get('description')}")
```

### Example 3: Change Monitoring

```python
# Monitor specific region for changes
analyzer = VisionAnalyzer()

print("Monitoring top-right corner for changes...")
changes = analyzer.monitor_changes(
    interval_seconds=3,
    max_iterations=10,
    region=(1200, 0, 720, 400)  # Top-right quarter
)

print(f"\nDetected {len(changes)} changes:")
for i, change in enumerate(changes, 1):
    print(f"{i}. {change.description[:100]}...")
```

---

**Version:** 1.0.0  
**Requires:** Python 3.9+, GEMINI_API_KEY  
**Dependencies:** pyautogui, Pillow, google-genai, numpy
