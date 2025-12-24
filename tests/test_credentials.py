"""
Unit tests for credential management system.

Tests verify:
- Credential loading from .env files
- Priority hierarchy (ENV VAR > skill .env > global .env)
- Error handling for missing/malformed files
- Sensitive data masking in logs
- Graceful degradation when python-dotenv unavailable
"""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from superskills.core.credentials import (
    check_credentials,
    get_credential,
    get_credential_status,
    load_credentials,
)


@pytest.fixture
def temp_repo_structure():
    """Create temporary repo structure with .env files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        superskills_dir = repo_root / "superskills"
        superskills_dir.mkdir()

        core_dir = superskills_dir / "core"
        core_dir.mkdir()

        yield {
            'root': repo_root,
            'superskills': superskills_dir,
            'core': core_dir
        }


@pytest.fixture
def clean_env():
    """Clean environment variables before and after test."""
    original_env = os.environ.copy()

    test_keys = [
        'TEST_GLOBAL_KEY',
        'TEST_SKILL_KEY',
        'TEST_OVERRIDE_KEY',
        'TEST_REQUIRED_KEY',
        'TEST_API_KEY',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY'
    ]

    for key in test_keys:
        os.environ.pop(key, None)

    yield

    os.environ.clear()
    os.environ.update(original_env)


class TestLoadCredentials:
    """Test credential loading functionality."""

    def test_load_credentials_no_dotenv_available(self, clean_env, caplog):
        """Test graceful handling when python-dotenv not available."""
        with caplog.at_level('WARNING'):
            with patch('superskills.core.credentials.DOTENV_AVAILABLE', False):
                load_credentials(verbose=True)

                assert 'python-dotenv not installed' in caplog.text

    def test_load_credentials_no_skill_name(self, clean_env, temp_repo_structure):
        """Test loading credentials without skill name (global only)."""
        repo_root = temp_repo_structure['root']

        global_env = repo_root / ".env"
        global_env.write_text("TEST_GLOBAL_KEY=global_value\n")

        with patch('superskills.core.credentials.Path') as mock_path:
            mock_path(__file__).parent.parent.parent = repo_root

            with patch('superskills.core.credentials.load_dotenv') as mock_load:
                load_credentials()

                mock_load.assert_called_once()
                call_args = mock_load.call_args
                assert str(call_args[0][0]).endswith('.env')
                assert not call_args[1]['override']

    def test_load_credentials_with_skill_name(self, clean_env, temp_repo_structure):
        """Test loading credentials with skill name (global + skill)."""
        repo_root = temp_repo_structure['root']

        global_env = repo_root / ".env"
        global_env.write_text("TEST_GLOBAL_KEY=global_value\n")

        skill_dir = repo_root / "superskills" / "test-skill"
        skill_dir.mkdir(parents=True)
        skill_env = skill_dir / ".env"
        skill_env.write_text("TEST_SKILL_KEY=skill_value\n")

        with patch('superskills.core.credentials.Path') as mock_path:
            mock_path(__file__).parent.parent.parent = repo_root

            with patch('superskills.core.credentials.load_dotenv') as mock_load:
                load_credentials(skill_name='test-skill')

                assert mock_load.call_count == 2

                first_call = mock_load.call_args_list[0]
                assert str(first_call[0][0]).endswith('.env')
                assert not first_call[1]['override']

                second_call = mock_load.call_args_list[1]
                assert 'test-skill' in str(second_call[0][0])
                assert second_call[1]['override']

    def test_load_credentials_skill_override_priority(self, clean_env):
        """Test that skill .env overrides global .env."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            global_env = repo_root / ".env"
            global_env.write_text("TEST_OVERRIDE_KEY=global_value\n")

            skill_dir = repo_root / "superskills" / "test-skill"
            skill_dir.mkdir(parents=True)
            skill_env = skill_dir / ".env"
            skill_env.write_text("TEST_OVERRIDE_KEY=skill_value\n")

            with patch('superskills.core.credentials.Path') as mock_path:
                mock_path(__file__).parent.parent.parent = repo_root

                load_credentials(skill_name='test-skill')

                assert os.getenv('TEST_OVERRIDE_KEY') == 'skill_value'

    def test_load_credentials_file_not_found(self, clean_env, caplog):
        """Test graceful handling when .env files don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            superskills_dir = repo_root / "superskills"
            superskills_dir.mkdir()

            with caplog.at_level('INFO'):
                with patch('superskills.core.credentials.Path') as mock_path:
                    mock_path(__file__).parent.parent.parent = repo_root

                    load_credentials(skill_name='nonexistent-skill', verbose=True)

                    assert 'No global .env found' in caplog.text
                    assert 'No skill-specific .env found' in caplog.text

    def test_load_credentials_verbose_mode(self, clean_env, caplog):
        """Test verbose output when verbose=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            global_env = repo_root / ".env"
            global_env.write_text("TEST_KEY=value\n")

            skill_dir = repo_root / "superskills" / "test-skill"
            skill_dir.mkdir(parents=True)
            skill_env = skill_dir / ".env"
            skill_env.write_text("TEST_SKILL_KEY=skill_value\n")

            with caplog.at_level('INFO'):
                with patch('superskills.core.credentials.Path') as mock_path:
                    mock_path(__file__).parent.parent.parent = repo_root

                    load_credentials(skill_name='test-skill', verbose=True)

                    assert 'Loaded global credentials' in caplog.text
                    assert 'Loaded test-skill credentials' in caplog.text

    def test_load_credentials_environment_variable_priority(self, clean_env):
        """Test that environment variables take precedence over .env files."""
        os.environ['TEST_ENV_PRIORITY'] = 'env_var_value'

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            global_env = repo_root / ".env"
            global_env.write_text("TEST_ENV_PRIORITY=global_value\n")

            with patch('superskills.core.credentials.Path') as mock_path:
                mock_path(__file__).parent.parent.parent = repo_root

                load_credentials()

                assert os.getenv('TEST_ENV_PRIORITY') == 'env_var_value'


