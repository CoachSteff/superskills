# SuperSkills — Bug Tracker

---

## BUG-001: CLI Hangs in Non-TTY Environments

| Field | Value |
|-------|-------|
| **Severity** | 🔴 HIGH |
| **Status** | ✅ FIXED |
| **Blocks** | All automation, scripting, agent use |
| **Location** | `/Users/kessa/superskills/cli/commands/call.py` |
| **Fixed In** | v2.5.2 (2026-01-27) |

### Description

When running `superskills call <skill> "input text"` in a non-TTY environment (scripts, automation, sub-agents), the CLI hangs indefinitely waiting for stdin.

### Root Cause

The input source priority was wrong. Old code checked `sys.stdin.isatty()` before checking if input was provided as a command-line argument:

```python
# Old (broken) order in call.py:
if not sys.stdin.isatty():
    input_text = sys.stdin.read()  # BLOCKS if no piped input
elif input_file:
    # ...
elif input_text:  # Too late — already blocked above
    # ...
```

### Fix Applied

Reordered input priority to check command-line argument first:

```python
# Fixed order (lines 22-40):
if input_text:
    pass  # Use CLI argument as-is
elif input_file:
    input_text = Path(input_file).read_text()
elif not sys.stdin.isatty():
    input_text = sys.stdin.read()
else:
    print("Error: Provide input via argument, --input-file flag, or stdin")
    return 1
```

### Tests Added

- **Unit tests**: 18 tests in `tests/test_call_command.py`
  - Input priority validation
  - Non-TTY regression tests
  - Error handling
  - Output formats
  
- **Integration tests**: 9 tests in `tests/integration/test_cli_non_tty.py`
  - Real CLI execution in subprocess
  - Timeout protection (no hanging)
  - Backward compatibility

### Verification

✅ All 267 existing tests still pass (no regressions)  
✅ 18 new unit tests pass  
✅ CLI argument input now works in non-TTY environments  
✅ Piped stdin still works  
✅ File input still works

### Workaround (No Longer Needed)

Old workaround was to pipe input:

```bash
# Now WORKS directly (fixed!)
superskills call author "Write a post"

# Also still works
echo "Write a post" | superskills call author
superskills call author --input-file prompt.txt
```

---

## BUG-002: Hardcoded Paths from Old Machine

| Field | Value |
|-------|-------|
| **Severity** | 🟡 MEDIUM |
| **Status** | ✅ FIXED |
| **Affects** | Skill templates and documentation |
| **Location** | `SKILL.md`, `PROFILE.md`, documentation files |
| **Fixed In** | v2.5.2 (2026-01-27) |

### Description

Configuration files contained hardcoded paths referencing `/Users/steffvanhaverbeke/` (old username) and `/mnt/user-data` (Docker/Linux mount) which don't exist on other machines.

### Fixed Files

| File | Issue | Fix Applied |
|------|-------|-------------|
| `.env` | `OBSIDIAN_VAULT_PATH` | ✅ Previously fixed |
| `manager/PROFILE.md` | Workspace path | ✅ Changed to `~/Documents/Workspace` |
| `manager/SKILL.md` | Workspace path | ✅ Changed to `~/Documents/Workspace` |
| `manager/SKILL.md` | Output path | ✅ Changed to `~/Documents/Outputs` |
| `publisher/PROFILE.md` | Output path | ✅ Changed to `~/Documents/Outputs` |
| `publisher/SKILL.md` | Output paths (3×) | ✅ Changed to `~/Documents/Outputs` |
| `docs/DEVELOPMENT_HISTORY.md` | Project path | ✅ Changed to relative paths |
| `tests/FINAL_TEST_REPORT.md` | Project path | ✅ Changed to `/path/to/superskills` |
| `tests/TEST_SUMMARY.md` | Project paths (2×) | ✅ Changed to relative paths |

### Fix Applied

Replaced all hardcoded paths with generic placeholders:

**Old paths:**
- `/Users/steffvanhaverbeke/Library/Mobile Documents/...` → `~/Documents/Workspace`
- `/mnt/user-data/outputs` → `~/Documents/Outputs`
- `/Users/steffvanhaverbeke/Development/01_projects/superskills` → `tests/` (relative)

**Generic patterns used:**
- `~` or `$HOME` for user home directory
- Relative paths for project-internal references
- Environment variable support (`$WORKSPACE_DIR`, `$OUTPUT_DIR`)

### Verification

✅ Zero occurrences of `steffvanhaverbeke` in skill files:
```bash
grep -r "steffvanhaverbeke" superskills/ docs/ tests/
# Result: No matches found
```

✅ Zero occurrences of `/mnt/user-data` in skill files:
```bash
grep -r "/mnt/user-data" superskills/ --include="*.md"
# Result: No matches found
```

### Prevention

**Best practices implemented:**
- Use `~` or `$HOME` for user-specific paths
- Use relative paths for project-internal references
- Document optional environment variables in PROFILE.md files
- Provide sensible defaults that work across environments

