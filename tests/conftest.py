"""Pytest configuration and shared fixtures."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from dotenv import load_dotenv

# Add superskills directory to path
superskills_dir = Path(__file__).parent.parent / "superskills"
sys.path.insert(0, str(superskills_dir))

# Load test environment variables
load_dotenv(Path(__file__).parent / ".env.test")


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    env_vars = {
        "GEMINI_API_KEY": "test_gemini_key",
        "MIDJOURNEY_API_KEY": "test_midjourney_key",
        "POSTIZ_API_KEY": "test_postiz_key",
        "POSTIZ_WORKSPACE_ID": "test_workspace",
        "ELEVENLABS_API_KEY": "test_elevenlabs_key",
        "ELEVENLABS_VOICE_ID": "test_voice_id",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for tests."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_image():
    """Create a mock PIL Image."""
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    return img


@pytest.fixture
def mock_requests_response():
    """Create a mock requests response."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "test_123", "status": "success"}
    return mock_response


@pytest.fixture
def mock_elevenlabs_client():
    """Create a mock ElevenLabs client."""
    mock_client = MagicMock()
    mock_audio = b"fake_audio_data"
    mock_client.generate.return_value = iter([mock_audio])
    return mock_client


@pytest.fixture
def sample_script():
    """Sample script for narrator testing."""
    return """
    Welcome to the Superworker Framework!
    
    Today we'll cover three key concepts:
    1. AI-Native Mindset
    2. Workflow Automation
    3. Continuous Learning
    
    Let's dive in!
    """


@pytest.fixture
def sample_social_content():
    """Sample social media content."""
    return {
        "text": "Exciting news: New AI course launching next month! Learn how to build AI-native workflows that 10x your productivity.",
        "hashtags": ["AIProductivity", "Superworker", "AILeadership"],
        "link": "https://coachsteff.com/ai-course"
    }
