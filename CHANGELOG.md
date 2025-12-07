# Changelog

All notable changes to SuperSkills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-01-07

### Added
- Voice profile configuration system for narrator skill
  - `voice_profiles.json` for customizable voice settings per content type
  - Three profiles: narration, podcast, meditation
  - VoiceConfig loader with validation and caching
- Integration test suite for narrator voice profiles
- Brand style customization for designer skill (parameter-based)
- Development guidelines section in README.md linking to `.cursorrules`
- `.cursorrules` file with comprehensive development workflow rules

### Changed
- **BREAKING**: Narrator skill now uses voice profiles instead of hardcoded settings
- Genericized narrator skill (removed "CoachSteff" hardcoded references)
- Designer BRAND_STYLE constant replaced with configurable parameter
- Updated PROFILE.md.template for designer with brand style documentation
- Consolidated all documentation to reference single canonical location (`superskills/` only)
- Updated ARCHITECTURE.md, CONTRIBUTING.md, and README.md to remove `new-skills/` references
- Updated project structure examples to showcase narrator, designer, and craft Python skills

### Removed
- `new-skills/` directory and all legacy agent definition files (47 files)
- Hardcoded personal branding from skill implementations
- PUBLICATION_COMPLETE.md and RELEASE_READINESS_REPORT.md (one-time release artifacts)

## [1.0.0] - 2024-12-07

### Added
- Initial public release
- 43 skills total:
  - 20 Claude .skill files (prompt-based AI specialists)
  - 23 Python-powered skills with API integrations
- Comprehensive credential management system
  - Hybrid env vars + .env file support
  - Skill-specific .env files with fallback to global
- Production-ready skills:
  - Narrator (ElevenLabs voice generation)
  - Designer (Gemini/Midjourney image generation)
  - Transcriber (OpenAI Whisper transcription)
  - Craft (web scraping framework)
  - Marketer (Postiz social media publishing)
  - And 38 more specialized skills
- Complete documentation:
  - README with quick start guide
  - ARCHITECTURE documentation
  - CONTRIBUTING guidelines
  - Per-skill PROFILE.md.template files
- Python packaging support (pip-installable via pyproject.toml)
- 90+ unit tests with pytest framework

### Changed
- Migrated from Anthropic agent-skills spec to independent project
- Removed all Anthropic-specific content and licensing
- Secured personal information (PROFILE.md files gitignored)

### Security
- API keys managed via .env files (gitignored)
- Personal voice profiles and brand guidelines in PROFILE.md (gitignored)
- No credentials committed to repository

---

## Version History Notes

### v1.0.0 - Initial Release
This is the first public release of SuperSkills, a comprehensive AI automation toolkit designed for coaches, trainers, and content creators. The project includes battle-tested skills used in production workflows.

**Migration from new-skills/**: The `new-skills/` directory was a development workspace that has been consolidated into the main `superskills/` directory. All active development now happens in `superskills/`.

**Genericization**: Personal branding and voice characteristics have been moved from hardcoded values to user-configurable PROFILE.md files, making the toolkit suitable for any user.
