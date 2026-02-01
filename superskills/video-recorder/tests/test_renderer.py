"""Unit tests for SlideRenderer."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from superskills.video_recorder.src import SlideRenderer


class TestSlideRenderer:
    """Test slide rendering functionality."""
    
    def test_init_creates_output_dir(self, tmp_path):
        """Test that renderer creates output directory."""
        output_dir = tmp_path / "frames"
        renderer = SlideRenderer(output_dir=str(output_dir))
        
        assert output_dir.exists()
        assert renderer.width == 1920
        assert renderer.height == 1080
    
    def test_brand_config_loads(self):
        """Test that brand configuration loads successfully."""
        renderer = SlideRenderer()
        
        assert 'colors' in renderer.brand
        assert 'fonts' in renderer.brand
        assert 'layout' in renderer.brand
        assert renderer.brand['colors']['primary'] == '#00BFFF'
    
    @patch('superskills.video_recorder.src.SlideRenderer.sync_playwright')
    def test_render_title_slide(self, mock_playwright, tmp_path):
        """Test rendering a title slide."""
        # Mock Playwright
        mock_browser = Mock()
        mock_page = Mock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        renderer = SlideRenderer(output_dir=str(tmp_path))
        slide_data = {"type": "title", "heading": "Test Title"}
        output = tmp_path / "slide_000.png"
        
        result = renderer.render_slide(slide_data, output, 0)
        
        assert mock_page.goto.called
        assert mock_page.screenshot.called
        assert mock_browser.close.called
    
    @patch('superskills.video_recorder.src.SlideRenderer.sync_playwright')
    def test_render_content_slide(self, mock_playwright, tmp_path):
        """Test rendering a content slide with bullets."""
        mock_browser = Mock()
        mock_page = Mock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        renderer = SlideRenderer(output_dir=str(tmp_path))
        slide_data = {
            "type": "content",
            "heading": "Topics",
            "bullets": ["One", "Two", "Three"]
        }
        output = tmp_path / "slide_001.png"
        
        result = renderer.render_slide(slide_data, output, 1)
        
        assert mock_page.screenshot.called
    
    @patch('superskills.video_recorder.src.SlideRenderer.sync_playwright')
    def test_render_slides_multiple(self, mock_playwright, tmp_path):
        """Test rendering multiple slides."""
        mock_browser = Mock()
        mock_page = Mock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        renderer = SlideRenderer(output_dir=str(tmp_path))
        slides = [
            {"type": "title", "heading": "Slide 1"},
            {"type": "content", "heading": "Slide 2", "bullets": ["A", "B"]},
            {"type": "title", "heading": "Slide 3"}
        ]
        
        frames = renderer.render_slides(slides)
        
        assert len(frames) == 3
        assert all(isinstance(f, Path) for f in frames)
