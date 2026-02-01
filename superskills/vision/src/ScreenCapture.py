"""
ScreenCapture.py - Utilities for screen capture and interaction.
"""
import json
import os
import re
import subprocess
import tempfile
import pyautogui
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from PIL import Image


@dataclass
class ScreenInfo:
    """Information about the screen."""
    width: int
    height: int
    mouse_x: int
    mouse_y: int


class WindowNotFoundError(Exception):
    """Raised when requested window is not found."""
    
    def __init__(self, app_name: str, window_title: Optional[str], available_windows: List[Dict]):
        self.app_name = app_name
        self.window_title = window_title
        self.available_windows = available_windows
        
        msg = f"Window not found for app '{app_name}'"
        if window_title:
            msg += f" with title matching '{window_title}'"
        
        if available_windows:
            msg += f"\n\nAvailable windows for '{app_name}':"
            for i, w in enumerate(available_windows[:10], 1):
                msg += f"\n  {i}. {w['window_title']} (ID: {w['window_id']})"
        else:
            msg += f"\n\n'{app_name}' has no windows or is not running."
        
        super().__init__(msg)


class ScreenCapture:
    """Utilities for screen capture and interaction."""

    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """Get screen dimensions.
        
        Returns:
            Tuple of (width, height)
        """
        return pyautogui.size()

    @staticmethod
    def get_mouse_position() -> Tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            Tuple of (x, y)
        """
        return pyautogui.position()

    @staticmethod
    def get_screen_info() -> ScreenInfo:
        """Get comprehensive screen information.
        
        Returns:
            ScreenInfo with dimensions and mouse position
        """
        width, height = pyautogui.size()
        mouse_x, mouse_y = pyautogui.position()
        return ScreenInfo(width, height, mouse_x, mouse_y)

    @staticmethod
    def capture_region(x: int, y: int, width: int, height: int) -> Image.Image:
        """
        Capture specific screen region with hybrid PyAutoGUI/subprocess approach.
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Region width
            height: Region height
        
        Returns:
            PIL Image of the captured region
        """
        region = (x, y, width, height)
        
        # Attempt 1: Try PyAutoGUI
        try:
            return pyautogui.screenshot(region=region)
        
        except FileNotFoundError as e:
            if 'screencapture' not in str(e):
                raise
            
            # Attempt 2: Fix PATH and retry
            env_path = os.environ.get('PATH', '')
            if '/usr/sbin' not in env_path:
                os.environ['PATH'] = f"/usr/sbin:{env_path}"
            
            try:
                return pyautogui.screenshot(region=region)
            
            except (FileNotFoundError, Exception):
                # Attempt 3: Fallback to subprocess
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp_path = tmp.name
                
                try:
                    # Capture full screen and crop
                    subprocess.run(['/usr/sbin/screencapture', '-x', tmp_path],
                                 check=True, capture_output=True)
                    full_screenshot = Image.open(tmp_path)
                    return full_screenshot.crop((x, y, x + width, y + height))
                
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

    @staticmethod
    def locate_on_screen(image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """Find image on screen (for visual automation).
        
        Args:
            image_path: Path to image to locate
            confidence: Match confidence (0.0-1.0)
        
        Returns:
            Tuple of (x, y) if found, None otherwise
        """
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return (location.left, location.top)
        except Exception:
            pass
        return None

    @staticmethod
    def get_pixel_color(x: int, y: int) -> Tuple[int, int, int]:
        """Get RGB color of pixel at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            Tuple of (r, g, b)
        """
        return pyautogui.pixel(x, y)

    @staticmethod
    def list_windows(app_name: Optional[str] = None) -> List[Dict[str, any]]:
        """
        List all windows or windows for a specific application using JXA.
        
        Args:
            app_name: Optional app name filter (e.g., "Google Chrome")
        
        Returns:
            List of dicts with keys: app_name, window_id, window_title, window_index
        
        Example:
            [
                {"app_name": "Google Chrome", "window_id": 12345, 
                 "window_title": "Canvas Presenter", "window_index": 0},
                ...
            ]
        """
        jxa_script = '''
        ObjC.import('stdlib');
        const se = Application('System Events');
        const processes = se.processes.whose({visible: true});
        const result = [];
        for (let proc of processes()) {
            const procName = proc.name();
            const windows = proc.windows();
            for (let i = 0; i < windows.length; i++) {
                try {
                    result.push({
                        app_name: procName,
                        window_id: windows[i].id(),
                        window_title: windows[i].name(),
                        window_index: i
                    });
                } catch (e) {
                    // Skip windows that can't be accessed
                }
            }
        }
        JSON.stringify(result);
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-l', 'JavaScript', '-e', jxa_script],
                capture_output=True,
                text=True,
                check=True
            )
            
            windows = json.loads(result.stdout.strip())
            
            # Filter by app_name if provided
            if app_name:
                windows = [w for w in windows if w['app_name'] == app_name]
            
            return windows
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to enumerate windows: {e.stderr}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse window list: {e}")

    @staticmethod
    def get_window_id(
        app_name: str,
        window_title: Optional[str] = None,
        use_regex: bool = False
    ) -> Optional[int]:
        """
        Get window ID for a specific application window.
        
        Args:
            app_name: Application name (e.g., "Google Chrome")
            window_title: Optional title filter (substring or regex)
            use_regex: If True, treat window_title as regex pattern
        
        Returns:
            Window ID (int) or None if not found
        
        Examples:
            # Get first Chrome window
            get_window_id("Google Chrome")
            
            # Filter by exact substring
            get_window_id("Google Chrome", "Canvas Presenter")
            
            # Filter by regex pattern
            get_window_id("Google Chrome", "Canvas.*", use_regex=True)
        """
        windows = ScreenCapture.list_windows(app_name=app_name)
        
        if not windows:
            return None
        
        # No filter - return first window
        if not window_title:
            return windows[0]['window_id']
        
        # Filter by title
        for window in windows:
            title = window['window_title']
            
            if use_regex:
                if re.search(window_title, title, re.IGNORECASE):
                    return window['window_id']
            else:
                if window_title.lower() in title.lower():
                    return window['window_id']
        
        return None

    @staticmethod
    def capture_window(
        window_id: Optional[int] = None,
        app_name: Optional[str] = None,
        window_title: Optional[str] = None,
        use_regex: bool = False,
        include_shadow: bool = False,
        fallback_to_fullscreen: bool = True
    ) -> Image.Image:
        """
        Capture a specific window by ID or app name.
        
        Args:
            window_id: Direct window ID (fastest, if known)
            app_name: Find window by app name
            window_title: Filter by title (substring or regex)
            use_regex: Treat window_title as regex pattern
            include_shadow: Include window shadow (-o flag if False)
            fallback_to_fullscreen: If True, capture full screen on error with warning
        
        Returns:
            PIL Image of the window
        
        Raises:
            WindowNotFoundError: If window not found and fallback_to_fullscreen=False
        
        Examples:
            # By direct window ID
            capture_window(window_id=12345)
            
            # By app name (first window)
            capture_window(app_name="Google Chrome")
            
            # By app + title regex
            capture_window(app_name="Google Chrome", window_title="Canvas.*", use_regex=True)
        """
        # Resolve window_id if not provided
        if window_id is None:
            if app_name is None:
                raise ValueError("Either window_id or app_name must be provided")
            
            window_id = ScreenCapture.get_window_id(
                app_name=app_name,
                window_title=window_title,
                use_regex=use_regex
            )
            
            if window_id is None:
                # Get available windows for error message
                available_windows = ScreenCapture.list_windows(app_name=app_name)
                
                if fallback_to_fullscreen:
                    print(f"Warning: Window not found for app '{app_name}'")
                    if window_title:
                        print(f"  with title matching '{window_title}'")
                    print("  Falling back to full screen capture...")
                    
                    # Fallback to full screen via PyAutoGUI
                    return pyautogui.screenshot()
                else:
                    raise WindowNotFoundError(app_name, window_title, available_windows)
        
        # Capture window using screencapture -l
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Build command
            cmd = ['/usr/sbin/screencapture', '-l', str(window_id), '-x']
            
            # Add -o flag if no shadow (default)
            if not include_shadow:
                cmd.append('-o')
            
            cmd.append(tmp_path)
            
            # Execute capture
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Load and return image
            screenshot = Image.open(tmp_path)
            return screenshot
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
