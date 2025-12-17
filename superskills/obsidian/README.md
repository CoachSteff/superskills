# Obsidian SuperSkill - Filesystem Vault Manager

Filesystem-based Obsidian vault manager for reading, writing, searching, and organizing Markdown notes with hierarchical tag taxonomy support.

## Features

- **Full CRUD Operations**: Create, read, update notes (delete intentionally omitted for safety)
- **Advanced Search**: Text search, hierarchical tag filtering, folder navigation, backlink discovery
- **Tag Management**: Add/remove hierarchical tags (topic/ai, status/draft, type/blog)
- **Wiki Link Management**: Extract links, auto-update on move/rename, add connections
- **Hub Note Creation**: Generate index notes grouped by tag categories
- **Frontmatter Support**: Parse and manipulate YAML frontmatter with auto-timestamps
- **Read-Only Mode**: Safe exploration without modifying vault
- **Path Validation**: Security checks prevent vault escape
- **Change Planning**: Dry-run mode to preview operations

## Installation

No additional dependencies beyond SuperSkills core requirements:

```bash
# Already included in requirements.txt
pyyaml>=6.0.0
python-dotenv>=1.0.0
```

## Configuration

### Step 1: Set Vault Path

Create `.env` file in `superskills/obsidian/`:

```bash
# Required: Absolute path to your Obsidian vault
OBSIDIAN_VAULT_PATH=/Users/username/Documents/Obsidian Vault

# Optional: Enable read-only mode (default: false)
OBSIDIAN_READ_ONLY=false

# Optional: Auto-update wiki links on move (default: true)
OBSIDIAN_AUTO_UPDATE_LINKS=true

# Optional: Verbose logging (default: true)
OBSIDIAN_VERBOSE=true
```

### Step 2: Verify Setup

```bash
# List all notes (read-only operation)
superskills call obsidian '{"action": "list"}'
```

## Quick Start

### List Notes

```bash
# List all notes in vault
superskills call obsidian '{"action": "list"}'

# List notes in specific folder
superskills call obsidian '{"action": "list", "folder": "Projects"}'

# Non-recursive (folder only, no subfolders)
superskills call obsidian '{"action": "list", "folder": "Inbox", "recursive": false}'
```

### Get Note

```bash
# By path
superskills call obsidian '{"action": "get", "path": "Projects/AI Strategy.md"}'

# By title (searches entire vault)
superskills call obsidian '{"action": "get", "path": "AI Strategy"}'
```

### Search Notes

```bash
# Search in content and titles
superskills call obsidian '{"action": "search", "query": "AI adoption", "search_in": "both"}'

# Search in titles only
superskills call obsidian '{"action": "search", "query": "Strategy", "search_in": "title"}'

# Case-sensitive search
superskills call obsidian '{"action": "search", "query": "API", "case_sensitive": true}'
```

### Find by Tag

```bash
# Exact tag match
superskills call obsidian '{"action": "find_by_tag", "tag": "topic/ai", "exact_match": true}'

# Hierarchical match (finds all topic/ai, topic/ai-adoption, topic/ai-tools, etc.)
superskills call obsidian '{"action": "find_by_tag", "tag": "topic/ai", "exact_match": false}'

# Find all notes with any topic tag
superskills call obsidian '{"action": "find_by_tag", "tag": "topic"}'

# Multiple tags (AND logic - must have all)
superskills call obsidian '{
  "action": "find_by_tags",
  "tags": ["topic/coaching", "status/active"],
  "match_all": true
}'

# Multiple tags (OR logic - has any)
superskills call obsidian '{
  "action": "find_by_tags",
  "tags": ["topic/ai", "topic/coaching"],
  "match_all": false
}'
```

### Create Note

```bash
# Simple note
superskills call obsidian '{
  "action": "create",
  "path": "Inbox/New Idea.md",
  "content": "## Overview\n\nInitial thoughts on this idea."
}'

# Note with full metadata
superskills call obsidian '{
  "action": "create",
  "path": "Projects/AI Strategy 2025.md",
  "content": "## Overview\n\nKey initiatives for AI adoption.",
  "title": "AI Strategy 2025",
  "tags": ["topic/ai-adoption", "type/strategy", "status/draft", "context/project", "author/steff"]
}'

# Note in specific folder (override path folder)
superskills call obsidian '{
  "action": "create",
  "path": "note.md",
  "folder": "Projects/Coaching",
  "content": "Content here",
  "tags": ["topic/coaching"]
}'
```

