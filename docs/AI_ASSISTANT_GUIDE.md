# SuperSkills AI Assistant Integration Guide

*Guide for IDE AI assistants (Cursor, GitHub Copilot, Windsurf, etc.) integrating with SuperSkills CLI*

## Quick Reference

### ✅ Recommended Patterns

**Pattern 1: Workflows First (PREFERRED)**
- Check available workflows: `superskills workflow list`
- Use when task matches existing workflow
- Example: `superskills run podcast-generation --input script.md`

**Pattern 2: Direct Skill Call**
- Use for single-skill tasks
- Discover skills first: `superskills list`
- Example: `superskills call narrator-podcast --input script.md`

**Pattern 3: Discovery-Driven**
- When unsure which skill to use
- Use: `superskills discover --query "meditation audio"`
- Shows relevant skills and workflows

### ❌ Common Mistakes

**Inventing CLI Parameters:**
```bash
# ❌ WRONG - These parameters don't exist
superskills call narrator --content-type podcast --profile-type podcast
superskills call skill --arbitrary-param value

# ✅ CORRECT - Use specialized skills instead
superskills call narrator-podcast --input script.md
```

**Writing Custom Python When CLI Works:**
```python
# ❌ WRONG - Don't import superskills modules directly
from superskills.narrator.src.Voiceover import VoiceoverGenerator

# ✅ CORRECT - Use CLI
superskills call narrator-podcast --input script.md
```

## Discovery Process for AI Assistants

### When User Requests a Task

1. **Check workflows first:**
   ```bash
   superskills workflow list
   superskills discover --task "create podcast from markdown"
   ```

2. **If no workflow, check available skills:**
   ```bash
   superskills list
   superskills discover --query "voice generation"
   ```

3. **Get skill details:**
   ```bash
   superskills show <skill-name>
   ```
   - Read description and capabilities
   - Check for specialized variants
   - Note any requirements

4. **Execute with appropriate skill:**
   ```bash
   superskills call <skill-name> --input <file>
   ```

## Skill Families

Some skills have specialized variants for different use cases, organized hierarchically:

### Narrator Family

**Parent:** `narrator` (defaults to podcast)

**Specialized Subskills:**
- `narrator-podcast` - Conversational podcast voiceovers (140-160 WPM)
- `narrator-meditation` - Calm meditation guides
- `narrator-educational` - Clear educational content (130-150 WPM)
- `narrator-marketing` - Energetic marketing content (150-170 WPM)
- `narrator-social` - Fast-paced social media (160-180 WPM)

**Discovery:**
```bash
superskills list                    # Shows hierarchical view
superskills discover --query "meditation audio"
```

**Usage:**
```bash
superskills call narrator-podcast --input episode-script.md
superskills call narrator-meditation --input guide.md
```

**Workflows (recommended):**
```bash
superskills run podcast-generation --input script.md
```

## Examples by Use Case

### Generate Podcast

```bash
# Workflow (recommended)
superskills run podcast-generation --input script.md

# Direct call
superskills call narrator-podcast --input script.md
```

### Create Meditation Guide

```bash
superskills call narrator-meditation --input meditation-script.md
```

### Generate Educational Content

```bash
superskills call narrator-educational --input lesson.md
```

### Create Marketing Video Voiceover

```bash
superskills call narrator-marketing --input promo-script.md
```

### Generate Social Media Voiceover

```bash
superskills call narrator-social --input reel-script.md
```

### Enhance Marketing Copy

```bash
superskills call copywriter --input draft.md
```

### Generate Image

```bash
superskills call designer --input "A serene mountain landscape"
```

## Handling Errors

### Skill Not Found
```bash
superskills list  # See available skills
superskills discover --query "<capability>"
```

### Missing API Keys
```bash
superskills status  # Check API key configuration
```

### Unclear Which Skill to Use
```bash
superskills discover --task "what I want to do"
# Returns relevant workflows and skills
```

## Integration Tips

1. **Always check workflows first** - Pre-configured for common tasks
2. **Use discovery commands** - Don't guess skill names or parameters
3. **Read skill documentation** - `superskills show <skill>` for details
4. **Leverage skill families** - Specialized skills for optimized results
5. **Check status regularly** - Ensures API keys are configured

## Workflow vs Direct Skill Usage

**Use Workflows When:**
- Task involves multiple steps (e.g., enhance script → generate audio)
- Common use case with existing workflow definition
- Want consistent, repeatable process
- Need to process multiple files (batch/watch mode)

**Use Direct Skills When:**
- Single, focused task (e.g., just generate voiceover)
- Quick one-off execution
- Custom parameters or workflow not applicable
- Testing or experimentation

## CLI Capabilities

### Skill Execution
```bash
superskills call <skill> --input <file>
superskills call <skill> --input <file> --format json
```

### Workflow Execution
```bash
superskills run <workflow> --input <file>
superskills run <workflow> --batch        # Process all files in input dir
superskills run <workflow> --watch        # Auto-process new files
```

### Discovery
```bash
superskills list                          # All skills
superskills show <skill>                  # Skill details
superskills discover --query "<search>"   # Find skills
superskills discover --task "<task>"      # Find workflows
superskills workflow list                 # All workflows
```

### Status & Configuration
```bash
superskills status                        # Check API keys
superskills init                          # Initialize profile
```

## Common Patterns

### Podcast Production
```bash
# Full workflow
superskills run podcast-generation --input script.md

# Individual steps
superskills call copywriter --input draft.md
superskills call narrator-podcast --input enhanced-script.md
```

### Course Creation
```bash
superskills call narrator-educational --input lesson-01.md
superskills call narrator-educational --input lesson-02.md
```

### Marketing Content
```bash
superskills call narrator-marketing --input promo.md
superskills call designer --input "Product showcase image"
```

### Meditation & Wellness
```bash
superskills call narrator-meditation --input morning-meditation.md
superskills call narrator-meditation --input breathing-exercise.md
```

## Troubleshooting

| Issue | Command | Fix |
|-------|---------|-----|
| Unknown skill | `superskills list` | Use exact skill name from list |
| Missing API key | `superskills status` | Set ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, etc. |
| Unsure which skill | `superskills discover --query "..."` | Find matching skill |
| Task unclear | `superskills discover --task "..."` | Find matching workflow |
| Workflow fails | Check input directory, API keys, file format | See workflow README |

## Best Practices

### For AI Assistants

1. **Discovery First** - Always check available skills/workflows before execution
2. **Don't Invent** - Never create CLI parameters that don't exist
3. **Use Specialized Skills** - Leverage skill families for optimized results
4. **Read Documentation** - `superskills show <skill>` provides context
5. **Prefer Workflows** - Use workflows for multi-step tasks
6. **Check Status** - Verify API keys before attempting execution

### For Users Working with AI Assistants

1. **Be Specific** - "Generate podcast voiceover" vs "Create audio"
2. **Mention Content Type** - Helps AI select right specialized skill
3. **Reference Workflows** - "Use podcast-generation workflow"
4. **Provide Context** - Input file format, expected output, special requirements

## Version Information

This guide applies to **SuperSkills v2.0+** with nested skill architecture.

For older versions, some skill names may differ. Run `superskills --version` to check.

## Support & Resources

- **CLI Help**: `superskills --help`
- **Skill Details**: `superskills show <skill>`
- **Workflow Details**: Check workflow directory README
- **Discovery**: `superskills discover --query <search>`
