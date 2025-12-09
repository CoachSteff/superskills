---
name: knowledgebase
description: Knowledge management and documentation organization system. Use when building internal wikis, organizing documentation, or managing institutional knowledge.
---

# Knowledge Base

Organize, search, and manage institutional knowledge with a structured documentation system for FAQs, guides, and reference materials.

## Tools

**KnowledgeBase.py** (in src/):
- Article creation and management
- Category and tag organization
- Full-text search capabilities
- Version tracking
- Related content linking
- Export and backup
- Markdown-based content storage

## Core Workflow

### 1. Content Organization
- Create knowledge base structure (categories, tags)
- Define article hierarchy and relationships
- Establish naming and formatting conventions
- Plan search and navigation

### 2. Article Management
- Create new articles from content
- Update existing documentation
- Tag and categorize for discoverability
- Link related articles
- Track versions and changes

### 3. Search & Retrieval
- Full-text search across all articles
- Filter by category or tag
- Browse by topic hierarchy
- Export selected content
- Generate knowledge maps

## Usage

**Create Article:**
```python
from superskills.knowledgebase.src import KnowledgeBase

kb = KnowledgeBase(base_dir="knowledge_base")

article = kb.create_article(
    title="Getting Started with SuperSkills",
    content="# Introduction\n\nSuperSkills is...",
    category="tutorials",
    tags=["beginner", "setup", "quickstart"]
)

print(f"Article created: {article.id}")
```

**Search Articles:**
```python
results = kb.search(
    query="API configuration",
    category="technical",
    limit=10
)

for article in results:
    print(f"{article.title} - Score: {article.relevance_score}")
```

**Get Related Articles:**
```python
article = kb.get_article("getting-started")
related = kb.get_related(article.id, limit=5)

for rel in related:
    print(f"Related: {rel.title}")
```

**Export Category:**
```python
articles = kb.export_category(
    category="troubleshooting",
    format="markdown"
)

print(f"Exported {len(articles)} troubleshooting articles")
```

**Update Article:**
```python
kb.update_article(
    article_id="getting-started",
    content="# Updated Introduction\n\nNew content...",
    tags=["beginner", "setup", "quickstart", "updated"]
)
```

## Environment Variables

```bash
# No API keys required - local file-based system
# Optional: Configure storage settings in config/knowledgebase_config.yaml
```

## Quality Checklist

- [ ] Articles properly categorized
- [ ] Tags descriptive and consistent
- [ ] Related articles linked
- [ ] Search returns relevant results
- [ ] Content up-to-date
- [ ] Backup/export performed regularly
- [ ] Formatting consistent (markdown)

## Avoid

- **Poor Organization**: Flat structure → Hierarchical categories and tags
- **Missing Search**: Manual browsing only → Implement full-text search
- **Stale Content**: Set and forget → Regular reviews and updates
- **No Linking**: Isolated articles → Link related content
- **Inconsistent Format**: Mixed styles → Standardize on markdown

## Escalate When

- Need advanced search (fuzzy matching, AI-powered)
- Require access control and permissions
- Need multi-language support
- Want real-time collaboration
- Need integration with external systems

## Integration Examples

**With Craft (Sync Knowledge Base):**
```python
from superskills.craft.src import CraftClient
from superskills.knowledgebase.src import KnowledgeBase

craft = CraftClient()
kb = KnowledgeBase()

# Import from Craft
docs = craft.search_documents(query="technical support", limit=50)

for doc in docs:
    kb.create_article(
        title=doc.title,
        content=doc.content,
        category="technical_support",
        tags=["imported", "craft"]
    )
```

**With Scraper (Import Web Documentation):**
```python
from superskills.scraper.src import scrape_urls
from superskills.knowledgebase.src import KnowledgeBase

urls = [
    "https://docs.example.com/api",
    "https://docs.example.com/guides"
]

results = scrape_urls(urls)
kb = KnowledgeBase()

for result in results:
    kb.create_article(
        title=result.title,
        content=result.content,
        category="external_docs",
        tags=["api", "documentation"]
    )
```

**With Author (Generate FAQ):**
```python
from superskills.author.src import ContentWriter
from superskills.knowledgebase.src import KnowledgeBase

writer = ContentWriter()
faq = writer.create_faq(
    topic="SuperSkills CLI",
    questions=10
)

kb = KnowledgeBase()
kb.create_article(
    title="SuperSkills CLI - FAQ",
    content=faq,
    category="faqs",
    tags=["cli", "frequently-asked"]
)
```

## Features

**Organization**: Categories, tags, hierarchies  
**Search**: Full-text, filtered, ranked  
**Versioning**: Track changes over time  
**Linking**: Connect related articles  
**Export**: Backup and distribution  
**Analytics**: Track popular content  

## Storage Structure

```
knowledge_base/
├── articles/
│   ├── getting-started.md
│   ├── api-reference.md
│   └── troubleshooting.md
├── categories/
│   ├── tutorials/
│   ├── technical/
│   └── faqs/
├── metadata/
│   └── index.json
└── backups/
```
