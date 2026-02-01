# OpenClaw Integration Guide 🦞

SuperSkills works seamlessly with [OpenClaw](https://openclaw.ai) — your personal AI assistant that runs locally and connects to WhatsApp, Telegram, Discord, and more.

## Why SuperSkills + OpenClaw?

| Feature | Benefit |
|---------|---------|
| **50+ Production Skills** | Research, writing, voiceovers, proposals — ready to use |
| **CLI-First Design** | OpenClaw can call `superskills` commands directly |
| **Profile Personalization** | Skills learn your voice and brand |
| **Workflow Chaining** | Multi-step automation pipelines |
| **Local & Private** | Your data stays on your machine |

## Quick Setup

### 1. Install SuperSkills

```bash
# Clone the repository
git clone https://github.com/CoachSteff/superskills.git
cd superskills

# Run automated setup (recommended)
bash setup.sh

# Or install manually with pipx
pipx install -e .
```

### 2. Verify Installation

```bash
# Should work from any directory
superskills --version
superskills list
```

### 3. Configure API Keys (Optional)

Some skills require API keys for external services:

```bash
# Add to your shell profile or .env file
export ANTHROPIC_API_KEY=your_key_here      # For AI-powered skills
export ELEVENLABS_API_KEY=your_key_here     # For narrator/voiceover
export OPENAI_API_KEY=your_key_here         # For transcription
```

See [CREDENTIAL_SETUP.md](CREDENTIAL_SETUP.md) for all available integrations.

## Using SuperSkills with OpenClaw

Once installed, OpenClaw can use SuperSkills through shell commands. Here are common patterns:

### Direct Skill Calls

Ask OpenClaw to run skills for you:

```
You: "Research the latest AI agent trends"
OpenClaw: *runs* superskills call researcher "AI agent trends 2026"

You: "Write a LinkedIn post about that research"  
OpenClaw: *runs* superskills call author --input research.md --format linkedin

You: "Generate a voiceover for this script"
OpenClaw: *runs* superskills call narrator-podcast --input script.md
```

### Workflow Automation

Chain multiple skills together:

```
You: "Create a podcast episode about AI automation"
OpenClaw: *runs* superskills run podcast-generation --topic "AI automation"
```

This runs: `researcher → copywriter → narrator` automatically.

### Skill Discovery

Find the right skill for any task:

```
You: "What skills can help me create training materials?"
OpenClaw: *runs* superskills discover --query "training materials"
```

## Recommended Skills for OpenClaw Users

| Skill | Use Case | Example |
|-------|----------|---------|
| `researcher` | Quick research & analysis | "Research competitor X" |
| `author` | Long-form content | "Write a blog post about..." |
| `copywriter` | Marketing copy | "Write ad copy for..." |
| `editor` | Polish existing content | "Edit this draft for clarity" |
| `translator` | Multi-language support | "Translate to Dutch" |
| `narrator-*` | Voice generation | "Create voiceover for script" |
| `transcriber` | Audio → text | "Transcribe this meeting" |
| `offer-builder` | Proposals & quotes | "Create proposal for client X" |

## Advanced: Creating an OpenClaw Skill

You can wrap SuperSkills as a dedicated OpenClaw skill:

### Option 1: Add to TOOLS.md

In your OpenClaw workspace, add to `TOOLS.md`:

```markdown
## SuperSkills

- **CLI:** `superskills` (globally installed)
- **Skills:** 50+ automation skills
- **Usage:** `superskills call <skill> "<input>"`
- **Discover:** `superskills discover --query "<capability>"`
- **Workflows:** `superskills run <workflow> --topic "<topic>"`
```

### Option 2: Create a Dedicated Skill

Create `~/.openclaw/skills/superskills/SKILL.md`:

```markdown
# SuperSkills Integration

You have access to the SuperSkills CLI for advanced automation tasks.

## Available Commands

- `superskills list` - Show all 50+ skills
- `superskills call <skill> "<input>"` - Run a skill
- `superskills discover --query "<need>"` - Find skills by capability
- `superskills run <workflow>` - Execute multi-step workflow

## When to Use

Use SuperSkills when:
- User needs research, writing, or content creation
- Task benefits from specialized skill (narrator, transcriber, etc.)
- Multi-step workflow would be more efficient

## Example Flows

Research + Write:
1. `superskills call researcher "topic"`
2. `superskills call author --input research.md`

Podcast Creation:
1. `superskills run podcast-generation --topic "topic"`
```

## Personalization (Recommended)

SuperSkills become more powerful when personalized to your voice:

```bash
# Interactive setup (15 minutes, guided)
superskills call profile-builder "help me create my master briefing"

# Or manual setup
cp MASTER_BRIEFING_TEMPLATE.yaml ~/.superskills/master-briefing.yaml
# Edit with your brand voice, expertise, and style
```

See [PROFILE_CUSTOMIZATION.md](PROFILE_CUSTOMIZATION.md) for details.

## Troubleshooting

### "Command not found: superskills"

```bash
# For pipx installation
pipx ensurepath
# Restart your terminal

# Or add to PATH manually
export PATH="$HOME/.local/bin:$PATH"
```

### Skills not finding API keys

```bash
# Check current configuration
superskills status

# Verify .env file exists
cat .env

# Or set environment variables directly
export ANTHROPIC_API_KEY=your_key
```

### OpenClaw can't execute commands

Ensure your OpenClaw configuration allows shell execution. Check your `openclaw.json` for security settings.

## Community & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/CoachSteff/superskills/issues)
- **GitHub Discussions**: [Ask questions, share workflows](https://github.com/CoachSteff/superskills/discussions)
- **OpenClaw Discord**: [Friends of the Crustacean 🦞](https://discord.com/invite/clawd)

## What's Next?

1. **Try a skill**: `superskills call researcher "your topic"`
2. **Personalize**: Set up your Master Briefing
3. **Explore workflows**: `superskills workflow list`
4. **Contribute**: PRs welcome for new skills!

---

*Built with 🦞 by the SuperSkills community. Works great with OpenClaw!*
