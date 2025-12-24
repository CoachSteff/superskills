---
name: obsidian
description: Filesystem-based Obsidian vault manager for reading, writing, searching, and organizing Markdown notes with hierarchical tag taxonomy
version: 1.0.0
license: MIT
---

# Obsidian Vault Manager

> **Note**: Review [PROFILE.md](PROFILE.md) for user-specific vault location, tag taxonomy, and note organization preferences.
> 
> **Master Briefing**: Global brand voice at `~/.superskills/master-briefing.yaml` applies automatically. Skill profile overrides when conflicts exist.

A filesystem-based Obsidian vault manager that enables reading, writing, searching, and organizing Markdown notes directly through the file system without requiring Obsidian plugins or REST APIs.

## Purpose

This skill helps you manage your Obsidian personal knowledge base programmatically. Use it when you need to:

- Create and update notes automatically from other workflows
- Search and filter notes by content, tags, or location
- Organize notes with hierarchical tags (topic/ai, status/draft, etc.)
- Build hub/index notes that link related content
- Maintain wiki link integrity when moving or renaming notes
- Integrate Obsidian vault with other SuperSkills workflows

## Instructions

When activated, this skill will:

1. **Read and search your vault** - List notes, search by text or tags, find backlinks
2. **Create and update notes** - Add new notes with frontmatter, update content or specific sections
3. **Organize with tags** - Add/remove hierarchical tags following your taxonomy
4. **Manage wiki links** - Auto-update links when moving notes, create link connections
5. **Build knowledge hubs** - Generate index notes grouped by tags or topics

### Key Guidelines

- **Safety First**: Use read-only mode (`OBSIDIAN_READ_ONLY=true`) when exploring or testing
- **Path Validation**: All paths are validated to stay within vault boundaries
- **Tag Hierarchy**: Support hierarchical tags with `/` separator (e.g., `topic/ai-adoption`)
- **Frontmatter Standards**: Auto-add `created` and `modified` timestamps to all notes
- **Link Integrity**: Automatically update wiki links when moving/renaming notes (configurable)

### Quality Standards

