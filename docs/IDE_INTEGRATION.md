# IDE Integration Guide

Integrate SuperSkills with AI-powered IDEs (Cursor, Antigravity, Verdent) for intelligent task delegation and workflow orchestration.

## Overview

SuperSkills enables IDE AI assistants to delegate specialized tasks through a CLI interface, combining the IDE AI's code manipulation strengths with SuperSkills' domain expertise in content creation, voice generation, research, and more.

## Quick Start

### 1. Ensure SuperSkills is Installed

```bash
# Verify installation
superskills --version

# If not installed, run setup
bash setup.sh
```

### 2. Configure IDE AI Assistant

Your IDE AI assistant reads `.cursorrules` automatically. SuperSkills includes a comprehensive delegation framework in `.cursorrules` that teaches the AI when and how to delegate tasks.

**Key sections in `.cursorrules`:**
- **1A. IDE AI Delegation Framework** - Complete delegation strategy
- Command templates for all operations
- Skill capability quick reference
- Workflow orchestration examples

### 3. Test Integration

```bash
# Export skill metadata for IDE AI
superskills export --output .cursorrules-skills.json

# Discover skills by capability
superskills discover --query "voice generation"

# Test JSON output mode
superskills call researcher "AI trends" --json
```

## Delegation Strategy

### When to Delegate to SuperSkills

✅ **Delegate when:**
- Specialized domain expertise needed (writing, voice, research)
- API integrations required (ElevenLabs, Gemini, etc.)
- PROFILE.md personalization needed (brand voice)
- Multi-step workflows (research → write → edit)
- Batch operations

❌ **Handle directly when:**
- Code changes, refactoring, debugging
- File operations, git commands
- Quick queries, explanations
- Context-dependent tasks
- IDE-native operations

### Decision Tree

```
Task Request
  ↓
  ├─ API integration needed? → YES → superskills call/run
  ├─ PROFILE.md personalization? → YES → superskills call
  ├─ Multi-step workflow? → YES → superskills run
  ├─ Code/file task? → YES → Handle directly
  └─ Quick question? → YES → Handle directly
```

## CLI Commands

### Skill Execution

**Basic usage:**
```bash
superskills call <skill-name> "<input>"
```

**With file input/output:**
```bash
superskills call author --input research.md --output article.md
```

**JSON output (recommended for IDE integration):**
```bash
superskills call author "Write about AI" --json
```

**Stdin piping:**
```bash
echo "AI automation trends" | superskills call researcher --json
```

### Workflow Execution

**Pre-built workflows:**
```bash
# Content creation pipeline
superskills run content-creation --topic "AI coaching" --json

# Podcast generation
superskills run podcast-generation --input script.txt --json

# Training material development
superskills run training-material --input recording.mp3 --json

# Client engagement
superskills run client-engagement --input "https://client.com" --json
```

**Dry-run (preview without execution):**
```bash
superskills run content-creation --topic "topic" --dry-run
```

### Skill Discovery

**Find skills by capability:**
```bash
superskills discover --query "voice generation" --json
```

**Find workflow for task:**
```bash
superskills discover --task "research and write article" --json
```

### Metadata Export

**Export all skill metadata:**
```bash
superskills export --output metadata.json
```

**Export as markdown reference:**
```bash
superskills export --markdown --output SKILLS_REFERENCE.md
```

**Filter skills:**
```bash
# Prompt-based skills only
superskills export --type prompt

# API-integrated skills only
superskills export --has-api
```

## JSON Output Format

All commands support `--json` flag for structured, parseable responses.

### Skill Call Response

```json
{
  "status": "success",
  "output": "Generated content here...",
  "metadata": {
    "skill": "author",
    "type": "prompt",
    "model": "claude-4.5-sonnet"
  },
  "output_file": "/path/to/output.md"
}
```

### Workflow Response

```json
{
  "status": "success",
  "workflow": "content-creation",
  "output": "Final output here...",
  "metadata": {
    "steps_executed": 4
  },
  "output_file": "/path/to/output.md"
}
```

### Error Response

```json
{
  "status": "error",
  "error": "Skill not found: invalid-skill"
}
```

### Discovery Response

