# Craft SuperSkill 📝

Craft Docs API integration for document management, collaboration, and knowledge organization.

## Features

- **Full CRUD Operations**: Create, read, update, delete documents
- **Search & Discovery**: Powerful document search
- **Export & Sync**: Export documents in multiple formats (Markdown, HTML, JSON)
- **Collaboration**: Share documents with team members
- **Batch Operations**: Import/export multiple documents
- **Space Management**: Organize documents in spaces
- **Rich Content**: Support for multiple block types (text, headings, lists, code, etc.)

## Installation

```bash
pip install requests python-dotenv
```

## Authentication Setup

### Step 1: Enable Imagine API in Craft

1. Open Craft Docs application
2. Navigate to the **Imagine** tab
3. Click **"Enable API"**
4. Select which documents/spaces to grant API access

### Step 2: Get API Endpoint

1. After enabling, Craft provides an API endpoint URL
2. Download the **"AI Bundle"** (contains API docs + endpoint)
3. Copy the endpoint URL

### Step 3: Configure Environment

```bash
export CRAFT_API_ENDPOINT="<your_endpoint_from_imagine>"
# If API key is provided separately:
export CRAFT_API_KEY="<your_api_key>"
```

Or create a `.env` file:
```env
CRAFT_API_ENDPOINT=https://api.craft.do/v1/your-endpoint
CRAFT_API_KEY=your_api_key_here
```

### Step 4: Test Connection

```python
from superskills.craft.src import CraftClient

craft = CraftClient()
docs = craft.list_documents()
print(f"Found {len(docs)} documents")
```

## Quick Start

### Create a Document

```python
from superskills.craft.src import CraftClient

craft = CraftClient()

result = craft.create_document(
    title="Meeting Notes - Dec 2025",
    content="# Agenda\n\n1. Project updates\n2. Q&A",
    space_id="my_space_id"
)

print(f"Document created: {result.document_id}")
```

### Retrieve a Document

```python
doc = craft.get_document("document_id")
print(f"Title: {doc.title}")
print(f"Content:\n{doc.content}")
```

### Update a Document

```python
result = craft.update_document(
    document_id="doc_123",
    title="Updated Title",
    content="# New Content\n\nUpdated information..."
)
```

### Search Documents

```python
results = craft.search_documents(
    query="training materials",
    limit=10
)

for doc in results:
    print(f"{doc.title}: {doc.url}")
```

### Export Documents

```python
# Export single document
file_path = craft.export_document(
    document_id="doc_123",
    format="markdown"
)

# Export all documents
files = craft.export_all(space_id="my_space", format="json")
print(f"Exported {len(files)} documents")
```

## API Reference

### CraftClient

**Constructor:**
```python
CraftClient(
    api_endpoint=None,    # Optional: override env var
    api_key=None,         # Optional: override env var
    output_dir="craft_exports",
    verbose=True
)
```

**Document Management:**

- `create_document(title, content, space_id=None, parent_id=None, format="markdown")` → CraftOperationResult
- `get_document(document_id)` → CraftDocument
- `update_document(document_id, content=None, title=None)` → CraftOperationResult
- `delete_document(document_id)` → CraftOperationResult
- `list_documents(space_id=None, limit=50)` → List[CraftDocument]

**Search & Discovery:**

- `search_documents(query, space_id=None, limit=20)` → List[CraftDocument]

**Content Operations:**

- `append_content(document_id, content, block_type="text")` → CraftOperationResult

**Export & Import:**

- `export_document(document_id, format="markdown", output_filename=None)` → str (file path)
- `export_all(space_id=None, format="markdown")` → List[str]
- `bulk_import(documents, space_id=None)` → List[CraftOperationResult]

**Collaboration:**

- `share_document(document_id, email, permission="read")` → CraftOperationResult
- `get_document_url(document_id, public=False)` → str

### CraftDocument

**Attributes:**
- `id`: Document ID
- `title`: Document title
- `content`: Document content (markdown/HTML)
- `url`: Document URL
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `space_id`: Parent space ID
- `parent_id`: Parent document ID
- `metadata`: Additional metadata
- `timestamp`: ISO timestamp

### CraftOperationResult

**Attributes:**
- `success`: Operation success status
- `operation`: Operation type (create, update, delete, etc.)
- `message`: Status message
- `document_id`: Related document ID
- `timestamp`: ISO timestamp

## Integration Examples

### 1. Training Session Documentation

```python
from superskills.craft.src import CraftClient
from superskills.transcriber.src import Transcriber

# Transcribe training session
transcriber = Transcriber()
result = transcriber.transcribe("training_session.mp4")

# Save to Craft
craft = CraftClient()
craft.create_document(
    title=f"Training Session - {datetime.now().strftime('%Y-%m-%d')}",
    content=f"# Session Transcript\n\n{result.transcript}",
    space_id="training_materials"
)
```

