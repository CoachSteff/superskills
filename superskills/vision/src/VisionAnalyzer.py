"""
VisionAnalyzer.py - AI-powered screen monitoring and analysis using Gemini Vision API.
"""
import io
import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

import pyautogui
from google import genai
from PIL import Image

AnalysisMode = Literal["describe", "detect", "ocr", "errors", "monitor", "test"]
OutputFormat = Literal["text", "json", "markdown"]


def _ensure_screencapture_available():
    """
    Ensure screencapture is available on macOS by adding /usr/sbin to PATH.
    
    This fixes the issue where virtual environments don't include /usr/sbin,
    causing PyAutoGUI to fail when calling screencapture.
    """
    env_path = os.environ.get('PATH', '')
    if '/usr/sbin' not in env_path:
        os.environ['PATH'] = f"/usr/sbin:{env_path}"


def _capture_screenshot_fallback(region: Optional[tuple] = None) -> Image.Image:
    """
    Fallback screenshot capture using direct subprocess call.
    
    Used when PyAutoGUI fails due to PATH issues or other errors.
    
    Args:
        region: (x, y, width, height) or None for full screen
    
    Returns:
        PIL Image of the captured screenshot
    """
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        if region:
            x, y, width, height = region
            # screencapture doesn't support direct region capture, so we capture full screen
            # and crop afterwards
            subprocess.run(['/usr/sbin/screencapture', '-x', tmp_path], 
                         check=True, capture_output=True)
            full_screenshot = Image.open(tmp_path)
            screenshot = full_screenshot.crop((x, y, x + width, y + height))
        else:
            subprocess.run(['/usr/sbin/screencapture', '-x', tmp_path], 
                         check=True, capture_output=True)
            screenshot = Image.open(tmp_path)
        
        return screenshot
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@dataclass
class VisionResult:
    """Result from vision analysis."""
    mode: str
    description: str
    elements: Optional[List[Dict]] = None  # UI elements with coordinates
    text_content: Optional[str] = None     # OCR extracted text
    errors: Optional[List[Dict]] = None    # Detected errors/issues
    suggestions: Optional[List[str]] = None # Action suggestions
    screenshot_path: Optional[str] = None
    timestamp: str = None
    metadata: Dict = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class VisionAnalyzer:
    """AI-powered screen monitoring and analysis using Gemini Vision."""

    def __init__(
        self,
        output_dir: str = "output/vision",
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash",
        save_screenshots: bool = True,
        verbose: bool = True
    ):
        """Initialize Vision Analyzer with Gemini API.
        
        Args:
            output_dir: Directory to save screenshots
            api_key: Gemini API key (or from GEMINI_API_KEY env var)
            model: Gemini model to use
            save_screenshots: Whether to save screenshots to disk
            verbose: Enable verbose logging
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment.\n"
                "Please set it with:\n"
                "  export GEMINI_API_KEY=your_key_here\n"
                "Or add it to a .env file in your project root."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.save_screenshots = save_screenshots
        self.verbose = verbose
        self.previous_screenshot = None  # For change detection

    def analyze(
        self,
        mode: AnalysisMode = "describe",
        screenshot_path: Optional[str] = None,
        region: Optional[tuple] = None,
        window_id: Optional[int] = None,
        app_name: Optional[str] = None,
        window_title: Optional[str] = None,
        window_title_regex: bool = False,
        include_shadow: bool = False,
        custom_prompt: Optional[str] = None,
        output_format: OutputFormat = "text"
    ) -> VisionResult:
        """
        Analyze screen content using Gemini Vision.
        
        Args:
            mode: Analysis mode (describe/detect/ocr/errors/monitor/test)
            screenshot_path: Path to existing screenshot, or None to capture
            region: Specific screen region (x, y, width, height)
            window_id: Capture specific window by ID
            app_name: Capture window by app name
            window_title: Filter window by title (substring or regex)
            window_title_regex: Treat window_title as regex pattern
            include_shadow: Include window shadow in capture
            custom_prompt: Override default prompt for mode
            output_format: Output format (text/json/markdown)
        
        Returns:
            VisionResult with analysis results
        """
        if self.verbose:
            print(f"Starting vision analysis (mode: {mode})...")

        # 1. Capture or load screenshot
        if screenshot_path:
            if self.verbose:
                print(f"Loading screenshot from: {screenshot_path}")
            image = Image.open(screenshot_path)
            saved_path = screenshot_path
        elif window_id or app_name:
            # Window capture
            image, saved_path = self._capture_window(
                window_id=window_id,
                app_name=app_name,
                window_title=window_title,
                use_regex=window_title_regex,
                include_shadow=include_shadow
            )
        else:
            # Full screen or region capture
            image, saved_path = self._capture_screenshot(region)

        # 2. Build prompt based on mode
        prompt = custom_prompt or self._build_prompt(mode)

        # 3. Call Gemini Vision API
        response = self._call_gemini_vision(image, prompt)

        # 4. Parse response based on mode
        result = self._parse_response(response, mode, saved_path)

        if self.verbose:
            print(f"✓ Vision analysis completed")
            if saved_path:
                print(f"  Screenshot: {saved_path}")

        return result

    def _capture_screenshot(
        self,
        region: Optional[tuple] = None
    ) -> tuple:
        """
        Capture screenshot using PyAutoGUI with fallback to subprocess.
        
        Implements hybrid approach:
        1. Try PyAutoGUI (preferred - works with existing code)
        2. If FileNotFoundError, ensure /usr/sbin in PATH and retry
        3. If still fails, use direct subprocess call to /usr/sbin/screencapture
        
        Args:
            region: (x, y, width, height) or None for full screen
        
        Returns:
            Tuple of (PIL Image, saved_path)
        """
        if self.verbose:
            if region:
                print(f"Capturing region: {region}")
            else:
                print("Capturing full screen...")

        screenshot = None
        
        # Attempt 1: Try PyAutoGUI (standard approach)
        try:
            if region:
                x, y, width, height = region
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
            else:
                screenshot = pyautogui.screenshot()
        
        except FileNotFoundError as e:
            if 'screencapture' in str(e):
                if self.verbose:
                    print("  PyAutoGUI failed (PATH issue), fixing PATH and retrying...")
                
                # Attempt 2: Fix PATH and retry PyAutoGUI
                _ensure_screencapture_available()
                
                try:
                    if region:
                        x, y, width, height = region
                        screenshot = pyautogui.screenshot(region=(x, y, width, height))
                    else:
                        screenshot = pyautogui.screenshot()
                
                except (FileNotFoundError, Exception):
                    # Attempt 3: Fallback to direct subprocess call
                    if self.verbose:
                        print("  PyAutoGUI still failing, using subprocess fallback...")
                    screenshot = _capture_screenshot_fallback(region)
            else:
                raise

        # Save if enabled
        saved_path = None
        if self.save_screenshots:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"screenshot-{timestamp}.png"
            saved_path = str(self.output_dir / filename)
            screenshot.save(saved_path)
            if self.verbose:
                print(f"  Saved to: {saved_path}")

        return screenshot, saved_path

    def _capture_window(
        self,
        window_id: Optional[int] = None,
        app_name: Optional[str] = None,
        window_title: Optional[str] = None,
        use_regex: bool = False,
        include_shadow: bool = False
    ) -> tuple:
        """
        Capture specific window using ScreenCapture.capture_window().
        
        Returns:
            Tuple of (PIL Image, saved_path)
        """
        if self.verbose:
            if window_id:
                print(f"Capturing window ID: {window_id}")
            elif app_name:
                msg = f"Capturing window for app: {app_name}"
                if window_title:
                    msg += f" (title: '{window_title}')"
                print(msg)
        
        from .ScreenCapture import ScreenCapture, WindowNotFoundError
        
        try:
            screenshot = ScreenCapture.capture_window(
                window_id=window_id,
                app_name=app_name,
                window_title=window_title,
                use_regex=use_regex,
                include_shadow=include_shadow,
                fallback_to_fullscreen=True
            )
        except WindowNotFoundError as e:
            if self.verbose:
                print(f"  Warning: {e}")
                print("  Falling back to full screen capture...")
            screenshot = self._capture_screenshot(region=None)[0]
        
        # Save if enabled
        saved_path = None
        if self.save_screenshots:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"window-{timestamp}.png"
            saved_path = str(self.output_dir / filename)
            screenshot.save(saved_path)
            if self.verbose:
                print(f"  Saved to: {saved_path}")
        
        return screenshot, saved_path

    def _build_prompt(self, mode: AnalysisMode) -> str:
        """Build analysis prompt based on mode."""

        prompts = {
            "describe": """