```json
{
  "status": "success",
  "query": "voice generation",
  "results": [
    {
      "name": "narrator",
      "description": "Generate professional voiceovers...",
      "type": "python",
      "score": 15.0,
      "capabilities": ["voice-generation", "text-to-speech", "audio"],
      "has_profile": true
    }
  ]
}
```

## Hybrid Workflow Patterns

### Pattern 1: Research + Write + Edit

**User request:** "Research AI trends and write an article"

**IDE AI orchestration:**
```bash
# 1. Research
research_output=$(superskills call researcher "AI automation trends" --json)

# 2. Parse and extract research
research_text=$(echo "$research_output" | jq -r '.output')

# 3. Write article
article_output=$(superskills call author --input <(echo "$research_text") --json)

# 4. Review and refine (direct handling by IDE AI)
# ... apply any code/formatting changes ...

# 5. Deliver to user
```

### Pattern 2: Content → Voice

**User request:** "Create podcast episode about productivity"

**IDE AI orchestration:**
```bash
# 1. Use content-creation workflow
script=$(superskills run content-creation --topic "productivity" --json | jq -r '.output')

# 2. Review script, make adjustments
# ... IDE AI can refine script directly ...

# 3. Generate voiceover
superskills call narrator --input <(echo "$script") --content-type podcast --json

# 4. Deliver MP3 file
```

### Pattern 3: Discover → Execute

**User request:** "I need to extract website content"

**IDE AI orchestration:**
```bash
# 1. Discover relevant skill
skill=$(superskills discover --query "web extraction" --json | jq -r '.results[0].name')

# 2. Execute skill
superskills call "$skill" "https://example.com" --json
```

## Context Handoff Best Practices

### From IDE AI to Skill

✅ **Good:**
- Pass minimal necessary context
- Use temp files or stdin for large inputs
- Always use `--json` for structured responses
- Sanitize sensitive data before delegation

❌ **Avoid:**
- Passing entire conversation history
- Hardcoding file paths
- Expecting skills to maintain state
- Over-delegating simple tasks

### From Skill to IDE AI

✅ **Good:**
- Parse JSON responses for structured data
- Extract metadata for logging/tracking
- Validate output before delivery
- Apply refinements using IDE AI's tools

❌ **Avoid:**
- Blindly passing skill output to user
- Ignoring error responses
- Assuming perfect output quality
- Skipping result validation

## Available Skills

### Content Skills

| Skill | Description | Profile | APIs |
|-------|-------------|---------|------|
| **author** | Ghostwriting in brand voice | ✓ | Anthropic |
| **copywriter** | Marketing copy optimization | ✓ | Anthropic |
| **editor** | Content editing and refinement | ✓ | Anthropic |
| **translator** | Translation and localization | ✓ | Anthropic |

### Media Skills

| Skill | Description | Profile | APIs |
|-------|-------------|---------|------|
| **narrator** | Voice generation (ElevenLabs) | ✓ | ElevenLabs |
| **designer** | AI image generation | ✓ | Gemini, Midjourney |
| **transcriber** | Audio/video transcription | - | OpenAI, AssemblyAI |
| **videoeditor** | Video editing workflows | - | FFmpeg |
| **presenter** | Presentation creation | ✓ | Anthropic |

### Business Skills

| Skill | Description | Profile | APIs |
|-------|-------------|---------|------|
| **coach** | Coaching session design | ✓ | Anthropic |
| **strategist** | Strategic planning | ✓ | Anthropic |
| **marketer** | Social media scheduling | ✓ | Postiz |
| **sales** | Sales messaging | ✓ | Anthropic |
| **publisher** | Content distribution | ✓ | Anthropic |

### Technical Skills

| Skill | Description | Profile | APIs |
|-------|-------------|---------|------|
| **developer** | Code generation | ✓ | Anthropic |
| **scraper** | Web content extraction | - | Crawl4AI |
| **craft** | Craft Docs integration | - | Craft Docs |
| **webmaster** | Website management | ✓ | Anthropic |

**Full list:** `superskills export --markdown`

## Pre-Built Workflows

### Content Creation
```yaml
Steps: researcher → strategist → author → editor
Use: Blog posts, articles, content marketing
Command: superskills run content-creation --topic "<topic>" --json
```

### Podcast Generation
```yaml
Steps: copywriter → narrator
Use: Audio content, voiceovers, podcasts
Command: superskills run podcast-generation --input script.txt --json
```

