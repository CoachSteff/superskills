"""
Test suite for AudiobookGenerator.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, mock_open

from superskills.audiobook.src.AudiobookGenerator import (
    AudiobookGenerator,
    AudiobookResult,
    ChapterAudioResult,
    ScriptOptimizer
)
from superskills.audiobook.src.ChapterDetector import Chapter
from superskills.audiobook.src.tts.base import TTSProvider, TTSConfig


class TestScriptOptimizer:
    """Tests for ScriptOptimizer class."""

    def test_optimize_removes_parentheticals(self):
        """Test removal of parenthetical content."""
        text = "This is text (with parenthetical) content."
        result = ScriptOptimizer.optimize_for_speech(text)
        assert "(with parenthetical)" not in result
        assert "This is text" in result

    def test_optimize_removes_brackets(self):
        """Test removal of bracket content."""
        text = "Text with [bracketed content] here."
        result = ScriptOptimizer.optimize_for_speech(text)
        assert "[bracketed content]" not in result

    def test_optimize_replaces_dashes(self):
        """Test replacement of dashes with pauses."""
        text = "Text — with em-dash and - hyphen."
        result = ScriptOptimizer.optimize_for_speech(text)
        assert "—" not in result
        assert "..." in result

    def test_optimize_normalizes_whitespace(self):
        """Test whitespace normalization."""
        text = "Text  with   extra    spaces."
        result = ScriptOptimizer.optimize_for_speech(text)
        assert "  " not in result


class TestAudiobookGenerator:
    """Tests for AudiobookGenerator class."""
    
    def _create_mock_config(self):
        """Helper to create a mock AudiobookConfig."""
        mock_config = MagicMock()
        mock_config.get_profile.return_value = {
            "provider": "gemini",
            "model": "gemini-2.5-flash-preview-tts",
            "voice_id": "Puck"
        }
        return mock_config

    def test_init_with_api_key(self):
        """Test initialization with explicit provider config."""
        # Mock the TTS provider factory
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        mock_provider.validate_config.return_value = None
        
        with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
            with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                with patch.dict("os.environ", {"ELEVENLABS_API_KEY": "test_key"}):
                    generator = AudiobookGenerator(tts_provider="elevenlabs")
                    assert generator.tts_provider == mock_provider

    def test_init_without_api_key_raises_error(self):
        """Test initialization without API key raises error."""
        # Mock the config, but no API key in environment
        with patch.dict("os.environ", {}, clear=True):
            with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                with patch("superskills.core.credentials.load_credentials"):  # Mock credential loading
                    with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
                        AudiobookGenerator()

    def test_init_from_env_var(self):
        """Test initialization from environment variable."""
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        mock_provider.validate_config.return_value = None
        
        with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
            with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                with patch.dict("os.environ", {"GEMINI_API_KEY": "env_key"}):
                    generator = AudiobookGenerator()
                    assert generator.tts_provider == mock_provider

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert AudiobookGenerator._sanitize_filename("Test: File/Name") == "test_filename"
        assert AudiobookGenerator._sanitize_filename("A" * 100) == "a" * 50
        assert AudiobookGenerator._sanitize_filename("  spaces  ") == "spaces"

    def test_format_duration_hours(self):
        """Test duration formatting with hours."""
        result = AudiobookGenerator._format_duration(3665)
        assert result == "1h 1m 5s"

    def test_format_duration_minutes(self):
        """Test duration formatting with minutes."""
        result = AudiobookGenerator._format_duration(125)
        assert result == "2m 5s"

    def test_format_duration_seconds(self):
        """Test duration formatting with seconds only."""
        result = AudiobookGenerator._format_duration(45)
        assert result == "45s"

    @patch("superskills.audiobook.src.AudiobookGenerator.DocumentParser")
    @patch("superskills.audiobook.src.AudiobookGenerator.ChapterDetector")
    def test_generate_audiobook_success(self, mock_detector_class, mock_parser_class):
        """Test successful audiobook generation."""
        # Setup mocks
        mock_parser = mock_parser_class.return_value
        mock_parser.parse_file.return_value = "Document text"
        
        mock_detector = mock_detector_class.return_value
        mock_detector.detect_chapters.return_value = [
            Chapter(1, "Chapter 1", "text " * 100, 0, 100, 100)
        ]
        
        # Mock TTS provider
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        mock_provider.validate_config.return_value = None
        mock_provider.check_quota.return_value = {
            'sufficient': True,
            'available': -1,
            'required': 100,
            'provider_supports_check': False
        }
        mock_provider.generate_speech.return_value = iter([b"audio_chunk_1", b"audio_chunk_2"])
        
        # Mock file operations
        with patch("builtins.open", mock_open()):
            with patch("pathlib.Path.mkdir"):
                with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
                    with patch("superskills.audiobook.src.AudiobookGenerator.PYDUB_AVAILABLE", False):
                        with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
                            with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                                generator = AudiobookGenerator(output_dir="/tmp/test")
                                result = generator.generate_audiobook("test.txt", "my_book")
        
        assert isinstance(result, AudiobookResult)
        assert result.total_chapters == 1
        assert result.source_file == "test.txt"
        assert result.output_prefix == "my_book"

    def test_generate_chapter_audio_model_fallback(self):
        """Test graceful error handling in chapter generation."""
        # Mock TTS provider that raises an error first, then succeeds
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        mock_provider.validate_config.return_value = None
        
        call_count = [0]
        def mock_generate(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("API Error: voice_not_fine_tuned")
            return iter([b"audio_data"])
        
        mock_provider.generate_speech.side_effect = mock_generate
        
        chapter = Chapter(1, "Test", "text " * 100, 0, 100, 100)
        
        with patch("builtins.open", mock_open()):
            with patch("pathlib.Path.mkdir"):
                with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
                    with patch("superskills.audiobook.src.AudiobookGenerator.PYDUB_AVAILABLE", False):
                        with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
                            with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                                generator = AudiobookGenerator()
                                # First call should fail and propagate error
                                with pytest.raises(Exception, match="voice_not_fine_tuned"):
                                    generator._generate_chapter_audio(chapter, "test", "Test Book")

    def test_create_metadata(self):
        """Test metadata file creation."""
        chapters = [
            Chapter(1, "Chapter 1", "text " * 100, 0, 100, 100),
            Chapter(2, "Chapter 2", "text " * 100, 100, 200, 100)
        ]
        
        audio_results = [
            ChapterAudioResult(1, "Chapter 1", "/tmp/ch1.mp3", 60.0, 100, 100),
            ChapterAudioResult(2, "Chapter 2", "/tmp/ch2.mp3", 60.0, 100, 100)
        ]
        
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        
        with patch("builtins.open", mock_open()) as mocked_file:
            with patch("pathlib.Path.mkdir"):
                with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
                    with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
                        with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                            generator = AudiobookGenerator()
                            metadata_path = generator._create_metadata(
                                chapters, audio_results, "test_book", "source.pdf"
                            )
        
        assert "metadata.json" in metadata_path
        
        # Verify JSON write was called
        handle = mocked_file()
        handle.write.assert_called()

    def test_output_directory_creation(self):
        """Test output directory is created if it doesn't exist."""
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            with patch.dict("os.environ", {"ELEVENLABS_API_KEY": "test_key"}):
                with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
                    with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                        generator = AudiobookGenerator(output_dir="/tmp/new_dir")
        
        mock_mkdir.assert_called_once()

    def test_sanitize_filename_removes_null_bytes(self):
        """Test null byte removal from filenames."""
        result = AudiobookGenerator._sanitize_filename("test\x00file\x00name")
        assert '\x00' not in result
        assert result == "testfilename"

    def test_sanitize_filename_removes_control_chars(self):
        """Test control character removal."""
        result = AudiobookGenerator._sanitize_filename("test\tfile\nname\r")
        assert '\t' not in result
        assert '\n' not in result
        assert '\r' not in result
        assert result == "testfilename"

    def test_sanitize_filename_handles_unicode(self):
        """Test Unicode normalization for Dutch characters."""
        result = AudiobookGenerator._sanitize_filename("Café naïve über")
        assert result  # Should not be empty
        assert len(result) <= 50
        # Check that accents were decomposed/normalized
        assert 'cafe' in result or 'caf' in result

    def test_sanitize_filename_fallback_empty(self):
        """Test fallback for completely sanitized strings."""
        result = AudiobookGenerator._sanitize_filename("\x00\x00\x00")
        assert result == "chapter"  # Fallback value

    def test_sanitize_filename_length_limit(self):
        """Test filename length truncation."""
        long_name = "a" * 100
        result = AudiobookGenerator._sanitize_filename(long_name)
        assert len(result) <= 50


