"""
Logging system for the CLI.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class CLILogger:
    """
    Centralized logging for SuperSkills CLI.
    
    Logs to both console (INFO+) and file (DEBUG+) with rotation.
    """

    _instance: Optional['CLILogger'] = None
    _logger: Optional[logging.Logger] = None

    def __init__(self, log_dir: Optional[Path] = None, verbose: bool = False):
        if log_dir is None:
            log_dir = Path.home() / ".superskills" / "logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.verbose = verbose
        self._setup_logger()

    def _setup_logger(self):
        """Configure logging with file and console handlers."""
        self._logger = logging.getLogger('superskills')
        self._logger.setLevel(logging.DEBUG)

        if self._logger.handlers:
            return

        log_file = self.log_dir / "superskills.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    @classmethod
    def get_logger(cls, verbose: bool = False) -> logging.Logger:
        """
        Get or create the singleton logger instance.
        
        Args:
            verbose: If True, show DEBUG messages in console
        
        Returns:
            Logger instance
        """
        if cls._instance is None:
            cls._instance = CLILogger(verbose=verbose)
        elif verbose and not cls._instance.verbose:
            cls._instance.verbose = verbose
            for handler in cls._instance._logger.handlers:
                if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
                    handler.setLevel(logging.DEBUG)

        return cls._instance._logger

    @classmethod
    def reset(cls):
        """Reset the logger (useful for testing)."""
        if cls._instance and cls._instance._logger:
            for handler in cls._instance._logger.handlers[:]:
                handler.close()
                cls._instance._logger.removeHandler(handler)
        cls._instance = None
        cls._logger = None


def get_logger(verbose: bool = False) -> logging.Logger:
    """
    Convenience function to get the CLI logger.
    
    Args:
        verbose: If True, show DEBUG messages in console
    
    Returns:
        Logger instance
    """
    return CLILogger.get_logger(verbose=verbose)
