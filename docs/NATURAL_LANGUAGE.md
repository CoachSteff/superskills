# Natural Language Interface for Superskills CLI

## Overview

The Superskills CLI supports natural language input, allowing you to interact with the system using plain English instead of memorizing exact command syntax.

## Usage

### Basic Syntax

Natural language mode requires the explicit `prompt` subcommand:

**Use the `prompt` command:**
```bash
# Correct - use 'prompt' for natural language
superskills prompt "find the Superworker executive summary"
superskills prompt "list all available skills"
superskills prompt "what skills help with podcasts"
superskills prompt "run copywriter on summary.txt"
```

**For faster execution, use exact commands:**
```bash
# Direct commands (no LLM call, instant execution)
superskills list
superskills show narrator
superskills discover --query "podcasts"
superskills call copywriter "Write about AI"
```

**Why `prompt` is required:**
- Shell parsing splits multi-word input before the CLI receives it
- `superskills find the summary` becomes `["find", "the", "summary"]` separate arguments
- The `prompt` subcommand explicitly signals: "treat everything after as natural language"
- This ensures reliable natural language processing

**How It Works:**
- The `prompt` command takes everything after it as a single natural language query
- LLM parses the intent and routes to appropriate command
- Confidence-based execution (high confidence = auto-execute, medium = confirm, low = suggest alternatives)
- All existing exact commands work as before

### Configuration

Natural language parsing is powered by an LLM (default: Gemini Flash). You can configure it via:

1. **Environment variables:**
   ```bash
   export SUPERSKILLS_INTENT_MODEL="gemini-2.0-flash-exp"
   export SUPERSKILLS_INTENT_PROVIDER="gemini"  # or anthropic, openai
   export GEMINI_API_KEY="your-key-here"
   ```

2. **CLI flags:**
   ```bash
   superskills --intent-model "gpt-4o-mini" find my files
   superskills --intent-provider anthropic prompt list skills
   ```

3. **Config file** (~/.superskills/config.yaml):
   ```yaml
   intent:
     enabled: true
     provider: gemini
     model: gemini-2.0-flash-exp
     confidence_threshold: 0.5
     always_confirm_medium: true
   ```

### Disable Natural Language

If you want to force exact command syntax:

```bash
superskills --no-intent list
```

Or disable it globally in config:

```yaml
intent:
  enabled: false
```

## Examples

### Search for Files
```bash
superskills prompt "find the Superworker executive summary"
→ Searching files for: Superworker executive summary
Found 2 matches:
  1. ~/Documents/Superworker/executive_summary.pdf
  2. ~/Documents/Superworker/summary_draft.txt
```

### Execute a Skill
```bash
superskills prompt "run copywriter on summary.txt"
→ Execute copywriter skill with file input
[... skill output ...]
```

### List Skills
```bash
superskills prompt "show me all skills"
→ List all available skills
[... list output ...]
```

### Discover Skills by Capability
```bash
superskills prompt "what skills can help with podcasts?"
→ Discover skills related to podcasts
[... matching skills ...]
```

### Configuration
```bash
superskills prompt "set temperature to 0.5"
I interpret this as:
  Set API temperature configuration

Action: config
Target: null
Parameters: {
  "key": "api.anthropic.temperature",
  "value": "0.5"
}

Proceed? [Y/n]
```

## Confidence Levels

The system assigns confidence scores to interpretations:

- **High (0.8-1.0)**: Executes immediately with feedback
  ```
  → File search for 'Superworker executive summary'
  [... results ...]
  ```

- **Medium (0.5-0.8)**: Asks for confirmation
  ```
  I interpret this as:
    Execute copywriter skill
  
  Proceed? [Y/n]
  ```

- **Low (<0.5)**: Suggests alternatives
  ```
  I'm not sure what you meant. Here are some suggestions:
    1. List all available skills
    2. Search for files
    3. Show CLI status
  ```

## Search Paths

File search looks in configured paths (default):
- Obsidian vault (if `OBSIDIAN_VAULT_PATH` is set)
- ~/Documents
- ~/Downloads
- Current directory

Configure in `~/.superskills/config.yaml`:

```yaml
search:
  paths:
    - ${OBSIDIAN_VAULT_PATH}
    - ~/Documents
    - ~/Downloads
    - ~/Projects
    - .
  use_ripgrep: true
  max_results: 50
```

## Supported Actions

- **search**: Find files or content
- **execute_skill**: Run a specific skill
- **run_workflow**: Execute a workflow
- **list**: Show all skills
- **show**: Display skill details
- **config**: Get/set configuration
- **discover**: Find skills by capability

## Troubleshooting

### "GEMINI_API_KEY not found"
Set your Gemini API key:
```bash
export GEMINI_API_KEY="your-key-here"
```

Or use a different provider:
```bash
export SUPERSKILLS_INTENT_PROVIDER="anthropic"
export ANTHROPIC_API_KEY="your-key-here"
```

### "Intent parsing disabled"
Enable in config:
```bash
superskills config set intent.enabled true
```

### Low confidence / unclear requests
Be more specific:
- Instead of: "do the thing"
- Try: "run copywriter on summary.txt"

## Backward Compatibility

All existing commands work exactly as before:
```bash
superskills list
superskills show copywriter
superskills call copywriter "Write a blog post"
superskills discover --query "voice generation"
```

Natural language is purely additive - use `prompt` for natural language, use exact commands for direct access.

## Known Limitations

**Multi-word natural language requires `prompt`:**
- **Why?** Shell splits arguments before CLI sees them
- `superskills find my files` → `["find", "my", "files"]` (three separate args)
- `superskills prompt "find my files"` → natural language query

**Workaround:**
- Always use `prompt` for natural language
- Use exact commands for faster, direct execution

**Future improvement:**
- Auto-detection for single unknown words may trigger suggestions
- Full multi-word auto-detection limited by shell behavior
