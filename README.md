# SuperSkills - AI-Powered Automation Skills for Claude

Custom skill library for Claude Desktop that automates coaching, training, and content creation workflows. Built on Anthropic's Agent Skills framework.

**Quick Start:** See [QUICKSTART.md](docs/QUICKSTART.md) for common commands and examples.

## Overview

SuperSkills is a comprehensive AI automation toolkit with **45 skills** that transform repetitive business tasks into automated workflows. Designed for freelance coaches, trainers, and content creators who want to scale their operations without proportional effort increases.

**What You Get:**
- 30 Claude Skills (folder-based) - Prompt-based AI specialists, no Python required
- 15 Python-Powered Skills - Full API integrations with advanced automation (including 5 specialized narrator skills)
- Hierarchical skill families (e.g., narrator-podcast, narrator-meditation, narrator-educational)
- Comprehensive test suite (90+ unit tests)
- Credential management system (hybrid env vars + .env files)
- Production-ready patterns and templates

## Quick Start

### Prerequisites
- Python 3.9+
- Git

### Installation

**Automated Setup (Recommended):**
```bash
git clone https://github.com/CoachSteff/superskills.git
cd superskills
bash setup.sh
```

The setup script will guide you through:
- Choosing installation method (pipx recommended, or venv/user install)
- Installing dependencies
- Initializing the CLI
- Configuring API keys

**Recommended:** Use pipx for global access - the `superskills` command works from any directory.

**Manual Installation:**
```bash
git clone https://github.com/CoachSteff/superskills.git
cd superskills

# Option 1: Global install with pipx (recommended)
pipx install -e .

# Option 2: Virtual environment (for development)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Option 3: User install
pip install --user -e .
```

### First Steps

1. **Initialize the CLI:**
   ```bash
   superskills init
   ```

2. **Set up API keys:**
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   export ELEVENLABS_API_KEY=your_key_here
   # Or add to .env file in project root
   ```

3. **List available skills:**
   ```bash
   superskills list
   ```

4. **Try a skill:**
   ```bash
   superskills call researcher "AI automation trends in 2024"
   ```

5. **Run a workflow:**
   ```bash
   superskills run content-creation --topic "Future of AI coaching"
   ```

6. **Set up personalized profiles (optional but recommended):**
   ```bash
   cp superskills/author/PROFILE.md.template superskills/author/PROFILE.md
   # Edit PROFILE.md with your brand voice, expertise, and style
   ```

### Verify Installation

After installation, verify the CLI works from anywhere:

```bash
# Test from any directory
cd ~
superskills --version
superskills --help
```

**If command not found:**

```bash
# For pipx: ensure pipx path is in your shell
pipx ensurepath
# Then restart your terminal

# For venv: activate it first
cd /path/to/superskills
source .venv/bin/activate
superskills --help

# For user install: add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Quick Example: Generate Podcast

```bash
# 1. Place your script in the workflow input folder
cp your-script.md workflows/podcast-generation/input/

# 2. Run the workflow (choose one):

# Watch mode - auto-processes new files
superskills run podcast-generation --watch

# Batch mode - processes all existing files
superskills run podcast-generation --batch

# Single file mode
superskills run podcast-generation --input your-script.md

# 3. Output appears in: workflows/podcast-generation/output/
```

See [QUICKSTART.md](docs/QUICKSTART.md) for more examples.

### Using with Claude Desktop

