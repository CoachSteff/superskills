"""Unit tests for Vision Analyzer."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io
import json

from superskills.vision.src import VisionAnalyzer, VisionResult, ScreenCapture, ScreenInfo


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini API client."""
    with patch('superskills.vision.src.VisionAnalyzer.genai.Client') as mock:
        client = MagicMock()
        
        # Mock file upload
        uploaded_file = MagicMock()
        uploaded_file.name = "test_file"
        client.files.upload.return_value = uploaded_file
        
        # Mock generate_content
        response = MagicMock()
        response.text = "Test analysis result from Gemini Vision"
        client.models.generate_content.return_value = response
        
        # Mock file delete
        client.files.delete.return_value = None
        
        mock.return_value = client
        yield client


@pytest.fixture
def mock_screenshot():
    """Mock PyAutoGUI screenshot."""
    with patch('pyautogui.screenshot') as mock:
        # Create test image
        img = Image.new('RGB', (800, 600), color='white')
        mock.return_value = img
        yield mock


class TestVisionAnalyzer:
    """Test VisionAnalyzer class."""
    
    def test_initialization_with_api_key(self, monkeypatch, mock_gemini_client):
        """Test initialization with GEMINI_API_KEY."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key_12345")
        
        analyzer = VisionAnalyzer()
        
        assert analyzer.api_key == "test_key_12345"
        assert analyzer.model == "gemini-2.0-flash-exp"
        assert analyzer.save_screenshots == True
    
    def test_initialization_without_api_key(self, monkeypatch):
        """Test initialization fails without API key."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
            VisionAnalyzer()
    
    def test_initialization_custom_params(self, monkeypatch, mock_gemini_client):
        """Test initialization with custom parameters."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer(
            output_dir="custom_output",
            model="gemini-pro",
            save_screenshots=False,
            verbose=False
        )
        
        assert str(analyzer.output_dir).endswith("custom_output")
        assert analyzer.model == "gemini-pro"
        assert analyzer.save_screenshots == False
        assert analyzer.verbose == False
    
    def test_capture_screenshot(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test screenshot capture."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer()
        image, path = analyzer._capture_screenshot()
        
        assert isinstance(image, Image.Image)
        assert image.size == (800, 600)
        mock_screenshot.assert_called_once()
    
    def test_capture_screenshot_region(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test region-specific screenshot capture."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer()
        region = (0, 0, 400, 300)
        image, path = analyzer._capture_screenshot(region=region)
        
        mock_screenshot.assert_called_once_with(region=region)
    
    def test_capture_screenshot_no_save(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test screenshot capture without saving."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer(save_screenshots=False)
        image, path = analyzer._capture_screenshot()
        
        assert isinstance(image, Image.Image)
        assert path is None
    
    def test_analyze_describe_mode(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test analyze with describe mode."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer(verbose=False)
        result = analyzer.analyze(mode="describe")
        
        assert isinstance(result, VisionResult)
        assert result.mode == "describe"
        assert result.description == "Test analysis result from Gemini Vision"
        assert result.timestamp
        assert result.metadata
        mock_gemini_client.models.generate_content.assert_called_once()
    
    def test_analyze_detect_mode(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test analyze with detect mode."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        # Mock response with UI elements
        response = MagicMock()
        response.text = """
- Type: button
  Label: Submit
  Position: center
  State: enabled
        """
        mock_gemini_client.models.generate_content.return_value = response
        
        analyzer = VisionAnalyzer(verbose=False)
        result = analyzer.analyze(mode="detect")
        
        assert result.mode == "detect"
        assert result.elements is not None
    
    def test_analyze_ocr_mode(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test analyze with OCR mode."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer(verbose=False)
        result = analyzer.analyze(mode="ocr")
        
        assert result.mode == "ocr"
        assert result.text_content == "Test analysis result from Gemini Vision"
    
    def test_analyze_errors_mode(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test analyze with errors mode."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        # Mock response with errors
        response = MagicMock()
        response.text = "Critical error detected in login form"
        mock_gemini_client.models.generate_content.return_value = response
        
        analyzer = VisionAnalyzer(verbose=False)
        result = analyzer.analyze(mode="errors")
        
        assert result.mode == "errors"
        assert result.errors is not None
    
    def test_analyze_test_mode(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test analyze with test mode."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        # Mock response with test suggestions
        response = MagicMock()
        response.text = """