class TestGetCredential:
    """Test get_credential functionality."""

    def test_get_credential_exists(self, clean_env):
        """Test getting an existing credential."""
        os.environ['TEST_API_KEY'] = 'test_value_123'

        result = get_credential('TEST_API_KEY')

        assert result == 'test_value_123'

    def test_get_credential_with_default(self, clean_env):
        """Test getting credential with default value."""
        result = get_credential('NONEXISTENT_KEY', default='default_value', required=False)

        assert result == 'default_value'

    def test_get_credential_required_missing(self, clean_env):
        """Test that required credential raises error when missing."""
        with pytest.raises(ValueError) as exc_info:
            get_credential('REQUIRED_MISSING_KEY', required=True)

        error_msg = str(exc_info.value)
        assert 'CREDENTIAL NOT FOUND' in error_msg
        assert 'REQUIRED_MISSING_KEY' in error_msg
        assert 'Global .env file' in error_msg
        assert 'Environment variable' in error_msg
        assert 'Claude Desktop' in error_msg

    def test_get_credential_not_required_missing(self, clean_env):
        """Test that non-required credential returns None when missing."""
        result = get_credential('OPTIONAL_KEY', required=False)

        assert result is None


class TestCheckCredentials:
    """Test check_credentials functionality."""

    def test_check_credentials_all_present(self, clean_env):
        """Test checking credentials when all are present."""
        os.environ['KEY1'] = 'value1'
        os.environ['KEY2'] = 'value2'
        os.environ['KEY3'] = 'value3'

        result = check_credentials(['KEY1', 'KEY2', 'KEY3'])

        assert result == {
            'KEY1': True,
            'KEY2': True,
            'KEY3': True
        }

    def test_check_credentials_partial(self, clean_env):
        """Test checking credentials when some are missing."""
        os.environ['KEY1'] = 'value1'

        result = check_credentials(['KEY1', 'KEY2', 'KEY3'])

        assert result == {
            'KEY1': True,
            'KEY2': False,
            'KEY3': False
        }

    def test_check_credentials_none_present(self, clean_env):
        """Test checking credentials when none are present."""
        result = check_credentials(['KEY1', 'KEY2'])

        assert result == {
            'KEY1': False,
            'KEY2': False
        }


