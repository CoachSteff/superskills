# SuperSkills Architecture

## Overview

Dual-architecture approach combining Claude Skills (prompt-based) with Python-powered skills (API integrations). The repository contains **43 total skills**: 20 pure prompt-based `.skill` files and 23 Python-powered skills with optional implementations.

## Directory Structure

### `/superskills/` - All Skill Definitions
43 skill directories with varying levels of implementation

**Prompt-Only Skills (20 .skill files):**
- Pure prompt/instruction-based
- No Python code required
- Instant activation in Claude Desktop

**Python-Powered Skills (23 implementations):**
- API integrations (Craft, ElevenLabs, Postiz, etc.)
- Advanced automation logic
- Full src/ directory with tested code

**Pattern:**
```
superskills/{skill-name}/
├── {skill-name}.skill   # Shortcut file (prompt-only skills)
├── SKILL.md             # Skill definition (all skills)
├── PROFILE.md           # Personal profile (gitignored)
├── PROFILE.md.template  # Profile template (committed)
└── src/                 # Python implementation (Python skills only)
```

### `/new-skills/` - Alternative Python Skill Implementations
Additional variants of designer, marketer, narrator with full documentation

**Pattern:**
```
new-skills/{skill-name}/
├── README.md, SKILL.md, PROFILE.md.template
├── src/, tests/, requirements.txt, .env.template
```

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

**Why Dual Architecture?**
- Claude Skills: Fast iteration, no dependencies
- Python Skills: API integrations, testable

**Why new-skills/ Separate?**
- Clear production-ready pattern
- Reference implementations
- Doesn't break existing structure

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