class TestChapterRange:
    """Tests for chapter range filtering."""
    
    def _create_mock_config(self):
        """Helper to create a mock AudiobookConfig."""
        mock_config = MagicMock()
        mock_config.get_profile.return_value = {
            "provider": "gemini",
            "model": "gemini-2.5-flash-preview-tts",
            "voice_id": "Puck"
        }
        return mock_config
    
    def test_parse_chapter_range_single(self):
        """Test parsing single chapter."""
        from superskills.audiobook.src import _parse_chapter_range
        assert _parse_chapter_range("5") == (5, 5)
        assert _parse_chapter_range("1") == (1, 1)
        assert _parse_chapter_range(" 3 ") == (3, 3)
    
    def test_parse_chapter_range_range(self):
        """Test parsing chapter range."""
        from superskills.audiobook.src import _parse_chapter_range
        assert _parse_chapter_range("1-3") == (1, 3)
        assert _parse_chapter_range("5-10") == (5, 10)
        assert _parse_chapter_range(" 2 - 5 ") == (2, 5)
    
    def test_parse_chapter_range_invalid_format(self):
        """Test invalid range formats."""
        from superskills.audiobook.src import _parse_chapter_range
        
        # Too many parts
        with pytest.raises(ValueError, match="Invalid range format"):
            _parse_chapter_range("1-2-3")
        
        # Not a number
        with pytest.raises(ValueError, match="Must be an integer"):
            _parse_chapter_range("abc")
        
        # Not integers in range
        with pytest.raises(ValueError, match="must be integers"):
            _parse_chapter_range("a-b")
    
    def test_parse_chapter_range_invalid_values(self):
        """Test invalid range values."""
        from superskills.audiobook.src import _parse_chapter_range
        
        # Start < 1
        with pytest.raises(ValueError, match="must be >= 1"):
            _parse_chapter_range("0")
        
        with pytest.raises(ValueError, match="must be >= 1"):
            _parse_chapter_range("0-5")
        
        # End < start
        with pytest.raises(ValueError, match="must be >= start"):
            _parse_chapter_range("5-3")
    
    def test_generate_audiobook_with_range(self):
        """Test generating audiobook with chapter range."""
        from superskills.audiobook.src.ChapterDetector import Chapter
        from superskills.audiobook.src.DocumentParser import DocumentParser
        from superskills.audiobook.src.ChapterDetector import ChapterDetector
        from superskills.audiobook.src.AudiobookGenerator import ChapterAudioResult
        
        # Create mock chapters
        chapters = [
            Chapter(1, "Chapter 1", "text " * 100, 0, 100, 100),
            Chapter(2, "Chapter 2", "text " * 100, 100, 200, 100),
            Chapter(3, "Chapter 3", "text " * 100, 200, 300, 100),
            Chapter(4, "Chapter 4", "text " * 100, 300, 400, 100),
        ]
        
        # Mock TTS provider
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        mock_provider.validate_config.return_value = None
        mock_provider.check_quota.return_value = {
            'sufficient': True,
            'available': -1,
            'required': 100,
            'provider_supports_check': False
        }
        
        with patch.object(ChapterDetector, 'detect_chapters', return_value=chapters):
            with patch.object(DocumentParser, 'parse_file', return_value="text " * 400):
                with patch("builtins.open", mock_open()):
                    with patch("pathlib.Path.mkdir"):
                        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
                            with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
                                with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                                    generator = AudiobookGenerator()
                                    
                                    # Mock the chapter generation
                                    with patch.object(generator, '_generate_chapter_audio') as mock_gen:
                                        mock_gen.return_value = [ChapterAudioResult(
                                            chapter_number=1,
                                            chapter_title="Test",
                                            output_file="test.mp3",
                                            duration_seconds=60.0,
                                            word_count=100,
                                            words_per_minute=100
                                        )]
                                        
                                        # Test range 2-3 (should process only chapters 2 and 3)
                                        with patch("tempfile.NamedTemporaryFile"):
                                            result = generator.generate_audiobook(
                                                "test.txt",
                                                chapter_range=(2, 3)
                                            )
                                        
                                        # Should have called _generate_chapter_audio twice (chapters 2 and 3)
                                        assert mock_gen.call_count == 2
                                        assert result.total_chapters == 2
    
    def test_generate_audiobook_single_chapter(self):
        """Test generating single chapter."""
        from superskills.audiobook.src.ChapterDetector import Chapter
        from superskills.audiobook.src.DocumentParser import DocumentParser
        from superskills.audiobook.src.ChapterDetector import ChapterDetector
        from superskills.audiobook.src.AudiobookGenerator import ChapterAudioResult
        
        chapters = [
            Chapter(1, "Chapter 1", "text " * 100, 0, 100, 100),
            Chapter(2, "Chapter 2", "text " * 100, 100, 200, 100),
            Chapter(3, "Chapter 3", "text " * 100, 200, 300, 100),
        ]
        
        # Mock TTS provider
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        mock_provider.validate_config.return_value = None
        mock_provider.check_quota.return_value = {
            'sufficient': True,
            'available': -1,
            'required': 100,
            'provider_supports_check': False
        }
        
        with patch.object(ChapterDetector, 'detect_chapters', return_value=chapters):
            with patch.object(DocumentParser, 'parse_file', return_value="text " * 300):
                with patch("builtins.open", mock_open()):
                    with patch("pathlib.Path.mkdir"):
                        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
                            with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
                                with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                                    generator = AudiobookGenerator()
                                    
                                    with patch.object(generator, '_generate_chapter_audio') as mock_gen:
                                        mock_gen.return_value = [ChapterAudioResult(
                                            chapter_number=1,
                                            chapter_title="Test",
                                            output_file="test.mp3",
                                            duration_seconds=60.0,
                                            word_count=100,
                                            words_per_minute=100
                                        )]
                                        
                                        # Test single chapter
                                        with patch("tempfile.NamedTemporaryFile"):
                                            result = generator.generate_audiobook(
                                                "test.txt",
                                                chapter_range=(1, 1)
                                            )
                                        
                                        assert mock_gen.call_count == 1
                                        assert result.total_chapters == 1
    
    def test_generate_audiobook_range_exceeds_chapters(self):
        """Test range that exceeds available chapters."""
        from superskills.audiobook.src.ChapterDetector import Chapter
        from superskills.audiobook.src.DocumentParser import DocumentParser
        from superskills.audiobook.src.ChapterDetector import ChapterDetector
        
        chapters = [
            Chapter(1, "Chapter 1", "text " * 100, 0, 100, 100),
            Chapter(2, "Chapter 2", "text " * 100, 100, 200, 100),
        ]
        
        # Mock TTS provider
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        
        with patch.object(ChapterDetector, 'detect_chapters', return_value=chapters):
            with patch.object(DocumentParser, 'parse_file', return_value="text " * 200):
                with patch("builtins.open", mock_open()):
                    with patch("pathlib.Path.mkdir"):
                        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
                            with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
                                with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                                    generator = AudiobookGenerator()
                                    
                                    # Start chapter exceeds total → should raise ValueError
                                    with pytest.raises(ValueError, match="exceeds total chapters"):
                                        generator.generate_audiobook(
                                            "test.txt",
                                            chapter_range=(5, 10)
                                        )
    
    def test_generate_audiobook_range_end_exceeds(self):
        """Test range where end exceeds chapters but start is valid."""
        from superskills.audiobook.src.ChapterDetector import Chapter
        from superskills.audiobook.src.DocumentParser import DocumentParser
        from superskills.audiobook.src.ChapterDetector import ChapterDetector
        from superskills.audiobook.src.AudiobookGenerator import ChapterAudioResult
        
        chapters = [
            Chapter(1, "Chapter 1", "text " * 100, 0, 100, 100),
            Chapter(2, "Chapter 2", "text " * 100, 100, 200, 100),
            Chapter(3, "Chapter 3", "text " * 100, 200, 300, 100),
        ]
        
        # Mock TTS provider
        mock_provider = MagicMock(spec=TTSProvider)
        mock_provider.get_character_limit.return_value = 5000
        mock_provider.validate_config.return_value = None
        mock_provider.check_quota.return_value = {
            'sufficient': True,
            'available': -1,
            'required': 100,
            'provider_supports_check': False
        }
        
        with patch.object(ChapterDetector, 'detect_chapters', return_value=chapters):
            with patch.object(DocumentParser, 'parse_file', return_value="text " * 300):
                with patch("builtins.open", mock_open()):
                    with patch("pathlib.Path.mkdir"):
                        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
                            with patch("superskills.audiobook.src.AudiobookGenerator.create_tts_provider", return_value=mock_provider):
                                with patch("superskills.audiobook.src.AudiobookGenerator.AudiobookConfig", return_value=self._create_mock_config()):
                                    generator = AudiobookGenerator()
                                    
                                    with patch.object(generator, '_generate_chapter_audio') as mock_gen:
                                        mock_gen.return_value = [ChapterAudioResult(
                                            chapter_number=1,
                                            chapter_title="Test",
                                            output_file="test.mp3",
                                            duration_seconds=60.0,
                                            word_count=100,
                                            words_per_minute=100
                                        )]
                                        
                                        # Range 2-10 should process chapters 2-3 (adjusted to available)
                                        with patch("tempfile.NamedTemporaryFile"):
                                            result = generator.generate_audiobook(
                                                "test.txt",
                                                chapter_range=(2, 10)
                                            )
                                        
                                        # Should process chapters 2 and 3
                                        assert mock_gen.call_count == 2
                                        assert result.total_chapters == 2
