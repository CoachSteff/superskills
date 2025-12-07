# SuperSkills - AI-Powered Automation Skills for Claude

Custom skill library for Claude Desktop that automates coaching, training, and content creation workflows. Built on Anthropic's Agent Skills framework.

## Overview

SuperSkills is a comprehensive AI automation toolkit with **43 skills** that transform repetitive business tasks into automated workflows. Designed for freelance coaches, trainers, and content creators who want to scale their operations without proportional effort increases.

**What You Get:**
- 20 Claude Skills (.skill files) - Prompt-based AI specialists, no Python required
- 23 Python-Powered Skills - Full API integrations with advanced automation
- Comprehensive test suite (90+ unit tests)
- Credential management system (hybrid env vars + .env files)
- Production-ready patterns and templates

## Quick Start

### Prerequisites
- Python 3.9+
- Claude Desktop App
- Git

### Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/CoachSteff/superskills.git
   cd superskills
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure credentials:**
   ```bash
   cp .env.template .env
   # Edit .env and add your API keys
   ```

4. **Set up personal profiles:**
   ```bash
   # For each skill you plan to use, copy the profile template:
   cp superskills/author/PROFILE.md.template superskills/author/PROFILE.md
   # Edit PROFILE.md with your brand voice, expertise, and style
   ```

5. **Verify setup:**
   ```bash
   python scripts/validate_credentials.py
   ```

### First Skill Usage

**Example: Using the Transcriber skill**
```bash
# Activate the transcriber skill in Claude Desktop
# Then ask: "Transcribe audio.mp3 using Whisper"
```

## Skill Categories

### 1. Claude Skills (Prompt-Based)
**20 .skill files** in `/superskills/` - No Python dependencies required

These are pure prompt-based skills that work immediately with Claude Desktop:

| Skill | Description |
|-------|-------------|
| **author** | Ghostwriting in your brand voice |
| **builder** | Workflow automation architect |
| **coach** | Coaching session design and delivery |
| **context-engineer** | Optimize AI context for better results |
| **copywriter** | Marketing copy and messaging |
| **designer** | Visual design direction |
| **developer** | Code generation and debugging |
| **editor** | Content editing and quality control |
| **manager** | Project and team coordination |
| **marketer** | Marketing strategy and campaigns |
| **narrator** | Voice and tone guidance |
| **producer** | Media production workflows |
| **publisher** | Content publishing and distribution |
| **quality-control** | Review and validation |
| **researcher** | Research and analysis |
| **sales** | Sales messaging and outreach |
| **scraper** | Web content extraction |
| **strategist** | Strategic planning |
| **translator** | Translation and localization |
| **webmaster** | Website management |

### 2. Python-Powered Skills (API Integrations)
**23 production-ready skills** with Python implementations in `/superskills/` and `/new-skills/`

#### Featured API-Integrated Skills

| Skill | APIs | Capabilities |
|-------|------|--------------|
| **craft** | Craft Docs API | Document management and export |
| **designer** | Gemini Imagen, Midjourney | AI image generation, brand consistency |
| **marketer** | Postiz API | Social media scheduling, multi-platform posting |
| **narrator** | ElevenLabs | Text-to-speech, podcast generation |
| **transcriber** | Whisper, AssemblyAI | Audio/video transcription |

#### Additional Python Skills

business-consultant, community-manager, compliance-manager, coursepackager, developer-tester, emailcampaigner, google-workspace-gemini, influencer, knowledgebase, legal, microsoft-365-copilot, n8n-workflow, presenter, process-engineer, product, risk-manager, trendwatcher, videoeditor

**Pattern:** Each includes SKILL.md definition, optional src/ implementation, and configuration templates

## Featured Workflows

### Content Creation Pipeline
```
1. researcher → Research topic
2. author → Write draft
3. editor → Edit and refine
4. designer → Create visuals
5. marketer → Schedule posts
```

### Training Material Development
```
1. craft → Pull existing docs
2. transcriber → Transcribe workshop recordings
3. author → Write training content
4. publisher → Format and publish
```

### Client Engagement
```
1. scraper → Monitor client websites
2. researcher → Analyze trends
3. copywriter → Draft outreach
4. sales → Personalize messaging
```

## Documentation

- **[Quick Start](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Architecture](ARCHITECTURE.md)** - System design and patterns
- **[Credential Setup](docs/CREDENTIAL_SETUP.md)** - API key configuration guide
- **[Skill Development](docs/SKILL_DEVELOPMENT.md)** - Create custom skills
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines

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
├── superskills/          # 43 skill directories (20 .skill files + 23 Python skills)
│   ├── author/           # .skill + SKILL.md + PROFILE.md.template
│   ├── craft/            # Python skill with API integration
│   ├── developer/        # .skill + SKILL.md + PROFILE.md.template
│   └── ...
├── new-skills/           # Additional Python skill variants
│   ├── designer/         # README, SKILL.md, src/, tests/, requirements.txt
│   ├── marketer/         # README, SKILL.md, src/, tests/, requirements.txt
│   └── narrator/         # README, SKILL.md, src/, tests/, requirements.txt
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

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/CoachSteff/superskills/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CoachSteff/superskills/discussions)
