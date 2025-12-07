"""Tests for Craft skill."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import os

from superskills.craft.src import CraftClient, CraftDocument, CraftOperationResult


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("CRAFT_API_ENDPOINT", "https://api.craft.test/v1")
    monkeypatch.setenv("CRAFT_API_KEY", "test_api_key")


@pytest.fixture
def craft_client(mock_env, tmp_path):
    """Create CraftClient instance with temp output dir."""
    return CraftClient(output_dir=str(tmp_path / "craft_exports"), verbose=False)


@pytest.fixture
def mock_document_data():
    """Mock document data from API."""
    return {
        "id": "doc_123",
        "title": "Test Document",
        "content": "# Test Content\n\nThis is a test.",
        "url": "https://craft.do/test/doc_123",
        "createdAt": "2025-01-01T10:00:00Z",
        "updatedAt": "2025-01-02T12:00:00Z",
        "spaceId": "space_456",
        "metadata": {"author": "test_user"}
    }


class TestCraftClient:
    """Test CraftClient class."""
    
    def test_init_requires_endpoint(self):
        """Test that initialization requires API endpoint."""
        with pytest.raises(ValueError, match="CRAFT_API_ENDPOINT"):
            CraftClient()
    
    def test_init_with_endpoint(self, mock_env):
        """Test initialization with endpoint."""
        client = CraftClient()
        assert client.api_endpoint == "https://api.craft.test/v1"
        assert client.api_key == "test_api_key"
    
    def test_endpoint_trailing_slash_removed(self, mock_env):
        """Test that trailing slash is removed from endpoint."""
        client = CraftClient(api_endpoint="https://api.test.com/")
        assert client.api_endpoint == "https://api.test.com"
    
    @patch('requests.Session.post')
    def test_create_document(self, mock_post, craft_client):
        """Test document creation."""
        mock_post.return_value.json.return_value = {"id": "doc_new_123"}
        mock_post.return_value.status_code = 200
        
        result = craft_client.create_document(
            title="New Document",
            content="Test content",
            space_id="space_123"
        )
        
        assert result.success is True
        assert result.operation == "create"
        assert result.document_id == "doc_new_123"
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.craft.test/v1/documents"
        assert call_args[1]["json"]["title"] == "New Document"
        assert call_args[1]["json"]["spaceId"] == "space_123"
    
    @patch('requests.Session.get')
    def test_get_document(self, mock_get, craft_client, mock_document_data):
        """Test retrieving a document."""
        mock_get.return_value.json.return_value = mock_document_data
        mock_get.return_value.status_code = 200
        
        doc = craft_client.get_document("doc_123")
        
        assert doc is not None
        assert doc.id == "doc_123"
        assert doc.title == "Test Document"
        assert doc.space_id == "space_456"
        
        mock_get.assert_called_once()
    
    @patch('requests.Session.put')
    def test_update_document(self, mock_put, craft_client):
        """Test updating a document."""
        mock_put.return_value.json.return_value = {}
        mock_put.return_value.status_code = 200
        
        result = craft_client.update_document(
            document_id="doc_123",
            title="Updated Title",
            content="Updated content"
        )
        
        assert result.success is True
        assert result.operation == "update"
        assert result.document_id == "doc_123"
        
        # Verify API call
        call_args = mock_put.call_args
        assert call_args[1]["json"]["title"] == "Updated Title"
        assert call_args[1]["json"]["content"] == "Updated content"
    
    @patch('requests.Session.delete')
    def test_delete_document(self, mock_delete, craft_client):
        """Test deleting a document."""
        mock_delete.return_value.status_code = 204
        mock_delete.return_value.content = b''
        
        result = craft_client.delete_document("doc_123")
        
        assert result.success is True
        assert result.operation == "delete"
        assert result.document_id == "doc_123"
    
    @patch('requests.Session.get')
    def test_list_documents(self, mock_get, craft_client, mock_document_data):
        """Test listing documents."""
        mock_get.return_value.json.return_value = {
            "documents": [mock_document_data, {**mock_document_data, "id": "doc_124"}]
        }
        mock_get.return_value.status_code = 200
        
        docs = craft_client.list_documents(limit=10)
        
        assert len(docs) == 2
        assert docs[0].id == "doc_123"
        assert docs[1].id == "doc_124"
        
        # Verify query params
        call_args = mock_get.call_args
        assert call_args[1]["params"]["limit"] == 10
    
    @patch('requests.Session.get')
    def test_search_documents(self, mock_get, craft_client, mock_document_data):
        """Test searching documents."""
        mock_get.return_value.json.return_value = {
            "results": [mock_document_data]
        }
        mock_get.return_value.status_code = 200
        
        results = craft_client.search_documents(query="test", limit=5)
        
        assert len(results) == 1
        assert results[0].id == "doc_123"
        
        # Verify search params
        call_args = mock_get.call_args
        assert call_args[1]["params"]["q"] == "test"
        assert call_args[1]["params"]["limit"] == 5
    
    @patch('requests.Session.post')
    def test_append_content(self, mock_post, craft_client):
        """Test appending content to document."""
        mock_post.return_value.json.return_value = {}
        mock_post.return_value.status_code = 200
        
        result = craft_client.append_content(
            document_id="doc_123",
            content="New paragraph",
            block_type="text"
        )
        
        assert result.success is True
        assert result.operation == "append_content"
        
        # Verify API call
        call_args = mock_post.call_args
        assert "blocks" in call_args[0][0]
        assert call_args[1]["json"]["content"] == "New paragraph"
    
    @patch('requests.Session.get')
    def test_export_document_markdown(self, mock_get, craft_client, mock_document_data, tmp_path):
        """Test exporting document as markdown."""
        mock_get.return_value.json.return_value = mock_document_data
        mock_get.return_value.status_code = 200
        
        file_path = craft_client.export_document("doc_123", format="markdown")
        
        assert Path(file_path).exists()
        assert file_path.endswith(".md")
        
        # Verify content
        with open(file_path, 'r') as f:
            content = f.read()
            assert "Test Document" in content
            assert "# Test Content" in content
    
    @patch('requests.Session.get')
    def test_export_document_json(self, mock_get, craft_client, mock_document_data):
        """Test exporting document as JSON."""
        mock_get.return_value.json.return_value = mock_document_data
        mock_get.return_value.status_code = 200
        
        file_path = craft_client.export_document("doc_123", format="json")
        
        assert Path(file_path).exists()
        assert file_path.endswith(".json")
        
        # Verify content
        with open(file_path, 'r') as f:
            data = json.load(f)
            assert data["id"] == "doc_123"
            assert data["title"] == "Test Document"
    
    @patch('requests.Session.get')
    def test_export_all(self, mock_get, craft_client, mock_document_data):
        """Test exporting all documents."""
        # Mock list_documents
        mock_get.return_value.json.return_value = {
            "documents": [mock_document_data, {**mock_document_data, "id": "doc_124"}]
        }
        mock_get.return_value.status_code = 200
        
        files = craft_client.export_all(format="markdown")
        
        assert len(files) == 2
        assert all(Path(f).exists() for f in files)
    
    @patch('requests.Session.post')
    def test_share_document(self, mock_post, craft_client):
        """Test sharing a document."""
        mock_post.return_value.json.return_value = {}
        mock_post.return_value.status_code = 200
        
        result = craft_client.share_document(
            document_id="doc_123",
            email="user@example.com",
            permission="read"
        )
        
        assert result.success is True
        assert result.operation == "share"
        
        # Verify API call
        call_args = mock_post.call_args
        assert call_args[1]["json"]["email"] == "user@example.com"
        assert call_args[1]["json"]["permission"] == "read"
    
    @patch('requests.Session.get')
    def test_get_document_url(self, mock_get, craft_client):
        """Test getting document URL."""
        mock_get.return_value.json.return_value = {
            "url": "https://craft.do/share/doc_123"
        }
        mock_get.return_value.status_code = 200
        
        url = craft_client.get_document_url("doc_123", public=True)
        
        assert url == "https://craft.do/share/doc_123"
        
        # Verify params
        call_args = mock_get.call_args
        assert call_args[1]["params"]["public"] == "true"
    
    @patch('requests.Session.post')
    def test_bulk_import(self, mock_post, craft_client):
        """Test bulk import of documents."""
        mock_post.return_value.json.return_value = {"id": "doc_new"}
        mock_post.return_value.status_code = 200
        
        documents = [
            {"title": "Doc 1", "content": "Content 1"},
            {"title": "Doc 2", "content": "Content 2"}
        ]
        
        results = craft_client.bulk_import(documents, space_id="space_123")
        
        assert len(results) == 2
        assert all(r.success for r in results)
        assert mock_post.call_count == 2
    
    @patch('requests.Session.post')
    def test_create_document_error_handling(self, mock_post, craft_client):
        """Test error handling in create_document."""
        mock_post.side_effect = Exception("Network error")
        
        result = craft_client.create_document(
            title="Test",
            content="Test"
        )
        
        assert result.success is False
        assert "Network error" in result.message
    
    @patch('requests.Session.get')
    def test_get_document_not_found(self, mock_get, craft_client):
        """Test handling of document not found."""
        mock_get.side_effect = Exception("404 Not Found")
        
        doc = craft_client.get_document("nonexistent")
        
        assert doc is None


class TestDataclasses:
    """Test dataclass definitions."""
    
    def test_craft_document_creation(self):
        """Test CraftDocument creation."""
        doc = CraftDocument(
            id="doc_1",
            title="Test",
            content="Content",
            url="https://craft.do/test",
            created_at="2025-01-01",
            updated_at="2025-01-02"
        )
        
        assert doc.id == "doc_1"
        assert doc.title == "Test"
        assert doc.timestamp is not None
    
    def test_craft_operation_result(self):
        """Test CraftOperationResult creation."""
        result = CraftOperationResult(
            success=True,
            operation="create",
            message="Success",
            document_id="doc_1"
        )
        
        assert result.success is True
        assert result.operation == "create"
        assert result.timestamp is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
