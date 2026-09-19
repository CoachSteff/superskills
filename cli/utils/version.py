"""
Version utilities for SuperSkills CLI
"""
import sys
from pathlib import Path


def get_version() -> str:
    """
<<<<<<< Updated upstream
    Get version from pyproject.toml.
=======
    Get the installed package version, falling back to pyproject.toml
    for source checkouts.
>>>>>>> Stashed changes

    Returns:
        Version string (e.g., "2.4.0") or "unknown" if not found
    """
    # Installed package (wheel/sdist): pyproject.toml is not shipped,
    # so ask package metadata first.
    try:
        from importlib.metadata import version
        return version('superskills')
    except Exception:
        pass

    pyproject_path = Path(__file__).parent.parent.parent / 'pyproject.toml'

    if not pyproject_path.exists():
        return 'unknown'

    try:
        # For Python 3.11+, use built-in tomllib
        if sys.version_info >= (3, 11):
            import tomllib
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
            return data.get('project', {}).get('version', 'unknown')

        # For Python 3.9-3.10, try tomli or fall back to simple parsing
        try:
            import tomli
            with open(pyproject_path, 'rb') as f:
                data = tomli.load(f)
            return data.get('project', {}).get('version', 'unknown')
        except ImportError:
            # Fallback: simple regex parsing
            with open(pyproject_path, 'r') as f:
                for line in f:
                    if line.startswith('version ='):
                        # Extract version from: version = "2.4.0"
                        version = line.split('=')[1].strip().strip('"').strip("'")
                        return version
            return 'unknown'

    except Exception:
        return 'unknown'