### 2. Knowledge Base Sync

```python
from superskills.craft.src import CraftClient
from superskills.knowledgebase.src import KnowledgeBase

kb = KnowledgeBase()
craft = CraftClient()

# Get all FAQs
articles = kb.get_all_articles(category="technical_support")

# Import to Craft
documents = [
    {"title": article.question, "content": article.answer}
    for article in articles
]

results = craft.bulk_import(documents, space_id="faq_space")
print(f"Imported {sum(r.success for r in results)} FAQs")
```

### 3. Content Summarization

```python
from superskills.craft.src import CraftClient
from superskills.summarizaier.src import SummarizAIer

craft = CraftClient()
summarizer = SummarizAIer()

# Fetch long document
doc = craft.get_document("long_article_id")

# Create summary
summary = summarizer.summarize(doc.content, summary_type="executive")

# Save summary back to Craft
craft.create_document(
    title=f"Summary: {doc.title}",
    content=summary.summary,
    parent_id=doc.id
)
```

### 4. Email Campaign Drafting

```python
from superskills.craft.src import CraftClient
from superskills.emailcampaigner.src import EmailCampaigner

craft = CraftClient()
emailer = EmailCampaigner()

# Draft campaign in Craft
doc = craft.get_document("email_campaign_draft")

# Send campaign
emailer.send_campaign(
    recipient_list=["student1@example.com", "student2@example.com"],
    subject=doc.title,
    body=doc.content
)
```

### 5. Course Material Generation

```python
from superskills.craft.src import CraftClient
from superskills.presenter.src import Presenter

craft = CraftClient()
presenter = Presenter()

# Fetch course outline from Craft
doc = craft.get_document("course_outline_id")

# Generate presentation
presenter.create_from_markdown(
    doc.content,
    template="professional"
)
```

### 6. Batch Export for Backup

```python
from superskills.craft.src import CraftClient

craft = CraftClient(output_dir="backup/craft_docs")

# Export everything
files = craft.export_all(format="json")

print(f"Backed up {len(files)} documents")
```

## Supported Block Types

- `text` - Plain text paragraphs
- `heading1`, `heading2`, `heading3` - Headings
- `bullet_list`, `numbered_list` - Lists
- `code` - Code blocks
- `quote` - Blockquotes
- `divider` - Horizontal rules
- `image` - Images
- `link` - Hyperlinks
- `table` - Tables

## Environment Variables

```bash
# Required
CRAFT_API_ENDPOINT=https://api.craft.do/v1/your-endpoint

# Optional (if API requires key-based auth)
CRAFT_API_KEY=your_api_key
```

## Configuration

Edit `config/craft_config.yaml`:

```yaml
api:
  timeout: 30
  retry_attempts: 3

content:
  default_format: "markdown"
  
export:
  include_metadata: true
  output_formats: ["md", "json", "html"]

search:
  default_limit: 50
  max_results: 100
```

## Best Practices

1. **Use Spaces for Organization**: Create separate spaces for different projects
2. **Markdown for Portability**: Use markdown format for easy migration
3. **Regular Exports**: Backup important documents regularly
4. **Descriptive Titles**: Use clear, searchable document titles
5. **Metadata Tags**: Leverage metadata for better organization
6. **Version Control**: Keep important documents in version control via exports

## Error Handling

```python
from superskills.craft.src import CraftClient

craft = CraftClient()

# Check operation success
result = craft.create_document(
    title="Test Document",
    content="Test content"
)

if result.success:
    print(f"✓ Created: {result.document_id}")
else:
    print(f"✗ Failed: {result.message}")
```

## Troubleshooting

### API Endpoint Not Set

```bash
# Set environment variable
export CRAFT_API_ENDPOINT="<your_endpoint>"
```

### Authentication Error

1. Verify API endpoint is correct
2. Check if API key is required and set
3. Ensure selected documents/spaces are accessible

### Document Not Found

- Verify document ID is correct
- Check if document is in an accessible space
- Ensure API has permission to access the document

### Rate Limiting

If you encounter rate limits:
- Add delays between batch operations
- Reduce `limit` parameter in list/search operations
- Contact Craft support for higher limits

## Version

1.0.0

## License

MIT

## Support

- **Craft Docs Help**: https://support.craft.do
- **Craft Imagine API**: https://www.craft.do/imagine/guide/api
- **GitHub Issues**: Report bugs or request features

---

Built with ❤️ for seamless Craft Docs integration