### Update Note

```bash
# Update content only
superskills call obsidian '{
  "action": "update",
  "path": "Projects/AI Strategy.md",
  "content": "## Updated Content\n\nNew information added."
}'

# Update frontmatter (merge with existing)
superskills call obsidian '{
  "action": "update",
  "path": "Projects/AI Strategy.md",
  "frontmatter": {"status": "active"},
  "merge_frontmatter": true
}'

# Replace frontmatter entirely
superskills call obsidian '{
  "action": "update",
  "path": "Projects/AI Strategy.md",
  "frontmatter": {"title": "New Title", "tags": ["topic/ai"]},
  "merge_frontmatter": false
}'

# Update specific section under heading
superskills call obsidian '{
  "action": "update_section",
  "path": "Projects/AI Strategy.md",
  "heading": "Implementation Plan",
  "content": "## Updated Implementation\n\n1. New step\n2. Another step"
}'

# Append content to end
superskills call obsidian '{
  "action": "append",
  "path": "Projects/AI Strategy.md",
  "content": "## Additional Notes\n\nNew thoughts on this topic."
}'
```

### Move/Rename Note

```bash
# Move note (auto-updates wiki links)
superskills call obsidian '{
  "action": "move",
  "source": "Inbox/Draft.md",
  "destination": "Projects/Final.md"
}'

# Move without updating links
superskills call obsidian '{
  "action": "move",
  "source": "Inbox/Draft.md",
  "destination": "Projects/Final.md",
  "update_links": false
}'
```

### Manage Tags

```bash
# Add single tag
superskills call obsidian '{
  "action": "add_tag",
  "path": "Projects/AI Strategy.md",
  "tag": "status/active"
}'

# Add multiple tags
superskills call obsidian '{
  "action": "add_tags",
  "path": "Projects/AI Strategy.md",
  "tags": ["topic/ai-adoption", "context/client", "language/en-gb"]
}'

# Remove tag
superskills call obsidian '{
  "action": "remove_tag",
  "path": "Projects/AI Strategy.md",
  "tag": "status/draft"
}'

# Replace all tags
superskills call obsidian '{
  "action": "set_tags",
  "path": "Projects/AI Strategy.md",
  "tags": ["topic/ai", "type/strategy", "status/completed"]
}'
```

### Manage Links

```bash
# Add wiki link to end of note
superskills call obsidian '{
  "action": "add_link",
  "path": "Projects/AI Strategy.md",
  "target": "Resources/AI Tools"
}'

# Add link after specific heading
superskills call obsidian '{
  "action": "add_link",
  "path": "Projects/AI Strategy.md",
  "target": "Resources/AI Tools",
  "position": "after_heading",
  "heading": "Related Resources"
}'

# Find backlinks (notes that link to this note)
superskills call obsidian '{
  "action": "find_backlinks",
  "path": "Projects/AI Strategy.md"
}'
```

### Create Hub Note

```bash
# Simple hub with list of links
superskills call obsidian '{
  "action": "create_hub",
  "path": "Hubs/AI Resources.md",
  "title": "AI Resources Hub",
  "linked_notes": ["note1.md", "note2.md", "note3.md"],
  "description": "Central hub for AI-related resources."
}'

# Hub grouped by tag category
superskills call obsidian '{
  "action": "create_hub",
  "path": "Hubs/Coaching Resources.md",
  "title": "Coaching Resources",
  "linked_notes": ["coaching-note1.md", "coaching-note2.md", "coaching-note3.md"],
  "group_by_tag": "topic"
}'
```

This creates sections like:
```markdown
## topic/coaching
- [[coaching-note1]]
- [[coaching-note2]]

## topic/facilitation
- [[coaching-note3]]
```

## Python API

### Basic Usage