For Claude Desktop integration, import individual skill folders as ZIP files:
- Open Claude Desktop Settings → Skills
- Click "Upload Custom Skill"
- Select skill folders (they'll be auto-zipped)
- Each skill's `SKILL.md` will be read by Claude

See [CLI_SETUP.md](dev/CLI_SETUP.md) for detailed CLI installation and usage.

## Skill Categories

### 1. Claude Skills (Prompt-Based)
**30 skill folders** in `/superskills/` - No Python dependencies required

These are pure prompt-based skills that work immediately with Claude Desktop. Each folder contains a `SKILL.md` file with the skill definition:

| Skill | Description |
|-------|-------------|
| **author** | Ghostwriting in your brand voice |
| **builder** | Workflow automation architect |
| **coach** | Coaching session design and delivery |
| **context-engineer** | Optimize AI context for better results |
| **copywriter** | Marketing copy and messaging |
| **developer** | Code generation and debugging |
| **editor** | Content editing and quality control |
| **manager** | Project and team coordination |
| **researcher** | Research and analysis |
| **sales** | Sales messaging and outreach |
| **strategist** | Strategic planning |
| **translator** | Translation and localization |
| ...and 18 more |

### 2. Python-Powered Skills (API Integrations)
**15 production-ready skills** with Python implementations in `/superskills/`

#### Featured API-Integrated Skills

| Skill | APIs | Capabilities |
|-------|------|--------------|
| **craft** | Craft Docs API | Document management and export |
| **designer** | Gemini Imagen, Midjourney | AI image generation, brand consistency |
| **marketer** | Postiz API | Social media scheduling, multi-platform posting |
| **narrator-podcast** | ElevenLabs | Conversational podcast voiceovers (140-160 WPM) |
| **narrator-meditation** | ElevenLabs | Calm meditation guides with slow pacing |
| **narrator-educational** | ElevenLabs | Clear educational content (130-150 WPM) |
| **narrator-marketing** | ElevenLabs | Energetic marketing content (150-170 WPM) |
| **narrator-social** | ElevenLabs | Fast-paced social media (160-180 WPM) |
| **transcriber** | Whisper, AssemblyAI | Audio/video transcription |

#### Narrator Skill Family

The **narrator** skill has been refactored into a hierarchical family with 5 specialized subskills:

```bash
superskills list | grep narrator
# Output:
- narrator (parent skill)
  ├─ narrator-educational - Clear educational content
  ├─ narrator-marketing - Energetic marketing content
  ├─ narrator-meditation - Calm meditation guides
  ├─ narrator-podcast - Conversational podcast voiceovers
  └─ narrator-social - Fast-paced social media
```

Each narrator variant is optimized for its specific use case with pre-configured voice settings, pacing, and tone.

#### Additional Python Skills

coursepackager, emailcampaigner, presenter, scraper, videoeditor

**Pattern:** Each includes SKILL.md definition, optional src/ implementation, and configuration templates

## Featured Workflows

SuperSkills includes a powerful CLI for orchestrating multi-skill workflows.

### CLI Workflow Execution

```bash
# Content creation workflow
superskills run content-creation --topic "AI in coaching"

# Podcast generation workflow
superskills run podcast-generation --input script.txt

# Training material workflow
superskills run training-material --input recording.mp3

# Client engagement workflow
superskills run client-engagement --input "https://client-website.com"
```

### Pre-Built Workflows

**Content Creation Pipeline:**
```
researcher → strategist → author → editor
```
End-to-end content production from research to polished article.

**Podcast Generation:**
```
copywriter → narrator
```
Script enhancement and MP3 generation with your tone-of-voice.

**Training Material Development:**
```
transcriber → author → editor
```
Transform recordings into structured training content.

**Client Engagement:**
```
scraper → researcher → copywriter → sales
```
Automated research and personalized outreach.

### Custom Workflows

Create your own workflow definitions in YAML:

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
```

Save to `workflows/custom/my-workflow.yaml` and run:
```bash
superskills run my-workflow --topic "Your topic"
```

## Documentation

- **[Roadmap](ROADMAP.md)** - Product vision and development roadmap
- **[CLI Setup](dev/CLI_SETUP.md)** - SuperSkills CLI installation and usage
- **[Quick Start](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[IDE Integration](docs/IDE_INTEGRATION.md)** - Integrate with Cursor, Antigravity, Verdent
- **[AI Assistant Guide](docs/AI_ASSISTANT_GUIDE.md)** - Integration patterns for IDE AI assistants
- **[Architecture](dev/ARCHITECTURE.md)** - System design and patterns
- **[Credential Setup](docs/CREDENTIAL_SETUP.md)** - API key configuration guide
- **[Skill Development](docs/SKILL_DEVELOPMENT.md)** - Create custom skills
- **[Contributing](dev/CONTRIBUTING.md)** - Contribution guidelines

## IDE Integration

SuperSkills integrates with AI-powered IDEs (Cursor, Antigravity, Verdent) for intelligent task delegation.

### Quick Start

```bash
# Export skill metadata for IDE AI
superskills export --output .cursorrules-skills.json

# Discover skills by capability
superskills discover --query "voice generation"

# Use JSON output for structured responses
superskills call author "Write about AI" --json
```

### Key Features

- **Intelligent Delegation**: IDE AI automatically routes tasks to specialized skills
- **JSON Output Mode**: Structured responses for easy parsing (`--json` flag)
- **Stdin Support**: Pipe workflows and chain skills
- **Skill Discovery**: Find skills by capability or task description
- **Metadata Export**: Generate skill reference for IDE AI consumption

### Example: Hybrid Workflow

```
User: "Research AI trends and write an article"
  ↓
IDE AI:
  1. superskills call researcher "AI automation trends" --json
  2. Parse JSON output
  3. superskills call author --input research.md --json
  4. Refine and deliver
```

**See [IDE_INTEGRATION.md](docs/IDE_INTEGRATION.md) for complete guide.**

## SuperSkills CLI

The SuperSkills CLI provides command-line access to all skills and workflows.

### Key Commands

```bash
# List all skills
superskills list

# Call individual skill
superskills call <skill-name> <input>
superskills call researcher "AI automation trends"
superskills call author --input research.md --output article.md

# JSON output mode (for IDE integration)
superskills call author "Write about AI" --json

# Execute workflow
superskills run <workflow-name>
superskills run content-creation --topic "Your topic"
superskills run podcast-generation --input script.txt

# Discover skills by capability
superskills discover --query "voice generation"
superskills discover --task "research and write article"

# Export skill metadata
superskills export --markdown
superskills export --output metadata.json

# Manage workflows
superskills workflow list

# Check status
superskills status
```

### Features

- **40 Skills Available**: All prompt-based and Python-powered skills
- **Pre-Built Workflows**: Content creation, podcasts, training materials, client engagement
- **Custom Workflows**: Create your own multi-skill pipelines in YAML
- **Flexible Execution**: Run skills individually or chain them together
- **JSON Output Mode**: Structured responses for IDE integration
- **Skill Discovery**: Find skills by capability or task description
- **Metadata Export**: Generate skill reference documentation
- **Stdin Support**: Pipe workflows and chain commands
- **Configuration Management**: Stored in `~/.superskills/`
- **Works Anywhere**: Run from any directory once installed

See [CLI_SETUP.md](dev/CLI_SETUP.md) for installation and detailed usage.

## Development Guidelines

**For IDE AI Assistants:**

This project follows strict conventions to ensure consistency and security. When working on SuperSkills:

1. **Read `.cursorrules`** - Comprehensive development workflow rules
2. **Use `superskills/` directory only** - Single canonical location for all skills
3. **Genericize everything** - No hardcoded personal information in committed code
4. **Follow PROFILE.md pattern** - Personal content → PROFILE.md (gitignored), templates → PROFILE.md.template (committed)
5. **Configuration over constants** - Use JSON/YAML config files for user customization

**Key Principles:**
- **Genericization**: Personal content belongs in PROFILE.md files, not code
- **Configuration**: User-facing settings in voice_profiles.json, brand_style parameters, etc.
- **Security**: Never commit .env or PROFILE.md files
- **Testing**: Mock all external APIs, maintain 80%+ coverage
- **Documentation**: Update CHANGELOG.md for all notable changes

See [.cursorrules](.cursorrules) for complete guidelines and code examples.

## Personal Profile System

Each skill uses a `PROFILE.md` file to match your brand voice and expertise. Never committed to git.

**Setup:**
1. Copy `PROFILE.md.template` to `PROFILE.md` in each skill directory
2. Fill in your name, role, voice characteristics, and examples
3. Skills automatically load your profile when activated

**Example:**
```bash
cp superskills/author/PROFILE.md.template superskills/author/PROFILE.md
# Edit superskills/author/PROFILE.md with your info
```

## Project Structure

```
superskills/
├── superskills/          # 45 skill directories (30 Claude Skills + 15 Python skills)
│   ├── author/           # Claude Skill: SKILL.md + PROFILE.md.template
│   ├── craft/            # Python skill with API integration
│   ├── narrator/         # Python skill family: ElevenLabs voice generation
│   │   ├── podcast/      # Subskill: narrator-podcast
│   │   ├── meditation/   # Subskill: narrator-meditation
│   │   ├── educational/  # Subskill: narrator-educational
│   │   ├── marketing/    # Subskill: narrator-marketing
│   │   ├── social/       # Subskill: narrator-social
│   │   └── src/          # Shared Python implementation
│   ├── designer/         # Python skill: AI image generation
│   ├── developer/        # Claude Skill: SKILL.md + PROFILE.md.template
│   └── ...
├── docs/                 # Documentation
├── tests/                # 90+ unit tests
├── scripts/              # Utility scripts
├── template/             # Skill creation template
└── archive/              # Legacy/incomplete code
```

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Install Development Dependencies
```bash
pip install -e ".[dev]"
```

### Create New Skill
```bash
# Use template as starting point
cp -r template/ superskills/my-new-skill/
cd superskills/my-new-skill/
# Edit SKILL.md with your skill definition
```

## Requirements

**Core:**
- Python 3.9+
- requests>=2.31.0
- python-dotenv>=1.0.0

**AI Services (optional):**
- openai>=1.0.0 (Transcriber, QuizMaker)
- anthropic>=0.7.0 (Alternative summarization)
- google-generativeai>=0.3.0 (Designer)
- elevenlabs>=0.2.0 (Narrator)

**Development:**
- pytest>=7.4.0
- pytest-mock>=3.12.0
- black>=23.0.0
- ruff>=0.1.0

See `requirements.txt` for complete list.

## Credential Management

SuperSkills uses a hybrid credential system with priority hierarchy:

1. **Environment variables** (Claude Desktop)
2. **Global `.env`** (repository root)
3. **Per-skill `.env`** (superskills/{skill}/.env)

**Currently configured skill-specific .env files:**
- `superskills/craft/.env` - Craft Docs API
- `superskills/designer/.env` - Gemini/Midjourney
- `superskills/narrator/.env` - ElevenLabs
- `superskills/transcriber/.env` - OpenAI/AssemblyAI

**Security:**
- All `.env` files gitignored
- Only `.env.template` files committed
- Validation script masks sensitive values
- Use `scripts/distribute_credentials.py` to sync credentials to skills
- See `docs/CREDENTIAL_SETUP.md` for API key setup

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Credits

Built on [Anthropic's Agent Skills framework](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).

## Contributing

Contributions welcome! See [CONTRIBUTING.md](dev/CONTRIBUTING.md) for guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/CoachSteff/superskills/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CoachSteff/superskills/discussions)