### Training Material
```yaml
Steps: transcriber → author → editor
Use: Course creation, training docs
Command: superskills run training-material --input recording.mp3 --json
```

### Client Engagement
```yaml
Steps: scraper → researcher → copywriter → sales
Use: Lead generation, sales outreach
Command: superskills run client-engagement --input "<url>" --json
```

## Error Handling

### Common Errors

**Skill not found:**
```bash
# IDE AI should run:
superskills list

# Then suggest alternatives based on description match
```

**API key missing:**
```bash
# Point user to credential setup:
cat docs/CREDENTIAL_SETUP.md

# Or suggest:
export ELEVENLABS_API_KEY=your_key_here
```

**Execution timeout:**
```bash
# Show partial results if available
# Offer retry or suggest simpler approach
```

**Invalid input:**
```bash
# Validate input before delegation
# Use superskills discover to confirm skill capabilities
```

### Error Response Handling

```python
# Python example for IDE AI
import json
import subprocess

result = subprocess.run(
    ['superskills', 'call', 'author', 'Write about AI', '--json'],
    capture_output=True,
    text=True
)

response = json.loads(result.stdout)

if response['status'] == 'error':
    # Handle error
    print(f"Skill failed: {response['error']}")
    # Fall back to direct handling
else:
    # Use output
    output = response['output']
    metadata = response['metadata']
```

## IDE-Specific Integration

### Cursor

Cursor reads `.cursorrules` automatically. SuperSkills delegation framework is pre-configured.

**Usage:**
- Natural language requests automatically routed
- Use Cmd+K/Ctrl+K and reference skills by name
- Cursor AI will delegate when appropriate

### Antigravity

Similar to Cursor, Antigravity respects `.cursorrules`.

**Usage:**
- Chat interface handles delegation
- JSON output automatically parsed
- Workflow suggestions integrated

### Verdent

Verdent provides advanced agent capabilities.

**Usage:**
- Spawn sub-agents for skill execution
- Parallel skill calls for efficiency
- Rich progress indicators

## Troubleshooting

### Skill not executing

1. Verify installation: `superskills --version`
2. Check skill exists: `superskills list`
3. Test directly: `superskills call <skill> "test" --json`
4. Check logs: `~/.superskills/logs/`

### API errors

1. Verify API keys: `superskills status`
2. Check credential setup: `docs/CREDENTIAL_SETUP.md`
3. Test with dry-run: `superskills run <workflow> --dry-run`

### JSON parsing errors

1. Ensure `--json` flag is used
2. Validate JSON: `superskills call skill "test" --json | jq`
3. Check for stderr output mixed with stdout

### Performance issues

1. Use `--dry-run` to preview token usage
2. Optimize input size before delegation
3. Use workflow chaining instead of sequential calls
4. Cache metadata: `superskills export --output cache.json`

## Advanced Usage

### Custom Workflows

Create custom workflows in `workflows/custom/`:

```yaml
name: my-workflow
description: Custom workflow description

steps:
  - name: research
    skill: researcher
    input: ${topic}
    output: research
    
  - name: write
    skill: author
    input: ${research}
    output: draft

variables:
  topic: ${input}
```

**Execute:**
```bash
superskills run my-workflow --topic "AI trends" --json
```

### Skill Chaining

```bash
# Chain skills with pipes
superskills call researcher "AI trends" --json \
  | jq -r '.output' \
  | superskills call author --json
```

### Batch Operations

```bash
# Process multiple inputs
for topic in "AI" "ML" "Automation"; do
  superskills call researcher "$topic" --json --output "${topic}_research.json"
done
```

### Metadata Caching

```bash
# Cache metadata for faster lookups
superskills export --output ~/.superskills/metadata.json

# IDE AI can read this file instead of calling export each time
```

## Security Considerations

- Never pass API keys in commands (use environment variables)
- Sanitize user inputs before delegation
- Don't expose conversation history in delegated tasks
- Validate file paths to prevent path traversal
- Use JSON output to avoid shell injection
- Review skill output before executing code

## Support

- **Documentation**: `docs/` directory
- **Issues**: GitHub Issues
- **Examples**: `.cursorrules` section 1A
- **CLI Help**: `superskills --help`

## Version

SuperSkills v1.2.0+ with IDE Integration support