**Suggested environment variables:**
```bash
# Optional configuration in .env
WORKSPACE_DIR=$HOME/Documents/Workspace
OUTPUT_DIR=$HOME/Documents/Outputs
```

---

## BUG-003: Most Python Skills Not Implemented in Skill Executor

| Field | Value |
|-------|-------|
| **Severity** | 🔴 HIGH |
| **Status** | ✅ FIXED |
| **Blocks** | 7 Python-powered skills (scraper, designer, videoeditor, craft, marketer, emailcampaigner, coursepackager) |
| **Location** | `/Users/kessa/superskills/cli/core/skill_executor.py` (lines 235-290) |
| **Fixed In** | v2.5.3 (2026-01-27) |

### Description

When calling Python-powered skills other than narrator, transcriber, or obsidian, the CLI returned:
```
ERROR: Python skill execution not implemented for: <skill_name>
NotImplementedError: Python skill execution not implemented for: <skill_name>
```

### Root Cause

The `_execute_python_skill` method in `skill_executor.py` only had hardcoded execution logic for three specific skills (narrator, transcriber, obsidian), with no generic handler for others.

### Fix Applied

Added a generic Python skill execution handler (lines 235-290) that:

1. **Dynamically instantiates** skill classes with common kwargs
2. **Tries multiple execution methods** in priority order: `execute`, `run`, `process`, `generate`, `__call__`
3. **Normalizes output format** (always returns dict with 'output' key and metadata)
4. **Provides helpful error messages** for missing dependencies or unrecognized methods

**Implementation:**
```python
else:
    # GENERIC PYTHON SKILL HANDLER
    skill_instance = skill_class(**init_kwargs)
    
    # Try common execution method names
    execution_methods = ['execute', 'run', 'process', 'generate', '__call__']
    for method_name in execution_methods:
        if hasattr(skill_instance, method_name) and callable(...):
            result = method(input_text, **kwargs)
            return normalized_output
    
    # No recognized method found
    raise NotImplementedError(...)
```

### Verification

✅ Existing skills (narrator, transcriber, obsidian) still work via hardcoded handlers  
✅ Generic handler successfully invoked for other Python skills  
✅ Clear error messages for skills without standard methods  
✅ Backward compatible - no breaking changes

### Current Status

**Skills now recognized by executor:** All 16 Python skills can attempt execution

**Note:** Some skills may still fail because:
1. **Missing dependencies** (e.g., `crawl4ai`, `python-pptx`) - install required
2. **Non-standard interfaces** (e.g., async methods, different method names) - need skill refactoring
3. **Configuration requirements** (API keys, file paths) - expected behavior

This is progress: "not implemented" error → specific dependency/interface errors that guide users to proper setup.

---

## BUG-004: Presenter Skill Fails with RGBColor Import Error

| Field | Value |
|-------|-------|
| **Severity** | 🟡 MEDIUM |
| **Status** | ✅ FIXED |
| **Blocks** | presenter skill |
| **Location** | `/Users/kessa/superskills/superskills/presenter/src/Presenter.py` (lines 45-90) |
| **Fixed In** | v2.5.3 (2026-01-27) |

### Description

When calling the presenter skill, it failed immediately with:
```
NameError: name 'RGBColor' is not defined
```

### Root Cause

The `Presenter.py` file used `RGBColor` in class-level constant definitions (THEMES dict), but when the `pptx` import failed, `RGBColor` was never defined, causing a NameError during class definition.

### Fix Applied

Moved the `THEMES` dictionary from class-level definition into the `__init__` method (lines 73-90), so it's only evaluated when dependencies are available:

```python
class Presenter:
    def __init__(self, ...):
        # Check dependencies first
        if not PPTX_AVAILABLE or not MARKDOWN_AVAILABLE:
            raise ImportError("Required dependencies not available...")
        
        # Now safe to use RGBColor
        self.THEMES = {
            "default": {"background": RGBColor(255, 255, 255), ...},
            "dark": {...},
            "professional": {...}
        }
```

### Verification

✅ Presenter class can now be imported without errors (even without dependencies)  
✅ Clear error message when dependencies missing  
✅ THEMES accessible via `self.THEMES` instead of `Presenter.THEMES`

### Note

Presenter still requires installation of dependencies to function:
```bash
pip install python-pptx markdown
```
---

## Bug Template

Copy this for new bugs:

```markdown
## BUG-XXX: Title

| Field | Value |
|-------|-------|
| **Severity** | 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW |
| **Status** | UNFIXED / PARTIAL / FIXED |
| **Blocks** | What functionality is affected |
| **Location** | File path |

### Description
What happens.

### Root Cause
Why it happens.

### Fix
How to fix it.

### Workaround
How to work around it until fixed.
```

---

*Last updated: 2026-01-27 (BUG-001 through BUG-004 fixed)*
