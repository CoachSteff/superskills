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
