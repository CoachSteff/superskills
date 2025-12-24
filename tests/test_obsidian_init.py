"""
Tests for Obsidian __init__.py execute() function.

Tests the CLI execution wrapper that provides a unified interface
to all Obsidian operations.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from superskills.obsidian.src import execute


@pytest.fixture
def mock_client():
    """Create a mock ObsidianClient."""
    with patch('superskills.obsidian.src.ObsidianClient') as MockClient:
        client = MagicMock()
        MockClient.return_value = client
        yield client, MockClient


def create_mock_note():
    """Create a mock note with dict() method."""
    note = MagicMock()
    note.dict.return_value = {
        "path": "test.md",
        "title": "Test Note",
        "content": "Test content",
        "frontmatter": {},
        "tags": [],
        "links": []
    }
    return note


def create_mock_result(success=True):
    """Create a mock result with dict() method."""
    result = MagicMock()
    result.dict.return_value = {
        "success": success,
        "message": "Success"
    }
    return result


def create_mock_plan():
    """Create a mock plan with dict() method."""
    plan = MagicMock()
    plan.dict.return_value = {
        "operations": [],
        "summary": "test plan"
    }
    return plan


class TestExecuteList:
    """Test list action."""

    def test_execute_list_default(self, mock_client):
        """Test list action with default parameters."""
        client, MockClient = mock_client

        mock_note = create_mock_note()
        client.list_notes.return_value = [mock_note]

        result = execute("list", vault_path="/vault")

        MockClient.assert_called_once_with(vault_path="/vault", read_only=False)
        client.list_notes.assert_called_once_with(folder=None, recursive=True)
        assert "notes" in result
        assert len(result["notes"]) == 1

    def test_execute_list_with_folder(self, mock_client):
        """Test list action with folder parameter."""
        client, _ = mock_client

        client.list_notes.return_value = []

        result = execute("list", vault_path="/vault", folder="projects", recursive=False)

        client.list_notes.assert_called_once_with(folder="projects", recursive=False)
        assert result["notes"] == []


class TestExecuteGet:
    """Test get action."""

    def test_execute_get_success(self, mock_client):
        """Test get action with existing note."""
        client, _ = mock_client

        mock_note = create_mock_note()
        client.get_note.return_value = mock_note

        result = execute("get", vault_path="/vault", path="note.md")

        client.get_note.assert_called_once_with("note.md")
        assert result["note"]["path"] == "test.md"

    def test_execute_get_not_found(self, mock_client):
        """Test get action with non-existent note."""
        client, _ = mock_client

        client.get_note.return_value = None

        result = execute("get", vault_path="/vault", path="missing.md")

        assert result["note"] is None


class TestExecuteSearch:
    """Test search action."""

    def test_execute_search_default(self, mock_client):
        """Test search with default parameters."""
        client, _ = mock_client

        mock_note = create_mock_note()
        client.search_notes.return_value = [mock_note]

        result = execute("search", vault_path="/vault", query="matching")

        client.search_notes.assert_called_once_with(
            query="matching",
            search_in="both",
            case_sensitive=False,
            limit=50
        )
        assert len(result["results"]) == 1

    def test_execute_search_custom_params(self, mock_client):
        """Test search with custom parameters."""
        client, _ = mock_client

        client.search_notes.return_value = []

        result = execute(
            "search",
            vault_path="/vault",
            query="test",
            search_in="title",
            case_sensitive=True,
            limit=10
        )

        client.search_notes.assert_called_once_with(
            query="test",
            search_in="title",
            case_sensitive=True,
            limit=10
        )
        assert result["results"] == []


class TestExecuteTags:
    """Test tag-related actions."""

    def test_execute_find_by_tag(self, mock_client):
        """Test find_by_tag action."""
        client, _ = mock_client

        mock_note = create_mock_note()
        client.find_by_tag.return_value = [mock_note]

        result = execute("find_by_tag", vault_path="/vault", tag="project")

        client.find_by_tag.assert_called_once_with(tag="project", exact_match=False)
        assert len(result["results"]) == 1

    def test_execute_find_by_tags(self, mock_client):
        """Test find_by_tags action."""
        client, _ = mock_client

        client.find_by_tags.return_value = []

        result = execute(
            "find_by_tags",
            vault_path="/vault",
            tags=["tag1", "tag2"],
            match_all=True
        )

        client.find_by_tags.assert_called_once_with(
            tags=["tag1", "tag2"],
            match_all=True
        )
        assert result["results"] == []

    def test_execute_add_tag(self, mock_client):
        """Test add_tag action."""
        client, _ = mock_client

        mock_result = create_mock_result()
        client.add_tag.return_value = mock_result

        result = execute("add_tag", vault_path="/vault", path="note.md", tag="new-tag")

        client.add_tag.assert_called_once_with(path="note.md", tag="new-tag")
        assert result["success"]


class TestExecuteCreate:
    """Test create action."""

    def test_execute_create_minimal(self, mock_client):
        """Test create with minimal parameters."""
        client, _ = mock_client

        mock_result = create_mock_result()
        client.create_note.return_value = mock_result

        result = execute("create", vault_path="/vault", path="new.md")

        client.create_note.assert_called_once_with(
            path="new.md",
            content="",
            title=None,
            tags=None,
            frontmatter=None,
            folder=None
        )
        assert result["success"]

    def test_execute_create_full(self, mock_client):
        """Test create with all parameters."""
        client, _ = mock_client

        mock_result = create_mock_result()
        client.create_note.return_value = mock_result

        result = execute(
            "create",
            vault_path="/vault",
            path="full.md",
            content="Test content",
            title="Test Title",
            tags=["tag1", "tag2"],
            frontmatter={"key": "value"},
            folder="projects"
        )

        client.create_note.assert_called_once_with(
            path="full.md",
            content="Test content",
            title="Test Title",
            tags=["tag1", "tag2"],
            frontmatter={"key": "value"},
            folder="projects"
        )
        assert result["success"]


class TestExecuteUpdate:
    """Test update actions."""

    def test_execute_update(self, mock_client):
        """Test update action."""
        client, _ = mock_client

        mock_result = create_mock_result()
        client.update_note.return_value = mock_result

        result = execute(
            "update",
            vault_path="/vault",
            path="note.md",
            content="Updated content",
            frontmatter={"updated": True},
            merge_frontmatter=False
        )

        client.update_note.assert_called_once_with(
            path="note.md",
            content="Updated content",
            frontmatter={"updated": True},
            merge_frontmatter_flag=False
        )
        assert result["success"]

    def test_execute_append(self, mock_client):
        """Test append action."""
        client, _ = mock_client

        mock_result = create_mock_result()
        client.append_content.return_value = mock_result

        result = execute(
            "append",
            vault_path="/vault",
            path="note.md",
            content="Appended text"
        )

        client.append_content.assert_called_once_with(
            path="note.md",
            content="Appended text"
        )
        assert result["success"]


class TestExecutePlan:
    """Test plan-related actions."""

    def test_execute_plan(self, mock_client):
        """Test plan action."""
        client, _ = mock_client

        operations = [{"action": "create", "path": "new.md"}]
        mock_plan = create_mock_plan()
        client.plan_changes.return_value = mock_plan

        result = execute("plan", vault_path="/vault", operations=operations)

        client.plan_changes.assert_called_once_with(operations)
        assert "operations" in result

    def test_execute_apply_plan(self, mock_client):
        """Test apply_plan action."""
        client, _ = mock_client

        plan = {"operations": []}
        mock_results = [create_mock_result()]
        client.apply_plan.return_value = mock_results

        result = execute("apply_plan", vault_path="/vault", plan=plan)

        client.apply_plan.assert_called_once_with(plan)
        assert len(result["results"]) == 1


class TestExecuteReadOnly:
    """Test read-only mode."""

    def test_execute_with_read_only(self, mock_client):
        """Test that read_only flag is passed to client."""
        client, MockClient = mock_client

        client.list_notes.return_value = []

        execute("list", vault_path="/vault", read_only=True)

        MockClient.assert_called_once_with(vault_path="/vault", read_only=True)


class TestExecuteUnknownAction:
    """Test unknown action handling."""

    def test_execute_unknown_action(self, mock_client):
        """Test execute with unknown action."""
        result = execute("unknown_action", vault_path="/vault")

        assert not result["success"]
        assert "Unknown action" in result["message"]
        assert "available_actions" in result
        assert "list" in result["available_actions"]


def main():
    """Run tests manually."""
    print("="*60)
    print("Obsidian __init__.py Execute Tests")
    print("="*60 + "\n")

    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    main()
