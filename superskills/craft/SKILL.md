---
name: craft
description: Craft Docs API integration for document management, collaboration, and knowledge organization. Use when managing documentation, syncing content, or organizing knowledge bases.
version: 1.0.0
---

# Craft

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific Craft workspace configuration and content organization preferences.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

Seamlessly integrate with Craft Docs for document management, content collaboration, and knowledge base organization.

## Tools

**CraftClient.py** (in src/):
- Full CRUD operations (create, read, update, delete documents)
- Search and discovery across documents
- Export in multiple formats (Markdown, HTML, JSON)
- Collaboration and sharing
- Batch import/export operations
- Space management and organization
- Rich content support (text, headings, lists, code, tables)

## Core Workflow

### 1. Document Operations
- Connect to Craft Docs via Imagine API
- Create, retrieve, update, or delete documents
- Organize documents in spaces
- Search across document library

### 2. Content Sync
- Export documents for backup or migration
- Import content from external sources
- Batch operations for multiple documents
- Maintain document structure and formatting

### 3. Delivery
- Export in appropriate format (Markdown, JSON, HTML)
- Share documents with collaborators
- Integrate with downstream workflows
- Archive or version control via exports

## Usage

**Create Document:**
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

**Retrieve Document:**
```python
doc = craft.get_document("document_id")
print(f"Title: {doc.title}")
print(f"Content:\n{doc.content}")
```

**Search Documents:**
```python
results = craft.search_documents(
    query="training materials",
    limit=10
)

for doc in results:
    print(f"{doc.title}: {doc.url}")
```

**Export Documents:**
```python
# Export single document
file_path = craft.export_document(
    document_id="doc_123",
    format="markdown"
)

# Export all documents (backup)
files = craft.export_all(space_id="my_space", format="json")
print(f"Exported {len(files)} documents")
```

## Environment Variables

```bash
# Required: Craft Docs Imagine API endpoint
CRAFT_API_ENDPOINT=https://api.craft.do/v1/your-endpoint

# Optional: API key if required
CRAFT_API_KEY=your_api_key
```

**Setup Instructions:**
1. Open Craft Docs application
2. Navigate to **Imagine** tab
3. Click **"Enable API"**
4. Select accessible documents/spaces
5. Copy provided API endpoint
6. Add to `.env` file

## Quality Checklist

- [ ] API endpoint configured correctly
- [ ] Document access permissions granted
- [ ] Content formatted in markdown
- [ ] Metadata preserved (title, dates, space)
- [ ] Exports backed up regularly
- [ ] Search queries return expected results
- [ ] Collaboration settings appropriate

## Avoid

- **Hardcoded Credentials**: API keys in code → Use environment variables
- **Skipping Backups**: Live docs only → Regular exports for version control
- **Poor Organization**: Flat structure → Use spaces for project organization
- **Missing Metadata**: Generic titles → Descriptive, searchable document titles
- **No Error Handling**: Assume success → Check result.success before proceeding

## Escalate When

- API endpoint changes or becomes invalid
- Document permissions need adjustment
- Rate limiting issues encountered
- Need advanced features (custom blocks, media)
- Collaboration conflicts arise

## Integration Examples

**With Transcriber (Training Sessions):**
```python
from superskills.craft.src import CraftClient
from superskills.transcriber.src import Transcriber

transcriber = Transcriber()
result = transcriber.transcribe("training_session.mp4")

craft = CraftClient()
craft.create_document(
    title=f"Training Session - {datetime.now().strftime('%Y-%m-%d')}",
    content=f"# Session Transcript\n\n{result.transcript}",
    space_id="training_materials"
)
```

**With Author (Content Export):**
```python
from superskills.craft.src import CraftClient
from superskills.author.src import ContentWriter

craft = CraftClient()
doc = craft.get_document("long_article_id")

writer = ContentWriter()
summary = writer.summarize(doc.content)

craft.create_document(
    title=f"Summary: {doc.title}",
    content=summary.summary,
    parent_id=doc.id
)
```

**With EmailCampaigner (Campaign Drafts):**
```python
from superskills.craft.src import CraftClient
from superskills.emailcampaigner.src import EmailCampaigner

craft = CraftClient()
emailer = EmailCampaigner()

doc = craft.get_document("email_campaign_draft")

emailer.send_campaign(
    recipient_list=["student1@example.com"],
    subject=doc.title,
    body=doc.content
)
```
