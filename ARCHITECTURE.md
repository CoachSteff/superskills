# SuperSkills Architecture

## Overview

Dual-architecture approach combining Claude Skills (prompt-based) with Python-powered skills (API integrations).

## Directory Structure

### `/superskills/` - Claude Skill Definitions
20 .skill files with YAML frontmatter + Markdown instructions

**Pattern:**
```
superskills/{skill-name}/
├── SKILL.md              # Skill definition (committed)
├── PROFILE.md            # Personal profile (gitignored)
└── PROFILE.md.template   # Profile template (committed)
```

### `/new-skills/` - Python-Powered Skills
3 production-ready skills with full infrastructure

**Pattern:**
```
new-skills/{skill-name}/
├── README.md, SKILL.md, PROFILE.md.template
├── src/, tests/, requirements.txt, .env.template
```

**Skills:** designer (Gemini), marketer (Postiz), narrator (ElevenLabs)

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

**Security:**
- All `.env` files gitignored
- Only `.env.template` committed
- Validation script masks values

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
