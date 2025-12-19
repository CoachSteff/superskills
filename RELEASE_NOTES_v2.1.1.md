# Release Notes - SuperSkills v2.1.1

**Release Date:** December 19, 2024  
**Type:** Patch Release  
**Previous Version:** v2.1.0

## Overview

SuperSkills v2.1.1 is a patch release that adds missing media processing dependencies to core requirements, ensuring narrator and designer skills work out-of-the-box without additional installation steps.

## What's Fixed

### 📦 Media Processing Dependencies Now Included

**Problem:** Users had to install optional media dependencies separately for audio and image processing skills.

**Before:**
```bash
pip install superskills          # Narrator/Designer don't work
pip install superskills[media]   # Required extra step
```

**After:**
```bash
pip install superskills          # Everything works
```

**Dependencies Added:**
- **`pydub>=0.25.0`** - Audio manipulation for narrator skill
- **`audioop-lts>=0.2.0`** - Audio operations (Python 3.13+ compatibility)
- **`Pillow>=10.0.0`** - Image processing for designer skill

**Impact:**
- ✅ Narrator skill works immediately after installation
- ✅ Designer skill works immediately after installation
- ✅ Python 3.13+ compatibility ensured
- ✅ Simpler installation experience

---

## Files Modified

### Package Configuration (1 file)

**`pyproject.toml`**
- Added `pydub>=0.25.0` to core dependencies
- Added `audioop-lts>=0.2.0; python_version >= '3.13'` for Python 3.13+ support
- Added `Pillow>=10.0.0` to core dependencies
- Version bump: `2.1.0` → `2.1.1`

**Note:** These dependencies were previously in the optional `[media]` extras section, now moved to core `dependencies` list.

---

## Installation

### New Installation
```bash
git clone https://github.com/CoachSteff/superskills.git
cd superskills
bash setup.sh
```

### Upgrade from v2.1.0
```bash
cd /path/to/superskills
git pull origin master
pipx uninstall superskills
pipx install -e .
```

**Note:** The new dependencies will be installed automatically during upgrade.

---

## Verification

After upgrading, verify media skills work:

```bash
# Check version
superskills --version
# Output: SuperSkills v2.1.1

# Test narrator skill (requires ELEVENLABS_API_KEY)
echo "Hello world" | superskills call narrator

# Test designer skill (requires GEMINI_API_KEY)
superskills call designer "A sunset over mountains"

# Both should work without "ModuleNotFoundError"
```

---

## Breaking Changes

**None** - This is a backward-compatible patch release.

---

## Migration Guide

No migration required. Dependencies are installed automatically during upgrade.

---

## Python 3.13+ Compatibility

The `audioop-lts` package is conditionally installed for Python 3.13+:
```toml
"audioop-lts>=0.2.0; python_version >= '3.13'"
```

This ensures the deprecated `audioop` module is replaced with a maintained alternative on newer Python versions.

---

## Known Issues

None at this time.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/CoachSteff/superskills/issues)
- **Discussions:** [GitHub Discussions](https://github.com/CoachSteff/superskills/discussions)
- **Documentation:** [README.md](README.md)

---

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

## Credits

**Fixed by:** Verdent AI Documentation Agent  
**Date:** December 19, 2024  
**Release:** SuperSkills v2.1.1 - Media Dependencies Patch
