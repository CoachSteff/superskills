"""Tests for Obsidian skill."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import os

from superskills.obsidian.src import (
    ObsidianClient,
    ObsidianNote,
    ObsidianOperationResult,
    PlannedOperation,
    ObsidianChangesPlan
)
from superskills.obsidian.src.ObsidianParser import (
    parse_frontmatter,
    serialize_frontmatter,
    merge_frontmatter,
    extract_headings,
    extract_tags_from_frontmatter,
    extract_links,
    find_section,
    update_link_in_content
)


@pytest.fixture
def tmp_vault(tmp_path):
    """Create temporary vault directory."""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    return vault


@pytest.fixture
def sample_notes(tmp_vault):
    """Populate vault with sample notes."""
    # Note 1: Simple note with tags
    note1 = tmp_vault / "note1.md"
    note1.write_text("""---
title: First Note
tags:
  - topic/ai
  - status/draft
created: 2025-12-17 10:00:00
modified: 2025-12-17 10:00:00
---

# First Note

This is the first note with a [[note2]] link.

## Section 1

Content here.
""")
    
    # Note 2: Note with hierarchical tags
    note2 = tmp_vault / "note2.md"
    note2.write_text("""---
title: Second Note
tags:
  - topic/ai-adoption
  - type/blog
  - status/active
created: 2025-12-17 11:00:00
modified: 2025-12-17 11:00:00
---

# Second Note

Referenced by [[note1]].

## Implementation

Details about AI adoption.
""")
    
    # Note 3: In subfolder
    subfolder = tmp_vault / "Projects"
    subfolder.mkdir()
    note3 = subfolder / "project.md"
    note3.write_text("""---
title: Project Note
tags:
  - topic/coaching
  - context/project
  - status/active
created: 2025-12-17 12:00:00
modified: 2025-12-17 12:00:00
---

# Project Note

Project details here.
""")
    
    return {
        "note1": note1,
        "note2": note2,
        "note3": note3
    }


@pytest.fixture
def obsidian_client(tmp_vault, sample_notes, monkeypatch):
    """Create ObsidianClient instance with temp vault and sample notes."""
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_vault))
    return ObsidianClient(vault_path=str(tmp_vault), verbose=False)


@pytest.fixture
def empty_client(tmp_vault, monkeypatch):
    """Create ObsidianClient instance with empty vault."""
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_vault))
    return ObsidianClient(vault_path=str(tmp_vault), verbose=False)


class TestObsidianParser:
    """Test parsing utilities."""
    
    def test_parse_frontmatter_valid(self):
        """Test parsing valid YAML frontmatter."""
        content = """---
title: Test Note
tags:
  - tag1
  - tag2
---

Body content here.
"""
        frontmatter, body = parse_frontmatter(content)
        
        assert frontmatter['title'] == 'Test Note'
        assert frontmatter['tags'] == ['tag1', 'tag2']
        assert body.strip() == 'Body content here.'
    
    def test_parse_frontmatter_missing(self):
        """Test parsing content without frontmatter."""
        content = "Just body content, no frontmatter."
        frontmatter, body = parse_frontmatter(content)
        
        assert frontmatter == {}
        assert body == content
    
    def test_parse_frontmatter_malformed(self):
        """Test graceful handling of malformed frontmatter."""
        content = """---
invalid: yaml: syntax:
---

Body content.
"""
        frontmatter, body = parse_frontmatter(content)
        
        assert frontmatter == {}
    
    def test_serialize_frontmatter(self):
        """Test serializing frontmatter to YAML."""
        fm = {"title": "Test", "tags": ["tag1", "tag2"]}
        yaml_str = serialize_frontmatter(fm)
        
        assert yaml_str.startswith('---\n')
        assert yaml_str.endswith('---\n')
        assert 'title: Test' in yaml_str
    
    def test_merge_frontmatter(self):
        """Test merging two frontmatter dicts."""
        existing = {"title": "Old Title", "tags": ["tag1"], "other": "value"}
        new = {"title": "New Title", "tags": ["tag2"]}
        
        merged = merge_frontmatter(existing, new)
        
        assert merged['title'] == 'New Title'
        assert set(merged['tags']) == {'tag1', 'tag2'}
        assert merged['other'] == 'value'
        assert 'modified' in merged
    
    def test_extract_headings(self):
        """Test extracting headings from markdown."""
        content = """# Heading 1
