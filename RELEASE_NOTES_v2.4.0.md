# SuperSkills v2.4.0 Release Notes

**Release Date:** December 21, 2024  
**Commit:** 7aae980

## 🎉 What's New

### Gemini 3 Flash Default Provider
SuperSkills now defaults to Google's Gemini 3 Flash for faster, cost-effective AI processing.
- **Model:** `gemini-3-flash-preview`
- **Benefit:** Faster responses, lower costs, high quality
- **Backward Compatible:** Existing Anthropic configs still work

### Test Command
Simplified testing for contributors and CI/CD:
```bash
superskills test                    # Full test suite
superskills test --quick            # Fast tests only
superskills test --file <name>      # Specific test
superskills test --coverage         # With coverage report
```

### Workflow Setup Automation
Interactive workflow template installation:
- Choose templates during `superskills init`
- 3 built-in templates ready to use
- No more manual copying required

### Transcriber-Local Skill (NEW)
Privacy-focused offline transcription:
- **Zero cloud dependencies** - runs entirely locally
- **GDPR/HIPAA compliant** - no data transmission
- **GPU acceleration** - CUDA and Apple Silicon support
- **5 model sizes** - tiny → large for speed/accuracy trade-offs
- **Unlimited usage** - no API costs

## 📊 Statistics

- **Total Skills:** 48 (30 prompt + 18 Python-powered)
- **Model Registry:** 6 models, 5 legacy aliases
- **Breaking Changes:** None

## 🔧 Technical Changes

### Model Resolution System
- Centralized registry: `cli/config/models.yaml`
- Automatic fallback for invalid model IDs
- Fixes 404 errors with `claude-3-sonnet-latest`
- Multi-provider support (Gemini, Anthropic, OpenAI)

### Configuration Migration
- Auto-migrates from v2.0.1 → v2.4.0
- New structure: `api.provider` + `api.model`
- Legacy structure still supported

### New Files
```
cli/config/models.yaml          - Model registry
cli/commands/test.py            - Test command
cli/utils/version.py            - Version utility
superskills/transcriber-local/  - Local transcription skill
```

## 🚀 Upgrade Instructions

### Fresh Installation
```bash
git pull origin master
pip install -e .
superskills init
```

### Existing Installation
```bash
git pull origin master
pip install -e .
# Config auto-migrates on first run
superskills --version  # Should show v2.4.0
```

### Verify Upgrade
```bash
superskills --version              # SuperSkills v2.4.0
superskills list | wc -l           # 48 skills
superskills test --quick           # Run tests
superskills workflow list          # Check workflows
```

## 📝 Migration Guide

### If You Were Using Anthropic
Your config will auto-migrate. To explicitly use Anthropic:
```bash
superskills config set api.provider anthropic
superskills config set api.model claude-sonnet-latest
```

### If You Want Gemini (New Default)
Nothing to do! It's already configured.

### For API Keys
```bash
# Gemini (recommended)
export GEMINI_API_KEY=your-key

# Or Anthropic (still supported)
export ANTHROPIC_API_KEY=your-key
```

## 🔒 Security & Privacy

- **No credentials in registry** - API keys remain environment-only
- **Local transcription** - `transcriber-local` for sensitive content
- **Backward compatible** - no breaking security changes

## 🐛 Bug Fixes

- Fixed 404 errors with invalid Anthropic model IDs
- Model resolution now handles legacy aliases correctly
- Workflow discovery improved

## 📚 Documentation Updates

- CHANGELOG.md - Full v2.4.0 entry
- CONTRIBUTING.md - Testing section added
- README files for transcriber-local skill

## 🙏 Contributors

This release brings major improvements to developer experience, testing workflow, and privacy-focused transcription capabilities.

## 📦 What's Next (v2.5.0 Roadmap)

- WhisperX integration for enhanced video transcription
- Shared transcript JSON schema
- Per-skill model configuration
- Cloud sync for profiles and workflows
- Skill marketplace

## 🔗 Links

- GitHub: https://github.com/CoachSteff/superskills
- Issues: https://github.com/CoachSteff/superskills/issues
- Discussions: https://github.com/CoachSteff/superskills/discussions

---

**Full Changelog:** [CHANGELOG.md](CHANGELOG.md)
