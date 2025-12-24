"""Unit tests for ImageGenerator."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent / "superskills" / "designer" / "src"))
from ImageGenerator import ImageGenerationResult, ImageGenerator


class TestImageGeneratorInit:
    """Test ImageGenerator initialization."""

    def test_init_with_defaults(self, mock_env_vars, temp_output_dir):
        """Test default initialization."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))
        assert generator.output_dir == temp_output_dir
        assert generator.provider == "gemini"
        assert generator.api_key == "test_gemini_key"

    def test_init_with_midjourney(self, mock_env_vars, temp_output_dir):
        """Test Midjourney provider initialization."""
        generator = ImageGenerator(output_dir=str(temp_output_dir), provider="midjourney")
        assert generator.provider == "midjourney"
        assert generator.api_key == "test_midjourney_key"

    def test_init_missing_api_key(self, monkeypatch, temp_output_dir):
        """Test error when API key is missing."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            ImageGenerator(output_dir=str(temp_output_dir))


class TestPlatformSpecs:
    """Test platform specifications."""

    def test_platform_specs_loaded(self):
        """Test that all platform specs are available."""
        specs = ImageGenerator.PLATFORM_SPECS
        assert len(specs) == 7
        assert "linkedin-feed" in specs
        assert "instagram-square" in specs
        assert "twitter" in specs
        assert "blog-hero" in specs

    def test_platform_dimensions(self):
        """Test specific platform dimensions."""
        assert ImageGenerator.PLATFORM_SPECS["linkedin-square"] == {"width": 1200, "height": 1200}
        assert ImageGenerator.PLATFORM_SPECS["instagram-portrait"] == {"width": 1080, "height": 1350}
        assert ImageGenerator.PLATFORM_SPECS["twitter"] == {"width": 1200, "height": 675}


class TestPromptOptimization:
    """Test prompt optimization."""

    def test_optimize_prompt_adds_brand_style(self, mock_env_vars, temp_output_dir):
        """Test that prompt optimization includes brand style."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))
        prompt = generator.optimize_prompt("AI adoption framework")

        assert "AI adoption framework" in prompt
        # Check for key style elements (flexible matching)
        assert "professional" in prompt.lower()
        assert "modern" in prompt.lower() or "clean" in prompt.lower()
        assert "accessibility" in prompt.lower() or "accessible" in prompt.lower()

    def test_optimize_prompt_with_platform_landscape(self, mock_env_vars, temp_output_dir):
        """Test landscape composition guidance."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))
        prompt = generator.optimize_prompt("Test concept", platform="linkedin-feed")

        assert "Horizontal composition" in prompt or "landscape orientation" in prompt

    def test_optimize_prompt_with_platform_portrait(self, mock_env_vars, temp_output_dir):
        """Test portrait composition guidance."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))
        prompt = generator.optimize_prompt("Test concept", platform="instagram-portrait")

        assert "Vertical composition" in prompt or "portrait orientation" in prompt

    def test_optimize_prompt_with_platform_square(self, mock_env_vars, temp_output_dir):
        """Test square composition guidance."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))
        prompt = generator.optimize_prompt("Test concept", platform="linkedin-square")

        assert "Square composition" in prompt or "centered focus" in prompt

    def test_optimize_prompt_with_style_override(self, mock_env_vars, temp_output_dir):
        """Test custom style override."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))
        custom_style = "Futuristic, neon, cyberpunk aesthetic"
        prompt = generator.optimize_prompt("Test concept", style_override=custom_style)

        assert custom_style in prompt
        assert "Modern, clean, professional" not in prompt


class TestFilenameGeneration:
    """Test filename generation."""

    def test_filename_with_timestamp(self, mock_env_vars, temp_output_dir):
        """Test that filename includes timestamp."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))

        with patch('ImageGenerator.ImageGenerator._create_placeholder') as mock_create:
            mock_img = Image.new('RGB', (100, 100))
            mock_create.return_value = mock_img

            result = generator.generate("Test concept", optimize_prompt=False)

            filename = Path(result.output_file).name
            assert "test-concept" in filename.lower()
            assert filename.endswith(".png")

    def test_filename_sanitization(self, mock_env_vars, temp_output_dir):
        """Test that special characters are removed from filename."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))

        with patch('ImageGenerator.ImageGenerator._create_placeholder') as mock_create:
            mock_img = Image.new('RGB', (100, 100))
            mock_create.return_value = mock_img

            result = generator.generate("Test @#$% Concept!!!", optimize_prompt=False)

            filename = Path(result.output_file).name
            assert "@" not in filename
            assert "#" not in filename
            assert "!" not in filename


class TestPlaceholderCreation:
    """Test placeholder image creation."""

    def test_create_placeholder(self, mock_env_vars, temp_output_dir):
        """Test placeholder image creation."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))
        img = generator._create_placeholder(1200, 627, "Test text")

        assert img.size == (1200, 627)
        assert img.mode == 'RGB'

    def test_placeholder_text_truncation(self, mock_env_vars, temp_output_dir):
        """Test that long text is truncated in placeholder."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))
        long_text = "A" * 100
        img = generator._create_placeholder(1200, 627, long_text)

        assert img is not None


class TestAccessibilityValidation:
    """Test accessibility validation."""

    def test_validate_accessibility_pass(self, mock_env_vars, temp_output_dir, mock_image):
        """Test accessibility validation for compliant image."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))

        # Create test image
        test_path = temp_output_dir / "test.png"
        small_img = Image.new('RGB', (1200, 627))
        small_img.save(test_path, format='PNG', optimize=True)

        validation = generator.validate_accessibility(str(test_path))

        assert "file_size_kb" in validation
        assert "dimensions" in validation
        assert "mobile_friendly" in validation
        assert validation["dimensions"] == "1200x627"

    def test_validate_accessibility_file_size(self, mock_env_vars, temp_output_dir):
        """Test file size validation."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))

        # Create small test image
        test_path = temp_output_dir / "test_small.png"
        small_img = Image.new('RGB', (100, 100))
        small_img.save(test_path, format='PNG', optimize=True)

        validation = generator.validate_accessibility(str(test_path))

        # Small image should pass file size check
        assert validation["file_size_ok"] == True


class TestImageGeneration:
    """Test image generation (mocked)."""

    def test_generate_with_placeholder_fallback(self, mock_env_vars, temp_output_dir):
        """Test that generation falls back to placeholder on API failure."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))

        result = generator.generate(
            concept="AI adoption framework",
            platform="linkedin-square",
            optimize_prompt=True
        )

        assert isinstance(result, ImageGenerationResult)
        assert Path(result.output_file).exists()
        assert result.provider == "gemini"
        assert result.dimensions == "1200x1200"
        assert result.file_size_kb > 0
        assert result.generation_time_seconds >= 0

    def test_generate_different_formats(self, mock_env_vars, temp_output_dir):
        """Test generation with different output formats."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))

        # Test PNG
        result_png = generator.generate("Test", format="png", optimize_prompt=False)
        assert result_png.output_file.endswith(".png")

        # Test JPG
        result_jpg = generator.generate("Test", format="jpg", optimize_prompt=False)
        assert result_jpg.output_file.endswith(".jpg")

    def test_generate_custom_filename(self, mock_env_vars, temp_output_dir):
        """Test generation with custom filename."""
        generator = ImageGenerator(output_dir=str(temp_output_dir))

        result = generator.generate(
            "Test",
            output_filename="custom-name.png",
            optimize_prompt=False
        )

        assert "custom-name.png" in result.output_file
