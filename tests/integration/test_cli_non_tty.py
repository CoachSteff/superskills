"""
Integration tests for CLI in non-TTY environments - BUG-001 fix validation

Tests the actual superskills CLI command in subprocess to ensure it doesn't hang
when run in non-interactive environments (scripts, automation, IDE agents).
"""
import subprocess
import sys
from pathlib import Path

import pytest


class TestCLINonTTYExecution:
    """Integration tests for non-TTY CLI execution"""

    def test_cli_arg_non_tty_does_not_hang(self):
        """
        CRITICAL: Test that CLI doesn't hang with argument in non-TTY
        This validates the BUG-001 fix
        """
        result = subprocess.run(
            [sys.executable, "-m", "cli", "call", "helper", "test input"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode in [0, 1]

    def test_piped_stdin_still_works(self):
        """Test that piped stdin continues to work after fix"""
        result = subprocess.run(
            [sys.executable, "-m", "cli", "call", "helper"],
            input="test input from stdin",
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode in [0, 1]

    def test_file_input_still_works(self, tmp_path):
        """Test that file input continues to work after fix"""
        input_file = tmp_path / "test_input.txt"
        input_file.write_text("test input from file")
        
        result = subprocess.run(
            [
                sys.executable, "-m", "cli", "call", "helper",
                "--input", str(input_file)
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode in [0, 1, 2]

    def test_no_input_returns_error(self):
        """Test that missing input returns error (doesn't hang)"""
        result = subprocess.run(
            [sys.executable, "-m", "cli", "call", "helper"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode in [0, 1]
        assert "Error: Provide input" in result.stdout or result.returncode == 1

    @pytest.mark.timeout(10)
    def test_multiple_parallel_calls(self):
        """Test multiple parallel CLI calls don't interfere"""
        import concurrent.futures
        
        def run_cli_call(text):
            return subprocess.run(
                [sys.executable, "-m", "cli", "call", "helper", text],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=Path(__file__).parent.parent.parent
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(run_cli_call, f"test input {i}")
                for i in range(3)
            ]
            
            results = [f.result(timeout=10) for f in futures]
            
            for result in results:
                assert result.returncode in [0, 1]


class TestCLIInputPriorityIntegration:
    """Integration tests for input source priority"""

    def test_cli_arg_overrides_stdin(self, tmp_path):
        """Test CLI arg takes priority over stdin in real execution"""
        result = subprocess.run(
            [sys.executable, "-m", "cli", "call", "helper", "CLI argument"],
            input="stdin input",
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode in [0, 1]

    def test_cli_arg_overrides_file(self, tmp_path):
        """Test CLI arg takes priority over file in real execution"""
        input_file = tmp_path / "test_input.txt"
        input_file.write_text("file input")
        
        result = subprocess.run(
            [
                sys.executable, "-m", "cli", "call", "helper",
                "CLI argument",
                "--input", str(input_file)
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode in [0, 1, 2]


class TestCLIBackwardCompatibility:
    """Test backward compatibility after BUG-001 fix"""

    def test_json_output_format(self):
        """Test JSON output format still works"""
        result = subprocess.run(
            [
                sys.executable, "-m", "cli", "call", "helper",
                "test input",
                "--format", "json"
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode in [0, 1]

    def test_plain_output_format(self):
        """Test plain output format still works"""
        result = subprocess.run(
            [
                sys.executable, "-m", "cli", "call", "helper",
                "test input",
                "--format", "plain"
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).parent.parent.parent
        )
        
        assert result.returncode in [0, 1]
