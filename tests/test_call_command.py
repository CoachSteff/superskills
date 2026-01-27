"""
Unit tests for call command - BUG-001 fix validation
"""
import io
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from cli.commands.call import call_command


@pytest.fixture
def mock_executor():
    """Create a mock SkillExecutor"""
    with patch('cli.commands.call.SkillExecutor') as mock_class:
        mock_instance = MagicMock()
        mock_instance.execute.return_value = {"output": "Test output from skill"}
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_config():
    """Create a mock CLIConfig"""
    with patch('cli.commands.call.CLIConfig') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


class TestCallCommandInputPriority:
    """Test input source priority: CLI arg > file > stdin"""

    def test_cli_argument_input(self, mock_executor, mock_config):
        """Test CLI argument input (BUG-001 fix)"""
        with patch('sys.stdin.isatty', return_value=False):
            result = call_command("test-skill", "CLI argument input")
            
            assert result == 0
            mock_executor.execute.assert_called_once_with(
                "test-skill", 
                "CLI argument input"
            )

    def test_file_input(self, mock_executor, mock_config, tmp_path):
        """Test file input via --input-file"""
        input_file = tmp_path / "test_input.txt"
        input_file.write_text("File input content")
        
        result = call_command(
            "test-skill", 
            input_text=None,
            input_file=str(input_file)
        )
        
        assert result == 0
        assert mock_executor.execute.call_count == 1
        call_args = mock_executor.execute.call_args
        assert call_args[0] == ("test-skill", "File input content")

    def test_stdin_piped_input(self, mock_executor, mock_config):
        """Test piped stdin input"""
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', return_value="Piped stdin content"):
            
            result = call_command("test-skill", input_text=None)
            
            assert result == 0
            mock_executor.execute.assert_called_once_with(
                "test-skill",
                "Piped stdin content"
            )

    def test_cli_arg_priority_over_stdin(self, mock_executor, mock_config):
        """Test CLI argument takes priority over stdin (BUG-001 fix core)"""
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', return_value="Stdin content"):
            
            result = call_command("test-skill", "CLI argument wins")
            
            assert result == 0
            mock_executor.execute.assert_called_once_with(
                "test-skill",
                "CLI argument wins"
            )

    def test_cli_arg_priority_over_file(self, mock_executor, mock_config, tmp_path):
        """Test CLI argument takes priority over file"""
        input_file = tmp_path / "test_input.txt"
        input_file.write_text("File content")
        
        result = call_command(
            "test-skill",
            "CLI argument wins",
            input_file=str(input_file)
        )
        
        assert result == 0
        assert mock_executor.execute.call_count == 1
        call_args = mock_executor.execute.call_args
        assert call_args[0] == ("test-skill", "CLI argument wins")

    def test_file_priority_over_stdin(self, mock_executor, mock_config, tmp_path):
        """Test file input takes priority over stdin"""
        input_file = tmp_path / "test_input.txt"
        input_file.write_text("File content wins")
        
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', return_value="Stdin content"):
            
            result = call_command(
                "test-skill",
                input_text=None,
                input_file=str(input_file)
            )
            
            assert result == 0
            assert mock_executor.execute.call_count == 1
            call_args = mock_executor.execute.call_args
            assert call_args[0] == ("test-skill", "File content wins")


class TestCallCommandErrorHandling:
    """Test error cases"""

    def test_no_input_provided_tty(self, mock_executor, mock_config, capsys):
        """Test error when no input provided in TTY environment"""
        with patch('sys.stdin.isatty', return_value=True):
            result = call_command("test-skill", input_text=None)
            
            assert result == 1
            captured = capsys.readouterr()
            assert "Error: Provide input via argument" in captured.out

    def test_no_input_provided_non_tty(self, mock_executor, mock_config, capsys):
        """Test error when no input provided in non-TTY (empty stdin)"""
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', return_value=""):
            
            result = call_command("test-skill", input_text=None)
            
            assert result == 1
            captured = capsys.readouterr()
            assert "Error: Provide input via argument" in captured.out

    def test_empty_string_input(self, mock_executor, mock_config, capsys):
        """Test error when input is empty string"""
        with patch('sys.stdin.isatty', return_value=True):
            result = call_command("test-skill", "")
            
            assert result == 1
            captured = capsys.readouterr()
            assert "Error: Provide input via argument" in captured.out

    def test_file_not_found(self, mock_executor, mock_config, capsys):
        """Test error when input file doesn't exist"""
        result = call_command(
            "test-skill",
            input_text=None,
            input_file="/nonexistent/file.txt"
        )
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Error: Input file not found" in captured.out

    def test_skill_execution_error(self, mock_executor, mock_config, capsys):
        """Test error handling during skill execution"""
        mock_executor.execute.side_effect = Exception("Execution failed")
        
        result = call_command("test-skill", "test input")
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Error executing skill" in captured.out


class TestCallCommandOutputFormats:
    """Test different output formats"""

    def test_markdown_format(self, mock_executor, mock_config):
        """Test markdown output format (default)"""
        result = call_command("test-skill", "test input", format='markdown')
        
        assert result == 0
        mock_executor.execute.assert_called_once()

    def test_json_format(self, mock_executor, mock_config):
        """Test JSON output format"""
        result = call_command("test-skill", "test input", format='json')
        
        assert result == 0
        mock_executor.execute.assert_called_once()

    def test_plain_format(self, mock_executor, mock_config, capsys):
        """Test plain output format (silent mode)"""
        result = call_command("test-skill", "test input", format='plain')
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Calling skill:" not in captured.err


class TestCallCommandOutputFile:
    """Test output file writing"""

    def test_output_to_file(self, mock_executor, mock_config, tmp_path):
        """Test writing output to file"""
        output_file = tmp_path / "output.txt"
        
        result = call_command(
            "test-skill",
            "test input",
            output_file=str(output_file)
        )
        
        assert result == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "Test output from skill" in content

    def test_output_creates_parent_dirs(self, mock_executor, mock_config, tmp_path):
        """Test output file creates parent directories"""
        output_file = tmp_path / "nested" / "dirs" / "output.txt"
        
        result = call_command(
            "test-skill",
            "test input",
            output_file=str(output_file)
        )
        
        assert result == 0
        assert output_file.exists()


class TestCallCommandNonTTYRegression:
    """Regression tests specifically for BUG-001"""

    def test_non_tty_with_cli_arg_does_not_hang(self, mock_executor, mock_config):
        """
        CRITICAL: Test that CLI argument input works in non-TTY environment
        This is the core BUG-001 fix validation
        """
        with patch('sys.stdin.isatty', return_value=False):
            result = call_command("test-skill", "Should not hang")
            
            assert result == 0
            mock_executor.execute.assert_called_once_with(
                "test-skill",
                "Should not hang"
            )

    def test_non_tty_does_not_call_stdin_read_when_arg_provided(self, mock_executor, mock_config):
        """Test that stdin.read() is never called when CLI arg is provided"""
        stdin_read_mock = Mock()
        
        with patch('sys.stdin.isatty', return_value=False), \
             patch('sys.stdin.read', stdin_read_mock):
            
            result = call_command("test-skill", "CLI arg provided")
            
            assert result == 0
            stdin_read_mock.assert_not_called()
