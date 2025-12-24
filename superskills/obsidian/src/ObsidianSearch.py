"""
Search functionality for Obsidian vault.
"""
import re
from pathlib import Path
from typing import List, Literal

from .ObsidianParser import extract_tags_from_frontmatter, parse_frontmatter


def text_search(
    vault_path: Path,
    query: str,
    search_in: Literal["content", "title", "both"] = "both",
    case_sensitive: bool = False
) -> List[Path]:
    """
    Search for text in vault notes.

    Args:
        vault_path: Path to vault root
        query: Search query
        search_in: Where to search (content, title, both)
        case_sensitive: Whether search is case-sensitive

    Returns:
        List of matching file paths
    """
    matches = []
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(re.escape(query), flags)

    for md_file in vault_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')

            if search_in in ("title", "both"):
                frontmatter, _ = parse_frontmatter(content)
                title = frontmatter.get('title', md_file.stem)
                if pattern.search(str(title)):
                    matches.append(md_file)
                    continue

            if search_in in ("content", "both"):
                if pattern.search(content):
                    matches.append(md_file)

        except Exception:
            continue

    return matches


def tag_search(
    vault_path: Path,
    tag: str,
    exact_match: bool = False
) -> List[Path]:
    """
    Search notes by tag.

    Args:
        vault_path: Path to vault root
        tag: Tag to search for (e.g., "topic/ai" or "topic")
        exact_match: If False, match tag prefix (e.g., "topic" matches "topic/ai")

    Returns:
        List of matching file paths
    """
    matches = []
    tag_lower = tag.lower()

    for md_file in vault_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter, _ = parse_frontmatter(content)
            note_tags = extract_tags_from_frontmatter(frontmatter)

            for note_tag in note_tags:
                note_tag_lower = note_tag.lower()

                if exact_match:
                    if note_tag_lower == tag_lower:
                        matches.append(md_file)
                        break
                else:
                    if note_tag_lower == tag_lower or note_tag_lower.startswith(tag_lower + '/'):
                        matches.append(md_file)
                        break

        except Exception:
            continue

    return matches


def filter_notes_by_folder(
    vault_path: Path,
    folder: str,
    recursive: bool = True
) -> List[Path]:
    """
    Get all notes in a specific folder.

    Args:
        vault_path: Path to vault root
        folder: Folder path relative to vault root
        recursive: Whether to search subfolders

    Returns:
        List of note paths
    """
    folder_path = vault_path / folder

    if not folder_path.exists() or not folder_path.is_dir():
        return []

    if recursive:
        return list(folder_path.rglob("*.md"))
    else:
        return list(folder_path.glob("*.md"))
