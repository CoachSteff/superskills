# Craft SuperSkill - Quick Reference

## Installation

```bash
pip install requests python-dotenv
```

## Setup

```bash
# 1. Enable Imagine API in Craft Docs app
# 2. Download AI Bundle and get endpoint URL
# 3. Set environment variable
export CRAFT_API_ENDPOINT="https://api.craft.do/v1/your-endpoint"
```

## Quick Start

```python
from superskills.craft.src import CraftClient

craft = CraftClient()
```

## Core Operations

### Create Document
```python
result = craft.create_document(
    title="Document Title",
    content="# Content\n\nYour markdown here...",
    space_id="optional_space_id"
)
print(result.document_id)  # "doc_123"
```

### Get Document
```python
doc = craft.get_document("doc_123")
print(doc.title)
print(doc.content)
```

### Update Document
```python
craft.update_document(
    document_id="doc_123",
    title="New Title",
    content="Updated content"
)
```

### Delete Document
```python
craft.delete_document("doc_123")
```

### List Documents
```python
docs = craft.list_documents(limit=50)
for doc in docs:
    print(f"{doc.title}: {doc.url}")
```

### Search
```python
results = craft.search_documents("training materials", limit=10)
```

## Export

### Export Single Document
```python
# Markdown
file_path = craft.export_document("doc_123", format="markdown")

# JSON
file_path = craft.export_document("doc_123", format="json")

# HTML
file_path = craft.export_document("doc_123", format="html")
```

### Export All
```python
files = craft.export_all(space_id="my_space", format="markdown")
print(f"Exported {len(files)} files")
```

## Collaboration

### Share Document
```python
craft.share_document(
    document_id="doc_123",
    email="colleague@example.com",
    permission="read"  # or "write", "admin"
)
```

### Get Shareable URL
```python
url = craft.get_document_url("doc_123", public=True)
```

## Batch Operations

### Bulk Import
```python
documents = [
    {"title": "Doc 1", "content": "Content 1"},
    {"title": "Doc 2", "content": "Content 2"},
    {"title": "Doc 3", "content": "Content 3"}
]

results = craft.bulk_import(documents, space_id="my_space")
successful = sum(r.success for r in results)
print(f"Imported {successful}/{len(documents)}")
```

## Integration Snippets

### With Transcriber
```python
from superskills.transcriber.src import Transcriber

transcriber = Transcriber()
transcript = transcriber.transcribe("video.mp4")

craft.create_document(
    title="Video Transcript",
    content=transcript.transcript
)
```

### With SummarizAIer
```python
from superskills.summarizaier.src import SummarizAIer

summarizer = SummarizAIer()
doc = craft.get_document("long_doc_id")

summary = summarizer.summarize(doc.content)
craft.create_document(
    title=f"Summary: {doc.title}",
    content=summary.summary,
    parent_id=doc.id
)
```

### With KnowledgeBase
```python
from superskills.knowledgebase.src import KnowledgeBase

kb = KnowledgeBase()
articles = kb.get_all_articles()

craft.bulk_import([
    {"title": a.question, "content": a.answer}
    for a in articles
])
```

## Error Handling

```python
result = craft.create_document(title="Test", content="Test")

if result.success:
    print(f"✓ Created: {result.document_id}")
else:
    print(f"✗ Error: {result.message}")
```

## Environment Variables

```bash
CRAFT_API_ENDPOINT=https://api.craft.do/v1/your-endpoint  # Required
CRAFT_API_KEY=your_api_key                                 # Optional
```

## Common Patterns

### Export for Backup
```python
import schedule

def backup_craft_docs():
    craft = CraftClient(output_dir="backups/craft")
    files = craft.export_all(format="json")
    print(f"Backed up {len(files)} documents")

# Run daily
schedule.every().day.at("02:00").do(backup_craft_docs)
```

### Sync from External Source
```python
import requests

def sync_blog_to_craft():
    craft = CraftClient()
    
    # Fetch blog posts
    posts = requests.get("https://myblog.com/api/posts").json()
    
    # Import to Craft
    documents = [
        {"title": post["title"], "content": post["content"]}
        for post in posts
    ]
    
    craft.bulk_import(documents, space_id="blog_space")

sync_blog_to_craft()
```

### Generate Reports
```python
from datetime import datetime

craft = CraftClient()

# Fetch all docs
docs = craft.list_documents()

# Create summary report
report = f"""# Craft Docs Report - {datetime.now().strftime('%Y-%m-%d')}

Total Documents: {len(docs)}

## Recent Updates
"""

for doc in sorted(docs, key=lambda d: d.updated_at, reverse=True)[:10]:
    report += f"- **{doc.title}** (updated: {doc.updated_at})\n"

craft.create_document(
    title=f"Report - {datetime.now().strftime('%Y-%m-%d')}",
    content=report
)
```

## Tips

1. **Use Spaces** - Organize documents into spaces for better structure
2. **Markdown First** - Use markdown format for portability
3. **Regular Exports** - Backup important documents regularly
4. **Batch Operations** - Use `bulk_import()` for efficiency
5. **Error Handling** - Always check `result.success` before proceeding

## Support

- **README**: Full documentation in `superskills/craft/README.md`
- **Tests**: See `tests/test_craft.py` for usage examples
- **Craft Docs**: https://support.craft.do
- **Imagine API**: https://www.craft.do/imagine/guide/api
