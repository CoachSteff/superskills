"""
CLI command: search - Search for files, content, or skills
"""
import os
import subprocess
from pathlib import Path
from typing import List

from cli.utils.config import CLIConfig
from cli.utils.logger import get_logger


def search_command(query: str, search_type: str = 'auto', **kwargs) -> int:
    """
    Search for files, content, or skills

    Args:
        query: Search query
        search_type: Type of search (file|content|skill|auto)
        **kwargs: Additional options

    Returns:
        Exit code (0 for success, 1 for error)
    """
    config = CLIConfig()
    logger = get_logger()

    logger.debug(f"Search query: {query}, type: {search_type}")

    # Auto-detect search type if needed
    if search_type == 'auto':
        search_type = _detect_search_type(query)

    try:
        if search_type == 'skill':
            return _search_skills(query, config)
        elif search_type == 'content':
            return _search_content(query, config)
        else:  # file or auto
            return _search_files(query, config)

    except Exception as e:
        logger.error(f"Search failed: {e}")
        print(f"✗ Error: {e}")
        return 1


def _detect_search_type(query: str) -> str:
    """Auto-detect search type from query"""
    query_lower = query.lower()

    # Skill-related keywords
    skill_keywords = ['skill', 'workflow', 'capability', 'can do', 'help with']
    if any(kw in query_lower for kw in skill_keywords):
        return 'skill'

    # Content-related keywords
    content_keywords = ['contains', 'text', 'content', 'inside']
    if any(kw in query_lower for kw in content_keywords):
        return 'content'

    # Default to file search
    return 'file'


def _search_skills(query: str, config: CLIConfig) -> int:
    """Search skills by description/capability"""
    from cli.commands.discover import discover_command

    print(f"→ Searching skills for: {query}\n")
    return discover_command(query=query)


def _search_files(query: str, config: CLIConfig) -> int:
    """Search for files by name"""
    print(f"→ Searching files for: {query}")

    search_paths = _get_search_paths(config)
    matches = []

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Search using glob patterns
        try:
            # Try exact match first
            exact_matches = list(search_path.rglob(query))
            matches.extend([(str(m), m) for m in exact_matches])

            # Try case-insensitive pattern match
            pattern = f"*{query}*"
            pattern_matches = list(search_path.rglob(pattern))
            matches.extend([(str(m), m) for m in pattern_matches if m not in exact_matches])

        except Exception as e:
            get_logger().warning(f"Error searching {search_path}: {e}")
            continue

    # Remove duplicates (keep order)
    seen = set()
    unique_matches = []
    for match_str, match_path in matches:
        if match_str not in seen:
            seen.add(match_str)
            unique_matches.append((match_str, match_path))

    # Display results
    if not unique_matches:
        print("No files found")
        return 0

    print(f"Found {len(unique_matches)} match(es):\n")
    for i, (match_str, match_path) in enumerate(unique_matches[:50], 1):
        # Show relative path if inside current directory
        try:
            rel_path = match_path.relative_to(Path.cwd())
            print(f"  {i}. {rel_path}")
        except ValueError:
            print(f"  {i}. {match_str}")

    if len(unique_matches) > 50:
        print(f"\n... and {len(unique_matches) - 50} more")

    return 0


def _search_content(query: str, config: CLIConfig) -> int:
    """Search file contents"""
    print(f"→ Searching file contents for: {query}")

    search_paths = _get_search_paths(config)
    use_ripgrep = config.get('search.use_ripgrep', True)

    # Try ripgrep first if enabled
    if use_ripgrep and _is_command_available('rg'):
        return _search_with_ripgrep(query, search_paths, config)
    else:
        return _search_with_grep(query, search_paths, config)


def _search_with_ripgrep(query: str, search_paths: List[Path], config: CLIConfig) -> int:
    """Search using ripgrep"""
    max_results = config.get('search.max_results', 50)

    # Build ripgrep command
    cmd = ['rg', '--color', 'never', '--line-number', '--max-count', str(max_results)]

    # Add search paths
    for path in search_paths:
        if path.exists():
            cmd.append(str(path))

    cmd.append(query)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Found matches
            print(result.stdout)
            return 0
        elif result.returncode == 1:
            # No matches found
            print("No matches found")
            return 0
        else:
            # Error
            print(f"Search error: {result.stderr}")
            return 1

    except Exception as e:
        get_logger().error(f"Ripgrep search failed: {e}")
        print(f"✗ Error: {e}")
        return 1


def _search_with_grep(query: str, search_paths: List[Path], config: CLIConfig) -> int:
    """Search using grep (fallback)"""
    max_results = config.get('search.max_results', 50)
    matches = []

    for search_path in search_paths:
        if not search_path.exists():
            continue

        try:
            # Use grep recursively
            cmd = ['grep', '-r', '-n', '-I', query, str(search_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                matches.append(result.stdout)

        except Exception as e:
            get_logger().warning(f"Error searching {search_path}: {e}")
            continue

    if not matches:
        print("No matches found")
        return 0

    # Display results (limit to max_results)
    all_lines = []
    for match_output in matches:
        all_lines.extend(match_output.strip().split('\n'))

    print('\n'.join(all_lines[:max_results]))

    if len(all_lines) > max_results:
        print(f"\n... and {len(all_lines) - max_results} more matches")

    return 0


def _get_search_paths(config: CLIConfig) -> List[Path]:
    """Get search paths from config with environment variable expansion"""
    path_configs = config.get('search.paths', [
        '${OBSIDIAN_VAULT_PATH}',
        '~/Documents',
        '~/Downloads',
        '.'
    ])

    search_paths = []
    for path_str in path_configs:
        # Expand environment variables
        expanded = os.path.expandvars(path_str)

        # Expand home directory
        expanded = os.path.expanduser(expanded)

        # Convert to Path
        path = Path(expanded)

        # Only add if exists
        if path.exists():
            search_paths.append(path)
        else:
            get_logger().debug(f"Search path does not exist: {expanded}")

    # Always include current directory if not already included
    cwd = Path.cwd()
    if cwd not in search_paths:
        search_paths.append(cwd)

    return search_paths


def _is_command_available(command: str) -> bool:
    """Check if a command is available in PATH"""
    try:
        subprocess.run([command, '--version'],
                      capture_output=True,
                      check=False,
                      timeout=1)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
