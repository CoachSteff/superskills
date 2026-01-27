# SuperSkills CLI Audit — Agent Briefing

**Owner:** Steff Vanhaverbeke (@CoachSteff)
**Started:** 2026-01-26
**Status:** IN PROGRESS
**Priority:** Complete audit before production use

---

## What Is This?

SuperSkills is Steff's custom CLI tool containing 49 specialized AI skills for content production, business consulting, automation, and more. It lives at `/Users/kessa/superskills/` and is accessible via the `superskills` command.

Your job: **systematically test every skill, document bugs, and ensure it's production-ready.**

---

## Quick Start

```bash
# List all skills
superskills list

# Get help on a skill
superskills info <skill-name>

# Call a skill (IMPORTANT: pipe input to avoid BUG-001)
echo "your input text" | superskills call <skill-name>

# Call with file input
superskills call <skill-name> --input-file /path/to/file.txt
```

---

## Critical Bug You Must Know

### BUG-001: CLI Hangs in Non-TTY Environments (HIGH SEVERITY)

**DO NOT** run skills like this in scripts/automation:
```bash
superskills call author "Write something"  # HANGS FOREVER
```

**ALWAYS** pipe input instead:
```bash
echo "Write something" | superskills call author  # WORKS
```

**Root cause:** `cli/commands/call.py` checks `sys.stdin.isatty()` before checking if input was provided as argument. In non-TTY environments, it blocks waiting for stdin that never comes.

**Fix location:** `/Users/kessa/superskills/cli/commands/call.py` — reorder the input source checks.

---

## Test Protocol

For each skill:

1. **Read the skill info:** `superskills info <skill-name>`
2. **Craft a realistic test input** relevant to Steff's work (AI training, coaching, content creation)
3. **Run the test:** `echo "input" | superskills call <skill-name>`
4. **Evaluate output:** Does it work? Quality? Errors?
5. **Document result** in RESULTS.md

### Test Input Guidelines

Steff's context:
- AI adoption consultant helping organizations integrate AI
- Author of "Being Replaced" (book about AI in the workplace)
- Trainer using Kolb learning cycle (experience → reflection → conceptualization → experimentation)
- "Superworker" framework for AI skill levels
- Based in Belgium, works in Dutch/English/French
- Clients: corporate professionals, L&D teams, executives

Use test inputs that reflect real use cases she'd have.

---

## Current Progress

### ✅ Tested & Working (4/49)

| Skill | Type | Test Summary |
|-------|------|--------------|
| author | Prompt | LinkedIn post about AI training — excellent voice |
| strategist | Prompt | Book promotion strategy — comprehensive 4-week plan |
| translator | Prompt | Dutch translation — good with translator notes |
| obsidian | Python | Vault search — works after path fix |

### ❌ Known Issues (2)

| Bug ID | Severity | Description | Status |
|--------|----------|-------------|--------|
| BUG-001 | HIGH | CLI hangs in non-TTY when input is CLI arg | Documented, unfixed |
| BUG-002 | MEDIUM | Hardcoded `/Users/steffvanhaverbeke/` paths | Partially fixed |

### ⏳ Not Yet Tested

**Prompt-Based (29 remaining):**
- builder, business-consultant, coach, community-manager, compliance-manager
- context-engineer, copywriter, developer, developer-tester, editor
- google-workspace-gemini, helper, influencer, knowledgebase, legal
- manager, microsoft-365-copilot, n8n-workflow, process-engineer, producer
- product, profile-builder, publisher, quality-control, researcher
- risk-manager, sales, transcriber-local, trendwatcher, webmaster

**Python-Powered (15 remaining):**
- coursepackager, craft, designer, emailcampaigner, marketer
- narrator (+ 5 variants), presenter, scraper, transcriber, videoeditor

---

## File Structure

```
/Users/kessa/superskills/          # Main CLI installation
├── cli/                           # CLI source code
│   └── commands/call.py           # BUG-001 location
├── skills/                        # Individual skill folders
│   └── <skill-name>/
│       ├── PROFILE.md             # Skill persona/context
│       └── SKILL.md               # Skill instructions
├── .env                           # Environment config (check paths!)
└── ...

/Users/kessa/clawd/superskills-audit/   # Your working directory
├── BRIEFING.md                    # This file
├── RESULTS.md                     # Test results (update this)
├── BUGS.md                        # Bug documentation
└── README.md                      # Project overview
```

---

## Environment Notes

- **Machine:** macOS (arm64)
- **User:** `kessa` (not `steffvanhaverbeke` — watch for hardcoded paths)
- **Obsidian vault:** `/Users/kessa/Documents/Obsidian Vault` (if testing obsidian skill)
- **Python skills:** May have dependency issues — document any import errors

---

## How to Update Results

Edit `/Users/kessa/clawd/superskills-audit/RESULTS.md`:

```markdown
#### ✅ skill-name
- **Test:** "What you asked it to do"
- **Result:** WORKS | PARTIAL | BROKEN
- **Output Quality:** Brief assessment
- **Notes:** Any issues or observations
```

For bugs, add to `/Users/kessa/clawd/superskills-audit/BUGS.md` following the existing format.

---

## Priority Order

1. **Fix BUG-001** if you can (or escalate to Steff)
2. **Test Python-powered skills** — more likely to have dependency issues
3. **Test remaining prompt skills** — lower risk, faster to validate
4. **Document everything** — future agents need clear handoff

---

## Questions?

Ask Steff via Telegram (@CoachSteff) or leave notes in this folder. When complete, update RESULTS.md with a final summary and mark status as COMPLETE.

---

*Last updated: 2026-01-26 22:30 CET by Kessa*
