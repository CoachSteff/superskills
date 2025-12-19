# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

SuperSkills is a comprehensive AI automation toolkit with **40 skills** built on Anthropic's Agent Skills framework. The project uses a dual-architecture approach:
- **29 Claude Skills** (folder-based with SKILL.md) - Prompt-based AI specialists
- **11 Python-Powered Skills** - Full API integrations with advanced automation

**Target users**: Freelance coaches, trainers, and content creators who want to automate repetitive business tasks.

## Common Development Commands

### Installation & Setup
```bash
# Install all dependencies (including dev)
pip install -e ".[dev]"

# Install with optional media support
pip install -e ".[media]"

# Install everything
pip install -e ".[all]"

# Set up credentials
cp .env.template .env
# Edit .env with your API keys

# Verify credential setup
python scripts/validate_credentials.py
```

### Testing
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run tests with coverage report
pytest tests/ --cov=superskills --cov-report=html

# Run specific test file
pytest tests/test_craft.py -v

# Run tests for a specific function
pytest tests/test_craft.py::test_create_document -v
```

### Code Quality
```bash
# Format code with Black (line length 100)
black . --line-length 100

# Run Ruff linter
ruff check .

# Run both formatting and linting
black . --line-length 100 && ruff check .
```

## Architecture Overview

### Directory Structure
```
superskills/
├── superskills/          # All 43 skill directories
│   ├── author/           # Prompt-only: .skill + SKILL.md + PROFILE.md.template
│   ├── craft/            # Python skill: API integration with Craft Docs
│   ├── developer/        # Prompt-only skill
│   ├── designer/         # Production pattern: README, SKILL.md, src/, tests/
│   ├── marketer/         # Full Postiz API integration
│   └── narrator/         # ElevenLabs text-to-speech integration
│   └── ...               # more skills
├── tests/                # 90+ unit tests, all APIs mocked
├── docs/                 # User documentation
├── scripts/              # Utility scripts (validate_credentials.py)
└── template/             # Template for creating new skills
```

### Two Skill Development Patterns

**Pattern 1: Prompt-Only Skill** (Fast iteration, no dependencies)
- Located in: `superskills/{skill-name}/`
- Files: `{skill-name}.skill`, `SKILL.md`, `PROFILE.md.template`
- Use for: Instructions/workflows without external APIs

**Pattern 2: Python-Powered Skill** (API integrations, complex logic)
- Located in: `superskills/{skill-name}/` or `new-skills/{skill-name}/`
- Files: `README.md`, `SKILL.md`, `PROFILE.md.template`, `src/`, `tests/`, `requirements.txt`, `.env.template`
- Use for: API integrations (OpenAI, Gemini, ElevenLabs, Craft, Postiz, etc.)

### Credential Management

**Priority Hierarchy:**
1. Environment variables (Claude Desktop) - highest priority
2. Global `.env` (repository root)
3. Per-skill `.env` (superskills/{skill}/.env) - lowest priority

**Critical Security Rules:**
- ✅ All `.env` files are gitignored
- ✅ Only `.env.template` files are committed
- ✅ `validate_credentials.py` masks sensitive values
- ❌ NEVER commit `.env` files or API keys
- ❌ NEVER commit `PROFILE.md` files (contain personal info)

### Personal Profile System

Each skill uses a `PROFILE.md` file to match the user's brand voice and expertise:
- `PROFILE.md.template` - Template for users (committed to git)
- `PROFILE.md` - User's personal profile (gitignored, never committed)

When creating/editing skills, always provide a `PROFILE.md.template` but never create or commit actual `PROFILE.md` files.

## Key Python Skills & APIs

| Skill | API Provider | Key Capabilities |
|-------|--------------|------------------|
| craft | Craft Docs API | Document management, export, collaboration |
| designer | Gemini Imagen, Midjourney | AI image generation, brand consistency |
| marketer | Postiz API | Social media scheduling, multi-platform posting |
| narrator | ElevenLabs | Text-to-speech, podcast generation |
| transcriber | Whisper, AssemblyAI | Audio/video transcription |

## Testing Requirements

**Critical Testing Rules:**
1. **All external APIs MUST be mocked** - No real API calls in tests
2. Use pytest fixtures from `tests/conftest.py` for common mocks
3. Target 80%+ coverage for Python skills
4. Mock environment variables using `mock_env_vars` fixture

**Example test pattern:**
```python
def test_api_call(mocker, mock_env_vars):
    mock_api = mocker.patch('requests.post')
    mock_api.return_value.json.return_value = {'success': True}
    
    result = my_function()
    
    assert result.success == True
    mock_api.assert_called_once()
```

## Creating a New Skill

### Prompt-Only Skill
```bash
mkdir superskills/my-skill
cp template/SKILL.md superskills/my-skill/SKILL.md
cp template/PROFILE.md.template superskills/my-skill/PROFILE.md.template
 
# Edit SKILL.md with YAML frontmatter + instructions
```

### Python-Powered Skill
Use `new-skills/designer/` as reference template. Include:
- README.md with usage examples
- SKILL.md with agent capabilities
- PROFILE.md.template for personalization
- src/ with implementation
- tests/ with mocked API tests
- requirements.txt with dependencies
- .env.template with credential placeholders

## Important Patterns

### Credential Loading
```python
from dotenv import load_dotenv
import os

# Load from skill-specific .env first, then global
load_dotenv(Path(__file__).parent / ".env")
load_dotenv()

api_key = os.getenv("API_KEY")
```

### Testing with Mocks
```python
# Use conftest.py fixtures
def test_with_mocks(mock_env_vars, temp_output_dir, mock_requests_response):
    # Tests run without real API calls
    pass
```

### Skill Organization
- Claude skills go in `superskills/{skill-name}/`
- Production Python pattern reference in `new-skills/`
- Legacy/incomplete code in `archive/` (preserved for reference only)

## Dependencies

**Core (required):**
- Python 3.9+
- requests>=2.31.0
- python-dotenv>=1.0.0

**AI Services (optional, install as needed):**
- openai>=1.0.0 (Transcriber, QuizMaker)
- anthropic>=0.7.0 (SummarizAIer)
- google-generativeai>=0.3.0 (Designer)
- elevenlabs>=0.2.0 (Narrator)

**Development:**
- pytest>=7.4.0
- pytest-mock>=3.12.0
- black>=23.0.0 (line-length 100)
- ruff>=0.1.0

## Code Style

- **Line length**: 100 characters (enforced by Black and Ruff)
- **Python version**: 3.9+ (see pyproject.toml)
- **Formatting**: Use Black with `--line-length 100`
- **Linting**: Ruff with E, F, I, N, W rules (E501 ignored)

## What NOT to Do

- ❌ Commit `.env` files or `PROFILE.md` files
- ❌ Make real API calls in tests
- ❌ Log API keys or credentials
- ❌ Add dependencies without updating requirements.txt/pyproject.toml
- ❌ Create skills without PROFILE.md.template
- ❌ Skip test coverage for Python skills
