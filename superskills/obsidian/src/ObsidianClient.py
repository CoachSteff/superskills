"""
ObsidianClient.py - Main client for Obsidian vault operations.
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Literal

from .ObsidianDocument import (
    ObsidianNote,
    ObsidianOperationResult,
    PlannedOperation,
    ObsidianChangesPlan
)
from .ObsidianParser import (
    parse_frontmatter,
    serialize_frontmatter,
    merge_frontmatter,
    extract_headings,
    extract_tags_from_frontmatter,
    extract_links,
    find_section,
    get_title_from_content
)
from .ObsidianSearch import text_search, tag_search, filter_notes_by_folder
from .ObsidianLinkUpdater import LinkIndex, update_links_after_move, resolve_link

logger = logging.getLogger(__name__)


class ObsidianClient:
    """Client for interacting with Obsidian vault via filesystem."""
    
    def __init__(
        self,
        vault_path: Optional[str] = None,
        read_only: bool = False,
        auto_update_links: bool = True,
        verbose: bool = True
    ):
        """
        Initialize Obsidian client.
        
        Args:
            vault_path: Path to vault root (or use OBSIDIAN_VAULT_PATH env var)
            read_only: If True, prevent all write operations
            auto_update_links: Auto-update wiki links on move/rename
            verbose: Enable verbose logging
        """
        self.vault_path = Path(vault_path or os.getenv("OBSIDIAN_VAULT_PATH", ""))
        
        if not vault_path and not os.getenv("OBSIDIAN_VAULT_PATH"):
            raise ValueError(
                "OBSIDIAN_VAULT_PATH environment variable not set. "
                "Please set vault_path parameter or OBSIDIAN_VAULT_PATH environment variable."
            )
        
        if not self.vault_path.exists():
            raise ValueError(
                f"Vault path does not exist: {self.vault_path}"
            )
        
        if not self.vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {self.vault_path}")
        
        self.vault_path = self.vault_path.resolve()
        self.read_only = read_only or os.getenv("OBSIDIAN_READ_ONLY", "").lower() == "true"
        self.auto_update_links = auto_update_links
        self.verbose = verbose
        
        self.link_index = LinkIndex()
        if self.verbose:
            logger.info(f"Building link index for vault: {self.vault_path}")
        self.link_index.build_index(self.vault_path)
    
    def _validate_path(self, path: Path) -> Path:
        """Ensure path is within vault."""
        resolved = path.resolve()
        try:
            resolved.relative_to(self.vault_path)
            return resolved
        except ValueError:
            raise ValueError(f"Path is outside vault: {path}")
    
    def _check_read_only(self):
        """Raise exception if in read-only mode."""
        if self.read_only:
            raise PermissionError("Vault is in read-only mode. Set read_only=False to enable writes.")
    
    def _ensure_folder_exists(self, folder: Path):
        """Create folder if it doesn't exist."""
        self._check_read_only()
        folder.mkdir(parents=True, exist_ok=True)
    
    def _parse_note(self, file_path: Path) -> ObsidianNote:
        """Parse a note file into ObsidianNote object."""
        content = file_path.read_text(encoding='utf-8')
        frontmatter, body = parse_frontmatter(content)
        
        tags = extract_tags_from_frontmatter(frontmatter)
        headings = extract_headings(body)
        links = extract_links(body)
        title = get_title_from_content(body, frontmatter, file_path.stem)
        
        stat = file_path.stat()
        created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
        updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        relative_path = str(file_path.relative_to(self.vault_path))
        backlinks = self.link_index.get_backlinks(relative_path)
        
        return ObsidianNote(
            path=file_path,
            relative_path=relative_path,
            title=title,
            frontmatter=frontmatter,
            content=content,
            body=body,
            headings=headings,
            tags=tags,
            links=links,
            created_at=created_at,
            updated_at=updated_at,
            backlinks=backlinks
        )
    
    def list_notes(
        self,
        folder: Optional[str] = None,
        recursive: bool = True
    ) -> List[ObsidianNote]:
        """
        List all notes in vault or specific folder.
        
        Args:
            folder: Folder path relative to vault root (None for all)
            recursive: Search subfolders
            
        Returns:
            List of ObsidianNote objects
        """
        if folder:
            search_path = self.vault_path / folder
            self._validate_path(search_path)
        else:
            search_path = self.vault_path
        
        if recursive:
            files = search_path.rglob("*.md")
        else:
            files = search_path.glob("*.md")
        
        notes = []
        for file_path in files:
            try:
                note = self._parse_note(file_path)
                notes.append(note)
            except Exception as e:
                if self.verbose:
                    logger.warning(f"Failed to parse {file_path}: {e}")
        
        return sorted(notes, key=lambda n: n.relative_path)
    
    def get_note(self, path_or_title: str) -> Optional[ObsidianNote]:
        """
        Get a note by path or title.
        
        Args:
            path_or_title: Relative path, absolute path, or note title
            
        Returns:
            ObsidianNote or None if not found
        """
        file_path = Path(path_or_title)
        
        if file_path.is_absolute():
            file_path = self._validate_path(file_path)
        else:
            file_path = self.vault_path / path_or_title
            file_path = self._validate_path(file_path)
        
        if file_path.exists() and file_path.suffix == '.md':
            return self._parse_note(file_path)
        
        if not path_or_title.endswith('.md'):
            file_path = self.vault_path / f"{path_or_title}.md"
            if file_path.exists():
                return self._parse_note(file_path)
        
        for md_file in self.vault_path.rglob("*.md"):
            if md_file.stem == path_or_title:
                return self._parse_note(md_file)
        
        # Search by title in frontmatter
        for md_file in self.vault_path.rglob("*.md"):
            try:
                note = self._parse_note(md_file)
                if note.title == path_or_title:
                    return note
            except Exception:
                continue
        
        return None
    
    def search_notes(
        self,
        query: str,
        search_in: Literal["content", "title", "both"] = "both",
        case_sensitive: bool = False,
        limit: int = 50
    ) -> List[ObsidianNote]:
        """
        Search notes by text.
        
        Args:
            query: Search query
            search_in: Where to search
            case_sensitive: Case-sensitive search
            limit: Maximum results
            
        Returns:
            List of matching notes
        """
        file_paths = text_search(self.vault_path, query, search_in, case_sensitive)
        
        notes = []
        for file_path in file_paths[:limit]:
            try:
                note = self._parse_note(file_path)
                notes.append(note)
            except Exception:
                continue
        
        return notes
    
    def find_by_tag(
        self,
        tag: str,
        exact_match: bool = False
    ) -> List[ObsidianNote]:
        """
        Find notes by tag.
        
        Args:
            tag: Tag to search for (e.g., "topic/ai" or "topic")
            exact_match: If False, match tag prefix
            
        Returns:
            List of matching notes
        """
        file_paths = tag_search(self.vault_path, tag, exact_match)
        
        notes = []
        for file_path in file_paths:
            try:
                note = self._parse_note(file_path)
                notes.append(note)
            except Exception:
                continue
        
        return notes
    
    def find_by_tags(
        self,
        tags: List[str],
        match_all: bool = True
    ) -> List[ObsidianNote]:
        """
        Find notes matching multiple tags.
        
        Args:
            tags: List of tags
            match_all: If True, note must have all tags (AND). If False, any tag (OR).
            
        Returns:
            List of matching notes
        """
        if not tags:
            return []
        
        tag_results = [set(tag_search(self.vault_path, tag, exact_match=False)) for tag in tags]
        
        if match_all:
            matching_paths = set.intersection(*tag_results)
        else:
            matching_paths = set.union(*tag_results)
        
        notes = []
        for file_path in matching_paths:
            try:
                note = self._parse_note(file_path)
                notes.append(note)
            except Exception:
                continue
        
        return notes
    
    def find_by_folder(
        self,
        folder: str,
        recursive: bool = True
    ) -> List[ObsidianNote]:
        """
        Find notes in a specific folder.
        
        Args:
            folder: Folder path relative to vault root
            recursive: Search subfolders
            
        Returns:
            List of notes in folder
        """
        return self.list_notes(folder=folder, recursive=recursive)
    
    def find_backlinks(self, note_path: str) -> List[ObsidianNote]:
        """
        Find all notes that link to the specified note.
        
        Args:
            note_path: Relative path or title of note
            
        Returns:
            List of notes linking to this note
        """
        backlink_paths = self.link_index.get_backlinks(note_path)
        
        notes = []
        for rel_path in backlink_paths:
            try:
                file_path = self.vault_path / rel_path
                note = self._parse_note(file_path)
                notes.append(note)
            except Exception:
                continue
        
        return notes
    
    def create_note(
        self,
        path: str,
        content: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        frontmatter: Optional[Dict] = None,
        folder: Optional[str] = None
    ) -> ObsidianOperationResult:
        """
        Create a new note.
        
        Args:
            path: Relative path for new note (with or without .md)
            content: Note content (body)
            title: Note title (added to frontmatter)
            tags: Tags to add to frontmatter
            frontmatter: Additional frontmatter fields
            folder: Create in specific folder (overrides path folder)
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        if not path.endswith('.md'):
            path = f"{path}.md"
        
        if folder:
            file_path = self.vault_path / folder / Path(path).name
        else:
            file_path = self.vault_path / path
        
        file_path = self._validate_path(file_path)
        
        if file_path.exists():
            return ObsidianOperationResult(
                success=False,
                operation="create",
                message=f"Note already exists: {path}",
                note_path=str(file_path.relative_to(self.vault_path))
            )
        
        self._ensure_folder_exists(file_path.parent)
        
        fm = frontmatter or {}
        fm['created'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fm['modified'] = fm['created']
        
        if title:
            fm['title'] = title
        
        if tags:
            fm['tags'] = tags
        
        full_content = serialize_frontmatter(fm) + "\n" + content
        
        file_path.write_text(full_content, encoding='utf-8')
        
        self.link_index.build_index(self.vault_path)
        
        return ObsidianOperationResult(
            success=True,
            operation="create",
            message=f"Note created: {path}",
            note_path=str(file_path.relative_to(self.vault_path))
        )
    
    def update_note(
        self,
        path: str,
        content: Optional[str] = None,
        frontmatter: Optional[Dict] = None,
        merge_frontmatter_flag: bool = True
    ) -> ObsidianOperationResult:
        """
        Update an existing note.
        
        Args:
            path: Relative path or title
            content: New content (None to keep existing)
            frontmatter: Frontmatter to add/update
            merge_frontmatter_flag: If True, merge. If False, replace.
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        note = self.get_note(path)
        if not note:
            return ObsidianOperationResult(
                success=False,
                operation="update",
                message=f"Note not found: {path}"
            )
        
        existing_fm, existing_body = parse_frontmatter(note.content)
        
        if frontmatter:
            if merge_frontmatter_flag:
                new_fm = merge_frontmatter(existing_fm, frontmatter)
            else:
                new_fm = frontmatter.copy()
                new_fm['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            new_fm = existing_fm.copy()
            new_fm['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_body = content if content is not None else existing_body
        
        full_content = serialize_frontmatter(new_fm) + "\n" + new_body
        
        note.path.write_text(full_content, encoding='utf-8')
        
        return ObsidianOperationResult(
            success=True,
            operation="update",
            message=f"Note updated: {note.relative_path}",
            note_path=note.relative_path
        )
    
    def update_section(
        self,
        path: str,
        heading: str,
        new_content: str
    ) -> ObsidianOperationResult:
        """
        Update content under a specific heading.
        
        Args:
            path: Relative path or title
            heading: Heading text
            new_content: New content for section
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        note = self.get_note(path)
        if not note:
            return ObsidianOperationResult(
                success=False,
                operation="update_section",
                message=f"Note not found: {path}"
            )
        
        section_range = find_section(note.body, heading)
        if not section_range:
            return ObsidianOperationResult(
                success=False,
                operation="update_section",
                message=f"Section not found: {heading}"
            )
        
        start_idx, end_idx = section_range
        new_body = note.body[:start_idx] + "\n" + new_content + "\n" + note.body[end_idx:]
        
        frontmatter, _ = parse_frontmatter(note.content)
        frontmatter['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        full_content = serialize_frontmatter(frontmatter) + "\n" + new_body
        
        note.path.write_text(full_content, encoding='utf-8')
        
        return ObsidianOperationResult(
            success=True,
            operation="update_section",
            message=f"Section updated: {heading}",
            note_path=note.relative_path
        )
    
    def append_content(
        self,
        path: str,
        content: str
    ) -> ObsidianOperationResult:
        """
        Append content to end of note.
        
        Args:
            path: Relative path or title
            content: Content to append
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        note = self.get_note(path)
        if not note:
            return ObsidianOperationResult(
                success=False,
                operation="append",
                message=f"Note not found: {path}"
            )
        
        frontmatter, body = parse_frontmatter(note.content)
        frontmatter['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_body = body.rstrip() + "\n\n" + content
        full_content = serialize_frontmatter(frontmatter) + "\n" + new_body
        
        note.path.write_text(full_content, encoding='utf-8')
        
        return ObsidianOperationResult(
            success=True,
            operation="append",
            message=f"Content appended to: {note.relative_path}",
            note_path=note.relative_path
        )
    
    def move_note(
        self,
        source: str,
        destination: str,
        update_links: Optional[bool] = None
    ) -> ObsidianOperationResult:
        """
        Move or rename a note.
        
        Args:
            source: Source path or title
            destination: Destination path (relative to vault)
            update_links: Update wiki links (uses auto_update_links if None)
            
        Returns:
            Operation result with affected files
        """
        self._check_read_only()
        
        note = self.get_note(source)
        if not note:
            return ObsidianOperationResult(
                success=False,
                operation="move",
                message=f"Note not found: {source}"
            )
        
        if not destination.endswith('.md'):
            destination = f"{destination}.md"
        
        dest_path = self.vault_path / destination
        dest_path = self._validate_path(dest_path)
        
        if dest_path.exists():
            return ObsidianOperationResult(
                success=False,
                operation="move",
                message=f"Destination already exists: {destination}"
            )
        
        self._ensure_folder_exists(dest_path.parent)
        
        old_title = note.path.stem
        new_title = dest_path.stem
        old_relative = note.relative_path
        new_relative = str(dest_path.relative_to(self.vault_path))
        
        note.path.rename(dest_path)
        
        affected_files = []
        should_update_links = update_links if update_links is not None else self.auto_update_links
        
        if should_update_links and old_title != new_title:
            if self.verbose:
                logger.info(f"Updating links: {old_title} -> {new_title}")
            affected_files = update_links_after_move(
                self.vault_path,
                old_relative,
                new_relative,
                old_title,
                new_title
            )
        
        self.link_index.build_index(self.vault_path)
        
        return ObsidianOperationResult(
            success=True,
            operation="move",
            message=f"Note moved: {old_relative} -> {new_relative}",
            note_path=new_relative,
            affected_files=affected_files
        )
    
    def add_tag(
        self,
        path: str,
        tag: str
    ) -> ObsidianOperationResult:
        """Add a tag to a note."""
        return self.add_tags(path, [tag])
    
    def add_tags(
        self,
        path: str,
        tags: List[str]
    ) -> ObsidianOperationResult:
        """
        Add tags to a note.
        
        Args:
            path: Relative path or title
            tags: Tags to add
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        note = self.get_note(path)
        if not note:
            return ObsidianOperationResult(
                success=False,
                operation="add_tags",
                message=f"Note not found: {path}"
            )
        
        frontmatter, body = parse_frontmatter(note.content)
        
        existing_tags = frontmatter.get('tags', [])
        if isinstance(existing_tags, str):
            existing_tags = [existing_tags]
        
        new_tags = list(set(existing_tags + tags))
        frontmatter['tags'] = new_tags
        frontmatter['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        full_content = serialize_frontmatter(frontmatter) + "\n" + body
        
        note.path.write_text(full_content, encoding='utf-8')
        
        return ObsidianOperationResult(
            success=True,
            operation="add_tags",
            message=f"Tags added: {', '.join(tags)}",
            note_path=note.relative_path
        )
    
    def remove_tag(
        self,
        path: str,
        tag: str
    ) -> ObsidianOperationResult:
        """
        Remove a tag from a note.
        
        Args:
            path: Relative path or title
            tag: Tag to remove
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        note = self.get_note(path)
        if not note:
            return ObsidianOperationResult(
                success=False,
                operation="remove_tag",
                message=f"Note not found: {path}"
            )
        
        frontmatter, body = parse_frontmatter(note.content)
        
        existing_tags = frontmatter.get('tags', [])
        if isinstance(existing_tags, str):
            existing_tags = [existing_tags]
        
        new_tags = [t for t in existing_tags if t != tag]
        frontmatter['tags'] = new_tags
        frontmatter['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        full_content = serialize_frontmatter(frontmatter) + "\n" + body
        
        note.path.write_text(full_content, encoding='utf-8')
        
        return ObsidianOperationResult(
            success=True,
            operation="remove_tag",
            message=f"Tag removed: {tag}",
            note_path=note.relative_path
        )
    
    def set_tags(
        self,
        path: str,
        tags: List[str]
    ) -> ObsidianOperationResult:
        """
        Replace all tags on a note.
        
        Args:
            path: Relative path or title
            tags: New tags list
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        note = self.get_note(path)
        if not note:
            return ObsidianOperationResult(
                success=False,
                operation="set_tags",
                message=f"Note not found: {path}"
            )
        
        frontmatter, body = parse_frontmatter(note.content)
        frontmatter['tags'] = tags
        frontmatter['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        full_content = serialize_frontmatter(frontmatter) + "\n" + body
        
        note.path.write_text(full_content, encoding='utf-8')
        
        return ObsidianOperationResult(
            success=True,
            operation="set_tags",
            message=f"Tags set: {', '.join(tags)}",
            note_path=note.relative_path
        )
    
    def add_link(
        self,
        source_path: str,
        target_note: str,
        position: Literal["end", "after_heading"] = "end",
        heading: Optional[str] = None
    ) -> ObsidianOperationResult:
        """
        Add a wiki link to a note.
        
        Args:
            source_path: Source note path or title
            target_note: Target note title or path
            position: Where to add link
            heading: Heading name (if position="after_heading")
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        note = self.get_note(source_path)
        if not note:
            return ObsidianOperationResult(
                success=False,
                operation="add_link",
                message=f"Note not found: {source_path}"
            )
        
        link_text = f"[[{target_note}]]"
        
        frontmatter, body = parse_frontmatter(note.content)
        
        if position == "end":
            new_body = body.rstrip() + f"\n\n{link_text}"
        elif position == "after_heading" and heading:
            section_range = find_section(body, heading)
            if not section_range:
                return ObsidianOperationResult(
                    success=False,
                    operation="add_link",
                    message=f"Heading not found: {heading}"
                )
            start_idx, _ = section_range
            new_body = body[:start_idx] + f"\n{link_text}\n" + body[start_idx:]
        else:
            new_body = body.rstrip() + f"\n\n{link_text}"
        
        frontmatter['modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        full_content = serialize_frontmatter(frontmatter) + "\n" + new_body
        
        note.path.write_text(full_content, encoding='utf-8')
        
        self.link_index.build_index(self.vault_path)
        
        return ObsidianOperationResult(
            success=True,
            operation="add_link",
            message=f"Link added: {target_note}",
            note_path=note.relative_path
        )
    
    def create_hub(
        self,
        hub_path: str,
        title: str,
        linked_notes: List[str],
        description: Optional[str] = None,
        group_by_tag: Optional[str] = None
    ) -> ObsidianOperationResult:
        """
        Create or update a hub/index note.
        
        Args:
            hub_path: Path for hub note
            title: Hub title
            linked_notes: List of note paths/titles to link
            description: Optional description
            group_by_tag: Group notes by tag category (e.g., "topic")
            
        Returns:
            Operation result
        """
        self._check_read_only()
        
        content_parts = []
        
        if description:
            content_parts.append(description)
            content_parts.append("")
        
        if group_by_tag:
            groups: Dict[str, List[str]] = {}
            
            for note_path in linked_notes:
                note = self.get_note(note_path)
                if not note:
                    continue
                
                tag_found = False
                for tag in note.tags:
                    if tag.startswith(f"{group_by_tag}/"):
                        group_name = tag
                        if group_name not in groups:
                            groups[group_name] = []
                        groups[group_name].append(note_path)
                        tag_found = True
                        break
                
                if not tag_found:
                    if "Other" not in groups:
                        groups["Other"] = []
                    groups["Other"].append(note_path)
            
            for group_name in sorted(groups.keys()):
                content_parts.append(f"## {group_name}")
                content_parts.append("")
                for note_path in sorted(groups[group_name]):
                    content_parts.append(f"- [[{note_path}]]")
                content_parts.append("")
        else:
            content_parts.append("## Notes")
            content_parts.append("")
            for note_path in sorted(linked_notes):
                content_parts.append(f"- [[{note_path}]]")
        
        content = "\n".join(content_parts)
        
        existing_note = self.get_note(hub_path)
        if existing_note:
            return self.update_note(hub_path, content=content)
        else:
            return self.create_note(hub_path, content, title=title)
    
    def plan_changes(
        self,
        operations: List[Dict]
    ) -> ObsidianChangesPlan:
        """
        Plan changes without executing (dry-run).
        
        Args:
            operations: List of operation dicts
            
        Returns:
            Change plan
        """
        planned_ops = []
        
        for op_dict in operations:
            action = op_dict.get('action')
            details = op_dict.get('details', '')
            target = op_dict.get('target', '')
            
            planned_op = PlannedOperation(
                action=action,
                target_path=target,
                details=details,
                changes=op_dict.get('changes')
            )
            planned_ops.append(planned_op)
        
        summary = f"{len(planned_ops)} operation(s) planned"
        
        return ObsidianChangesPlan(
            operations=planned_ops,
            summary=summary
        )
    
    def apply_plan(
        self,
        plan: ObsidianChangesPlan
    ) -> List[ObsidianOperationResult]:
        """
        Execute a change plan.
        
        Args:
            plan: Change plan to execute
            
        Returns:
            List of operation results
        """
        results = []
        
        for op in plan.operations:
            if op.action == "create":
                result = self.create_note(
                    path=op.target_path,
                    content=op.changes.get('content', '') if op.changes else '',
                    **op.changes if op.changes else {}
                )
            elif op.action == "update":
                result = self.update_note(
                    path=op.target_path,
                    **op.changes if op.changes else {}
                )
            elif op.action == "move":
                result = self.move_note(
                    source=op.changes.get('source') if op.changes else op.target_path,
                    destination=op.target_path
                )
            elif op.action == "delete":
                result = ObsidianOperationResult(
                    success=False,
                    operation="delete",
                    message="Delete operation not implemented for safety"
                )
            else:
                result = ObsidianOperationResult(
                    success=False,
                    operation=op.action,
                    message=f"Unknown operation: {op.action}"
                )
            
            results.append(result)
        
        return results