Some text.

## Heading 2

### Heading 3

More text.

## Another H2
"""
        headings = extract_headings(content)
        
        assert len(headings) == 4
        assert headings[0] == (1, 'Heading 1')
        assert headings[1] == (2, 'Heading 2')
        assert headings[2] == (3, 'Heading 3')
        assert headings[3] == (2, 'Another H2')
    
    def test_extract_tags_from_frontmatter(self):
        """Test extracting tags from frontmatter."""
        fm = {"tags": ["topic/ai", "status/draft"]}
        tags = extract_tags_from_frontmatter(fm)
        
        assert tags == ["topic/ai", "status/draft"]
    
    def test_extract_tags_string(self):
        """Test extracting single tag as string."""
        fm = {"tags": "single-tag"}
        tags = extract_tags_from_frontmatter(fm)
        
        assert tags == ["single-tag"]
    
    def test_extract_links(self):
        """Test extracting wiki links."""
        content = """Some text with [[Link 1]] and [[Link 2|Alias]].
        
Also [[another link]] here.
"""
        links = extract_links(content)
        
        assert len(links) == 3
        assert 'Link 1' in links
        assert 'Link 2' in links
        assert 'another link' in links
    
    def test_find_section(self):
        """Test finding section boundaries."""
        content = """# Main Heading

Intro text.

## Section 1

Section 1 content.

## Section 2

Section 2 content.

## Section 3

