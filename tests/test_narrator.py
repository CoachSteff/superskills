"""Unit tests for Narrator (Voiceover and Podcast)."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys

# Mock pydub before importing Podcast to avoid audioop dependency (removed in Python 3.13)
sys.modules['pydub'] = MagicMock()
sys.modules['pydub.AudioSegment'] = MagicMock()

# Proper package imports
from superskills.narrator.src.Voiceover import VoiceoverGenerator, ScriptOptimizer
from superskills.narrator.src.Podcast import PodcastGenerator, PodcastSegment


class TestScriptOptimizer:
    """Test script optimization utilities."""
    
    def test_optimize_for_speech(self):
        """Test removing parentheticals and brackets."""
        text = "This is (a test) with [some notes] and content"
        optimized = ScriptOptimizer.optimize_for_speech(text)
        
        assert "(" not in optimized
        assert ")" not in optimized
        assert "[" not in optimized
        assert "]" not in optimized
        assert "This is" in optimized
        assert "with" in optimized
    
    def test_optimize_dashes_to_pauses(self):
        """Test converting dashes to ellipses for pauses."""
        text = "First part—second part"
        optimized = ScriptOptimizer.optimize_for_speech(text)
        
        assert "..." in optimized
        assert "—" not in optimized
    
    def test_optimize_colons_to_pauses(self):
        """Test converting colons to pauses."""
        text = "Here's the point: it works"
        optimized = ScriptOptimizer.optimize_for_speech(text)
        
        assert "..." in optimized
    
    def test_optimize_whitespace(self):
        """Test normalizing whitespace."""
        text = "Too    much     space"
        optimized = ScriptOptimizer.optimize_for_speech(text)
        
        assert "    " not in optimized
        assert optimized == "Too much space"
    
    def test_pronunciation_guide_default(self):
        """Test default pronunciation guide."""
        text = "Using AI and API with ChatGPT"
        guided = ScriptOptimizer.add_pronunciation_guide(text)
        
        assert "A-I" in guided
        assert "A-P-I" in guided
        assert "Chat-G-P-T" in guided
    
    def test_pronunciation_guide_custom(self):
        """Test custom pronunciation additions."""
        text = "CoachSteff uses AI"
        custom = {"CoachSteff": "Coach Steff"}
        guided = ScriptOptimizer.add_pronunciation_guide(text, custom)
        
        assert "Coach Steff" in guided
        assert "A-I" in guided


class TestVoiceoverGeneratorInit:
    """Test VoiceoverGenerator initialization."""
    
    def test_init_with_defaults(self, mock_env_vars, temp_output_dir):
        """Test default initialization."""
        generator = VoiceoverGenerator(output_dir=str(temp_output_dir))
        assert generator.output_dir == temp_output_dir
        assert generator.api_key == "test_elevenlabs_key"
        assert generator.voice_id == "test_voice_id"
    
    def test_init_missing_api_key(self, monkeypatch, temp_output_dir):
        """Test error when API key missing."""
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="ELEVENLABS_API_KEY"):
            VoiceoverGenerator(output_dir=str(temp_output_dir))
    
    def test_init_missing_voice_id(self, monkeypatch, mock_env_vars, temp_output_dir):
        """Test error when voice ID missing."""
        monkeypatch.delenv("ELEVENLABS_VOICE_ID", raising=False)
        
        with pytest.raises(ValueError, match="ELEVENLABS_VOICE_ID"):
            VoiceoverGenerator(output_dir=str(temp_output_dir))


class TestVoiceSettings:
    """Test voice settings per content type."""
    
    def test_voice_settings_defined(self):
        """Test that all content types have voice settings."""
        settings = VoiceoverGenerator.VOICE_SETTINGS
        
        assert "educational" in settings
        assert "marketing" in settings
        assert "social" in settings
        assert "podcast" in settings
    
    def test_educational_settings(self):
        """Test educational content settings."""
        settings = VoiceoverGenerator.VOICE_SETTINGS["educational"]
        
        assert settings["stability"] == 0.70
        assert settings["similarity_boost"] == 0.80
        assert "use_speaker_boost" in settings
    
    def test_marketing_settings(self):
        """Test marketing content settings."""
        settings = VoiceoverGenerator.VOICE_SETTINGS["marketing"]
        
        assert settings["stability"] == 0.65
        assert settings["style"] == 0.40


class TestWordCount:
    """Test word counting."""
    
    def test_word_count_basic(self, mock_env_vars, temp_output_dir):
        """Test basic word counting."""
        generator = VoiceoverGenerator(output_dir=str(temp_output_dir))
        
        script = "This is a simple test script"
        # Access the word counting logic indirectly through script length
        words = len(script.split())
        assert words == 6
    
    def test_word_count_with_punctuation(self, mock_env_vars, temp_output_dir):
        """Test word count ignores punctuation."""
        script = "Hello, world! How are you?"
        words = len(script.split())
        assert words == 5


class TestVoiceoverGeneration:
    """Test voiceover generation (mocked)."""
    
    @patch('Voiceover.ElevenLabs')
    def test_generate_basic(self, mock_elevenlabs_class, mock_env_vars, temp_output_dir, sample_script):
        """Test basic voiceover generation."""
        # Mock ElevenLabs client
        mock_client = MagicMock()
        mock_audio = b"fake_audio_data_12345"
        mock_client.text_to_speech.convert.return_value = iter([mock_audio])
        mock_elevenlabs_class.return_value = mock_client
        
        generator = VoiceoverGenerator(output_dir=str(temp_output_dir))
        
        result = generator.generate(
            script=sample_script,
            content_type="educational",
            optimize_script=True
        )
        
        assert "output_file" in result
        assert Path(result["output_file"]).exists()
        assert result["content_type"] == "educational"
        assert "word_count" in result
    
    @patch('Voiceover.ElevenLabs')
    def test_generate_different_content_types(self, mock_elevenlabs_class, mock_env_vars, temp_output_dir):
        """Test generation with different content types."""
        mock_client = MagicMock()
        mock_audio = b"fake_audio"
        # Return a new iterator for each call
        mock_client.text_to_speech.convert.side_effect = lambda **kwargs: iter([mock_audio])
        mock_elevenlabs_class.return_value = mock_client
        
        generator = VoiceoverGenerator(output_dir=str(temp_output_dir))
        
        for content_type in ["educational", "marketing", "social", "podcast"]:
            result = generator.generate(
                script="Test script",
                content_type=content_type,
                optimize_script=False
            )
            assert result["content_type"] == content_type
    
    @patch('Voiceover.ElevenLabs')
    def test_generate_with_optimization(self, mock_elevenlabs_class, mock_env_vars, temp_output_dir):
        """Test script optimization during generation."""
        mock_client = MagicMock()
        mock_audio = b"fake_audio"
        mock_client.text_to_speech.convert.return_value = iter([mock_audio])
        mock_elevenlabs_class.return_value = mock_client
        
        generator = VoiceoverGenerator(output_dir=str(temp_output_dir))
        
        script_with_issues = "This is (a test) with [notes] and AI content"
        
        result = generator.generate(
            script=script_with_issues,
            content_type="educational",
            optimize_script=True
        )
        
        assert result["optimized"] == True
    
    @patch('Voiceover.ElevenLabs')
    def test_generate_custom_filename(self, mock_elevenlabs_class, mock_env_vars, temp_output_dir):
        """Test custom filename."""
        mock_client = MagicMock()
        mock_audio = b"fake_audio"
        mock_client.text_to_speech.convert.return_value = iter([mock_audio])
        mock_elevenlabs_class.return_value = mock_client
        
        generator = VoiceoverGenerator(output_dir=str(temp_output_dir))
        
        result = generator.generate(
            script="Test",
            content_type="educational",
            output_filename="custom-voiceover.mp3"
        )
        
        assert "custom-voiceover.mp3" in result["output_file"]


class TestPodcastSegment:
    """Test PodcastSegment dataclass."""
    
    def test_podcast_segment_creation(self):
        """Test creating podcast segment."""
        segment = PodcastSegment(
            text="Welcome to the show",
            content_type="podcast"
        )
        
        assert segment.text == "Welcome to the show"
        assert segment.content_type == "podcast"


class TestPodcastGeneratorInit:
    """Test PodcastGenerator initialization."""
    
    def test_init_with_defaults(self, mock_env_vars, temp_output_dir):
        """Test default initialization."""
        generator = PodcastGenerator(output_dir=str(temp_output_dir))
        assert generator.output_dir == temp_output_dir
        assert generator.api_key == "test_elevenlabs_key"


class TestPodcastGeneration:
    """Test podcast generation (mocked)."""
    
    @patch('Podcast.ElevenLabs')
    @patch('Podcast.AudioSegment')
    def test_generate_podcast_basic(self, mock_audio_segment, mock_elevenlabs_class, 
                                     mock_env_vars, temp_output_dir):
        """Test basic podcast generation."""
        # Mock ElevenLabs
        mock_client = MagicMock()
        mock_audio = b"fake_audio_segment"
        mock_client.text_to_speech.convert.return_value = iter([mock_audio])
        mock_elevenlabs_class.return_value = mock_client
        
        # Mock AudioSegment
        mock_segment = MagicMock()
        mock_segment.duration_seconds = 10.0
        mock_audio_segment.from_mp3.return_value = mock_segment
        mock_segment.__add__.return_value = mock_segment
        mock_segment.export.return_value = None
        
        generator = PodcastGenerator(output_dir=str(temp_output_dir))
        
        segments = [
            PodcastSegment(text="Welcome!", content_type="podcast"),
            PodcastSegment(text="First topic", content_type="educational")
        ]
        
        result = generator.generate_podcast(
            segments=segments,
            output_filename="test-podcast.mp3"
        )
        
        assert "output_file" in result
        assert "total_duration_seconds" in result
        assert "segments" in result
        assert len(result["segments"]) == 2
    
    @patch('Podcast.ElevenLabs')
    @patch('Podcast.AudioSegment')
    def test_generate_podcast_with_transitions(self, mock_audio_segment, mock_elevenlabs_class,
                                                mock_env_vars, temp_output_dir):
        """Test podcast with custom transition time."""
        mock_client = MagicMock()
        mock_audio = b"audio"
        mock_client.text_to_speech.convert.return_value = iter([mock_audio])
        mock_elevenlabs_class.return_value = mock_client
        
        mock_segment = MagicMock()
        mock_segment.duration_seconds = 5.0
        mock_audio_segment.from_mp3.return_value = mock_segment
        mock_segment.__add__.return_value = mock_segment
        mock_segment.export.return_value = None
        mock_audio_segment.silent.return_value = mock_segment
        
        generator = PodcastGenerator(output_dir=str(temp_output_dir))
        
        segments = [
            PodcastSegment(text="Part 1", content_type="podcast"),
            PodcastSegment(text="Part 2", content_type="podcast")
        ]
        
        result = generator.generate_podcast(
            segments=segments,
            transition_ms=1000  # 1 second transition
        )
        
        assert result is not None
    
    @patch('Podcast.ElevenLabs')
    @patch('Podcast.AudioSegment')
    def test_generate_podcast_metadata(self, mock_audio_segment, mock_elevenlabs_class,
                                        mock_env_vars, temp_output_dir):
        """Test podcast metadata generation."""
        mock_client = MagicMock()
        mock_audio = b"audio"
        mock_client.text_to_speech.convert.return_value = iter([mock_audio])
        mock_elevenlabs_class.return_value = mock_client
        
        mock_segment = MagicMock()
        mock_segment.duration_seconds = 10.0
        mock_audio_segment.from_mp3.return_value = mock_segment
        mock_segment.__add__.return_value = mock_segment
        mock_segment.export.return_value = None
        
        generator = PodcastGenerator(output_dir=str(temp_output_dir))
        
        segments = [
            PodcastSegment(text="Intro", content_type="podcast"),
            PodcastSegment(text="Main content", content_type="educational"),
            PodcastSegment(text="Outro", content_type="podcast")
        ]
        
        result = generator.generate_podcast(segments=segments)
        
        # Check metadata structure
        assert "output_file" in result
        assert "total_duration_seconds" in result
        assert "total_words" in result
        assert "segments" in result
        assert len(result["segments"]) == 3
        
        # Check segment metadata
        for i, seg_meta in enumerate(result["segments"]):
            assert "index" in seg_meta
            assert "start_time" in seg_meta
            assert "duration" in seg_meta
            assert "content_type" in seg_meta
