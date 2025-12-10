# Release Notes - SuperSkills v2.0.1

**Release Date:** December 10, 2025  
**Type:** Critical Patch Release  
**Previous Version:** v2.0.0

## Overview

SuperSkills v2.0.1 is a critical patch release that fixes three blocking issues from v2.0.0 that prevented installation and runtime functionality. **All users should upgrade immediately.**

## What's Fixed

### 🔴 CRITICAL: Invalid Model Name (404 Errors)

**Problem:** CLI used `claude-sonnet-4` which doesn't exist in the Anthropic API.

**Symptom:**
```
Error: model: claude-sonnet-4 does not exist
```

**Solution:** Changed to `claude-4.5-sonnet` (latest Sonnet model) in all locations:
- `cli/utils/api_client.py` - Default parameter
- `cli/utils/config.py` - Default configuration
- `cli/core/skill_executor.py` - Fallback model
- `docs/IDE_INTEGRATION.md` - Documentation

**Impact:** Skills now execute without model errors.

---

### 🔴 CRITICAL: Environment Variables Not Loading

**Problem:** CLI didn't load `.env` files, causing API key errors even when `.env` existed.

**Symptom:**
```
Error: ANTHROPIC_API_KEY not found
# Even though .env file exists with the key
```

**Solution:** 
- Added `load_dotenv()` to `cli/main.py` entry point for global .env loading
- Added skill-specific credential loading to `cli/core/skill_executor.py`

**Correct Precedence Order** (highest to lowest):
1. **System environment variables** (always respected)
2. **Skill-specific `.env`** (`superskills/{skill}/.env`) - overrides global for that skill
3. **User config `.env`** (`~/.superskills/.env`)
4. **Project root `.env`**

**Example:**
```bash
# Global API key for all skills
echo "ELEVENLABS_API_KEY=global_key" > .env

# Override for narrator skill only
echo "ELEVENLABS_API_KEY=narrator_key" > superskills/narrator/.env

# Test precedence
superskills call copywriter "test"  # Uses: global_key
superskills call narrator "test"    # Uses: narrator_key

# System env always wins
export ELEVENLABS_API_KEY=system_key
superskills call narrator "test"    # Uses: system_key
```

**Impact:** 
- API keys correctly loaded from `.env` files
- Skill-specific configurations override global settings
- System environment variables always take precedence

---

### 🔴 CRITICAL: Cached Invalid Configuration

**Problem:** Users upgrading from v2.0.0 had cached `~/.superskills/config.yaml` with invalid model name.

**Symptom:**
```
# Config file contains:
model: claude-sonnet-4  # Invalid!
```

**Solution:** Auto-regeneration system in `cli/utils/config.py`:
- Detects version mismatch
- Detects invalid model name
- Automatically regenerates with correct defaults
- Shows warning message

**Impact:** No manual deletion of config files required - automatic migration.

---

### 🟡 MINOR: setup.sh Input Handling

**Problem:** User input with trailing whitespace (e.g., "1 ") wasn't recognized.

**Solution:** Trim whitespace from input in `setup.sh`.

**Impact:** More reliable installation experience.

---

## Installation

### New Installation

```bash
git clone https://github.com/CoachSteff/superskills.git
cd superskills
bash setup.sh
```

### Upgrade from v2.0.0

```bash
cd /path/to/superskills
git pull origin master
pipx uninstall superskills
pipx install -e .
```

**Note:** Config auto-regenerates on first run - no manual intervention needed.

---

## Verification

After upgrading, verify the fixes:

```bash
# 1. Check version
superskills --version
# Output: superskills 2.0.1

# 2. Verify config has correct model
cat ~/.superskills/config.yaml | grep model
# Output: model: claude-4.5-sonnet

# 3. Test .env loading (create test .env first)
echo 'ANTHROPIC_API_KEY=test-key' > .env
superskills list
# Should not error about missing API key

# 4. Test actual skill (requires real API key)
superskills call researcher "AI trends"
# Should succeed without 404 error
```

---

## Files Modified

### Code Changes (5 files)

1. **`cli/utils/api_client.py`**
   - Changed default model parameter: `claude-sonnet-4` → `claude-4.5-sonnet`

2. **`cli/utils/config.py`**
   - Updated default model in config: `claude-4.5-sonnet`
   - Added version tracking: `version: 2.0.1`
   - Added auto-regeneration logic for outdated configs

3. **`cli/core/skill_executor.py`**
   - Changed fallback model: `claude-sonnet-4` → `claude-4.5-sonnet`
   - Added skill-specific credential loading (`load_credentials()`)
   - Ensures skill-specific `.env` files override global settings

4. **`cli/main.py`**
   - Added `load_dotenv()` import and function call
   - Loads `.env` from user config (`~/.superskills/.env`)
   - Loads `.env` from project root (with correct precedence)
   - Documented precedence order in comments

5. **`setup.sh`**
   - Added whitespace trimming for user input

### Documentation Updates (3 files)

1. **`docs/IDE_INTEGRATION.md`**
   - Updated model reference to `claude-4.5-sonnet`

2. **`QUICKSTART.md`**
   - Added troubleshooting sections:
     - Model 404 error solutions
     - .env loading explanation
     - Config regeneration instructions

3. **`CHANGELOG.md`**
   - Added v2.0.1 release notes

### Version Bump (1 file)

1. **`pyproject.toml`**
   - Version: `2.0.0` → `2.0.1`

---

## Breaking Changes

**None** - This is a backward-compatible patch release.

---

## Migration Guide

### Automatic Migration

No action required. On first run of v2.0.1:
1. CLI detects outdated config
2. Shows warning: `⚠ Outdated config detected. Regenerating with claude-4.5-sonnet...`
3. Auto-regenerates `~/.superskills/config.yaml`
4. Continues execution normally

### Manual Migration (if needed)

If you experience issues:

```bash
# Option 1: Delete config (will regenerate automatically)
rm ~/.superskills/config.yaml
superskills init

# Option 2: Edit config manually
# Change in ~/.superskills/config.yaml:
#   version: 2.0.0 → 2.0.1
#   model: claude-sonnet-4 → claude-4.5-sonnet

# Option 3: Reinstall CLI
pipx uninstall superskills
pipx install -e .
```

---

## Known Issues

None at this time.

---

## Testing Summary

### Test Environment
- macOS 15.7.2
- Python 3.11
- Fresh installation from scratch

### Tests Performed

✅ Installation via pipx  
✅ Version detection (`superskills --version`)  
✅ Config generation with correct model  
✅ .env loading from project root  
✅ .env loading from `~/.superskills/`  
✅ Auto-regeneration of v2.0.0 config  
✅ setup.sh option selection  
✅ Skill execution without 404 errors  

---

## Support

- **Issues:** [GitHub Issues](https://github.com/CoachSteff/superskills/issues)
- **Discussions:** [GitHub Discussions](https://github.com/CoachSteff/superskills/discussions)
- **Documentation:** [README.md](README.md)

---

## Credits

**Fixed by:** Verdent AI Documentation Agent  
**Reported by:** Installation test report from v2.0.0 release testing

---

## Next Steps

After upgrading:

1. **Verify installation** (see Verification section above)
2. **Test your workflows** to ensure they work correctly
3. **Report issues** if you encounter any problems
4. **Review documentation** for new features and best practices

---

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.
