# Changelog

All notable changes to SuperSkills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.2] - 2024-12-18

### Fixed
- **CRITICAL: Natural Language Interface** - Fixed broken quote-detection mechanism
  - Replaced quote-based detection with auto-detection of unknown commands
  - Shell quote-stripping prevented v2.1.0 implementation from working
  - Now works: `superskills find my files` (no quotes needed!)
  - Added explicit `prompt` subcommand: `superskills prompt <query>`
  - 100% backward compatible with all existing commands

### Technical Details
- Auto-detect: Unknown commands (not matching known commands) treated as natural language
- Explicit: `prompt` subcommand always triggers natural language processing
- Quote-based detection removed (fundamentally incompatible with shell parsing)
- Known commands: init, list, show, call, run, status, validate, workflow, export, config, discover, prompt

### Migration
- **v2.1.0 users:** No action needed, syntax improved
- Previous documentation showed `superskills "query"` (didn't work)
- Now use: `superskills query` or `superskills prompt query` (works!)
- More intuitive, no shell escaping required

## [2.1.1] - 2024-12-19

### Summary
Patch release: Added missing media processing dependencies for narrator and designer skills.

### Added
- **Media Processing Dependencies**
  - `pydub>=0.25.0` - Audio manipulation for narrator skill
  - `audioop-lts>=0.2.0` - Audio operations for Python 3.13+ compatibility
  - `Pillow>=10.0.0` - Image processing for designer skill
  - These were previously in optional `[media]` extras, now included in core dependencies

### Changed
- Media dependencies moved from optional to core requirements
- Ensures narrator (audio generation) and designer (image generation) work out-of-the-box

### Fixed
- Installation issues when using narrator or designer skills without `pip install superskills[media]`
- Python 3.13+ compatibility with `audioop-lts` package

## [2.1.0] - 2024-12-18

### Summary
Major feature release: Natural language interface with AI-powered intent parsing, enabling frictionless CLI interaction through quoted input.

### Added
- **Natural Language Interface** - AI-powered intent parsing for seamless CLI interaction
  - Quote input for natural language mode: `superskills "find my files"`
  - Unquoted input works exactly as before (100% backward compatible)
  - Smart confidence-based execution:
    - High confidence (≥0.8): Execute with feedback
    - Medium confidence (0.5-0.8): Ask for confirmation
    - Low confidence (<0.5): Suggest alternatives
  - Configurable LLM provider (Gemini Flash, Anthropic, OpenAI)
  - Override via env vars or CLI flags: `--intent-model`, `--intent-provider`
  - Comprehensive user guide: `NATURAL_LANGUAGE.md`

- **Unified LLM Client** (`cli/utils/llm_client.py`)
  - Multi-provider support: Gemini, Anthropic, OpenAI
  - Factory pattern for easy provider switching
  - Retry logic with exponential backoff
  - Comprehensive error handling

- **Intent Parser** (`cli/core/intent_parser.py`)
  - Converts natural language to structured JSON intents
  - Returns confidence scores (0.0-1.0)
  - Validates against JSON schema
  - Caches skill metadata for performance

- **Intent Router** (`cli/core/intent_router.py`)
  - Routes parsed intents to appropriate commands
  - Pre-execution validation (files exist, skills available)
  - Supports all actions: search, execute_skill, run_workflow, list, show, config, discover

- **Search Command** (`cli/commands/search.py`)
  - File search by name (glob patterns)
  - Content search (ripgrep or grep fallback)
  - Skill search (delegates to discover)
  - Configurable search paths with environment variable expansion
  - Auto-detection of search type

- **Intent Schema** (`cli/schemas/intent_schema.json`)
  - JSON schema for intent validation
  - Ensures structured, type-safe intents

### Changed
- **Configuration System** - Extended with intent and search settings
  - New `intent` section: provider, model, confidence threshold
  - New `search` section: paths, use_ripgrep, max_results
  - Default: Gemini Flash 2.0 (`gemini-2.0-flash-exp`) for intent parsing
  - Configurable search paths: `${OBSIDIAN_VAULT_PATH}`, `~/Documents`, `~/Downloads`, `.`

- **CLI Flags** - Added natural language control options
  - `--intent-model MODEL`: Override LLM model for intent parsing
  - `--intent-provider {gemini,anthropic,openai}`: Override LLM provider
  - `--no-intent`: Disable intent parsing, force exact syntax

### Technical Details
- Intent parsing latency: <3s (p95)
- Test coverage: 20 new unit tests for intent parser and router
- Zero breaking changes to existing CLI commands
- All imports validated, syntax checked
- Documentation: Comprehensive user guide with troubleshooting

## [2.0.3] - 2024-12-17

### Summary
Feature release: Obsidian filesystem vault manager skill and enhanced narrator architecture with specialized sub-skills.

### Added
- **Obsidian Skill** (`superskills/obsidian/`) - Filesystem-based Obsidian vault manager
  - Full CRUD operations on Markdown notes (create, read, update)
  - Advanced search: text search, hierarchical tag filtering, folder navigation
  - Hierarchical tag taxonomy support (topic/ai, status/draft, type/blog)
  - Wiki link management: auto-update links on move/rename, backlink discovery
  - Hub note creation: generate index notes grouped by tag categories
  - Frontmatter YAML parsing and manipulation with auto-timestamps
  - Read-only mode for safe vault exploration
  - Path validation preventing vault escape (security)
  - Change planning (dry-run mode)
  - 46 comprehensive unit tests with 74% code coverage
  - Complete documentation: SKILL.md, README.md, .env.template
  - CLI integration via JSON-based command interface
  - Python API: `from superskills.obsidian.src import ObsidianClient`

- **CLI Test Coverage**: 8 successful CLI tests covering all major operations
  - List notes, search by tag, text search, get note
  - Create note, add tags, find backlinks, create hub

- **Narrator Skill Family**: Hierarchical skill architecture with 5 specialized narrator subskills
  - `narrator-podcast` - Conversational podcast voiceovers (140-160 WPM, Steff Pro voice)
  - `narrator-meditation` - Calm meditation guides (slower pacing, Steff Pro voice)
  - `narrator-educational` - Clear educational content (130-150 WPM, Steff Basic Dutch voice)
  - `narrator-marketing` - Energetic marketing content (150-170 WPM, Steff Basic voice)
  - `narrator-social` - Fast-paced social media (160-180 WPM, Steff Basic voice)
  - Each subskill has dedicated SKILL.md and PROFILE.md.template files
  - Nested folder structure: `superskills/narrator/{podcast,meditation,educational,marketing,social}/`

- **Hierarchical Skill Display**: Enhanced `superskills list` command
  - Tree-style indentation for parent-child skill relationships
  - Visual hierarchy using `├─` and `└─` characters
  - Shows 45 total skills (40 base + 5 narrator subskills)
  - Example display:
    ```
    - narrator
      ├─ narrator-educational
      ├─ narrator-marketing
      ├─ narrator-meditation
      ├─ narrator-podcast
      └─ narrator-social
    ```

- **AI Assistant Integration Guide**: New `docs/AI_ASSISTANT_GUIDE.md`
  - Discovery-first patterns for IDE AI assistants
  - Skill families explanation with narrator example
  - Common mistakes section (don't invent CLI parameters)
  - Examples by use case (podcast, meditation, marketing, etc.)
  - Integration tips and troubleshooting guide
  - Linked from README.md and IDE_INTEGRATION.md

### Changed
- **BREAKING**: Removed `--content-type` and `--profile-type` CLI parameters
  - Old syntax: `superskills call narrator --content-type podcast` ❌
  - New syntax: `superskills call narrator-podcast` ✅
  - Simplifies CLI interface - no business logic in CLI layer
  - Each narrator variant is now a discoverable skill

- **Skill Executor Enhancement**: Added JSON input parsing for Obsidian skill
  - New handler in `cli/core/skill_executor.py` for Obsidian skill
  - Parses JSON input and delegates to `superskills.obsidian.src.execute()`
  - Example: `echo '{"action": "list"}' | superskills call obsidian`

- **Skill Loader Enhancement**: Recursive subskill discovery
  - `SkillLoader.discover_skills()` now scans subdirectories for nested skills
  - Skips `src/` and hidden directories
  - Added `parent_skill` field to `SkillInfo` dataclass for hierarchy tracking
  - PYTHON_SKILLS registry expanded with 5 narrator subskills

- **Skill Executor Refactor**: Hardcoded configuration mapping
  - Narrator family uses skill name to determine voice profile and content type
  - Configuration lives in `skill_executor.py`, not CLI arguments
  - Each subskill has predictable, documented defaults
  - Example: `narrator-meditation` → `content_type='meditation', profile_type='meditation'`

- **README.md**: Updated Python-Powered Skills table
  - Added Obsidian to Featured API-Integrated Skills section
  - Description: "Filesystem | Obsidian vault manager - read/write notes, hierarchical tags, wiki links"

- **Skill Loader**: Registered Obsidian skill in PYTHON_SKILLS registry
  - Entry: `'obsidian': 'superskills.obsidian.src.ObsidianClient:ObsidianClient'`

- **Workflow Updates**: Using specialized narrator skills
  - `podcast-generation/workflow.yaml` now uses `narrator-podcast` instead of `narrator` + config
  - Removed `config:` sections from workflow steps
  - Cleaner, more maintainable workflow definitions

- **Documentation Updates**: Aligned with new architecture
  - `QUICKSTART.md` shows specialized skills, removed fake CLI parameters
  - `docs/IDE_INTEGRATION.md` corrected examples, added AI guide link
  - `superskills/narrator/SKILL.md` references specialized subskills
  - `README.md` includes AI Assistant Guide in documentation section

- **Project Organization**: Cleaned up root directory to maintain only essential files
  - Moved implementation docs to `dev/` directory (IMPLEMENTATION_*.md, VERIFICATION.md, etc.)
  - Moved test files to `dev/` directory (test-podcast-*.md, meditation_script.md)
  - Moved QUICKSTART.md to `docs/` directory
  - Updated README.md references to point to correct locations
  - Root now contains only: WARP.md, ROADMAP.md, CHANGELOG.md, README.md, CONTRIBUTING.md

- **.cursorrules Enhancement**: Added comprehensive CHANGELOG.md maintenance guidelines
  - Mandatory CHANGELOG.md update workflow before commits
  - Detailed format and best practices with examples
  - Pre-commit checklist for CHANGELOG.md verification
  - Pre-release checklist for proper version management
  - Clear categorization rules (Added/Changed/Fixed/Security/Performance)
  - Anti-patterns to avoid and user-facing description guidelines

### Fixed
- **Credential Loading**: Removed invalid `superskills/narrator/.env` with corrupted API key
  - File had extra 's' prefix in ELEVENLABS_API_KEY
  - Now correctly loads from root `.env` file
  - Skill-specific .env files take precedence when valid

### Migration Guide

**For Users:**
If you were using the old narrator CLI syntax, update to specialized skills:

```bash
# Old (no longer works)
superskills call narrator --content-type podcast --profile-type podcast

# New (recommended)
superskills call narrator-podcast --input script.md

# For different content types
superskills call narrator-meditation --input meditation.md
superskills call narrator-educational --input lesson.md
superskills call narrator-marketing --input promo.md
superskills call narrator-social --input social-post.md
```

**For Workflows:**
Update workflow definitions to use specialized narrator skills:

```yaml
# Old
- name: narrate
  skill: narrator
  config:
    content_type: podcast
    profile_type: podcast

# New
- name: narrate
  skill: narrator-podcast
```

## [2.0.2] - 2024-12-10

### Summary
Feature release: Intelligent model resolution with automatic alias expansion and config auto-regeneration.

### Added
- **Model Resolver System**: Automatic resolution of model aliases to stable versions
  - `ModelResolver` class with lazy resolution (only on first API call)
  - Global caching to prevent redundant API calls
  - 4 model aliases configured:
    - `claude-3-opus-latest` → `claude-3-opus-20240229`
    - `claude-3-sonnet-latest` → `claude-3-5-sonnet-20241022`
    - `claude-3-haiku-latest` → `claude-3-5-haiku-20241022`
    - `claude-4.5-sonnet` → `claude-3-5-sonnet-20241022`
  - Automatic fallback on 404 errors with user notification
  - Non-aliased models pass through unchanged
  - Test suite with 100% pass rate (16/16 tests)
  
- **Config Auto-Regeneration**: Detects and fixes outdated configurations
  - Detects version < 2.0.1
  - Detects deprecated models (`claude-sonnet-4`, `claude-4.5-sonnet`)
  - Auto-regenerates with `claude-3-sonnet-latest`
  - Clear notification: `⚠ Outdated config detected. Regenerating...`
  
- **Model Discovery Tool**: `tools/discover_models.py` for finding available models
  - Lists all models from Anthropic API
  - Helps identify latest model versions
  - Useful for maintaining alias mappings
  
- **Documentation**:
  - MODEL_RESOLVER_TEST_REPORT.md with comprehensive test results
  - Updated QUICKSTART.md with model resolution examples

### Changed
- Default model: `claude-4.5-sonnet` → `claude-3-sonnet-latest` (auto-resolves)
- APIClient now uses ModelResolver for all API calls
- Config default updated to use latest alias
- All 3 config locations updated (api_client.py, config.py, skill_executor.py)

### Performance
- Initialization: < 1ms (no API call)
- First resolution: ~100-200ms (one API test call)
- Cached lookups: < 0.1ms (dictionary access)
- Overall impact: Negligible

### Test Results
✅ 100% pass rate (16/16 tests)
- 5 pytest unit tests
- 6 integration tests
- 3 config auto-regeneration tests
- 2 CLI integration tests

### Backward Compatibility
- ✅ Non-aliased models work unchanged
- ✅ Existing code continues to work
- ✅ No breaking changes

## [2.0.1] - 2024-12-10

### Summary
**Critical Patch Release**: Fixes blocking installation and runtime issues from v2.0.0. All users should upgrade immediately.

### Fixed
- **CRITICAL: Invalid model name** - Changed from `claude-sonnet-4` (doesn't exist) to `claude-4.5-sonnet` (latest Sonnet)
  - Updated in `cli/utils/api_client.py` default parameter
  - Updated in `cli/utils/config.py` default configuration  
  - Updated in `cli/core/skill_executor.py` fallback model
  - Updated in `docs/IDE_INTEGRATION.md` documentation
  - Fixes 404 errors: "model: claude-sonnet-4 does not exist"
  
- **CRITICAL: .env files not loading** - Environment variables now properly loaded from `.env` files with correct precedence
  - Added `load_dotenv()` to `cli/main.py` entry point
  - Added skill-specific credential loading to `cli/core/skill_executor.py`
  - **Correct precedence order** (highest to lowest):
    1. System environment variables (always respected)
    2. Skill-specific `.env` files (`superskills/{skill}/.env`)
    3. User config `.env` (`~/.superskills/.env`)
    4. Project root `.env`
  - Skill-specific `.env` files override global settings for that skill only
  - Fixes "ANTHROPIC_API_KEY not found" errors when .env exists
  
- **CRITICAL: Cached config with invalid model** - Auto-regeneration of outdated configurations
  - Detects version mismatch (< 2.0.1)
  - Detects invalid model name (`claude-sonnet-4`)
  - Automatically regenerates config with correct defaults
  - Shows warning: "⚠ Outdated config detected. Regenerating with claude-4.5-sonnet..."
  - Users no longer need to manually delete `~/.superskills/config.yaml`
  
- **MINOR: setup.sh input handling** - Trimmed whitespace from user input
  - Option "1" now correctly recognized (was failing with trailing spaces)
  - Improved installation reliability

### Changed
- Default model everywhere: `claude-4.5-sonnet` (was `claude-sonnet-4`)
- Config version tracking: Added `version: 2.0.1` field for migration detection
- .env loading precedence: Skill-specific `.env` files now correctly override global settings

### Documentation
- Added troubleshooting sections to `QUICKSTART.md`:
  - Model 404 error solutions
  - .env loading explanation
  - Config regeneration instructions
  - API key setup verification

### Migration from v2.0.0

**No action required** - Config auto-regenerates on first run.

If you experience issues:
```bash
# 1. Reinstall CLI
pipx uninstall superskills
pipx install -e .

# 2. Verify config
cat ~/.superskills/config.yaml | grep model
# Should show: model: claude-4.5-sonnet

# 3. Test with real API key
superskills call researcher "AI trends"
```

## [2.0.0] - 2024-12-09

### Added
- **Obsidian Skill** (`superskills/obsidian/`) - Filesystem-based Obsidian vault manager
  - Full CRUD operations on Markdown notes (create, read, update)
  - Advanced search: text search, hierarchical tag filtering, folder navigation
  - Hierarchical tag taxonomy support (topic/ai, status/draft, type/blog)
  - Wiki link management: auto-update links on move/rename, backlink discovery
  - Hub note creation: generate index notes grouped by tag categories
  - Frontmatter YAML parsing and manipulation with auto-timestamps
  - Read-only mode for safe vault exploration
  - Path validation preventing vault escape (security)
  - Change planning (dry-run mode)
  - 46 comprehensive unit tests with 74% code coverage
  - Complete documentation: SKILL.md, README.md, .env.template
  - CLI integration via JSON-based command interface
  - Python API: `from superskills.obsidian.src import ObsidianClient`

- **CLI Test Coverage**: 8 successful CLI tests covering all major operations
  - List notes, search by tag, text search, get note
  - Create note, add tags, find backlinks, create hub

### Changed
- **Skill Executor Enhancement**: Added JSON input parsing for Obsidian skill
  - New handler in `cli/core/skill_executor.py` for Obsidian skill
  - Parses JSON input and delegates to `superskills.obsidian.src.execute()`
  - Example: `echo '{"action": "list"}' | superskills call obsidian`

- **README.md**: Updated Python-Powered Skills table
  - Added Obsidian to Featured API-Integrated Skills section
  - Description: "Filesystem | Obsidian vault manager - read/write notes, hierarchical tags, wiki links"

- **Skill Loader**: Registered Obsidian skill in PYTHON_SKILLS registry
  - Entry: `'obsidian': 'superskills.obsidian.src.ObsidianClient:ObsidianClient'`

### Fixed
- **Narrator Skill Family**: Hierarchical skill architecture with 5 specialized narrator subskills
  - `narrator-podcast` - Conversational podcast voiceovers (140-160 WPM, Steff Pro voice)
  - `narrator-meditation` - Calm meditation guides (slower pacing, Steff Pro voice)
  - `narrator-educational` - Clear educational content (130-150 WPM, Steff Basic Dutch voice)
  - `narrator-marketing` - Energetic marketing content (150-170 WPM, Steff Basic voice)
  - `narrator-social` - Fast-paced social media (160-180 WPM, Steff Basic voice)
  - Each subskill has dedicated SKILL.md and PROFILE.md.template files
  - Nested folder structure: `superskills/narrator/{podcast,meditation,educational,marketing,social}/`

- **Hierarchical Skill Display**: Enhanced `superskills list` command
  - Tree-style indentation for parent-child skill relationships
  - Visual hierarchy using `├─` and `└─` characters
  - Shows 45 total skills (40 base + 5 narrator subskills)
  - Example display:
    ```
    - narrator
      ├─ narrator-educational
      ├─ narrator-marketing
      ├─ narrator-meditation
      ├─ narrator-podcast
      └─ narrator-social
    ```

- **AI Assistant Integration Guide**: New `docs/AI_ASSISTANT_GUIDE.md`
  - Discovery-first patterns for IDE AI assistants
  - Skill families explanation with narrator example
  - Common mistakes section (don't invent CLI parameters)
  - Examples by use case (podcast, meditation, marketing, etc.)
  - Integration tips and troubleshooting guide
  - Linked from README.md and IDE_INTEGRATION.md

### Changed
- **BREAKING**: Removed `--content-type` and `--profile-type` CLI parameters
  - Old syntax: `superskills call narrator --content-type podcast` ❌
  - New syntax: `superskills call narrator-podcast` ✅
  - Simplifies CLI interface - no business logic in CLI layer
  - Each narrator variant is now a discoverable skill

- **Skill Loader Enhancement**: Recursive subskill discovery
  - `SkillLoader.discover_skills()` now scans subdirectories for nested skills
  - Skips `src/` and hidden directories
  - Added `parent_skill` field to `SkillInfo` dataclass for hierarchy tracking
  - PYTHON_SKILLS registry expanded with 5 narrator subskills

- **Skill Executor Refactor**: Hardcoded configuration mapping
  - Narrator family uses skill name to determine voice profile and content type
  - Configuration lives in `skill_executor.py`, not CLI arguments
  - Each subskill has predictable, documented defaults
  - Example: `narrator-meditation` → `content_type='meditation', profile_type='meditation'`

- **Workflow Updates**: Using specialized narrator skills
  - `podcast-generation/workflow.yaml` now uses `narrator-podcast` instead of `narrator` + config
  - Removed `config:` sections from workflow steps
  - Cleaner, more maintainable workflow definitions

- **Documentation Updates**: Aligned with new architecture
  - `QUICKSTART.md` shows specialized skills, removed fake CLI parameters
  - `docs/IDE_INTEGRATION.md` corrected examples, added AI guide link
  - `superskills/narrator/SKILL.md` references specialized subskills
  - `README.md` includes AI Assistant Guide in documentation section

- **Project Organization**: Cleaned up root directory to maintain only essential files
  - Moved implementation docs to `dev/` directory (IMPLEMENTATION_*.md, VERIFICATION.md, etc.)
  - Moved test files to `dev/` directory (test-podcast-*.md, meditation_script.md)
  - Moved QUICKSTART.md to `docs/` directory
  - Updated README.md references to point to correct locations
  - Root now contains only: WARP.md, ROADMAP.md, CHANGELOG.md, README.md, CONTRIBUTING.md

- **.cursorrules Enhancement**: Added comprehensive CHANGELOG.md maintenance guidelines
  - Mandatory CHANGELOG.md update workflow before commits
  - Detailed format and best practices with examples
  - Pre-commit checklist for CHANGELOG.md verification
  - Pre-release checklist for proper version management
  - Clear categorization rules (Added/Changed/Fixed/Security/Performance)
  - Anti-patterns to avoid and user-facing description guidelines

### Fixed
- **Credential Loading**: Removed invalid `superskills/narrator/.env` with corrupted API key
  - File had extra 's' prefix in ELEVENLABS_API_KEY
  - Now correctly loads from root `.env` file
  - Skill-specific .env files take precedence when valid

### Migration Guide

**For Users:**
If you were using the old narrator CLI syntax, update to specialized skills:

```bash
# Old (no longer works)
superskills call narrator --content-type podcast --profile-type podcast

# New (recommended)
superskills call narrator-podcast --input script.md

# For different content types
superskills call narrator-meditation --input meditation.md
superskills call narrator-educational --input lesson.md
superskills call narrator-marketing --input promo.md
superskills call narrator-social --input reel.md
```

**For Workflows:**
Update workflow YAML files to use specialized skills:

```yaml
# Old
steps:
  - name: generate-audio
    skill: narrator
    input: ${script}
    config:
      content_type: podcast
      profile_type: podcast

# New
steps:
  - name: generate-audio
    skill: narrator-podcast
    input: ${script}
```

### Technical Details

**Architecture Benefits:**
- CLI remains simple UI layer (no business logic)
- Capabilities live in discoverable skill folders
- Nested structure improves maintainability
- Clear parent-child relationships visible to users and AI assistants
- Backward compatible: original `narrator` skill still works (defaults to podcast)

**Verification Tests Passed:**
- ✅ Discovery: `superskills list` shows 45 skills with hierarchical display
- ✅ Execution: `narrator-podcast` generates 6m17s audio from 807-word script
- ✅ Show command: `superskills show narrator-podcast` displays subskill docs
- ✅ Discovery search: `superskills discover --query "meditation"` finds `narrator-meditation`
- ✅ Workflows: `podcast-generation` workflow uses `narrator-podcast` correctly
- ✅ Translation + Voice: Generated 7m30s Flemish podcast using Dutch voice profile
- ✅ Documentation: No references to removed CLI parameters

### Planned
- IDE AI integration framework

## [1.1.1] - 2025-12-08

### Added
- `voice_profiles.json.template` for narrator skill with placeholder values

### Changed
- **BREAKING**: Removed `.skill` file extension (invalid format per Claude Skills specification)
- Claude Skills now properly structured as folders containing `SKILL.md` files
- Updated all documentation with correct ZIP import instructions
- Updated README.md with step-by-step ZIP creation guide
- Updated ARCHITECTURE.md with proper skill structure patterns
- Updated QUICKSTART.md with detailed import workflow
- Updated SKILL_DEVELOPMENT.md with correct reference paths
- Updated CONTRIBUTING.md to reflect folder-based structure
- Enhanced .gitignore with voice_profiles.json exclusion pattern

### Removed
- 20 `.skill` files (author, builder, coach, context-engineer, copywriter, designer, developer, editor, manager, marketer, narrator, producer, publisher, quality-control, researcher, sales, scraper, strategist, translator, webmaster)
- Personal `voice_profiles.json` removed from git tracking (now gitignored)

### Security
- Personal voice profiles (voice_profiles.json) now excluded from version control
- Voice IDs and profile names no longer committed to repository

### Migration Guide
To use Claude Skills after this update:
1. Create ZIP files: `cd superskills && zip -r {skill-name}.zip {skill-name}/`
2. Import in Claude Desktop: Settings → Skills → Upload Custom Skill
3. Select the ZIP files you created
4. Claude will read each skill's `SKILL.md` file

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
- Updated ARCHITECTURE.md, CONTRIBUTING.md, and README.md to remove `new-skills/` references (dev docs moved to `dev/`)
- Updated project structure examples to showcase narrator, designer, and craft Python skills

### Removed
- `new-skills/` directory and all legacy agent definition files (47 files)
- Hardcoded personal branding from skill implementations
- PUBLICATION_COMPLETE.md and RELEASE_READINESS_REPORT.md (one-time release artifacts)

## [1.0.0] - 2024-12-07

### Added
- Initial public release
- 40 skills total:
  - 29 Claude Skills (prompt-based AI specialists, folder-based with SKILL.md)
  - 11 Python-powered skills with API integrations
- Comprehensive credential management system
  - Hybrid env vars + .env file support
  - Skill-specific .env files with fallback to global
- Production-ready skills:
  - Narrator (ElevenLabs voice generation)
  - Designer (Gemini/Midjourney image generation)
  - Transcriber (OpenAI Whisper transcription)
  - Craft (web scraping framework)
  - Marketer (Postiz social media publishing)
  - And 35 more specialized skills
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
