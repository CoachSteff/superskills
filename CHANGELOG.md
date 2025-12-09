# Changelog

All notable changes to SuperSkills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- IDE AI integration framework

## [2.0.0] - 2025-12-09

### Summary
**Major Release**: Production-ready CLI with 40 skills, comprehensive testing, and quality validation. All critical bugs fixed, 95% quality grade achieved.

### Added
- **SuperSkills CLI**: Complete command-line interface for all skills
  - `superskills` command with 11 working commands
  - Skill discovery system detecting all 40 skills (29 Prompt + 11 Python)
  - Skill executor for both prompt-based and Python-powered skills
  - Workflow engine for multi-step orchestration
  - Configuration management in `~/.superskills/`
  - Commands: init, list, call, run, status, workflow, export, discover, validate
  
- **New Skill Documentation**: 8 missing SKILL.md files created
  - coursepackager, craft, emailcampaigner, knowledgebase, presenter, scraper, transcriber, videoeditor
  - All 40 skills now have proper SKILL.md files
  
- **Validation System**: New `superskills validate` command
  - Checks skill integrity and accessibility
  - Verifies SKILL.md files exist and are valid
  - Reports missing files and configuration issues
  
- **Enhanced CLI Features**:
  - Export command with skill metadata (JSON/Markdown)
  - Discovery command with capability-based search
  - JSON output mode for all commands (`--json` flag)
  - Structured error messages with helpful guidance
  - Version detection now working correctly
  
- **Documentation**:
  - IDE Integration guide (docs/IDE_INTEGRATION.md)
  - Test reports (TEST_REPORT.md, BUGS_AND_IMPROVEMENTS.md, TESTING_SUMMARY.md, TEST_COMPLETION_REPORT.md)
  - Enhanced README with CLI installation and usage
  - Automated setup script (setup.sh)

### Changed
- **BREAKING**: CLI moved from `superskills/cli/` to `/cli/` (root level)
  - Import path changed: `from superskills.cli` → `from cli`
  - Entry point remains `superskills` command
  - Skills directory correctly resolved to `/superskills/`
  - Path resolution uses project root detection (pyproject.toml, .git)
  
- **Fixed Critical Bugs** (5 major issues resolved):
  1. SkillLoader directory resolution - now detects all 40 skills
  2. Version detection - correctly shows v2.0.0
  3. Export command version - returns correct 2.0.0 in metadata
  4. Documentation accuracy - updated to 40 skills (29 Prompt + 11 Python)
  5. Missing SKILL.md files - created for 8 skills
  
- **BREAKING**: Workflow structure simplified
  - Workflows now use input/output folder pattern (no Python files in workflow folders)
  - Use `superskills run <workflow>` commands instead of custom Python runners
  - Folder-based workflows have `workflow.yaml` with `io` configuration
  - Example: `workflows/podcast-generation/` (formerly `workflows/podcast-workflow/`)
  
- Enhanced error messages with actionable guidance
- Improved capability tagging for skill discovery
- Updated all documentation for accuracy

### Added
- Watch mode for workflows: `superskills run <workflow> --watch`
  - Monitors workflow's `input/` folder for new files
  - Automatically processes files as they appear
  - Press Ctrl+C to stop watching

- Batch mode for workflows: `superskills run <workflow> --batch`
  - Processes all files in workflow's `input/` folder at once
  - Shows progress and summary statistics
  
- Folder-based workflow detection
  - CLI now finds workflows in three locations:
    1. `workflows/definitions/{name}.yaml` (simple workflows)
    2. `workflows/custom/{name}.yaml` (custom simple workflows)
    3. `workflows/{name}/workflow.yaml` (folder-based workflows with input/output)

- Enhanced workflow configuration
  - `io.input_dir` and `io.output_dir` settings in workflow.yaml
  - `save_to` parameter in workflow steps for file output
  - `${filename}` variable for dynamic output naming

### Removed
- Python files from workflows (run_workflow.py, process_direct.py, requirements.txt)
- Workflow-specific source code directories (src/ folders)
- Old `inbox/` directory (renamed to `input/`)

### Migration Guide

**CLI Installation:**
```bash
# Reinstall CLI in development mode
pip install -e .  # or pipx install -e . or pip install --user -e .

# Verify installation
superskills --help
superskills list
```

**Workflows:**

Old structure (v1.x):
```
workflows/podcast-workflow/
├── run_workflow.py          # Removed
├── process_direct.py         # Removed  
├── requirements.txt          # Removed
├── src/                      # Removed
├── inbox/                    # Renamed to input/
├── output/
└── config.yaml              # Replaced by workflow.yaml
```

New structure (v2.0):
```
workflows/podcast-generation/
├── input/                   # Place source files here
├── output/                  # Generated files appear here
├── workflow.yaml            # Unified configuration
└── README.md                # CLI usage instructions
```

**Usage Changes:**

Before (v1.x):
```bash
cd workflows/podcast-workflow
python run_workflow.py
# Drop files in inbox/ folder
```

After (v2.0):
```bash
# Option 1: Single file
superskills run podcast-generation --input input/my-script.md

# Option 2: Watch folder
superskills run podcast-generation --watch

# Option 3: Batch process
superskills run podcast-generation --batch
```

### Technical Details

**Path Resolution:**
- CLI now at `/cli/` instead of `/superskills/cli/`
- Skills remain at `/superskills/{skill-name}/`
- Workflows at `/workflows/{workflow-name}/` or `/workflows/definitions/`
- Project root detected via pyproject.toml or .git directory

**Workflow Engine:**
- New `watch_and_execute()` method for file monitoring
- New `batch_execute()` method for bulk processing
- Enhanced `_find_workflow_file()` to support folder-based workflows
- Variables: `input`, `input_file`, `filename` automatically provided in watch/batch modes

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
