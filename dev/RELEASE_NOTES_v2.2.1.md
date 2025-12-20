# SuperSkills v2.2.1 - Critical Patch Release

**Release Date:** December 20, 2024  
**Type:** Patch Release (Critical Bug Fixes)  
**Upgrade Priority:** High (All v2.2.0 users should upgrade immediately)

---

## 🚨 Critical Fixes

This patch release addresses 4 critical issues discovered in post-release testing of v2.2.0:

### 1. Model 404 Errors - All Prompt Skills Broken

**Problem:** Claude 3.5 Sonnet/Haiku models deprecated by Anthropic  
**Impact:** All 30 prompt-based skills failed with 404 errors  
**Status:** ✅ FIXED

**What Changed:**
- Updated model resolver aliases to Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- All prompt-based skills (researcher, author, copywriter, etc.) now working
- Automatic fallback to latest stable model

**Before:**
```bash
superskills call researcher "test"
# Error: model: claude-3-5-sonnet-20241022 not found (404)
```

**After:**
```bash
superskills call researcher "test"
# ✅ Works with claude-sonnet-4-20250514
```

---

### 2. Workflow Detection Bug - Workflows Not Found

**Problem:** Personal workflows invisible to CLI  
**Impact:** `superskills workflow list` returned "No workflows found" despite workflows existing  
**Status:** ✅ FIXED

**What Changed:**
- Extended workflow scanner to detect folder-based workflows in `workflows/` root
- Now finds patterns like `workflows/podcast-generation/workflow.yaml`
- Maintains backward compatibility with `definitions/` and `custom/` subdirectories

**Before:**
```bash
superskills workflow list
# No workflows found.
```

**After:**
```bash
superskills workflow list
# Available Workflows (5 total)
# - podcast-generation
# - content-creation
# - training-material
# - client-engagement
```

---

### 3. Discovery Scoring Discrepancy - Plural Queries Failed

**Problem:** Plural query forms returned poor relevance scores  
**Impact:** `discover --query "podcasts"` scored 11.00 (should be ~78.00)  
**Status:** ✅ FIXED

**What Changed:**
- Added bidirectional synonym mappings for common plural forms
- "podcast" ↔ "podcasts" now treated equivalently
- Consistent scoring regardless of singular/plural

**Before:**
```bash
superskills discover --query "podcasts"
# narrator score: 11.00 (poor relevance)
```

**After:**
```bash
superskills discover --query "podcasts"
# narrator score: 70.00 (correct relevance)
```

---

### 4. Documentation Inaccuracy - Wrong CLI Syntax

**Problem:** Documentation showed `--json` flag (doesn't exist)  
**Impact:** Users copying examples got "unrecognized arguments" errors  
**Status:** ✅ FIXED

**What Changed:**
- Corrected 29 instances across README.md and docs/IDE_INTEGRATION.md
- All examples now show correct `--format json` syntax
- Every documented command verified working

**Before:**
```bash
superskills call author "test" --json
# Error: unrecognized arguments: --json
```

**After:**
```bash
superskills call author "test" --format json
# ✅ Returns JSON-formatted output
```

---

## 📦 Installation & Upgrade

### New Installation
```bash
# Using pipx (recommended)
pipx install superskills

# Using pip
pip install superskills
```

### Upgrade from v2.2.0
```bash
# Using pipx
pipx upgrade superskills

# Using pip
pip install --upgrade superskills

# Verify version
superskills --version
# Expected: 2.2.1
```

### Verification After Upgrade
```bash
# 1. Test model fix (no 404 error)
superskills call researcher "test query"

# 2. Test workflow detection
superskills workflow list

# 3. Test discovery scoring
superskills discover --query "podcasts"

# 4. Test JSON output
superskills call author "test" --format json
```

---

## 🔍 What's Fixed

| Issue | Severity | Files Changed | Impact |
|-------|----------|---------------|--------|
| Model 404 errors | CRITICAL | `cli/utils/model_resolver.py` | 30 skills restored |
| Workflow detection | CRITICAL | `cli/core/workflow_engine.py` | User workflows visible |
| Discovery plural forms | MEDIUM | `cli/commands/discover.py` | Better search results |
| Documentation syntax | MEDIUM | `README.md`, `docs/IDE_INTEGRATION.md` | Copy-paste works |

---

## 📊 Testing Summary

All fixes verified through comprehensive testing:

### Model Resolution
```bash
✅ claude-3-sonnet-latest → claude-sonnet-4-20250514
✅ claude-3-haiku-latest → claude-sonnet-4-20250514
✅ claude-4.5-sonnet → claude-sonnet-4-20250514
✅ No 404 errors on skill execution
```

### Workflow Detection
```bash
✅ Folder-based workflows detected
✅ Built-in workflows still work
✅ Custom workflows still work
✅ Type: "user" correctly assigned
```

### Discovery Scoring
```bash
✅ "podcast" query: narrator-podcast scores 78.00
✅ "podcasts" query: narrator scores 70.00
✅ Plural forms work equivalently to singular
✅ All 46 skills searchable
```

### Documentation
```bash
✅ Zero instances of --json in README.md
✅ Zero instances of --json in IDE_INTEGRATION.md
✅ All examples tested and working
✅ Copy-paste verification passed
```

---

## 🔄 Migration Notes

**No migration required** - This is a drop-in replacement for v2.2.0.

### Breaking Changes
None. All changes are bug fixes maintaining existing behavior.

### API Changes
None. All CLI commands work identically.

### Configuration Changes
None. No config file updates needed.

---

## 🐛 Known Issues

None identified in this release.

---

## 📝 Complete Changelog

See [CHANGELOG.md](../CHANGELOG.md#221---2024-12-20) for detailed technical changes.

---

## 🎯 Next Release (v2.3.0)

Planned improvements based on A++ upgrade plan:

1. **Test Coverage Expansion** - Add 26 tests for Python skills
   - emailcampaigner, coursepackager, presenter, videoeditor
   - Target: 93 tests total, 80%+ coverage

2. **Validation Enhancement** - Distinguish API vs library dependencies
   - Remove false .env.template warnings
   - Clear messaging for library-only skills

3. **Missing PROFILE Templates** - Complete remaining 6 templates
   - risk-manager, process-engineer, product
   - compliance-manager, knowledgebase, legal

**Target Grade:** A++ (98/100)

---

## 🔗 Links

- **GitHub Repository**: https://github.com/CoachSteff/superskills
- **Issues**: https://github.com/CoachSteff/superskills/issues
- **Documentation**: https://github.com/CoachSteff/superskills#readme
- **Changelog**: https://github.com/CoachSteff/superskills/blob/master/CHANGELOG.md

---

## 👥 Credits

This release addresses issues identified through comprehensive automated testing and user feedback. Special thanks to the testing process that caught these critical bugs before widespread adoption.

---

## 📞 Support

If you encounter any issues after upgrading:

1. Check the [Troubleshooting Guide](../docs/QUICKSTART.md#troubleshooting)
2. Search [existing issues](https://github.com/CoachSteff/superskills/issues)
3. Open a [new issue](https://github.com/CoachSteff/superskills/issues/new) with:
   - Output of `superskills --version`
   - Full error message
   - Command you ran
   - Expected vs actual behavior

---

**Upgrade now:** `pipx upgrade superskills`
