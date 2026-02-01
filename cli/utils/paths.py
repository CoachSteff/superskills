"""
Path resolution utilities for the CLI.
"""
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """
    Find the project root directory by looking for anchor files.

    Tries multiple strategies:
    1. Look for pyproject.toml (most reliable)
    2. Look for .git directory
    3. Fallback to relative path from package location

    Returns:
        Path object pointing to project root
    """
    current = Path(__file__).resolve()

    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent

        if (parent / ".git").exists():
            return parent

    fallback = Path(__file__).parent.parent.parent.parent
    return fallback.resolve()


def get_workflows_dir(subdirectory: Optional[str] = None) -> Path:
    """
    Get the workflows directory path.

    Args:
        subdirectory: Optional subdirectory name ('definitions' or 'custom')

    Returns:
        Path to workflows directory or subdirectory
    """
    root = get_project_root()
    workflows = root / "workflows"

    if subdirectory:
        return workflows / subdirectory

    return workflows


def get_skills_dir() -> Path:
    """
    Get the skills directory path.

    Returns:
        Path to skills directory
    """
    return get_project_root() / "superskills"


def get_user_config_dir() -> Path:
    """
    Get the user configuration directory path.

    Returns:
        Path to user config directory (~/.superskills)
    """
    config_dir = Path.home() / ".superskills"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def generate_output_filename(name: str, format: str = 'markdown') -> str:
    """
    Generate a timestamped output filename.
    
    Args:
        name: Base name (skill or workflow name)
        format: Output format ('markdown', 'plain', 'json', 'yaml')
    
    Returns:
        Filename string with timestamp
    """
    from datetime import datetime
    
    # Sanitize name (remove special characters)
    safe_name = name.replace('/', '_').replace('\\', '_').replace(' ', '_')
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Determine file extension
    ext_map = {
        'markdown': 'md',
        'plain': 'txt',
        'json': 'json',
        'yaml': 'yaml'
    }
    ext = ext_map.get(format, 'txt')
    
    return f"{safe_name}_{timestamp}.{ext}"
