# SuperSkills Architecture

## Overview

Dual-architecture approach combining Claude Skills (prompt-based) with Python-powered skills (API integrations). The repository contains **43 total skills**: 20 pure prompt-based Claude Skills and 23 Python-powered skills with optional implementations.

## Directory Structure

### `/superskills/` - All Skill Definitions
43 skill directories with varying levels of implementation. This is the **single canonical location** for all skills.

**Prompt-Only Skills (20 Claude Skills):**
- Pure prompt/instruction-based
- No Python code required
- Instant activation in Claude Desktop
- Packaged as ZIP files containing SKILL.md

**Python-Powered Skills (23 implementations):**
- API integrations (Craft, ElevenLabs, Postiz, etc.)
- Advanced automation logic
- Full src/ directory with tested code

**Pattern:**
```
superskills/{skill-name}/
├── SKILL.md             # Skill definition (all skills)
├── PROFILE.md           # Personal profile (gitignored)
├── PROFILE.md.template  # Profile template (committed)
└── src/                 # Python implementation (Python skills only)
    ├── *.py             # Implementation modules
    └── tests/           # Unit tests
```

**Claude Skills are imported as ZIP files:**
- Folder structure: `{skill-name}/SKILL.md`
- ZIP the folder: `zip -r {skill-name}.zip {skill-name}/`
- Import in Claude Desktop Settings → Skills

**Example Python Skills:**
- `superskills/narrator/` - ElevenLabs voice generation with voice_profiles.json
- `superskills/designer/` - AI image generation with brand_style configuration
- `superskills/craft/` - Craft Docs API integration

### `/docs/` - Documentation
- CREDENTIAL_SETUP.md, QUICKSTART.md, SKILL_DEVELOPMENT.md

### `/tests/` - Test Suite
90+ unit tests, all external APIs mocked

### `/archive/` - Legacy Code
6 incomplete skills preserved for reference

## Skill Development Patterns

### Pattern 1: Prompt-Only Skill
**Use for:** Instructions/workflows without external APIs
- Fast iteration, no dependencies
- SKILL.md + PROFILE.md.template only

### Pattern 2: Python-Powered Skill
**Use for:** API integrations, complex logic
- Full infrastructure (src/, tests/, etc.)
- Testable with mocked APIs

## Credential Management

**Priority Hierarchy:**
1. Environment variables (Claude Desktop)
2. Global `.env` (repository root)
3. Per-skill `.env` (superskills/{skill}/.env)

**Example: Skill-Specific .env in Action**

```bash
# Global .env (root)
OPENAI_API_KEY=sk-global-key-abc123
GEMINI_API_KEY=AIza-global-key-xyz789

# superskills/transcriber/.env (overrides global for this skill)
OPENAI_API_KEY=sk-transcriber-specific-key-def456

# When Transcriber runs:
# Uses: sk-transcriber-specific-key-def456 (per-skill overrides global)
```

**Currently configured skill-specific .env files:**
- `superskills/craft/.env` - Craft Docs API
- `superskills/designer/.env` - Gemini/Midjourney  
- `superskills/narrator/.env` - ElevenLabs
- `superskills/transcriber/.env` - OpenAI/AssemblyAI

**Security:**
- All `.env` files gitignored
- Only `.env.template` committed
- Validation script masks values
- Distribution script syncs credentials from root to skills

## Personal Profile System

**Purpose:** Customize AI to user's brand voice without committing personal info

**Files:**
- `PROFILE.md` - User's profile (gitignored)
- `PROFILE.md.template` - Template (committed)

**Loading:** Skill activates → Claude loads PROFILE.md → AI matches user's voice

## Testing Strategy

**All external APIs mocked** - No real API calls in tests

**Coverage Target:** 80%+ for Python skills

```bash
pytest tests/ --cov=superskills --cov-report=html
```

## Design Decisions

**Why Single Directory Structure?**
- Clear canonical location (superskills/ only)
- No confusion between duplicate implementations
- Easier navigation and maintenance

**Why Configuration Files?**
- User customization without code changes
- Examples: voice_profiles.json, brand_style parameter
- Validates settings and provides defaults

**Why Hybrid Credentials?**
- Flexibility for different user types
- Security (no hardcoded credentials)

**Why PROFILE.md Files?**
- Personalization without public exposure
- Each user has unique brand voice
- Gitignored for privacy

## Integration Patterns

**Skill-to-Skill:** craft + transcriber, scraper + researcher

**External Services:** OpenAI, Anthropic, Gemini, ElevenLabs, Craft Docs, Postiz

## Security

- ✅ `.gitignore` excludes `.env`, `PROFILE.md`
- ✅ Validation script masks values
- ❌ NEVER log API keys
- ❌ NEVER commit credentials or personal info