class TestGetCredentialStatus:
    """Test get_credential_status functionality."""

    def test_credential_status_all_present(self, clean_env):
        """Test credential status when all are present."""
        os.environ['API_KEY_1'] = 'sk-1234567890abcdef'
        os.environ['API_KEY_2'] = 'key-9876543210'

        status = get_credential_status(['API_KEY_1', 'API_KEY_2'])

        assert 'Credential Status:' in status
        assert '✓ API_KEY_1' in status
        assert '✓ API_KEY_2' in status
        assert 'Found 2/2 required credentials' in status
        assert '⚠️' not in status

    def test_credential_status_partial(self, clean_env):
        """Test credential status when some are missing."""
        os.environ['API_KEY_1'] = 'sk-1234567890'

        status = get_credential_status(['API_KEY_1', 'API_KEY_2', 'API_KEY_3'])

        assert '✓ API_KEY_1' in status
        assert '✗ API_KEY_2' in status
        assert '✗ API_KEY_3' in status
        assert 'Found 1/3 required credentials' in status
        assert '⚠️ Some credentials are missing!' in status
        assert 'cp .env.template .env' in status

    def test_credential_status_masking(self, clean_env):
        """Test that API keys are masked in status output."""
        os.environ['LONG_API_KEY'] = 'sk-1234567890abcdefghijklmnop'
        os.environ['SHORT_KEY'] = 'abc'

        status = get_credential_status(['LONG_API_KEY', 'SHORT_KEY'])

        assert 'sk-12345...' in status
        assert '***' in status

        assert 'sk-1234567890abcdefghijklmnop' not in status
        assert 'abc' not in status

    def test_sensitive_data_not_logged(self, clean_env, caplog):
        """Test that API keys are not logged in verbose mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            global_env = repo_root / ".env"
            global_env.write_text("OPENAI_API_KEY=sk-secret123456789\nANTHROPIC_API_KEY=sk-ant-secret999\n")

            with caplog.at_level('INFO'):
                with patch('superskills.core.credentials.Path') as mock_path:
                    mock_path(__file__).parent.parent.parent = repo_root

                    load_credentials(verbose=True)

                    log_output = caplog.text

                    assert 'sk-secret123456789' not in log_output
                    assert 'sk-ant-secret999' not in log_output

                    assert 'Loaded global credentials' in log_output


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_env_file(self, clean_env):
        """Test loading empty .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            global_env = repo_root / ".env"
            global_env.write_text("")

            with patch('superskills.core.credentials.Path') as mock_path:
                mock_path(__file__).parent.parent.parent = repo_root

                load_credentials()

    def test_malformed_env_file(self, clean_env):
        """Test handling of malformed .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)

            global_env = repo_root / ".env"
            global_env.write_text("INVALID LINE WITHOUT EQUALS\nVALID_KEY=value\n")

            with patch('superskills.core.credentials.Path') as mock_path:
                mock_path(__file__).parent.parent.parent = repo_root

                load_credentials()

    def test_credential_with_special_characters(self, clean_env):
        """Test credentials with special characters."""
        os.environ['SPECIAL_KEY'] = 'value-with-dashes_and_underscores@symbols#123'

        result = get_credential('SPECIAL_KEY')

        assert result == 'value-with-dashes_and_underscores@symbols#123'

    def test_credential_with_whitespace(self, clean_env):
        """Test credentials with leading/trailing whitespace."""
        os.environ['WHITESPACE_KEY'] = '  value_with_spaces  '

        result = get_credential('WHITESPACE_KEY')

        assert result == '  value_with_spaces  '


def main():
    """Run tests manually."""
    print("="*60)
    print("Credential Management Tests")
    print("="*60 + "\n")

    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    main()
