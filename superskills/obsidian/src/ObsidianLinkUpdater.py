"""
Link tracking and updating for Obsidian vault.
"""
from pathlib import Path
from typing import Dict, List, Set

from .ObsidianParser import extract_links, parse_frontmatter, update_link_in_content


class LinkIndex:
    """Manages link index for fast backlink queries."""

    def __init__(self):
        self.forward_links: Dict[str, List[str]] = {}
        self.backlinks: Dict[str, Set[str]] = {}

    def build_index(self, vault_path: Path) -> None:
        """
        Build link index by scanning all notes.

        Args:
            vault_path: Path to vault root
        """
        self.forward_links = {}
        self.backlinks = {}

        for md_file in vault_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                _, body = parse_frontmatter(content)
                links = extract_links(body)

                relative_path = str(md_file.relative_to(vault_path))
                self.forward_links[relative_path] = links

                for link_target in links:
                    if link_target not in self.backlinks:
                        self.backlinks[link_target] = set()
                    self.backlinks[link_target].add(relative_path)

            except Exception:
                continue

    def get_backlinks(self, note_path: str) -> List[str]:
        """
        Get all notes that link to the specified note.

        Args:
            note_path: Relative path or title of note

        Returns:
            List of relative paths of notes linking to this note
        """
        note_title = Path(note_path).stem

        backlinks = set()

        if note_path in self.backlinks:
            backlinks.update(self.backlinks[note_path])

        if note_title in self.backlinks:
            backlinks.update(self.backlinks[note_title])

        return list(backlinks)


def update_links_after_move(
    vault_path: Path,
    old_path: str,
    new_path: str,
    old_title: str,
    new_title: str
) -> List[str]:
    """
    Update all wiki links after moving/renaming a note.

    Args:
        vault_path: Path to vault root
        old_path: Old relative path
        new_path: New relative path
        old_title: Old note title (filename without extension)
        new_title: New note title (filename without extension)

    Returns:
        List of affected file paths
    """
    affected_files = []

    for md_file in vault_path.rglob("*.md"):
        relative_path = str(md_file.relative_to(vault_path))

        if relative_path == new_path:
            continue

        try:
            content = md_file.read_text(encoding='utf-8')
            original_content = content

            content = update_link_in_content(content, old_title, new_title)

            old_path_without_ext = old_path.replace('.md', '')
            new_path_without_ext = new_path.replace('.md', '')
            content = update_link_in_content(content, old_path_without_ext, new_path_without_ext)

            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                affected_files.append(relative_path)

        except Exception:
            continue

    return affected_files


def resolve_link(vault_path: Path, link_text: str) -> List[Path]:
    """
    Resolve wiki link to actual file path(s).

    Args:
        vault_path: Path to vault root
        link_text: Link text from [[...]]

    Returns:
        List of matching file paths (can be multiple if ambiguous)
    """
    matches = []

    link_text = link_text.strip()

    if link_text.endswith('.md'):
        exact_path = vault_path / link_text
        if exact_path.exists():
            return [exact_path]
    else:
        exact_path = vault_path / f"{link_text}.md"
        if exact_path.exists():
            return [exact_path]

    for md_file in vault_path.rglob("*.md"):
        if md_file.stem == link_text:
            matches.append(md_file)

    return matches