```python
from superskills.obsidian.src import ObsidianClient

# Initialize client
client = ObsidianClient(vault_path="/path/to/vault")

# List notes
notes = client.list_notes(folder="Projects", recursive=True)
for note in notes:
    print(f"{note.title}: {', '.join(note.tags)}")

# Get specific note
note = client.get_note("Projects/AI Strategy.md")
print(f"Title: {note.title}")
print(f"Tags: {note.tags}")
print(f"Links: {note.links}")
print(f"Backlinks: {note.backlinks}")

# Search
results = client.search_notes("AI adoption", search_in="both")
print(f"Found {len(results)} matches")

# Find by tag (hierarchical)
ai_notes = client.find_by_tag("topic/ai", exact_match=False)
print(f"Found {len(ai_notes)} AI-related notes")

# Create note
result = client.create_note(
    path="Projects/New Project.md",
    content="## Overview\n\nProject description.",
    title="New Project",
    tags=["topic/project-management", "status/draft"]
)
print(f"Created: {result.note_path}")

# Update note
result = client.update_note(
    path="Projects/New Project.md",
    frontmatter={"status": "active"},
    merge_frontmatter_flag=True
)

# Move note (auto-updates links)
result = client.move_note(
    source="Inbox/Draft.md",
    destination="Projects/Final.md"
)
print(f"Affected files: {result.affected_files}")
```

### Read-Only Mode

```python
# Safe exploration mode
client = ObsidianClient(vault_path="/path/to/vault", read_only=True)

# All reads work
notes = client.list_notes()
note = client.get_note("note.md")

# Writes raise PermissionError
try:
    client.create_note("test.md", "content")
except PermissionError as e:
    print(f"Blocked: {e}")
```

## API Reference

### ObsidianClient

**Constructor:**
```python
ObsidianClient(
    vault_path: Optional[str] = None,  # Defaults to OBSIDIAN_VAULT_PATH env
    read_only: bool = False,
    auto_update_links: bool = True,
    verbose: bool = True
)
```

**List & Inspect:**
- `list_notes(folder=None, recursive=True) -> List[ObsidianNote]`
- `get_note(path_or_title: str) -> Optional[ObsidianNote]`

**Search & Filter:**
- `search_notes(query, search_in="both", case_sensitive=False, limit=50) -> List[ObsidianNote]`
- `find_by_tag(tag, exact_match=False) -> List[ObsidianNote]`
- `find_by_tags(tags, match_all=True) -> List[ObsidianNote]`
- `find_by_folder(folder, recursive=True) -> List[ObsidianNote]`
- `find_backlinks(note_path) -> List[ObsidianNote]`

**Create & Update:**
- `create_note(path, content, title=None, tags=None, frontmatter=None, folder=None) -> ObsidianOperationResult`
- `update_note(path, content=None, frontmatter=None, merge_frontmatter_flag=True) -> ObsidianOperationResult`
- `update_section(path, heading, new_content) -> ObsidianOperationResult`
- `append_content(path, content) -> ObsidianOperationResult`

**Organization:**
- `move_note(source, destination, update_links=None) -> ObsidianOperationResult`
- `add_tag(path, tag) -> ObsidianOperationResult`
- `add_tags(path, tags) -> ObsidianOperationResult`
- `remove_tag(path, tag) -> ObsidianOperationResult`
- `set_tags(path, tags) -> ObsidianOperationResult`
- `add_link(source_path, target_note, position="end", heading=None) -> ObsidianOperationResult`
- `create_hub(hub_path, title, linked_notes, description=None, group_by_tag=None) -> ObsidianOperationResult`

**Planning:**
- `plan_changes(operations) -> ObsidianChangesPlan`
- `apply_plan(plan) -> List[ObsidianOperationResult]`

### ObsidianNote

**Attributes:**
- `path: Path` - Full file path
- `relative_path: str` - Path relative to vault root
- `title: str` - Note title
- `frontmatter: Dict` - YAML frontmatter
- `content: str` - Full content with frontmatter
- `body: str` - Content without frontmatter
- `headings: List[Tuple[int, str]]` - (level, text) tuples
- `tags: List[str]` - Tags from frontmatter
- `links: List[str]` - Wiki links
- `backlinks: List[str]` - Notes linking to this note
- `created_at: str` - Creation timestamp
- `updated_at: str` - Last modified timestamp

## Tag Taxonomy Support

This skill fully supports hierarchical tag taxonomies:

