"""
Data models for Obsidian vault operations.
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple


@dataclass
class ObsidianNote:
    """Represents an Obsidian note."""
    path: Path
    relative_path: str
    title: str
    frontmatter: Dict
    content: str
    body: str
    headings: List[Tuple[int, str]]
    tags: List[str]
    links: List[str]
    created_at: str
    updated_at: str
    backlinks: List[str] = field(default_factory=list)

    def dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": str(self.path),
            "relative_path": self.relative_path,
            "title": self.title,
            "frontmatter": self.frontmatter,
            "content": self.content,
            "body": self.body,
            "headings": self.headings,
            "tags": self.tags,
            "links": self.links,
            "backlinks": self.backlinks,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ObsidianOperationResult:
    """Result from an Obsidian operation."""
    success: bool
    operation: str
    message: str
    note_path: Optional[str] = None
    affected_files: Optional[List[str]] = None
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "operation": self.operation,
            "message": self.message,
            "note_path": self.note_path,
            "affected_files": self.affected_files,
            "timestamp": self.timestamp,
        }


@dataclass
class PlannedOperation:
    """A planned operation in a change plan."""
    action: Literal["create", "update", "move", "delete"]
    target_path: str
    details: str
    changes: Optional[Dict] = None

    def dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "action": self.action,
            "target_path": self.target_path,
            "details": self.details,
            "changes": self.changes,
        }


@dataclass
class ObsidianChangesPlan:
    """A plan describing changes to be made to the vault."""
    operations: List[PlannedOperation]
    summary: str

    def dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "operations": [op.dict() for op in self.operations],
            "summary": self.summary,
        }