Section 3 content.
"""
        start, end = find_section(content, "Section 2")
        
        section_content = content[start:end].strip()
        assert 'Section 2 content' in section_content
        assert 'Section 3' not in section_content
    
    def test_update_link_in_content(self):
        """Test updating wiki links in content."""
        content = "Link to [[Old Note]] and [[Old Note|Alias]]."
        
        updated = update_link_in_content(content, "Old Note", "New Note")
        
        assert "[[New Note]]" in updated
        assert "[[New Note|Alias]]" in updated
        assert "[[Old Note]]" not in updated


class TestObsidianClient:
    """Test ObsidianClient class."""
    
    def test_init_requires_vault_path(self, monkeypatch):
        """Test that initialization requires vault path."""
        monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
        with pytest.raises(ValueError, match="OBSIDIAN_VAULT_PATH"):
            ObsidianClient(vault_path=None)
    
    def test_init_with_vault_path(self, tmp_vault):
        """Test initialization with valid vault path."""
        client = ObsidianClient(vault_path=str(tmp_vault))
        assert client.vault_path == tmp_vault.resolve()
    
    def test_read_only_mode(self, tmp_vault):
        """Test read-only mode initialization."""
        client = ObsidianClient(vault_path=str(tmp_vault), read_only=True)
        assert client.read_only is True
    
    def test_list_notes(self, obsidian_client, sample_notes):
        """Test listing all notes."""
        notes = obsidian_client.list_notes()
        
        assert len(notes) == 3
        titles = [n.title for n in notes]
        assert "First Note" in titles
        assert "Second Note" in titles
        assert "Project Note" in titles
    
    def test_list_notes_in_folder(self, obsidian_client, sample_notes):
        """Test listing notes in specific folder."""
        notes = obsidian_client.list_notes(folder="Projects")
        
        assert len(notes) == 1
        assert notes[0].title == "Project Note"
    
    def test_get_note_by_path(self, obsidian_client, sample_notes):
        """Test getting note by path."""
        note = obsidian_client.get_note("note1.md")
        
        assert note is not None
        assert note.title == "First Note"
        assert "topic/ai" in note.tags
        assert "status/draft" in note.tags
    
    def test_get_note_by_title(self, obsidian_client, sample_notes):
        """Test getting note by title."""
        note = obsidian_client.get_note("Second Note")
        
        assert note is not None
        assert note.title == "Second Note"
    
    def test_get_note_not_found(self, obsidian_client, sample_notes):
        """Test getting non-existent note."""
        note = obsidian_client.get_note("nonexistent.md")
        
        assert note is None
    
    def test_search_notes(self, obsidian_client, sample_notes):
        """Test searching notes by text."""
        results = obsidian_client.search_notes("AI adoption")
        
        assert len(results) >= 1
        assert any(n.title == "Second Note" for n in results)
    
    def test_find_by_tag_exact(self, obsidian_client, sample_notes):
        """Test finding notes by exact tag."""
        notes = obsidian_client.find_by_tag("topic/ai", exact_match=True)
        
        assert len(notes) == 1
        assert notes[0].title == "First Note"
    
    def test_find_by_tag_hierarchical(self, obsidian_client, sample_notes):
        """Test finding notes by tag prefix."""
        # Search for "topic" should match all topic/* tags
        notes = obsidian_client.find_by_tag("topic", exact_match=False)
        
        assert len(notes) == 3  # All notes have topic/* tags
        titles = [n.title for n in notes]
        assert "First Note" in titles
        assert "Second Note" in titles
        assert "Project Note" in titles
    
    def test_find_by_tags_all(self, obsidian_client, sample_notes):
        """Test finding notes with all tags (AND)."""
        notes = obsidian_client.find_by_tags(
            ["type/blog", "status/active"],
            match_all=True
        )
        
        assert len(notes) == 1
        assert notes[0].title == "Second Note"
    
    def test_find_by_tags_any(self, obsidian_client, sample_notes):
        """Test finding notes with any tag (OR)."""
        notes = obsidian_client.find_by_tags(
            ["topic/coaching", "type/blog"],
            match_all=False
        )
        
        assert len(notes) == 2
    
    def test_create_note(self, empty_client):
        """Test creating a new note."""
        result = empty_client.create_note(
            path="test.md",
            content="Test content",
            title="Test Note",
            tags=["topic/test", "status/draft"]
        )
        
        assert result.success is True
        assert "test.md" in result.note_path
        
        note = empty_client.get_note("test.md")
        assert note.title == "Test Note"
        assert "topic/test" in note.tags
    
    def test_create_note_in_folder(self, empty_client):
        """Test creating note in specific folder."""
        result = empty_client.create_note(
            path="note.md",
            folder="NewFolder",
            content="Content",
            tags=["tag1"]
        )
        
        assert result.success is True
        assert "NewFolder" in result.note_path
    
    def test_create_note_already_exists(self, obsidian_client, sample_notes):
        """Test creating note that already exists."""
        result = obsidian_client.create_note(
            path="note1.md",
            content="Content"
        )
        
        assert result.success is False
        assert "already exists" in result.message
    
    def test_update_note_content(self, obsidian_client, sample_notes):
        """Test updating note content."""
        result = obsidian_client.update_note(
            path="note1.md",
            content="Updated content"
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert "Updated content" in note.body
    
    def test_update_note_frontmatter_merge(self, obsidian_client, sample_notes):
        """Test updating frontmatter with merge."""
        result = obsidian_client.update_note(
            path="note1.md",
            frontmatter={"status": "active"},
            merge_frontmatter_flag=True
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert note.frontmatter['status'] == 'active'
        assert note.frontmatter['title'] == 'First Note'
    
    def test_update_section(self, obsidian_client, sample_notes):
        """Test updating specific section."""
        result = obsidian_client.update_section(
            path="note1.md",
            heading="Section 1",
            new_content="Updated section content"
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert "Updated section content" in note.body
    
    def test_append_content(self, obsidian_client, sample_notes):
        """Test appending content to note."""
        result = obsidian_client.append_content(
            path="note1.md",
            content="Appended text"
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert "Appended text" in note.body
    
    def test_move_note(self, obsidian_client, sample_notes):
        """Test moving/renaming note."""
        result = obsidian_client.move_note(
            source="note1.md",
            destination="renamed.md"
        )
        
        assert result.success is True
        assert obsidian_client.get_note("renamed.md") is not None
        assert obsidian_client.get_note("note1.md") is None
    
    def test_move_note_updates_links(self, obsidian_client, sample_notes):
        """Test that moving note updates wiki links."""
        result = obsidian_client.move_note(
            source="note2.md",
            destination="new_note2.md"
        )
        
        assert result.success is True
        
        note1 = obsidian_client.get_note("note1.md")
        assert "[[new_note2]]" in note1.body or "[[new_note2.md]]" in note1.body
    
    def test_add_tag(self, obsidian_client, sample_notes):
        """Test adding a tag."""
        result = obsidian_client.add_tag(
            path="note1.md",
            tag="topic/new-tag"
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert "topic/new-tag" in note.tags
    
    def test_add_tags_prevents_duplicates(self, obsidian_client, sample_notes):
        """Test that adding existing tag doesn't duplicate."""
        result = obsidian_client.add_tags(
            path="note1.md",
            tags=["topic/ai", "topic/new"]
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert note.tags.count("topic/ai") == 1
        assert "topic/new" in note.tags
    
    def test_remove_tag(self, obsidian_client, sample_notes):
        """Test removing a tag."""
        result = obsidian_client.remove_tag(
            path="note1.md",
            tag="status/draft"
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert "status/draft" not in note.tags
    
    def test_set_tags(self, obsidian_client, sample_notes):
        """Test replacing all tags."""
        result = obsidian_client.set_tags(
            path="note1.md",
            tags=["tag1", "tag2", "tag3"]
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert note.tags == ["tag1", "tag2", "tag3"]
    
    def test_add_link(self, obsidian_client, sample_notes):
        """Test adding wiki link."""
        result = obsidian_client.add_link(
            source_path="note1.md",
            target_note="note3"
        )
        
        assert result.success is True
        
        note = obsidian_client.get_note("note1.md")
        assert "[[note3]]" in note.body
    
    def test_create_hub_simple(self, obsidian_client, sample_notes):
        """Test creating simple hub note."""
        result = obsidian_client.create_hub(
            hub_path="hub.md",
            title="Test Hub",
            linked_notes=["note1.md", "note2.md"]
        )
        
        assert result.success is True
        
        hub = obsidian_client.get_note("hub.md")
        assert "[[note1.md]]" in hub.body
        assert "[[note2.md]]" in hub.body
    
    def test_create_hub_grouped(self, obsidian_client, sample_notes):
        """Test creating hub grouped by tag."""
        result = obsidian_client.create_hub(
            hub_path="hub.md",
            title="Grouped Hub",
            linked_notes=["note1.md", "note2.md", "Projects/project.md"],
            group_by_tag="topic"
        )
        
        assert result.success is True
        
        hub = obsidian_client.get_note("hub.md")
        assert "## topic/" in hub.body
    
    def test_read_only_mode_blocks_create(self, tmp_vault):
        """Test read-only mode blocks writes."""
        client = ObsidianClient(vault_path=str(tmp_vault), read_only=True)
        
        with pytest.raises(PermissionError, match="read-only"):
            client.create_note("test.md", "content")
    
    def test_read_only_mode_blocks_update(self, tmp_vault, sample_notes):
        """Test read-only mode blocks updates."""
        client = ObsidianClient(vault_path=str(tmp_vault), read_only=True)
        
        with pytest.raises(PermissionError, match="read-only"):
            client.update_note("note1.md", content="new")
    
    def test_path_validation_rejects_outside_vault(self, obsidian_client):
        """Test path validation rejects paths outside vault."""
        with pytest.raises(ValueError, match="outside vault"):
            obsidian_client._validate_path(Path("/etc/passwd"))
    
    def test_find_backlinks(self, obsidian_client, sample_notes):
        """Test finding backlinks."""
        backlinks = obsidian_client.find_backlinks("note2")
        
        assert len(backlinks) >= 1
        assert any(n.title == "First Note" for n in backlinks)


class TestLinkIndex:
    """Test link index functionality."""
    
    def test_link_index_builds(self, obsidian_client, sample_notes):
        """Test that link index is built on init."""
        assert obsidian_client.link_index.forward_links
        assert obsidian_client.link_index.backlinks
    
    def test_link_index_backlinks(self, obsidian_client, sample_notes):
        """Test backlink lookup."""
        backlinks = obsidian_client.link_index.get_backlinks("note2")
        
        assert len(backlinks) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