- Test button click behavior
- Validate form inputs
- Check error messages
        """
        mock_gemini_client.models.generate_content.return_value = response
        
        analyzer = VisionAnalyzer(verbose=False)
        result = analyzer.analyze(mode="test")
        
        assert result.mode == "test"
        assert result.suggestions is not None
        assert len(result.suggestions) > 0
    
    def test_analyze_with_existing_screenshot(self, monkeypatch, mock_gemini_client, tmp_path):
        """Test analyze with existing screenshot file."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        # Create test screenshot
        screenshot_path = tmp_path / "test.png"
        img = Image.new('RGB', (800, 600), color='blue')
        img.save(screenshot_path)
        
        analyzer = VisionAnalyzer(verbose=False)
        result = analyzer.analyze(mode="describe", screenshot_path=str(screenshot_path))
        
        assert result.screenshot_path == str(screenshot_path)
        assert result.description
    
    def test_analyze_with_custom_prompt(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test analyze with custom prompt."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer(verbose=False)
        custom_prompt = "Find the login button and describe its state"
        result = analyzer.analyze(mode="describe", custom_prompt=custom_prompt)
        
        # Verify custom prompt was used in API call
        call_args = mock_gemini_client.models.generate_content.call_args
        assert custom_prompt in str(call_args)
    
    def test_build_prompt_all_modes(self, monkeypatch, mock_gemini_client):
        """Test prompt building for all modes."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer()
        modes = ["describe", "detect", "ocr", "errors", "monitor", "test"]
        
        for mode in modes:
            prompt = analyzer._build_prompt(mode)
            assert len(prompt) > 50  # Prompt should be substantial
            assert isinstance(prompt, str)
            # Verify mode-specific content
            if mode == "describe":
                assert "description" in prompt.lower()
            elif mode == "detect":
                assert "element" in prompt.lower()
            elif mode == "ocr":
                assert "text" in prompt.lower()
    
    def test_call_gemini_vision_error_handling(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test error handling in Gemini API calls."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        # Mock API error
        mock_gemini_client.models.generate_content.side_effect = Exception("Rate limit exceeded")
        
        analyzer = VisionAnalyzer(verbose=False)
        
        with pytest.raises(ValueError, match="rate limit"):
            analyzer.analyze(mode="describe")
    
    def test_extract_ui_elements(self, monkeypatch, mock_gemini_client):
        """Test UI element extraction from response."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer()
        
        response = """
- Type: button
  Label: Submit
  Position: center-bottom
  State: enabled

- Type: input
  Label: Email
  Position: top-left
  State: focused
        """
        
        elements = analyzer._extract_ui_elements(response)
        
        assert elements is not None
        assert len(elements) >= 2
        assert any(elem.get('type') == 'button' for elem in elements)
    
    def test_extract_errors(self, monkeypatch, mock_gemini_client):
        """Test error extraction from response."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer()
        
        response = """
Critical: Login form is missing CSRF token
Low: Button text has low contrast
        """
        
        errors = analyzer._extract_errors(response)
        
        assert errors is not None
        assert len(errors) >= 2
        assert any(err.get('severity') == 'critical' for err in errors)
    
    def test_extract_test_cases(self, monkeypatch, mock_gemini_client):
        """Test test case extraction from response."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer()
        
        response = """
1. Test login button click
2. Validate email format
3. Check error message display
* Test password visibility toggle
        """
        
        suggestions = analyzer._extract_test_cases(response)
        
        assert suggestions is not None
        assert len(suggestions) >= 4


class TestScreenCapture:
    """Test ScreenCapture utilities."""
    
    def test_get_screen_size(self):
        """Test get_screen_size."""
        with patch('pyautogui.size', return_value=(1920, 1080)):
            width, height = ScreenCapture.get_screen_size()
            assert width == 1920
            assert height == 1080
    
    def test_get_mouse_position(self):
        """Test get_mouse_position."""
        with patch('pyautogui.position', return_value=(500, 300)):
            x, y = ScreenCapture.get_mouse_position()
            assert x == 500
            assert y == 300
    
    def test_get_screen_info(self):
        """Test get_screen_info."""
        with patch('pyautogui.size', return_value=(1920, 1080)), \
             patch('pyautogui.position', return_value=(500, 300)):
            
            info = ScreenCapture.get_screen_info()
            
            assert isinstance(info, ScreenInfo)
            assert info.width == 1920
            assert info.height == 1080
            assert info.mouse_x == 500
            assert info.mouse_y == 300
    
    def test_capture_region(self):
        """Test capture_region."""
        with patch('pyautogui.screenshot') as mock:
            img = Image.new('RGB', (400, 300), color='red')
            mock.return_value = img
            
            result = ScreenCapture.capture_region(100, 100, 400, 300)
            
            assert isinstance(result, Image.Image)
            mock.assert_called_once_with(region=(100, 100, 400, 300))
    
    def test_get_pixel_color(self):
        """Test get_pixel_color."""
        with patch('pyautogui.pixel', return_value=(255, 0, 0)):
            r, g, b = ScreenCapture.get_pixel_color(100, 200)
            assert r == 255
            assert g == 0
            assert b == 0


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""
    
    def test_analyze_screen(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test analyze_screen convenience function."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        from superskills.vision.src import analyze_screen
        
        result = analyze_screen(mode="describe", verbose=False)
        
        assert isinstance(result, VisionResult)
        assert result.mode == "describe"
        assert result.description


class TestVisionResult:
    """Test VisionResult dataclass."""
    
    def test_vision_result_creation(self):
        """Test creating VisionResult."""
        result = VisionResult(
            mode="describe",
            description="Test description",
            screenshot_path="/path/to/screenshot.png"
        )
        
        assert result.mode == "describe"
        assert result.description == "Test description"
        assert result.screenshot_path == "/path/to/screenshot.png"
        assert result.timestamp  # Auto-generated
        assert result.metadata == {}  # Auto-initialized
    
    def test_vision_result_with_all_fields(self):
        """Test VisionResult with all fields."""
        result = VisionResult(
            mode="detect",
            description="UI elements detected",
            elements=[{"type": "button", "label": "Submit"}],
            text_content="Sample text",
            errors=[{"severity": "low", "description": "Minor issue"}],
            suggestions=["Test case 1", "Test case 2"],
            screenshot_path="/path/to/screenshot.png",
            timestamp="2026-01-31T12:00:00",
            metadata={"model": "gemini-2.0"}
        )
        
        assert result.mode == "detect"
        assert len(result.elements) == 1
        assert result.text_content == "Sample text"
        assert len(result.errors) == 1
        assert len(result.suggestions) == 2
        assert result.metadata["model"] == "gemini-2.0"


class TestMonitorChanges:
    """Test change monitoring functionality."""
    
    def test_monitor_changes_detects_change(self, monkeypatch, mock_gemini_client, mock_screenshot):
        """Test that monitor_changes detects screen changes."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        # Create different images for each capture
        images = [
            Image.new('RGB', (800, 600), color='white'),
            Image.new('RGB', (800, 600), color='black'),  # Different color = change
        ]
        mock_screenshot.side_effect = images
        
        analyzer = VisionAnalyzer(verbose=False)
        
        # Only 2 iterations to test change detection
        results = analyzer.monitor_changes(
            interval_seconds=0.1,
            max_iterations=2
        )
        
        # Should detect the change between first and second capture
        assert isinstance(results, list)
    
    def test_has_significant_change(self, monkeypatch, mock_gemini_client):
        """Test _has_significant_change method."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer()
        
        # Same images
        img1 = Image.new('RGB', (100, 100), color='white')
        img2 = Image.new('RGB', (100, 100), color='white')
        
        assert analyzer._has_significant_change(img1, img2) == False
        
        # Different images
        img3 = Image.new('RGB', (100, 100), color='black')
        
        assert analyzer._has_significant_change(img1, img3) == True


class TestScreenshotFallback:
    """Test screenshot capture fallback mechanisms."""
    
    def test_capture_with_path_issue(self, monkeypatch, mock_gemini_client):
        """Test that PATH issue triggers fallback."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer(verbose=False)
        
        # Mock PyAutoGUI to fail with FileNotFoundError
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_screenshot.side_effect = FileNotFoundError(
                "[Errno 2] No such file or directory: 'screencapture'"
            )
            
            # Mock the fallback subprocess call
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value = None
                
                # Mock Image.open for the temp file
                with patch('PIL.Image.open') as mock_open:
                    mock_img = Mock()
                    mock_img.size = (800, 600)
                    mock_open.return_value = mock_img
                    
                    # Should not raise, should use fallback
                    image, path = analyzer._capture_screenshot()
                    
                    assert mock_subprocess.called
                    assert '/usr/sbin/screencapture' in str(mock_subprocess.call_args)
    
    def test_capture_fixes_path_on_retry(self, monkeypatch, mock_gemini_client):
        """Test that PATH is fixed before retry."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        monkeypatch.setenv("PATH", "/usr/bin:/bin")  # Missing /usr/sbin
        
        analyzer = VisionAnalyzer(verbose=False)
        
        call_count = 0
        def mock_screenshot_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call fails
                raise FileNotFoundError("[Errno 2] 'screencapture'")
            else:
                # Second call succeeds after PATH fix
                return Image.new('RGB', (800, 600), color='white')
        
        with patch('pyautogui.screenshot', side_effect=mock_screenshot_side_effect):
            image, path = analyzer._capture_screenshot()
            
            assert call_count == 2  # Tried twice
            assert isinstance(image, Image.Image)
            assert '/usr/sbin' in os.environ.get('PATH', '')
    
    def test_screencapture_capture_region_fallback(self):
        """Test ScreenCapture.capture_region fallback."""
        from superskills.vision.src import ScreenCapture
        
        # Mock PyAutoGUI to fail
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_screenshot.side_effect = FileNotFoundError("'screencapture'")
            
            # Mock subprocess fallback
            with patch('subprocess.run') as mock_subprocess:
                mock_subprocess.return_value = None
                
                with patch('PIL.Image.open') as mock_open:
                    mock_img = Mock()
                    mock_img.crop.return_value = Image.new('RGB', (400, 300))
                    mock_open.return_value = mock_img
                    
                    result = ScreenCapture.capture_region(0, 0, 400, 300)
                    
                    assert mock_subprocess.called
                    assert isinstance(result, Image.Image)


class TestWindowCapture:
    """Test window capture functionality."""
    
    def test_list_windows(self):
        """Test window enumeration via JXA."""
        from superskills.vision.src import ScreenCapture
        
        try:
            windows = ScreenCapture.list_windows()
            assert isinstance(windows, list)
            
            if windows:
                w = windows[0]
                assert 'app_name' in w
                assert 'window_id' in w
                assert 'window_title' in w
                assert 'window_index' in w
        except RuntimeError as e:
            if 'assistive access' in str(e).lower():
                pytest.skip("Requires assistive access permission")
            raise
    
    def test_list_windows_filtered(self):
        """Test window enumeration with app filter."""
        from superskills.vision.src import ScreenCapture
        
        try:
            windows = ScreenCapture.list_windows(app_name="Finder")
            assert isinstance(windows, list)
            
            for w in windows:
                assert w['app_name'] == "Finder"
        except RuntimeError as e:
            if 'assistive access' in str(e).lower():
                pytest.skip("Requires assistive access permission")
            raise
    
    def test_get_window_id_by_app(self):
        """Test window ID lookup by app name."""
        from superskills.vision.src import ScreenCapture
        
        try:
            window_id = ScreenCapture.get_window_id("Finder")
            assert isinstance(window_id, (int, type(None)))
        except RuntimeError as e:
            if 'assistive access' in str(e).lower():
                pytest.skip("Requires assistive access permission")
            raise
    
    def test_get_window_id_with_title_substring(self):
        """Test window ID lookup with title substring match."""
        from superskills.vision.src import ScreenCapture
        
        try:
            windows = ScreenCapture.list_windows(app_name="Finder")
            if windows and windows[0]['window_title']:
                title_part = windows[0]['window_title'][:5]
                if title_part:
                    window_id = ScreenCapture.get_window_id("Finder", window_title=title_part)
                    assert window_id is not None
        except RuntimeError as e:
            if 'assistive access' in str(e).lower():
                pytest.skip("Requires assistive access permission")
            raise
    
    def test_get_window_id_with_regex(self):
        """Test window ID lookup with regex pattern."""
        from superskills.vision.src import ScreenCapture
        
        try:
            window_id = ScreenCapture.get_window_id(
                "Finder",
                window_title=".*",
                use_regex=True
            )
            assert isinstance(window_id, (int, type(None)))
        except RuntimeError as e:
            if 'assistive access' in str(e).lower():
                pytest.skip("Requires assistive access permission")
            raise
    
    def test_capture_window_not_found_exception(self):
        """Test WindowNotFoundError with available windows list."""
        from superskills.vision.src import ScreenCapture, WindowNotFoundError
        
        try:
            with pytest.raises(WindowNotFoundError) as exc_info:
                ScreenCapture.capture_window(
                    app_name="NonExistentApp12345",
                    fallback_to_fullscreen=False
                )
            
            error = exc_info.value
            assert error.app_name == "NonExistentApp12345"
            assert isinstance(error.available_windows, list)
        except RuntimeError as e:
            if 'assistive access' in str(e).lower():
                pytest.skip("Requires assistive access permission")
            raise
    
    def test_capture_window_fallback_to_fullscreen(self):
        """Test fallback to full screen when window not found."""
        from superskills.vision.src import ScreenCapture
        
        try:
            with patch('pyautogui.screenshot') as mock_screenshot:
                mock_screenshot.return_value = Image.new('RGB', (1920, 1080), color='blue')
                
                image = ScreenCapture.capture_window(
                    app_name="NonExistentApp12345",
                    fallback_to_fullscreen=True
                )
                
                assert isinstance(image, Image.Image)
                assert image.size[0] > 0 and image.size[1] > 0
        except RuntimeError as e:
            if 'assistive access' in str(e).lower():
                pytest.skip("Requires assistive access permission")
            raise
    
    @patch('subprocess.run')
    @patch('PIL.Image.open')
    def test_capture_window_with_shadow(self, mock_img_open, mock_subprocess):
        """Test window capture with shadow included."""
        from superskills.vision.src import ScreenCapture
        
        mock_img = Mock()
        mock_img.size = (800, 600)
        mock_img_open.return_value = mock_img
        mock_subprocess.return_value = None
        
        with patch.object(ScreenCapture, 'get_window_id', return_value=12345):
            image = ScreenCapture.capture_window(
                app_name="TestApp",
                include_shadow=True
            )
            
            call_args = mock_subprocess.call_args[0][0]
            assert '-l' in call_args
            assert '12345' in str(call_args)
            assert '-o' not in call_args
    
    @patch('subprocess.run')
    @patch('PIL.Image.open')
    def test_capture_window_no_shadow(self, mock_img_open, mock_subprocess):
        """Test window capture without shadow (default)."""
        from superskills.vision.src import ScreenCapture
        
        mock_img = Mock()
        mock_img.size = (800, 600)
        mock_img_open.return_value = mock_img
        mock_subprocess.return_value = None
        
        with patch.object(ScreenCapture, 'get_window_id', return_value=12345):
            image = ScreenCapture.capture_window(
                app_name="TestApp",
                include_shadow=False
            )
            
            call_args = mock_subprocess.call_args[0][0]
            assert '-o' in call_args
    
    def test_vision_analyzer_with_window_params(self, monkeypatch, mock_gemini_client):
        """Test VisionAnalyzer.analyze() with window parameters."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        
        analyzer = VisionAnalyzer(verbose=False, save_screenshots=False)
        
        with patch.object(ScreenCapture, 'capture_window') as mock_capture:
            mock_capture.return_value = Image.new('RGB', (800, 600), color='white')
            
            result = analyzer.analyze(
                mode="describe",
                app_name="TestApp",
                window_title="Test.*",
                window_title_regex=True
            )
            
            assert mock_capture.called
            call_kwargs = mock_capture.call_args[1]
            assert call_kwargs['app_name'] == "TestApp"
            assert call_kwargs['window_title'] == "Test.*"
            assert call_kwargs['use_regex'] is True