- Preserve existing frontmatter when updating notes
- Maintain tag consistency following vault taxonomy
- Never break wiki links - auto-update or notify
- Respect read-only mode - fail gracefully on write attempts
- Handle malformed frontmatter gracefully (don't crash)

## Configuration

### Required Environment Variables

```bash
# Absolute path to your Obsidian vault root
OBSIDIAN_VAULT_PATH=/Users/username/Documents/Obsidian Vault
```

### Optional Settings

```bash
# Prevent all write operations (default: false)
OBSIDIAN_READ_ONLY=false

# Auto-update wiki links on move/rename (default: true)
OBSIDIAN_AUTO_UPDATE_LINKS=true

# Enable verbose logging (default: true)
OBSIDIAN_VERBOSE=true
```

### Setup Instructions

1. Copy `.env.template` to `.env` in the `superskills/obsidian/` directory
2. Set `OBSIDIAN_VAULT_PATH` to your vault's absolute path
3. (Optional) Enable read-only mode for safe exploration
4. Test with: `superskills call obsidian '{"action": "list"}'`

## Examples

### Example 1: List All Notes
**Input:** List all notes in vault  
**CLI:**
```bash
superskills call obsidian '{"action": "list"}'
```

**Expected Output:** JSON array of all notes with metadata (title, tags, links, timestamps)

### Example 2: Search by Hierarchical Tag
**Input:** Find all AI-related notes  
**CLI:**
```bash
superskills call obsidian '{"action": "find_by_tag", "tag": "topic/ai"}'
```

**Expected Output:** All notes tagged with `topic/ai`, `topic/ai-adoption`, `topic/ai-tools`, etc.

### Example 3: Create Note with Tags
**Input:** Create a new project note  
**CLI:**
```bash
superskills call obsidian '{
  "action": "create",
  "path": "Projects/AI Strategy 2025.md",
  "content": "## Overview\n\nKey initiatives for AI adoption.",
  "title": "AI Strategy 2025",
  "tags": ["topic/ai-adoption", "type/strategy", "status/draft", "context/project"]
}'
```

**Expected Output:** Note created with YAML frontmatter containing tags and timestamps

### Example 4: Move Note (Auto-Update Links)
**Input:** Move draft from Inbox to Projects  
**CLI:**
```bash
superskills call obsidian '{
  "action": "move",
  "source": "Inbox/Draft Idea.md",
  "destination": "Projects/Final Idea.md"
}'
```

**Expected Output:** Note moved, all wiki links in vault updated from `[[Draft Idea]]` to `[[Final Idea]]`

### Example 5: Create Hub Note Grouped by Tags
**Input:** Build an index of all coaching resources grouped by topic  
**CLI:**
```bash
superskills call obsidian '{
  "action": "create_hub",
  "path": "Hubs/Coaching Resources.md",
  "title": "Coaching Resources Hub",
  "linked_notes": ["note1.md", "note2.md", "note3.md"],
  "group_by_tag": "topic"
}'
```

**Expected Output:** Hub note with sections for each topic tag (topic/coaching, topic/facilitation, etc.), listing relevant notes under each

## Tools & Integrations

**Filesystem Only:**
- No external APIs or plugins required
- Direct Markdown file manipulation
- YAML frontmatter parsing and serialization

**Python Libraries:**
- `pyyaml` - YAML frontmatter parsing
- `pathlib` - Safe path operations

## Tag Taxonomy Support

This skill fully supports hierarchical tag taxonomies with the `/` separator. It respects the tag structure defined in your vault's taxonomy (e.g., `topic/ai`, `status/active`, `type/blog`).

**Tag Operations:**
- Extract tags from frontmatter `tags:` array
- Add/remove tags while preventing duplicates
- Search by tag prefix (e.g., search `topic` matches all `topic/*` tags)
- Filter notes by multiple tags (AND/OR logic)
- Group hub notes by tag category

**Example Taxonomy:**
```yaml
tags:
  - topic/ai-adoption
  - type/course-material
  - context/client
  - status/active
  - author/steff
  - language/en-gb
```

## User Profile Integration

This skill does not use a PROFILE.md file. All configuration is via environment variables in `.env`.

## Tips & Best Practices

- **Tip 1**: Start in read-only mode when testing - set `OBSIDIAN_READ_ONLY=true`
- **Tip 2**: Use hierarchical tags consistently - follow your vault's taxonomy
- **Tip 3**: Let auto-update links handle renames - saves manual fix-up work
- **Tip 4**: Create hub notes to organize related content - easier navigation
- **Tip 5**: Always include tags from required categories: topic, type, status

## Common Issues & Troubleshooting

### Issue: OBSIDIAN_VAULT_PATH not set
**Symptom**: Error on initialization: "OBSIDIAN_VAULT_PATH environment variable not set"  
**Solution**: Set the environment variable in `.env` file with absolute path to vault

### Issue: Path outside vault error
**Symptom**: "Path is outside vault" error  
**Solution**: Ensure all paths are relative to vault root, or use absolute paths inside vault

### Issue: Read-only mode blocks writes
**Symptom**: "Vault is in read-only mode" error on create/update  
**Solution**: Set `OBSIDIAN_READ_ONLY=false` in `.env` to enable write operations

### Issue: Malformed frontmatter
**Symptom**: Note doesn't parse correctly  
**Solution**: Skill handles gracefully - returns empty frontmatter dict. Manually fix YAML syntax.

## Related Skills

**Skills that work well together:**
- **researcher**: Gather information, then save to Obsidian note
- **author**: Generate content, then create note in vault
- **editor**: Refine existing note content
- **scraper**: Extract web content, store as reference note

## Limitations

- **Filesystem only** - No Obsidian plugin features (graph view, canvas, etc.)
- **No delete operation** - For safety, deletion not implemented
- **Link resolution** - Ambiguous links (multiple notes with same title) use first match
- **No binary files** - Only Markdown (`.md`) files supported

## Version History

**Current Version**: 1.0.0

- **v1.0.0** - 2025-12-17 - Initial release
  - Full CRUD operations on notes
  - Hierarchical tag support with frontmatter YAML
  - Wiki link extraction and auto-update on move
  - Search by text, tags, folder
  - Hub note creation with tag grouping
  - Read-only mode for safe exploration
  - Path validation and security

## Credits & Attribution

- Built for SuperSkills framework
- Designed for filesystem-based Obsidian vault management
- No dependencies on Obsidian APIs or plugins

## Support & Feedback

- **Issues**: Report bugs at [GitHub Issues](https://github.com/CoachSteff/superskills/issues)
- **Documentation**: See `README.md` in `superskills/obsidian/`
