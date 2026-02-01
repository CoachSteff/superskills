"""Unit tests for TimingSync."""

import pytest
from pathlib import Path
from unittest.mock import patch
from superskills.video_recorder.src import TimingSync, TimedSlide


class TestTimingSync:
    """Test slide-audio timing synchronization."""
    
    def test_timed_slide_dataclass(self):
        """Test TimedSlide dataclass."""
        slide = TimedSlide(
            slide_index=0,
            start_ms=0,
            duration_ms=5000,
            slide_data={"type": "title", "heading": "Test"}
        )
        
        assert slide.slide_index == 0
        assert slide.start_ms == 0
        assert slide.duration_ms == 5000
        assert slide.slide_data['heading'] == "Test"
    
    @patch('superskills.video_recorder.src.TimingSync.subprocess.run')
    def test_auto_timing_equal_distribution(self, mock_run, tmp_path):
        """Test equal distribution of slides across audio."""
        mock_run.return_value.stdout = "30.0\n"  # 30 seconds audio
        
        timing = TimingSync()
        slides = [
            {"type": "title", "heading": "Slide 1"},
            {"type": "content", "heading": "Slide 2"},
            {"type": "title", "heading": "Slide 3"}
        ]
        audio_path = tmp_path / "audio.mp3"
        
        timed_slides = timing.auto_timing(slides, audio_path)
        
        assert len(timed_slides) == 3
        assert all(isinstance(ts, TimedSlide) for ts in timed_slides)
        assert timed_slides[0].duration_ms == 10000  # 30s / 3 slides = 10s each
        assert timed_slides[1].start_ms == 10000
        assert timed_slides[2].start_ms == 20000
    
    @patch('superskills.video_recorder.src.TimingSync.subprocess.run')
    def test_auto_timing_explicit_duration(self, mock_run, tmp_path):
        """Test explicit duration override."""
        mock_run.return_value.stdout = "30.0\n"
        
        timing = TimingSync()
        slides = [
            {"type": "title", "heading": "Slide 1", "duration_ms": 15000},
            {"type": "title", "heading": "Slide 2"}
        ]
        audio_path = tmp_path / "audio.mp3"
        
        timed_slides = timing.auto_timing(slides, audio_path)
        
        assert timed_slides[0].duration_ms == 15000  # Explicit override
        assert timed_slides[1].duration_ms == 15000  # Default calculated
    
    @patch('superskills.video_recorder.src.TimingSync.subprocess.run')
    def test_auto_timing_empty_slides(self, mock_run, tmp_path):
        """Test empty slides list."""
        mock_run.return_value.stdout = "30.0\n"
        
        timing = TimingSync()
        slides = []
        audio_path = tmp_path / "audio.mp3"
        
        timed_slides = timing.auto_timing(slides, audio_path)
        
        assert timed_slides == []