**Hierarchical Tags:**
- Use `/` separator: `topic/ai-adoption`, `status/draft`, `type/blog`
- Prefix matching: Search `topic` matches all `topic/*` tags
- Tag categories: topic, context, type, author, status, client, language, org

**Example Frontmatter:**
```yaml
---
title: AI Strategy 2025
created: 2025-12-17 10:30:00
modified: 2025-12-17 14:20:00
tags:
  - topic/ai-adoption
  - type/strategy
  - context/client
  - status/active
  - author/steff
  - language/en-gb
  - org/the-house-of-ai
---
```

**Tag Operations:**
- Extract tags from `tags:` array in frontmatter
- Add/remove tags with automatic deduplication
- Search by tag prefix or exact match
- Filter by multiple tags (AND/OR logic)
- Group hub notes by tag category

## Integration Examples

### 1. Research → Obsidian Note

```python
from superskills.researcher.src import Researcher
from superskills.obsidian.src import ObsidianClient

# Research topic
researcher = Researcher()
research = researcher.research("AI adoption trends 2025")

# Save to vault
obs = ObsidianClient()
obs.create_note(
    path="Research/AI Adoption Trends.md",
    content=research,
    tags=["topic/ai-adoption", "type/research", "context/research"]
)
```

### 2. Web Content → Reference Note

```python
from superskills.scraper.src import WebScraper
from superskills.obsidian.src import ObsidianClient

# Scrape article
scraper = WebScraper()
article = scraper.scrape("https://example.com/ai-article")

# Save as reference
obs = ObsidianClient()
obs.create_note(
    path="References/Web Articles/AI Article.md",
    content=f"# {article.title}\n\n{article.content}",
    frontmatter={"source": article.url},
    tags=["type/reference", "topic/ai", "author/external"]
)
```

### 3. Generate Content → Draft Note

```python
from superskills.author.src import Author
from superskills.obsidian.src import ObsidianClient

# Generate blog post
author = Author()
post = author.write("Blog post about AI coaching trends")

# Save as draft
obs = ObsidianClient()
obs.create_note(
    path="Content/Blog/AI Coaching Trends.md",
    content=post,
    tags=["type/blog", "topic/coaching", "topic/ai", "status/draft"]
)
```

### 4. Build Knowledge Hub

```python
from superskills.obsidian.src import ObsidianClient

obs = ObsidianClient()

# Find all active projects
projects = obs.find_by_tags(
    tags=["context/project", "status/active"],
    match_all=True
)

# Create hub grouped by topic
project_paths = [p.relative_path for p in projects]
obs.create_hub(
    hub_path="Hubs/Active Projects.md",
    title="Active Projects Hub",
    linked_notes=project_paths,
    group_by_tag="topic"
)
```

## Troubleshooting

### OBSIDIAN_VAULT_PATH not set

```
ValueError: OBSIDIAN_VAULT_PATH environment variable not set
```

**Solution:** Set in `.env` file:
```bash
OBSIDIAN_VAULT_PATH=/Users/username/Documents/Obsidian Vault
```

### Path outside vault

```
ValueError: Path is outside vault: /some/other/path
```

**Solution:** Use paths relative to vault root, or absolute paths inside vault.

### Read-only mode blocks writes

```
PermissionError: Vault is in read-only mode
```

**Solution:** Set `OBSIDIAN_READ_ONLY=false` in `.env` or pass `read_only=False` to constructor.

### Malformed frontmatter

**Symptom:** Note doesn't parse correctly or returns empty frontmatter

**Solution:** Fix YAML syntax manually. Skill handles gracefully but can't auto-fix.

### Link ambiguity

**Symptom:** Multiple notes found with same title

**Solution:** Use full path instead of title when referencing notes.

## Best Practices

1. **Use read-only mode** when testing or exploring
2. **Follow tag taxonomy** consistently across vault
3. **Let auto-update links work** - saves manual link maintenance
4. **Create hub notes** for related content organization
5. **Use required tag categories** - topic, type, status minimum
6. **Backup vault** regularly (git, Time Machine, etc.)

## Version

1.0.0

## License

MIT

## Support

- **Craft Docs Help**: N/A (filesystem only)
- **GitHub Issues**: https://github.com/CoachSteff/superskills/issues

---

Built with ❤️ for seamless Obsidian vault automation