Analyze this screenshot and provide a clear, detailed description.
Include:
- Main content and purpose of the screen
- Key UI elements and their layout
- Any notable text, images, or interactive elements
- Overall state or context

Be concise but thorough.
            """,

            "detect": """
Detect and list all interactive UI elements in this screenshot.
For each element, provide:
- Type (button, input, link, dropdown, etc.)
- Label or text content
- Approximate position (top-left, center, bottom-right, etc.)
- State (enabled, disabled, active, etc.)

Return as structured data that can be used for automation.
Format your response as a list of elements.
            """,

            "ocr": """
Extract ALL text visible in this screenshot.
Maintain the reading order and structure.
Include:
- Headings and titles
- Body text
- Button labels
- Form fields and labels
- Error messages or alerts

Preserve formatting where relevant.
            """,

            "errors": """
Analyze this screenshot for errors, warnings, or issues.
Look for:
- Error messages or alerts
- UI problems (overlapping elements, cut-off text, etc.)
- Accessibility issues (low contrast, missing labels)
- Broken layouts or missing images
- Performance indicators (loading states, frozen UI)

For each issue found, describe:
- What the problem is
- Where it's located
- Severity (critical/medium/low)
- Suggested fix
            """,

            "monitor": """
Compare this screenshot with context to detect changes.
Note any differences in:
- UI elements appearing/disappearing
- Content changes
- State changes (loading, error states, etc.)
- Position or layout shifts

