"""
Credential management for SuperSkills.

Loads credentials from:
1. Environment variables (highest priority - for Claude Desktop)
2. Global .env file (root of repo)
3. Per-skill .env files (skill-specific overrides)
"""
import logging
import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


def load_credentials(skill_name: Optional[str] = None, verbose: bool = False):
    """Load credentials from .env files.
    
    Args:
        skill_name: Optional skill name for per-skill .env loading
        verbose: Print loading information
    
    Priority:
        1. Environment variables (Claude Desktop sets these)
        2. Global .env (root of repo)
        3. Per-skill .env (superskills/{skill_name}/.env)
    """
    if not DOTENV_AVAILABLE:
        if verbose:
            logger.warning("python-dotenv not installed. Using environment variables only.")
            logger.info("Install with: pip install python-dotenv")
        return

    # Find repo root (where .env should be)
    current = Path(__file__).parent
    repo_root = current.parent.parent

    # Load global .env if it exists
    global_env = repo_root / ".env"
    if global_env.exists():
        load_dotenv(global_env, override=False)  # Don't override env vars
        if verbose:
            logger.info(f"Loaded global credentials from {global_env}")
    elif verbose:
        logger.info(f"No global .env found at {global_env}")

    # Load per-skill .env if skill_name provided
    if skill_name:
        skill_env = repo_root / "superskills" / skill_name / ".env"
        if skill_env.exists():
            load_dotenv(skill_env, override=True)  # Override global with skill-specific
            if verbose:
                logger.info(f"Loaded {skill_name} credentials from {skill_env}")
        elif verbose:
            logger.info(f"No skill-specific .env found at {skill_env}")


def get_credential(
    key: str,
    default: Optional[str] = None,
    required: bool = True
) -> Optional[str]:
    """Get credential with helpful error message.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: If True, raise error when not found and no default
        
    Returns:
        Credential value or default
        
    Raises:
        ValueError: If credential not found, no default, and required=True
    """
    value = os.getenv(key, default)

    if value is None and required:
        error_msg = (
            f"\n{'='*60}\n"
            f"❌ CREDENTIAL NOT FOUND: {key}\n"
            f"{'='*60}\n\n"
            f"Please set it in one of the following ways:\n\n"
            f"1. Global .env file (recommended):\n"
            f"   cp .env.template .env\n"
            f"   # Edit .env and add: {key}=your_value_here\n\n"
            f"2. Per-skill .env file:\n"
            f"   # Create superskills/{{skill_name}}/.env\n\n"
            f"3. Environment variable:\n"
            f"   export {key}=your_value_here\n\n"
            f"4. Claude Desktop settings:\n"
            f"   Claude Desktop → Settings → Environment Variables\n\n"
            f"📖 See docs/CREDENTIAL_SETUP.md for detailed setup instructions.\n"
            f"{'='*60}\n"
        )
        raise ValueError(error_msg)

    return value


def check_credentials(required_keys: list[str]) -> dict[str, bool]:
    """Check which credentials are set.
    
    Args:
        required_keys: List of environment variable names to check
        
    Returns:
        Dict mapping key names to whether they're set (True/False)
    """
    return {key: os.getenv(key) is not None for key in required_keys}


def get_credential_status(required_keys: list[str]) -> str:
    """Get a formatted status message for credentials.
    
    Args:
        required_keys: List of environment variable names to check
        
    Returns:
        Formatted status string
    """
    status = check_credentials(required_keys)
    lines = ["Credential Status:", "-" * 50]

    for key, is_set in status.items():
        symbol = "✓" if is_set else "✗"
        value = os.getenv(key, "")
        masked = value[:8] + "..." if len(value) > 8 else "***" if is_set else "NOT SET"
        lines.append(f"{symbol} {key:30} {masked}")

    found = sum(status.values())
    total = len(required_keys)
    lines.append("-" * 50)
    lines.append(f"Found {found}/{total} required credentials")

    if found < total:
        lines.append("\n⚠️ Some credentials are missing!")
        lines.append("Run: cp .env.template .env")
        lines.append("Then edit .env and add your API keys.")

    return "\n".join(lines)
