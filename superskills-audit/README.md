# SuperSkills Audit

**Owner:** Steff Vanhaverbeke
**Started:** 2026-01-26
**Status:** 🔄 In Progress — 4/49 skills tested, 2 bugs found

---

## Start Here

👉 **[BRIEFING.md](./BRIEFING.md)** — Complete handoff document for any agent picking this up

---

## Files

| File | Purpose |
|------|---------|
| **BRIEFING.md** | Full context, test protocol, current progress |
| **RESULTS.md** | Detailed test results (update as you go) |
| **BUGS.md** | Bug documentation with root causes |

---

## Quick Reference

```bash
# List all 49 skills
superskills list

# Get skill details
superskills info <skill-name>

# Run a skill (ALWAYS pipe input!)
echo "your input" | superskills call <skill-name>
```

⚠️ **Critical:** Do NOT use `superskills call skill "text"` — it hangs in non-TTY environments. Always pipe.

---

## Evaluation Criteria

| Criterion | Description |
|-----------|-------------|
| **Runs** | Executes without errors |
| **Output** | Produces meaningful content |
| **Useful** | Actually helpful, not filler |
| **Accurate** | Information is correct |
| **Voice** | Matches Steff's voice (where relevant) |
| **Actionable** | Output can be used directly |

## Rating Scale

- ✅ **Works** — Production ready
- ⚠️ **Partial** — Works but has issues
- ❌ **Broken** — Does not function
- 🔄 **Untested** — Not yet evaluated

---

*Last updated: 2026-01-26*
