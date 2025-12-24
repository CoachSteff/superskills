"""Unit tests for SocialMediaPublisher."""
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "superskills" / "marketer" / "src"))
from SocialMediaPublisher import Platform, SocialMediaPublisher


class TestSocialMediaPublisherInit:
    """Test SocialMediaPublisher initialization."""

    def test_init_with_env_vars(self, mock_env_vars):
        """Test initialization with environment variables."""
        publisher = SocialMediaPublisher()
        assert publisher.api_key == "test_postiz_key"
        assert publisher.workspace_id == "test_workspace"
        assert publisher.base_url == "https://api.postiz.com/v1"

    def test_init_missing_api_key(self, monkeypatch):
        """Test error when API key is missing."""
        monkeypatch.delenv("POSTIZ_API_KEY", raising=False)
        with pytest.raises(ValueError, match="POSTIZ_API_KEY"):
            SocialMediaPublisher()

    def test_init_missing_workspace_id(self, monkeypatch, mock_env_vars):
        """Test error when workspace ID is missing."""
        monkeypatch.delenv("POSTIZ_WORKSPACE_ID", raising=False)
        with pytest.raises(ValueError, match="POSTIZ_WORKSPACE_ID"):
            SocialMediaPublisher()


class TestCharacterLimits:
    """Test character limits."""

    def test_char_limits_defined(self):
        """Test that all platform limits are defined."""
        limits = SocialMediaPublisher.CHAR_LIMITS
        assert limits[Platform.TWITTER] == 280
        assert limits[Platform.LINKEDIN] == 3000
        assert limits[Platform.INSTAGRAM] == 2200
        assert limits[Platform.FACEBOOK] == 63206


class TestContentOptimization:
    """Test content optimization for platforms."""

    def test_optimize_within_limit(self, mock_env_vars):
        """Test content that fits within limit."""
        publisher = SocialMediaPublisher()
        content = "Short post"

        optimized = publisher.optimize_for_platform(content, Platform.TWITTER)
        assert optimized == content

    def test_optimize_exceeds_limit(self, mock_env_vars):
        """Test content truncation when exceeding limit."""
        publisher = SocialMediaPublisher()
        content = "A" * 300  # Exceeds Twitter limit of 280

        optimized = publisher.optimize_for_platform(content, Platform.TWITTER)
        assert len(optimized) <= 280
        assert optimized.endswith("...")

    def test_optimize_with_custom_limit(self, mock_env_vars):
        """Test optimization with custom max length."""
        publisher = SocialMediaPublisher()
        content = "A" * 100

        optimized = publisher.optimize_for_platform(content, Platform.TWITTER, max_length=50)
        assert len(optimized) <= 50
        assert optimized.endswith("...")


class TestHashtagExtraction:
    """Test hashtag extraction."""

    def test_extract_hashtags(self, mock_env_vars):
        """Test extracting hashtags from text."""
        publisher = SocialMediaPublisher()
        text = "Great post about #AI and #Productivity! #Superworker"

        hashtags = publisher.extract_hashtags(text)
        assert hashtags == ["AI", "Productivity", "Superworker"]

    def test_extract_no_hashtags(self, mock_env_vars):
        """Test text without hashtags."""
        publisher = SocialMediaPublisher()
        text = "No hashtags here"

        hashtags = publisher.extract_hashtags(text)
        assert hashtags == []


class TestHashtagFormatting:
    """Test hashtag formatting per platform."""

    def test_format_hashtags_twitter(self, mock_env_vars):
        """Test Twitter hashtag formatting."""
        publisher = SocialMediaPublisher()
        hashtags = ["AI", "Productivity", "Superworker"]

        formatted = publisher.format_hashtags(hashtags, Platform.TWITTER)
        assert formatted == "#AI #Productivity #Superworker"

    def test_format_hashtags_linkedin(self, mock_env_vars):
        """Test LinkedIn hashtag formatting (end of post)."""
        publisher = SocialMediaPublisher()
        hashtags = ["AI", "Productivity"]

        formatted = publisher.format_hashtags(hashtags, Platform.LINKEDIN)
        assert formatted.startswith("\n\n")
        assert "#AI #Productivity" in formatted

    def test_format_hashtags_instagram(self, mock_env_vars):
        """Test Instagram hashtag formatting."""
        publisher = SocialMediaPublisher()
        hashtags = ["AI", "Productivity"]

        formatted = publisher.format_hashtags(hashtags, Platform.INSTAGRAM)
        assert formatted.startswith("\n\n")
        assert "#AI #Productivity" in formatted

    def test_format_hashtags_max_limit(self, mock_env_vars):
        """Test hashtag limiting."""
        publisher = SocialMediaPublisher()
        hashtags = ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5", "Tag6", "Tag7"]

        formatted = publisher.format_hashtags(hashtags, Platform.TWITTER, max_tags=3)
        assert formatted == "#Tag1 #Tag2 #Tag3"