Describe what changed and the significance.
            """,

            "test": """
Analyze this screenshot as a QA engineer.
Suggest automated test scenarios covering:
- Clickable elements and expected behaviors
- Form validation to test
- Navigation flows to verify
- Edge cases to check
- Accessibility considerations

Provide actionable test cases with steps.
            """
        }

        return prompts.get(mode, prompts["describe"]).strip()

    def _call_gemini_vision(
        self,
        image: Image.Image,
        prompt: str
    ) -> str:
        """
        Call Gemini Vision API with image and prompt.
        
        Args:
            image: PIL Image object
            prompt: Analysis prompt
        
        Returns:
            Response text from Gemini
        """
        if self.verbose:
            print("Calling Gemini Vision API...")

        # Convert image to base64 for inline upload
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        try:
            # Create Part object for the image
            from google.genai import types
            
            # Use PIL Image directly (supported by Gemini SDK)
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, image],  # Pass PIL Image directly
                config={
                    "temperature": 0.2,  # Lower for more factual analysis
                    "max_output_tokens": 4000
                }
            )

            return response.text

        except Exception as e:
            error_msg = str(e).lower()
            if 'rate limit' in error_msg or 'quota' in error_msg:
                raise ValueError(
                    f"Gemini API rate limit exceeded: {e}\n"
                    "Please wait a few moments and try again."
                )
            elif 'api key' in error_msg or 'authentication' in error_msg:
                raise ValueError(
                    f"Gemini API authentication failed: {e}\n"
                    "Your API key may be invalid or expired."
                )
            else:
                raise ValueError(f"Gemini Vision API error: {e}")

    def _parse_response(
        self,
        response: str,
        mode: AnalysisMode,
        screenshot_path: Optional[str]
    ) -> VisionResult:
        """Parse Gemini response into structured VisionResult."""

        result_data = {
            "mode": mode,
            "description": response,
            "screenshot_path": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"model": self.model}
        }

        # Mode-specific parsing
        if mode == "detect":
            # Extract structured UI element data
            result_data["elements"] = self._extract_ui_elements(response)

        elif mode == "ocr":
            result_data["text_content"] = response

        elif mode == "errors":
            result_data["errors"] = self._extract_errors(response)

        elif mode == "test":
            result_data["suggestions"] = self._extract_test_cases(response)

        return VisionResult(**result_data)

    def _extract_ui_elements(self, response: str) -> List[Dict]:
        """Extract UI elements from response text."""
        elements = []

        # Simple parsing: look for lines that describe UI elements
        lines = response.split('\n')
        current_element = {}

        for line in lines:
            line = line.strip()
            if not line:
                if current_element:
                    elements.append(current_element)
                    current_element = {}
                continue

            # Try to extract structured data
            if line.startswith(('-', '*', '•')):
                line = line[1:].strip()

            # Look for key-value patterns
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip().lower()
                value = parts[1].strip()

                if key in ['type', 'label', 'position', 'state', 'text']:
                    current_element[key] = value
            elif line and current_element:
                # Add as description if we have an element started
                if 'description' not in current_element:
                    current_element['description'] = line
                else:
                    current_element['description'] += ' ' + line

        # Add last element
        if current_element:
            elements.append(current_element)

        return elements if elements else None

    def _extract_errors(self, response: str) -> List[Dict]:
        """Extract errors/issues from response text."""
        errors = []

        # Simple parsing: look for issue descriptions
        lines = response.split('\n')
        current_error = {}

        for line in lines:
            line = line.strip()
            if not line:
                if current_error:
                    errors.append(current_error)
                    current_error = {}
                continue

            if line.startswith(('-', '*', '•')):
                line = line[1:].strip()

            # Look for severity indicators
            severity_match = re.search(r'\b(critical|high|medium|low)\b', line, re.IGNORECASE)
            if severity_match:
                current_error['severity'] = severity_match.group(1).lower()

            # Store description
            if 'description' not in current_error:
                current_error['description'] = line
            else:
                current_error['description'] += ' ' + line

        # Add last error
        if current_error:
            errors.append(current_error)

        return errors if errors else None

    def _extract_test_cases(self, response: str) -> List[str]:
        """Extract test case suggestions from response text."""
        suggestions = []

        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '*', '•', '1.', '2.', '3.')):
                # Remove leading markers
                line = re.sub(r'^[-*•\d.]+\s*', '', line)
                if line:
                    suggestions.append(line)

        return suggestions if suggestions else None

    def monitor_changes(
        self,
        interval_seconds: int = 5,
        max_iterations: int = 10,
        region: Optional[tuple] = None
    ) -> List[VisionResult]:
        """
        Monitor screen for changes over time.
        
        Args:
            interval_seconds: Time between captures
            max_iterations: Maximum number of captures
            region: Screen region to monitor
        
        Returns:
            List of VisionResult objects for changes detected
        """
        if self.verbose:
            print(f"Starting monitor mode: {max_iterations} iterations, {interval_seconds}s interval")

        results = []

        for i in range(max_iterations):
            if self.verbose:
                print(f"\nIteration {i+1}/{max_iterations}...")

            current_image, path = self._capture_screenshot(region)

            if self.previous_screenshot is not None:
                # Compare with previous
                if self._has_significant_change(self.previous_screenshot, current_image):
                    if self.verbose:
                        print("  Change detected!")
                    result = self.analyze(
                        mode="monitor",
                        screenshot_path=path
                    )
                    results.append(result)
                else:
                    if self.verbose:
                        print("  No significant change")

            self.previous_screenshot = current_image

            if i < max_iterations - 1:
                time.sleep(interval_seconds)

        if self.verbose:
            print(f"\nMonitoring complete. {len(results)} changes detected.")

        return results

    def _has_significant_change(
        self,
        img1: Image.Image,
        img2: Image.Image,
        threshold: float = 0.05
    ) -> bool:
        """Check if two images differ significantly."""
        try:
            import numpy as np

            # Downsample for speed
            arr1 = np.array(img1.resize((100, 100)))
            arr2 = np.array(img2.resize((100, 100)))

            # Calculate normalized pixel difference
            diff = np.abs(arr1.astype(float) - arr2.astype(float)).sum() / (100 * 100 * 3 * 255)
            return diff > threshold

        except ImportError:
            # Fallback if numpy not available
            return True  # Assume change to be safe


# Convenience function for direct usage
def analyze_screen(
    mode: str = "describe",
    screenshot_path: str = None,
    **kwargs
) -> VisionResult:
    """
    Quick screen analysis function.
    
    Args:
        mode: Analysis mode (describe/detect/ocr/errors/monitor/test)
        screenshot_path: Path to screenshot, or None to capture current screen
        **kwargs: Additional arguments for VisionAnalyzer including:
            - window_id: Capture specific window by ID
            - app_name: Capture window by app name
            - window_title: Filter by title pattern
            - window_title_regex: Treat window_title as regex
    
    Returns:
        VisionResult with analysis
    
    Examples:
        # Full screen
        analyze_screen(mode="describe")
        
        # Specific window
        analyze_screen(mode="describe", app_name="Google Chrome")
        
        # Window with title filter
        analyze_screen(
            mode="describe",
            app_name="Google Chrome",
            window_title="Canvas.*",
            window_title_regex=True
        )
    """
    # Separate kwargs for VisionAnalyzer constructor vs analyze() method
    analyzer_kwargs = {}
    analyze_kwargs = {}
    
    # VisionAnalyzer constructor params
    analyzer_param_names = {'output_dir', 'api_key', 'model', 'save_screenshots', 'verbose'}
    # analyze() method params (window-related)
    analyze_param_names = {'window_id', 'app_name', 'window_title', 'window_title_regex', 
                           'include_shadow', 'region', 'custom_prompt', 'output_format'}
    
    for key, value in kwargs.items():
        if key in analyzer_param_names:
            analyzer_kwargs[key] = value
        elif key in analyze_param_names:
            analyze_kwargs[key] = value
    
    analyzer = VisionAnalyzer(**analyzer_kwargs)
    return analyzer.analyze(mode=mode, screenshot_path=screenshot_path, **analyze_kwargs)
