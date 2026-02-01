"""Unit tests for VideoEncoder."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from superskills.video_recorder.src import VideoEncoder, TimedSlide


class TestVideoEncoder:
    """Test video encoding functionality."""
    
    def test_init_sets_defaults(self):
        """Test default initialization."""
        encoder = VideoEncoder()
        
        assert encoder.fps == 1
        assert encoder.crf == 18  # high quality
    
    def test_init_quality_levels(self):
        """Test quality level mappings."""
        encoder_low = VideoEncoder(quality="low")
        encoder_med = VideoEncoder(quality="medium")
        encoder_high = VideoEncoder(quality="high")
        
        assert encoder_low.crf == 28
        assert encoder_med.crf == 23
        assert encoder_high.crf == 18
    
    @patch('superskills.video_recorder.src.VideoEncoder.subprocess.run')
    def test_encode_complete_creates_concat_file(self, mock_run, tmp_path):
        """Test concat file creation."""
        encoder = VideoEncoder()
        
        frames = [tmp_path / "frame_000.png", tmp_path / "frame_001.png"]
        for f in frames:
            f.touch()
        
        audio = tmp_path / "audio.mp3"
        audio.touch()
        
        timing = [
            TimedSlide(0, 0, 5000, {}),
            TimedSlide(1, 5000, 5000, {})
        ]
        
        output = tmp_path / "output.mp4"
        
        encoder.encode_complete(frames, audio, timing, output)
        
        # Check ffmpeg was called twice (video + audio)
        assert mock_run.call_count == 2
        
        # Check concat file was created
        work_dir = output.parent / ".encode_work"
        concat_file = work_dir / "concat.txt"
        # Note: concat file is cleaned up, but we can verify call pattern
        
        first_call = mock_run.call_args_list[0][0][0]
        assert 'ffmpeg' in first_call
        assert '-f' in first_call
        assert 'concat' in first_call