class TestOptimalTiming:
    """Test optimal posting time calculation."""

    def test_get_optimal_time_linkedin(self, mock_env_vars):
        """Test LinkedIn optimal time."""
        publisher = SocialMediaPublisher()

        optimal_time = publisher.get_optimal_time(Platform.LINKEDIN, days_ahead=1)
        assert isinstance(optimal_time, datetime)
        assert optimal_time.hour == 10  # First optimal time for LinkedIn

    def test_get_optimal_time_twitter(self, mock_env_vars):
        """Test Twitter optimal time."""
        publisher = SocialMediaPublisher()

        optimal_time = publisher.get_optimal_time(Platform.TWITTER, days_ahead=1)
        assert isinstance(optimal_time, datetime)
        assert optimal_time.hour == 9  # First optimal time for Twitter

    def test_get_optimal_time_future(self, mock_env_vars):
        """Test optimal time in future."""
        publisher = SocialMediaPublisher()

        now = datetime.now()
        optimal_time = publisher.get_optimal_time(Platform.LINKEDIN, days_ahead=2)

        assert optimal_time > now
        assert (optimal_time - now).days >= 1


class TestPostPreview:
    """Test post preview functionality."""

    def test_preview_post_basic(self, mock_env_vars):
        """Test basic post preview."""
        publisher = SocialMediaPublisher()
        content = "Test post about AI"

        preview = publisher.preview_post(content, Platform.LINKEDIN)

        assert preview["platform"] == "linkedin"
        assert preview["content"] == content
        assert preview["character_count"] == len(content)
        assert preview["character_limit"] == 3000
        assert preview["within_limit"] == True

    def test_preview_post_with_hashtags(self, mock_env_vars):
        """Test preview with hashtags."""
        publisher = SocialMediaPublisher()
        content = "Test post"
        hashtags = ["AI", "Productivity"]

        preview = publisher.preview_post(content, Platform.LINKEDIN, hashtags=hashtags)

        assert "#AI" in preview["content"]
        assert "#Productivity" in preview["content"]

    def test_preview_post_exceeds_limit(self, mock_env_vars):
        """Test preview when content exceeds limit."""
        publisher = SocialMediaPublisher()
        content = "A" * 300  # Exceeds Twitter limit

        preview = publisher.preview_post(content, Platform.TWITTER)

        assert preview["within_limit"] == False
        assert preview["character_count"] > preview["character_limit"]

    def test_preview_includes_optimal_time(self, mock_env_vars):
        """Test that preview includes optimal posting time."""
        publisher = SocialMediaPublisher()
        content = "Test post"

        preview = publisher.preview_post(content, Platform.LINKEDIN)

        assert "optimal_time" in preview
        assert isinstance(preview["optimal_time"], str)


class TestPostingMocked:
    """Test posting with mocked API calls."""

    @patch('SocialMediaPublisher.requests.post')
    def test_post_single_platform_success(self, mock_post, mock_env_vars, mock_requests_response):
        """Test successful post to single platform."""
        mock_post.return_value = mock_requests_response

        publisher = SocialMediaPublisher()
        results = publisher.post(
            content="Test post",
            platforms=[Platform.LINKEDIN]
        )

        assert len(results) == 1
        assert results[0].platform == "linkedin"
        assert results[0].status == "published"
        mock_post.assert_called_once()

    @patch('SocialMediaPublisher.requests.post')
    def test_post_multiple_platforms(self, mock_post, mock_env_vars, mock_requests_response):
        """Test posting to multiple platforms."""
        mock_post.return_value = mock_requests_response

        publisher = SocialMediaPublisher()
        results = publisher.post(
            content="Test post",
            platforms=[Platform.LINKEDIN, Platform.TWITTER, Platform.INSTAGRAM]
        )

        assert len(results) == 3
        assert mock_post.call_count == 3

    @patch('SocialMediaPublisher.requests.post')
    def test_post_with_hashtags(self, mock_post, mock_env_vars, mock_requests_response):
        """Test posting with hashtags."""
        mock_post.return_value = mock_requests_response

        publisher = SocialMediaPublisher()
        results = publisher.post(
            content="Test post",
            platforms=[Platform.LINKEDIN],
            hashtags=["AI", "Productivity"]
        )

        # Check that the posted content includes hashtags
        call_args = mock_post.call_args
        posted_content = call_args[1]["json"]["content"]
        assert "#AI" in posted_content
        assert "#Productivity" in posted_content

    @patch('SocialMediaPublisher.requests.post')
    def test_post_scheduled(self, mock_post, mock_env_vars, mock_requests_response):
        """Test scheduling a post."""
        mock_post.return_value = mock_requests_response

        publisher = SocialMediaPublisher()
        schedule_time = datetime.now() + timedelta(hours=2)

        results = publisher.post(
            content="Test post",
            platforms=[Platform.LINKEDIN],
            schedule_time=schedule_time
        )

        assert results[0].status == "scheduled"
        assert results[0].scheduled_time is not None

    @patch('SocialMediaPublisher.requests.post')
    def test_post_api_failure(self, mock_post, mock_env_vars):
        """Test handling of API failure."""
        # Mock API failure
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response

        publisher = SocialMediaPublisher()
        results = publisher.post(
            content="Test post",
            platforms=[Platform.LINKEDIN]
        )

        assert len(results) == 1
        assert "failed" in results[0].status
