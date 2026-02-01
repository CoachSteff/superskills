"""Unit tests for AudioGenerator."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from superskills.video_recorder.src import AudioGenerator


class TestAudioGenerator:
    """Test audio generation functionality."""
    
    def test_init_sets_defaults(self):
        """Test default initialization."""
        audio_gen = AudioGenerator()
        
        assert audio_gen.voice == "steff"
        assert audio_gen.profile_type == "podcast"
    
    @patch('superskills.video_recorder.src.AudioGenerator.subprocess.run')
    def test_get_duration(self, mock_run, tmp_path):
        """Test audio duration measurement."""
        mock_run.return_value.stdout = "45.2\n"
        
        audio_gen = AudioGenerator()
        audio_path = tmp_path / "audio.mp3"
        
        duration = audio_gen.get_duration(audio_path)
        
        assert duration == 45.2
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert 'ffprobe' in call_args
    
    @patch('superskills.video_recorder.src.AudioGenerator.Voiceover')
    def test_generate_with_narrator_import(self, mock_voiceover, tmp_path):
        """Test audio generation using narrator skill."""
        mock_instance = Mock()
        mock_instance.generate.return_value.audio_path = str(tmp_path / "audio.mp3")
        mock_voiceover.return_value = mock_instance
        
        audio_gen = AudioGenerator()
        output_path = tmp_path / "audio.mp3"
        
        result = audio_gen.generate("Test script", output_path)
        
        assert mock_voiceover.called
        assert mock_instance.generate.called
        assert result.name == "audio.mp3"
    
    @patch('superskills.video_recorder.src.AudioGenerator.subprocess.run')
    def test_generate_fallback_to_cli(self, mock_run, tmp_path):
        """Test fallback to CLI when import fails."""
        with patch('superskills.video_recorder.src.AudioGenerator.Voiceover', side_effect=ImportError):
            audio_gen = AudioGenerator()
            output_path = tmp_path / "audio.mp3"
            
            result = audio_gen.generate("Test script", output_path)
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert 'superskills' in call_args
            assert 'narrator-podcast' in call_args
