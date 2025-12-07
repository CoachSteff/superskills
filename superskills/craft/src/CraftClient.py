"""
CraftClient.py - Craft Docs API integration for document management.
"""
import os
import requests
from typing import Dict, List, Optional, Literal
from pathlib import Path
from datetime import datetime
import json
from dataclasses import dataclass, field


ContentFormat = Literal["markdown", "html", "json"]
BlockType = Literal["text", "heading1", "heading2", "heading3", "bullet_list", "numbered_list", "code", "quote", "divider"]
Permission = Literal["read", "write", "admin"]


@dataclass
class CraftDocument:
    """Represents a Craft document."""
    id: str
    title: str
    content: str
    url: str
    created_at: str
    updated_at: str
    space_id: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class CraftBlock:
    """Represents a content block in a Craft document."""
    id: str
    type: str
    content: str
    style: Optional[Dict] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class CraftOperationResult:
    """Result from a Craft API operation."""
    success: bool
    operation: str
    message: str
    document_id: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class CraftClient:
    """Client for interacting with Craft Docs Imagine API."""
    
    # Supported block types
    BLOCK_TYPES = [
        "text", "heading1", "heading2", "heading3",
        "bullet_list", "numbered_list", "code", "quote", "divider",
        "image", "link", "table"
    ]
    
    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        output_dir: str = "craft_exports",
        verbose: bool = True
    ):
        """Initialize Craft API client.
        
        Args:
            api_endpoint: Craft Imagine API endpoint URL
            api_key: API authentication key (if required)
            output_dir: Directory for exported documents
            verbose: Enable verbose logging
        """
        self.api_endpoint = api_endpoint or os.getenv("CRAFT_API_ENDPOINT")
        if not self.api_endpoint:
            raise ValueError(
                "CRAFT_API_ENDPOINT environment variable not set. "
                "Get this from Craft Docs > Imagine tab > Enable API"
            )
        
        self.api_key = api_key or os.getenv("CRAFT_API_KEY")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        # Remove trailing slash from endpoint
        self.api_endpoint = self.api_endpoint.rstrip('/')
        
        # Setup session
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
        else:
            self.session.headers.update({
                "Content-Type": "application/json"
            })
    
    def create_document(
        self,
        title: str,
        content: str,
        space_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        format: ContentFormat = "markdown"
    ) -> CraftOperationResult:
        """Create a new document in Craft.
        
        Args:
            title: Document title
            content: Document content (markdown, HTML, or JSON)
            space_id: Space ID to create document in
            parent_id: Parent document ID (for nested docs)
            format: Content format (markdown, html, json)
            
        Returns:
            CraftOperationResult with creation status
        """
        if self.verbose:
            print(f"Creating document: {title}")
        
        payload = {
            "title": title,
            "content": content,
            "format": format
        }
        
        if space_id:
            payload["spaceId"] = space_id
        if parent_id:
            payload["parentId"] = parent_id
        
        try:
            response = self._make_request("POST", "/documents", data=payload)
            document_id = response.get("id") or response.get("documentId")
            
            if self.verbose:
                print(f"✓ Document created: {document_id}")
            
            return CraftOperationResult(
                success=True,
                operation="create",
                message=f"Document '{title}' created successfully",
                document_id=document_id
            )
        
        except Exception as e:
            return CraftOperationResult(
                success=False,
                operation="create",
                message=f"Failed to create document: {str(e)}"
            )
    
    def get_document(self, document_id: str) -> Optional[CraftDocument]:
        """Retrieve a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            CraftDocument or None if not found
        """
        if self.verbose:
            print(f"Fetching document: {document_id}")
        
        try:
            response = self._make_request("GET", f"/documents/{document_id}")
            return self._parse_document(response)
        
        except Exception as e:
            if self.verbose:
                print(f"Error fetching document: {e}")
            return None
    
    def update_document(
        self,
        document_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None
    ) -> CraftOperationResult:
        """Update an existing document.
        
        Args:
            document_id: Document ID to update
            content: New content (optional)
            title: New title (optional)
            
        Returns:
            CraftOperationResult with update status
        """
        if self.verbose:
            print(f"Updating document: {document_id}")
        
        payload = {}
        if content is not None:
            payload["content"] = content
        if title is not None:
            payload["title"] = title
        
        if not payload:
            return CraftOperationResult(
                success=False,
                operation="update",
                message="No updates provided",
                document_id=document_id
            )
        
        try:
            self._make_request("PUT", f"/documents/{document_id}", data=payload)
            
            if self.verbose:
                print(f"✓ Document updated: {document_id}")
            
            return CraftOperationResult(
                success=True,
                operation="update",
                message="Document updated successfully",
                document_id=document_id
            )
        
        except Exception as e:
            return CraftOperationResult(
                success=False,
                operation="update",
                message=f"Failed to update document: {str(e)}",
                document_id=document_id
            )
    
    def delete_document(self, document_id: str) -> CraftOperationResult:
        """Delete a document.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            CraftOperationResult with deletion status
        """
        if self.verbose:
            print(f"Deleting document: {document_id}")
        
        try:
            self._make_request("DELETE", f"/documents/{document_id}")
            
            if self.verbose:
                print(f"✓ Document deleted: {document_id}")
            
            return CraftOperationResult(
                success=True,
                operation="delete",
                message="Document deleted successfully",
                document_id=document_id
            )
        
        except Exception as e:
            return CraftOperationResult(
                success=False,
                operation="delete",
                message=f"Failed to delete document: {str(e)}",
                document_id=document_id
            )
    
    def list_documents(
        self,
        space_id: Optional[str] = None,
        limit: int = 50
    ) -> List[CraftDocument]:
        """List documents.
        
        Args:
            space_id: Filter by space ID (optional)
            limit: Maximum number of documents to return
            
        Returns:
            List of CraftDocument objects
        """
        if self.verbose:
            print(f"Listing documents (limit: {limit})")
        
        params = {"limit": limit}
        if space_id:
            params["spaceId"] = space_id
        
        try:
            response = self._make_request("GET", "/documents", params=params)
            
            # Handle different response formats
            if isinstance(response, list):
                documents = response
            elif isinstance(response, dict) and "documents" in response:
                documents = response["documents"]
            elif isinstance(response, dict) and "data" in response:
                documents = response["data"]
            else:
                documents = []
            
            results = [self._parse_document(doc) for doc in documents]
            
            if self.verbose:
                print(f"✓ Found {len(results)} documents")
            
            return results
        
        except Exception as e:
            if self.verbose:
                print(f"Error listing documents: {e}")
            return []
    
    def search_documents(
        self,
        query: str,
        space_id: Optional[str] = None,
        limit: int = 20
    ) -> List[CraftDocument]:
        """Search for documents.
        
        Args:
            query: Search query
            space_id: Filter by space ID (optional)
            limit: Maximum results
            
        Returns:
            List of matching CraftDocument objects
        """
        if self.verbose:
            print(f"Searching documents: '{query}'")
        
        params = {"q": query, "limit": limit}
        if space_id:
            params["spaceId"] = space_id
        
        try:
            response = self._make_request("GET", "/search", params=params)
            
            # Handle different response formats
            if isinstance(response, list):
                documents = response
            elif isinstance(response, dict) and "results" in response:
                documents = response["results"]
            else:
                documents = []
            
            results = [self._parse_document(doc) for doc in documents]
            
            if self.verbose:
                print(f"✓ Found {len(results)} matching documents")
            
            return results
        
        except Exception as e:
            if self.verbose:
                print(f"Error searching documents: {e}")
            return []
    
    def append_content(
        self,
        document_id: str,
        content: str,
        block_type: BlockType = "text"
    ) -> CraftOperationResult:
        """Append content to a document.
        
        Args:
            document_id: Document ID
            content: Content to append
            block_type: Type of content block
            
        Returns:
            CraftOperationResult with operation status
        """
        if self.verbose:
            print(f"Appending content to document: {document_id}")
        
        payload = {
            "content": content,
            "blockType": block_type,
            "position": "end"
        }
        
        try:
            self._make_request("POST", f"/documents/{document_id}/blocks", data=payload)
            
            if self.verbose:
                print(f"✓ Content appended to document: {document_id}")
            
            return CraftOperationResult(
                success=True,
                operation="append_content",
                message="Content appended successfully",
                document_id=document_id
            )
        
        except Exception as e:
            return CraftOperationResult(
                success=False,
                operation="append_content",
                message=f"Failed to append content: {str(e)}",
                document_id=document_id
            )
    
    def export_document(
        self,
        document_id: str,
        format: ContentFormat = "markdown",
        output_filename: Optional[str] = None
    ) -> str:
        """Export a document to file.
        
        Args:
            document_id: Document ID to export
            format: Export format (markdown, html, json)
            output_filename: Custom filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if self.verbose:
            print(f"Exporting document: {document_id} as {format}")
        
        doc = self.get_document(document_id)
        if not doc:
            raise ValueError(f"Document not found: {document_id}")
        
        # Generate filename
        if not output_filename:
            safe_title = "".join(c for c in doc.title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '-')[:50]
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            
            if format == "markdown":
                ext = "md"
            elif format == "html":
                ext = "html"
            else:
                ext = "json"
            
            output_filename = f"{timestamp}-{safe_title}.{ext}"
        
        output_path = self.output_dir / output_filename
        
        # Save content
        if format == "json":
            data = {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "url": doc.url,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at,
                "space_id": doc.space_id,
                "metadata": doc.metadata
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            content = doc.content
            if format == "markdown" and not doc.content.startswith('#'):
                content = f"# {doc.title}\n\n{doc.content}"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        if self.verbose:
            print(f"✓ Document exported: {output_path}")
        
        return str(output_path)
    
    def export_all(
        self,
        space_id: Optional[str] = None,
        format: ContentFormat = "markdown"
    ) -> List[str]:
        """Export all documents to files.
        
        Args:
            space_id: Filter by space ID (optional)
            format: Export format
            
        Returns:
            List of exported file paths
        """
        if self.verbose:
            print("Exporting all documents...")
        
        documents = self.list_documents(space_id=space_id)
        exported_files = []
        
        for doc in documents:
            try:
                file_path = self.export_document(doc.id, format=format)
                exported_files.append(file_path)
            except Exception as e:
                if self.verbose:
                    print(f"Error exporting {doc.id}: {e}")
        
        if self.verbose:
            print(f"✓ Exported {len(exported_files)} documents")
        
        return exported_files
    
    def share_document(
        self,
        document_id: str,
        email: str,
        permission: Permission = "read"
    ) -> CraftOperationResult:
        """Share a document with a user.
        
        Args:
            document_id: Document ID to share
            email: Email of user to share with
            permission: Permission level (read, write, admin)
            
        Returns:
            CraftOperationResult with share status
        """
        if self.verbose:
            print(f"Sharing document {document_id} with {email} ({permission})")
        
        payload = {
            "email": email,
            "permission": permission
        }
        
        try:
            self._make_request("POST", f"/documents/{document_id}/share", data=payload)
            
            if self.verbose:
                print(f"✓ Document shared with {email}")
            
            return CraftOperationResult(
                success=True,
                operation="share",
                message=f"Document shared with {email}",
                document_id=document_id
            )
        
        except Exception as e:
            return CraftOperationResult(
                success=False,
                operation="share",
                message=f"Failed to share document: {str(e)}",
                document_id=document_id
            )
    
    def get_document_url(
        self,
        document_id: str,
        public: bool = False
    ) -> str:
        """Get shareable URL for a document.
        
        Args:
            document_id: Document ID
            public: Generate public URL (if False, requires auth)
            
        Returns:
            Document URL
        """
        try:
            params = {"public": str(public).lower()}
            response = self._make_request("GET", f"/documents/{document_id}/url", params=params)
            
            return response.get("url", f"{self.api_endpoint}/documents/{document_id}")
        
        except Exception as e:
            if self.verbose:
                print(f"Error getting document URL: {e}")
            return f"{self.api_endpoint}/documents/{document_id}"
    
    def bulk_import(
        self,
        documents: List[Dict],
        space_id: Optional[str] = None
    ) -> List[CraftOperationResult]:
        """Import multiple documents at once.
        
        Args:
            documents: List of document dicts with 'title' and 'content'
            space_id: Space ID to import into
            
        Returns:
            List of CraftOperationResult objects
        """
        if self.verbose:
            print(f"Bulk importing {len(documents)} documents...")
        
        results = []
        for doc_data in documents:
            result = self.create_document(
                title=doc_data.get("title", "Untitled"),
                content=doc_data.get("content", ""),
                space_id=space_id,
                format=doc_data.get("format", "markdown")
            )
            results.append(result)
        
        successful = sum(1 for r in results if r.success)
        if self.verbose:
            print(f"✓ Imported {successful}/{len(documents)} documents")
        
        return results
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to Craft API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dict
        """
        url = f"{self.api_endpoint}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, params=params, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, params=params, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {}
            
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {str(e)}")
    
    def _parse_document(self, data: Dict) -> CraftDocument:
        """Parse API response into CraftDocument.
        
        Args:
            data: Document data from API
            
        Returns:
            CraftDocument object
        """
        return CraftDocument(
            id=data.get("id", ""),
            title=data.get("title", "Untitled"),
            content=data.get("content", ""),
            url=data.get("url", ""),
            created_at=data.get("createdAt") or data.get("created_at", ""),
            updated_at=data.get("updatedAt") or data.get("updated_at", ""),
            space_id=data.get("spaceId") or data.get("space_id"),
            parent_id=data.get("parentId") or data.get("parent_id"),
            metadata=data.get("metadata", {})
        )
